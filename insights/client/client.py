from __future__ import print_function
from __future__ import absolute_import
import sys
import json
import logging
import logging.handlers
import os
import time
import shutil
import six
import atexit

from .utilities import (generate_machine_id,
                        write_to_disk,
                        write_registered_file,
                        write_unregistered_file,
                        delete_registered_file,
                        delete_unregistered_file,
                        determine_hostname,
                        read_pidfile,
                        systemd_notify)
from .collection_rules import InsightsUploadConf
from .data_collector import DataCollector
from .connection import InsightsConnection
from .archive import InsightsArchive
from .support import registration_check
from .constants import InsightsConstants as constants
from .schedule import get_scheduler

LOG_FORMAT = ("%(asctime)s %(levelname)8s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def do_log_rotation():
    handler = get_file_handler()
    return handler.doRollover()


def get_file_handler(config):
    log_file = config.logging_file
    log_dir = os.path.dirname(log_file)
    if not log_dir:
        log_dir = os.getcwd()
    elif not os.path.exists(log_dir):
        os.makedirs(log_dir, 0o700)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, backupCount=3)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_console_handler(config):
    if config.silent:
        target_level = logging.FATAL
    elif config.verbose:
        target_level = logging.DEBUG
    elif config.quiet:
        target_level = logging.ERROR
    else:
        target_level = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(target_level)

    log_format = LOG_FORMAT if config.verbose else "%(message)s"
    handler.setFormatter(logging.Formatter(log_format))

    return handler


def configure_level(config):
    config_level = 'DEBUG' if config.verbose else config.loglevel

    init_log_level = logging.getLevelName(config_level)
    if type(init_log_level) in six.string_types:
        print("Invalid log level %s, defaulting to DEBUG" % config_level)
        init_log_level = logging.DEBUG

    logger.setLevel(init_log_level)
    logging.root.setLevel(init_log_level)

    net_debug_level = logging.INFO if config.net_debug else logging.ERROR
    logging.getLogger('network').setLevel(net_debug_level)
    if not config.verbose:
        logging.getLogger('insights.core.dr').setLevel(logging.WARNING)


def set_up_logging(config):
    if len(logging.root.handlers) == 0:
        logging.root.addHandler(get_console_handler(config))
        logging.root.addHandler(get_file_handler(config))
        configure_level(config)
        logger.debug("Logging initialized")


# -LEGACY-
def register(config, pconn):
    """
    Do registration using basic auth
    """
    username = config.username
    password = config.password
    authmethod = config.authmethod
    auto_config = config.auto_config
    if not username and not password and not auto_config and authmethod == 'BASIC':
        logger.debug('Username and password must be defined in configuration file with BASIC authentication method.')
        return False
    return pconn.register()


# -LEGACY-
def _legacy_handle_registration(config, pconn):
    '''
    Handle the registration process
    Returns:
        True - machine is registered
        False - machine is unregistered
        None - could not reach the API
    '''
    logger.debug('Trying registration.')
    # force-reregister -- remove machine-id files and registration files
    # before trying to register again
    if config.reregister:
        delete_registered_file()
        delete_unregistered_file()
        write_to_disk(constants.machine_id_file, delete=True)
        logger.debug('Re-register set, forcing registration.')

    logger.debug('Machine-id: %s', generate_machine_id(new=config.reregister))

    # check registration with API
    check = get_registration_status(config, pconn)

    for m in check['messages']:
        logger.debug(m)

    if check['unreachable']:
        # Run connection test and exit
        return None

    if check['status']:
        # registered in API, resync files
        if config.register:
            logger.info('This host has already been registered.')
        write_registered_file()
        return True

    if config.register:
        # register if specified
        message, hostname, group, display_name = register(config, pconn)
        if not hostname:
            # API could not be reached, run connection test and exit
            logger.error(message)
            return None
        if config.display_name is None and config.group is None:
            logger.info('Successfully registered host %s', hostname)
        elif config.display_name is None:
            logger.info('Successfully registered host %s in group %s',
                        hostname, group)
        else:
            logger.info('Successfully registered host %s as %s in group %s',
                        hostname, display_name, group)
        if message:
            logger.info(message)
        write_registered_file()
        return True
    else:
        # unregistered in API, resync files
        write_unregistered_file(date=check['unreg_date'])
        # print messaging and exit
        if check['unreg_date']:
            # registered and then unregistered
            logger.info('This machine has been unregistered. '
                        'Use --register if you would like to '
                        're-register this machine.')
        else:
            # not yet registered
            logger.info('This machine has not yet been registered.'
                        'Use --register to register this machine.')
        return False


def handle_registration(config, pconn):
    '''
    Does nothing on the platform. Will be deleted eventually.
    '''
    if config.legacy_upload:
        return _legacy_handle_registration(config, pconn)


def get_registration_status(config, pconn):
    '''
        Handle the registration process
        Returns:
            True - machine is registered
            False - machine is unregistered
            None - could not reach the API
    '''
    return registration_check(pconn)


# -LEGACY-
def _legacy_handle_unregistration(config, pconn):
    """
        returns (bool): True success, False failure
    """
    check = get_registration_status(config, pconn)

    for m in check['messages']:
        logger.debug(m)

    if check['unreachable']:
        # Run connection test and exit
        return None

    if check['status']:
        unreg = pconn.unregister()
    else:
        unreg = True
        logger.info('This system is already unregistered.')
    if unreg:
        # only set if unreg was successful
        write_unregistered_file()
        get_scheduler(config).remove_scheduling()
    return unreg


def handle_unregistration(config, pconn):
    """
    Returns:
        True - machine was successfully unregistered
        False - machine could not be unregistered
        None - could not reach the API
    """
    if config.legacy_upload:
        return _legacy_handle_unregistration(config, pconn)

    unreg = pconn.unregister()
    if unreg:
        # only set if unreg was successful
        write_unregistered_file()
    return unreg


def get_machine_id():
    return generate_machine_id()


def update_rules(config, pconn):
    if not pconn:
        raise ValueError('ERROR: Cannot update rules in --offline mode. '
                         'Disable auto_update in config file.')

    pc = InsightsUploadConf(config, conn=pconn)
    return pc.get_conf_update()


def get_branch_info(config):
    """
    Get branch info for a system
    returns (dict): {'remote_branch': -1, 'remote_leaf': -1}
    """
    # in the case we are running on offline mode
    # or we are analyzing a running container/image
    # or tar file, mountpoint, simply return the default branch info
    if config.offline:
        return constants.default_branch_info
    return config.branch_info


def collect(config, pconn):
    """
    All the heavy lifting done here
    """
    branch_info = get_branch_info(config)
    pc = InsightsUploadConf(config)
    tar_file = None

    collection_rules = pc.get_conf_file()
    rm_conf = pc.get_rm_conf()
    if rm_conf:
        logger.warn("WARNING: Excluding data from files")

    # defaults
    mp = None
    archive = InsightsArchive(compressor=config.compressor)
    atexit.register(_delete_archive_internal, config, archive)

    msg_name = determine_hostname(config.display_name)
    dc = DataCollector(config, archive, mountpoint=mp)
    logger.info('Starting to collect Insights data for %s', msg_name)
    dc.run_collection(collection_rules, rm_conf, branch_info)
    tar_file = dc.done(collection_rules, rm_conf)
    return tar_file


def get_connection(config):
    return InsightsConnection(config)


def _legacy_upload(config, pconn, tar_file, content_type, collection_duration=None):
    logger.info('Uploading Insights data.')
    api_response = None
    parent_pid = read_pidfile()
    for tries in range(config.retries):
        systemd_notify(parent_pid)
        upload = pconn.upload_archive(tar_file, '', collection_duration)

        if upload.status_code in (200, 201):
            api_response = json.loads(upload.text)

            # Write to last upload file
            with open(constants.last_upload_results_file, 'w') as handler:
                if six.PY3:
                    handler.write(upload.text)
                else:
                    handler.write(upload.text.encode('utf-8'))
            write_to_disk(constants.lastupload_file)

            msg_name = determine_hostname(config.display_name)
            account_number = config.account_number
            if account_number:
                logger.info("Successfully uploaded report from %s to account %s.",
                            msg_name, account_number)
            else:
                logger.info("Successfully uploaded report for %s.", msg_name)
            break

        elif upload.status_code == 412:
            pconn.handle_fail_rcs(upload)
            break
        else:
            logger.error("Upload attempt %d of %d failed! Status Code: %s",
                         tries + 1, config.retries, upload.status_code)
            if tries + 1 != config.retries:
                logger.info("Waiting %d seconds then retrying",
                            constants.sleep_time)
                time.sleep(constants.sleep_time)
            else:
                logger.error("All attempts to upload have failed!")
                logger.error("Please see %s for additional information", config.logging_file)
    return api_response


def upload(config, pconn, tar_file, content_type, collection_duration=None):
    if config.legacy_upload:
        return _legacy_upload(config, pconn, tar_file, content_type, collection_duration)
    logger.info('Uploading Insights data.')
    parent_pid = read_pidfile()
    for tries in range(config.retries):
        systemd_notify(parent_pid)
        upload = pconn.upload_archive(tar_file, content_type, collection_duration)

        if upload.status_code in (200, 202):
            msg_name = determine_hostname(config.display_name)
            logger.info("Successfully uploaded report for %s.", msg_name)
        else:
            logger.error("Upload attempt %d of %d failed! Status code: %s",
                         tries + 1, config.retries, upload.status_code)
            if tries + 1 != config.retries:
                logger.info("Waiting %d seconds then retrying",
                            constants.sleep_time)
                time.sleep(constants.sleep_time)
            else:
                logger.error("All attempts to upload have failed!")
                logger.error("Please see %s for additional information", config.logging_file)


def _delete_archive_internal(config, archive):
    '''
    Only used during built-in collection.
    Delete archive and tmp dirs on unexpected exit.
    '''
    if not config.keep_archive:
        archive.delete_tmp_dir()
        archive.delete_archive_file()


def delete_archive(path, delete_parent_dir):
    removed_archive = False

    try:
        logger.debug("Removing archive %s", path)
        removed_archive = os.remove(path)

        dirname = os.path.dirname
        abspath = os.path.abspath
        parent_tmp_dir = dirname(abspath(path))
        if delete_parent_dir:
            logger.debug("Detected parent temporary directory %s", parent_tmp_dir)
            if parent_tmp_dir != "/var/tmp" and parent_tmp_dir != "/var/tmp/":
                logger.debug("Removing %s", parent_tmp_dir)
                shutil.rmtree(parent_tmp_dir)

    except:
        logger.error("Error removing %s", path)

    return removed_archive
