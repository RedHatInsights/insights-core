import os
import sys
import logging
import tempfile
import time
import shlex
from subprocess import Popen, PIPE
from shutil import copyfile

from .. import get_nvr
from . import client
from .constants import InsightsConstants as constants
from .auto_config import try_auto_configuration
from .config import CONFIG as config, compile_config

LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")
APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger("network")


class InsightsClient(object):

    def __init__(self, read_config=True, **kwargs):
        """
            Arguments:
                read_config: Whether or not to read config files to
                  determine configuration.  If False, defaults are
                  assumed and can be overridden programmatically.
        """
        if read_config:
            compile_config()

        invalid_keys = [k for k in kwargs if k not in config]
        if invalid_keys:
            raise ValueError("Invalid argument(s): %s" % invalid_keys)

        for key, value in kwargs.items():
            config[key] = value

        # set up logging
        client.set_up_logging()

        # Log config except the password
        # and proxy as it might have a pw as well
        if logging.root.level == logging.DEBUG:
            config_log = logging.getLogger("Insights Config")
            for item, value in config.items():
                if item != 'password' and item != 'proxy':
                    config_log.debug("%s:%s", item, value)

        # setup insights connection placeholder
        # used for requests
        self.session = None
        self.connection = None

    def version(self):
        """
            returns (dict): {'core': str,
                            'client_api': str}
        """
        core_version = get_nvr()
        client_api_version = constants.version

        return {'core': core_version, 'client_api': client_api_version}

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

    def fetch(self,
              egg_url=constants.egg_path,
              gpg_sig_url=constants.gpg_sig_path,
              force=False):
        """
            returns (dict): {'core': path to new egg, None if no update,
                             'gpg_sig': path to new sig, None if no update}
        """
        # was a custom egg url passed in?
        if config['core_url']:
            egg_url = config['core_url']

        # was a custom gpg_sig_url passed?
        if config['gpg_sig_url']:
            gpg_sig_url = config['gpg_sig_url']

        tmpdir = tempfile.mkdtemp()
        fetch_results = {
            'core': os.path.join(tmpdir, 'insights-core.egg'),
            'gpg_sig': os.path.join(tmpdir, 'insights-core.egg.asc')
        }

        logger.debug("Beginning core fetch.")

        # run fetch for egg
        updated = self._fetch(egg_url,
                              constants.core_etag_file,
                              fetch_results['core'],
                              force)

        # if new core was fetched, get new core sig
        if updated:
            logger.debug("New core was fetched.")
            logger.debug("Beginning fetch for core gpg signature.")
            self._fetch(gpg_sig_url,
                        constants.core_gpg_sig_etag_file,
                        fetch_results['gpg_sig'],
                        force)

        # return new core path and gpg sig or None
        return fetch_results

    def _fetch(self, url, etag_file, target_path, force):
        """
            returns (str): path to new egg. None if no update.
        """
        # setup a request session
        if not self.session:
            self.connection = client.get_connection()
            self.session = self.connection.session

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
        for header, value in response.headers.iteritems():
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
        egg_path = self.fetch()
        if (egg_path.get('core') is not None and self.verify(egg_path['core'])['gpg']):
            return self.install(egg_path['core'], egg_path['gpg_sig'])
        else:
            return False

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
        if not new_egg:
            the_message = 'Must provide a valid Core installation path.'
            logger.debug(the_message)
            return {'success': False, 'message': the_message}

        logger.debug("Installing the new Core %s", new_egg)

        # Make sure /var/lib/insights exists
        try:
            if not os.path.isdir(constants.insights_core_lib_dir):
                logger.debug("Creating directory %s for the Core." %
                             (constants.insights_core_lib_dir))
                os.mkdir(constants.insights_core_lib_dir)
        except OSError:
            message = "There was an error creating %s for Core installation." %\
                (constants.insights_core_lib_dir)
            raise OSError(message)

        # Copy the NEW (/tmp/insights-core.egg) egg to /var/lib/insights/newest.egg
        try:
            logger.debug("Copying %s to %s." % (new_egg, constants.insights_core_newest))
            copyfile(new_egg, constants.insights_core_newest)
            copyfile(new_egg_gpg_sig, constants.insights_core_gpg_sig_newest)
        except IOError:
            message = "There was an error copying the new Core from %s to %s." %\
                (new_egg, constants.insights_core_newest)
            raise IOError(message)

        logger.debug("The new Insights Core was installed successfully.")
        return {'success': True}

    def update_rules(self):
        """
            returns (dict): new client rules
        """
        if config['update']:
            return client.update_rules()
        else:
            logger.debug("Bypassing rule update due to config")

    def fetch_rules(self):
        """
            returns (dict): existing client rules
        """
        return client.fetch_rules()

    def _cached_results(self):
        # archive_tmp_dir and .lastcollected must both exist
        file_name = constants.archive_last_collected_date_file
        if not os.path.isfile(file_name):
            return

        # get .lastcollected timestamp and archive
        # .lastcollected contains the timestamp on the first line
        # .lastcollected contains the archive path and name on the second line
        with open(file_name) as coll_file:
            try:
                lastcollected = int(float(coll_file.readline().strip()))
                logger.debug("Found last collected timestamp %s." % (lastcollected))
            except ValueError:
                logger.debug("Invalid last collected timestamp detected.")
                lastcollected = 0
            last_collected_archive = coll_file.readline().strip()

        # make sure the archive actually exists on the filesystem
        if not os.path.isfile(last_collected_archive):
            logger.debug("Found last collected archive %s in .lastcollected"
                         " but file does not exist" % (last_collected_archive))
            return
        else:
            logger.debug("Found last collected archive %s." % (last_collected_archive))

        # get the latest archive if .lastcollected is < 24hrs
        try:
            hours_since_last_collection = (time.time() - lastcollected) / 3600
            logger.debug("Hours since last collection: %s" % (hours_since_last_collection))
            if (hours_since_last_collection) < 24:
                logger.debug("Time since last collection is less than 24 hours.")
                logger.debug("Latest archive %s found." % (last_collected_archive))
                return last_collected_archive
            else:
                logger.debug("Last time collected greater than 24 hours")

        except:
            logger.debug("There was an error with the last collected timestamp"
                         " file or archives.")

    def collect(self, **kwargs):
        """
            kwargs: check_timestamp=True,
                    image_id=UUID,
                    tar_file=/path/to/tar,
                    mountpoint=/path/to/mountpoint
            returns (str, json): will return a string path to archive, or json facts
        """
        # check if we are scanning a host or scanning one of the following:
        # image/container running in docker
        # tar_file
        # OR a mount point (FS that is already mounted somewhere)
        if (kwargs.get('image_id') or kwargs.get('tar_file') or kwargs.get('mountpoint')):
            logger.debug('Not scanning host.')

        # setup other scanning cases
        # scanning images/containers running in docker
        if kwargs.get('image_id'):
            logger.debug('Scanning an image id.')
            config['container_mode'] = True
            config['only'] = kwargs.get('image_id')

        # compressed filesystems (tar files)
        if kwargs.get('tar_file'):
            logger.debug('Scanning a tar file.')
            config['container_mode'] = True
            config['analyze_compressed_file'] = kwargs.get('tar_file')

        # FSs already mounted somewhere
        if kwargs.get('mountpoint'):
            logger.debug('Scanning a mount point.')
            config['container_mode'] = True
            config['mountpoint'] = kwargs.get('mountpoint')

        # If check_timestamp is not flagged
        # bypass timestamp checks for other cases
        if kwargs.get('check_timestamp', True):
            logger.debug('Check timestamp is True.')
            cached_results = self._cached_results()
            if cached_results:
                logger.info("Using cached collection: %s", cached_results)

                # it is important to note that --to-stdout is utilized via the wrapper RPM
                # this file is received and then we invoke shutil.copyfileobj
                return cached_results
        else:
            logger.debug("Collection timestamp check bypassed. Now collecting.")

        # return collection results
        tar_file = client.collect()

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
        config['register'] = True
        if force_register:
            config['reregister'] = True
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

    def get_conf(self):
        """
            returns (optparse): OptParse config/options
        """
        return config

    def upload(self, path, rotate_eggs=True):
        """
            returns (int): upload status code
        """
        # do the upload
        upload_results = client.upload(path)

        if upload_results['status'] == 201:
            if not config['keep_archive']:
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

        # return status code
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
                    copyfile(constants.insights_core_newest,
                             constants.insights_core_last_stable)
                    # copy the core sig
                    copyfile(constants.insights_core_gpg_sig_newest,
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


def run(op, *args, **kwargs):
    compile_config()
    client.set_up_logging()
    try_auto_configuration()
    status = client.handle_startup()
    if status is not None:
        logger.debug("Returning early due to initialization response: %s", status)
        print "STDOUTRESPONSE: %s" % (status if type(status) in (str, unicode) else "")
        return
    else:
        try:
            c = InsightsClient()
            return getattr(c, op)(*args, **kwargs)
        except:
            logger.exception("Fatal error")
            sys.exit(1)


def update():
    if run("update") is not None:
        # Only update rules if InsightsClient.update() was called
        # handle_startup() could have returned early
        try:
            c = InsightsClient(read_config=False)
            c.update_rules()
        except:
            logger.exception("Fatal error")
            sys.exit(1)


def collect():
    print run("collect", check_timestamp=config["check_timestamp"],
                         image_id=(config["image_id"] or config["only"]),
                         tar_file=config["tar_file"],
                         mountpoint=config["mountpoint"])


def upload():
    egg_path = sys.stdin.read().strip()
    if config["to_json"]:
        print "STDOUTRESPONSE: %s" % (str(run("upload", egg_path)))
    else:
        run("upload", egg_path)
