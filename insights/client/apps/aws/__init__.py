import logging
from insights.client.schedule import get_scheduler
from insights.client.constants import InsightsConstants as constants

logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')

IDENTITY_URI = 'http://169.254.169.254/latest/dynamic/instance-identity'
IDENTITY_DOC_URI = IDENTITY_URI + '/document'
IDENTITY_SIG_URI = IDENTITY_URI + '/signature'
IDENTITY_PKCS7_URI = IDENTITY_URI + '/pkcs7'


def aws_main(session):
    '''
    Process AWS entitlements with Hydra
    '''
    bundle = get_aws_identity(session)
    post_to_hydra(bundle)
    enable_delayed_registration()
    # job = get_scheduler()
    # job.set_daily()


def get_uri(session, uri):
    try:
        net_logger.info('GET %s', uri)
        res = session.get(uri)
    except (requests.ConnectionError, requests.Timeout) as e:
        logger.error(e)
        logger.error('Could not reach %s', uri)
        return None
    logger.debug('Status code: %s', res.status_code)
    return res


def get_aws_identity(session):
    '''
    Get data from AWS
    '''
    doc_res = get_uri(session, IDENTITY_DOC_URI)
    sig_res = get_uri(session, IDENTITY_SIG_URI)
    pkcs7_res = get_uri(session, IDENTITY_SIG_URI)
    if not (doc_res and sig_res and pkcs7_res):
        logger.error('Error getting identity documents.')
        return None
    try:
        identity_doc = doc_res.json()
        identity_sig = sig_res.json()
        identity_pkcs7 = pkcs7_res.json()
    except ValueError as e:
        logger.error(e)
        logger.error('Could not parse JSON.')
    return {
        'document': identity_doc,
        'signature': identity_sig
        'pkcs7': identity_pkcs7
    }


def verify_pkcs7_signature():
    '''
    Verify the PKSC7 signature
    '''
    # do we need to do this clientside?
    pass


def post_to_hydra(data):
    '''
    Post data to Hydra
    '''
    print(data)


def enable_delayed_registration():
    '''
    Write a marker file to allow client to know that
    it should attempt to register when it runs
    '''
    pass


def main(config, client):
    session = client.connection.session
    aws_main(session)
