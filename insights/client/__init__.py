import requests
from . import client
from .constants import InsightsConstants as constants
from .auto_config import try_auto_configuration
from .client_config import InsightsClient
import logging

LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")
APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)
handler = None


class InsightsClientApi(object):

    def __init__(self, options=None, config=None):
        """
            Intialize an instance of the Insights Client API for the Core
            params:
                (optional) options=dict
                (optional) config=dict
            returns:
                InsightsClientApi()
        """

        # Overwrite anything passed in
        if options:
            for key in options:
                setattr(InsightsClient.options, key, options[key])
        if config:
            for new_config_var in config:
                InsightsClient.config.set(constants.app_name,
                                          new_config_var,
                                          config[new_config_var])

        # Disable GPG verification
        if InsightsClient.options.no_gpg:
            logger.warn("WARNING: GPG VERIFICATION DISABLED")
            InsightsClient.config.set(APP_NAME, 'gpg', 'False')

        # Log config except the password
        # and proxy as it might have a pw as well
        for item, value in InsightsClient.config.items(APP_NAME):
            if item != 'password' and item != 'proxy':
                logger.debug("%s:%s", item, value)

    def version(self):
        """
            returns (dict): {'core': str,
                            'client_api': str}
        """
        from .. import get_nvr
        core_version = get_nvr()
        client_api_version = constants.version

        return {'core': core_version, 'client_api': client_api_version}

    def test_connection(self):
        """
            returns (int): 0 if success 1 if failure
        """
        try_auto_configuration()
        return client.test_connection()

    def handle_startup(self):
        try_auto_configuration()
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
        if not InsightsClient.options.offline and not is_registered:
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

            results = self.collect(collection_format)
            logger.debug('Results: %s', results)
        else:
            logger.debug('New Core was not verified, not collecting information.')
            results = False

        # Upload things
        if not skip_upload and not InsightsClient.options.no_upload and not InsightsClient.options.offline and is_registered:
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
        if InsightsClient.options.core_url:
            egg_url = InsightsClient.options.core_url

        # Searched for cached etag information
        current_etag = None
        import os
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
            import tempfile
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

    def verify(self,
               egg_path,
               gpg_key=constants.default_egg_gpg_key):
        """
            returns (dict): {'gpg': if the egg checks out,
                             'stderr': error message if present,
                             'stdout': stdout,
                             'rc': return code}
        """
        if egg_path and gpg_key:
            from subprocess import Popen, PIPE
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
        import os
        from shutil import copyfile

        if not new_egg:
            the_message = 'Must provide a valid Core installation path.'
            logger.debug(the_message)
            return {'success': False, 'message': the_message}

        logger.debug("Installing the new Core %s", new_egg)

        # Make sure /var/lib/insights exists
        try:
            if not os.path.isdir(constants.insights_core_lib_dir):
                logger.debug("Creating directory %s for the Core."
                    % (constants.insights_core_lib_dir))
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
        try_auto_configuration()
        return client.update_rules()

    def fetch_rules(self, options=None, config=None):
        """
            returns (dict): existing client rules
        """
        try_auto_configuration()
        return client.fetch_rules()

    def collect(self, format="json", options=None, config=None):
        """
            returns (str, json): will return a string path to archive, or json facts
        """
        return client.collect()

    def register(self, force_register=False):
        """
            returns (json): {'success': bool,
                            'machine-id': uuid from API,
                            'response': response from API,
                            'code': http code}
        """
        try_auto_configuration()
        setattr(InsightsClient.options, 'register', True)
        if force_register:
            setattr(InsightsClient.options, 'reregister', True)
        return client.handle_registration()

    def unregister(self):
        """
            returns (bool): True success, False failure
        """
        try_auto_configuration()
        return client.handle_unregistration()

    def get_registration_information(self):
        """
            returns (json): {'machine-id': uuid from API,
                            'response': response from API}
        """
        try_auto_configuration()
        registration_status = client.get_registration_status()
        return {'machine-id': client.get_machine_id(),
                'registration_status': registration_status,
                'is_registered': registration_status['status']}

    def get_conf(self):
        """
            returns (optparse): OptParse config/options
        """
        return InsightsClient

    def upload(self, path):
        """
            returns (int): upload status code
        """
        try_auto_configuration()
        return client.upload(path)

    def get_last_upload_results(self):
        """
            returns (json): returns last upload json results or False
        """
        import os
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
    # Setup the base config and options
    InsightsClient.config, InsightsClient.options = client.parse_options()
    client.set_up_logging()
    try_auto_configuration()
    status = client.handle_startup()
    if status:
        logger.info("Returning early due to initialization response: %s", status)
        return status
    else:
        try:
            c = InsightsClientApi()
            return getattr(c, op)(*args, **kwargs)
        except:
            logger.exception("Fatal error")


def update():
    pass


def collect():
    run("collect")


def upload():
    pass
