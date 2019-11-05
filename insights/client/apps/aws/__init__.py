import logging
import requests
import ssl
import urllib3
from insights.client.connection import InsightsConnection
from insights.client.schedule import get_scheduler
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import write_to_disk

logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')

IDENTITY_URI = 'http://169.254.169.254/latest/dynamic/instance-identity'
IDENTITY_DOC_URI = IDENTITY_URI + '/document'
IDENTITY_SIG_URI = IDENTITY_URI + '/signature'
IDENTITY_PKCS7_URI = IDENTITY_URI + '/pkcs7'


def aws_main(config):
    '''
    Process AWS entitlements with Hydra
    '''
    conn = InsightsConnection(config)
    bundle = get_aws_identity(conn)
    if not bundle:
        return False
    succ = post_to_hydra(conn, bundle)
    if not succ:
        return False
    # register with insights if this option
    #   wasn't specified
    if not config.portal_access_no_insights:
        enable_delayed_registration()
        job = get_scheduler(config)
        job.set_daily()
    return True


def get_uri(conn, uri):
    '''
    Fetch information from URIs
    '''
    try:
        net_logger.info('GET %s', uri)
        res = conn.session.get(uri, timeout=conn.config.http_timeout)
    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error(e)
        logger.error('Could not reach %s', uri)
        return None
    net_logger.info('Status code: %s', res.status_code)
    return res


def get_aws_identity(conn):
    '''
    Get data from AWS
    '''
    logger.info('Fetching AWS identity information.')
    doc_res = get_uri(conn, IDENTITY_DOC_URI)
    sig_res = get_uri(conn, IDENTITY_SIG_URI)
    pkcs7_res = get_uri(conn, IDENTITY_SIG_URI)
    if not (doc_res and sig_res and pkcs7_res):
        logger.error('Error getting identity information.')
        return None
    identity_doc = {}
    try:
        identity_doc = doc_res.json()
    except ValueError as e:
        logger.error(e)
        logger.error('Could not parse identity document JSON.')
        return {}
    logger.debug('Identity information obtained successfully.')

    def identity_doc_filter(doc):
        '''
        Only take the fields we need
        '''
        try:
            return {
                'version': doc['version'],
                'accountId': doc['accountId'],
                'availabilityZone': doc['availabilityZone'],
                'region': doc['region']
            }
        except KeyError as e:
            logger.error(e)
            logger.error('Could not parse identity document JSON.')
            return {}

    return {
        'document': identity_doc_filter(identity_doc),
        'signature': sig_res.content.decode('utf-8'),
        'pkcs7': pkcs7_res.content.decode('utf-8')
    }


def post_to_hydra(conn, data):
    '''
    Post data to Hydra
    '''
    logger.info('Submitting identity information to Red Hat.')
    hydra_endpoint = conn.config.portal_access_hydra_url
    print(data)
    # POST to hydra
    try:
        net_logger.info('POST %s', hydra_endpoint)
        res = conn.session.post(hydra_endpoint, timeout=conn.config.http_timeout, data=data)
    except (requests.ConnectionError, requests.Timeout, ssl.SSLError, urllib3.exceptions.MaxRetryError) as e:
        logger.error(e)
        logger.error('Could not reach %s', hydra_endpoint)
        return False
    net_logger.info('Status code: %s', res.status_code)
    if res.status_code not in (200, 201):
        # if failure,
        # error, return False
        logger.error('Entitlement information could not be sent. HTTP status: %s', res.status_code)
        return False
    # if success,
    # something like "Entitlement information has been sent." Maybe link to a KB article
    logger.info('Entitlement information has been sent.')
    return True


def enable_delayed_registration():
    '''
    Write a marker file to allow client to know that
    it should attempt to register when it runs
    '''
    logger.debug('Writing to %s', constants.register_marker_file)
    write_to_disk(constants.register_marker_file)
