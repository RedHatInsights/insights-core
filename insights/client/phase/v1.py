from __future__ import print_function
import functools
import json
import logging
import os
import shutil
import sys

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from insights.client.auto_config import try_auto_configuration
from insights.client.support import registration_check, InsightsSupport
from insights.client.utilities import (write_to_disk,
                                       generate_machine_id,
                                       validate_remove_file,
                                       delete_registered_file,
                                       delete_unregistered_file)
from insights.client.schedule import get_scheduler

logger = logging.getLogger(__name__)


def phase(func):
    @functools.wraps(func)
    def _f():
        try:
            config = InsightsConfig().load_all()
        except ValueError as e:
            sys.stderr.write('ERROR: ' + str(e) + '\n')
            sys.exit(constants.sig_kill_bad)
        client = InsightsClient(config)
        client.set_up_logging()
        if config.debug:
            logger.info("Core path: %s", os.path.dirname(__file__))
        try_auto_configuration(config)
        try:
            func(client, config)
        except Exception:
            logger.exception("Fatal error")
            sys.exit(1)
        else:
            sys.exit()  # Exit gracefully
    return _f


def get_phases():
    return [{
        'name': 'pre_update',
        'run_as_root': True
    }, {
        'name': 'update',
        'run_as_root': True
    }, {
        'name': 'post_update',
        'run_as_root': True
    }, {
        'name': 'collect_and_output',
        'run_as_root': True
    }]


@phase
def pre_update(client, config):
    if config.version:
        logger.info(constants.version)
        sys.exit(constants.sig_kill_ok)

    # validate the remove file
    if config.validate:
        if validate_remove_file():
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    # handle cron stuff
    if config.enable_schedule:
        # enable automatic scheduling
        logger.debug('Updating config...')
        updated = get_scheduler(config).set_daily()
        if updated:
            logger.info('Automatic scheduling for Insights has been enabled.')
        sys.exit(constants.sig_kill_ok)

    if config.disable_schedule:
        # disable automatic schedling
        updated = get_scheduler(config).remove_scheduling()
        if updated:
            logger.info('Automatic scheduling for Insights has been disabled.')
        if not config.register:
            sys.exit(constants.sig_kill_ok)

    if config.analyze_container:
        logger.debug('Not scanning host.')
        logger.debug('Scanning image ID, tar file, or mountpoint.')

    # test the insights connection
    if config.test_connection:
        logger.info("Running Connection Tests...")
        pconn = client.get_connection()
        rc = pconn.test_connection()
        if rc == 0:
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    if config.support:
        support = InsightsSupport()
        support.collect_support_info()
        sys.exit(constants.sig_kill_ok)


@phase
def update(client, config):
    client.update()
    client.update_rules()


@phase
def post_update(client, config):
    logger.debug("CONFIG: %s", config)
    if config['status']:
        reg_check = registration_check(client.get_connection())
        for msg in reg_check['messages']:
            logger.info(msg)
        sys.exit(constants.sig_kill_ok)

    # put this first to avoid conflicts with register
    if config['unregister']:
        pconn = client.get_connection()
        if pconn.unregister():
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    # force-reregister -- remove machine-id files and registration files
    # before trying to register again
    new = False
    if config['reregister']:
        new = True
        config['register'] = True
        delete_registered_file()
        delete_unregistered_file()
        write_to_disk(constants.machine_id_file, delete=True)
    logger.debug('Machine-id: %s', generate_machine_id(new))

    if config['register']:
        registration = client.try_register()
        if registration is None:
            logger.info('Running connection test...')
            client.test_connection()
            sys.exit(constants.sig_kill_bad)
        if (not config['disable_schedule'] and
           get_scheduler(config).set_daily()):
            logger.info('Automatic scheduling for Insights has been enabled.')

    # check registration before doing any uploads
    # only do this if we are not running in container mode
    # Ignore if in offline mode
    if not config["analyze_container"]:
        if not config['register'] and not config['offline']:
            msg, is_registered = client._is_client_registered()
            if not is_registered:
                logger.error(msg)
                sys.exit(constants.sig_kill_bad)


@phase
def collect_and_output(client, config):
    tar_file = client.collect()
    if not tar_file:
        sys.exit(constants.sig_kill_bad)
    if config['to_stdout']:
        with open(tar_file, 'rb') as tar_content:
            shutil.copyfileobj(tar_content, sys.stdout)
    else:
        resp = None
        if not config['no_upload']:
            resp = client.upload(tar_file)
        else:
            logger.info('Archive saved at %s', tar_file)
        if resp and config["to_json"]:
            print(json.dumps(resp))
    sys.exit()
