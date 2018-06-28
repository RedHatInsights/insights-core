import json
import os
import logging
import tempfile
import shlex
import shutil
from subprocess import Popen, PIPE

from .. import package_info
from . import client
from .constants import InsightsConstants as constants
from .config import InsightsConfig

logger = logging.getLogger(__name__)
net_logger = logging.getLogger("network")


class InsightsClient(object):

    def __init__(self, config, setup_logging=True, **kwargs):
        """
        The Insights client interface
        """
        #  small hack to maintain compatability with RPM wrapper
        if isinstance(config, InsightsConfig):
            self.config = config
        else:
            self.config = InsightsConfig().load_all()
        # end hack. in the future, just set self.config=config

        # set up logging
        if setup_logging:
            self.set_up_logging()

        # setup insights connection placeholder
        # used for requests
        self.session = None
        self.connection = None

    def get_conf(self):
        # need this getter to maintain compatability with RPM wrapper
        return self.config

    def set_up_logging(self):
        return client.set_up_logging(self.config)

    def version(self):
        return "%s-%s" % (package_info["VERSION"], package_info["RELEASE"])

    def test_connection(self):
        """
            returns (int): 0 if success 1 if failure
        """
        return client.test_connection()

    def branch_info(self):
        """
            returns (dict): {'remote_leaf': -1, 'remote_branch': -1}
        """
        return client.get_branch_info()

    def handle_startup(self):
        return client.handle_startup()

    def fetch(self, force=False):
        """
            returns (dict): {'core': path to new egg, None if no update,
                             'gpg_sig': path to new sig, None if no update}
        """
        tmpdir = tempfile.mkdtemp()
        fetch_results = {
            'core': os.path.join(tmpdir, 'insights-core.egg'),
            'gpg_sig': os.path.join(tmpdir, 'insights-core.egg.asc')
        }

        logger.debug("Beginning core fetch.")

        # run fetch for egg
        updated = self._fetch(self.config.egg_path,
                              constants.core_etag_file,
                              fetch_results['core'],
                              force)

        # if new core was fetched, get new core sig
        if updated:
            logger.debug("New core was fetched.")
            logger.debug("Beginning fetch for core gpg signature.")
            self._fetch(self.config.egg_gpg_path,
                        constants.core_gpg_sig_etag_file,
                        fetch_results['gpg_sig'],
                        force)

            return fetch_results

    def _fetch(self, path, etag_file, target_path, force):
        """
            returns (str): path to new egg. None if no update.
        """
        # setup a request session
        if not self.session:
            self.connection = client.get_connection(self.config)
            self.session = self.connection.session

        url = self.connection.base_url + path
        # Searched for cached etag information
        current_etag = None
        if os.path.isfile(etag_file):
            with open(etag_file, 'r') as fp:
                current_etag = fp.read().strip()
                logger.debug('Found etag %s', current_etag)

        # Setup the new request for core retrieval
        logger.debug('Making request to %s for new core', url)

        # If the etag was found and we are not force fetching
        # Then add it to the request
        net_logger.info("GET %s", url)
        if current_etag and not force:
            logger.debug('Requesting new file with etag %s', current_etag)
            etag_headers = {'If-None-Match': current_etag}
            response = self.session.get(url, headers=etag_headers)
        else:
            logger.debug('Found no etag or forcing fetch')
            response = self.session.get(url)

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

    def update_rules(self):
        """
            returns (dict): new client rules
        """
        if self.config.offline or not self.config.auto_update:
            logger.debug("Bypassing rule update due to config "
                "running in offline mode or auto updating turned off.")
        else:
            return client.update_rules(self.config)

    def collect(self):
        # return collection results
        tar_file = client.collect(self.config)

        # it is important to note that --to-stdout is utilized via the wrapper RPM
        # this file is received and then we invoke shutil.copyfileobj
        return tar_file

    def register(self, force_register=False):
        """
            returns (json): {'success': bool,
                            'machine-id': uuid from API,
                            'response': response from API,
                            'code': http code}
        """
        self.config.register = True
        if force_register:
            self.config.reregister = True
        return client.handle_registration()

    def unregister(self):
        """
            returns (bool): True success, False failure
        """
        return client.handle_unregistration()

    def get_registration_information(self):
        """
            returns (json): {'machine-id': uuid from API,
                            'response': response from API}
        """
        registration_status = client.get_registration_status()
        return {'machine-id': client.get_machine_id(),
                'registration_status': registration_status,
                'is_registered': registration_status['status']}

    def upload(self, path, rotate_eggs=True):
        """
            returns (int): upload status code
        """
        # do the upload
        upload_results = client.upload(self.config, path)
        if upload_results:

            # delete the archive
            if self.config.keep_archive:
                logger.info('Insights archive retained in ' + path)
            else:
                client.delete_archive(path)

            # if we are rotating the eggs and success on upload do rotation
            if rotate_eggs:
                try:
                    self.rotate_eggs()
                except IOError:
                    message = ("Failed to rotate %s to %s" %
                               (constants.insights_core_newest,
                                constants.insights_core_last_stable))
                    logger.debug(message)
                    raise IOError(message)

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

    def delete_archive(self, path):
        """
            returns (bool): successful archive deletion
        """
        return client.delete_archive(path)

    def _is_client_registered(self):
        return client._is_client_registered(self.config)

    def try_register(self):
        return client.try_register(self.config)

    def get_connection(self):
        return client.get_connection(self.config)


def format_config(config):
    # Log config except the password
    # and proxy as it might have a pw as well
    config_copy = config.copy()
    try:
        del config_copy["password"]
        del config_copy["proxy"]
    finally:
        return json.dumps(config_copy, indent=4)
