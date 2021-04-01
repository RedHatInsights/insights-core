from __future__ import print_function
import functools
import json
import logging
import os
import sys
import runpy

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from insights.client.support import InsightsSupport
from insights.client.utilities import validate_remove_file, print_egg_versions
from insights.client.schedule import get_scheduler
from insights.client.apps.compliance import ComplianceClient

logger = logging.getLogger(__name__)


def phase(func):
    @functools.wraps(func)
    def _f():
        try:
            config = InsightsConfig().load_all()
            client = InsightsClient(config)
        except (ValueError, OSError) as e:
            sys.stderr.write('ERROR: ' + str(e) + '\n')
            sys.exit(constants.sig_kill_bad)
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
        try:
            validate_remove_file(config)
            sys.exit(constants.sig_kill_ok)
        except RuntimeError as e:
            logger.error(e)
            sys.exit(constants.sig_kill_bad)

    # handle cron stuff
    if config.enable_schedule:
        # enable automatic scheduling
        logger.debug('Updating config...')
        scheduler = get_scheduler(config)
        updated = scheduler.schedule()
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

    if config.checkin:
        try:
            checkin_success = client.checkin()
        except Exception as e:
            print(e)
            sys.exit(constants.sig_kill_bad)

        if checkin_success:
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)


@phase
def update(client, config):
    client.update()
    if config.payload:
        logger.debug('Uploading a payload. Bypassing rules update.')
        return
    if not config.core_collect:
        client.update_rules()


@phase
def post_update(client, config):
    # create a machine id first thing. we'll need it for all uploads
    logger.debug('Machine ID: %s', client.get_machine_id())
    logger.debug("CONFIG: %s", config)
    print_egg_versions()

    if config.list_specs:
        client.list_specs()
        sys.exit(constants.sig_kill_ok)

    if config.show_results:
        try:
            client.show_results()
            sys.exit(constants.sig_kill_ok)
        except Exception as e:
            print(e)
            sys.exit(constants.sig_kill_bad)

    if config.check_results:
        try:
            client.check_results()
            sys.exit(constants.sig_kill_ok)
        except Exception as e:
            print(e)
            sys.exit(constants.sig_kill_bad)

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
            logger.info('Could not connect to the Insights API. Run insights-client --test-connection for more information.')
            sys.exit(constants.sig_kill_bad)
        elif reg is False:
            # unregistered
            sys.exit(constants.sig_kill_bad)
        if config.register and not config.disable_schedule:
            scheduler = get_scheduler(config)
            updated = scheduler.schedule()
            if updated:
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
        if not config.disable_schedule:
            scheduler = get_scheduler(config)
            updated = scheduler.schedule()
            if updated:
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
    # run a specified module
    if config.module:
        try:
            runpy.run_module(config.module)
        except ImportError as e:
            logger.error(e)
            sys.exit(constants.sig_kill_bad)
        sys.exit(constants.sig_kill_ok)

    # --compliance was called
    if config.compliance:
        config.payload, config.content_type = ComplianceClient(config).oscap_scan()

    # default (below)
    if config.payload:
        insights_archive = config.payload
    else:
        try:
            insights_archive = client.collect()
        except RuntimeError as e:
            logger.error(e)
            sys.exit(constants.sig_kill_bad)
        config.content_type = 'application/vnd.redhat.advisor.collection+tgz'

    if config.no_upload:
        # output options for which upload is not performed
        if config.output_dir:
            client.copy_to_output_dir(insights_archive)
        elif config.output_file:
            client.copy_to_output_file(insights_archive)
    else:
        # upload the archive
        if not insights_archive:
            # no archive to upload, something went wrong
            sys.exit(constants.sig_kill_bad)
        resp = None
        try:
            resp = client.upload(payload=insights_archive, content_type=config.content_type)
        except (IOError, ValueError, RuntimeError) as e:
            logger.error(str(e))
            sys.exit(constants.sig_kill_bad)
        if resp:
            if config.to_json:
                print(json.dumps(resp))
            client.show_inventory_deep_link()

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
