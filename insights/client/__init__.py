import errno
import json
import os
import logging
import tempfile
import shlex
import shutil
import sys
import atexit
from subprocess import Popen, PIPE
from requests import ConnectionError

from .. import package_info
from . import client
from .constants import InsightsConstants as constants
from .config import InsightsConfig
from .auto_config import try_auto_configuration
from .utilities import (write_data_to_file,
                        write_to_disk,
                        get_tags,
                        write_tags,
                        migrate_tags,
                        get_parent_process)

NETWORK = constants.custom_network_log_level
logger = logging.getLogger(__name__)


class InsightsClient(object):

    def __init__(self, config=None, from_phase=True, **kwargs):
        """
        The Insights client interface
        """
        if config is None:
            # initialize with default config if not specified with one
            self.config = InsightsConfig()
        else:
            # BEGIN small hack to maintain compatibility with RPM wrapper:
            #   wrapper calls with bool second arg so be smart about it
            if isinstance(config, InsightsConfig):
                self.config = config
            else:
                try:
                    self.config = InsightsConfig(_print_errors=True).load_all()
                except ValueError as e:
                    sys.stderr.write('ERROR: ' + str(e) + '\n')
                    sys.exit(constants.sig_kill_bad)
            # END hack. in the future, just set self.config=config

        if from_phase:
            _init_client_config_dirs()
            self.set_up_logging()
            try_auto_configuration(self.config)
            self.initialize_tags()
        else:  # from wrapper
            _write_pid_files()

        # setup insights connection placeholder
        # used for requests
        self.connection = None
        self.tmpdir = None

    def _net(func):
        def _init_connection(self, *args, **kwargs):
            # setup a request session
            if not self.config.offline and not self.connection:
                self.connection = client.get_connection(self.config)
            return func(self, *args, **kwargs)
        return _init_connection

    def get_conf(self):
        # need this getter to maintain compatability with RPM wrapper
        return self.config

    def set_up_logging(self):
        return client.set_up_logging(self.config)

    def version(self):
        return "%s-%s" % (package_info["VERSION"], package_info["RELEASE"])

    @_net
    def test_connection(self):
        """
            returns (int): 0 if success 1 if failure
        """
        return self.connection.test_connection()

    @_net
    def branch_info(self):
        """
            returns (dict): {'remote_leaf': -1, 'remote_branch': -1}
        """
        return client.get_branch_info(self.config, self.connection)

    @_net
    def get_egg_url(self):
        """
        Get the proper url based on the configured egg release branch
        """
        if self.config.legacy_upload:
            url = self.connection.base_url + '/platform' + constants.module_router_path
        else:
            url = self.connection.base_url + constants.module_router_path
        try:
            response = self.connection.get(url)
            if response.status_code == 200:
                return response.json()["url"]
            else:
                raise ConnectionError("%s: %s" % (response.status_code, response.reason))
        except ConnectionError as e:
            logger.warning("Unable to fetch egg url %s: %s. Defaulting to /release", url, str(e))
            return '/release'

    def fetch(self, force=False):
        """
            returns (dict): {'core': path to new egg, None if no update,
                             'gpg_sig': path to new sig, None if no update}
        """
        self.tmpdir = tempfile.mkdtemp()
        atexit.register(self.delete_tmpdir)
        fetch_results = {
            'core': os.path.join(self.tmpdir, 'insights-core.egg'),
            'gpg_sig': os.path.join(self.tmpdir, 'insights-core.egg.asc')
        }

        logger.debug("Beginning core fetch.")

        # guess the URLs based on what legacy setting is
        egg_release = self.get_egg_url()

        try:
            # write the release path to temp so we can collect it
            #   in the archive
            write_data_to_file(egg_release, constants.egg_release_file)
        except (OSError, IOError) as e:
            logger.debug('Could not write egg release file: %s', str(e))

        egg_url = self.config.egg_path
        egg_gpg_url = self.config.egg_gpg_path
        if egg_url is None:
            egg_url = '/v1/static{0}/insights-core.egg'.format(egg_release)
            # if self.config.legacy_upload:
            #     egg_url = '/v1/static/core/insights-core.egg'
            # else:
            #     egg_url = '/static/insights-core.egg'
        if egg_gpg_url is None:
            egg_gpg_url = '/v1/static{0}/insights-core.egg.asc'.format(egg_release)
            # if self.config.legacy_upload:
            #     egg_gpg_url = '/v1/static/core/insights-core.egg.asc'
            # else:
            #     egg_gpg_url = '/static/insights-core.egg.asc'
        # run fetch for egg
        updated = self._fetch(egg_url,
                              constants.core_etag_file,
                              fetch_results['core'],
                              force)

        # if new core was fetched, get new core sig
        if updated:
            logger.debug("New core was fetched.")
            logger.debug("Beginning fetch for core gpg signature.")
            self._fetch(egg_gpg_url,
                        constants.core_gpg_sig_etag_file,
                        fetch_results['gpg_sig'],
                        force)

            return fetch_results

    @_net
    def _fetch(self, path, etag_file, target_path, force):
        """
            returns (str): path to new egg. None if no update.
        """
        # Searched for cached etag information
        current_etag = None
        if os.path.isfile(etag_file):
            with open(etag_file, 'r') as fp:
                current_etag = fp.read().strip()
                logger.debug('Found etag %s', current_etag)

        # it's only temporary. I promise. this is the worst timeline
        # all for a phone popup
        if self.config.legacy_upload:
            url = self.connection.base_url + path
            # verify = self.config.cert_verify
        else:
            url = self.connection.base_url.split('/platform')[0] + path
            # if self.config.cert_verify is True:
            #     # dont overwrite satellite cert
            #     self.cert_verify = os.path.join(
            #         constants.default_conf_dir,
            #         'cert-api.access.redhat.com.pem')

        # Setup the new request for core retrieval
        logger.debug('Making request to %s for new core', url)

        # If the etag was found and we are not force fetching
        # Then add it to the request
        logger.log(NETWORK, "GET %s", url)
        try:
            if current_etag and not force:
                logger.debug('Requesting new file with etag %s', current_etag)
                etag_headers = {'If-None-Match': current_etag}
                response = self.connection.get(url, headers=etag_headers, log_response_text=False)
            else:
                logger.debug('Found no etag or forcing fetch')
                response = self.connection.get(url, log_response_text=False)
        except ConnectionError as e:
            logger.error(e)
            logger.error('The Insights API could not be reached.')
            return False

        # Debug information
        logger.debug('Status code: %d', response.status_code)
        for header, value in response.headers.items():
            logger.debug('%s: %s', header, value)

        # Debug the ETag
        logger.debug('ETag: %s', response.request.headers.get('If-None-Match'))

        # If data was received, write the new egg and etag
        if response.status_code == 200 and len(response.content) > 0:

            # Write the new core
            with open(target_path, 'wb') as handle:
                logger.debug('Data received, writing core to %s', target_path)
                handle.write(response.content)

            # Write the new etag
            with open(etag_file, 'w') as handle:
                logger.debug('Cacheing etag to %s', etag_file)
                handle.write(response.headers['etag'])

            return True

        # Received a 304 not modified
        # Return nothing
        elif response.status_code == 304:
            logger.debug('No data received')
            logger.debug('Tags match, not updating core')

        # Something unexpected received
        else:
            logger.debug('Received Code %s', response.status_code)
            logger.debug('Not writing new core, or updating etag')
            logger.debug('Please check config, error reaching %s', url)

    def update(self):
        # dont update if running in offline mode
        if self.config.offline:
            logger.debug("Not updating Core. Running in offline mode.")
            return True

        if self.config.auto_update:
            logger.debug("Egg update enabled")
            # fetch the new eggs and gpg
            egg_paths = self.fetch()

            # if the gpg checks out install it
            if (egg_paths and self.verify(egg_paths['core'])['gpg']):
                return self.install(egg_paths['core'], egg_paths['gpg_sig'])
            else:
                return False
        else:
            logger.debug("Egg update disabled")

    def verify(self, egg_path, gpg_key=constants.pub_gpg_path):
        """
            Verifies the GPG signature of the egg.  The signature is assumed to
            be in the same directory as the egg and named the same as the egg
            except with an additional ".asc" extension.

            returns (dict): {'gpg': if the egg checks out,
                             'stderr': error message if present,
                             'stdout': stdout,
                             'rc': return code}
        """
        # check if the provided files (egg and gpg) actually exist
        if egg_path and not os.path.isfile(egg_path):
            the_message = "Provided egg path %s does not exist, cannot verify." % (egg_path)
            logger.debug(the_message)
            return {'gpg': False,
                    'stderr': the_message,
                    'stdout': the_message,
                    'rc': 1,
                    'message': the_message}
        if self.config.gpg and gpg_key and not os.path.isfile(gpg_key):
            the_message = ("Running in GPG mode but cannot find "
                            "file %s to verify against." % (gpg_key))
            logger.debug(the_message)
            return {'gpg': False,
                    'stderr': the_message,
                    'stdout': the_message,
                    'rc': 1,
                    'message': the_message}

        # if we are running in no_gpg or not gpg mode then return true
        if not self.config.gpg:
            return {'gpg': True,
                    'stderr': None,
                    'stdout': None,
                    'rc': 0}

        # if a valid egg path and gpg were received do the verification
        if egg_path and gpg_key:
            cmd_template = '/usr/bin/gpg --verify --keyring %s %s %s'
            cmd = cmd_template % (gpg_key, egg_path + '.asc', egg_path)
            logger.debug(cmd)
            process = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            rc = process.returncode
            logger.debug("GPG return code: %s" % rc)
            return {'gpg': True if rc == 0 else False,
                    'stderr': stderr,
                    'stdout': stdout,
                    'rc': rc}
        else:
            return {'gpg': False,
                    'stderr': 'Must specify a valid core and gpg key.',
                    'stdout': 'Must specify a valid core and gpg key.',
                    'rc': 1}

    def install(self, new_egg, new_egg_gpg_sig):
        """
        returns (dict): {'success': True if the core installation successfull else False}
        raises OSError if cannot create /var/lib/insights
        raises IOError if cannot copy /tmp/insights-core.egg to /var/lib/insights/newest.egg
        """

        # make sure a valid egg was provided
        if not new_egg:
            the_message = 'Must provide a valid Core installation path.'
            logger.debug(the_message)
            return {'success': False, 'message': the_message}

        # if running in gpg mode, check for valid sig
        if self.config.gpg and new_egg_gpg_sig is None:
            the_message = "Must provide a valid Core GPG installation path."
            logger.debug(the_message)
            return {'success': False, 'message': the_message}

        # debug
        logger.debug("Installing the new Core %s", new_egg)
        if self.config.gpg:
            logger.debug("Installing the new Core GPG Sig %s", new_egg_gpg_sig)

        # Make sure /var/lib/insights exists
        try:
            if not os.path.isdir(constants.insights_core_lib_dir):
                logger.debug("Creating directory %s for the Core." %
                             (constants.insights_core_lib_dir))
                os.mkdir(constants.insights_core_lib_dir)
        except OSError:
            logger.info("There was an error creating %s for core installation." % (
                constants.insights_core_lib_dir))
            raise

        # Copy the NEW (/tmp/insights-core.egg) egg to /var/lib/insights/newest.egg
        # Additionally, copy NEW (/tmp/insights-core.egg.asc) to /var/lib/insights/newest.egg.asc
        try:
            logger.debug("Copying %s to %s." % (new_egg, constants.insights_core_newest))
            shutil.copyfile(new_egg, constants.insights_core_newest)
            shutil.copyfile(new_egg_gpg_sig, constants.insights_core_gpg_sig_newest)
        except IOError:
            logger.info("There was an error copying the new core from %s to %s." % (
                new_egg, constants.insights_core_newest))
            raise

        logger.debug("The new Insights Core was installed successfully.")
        return {'success': True}

    def delete_tmpdir(self):
        if self.tmpdir:
            logger.debug("Deleting temp directory %s." % (self.tmpdir))
            shutil.rmtree(self.tmpdir, True)

    @_net
    def update_rules(self):
        """
            returns (dict): new client rules
        """
        if self.config.offline or not self.config.auto_update:
            logger.debug("Bypassing rule update due to config "
                "running in offline mode or auto updating turned off.")
        else:
            return client.update_rules(self.config, self.connection)

    @_net
    def collect(self):
        # return collection results
        tar_file = client.collect(self.config)

        # it is important to note that --to-stdout is utilized via the wrapper RPM
        # this file is received and then we invoke shutil.copyfileobj
        return tar_file

    @_net
    def register(self):
        """
            returns (bool | None):
                True - machine is registered
                False - machine is unregistered
                None - could not reach the API
        """
        return client.handle_registration(self.config, self.connection)

    @_net
    def unregister(self):
        """
            returns (bool): True success, False failure
        """
        return client.handle_unregistration(self.config, self.connection)

    @_net
    def upload(self, payload=None, content_type=None):
        """
            Upload the archive at `path` with content type `content_type`
            returns (int): upload status code
        """
        # platform - prefer the value passed in to func over config
        payload = payload or self.config.payload
        content_type = content_type or self.config.content_type

        if payload is None:
            raise ValueError('Specify a file to upload.')

        if not os.path.exists(payload):
            raise IOError('Cannot upload %s: File does not exist.' % payload)

        upload_results = client.upload(
            self.config, self.connection, payload, content_type)

        # return api response
        return upload_results

    def rotate_eggs(self):
        """
            moves newest.egg to last_stable.egg
            this is used by the upload() function upon 2XX return
            returns (bool): if eggs rotated successfully
            raises (IOError): if it cant copy the egg from newest to last_stable
        """
        # make sure the library directory exists
        if os.path.isdir(constants.insights_core_lib_dir):
            # make sure the newest.egg exists
            if os.path.isfile(constants.insights_core_newest):
                # try copying newest to latest_stable
                try:
                    # copy the core
                    shutil.move(constants.insights_core_newest,
                             constants.insights_core_last_stable)
                    # copy the core sig
                    shutil.move(constants.insights_core_gpg_sig_newest,
                             constants.insights_core_last_stable_gpg_sig)
                except IOError:
                    message = ("There was a problem copying %s to %s." %
                                (constants.insights_core_newest,
                                constants.insights_core_last_stable))
                    logger.debug(message)
                    raise IOError(message)
                return True
            else:
                message = ("Cannot copy %s to %s because %s does not exist." %
                            (constants.insights_core_newest,
                            constants.insights_core_last_stable,
                            constants.insights_core_newest))
                logger.debug(message)
                return False
        else:
            logger.debug("Cannot copy %s to %s because the %s directory does not exist." %
                (constants.insights_core_newest,
                    constants.insights_core_last_stable,
                    constants.insights_core_lib_dir))
            logger.debug("Try installing the Core first.")
            return False

    def get_last_upload_results(self):
        """
            returns (json): returns last upload json results or False
        """
        if os.path.isfile(constants.last_upload_results_file):
            logger.debug('Last upload file %s found, reading results.', constants.last_upload_results_file)
            with open(constants.last_upload_results_file, 'r') as handler:
                return handler.read()
        else:
            logger.debug('Last upload file %s not found, cannot read results', constants.last_upload_results_file)
            return False

    @_net
    def get_registration_status(self):
        """
            returns (json):
                {'messages': [dotfile message, api message],
                 'status': (bool) registered = true; unregistered = false
                 'unreg_date': Date the machine was unregistered | None,
                 'unreachable': API could not be reached}
        """
        return client.get_registration_status(self.config, self.connection)

    @_net
    def set_display_name(self, display_name):
        '''
            returns True on success, False on failure
        '''
        return self.connection.set_display_name(display_name)

    @_net
    def set_ansible_host(self, ansible_host):
        '''
            returns True on success, False on failure
        '''
        return self.connection.set_ansible_host(ansible_host)

    @_net
    def get_diagnosis(self, remediation_id=None):
        '''
            returns JSON of diagnosis data on success, None on failure
            Optional arg remediation_id to get a particular remediation set.
        '''
        if self.config.offline:
            logger.error('Cannot get diagnosis in offline mode.')
            return None
        return self.connection.get_diagnosis(remediation_id)

    def delete_cached_branch_info(self):
        '''
            Deletes cached branch_info file
        '''
        if os.path.isfile(constants.cached_branch_info):
            logger.debug('Deleting cached branch_info file...')
            os.remove(constants.cached_branch_info)
        else:
            logger.debug('Cached branch_info file does not exist.')

    def get_machine_id(self):
        return client.get_machine_id()

    @_net
    def check_results(self):
        content = self.connection.get_advisor_report()
        if content is None:
            raise Exception("Error: failed to download advisor report.")

    def show_results(self):
        '''
        Show insights about this machine
        '''
        try:
            with open("/var/lib/insights/insights-details.json", mode="r+b") as f:
                insights_data = json.load(f)
            print(json.dumps(insights_data, indent=1))
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise Exception("Error: no report found. Run insights-client --check-results to update the report cache: %s" % e)
            else:
                raise e

    def show_inventory_deep_link(self):
        """
        Show a deep link to this host inventory record
        """
        system = self.connection._fetch_system_by_machine_id()
        if system:
            if len(system) == 1:
                try:
                    id = system[0]["id"]
                    logger.info("View details about this system on console.redhat.com:")
                    logger.info(
                        "https://console.redhat.com/insights/inventory/{0}".format(id)
                    )
                except Exception as e:
                    logger.error(
                        "Error: malformed system record: {0}: {1}".format(system, e)
                    )

    def _copy_soscleaner_files(self, insights_archive):
        '''
        Helper function to copy the .csv reports generated by SOScleaner

        Parameters:
            insights_archive - source path of the scrubbed data in temp
        '''
        src_dir = os.path.dirname(insights_archive)
        dst_file_prefix = self.config.output_dir if self.config.output_dir else self.config.output_file

        for fil in os.listdir(src_dir):
            if fil.endswith('.csv'):
                file_suffix = fil.rsplit('-', 1)[1]
                src_path = os.path.join(src_dir, fil)
                dst_path = dst_file_prefix + '-' + file_suffix
                try:
                    if os.path.exists(dst_path):
                        # don't overwrite anything arbitrary
                        raise OSError('%s already exists.' % dst_path)
                    logger.debug('Copying SOScleaner report from %s to %s', src_path, dst_path)
                    shutil.copyfile(src_path, dst_path)
                    logger.info('SOScleaner report copied to %s', dst_path)
                except OSError as e:
                    logger.error('ERROR: Could not write data to %s', dst_path)
                    logger.error(e)

    def copy_to_output_dir(self, insights_archive):
        '''
        Copy the collected data from temp to the directory
        specified by --output-dir

        Parameters:
            insights_archive - the path to the collected dir
        '''
        logger.debug('Copying collected data from %s to %s',
                     insights_archive, self.config.output_dir)
        try:
            shutil.copytree(insights_archive, self.config.output_dir)
        except OSError as e:
            if e.errno == 17:
                # dir exists already, see if it's empty
                if os.listdir(self.config.output_dir):
                    # we should never get here because of the check in config.py, but just in case
                    logger.error('ERROR: Could not write data to %s.', self.config.output_dir)
                    logger.error(e)
                    return
                else:
                    # if it's empty, copy the contents to it
                    for fil in os.listdir(insights_archive):
                        src_path = os.path.join(insights_archive, fil)
                        dst_path = os.path.join(self.config.output_dir, fil)
                        try:
                            if os.path.isfile(src_path):
                                shutil.copyfile(src_path, dst_path)
                            elif os.path.isdir(src_path):
                                shutil.copytree(src_path, dst_path)
                        except OSError as e:
                            logger.error(e)
                            # in case this happens partway through let the user know
                            logger.warning('WARNING: Directory copy may be incomplete.')
                            return
            else:
                # some other error
                logger.error(e)
                return
        logger.info('Collected data copied to %s', self.config.output_dir)
        if self.config.obfuscate:
            self._copy_soscleaner_files(insights_archive)

    def copy_to_output_file(self, insights_archive):
        '''
        Copy the collected archive from temp to the file
        specified by output-file

        insights_archive - the path to the collected archive
        '''
        logger.debug('Copying archive from %s to %s',
                     insights_archive, self.config.output_file)
        try:
            shutil.copyfile(insights_archive, self.config.output_file)
        except OSError as e:
            # file exists already
            logger.error('ERROR: Could not write data to %s', self.config.output_file)
            logger.error(e)
            return
        logger.info('Collected data copied to %s', self.config.output_file)
        if self.config.obfuscate:
            self._copy_soscleaner_files(insights_archive)

    def initialize_tags(self):
        '''
        Initialize the tags file if needed
        '''
        # migrate the old file if necessary
        migrate_tags()

        # initialize with group if group was specified
        if self.config.group:
            tags = get_tags()
            if tags is None:
                tags = {}
            tags["group"] = self.config.group
            write_tags(tags)

    def list_specs(self):
        logger.info("For a full list of insights-core datasources, please refer to https://insights-core.readthedocs.io/en/latest/specs_catalog.html")
        logger.info("The items in General Datasources can be selected for omission by adding them to the 'components' section of file-redaction.yaml")
        logger.info("When specifying these items in file-redaction.yaml, they must be prefixed with 'insights.specs.default.DefaultSpecs.', i.e. 'insights.specs.default.DefaultSpecs.httpd_V'")
        logger.info("This information applies only to Insights Core collection. To use Core collection, set core_collect=True in %s", self.config.conf)

    @_net
    def checkin(self):
        if self.config.offline:
            logger.error('Cannot check-in in offline mode.')
            return None

        return self.connection.checkin()


def format_config(config):
    # Log config except the password
    # and proxy as it might have a pw as well
    config_copy = config.copy()
    try:
        del config_copy["password"]
        del config_copy["proxy"]
    finally:
        return json.dumps(config_copy, indent=4)


def _init_client_config_dirs():
    '''
    Initialize log and lib dirs
    TODO: init non-root config dirs
    '''
    for d in (constants.log_dir, constants.insights_core_lib_dir):
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno == errno.EEXIST:
                # dir exists, this is OK
                pass
            else:
                raise e


def _write_pid_files():
    for file, content in (
        (constants.pidfile, str(os.getpid())),  # PID in case we need to ping systemd
        (constants.ppidfile, get_parent_process())  # PPID so that we can grab the client execution method
    ):
        write_to_disk(file, content=content)
        atexit.register(write_to_disk, file, delete=True)
