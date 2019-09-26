import logging
from insights.client.schedule import get_scheduler
from insights.client.constants import InsightsConstants as constants

logger = logging.getLogger(__name__)


def aws_main():
    '''
    Process AWS entitlements with Hydra
    '''
    bundle = get_aws_bundle()
    post_to_hydra(bundle)
    enable_delayed_registration()
    job = get_scheduler()
    job.set_daily()


def get_aws_bundle():
    '''
    Get data from AWS
    '''
    pass


def post_to_hydra(data):
    '''
    Post data to Hydra
    '''
    pass


def enable_delayed_registration():
    '''
    Write a marker file to allow client to know that
    it should attempt to register when it runs
    '''
    pass


def main(config, client):
    print('TEST')
    return 100
