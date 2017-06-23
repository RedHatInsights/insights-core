import optparse
import urllib2
from . import client
from .constants import InsightsConstants as constants
from .auto_config import try_auto_configuration
from .client_config import parse_config_file, InsightsClient, set_up_options
import logging

LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")
APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)
handler = None


def version():
    '''
    returns (dict): {'core': str,
                    'client_api': str}
    '''
    from .. import get_nvr
    core_version = get_nvr()
    client_api_version = constants.version

    return {'core': core_version,
        'client_api': client_api_version}


def run(egg_url=constants.egg_path,
        gpg_key=constants.default_egg_gpg_key,
        collection_format='json',
        options=None,
        config=None,
        skip_update=False,
        skip_verify=False,
        skip_upload=False,
        force_fetch=False):
    '''
        do everything
    '''
    new_egg = None
    verification = True
    results = None
    if not skip_update:
        new_egg = fetch(egg_url, force_fetch)
    if new_egg and not skip_verify:
        verification = verify(new_egg, gpg_key)
    if verification:
        results = collect(collection_format, options, config)
    else:
        results = False
    if not skip_upload:
        return upload(results)
    else:
        return results


def parse_options():
    '''
        returns (tuple): returns a tuple with configparser and argparser options
    '''
    parser = optparse.OptionParser()
    set_up_options(parser)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unknown arguments: %s" % args)
    return parse_config_file(options.conf), options


def fetch(egg_url=constants.egg_path, force=False, verbose=False):
    """
        returns (str): path to new egg.  None if no update.
    """
    # Setup the config and options
    InsightsClient.config, InsightsClient.options = parse_options()
    if verbose:
        setattr(InsightsClient.options, 'verbose', True)
    client.set_up_logging()

    # Searched for cached etag information
    current_etag = None
    import os
    if os.path.isfile(constants.core_etag_file):
        with open(constants.core_etag_file, 'r') as etag_file:
            current_etag = etag_file.read().strip()
            logger.debug('Found etag %s', current_etag)

    # Setup the new request for core retrieval
    logger.debug('Making request to %s for new core', egg_url)
    request = urllib2.Request(egg_url)

    # If the etag was found and we are not force fetching
    # Then add it to the request
    if current_etag and not force:
        logger.debug('Requesting new core with etag %s', current_etag)
        request.add_header('If-None-Match', current_etag)
    else:
        logger.debug('Found no etag or forcing fetch')

    # Initialize the data stream
    opener = urllib2.build_opener(DefaultErrorHandler())
    datastream = opener.open(request)
    data = datastream.read()

    # Debug information
    if datastream:
        for attr in ['status', 'code', 'message', 'msg']:
            if hasattr(datastream, attr):
                logger.debug('%s: %s', attr, getattr(datastream, attr))
        if datastream.headers:
            for header in datastream.headers.dict:
                logger.debug('%s: %s', header, datastream.headers.dict[header])

    # If data was received, write the new egg and etag
    if data and datastream.code == 200:

        # Setup tmp egg path
        import tempfile
        tmpdir = tempfile.mkdtemp()
        tmp_egg_path = os.path.join(tmpdir, 'insights-core.egg')

        # Write the new core
        with open(tmp_egg_path, 'wb') as handle:
            logger.debug('Data received, writing core to %s', tmp_egg_path)
            handle.write(data)

        # Write the new etag
        with open(constants.core_etag_file, 'w') as etag_file:
            logger.debug('Cacheing etag to %s', constants.core_etag_file)
            etag_file.write(datastream.headers.dict['etag'])

        # Return the tmp egg path
        return tmp_egg_path

    # Received a 304 not modified
    # Return nothing
    elif datastream.code == 304:
        logger.debug('No data received')
        logger.debug('Tags match, not updating core')
        return None

    # Something unexpected received
    else:
        logger.debug('Received Code %s', datastream.code)
        logger.debug('Not writing new core, or updating etag')
        logger.debug('Please check config, error reaching %s', egg_url)
        return None


class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
        def http_error_default(self, req, fp, code, msg, headers):
            result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
            result.status = code
            return result


def verify(egg_path, gpg_key=constants.default_egg_gpg_key):
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


def fetch_rules(options=None, config=None):
    '''
        returns (dict): new client rules
    '''
    InsightsClient.config, InsightsClient.options = parse_options()
    try_auto_configuration()
    return client.fetch_rules()


def collect(format="json", options=None, config=None):
    '''
        returns (str, json): will return a string path to archive, or json facts
    '''
    InsightsClient.config, InsightsClient.options = parse_options()
    if options:
        for key in options:
            setattr(InsightsClient.options, key, options[key])
    if config:
        for new_config_var in config:
            InsightsClient.config.set(constants.app_name, new_config_var, config[new_config_var])
    return client.collect()


def upload(path):
    InsightsClient.config, InsightsClient.options = parse_options()
    try_auto_configuration()
    return client.upload(path)


def delete_archive(path):
    InsightsClient.config, InsightsClient.options = parse_options()
    return client.delete_archive(path)
