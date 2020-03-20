import logging
import base64
import json
from requests import ConnectionError, Timeout
from requests.exceptions import HTTPError, MissingSchema
from ssl import SSLError
from urllib3.exceptions import MaxRetryError
from insights.client.connection import InsightsConnection
from insights.client.schedule import get_scheduler
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import write_to_disk

logger = logging.getLogger(__name__)
NETWORK = constants.custom_network_log_level

IDENTITY_URI = 'http://169.254.169.254/latest/dynamic/instance-identity'
IDENTITY_DOC_URI = IDENTITY_URI + '/document'
IDENTITY_PKCS7_URI = IDENTITY_URI + '/pkcs7'


def aws_main(config):
    '''
    Process AWS entitlements with Hydra
    '''
    if config.authmethod != 'BASIC':
        logger.error('AWS entitlement is only available when BASIC auth is used.\n'
                     'Set auto_config=False and authmethod=BASIC in %s.', config.conf)
        return False
    # workaround for a workaround
    #   the hydra API doesn't accept the legacy cert
    #   and legacy_upload=False currently just
    #   redirects to the classic API with /platform added
    #   so if doing AWS entitlement, use cert_verify=True
    config.cert_verify = True
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
        enable_delayed_registration(config)
    return True


def get_uri(conn, uri):
    '''
    Fetch information from URIs
    '''
    try:
        logger.log(NETWORK, 'GET %s', uri)
        res = conn.session.get(uri, timeout=conn.config.http_timeout)
    except (ConnectionError, Timeout) as e:
        logger.error(e)
        logger.error('Could not reach %s', uri)
        return None
    logger.log(NETWORK, 'Status code: %s', res.status_code)
    return res


def get_aws_identity(conn):
    '''
    Get data from AWS
    '''
    logger.info('Fetching AWS identity information.')
    doc_res = get_uri(conn, IDENTITY_DOC_URI)
    pkcs7_res = get_uri(conn, IDENTITY_PKCS7_URI)
    if not (doc_res and pkcs7_res) or not (doc_res.ok and pkcs7_res.ok):
        logger.error('Error getting identity information.')
        return None
    logger.debug('Identity information obtained successfully.')
    identity_doc = base64.b64encode(doc_res.content)

    return {
        'document': identity_doc.decode('utf-8'),
        'pkcs7': pkcs7_res.text
    }


def post_to_hydra(conn, data):
    '''
    Post data to Hydra
    '''
    logger.info('Submitting identity information to Red Hat.')
    hydra_endpoint = conn.config.portal_access_hydra_url

    # POST to hydra
    try:
        json_data = json.dumps(data)
        logger.log(NETWORK, 'POST %s', hydra_endpoint)
        logger.log(NETWORK, 'POST body: %s', json_data)
        res = conn.session.post(hydra_endpoint, data=json_data, timeout=conn.config.http_timeout)
    except MissingSchema as e:
        logger.error(e)
        return False
    except (ConnectionError, Timeout, SSLError, MaxRetryError) as e:
        logger.error(e)
        logger.error('Could not reach %s', hydra_endpoint)
        return False
    logger.log(NETWORK, 'Status code: %s', res.status_code)
    try:
        res.raise_for_status()
    except HTTPError as e:
        # if failure,
        # error, return False
        logger.error(e)
        try:
            res_json = res.json()
            err_msg = res_json.get('message', '')
            err_details = res_json.get('detailMessage', '')
            logger.error('%s\n%s', err_msg, err_details)
        except ValueError:
            logger.error('Could not parse JSON response.')
        return False
    logger.info('Entitlement information has been sent.')
    return True


def enable_delayed_registration(config):
    '''
    Write a marker file to allow client to know that
    it should attempt to register when it runs
    '''
    logger.debug('Writing to %s', constants.register_marker_file)
    write_to_disk(constants.register_marker_file)
    job = get_scheduler(config)
    job.set_daily()
