from __future__ import print_function
import functools
import json
import logging
import os
import shutil
import sys
import six
import atexit

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from insights.client.support import InsightsSupport
from insights.client.utilities import validate_remove_file, print_egg_versions, write_to_disk
from insights.client.schedule import get_scheduler
from insights.client.apps.compliance import ComplianceClient

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
        if config.debug:
            logger.info("Core path: %s", os.path.dirname(__file__))
        try:
            func(client, config)
        except Exception:
            logger.exception("Fatal error")
            sys.exit(1)
        else:
            sys.exit(0)  # Exit gracefully
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

    # delete someday
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

    if config.diagnosis:
        remediation_id = None
        if config.diagnosis is not True:
            remediation_id = config.diagnosis
        resp = client.get_diagnosis(remediation_id)
        if not resp:
            sys.exit(constants.sig_kill_bad)
        print(json.dumps(resp))
        sys.exit(constants.sig_kill_ok)


@phase
def update(client, config):
    client.update()
    if config.payload:
        logger.debug('Uploading a payload. Bypassing rules update.')
        return
    client.update_rules()


@phase
def post_update(client, config):
    # create a machine id first thing. we'll need it for all uploads
    logger.debug('Machine ID: %s', client.get_machine_id())
    logger.debug("CONFIG: %s", config)
    print_egg_versions()
    # -------delete everything below this line-------
    if config.legacy_upload:
        if config.status:
            reg_check = client.get_registration_status()
            for msg in reg_check['messages']:
                logger.info(msg)
            if reg_check['status']:
                sys.exit(constants.sig_kill_ok)
            else:
                sys.exit(constants.sig_kill_bad)

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
        return
    # -------delete everything above this line-------

    if config.offline:
        logger.debug('Running client in offline mode. Bypassing registration.')
        return

    # --payload short circuits registration check
    if config.payload:
        logger.debug('Uploading a specified archive. Bypassing registration.')
        return

    # check registration status before anything else
    reg_check = client.get_registration_status()
    if reg_check is None:
        sys.exit(constants.sig_kill_bad)

    # --status
    if config.status:
        if reg_check:
            logger.info('This host is registered.')
            sys.exit(constants.sig_kill_ok)
        else:
            logger.info('This host is unregistered.')
            sys.exit(constants.sig_kill_bad)

    # put this first to avoid conflicts with register
    if config.unregister:
        if reg_check:
            logger.info('Unregistering this host from Insights.')
            if client.unregister():
                get_scheduler(config).remove_scheduling()
                sys.exit(constants.sig_kill_ok)
            else:
                sys.exit(constants.sig_kill_bad)
        else:
            logger.info('This host is not registered, unregistration is not applicable.')
            sys.exit(constants.sig_kill_bad)

    # halt here if unregistered
    if not reg_check and not config.register:
        logger.info('This host has not been registered. '
                    'Use --register to register this host.')
        sys.exit(constants.sig_kill_bad)

    # --force-reregister, clear machine-id
    if config.reregister:
        reg_check = False
        client.clear_local_registration()

    # --register was called
    if config.register:
        # don't actually need to make a call to register() since
        #   system creation and upload are a single event on the platform
        if reg_check:
            logger.info('This host has already been registered.')
        if (not config.disable_schedule and
           get_scheduler(config).set_daily()):
            logger.info('Automatic scheduling for Insights has been enabled.')

    # set --display-name independent of register
    # only do this if set from the CLI. normally display_name is sent on upload
    if 'display_name' in config._cli_opts and not config.register:
        if client.set_display_name(config.display_name):
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)


@phase
def collect_and_output(client, config):
    # last phase, delete PID file on exit
    atexit.register(write_to_disk, constants.pidfile, delete=True)
    # --compliance was called
    if config.compliance:
        config.payload, config.content_type = ComplianceClient(config).oscap_scan()
    if config.payload:
        insights_archive = config.payload
    else:
        try:
            insights_archive = client.collect()
        except RuntimeError as e:
            logger.error(e)
            sys.exit(constants.sig_kill_bad)
        config.content_type = 'application/vnd.redhat.advisor.collection+tgz'

    if not insights_archive:
        sys.exit(constants.sig_kill_bad)
    if config.to_stdout:
        with open(insights_archive, 'rb') as tar_content:
            if six.PY3:
                sys.stdout.buffer.write(tar_content.read())
            else:
                shutil.copyfileobj(tar_content, sys.stdout)
    else:
        resp = None
        if not config.no_upload:
            try:
                resp = client.upload(payload=insights_archive, content_type=config.content_type)
            except IOError as e:
                logger.error(str(e))
                sys.exit(constants.sig_kill_bad)
            except ValueError as e:
                logger.error(str(e))
                sys.exit(constants.sig_kill_bad)
        else:
            logger.info('Archive saved at %s', insights_archive)
        if resp:
            if config.to_json:
                print(json.dumps(resp))

            if not config.payload:
                # delete the archive
                if config.keep_archive:
                    logger.info('Insights archive retained in ' + insights_archive)
                else:
                    client.delete_archive(insights_archive, delete_parent_dir=True)
    client.delete_cached_branch_info()

    # rotate eggs once client completes all work successfully
    try:
        client.rotate_eggs()
    except IOError:
        message = ("Failed to rotate %s to %s" %
                   (constants.insights_core_newest,
                    constants.insights_core_last_stable))
        logger.debug(message)
        raise IOError(message)
