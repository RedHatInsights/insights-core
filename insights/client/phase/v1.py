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
from insights.client.support import InsightsSupport
from insights.client.utilities import validate_remove_file
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
        if validate_remove_file(config.remove_file):
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
        rc = client.test_connection()
        if rc == 0:
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    if config.support:
        support = InsightsSupport(config)
        support.collect_support_info()
        sys.exit(constants.sig_kill_ok)


@phase
def update(client, config):
    client.update()
    client.update_rules()


@phase
def post_update(client, config):
    logger.debug("CONFIG: %s", config)
    if config.status:
        reg_check = client.get_registration_status()
        for msg in reg_check['messages']:
            logger.info(msg)
        sys.exit(constants.sig_kill_ok)

    # put this first to avoid conflicts with register
    if config.unregister:
        if client.unregister():
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    if config.offline:
        logger.debug('Running client in offline mode. Bypassing registration.')
        return

    if config.analyze_container:
        logger.debug(
            'Running client in container mode. Bypassing registration.')
        return

    if config.display_name and not config.register:
        # setting display name independent of registration
        if client.set_display_name(config.display_name):
            if 'display_name' in config._cli_opts:
                # only exit on success if it was invoked from command line
                sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    reg = client.register()
    if reg is None:
        # API unreachable
        logger.info('Running connection test...')
        client.test_connection()
        sys.exit(constants.sig_kill_bad)
    elif reg is False:
        # unregistered
        sys.exit(constants.sig_kill_bad)
    if config.register:
        if (not config.disable_schedule and
           get_scheduler(config).set_daily()):
            logger.info('Automatic scheduling for Insights has been enabled.')


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
        if resp:
            if config["to_json"]:
                print(json.dumps(resp))

            # delete the archive
            if config.keep_archive:
                logger.info('Insights archive retained in ' + tar_file)
            else:
                client.delete_archive(tar_file, delete_parent_dir=True)

            # if we are rotating the eggs and success on upload do rotation
            try:
                client.rotate_eggs()
            except IOError:
                message = ("Failed to rotate %s to %s" %
                           (constants.insights_core_newest,
                            constants.insights_core_last_stable))
                logger.debug(message)
                raise IOError(message)
    sys.exit()
