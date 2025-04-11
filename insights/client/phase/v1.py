from __future__ import print_function
import functools
from os.path import isfile
import json
import logging
import os
import sys
import runpy

from insights.client import InsightsClient
from insights.client.config import InsightsConfig
from insights.client.constants import InsightsConstants as constants
from insights.client.support import InsightsSupport
from insights.client.utilities import validate_remove_file, print_egg_versions, _get_rhsm_identity
from insights.client.schedule import get_scheduler

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
        resp = client.get_diagnosis()
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
    try:
        client.update()
    except Exception as e:
        logger.error("Failed to update rules. Error: %s", str(e))
        sys.exit(constants.sig_kill_bad)

    if config.payload:
        logger.debug('Uploading a payload. Bypassing rules update.')
        return


@phase
def post_update(client, config):

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
        if config.offline or config.no_upload or config.module:
            # create a machine id first thing. we'll need it for all uploads
            logger.debug('Machine ID: %s', client.get_machine_id())
            logger.debug("CONFIG: %s", config)
            if config.offline:
                logger.debug('Running client in offline mode. Bypassing registration.')
            elif config.no_upload:
                logger.debug("Running client without uploading. Bypassing registration.")
            else:
                logger.debug('Running a specified module. Bypassing registration.')
            return

        if not _get_rhsm_identity():
            logger.error(
                "This host is unregistered, please ensure that "
                "the system is registered with subscription-manager "
                "and then with insights-client.\n"
                "\n1. Register with subscription-manager"
                "\n# subscription-manager register\n"
                "\n2. Register with insights-client"
                "\n# insights-client --register"
            )
            sys.exit(constants.sig_kill_bad)

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
                get_scheduler(config).remove_scheduling()
                sys.exit(constants.sig_kill_ok)
            else:
                sys.exit(constants.sig_kill_bad)

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

    if config.offline or config.no_upload or config.payload or config.module:
        # create a machine id first thing. we'll need it for all uploads
        logger.debug('Machine ID: %s', client.get_machine_id())
        logger.debug("CONFIG: %s", config)
        if config.offline:
            logger.debug('Running client in offline mode. Bypassing registration.')
        elif config.no_upload:
            logger.debug("Running client without uploading. Bypassing registration.")
        elif config.payload:
            logger.debug('Uploading a specified archive. Bypassing registration.')
        else:
            logger.debug('Running a specified module. Bypassing registration.')
        return

    # check registration status before anything else
    reg_check = isfile(constants.registered_files[0])

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
        if client.unregister():
            get_scheduler(config).remove_scheduling()
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    # halt here if unregistered
    if not reg_check and not config.register:
        logger.error("This host is unregistered. "
                     "Use --register to register this host.\n"
                     "# insights-client --register")
        sys.exit(constants.sig_kill_bad)

    # --register was called
    if config.register:
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

    # set --ansible-hostname independent of register
    # only do this if set from the CLI. normally display_name is sent on upload
    if 'ansible_host' in config._cli_opts and not config.register:
        if client.set_ansible_host(config.ansible_host):
            sys.exit(constants.sig_kill_ok)
        else:
            sys.exit(constants.sig_kill_bad)

    # create a machine id first thing. we'll need it for all uploads
    logger.debug('Machine ID: %s', client.get_machine_id())
    logger.debug("CONFIG: %s", config)


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

    # default (below)
    if config.payload:
        insights_archive = config.payload
    else:
        try:
            insights_archive = client.collect()
        except RuntimeError as e:
            logger.error(e)
            sys.exit(constants.sig_kill_bad)
        if not config.content_type:
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
        content_type = None
        if config.content_type in ['gz', 'bz2', 'xz']:
            content_type = 'application/vnd.redhat.advisor.collection+' + config.content_type
            extension = os.path.splitext(insights_archive)[1][1:]
            compression_type = content_type.split('+')[1]
            if extension not in compression_type:
                logger.error("Content type different from compression")
                sys.exit(constants.sig_kill_bad)
        try:
            resp = client.upload(payload=insights_archive, content_type=(content_type if content_type else config.content_type))
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
