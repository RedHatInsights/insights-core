import os
import sys
import requests
import logging
import tempfile
import time
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
handler = None


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

    def handle_startup(self):
        return client.handle_startup()

    def run(self,
            egg_url=constants.egg_path,
            gpg_key=constants.default_egg_gpg_key,
            collection_format='json',
            skip_update=False,
            skip_verify=False,
            skip_upload=False,
            force_fetch=False,
            force_register=False,
            update_rules=True):
        """
            do everything
        """
        new_egg = None
        verification = True
        results = None
        registration = None

        # Update things
        if not skip_update:
            new_egg = self.fetch(egg_url, force_fetch)
            logger.debug('Fetching new core: %s', new_egg)

        # Verify things
        if new_egg and not skip_verify:
            verification = self.verify(new_egg, gpg_key)
            logger.debug('Core was verified: %s', verification)

        # Need to install the new Core here
        if new_egg and verification['gpg']:
            installation = self.install(new_egg)
            logger.debug('Core installation: %s', installation)
            # Return 42 to the wrapper
            # Indicates we want to stop execution and start the new Client
            if installation['success']:
                return 42
            else:
                logger.debug('There was an error installing the new core.')
        else:
            logger.debug('New egg was not retrieved or was retrieved but failed verification.')
            logger.debug('Egg retrieval: %s', new_egg)
            logger.debug('Verification: %s', verification)

        # Register
        is_registered = self.get_registration_information()['is_registered']
        logger.debug('System is registered: %s', is_registered)
        if not config['offline'] and not is_registered:
            registration = self.register(force_register)
            is_registered = registration['registration']['status']
            logger.debug('Registration response: %s', registration)
            logger.debug('System is now registered: %s', is_registered)

        # Collect things
        if verification:
            logger.debug('New Core was verified. Collecting information.')

            if update_rules:
                logger.debug("Updating rules.")
                self.update_rules()  # won't be needed after we move to new egg format

            results = self.collect()
            logger.debug('Results: %s', results)
        else:
            logger.debug('New Core was not verified, not collecting information.')
            results = False

        # Upload things
        if not skip_upload and not config['no_upload'] and not config['offline'] and is_registered:
            logger.debug('Not skipping upload, or running offline.')
            logger.debug('System is registered, proceeding with upload.')
            upload_results = self.upload(results)
            logger.debug('Upload results: %s', upload_results)
        else:
            logger.debug('Skipping upload, running offline, or system is not properly registered.')
            logger.debug('Skipping upload.')
            logger.debug('Insights results: %s', results)
            return results

    def fetch(self,
              egg_url=constants.egg_path,
              force=False,
              verbose=False):
        """
            returns (str): path to new egg.  None if no update.
        """
        # was a custom egg url passed in?
        if config['core_url']:
            egg_url = config['core_url']

        # Searched for cached etag information
        current_etag = None
        if os.path.isfile(constants.core_etag_file):
            with open(constants.core_etag_file, 'r') as etag_file:
                current_etag = etag_file.read().strip()
                logger.debug('Found etag %s', current_etag)

        # Setup the new request for core retrieval
        logger.debug('Making request to %s for new core', egg_url)

        # If the etag was found and we are not force fetching
        # Then add it to the request
        if current_etag and not force:
            logger.debug('Requesting new core with etag %s', current_etag)
            response = requests.get(egg_url, headers={'If-None-Match': current_etag})
        else:
            logger.debug('Found no etag or forcing fetch')
            response = requests.get(egg_url)

        # Debug information
        logger.debug('status code: %d', response.status_code)
        for header, value in response.headers.iteritems():
            logger.debug('%s: %s', header, value)

        # Debug the ETag
        logger.debug('ETag: %s', response.request.headers.get('If-None-Match'))

        # If data was received, write the new egg and etag
        if response.status_code == 200 and len(response.content) > 0:

            # Setup tmp egg path
            tmpdir = tempfile.mkdtemp()
            tmp_egg_path = os.path.join(tmpdir, 'insights-core.egg')

            # Write the new core
            with open(tmp_egg_path, 'wb') as handle:
                logger.debug('Data received, writing core to %s', tmp_egg_path)
                handle.write(response.content)

            # Write the new etag
            with open(constants.core_etag_file, 'w') as etag_file:
                logger.debug('Cacheing etag to %s', constants.core_etag_file)
                etag_file.write(response.headers['etag'])

            # Return the tmp egg path
            return tmp_egg_path

        # Received a 304 not modified
        # Return nothing
        elif response.status_code == 304:
            logger.debug('No data received')
            logger.debug('Tags match, not updating core')
            return None

        # Something unexpected received
        else:
            logger.debug('Received Code %s', response.status_code)
            logger.debug('Not writing new core, or updating etag')
            logger.debug('Please check config, error reaching %s', egg_url)
            return None

    def update(self):
        egg_path = self.fetch()
        if egg_path and self.verify(egg_path):
            self.install(egg_path)

    def verify(self, egg_path, gpg_key=constants.default_egg_gpg_key):
        """
            returns (dict): {'gpg': if the egg checks out,
                             'stderr': error message if present,
                             'stdout': stdout,
                             'rc': return code}
        """
        if egg_path and gpg_key:
            process = Popen(['gpg', '--verify', gpg_key, egg_path], stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            rc = process.returncode
            success = True if rc == 0 else False
            return {'gpg': success,
                    'stderr': stderr,
                    'stdout': stdout,
                    'rc': rc}
        else:
            return {'gpg': False,
                    'stderr': 'Must specify a valid core and gpg key.',
                    'stdout': 'Must specify a valid core and gpg key.',
                    'rc': 1}

    def install(self, new_egg):
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
        except IOError:
            message = "There was an error copying the new Core from %s to %s." %\
                (new_egg, constants.insights_core_newest)
            raise IOError(message)

        logger.debug("The new Insights Core was installed successfully.")
        return {'success': True}

    def update_rules(self, options=None, config=None):
        """
            returns (dict): new client rules
        """
        return client.update_rules()

    def fetch_rules(self, options=None, config=None):
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
        scanning_host = True
        if (kwargs.get('image_id') or kwargs.get('tar_file') or kwargs.get('mountpoint')):
            scanning_host = False

        # setup other scanning cases
        # scanning images/containers running in docker
        if kwargs.get('image_id'):
            config['container_mode'] = True
            config['only'] = kwargs.get('image_id')

        # compressed filesystems (tar files)
        if kwargs.get('tar_file'):
            config['container_mode'] = True
            config['analyze_compressed_file'] = kwargs.get('tar_file')

        # FSs already mounted somewhere
        if kwargs.get('mountpoint'):
            config['container_mode'] = True
            config['mountpoint'] = kwargs.get('mountpoint')

        # If check_timestamp is not flagged, then skip this check AND
        # we are also scanning a host
        # bypass timestamp checks for other cases
        if kwargs.get('check_timestamp', True) and scanning_host:
            cached_results = self._cached_results()
            if cached_results:
                logger.info("Using cached collection: %s", cached_results)
                return cached_results
        else:
            logger.debug("Collection timestamp check bypassed. Now collecting.")

        # return collection results
        return client.collect()

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
        upload_status = client.upload(path)

        # if we are rotating the eggs and success on upload do rotation
        if rotate_eggs and upload_status == 201:
            try:
                self.rotate_eggs()
            except IOError:
                message = ("Failed to rotate %s to %s" %
                            (constants.insights_core_newest,
                            constants.insights_core_last_stable))
                logger.debug(message)
                raise IOError(message)

        # return status code
        return upload_status

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
                    copyfile(constants.insights_core_newest, constants.insights_core_last_stable)
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
        logger.info("Returning early due to initialization response: %s", status)
        return status
    else:
        try:
            c = InsightsClient()
            return getattr(c, op)(*args, **kwargs)
        except:
            logger.exception("Fatal error")


def update():
    run("update")


def collect():
    print run("collect")


def upload():
    egg_path = sys.stdin.read().strip()
    run("upload", egg_path)
