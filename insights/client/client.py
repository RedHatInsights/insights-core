from __future__ import print_function
from __future__ import absolute_import
from os.path import isfile
import sys
import json
import logging
import logging.handlers
import os
import time
import six
from distutils.version import LooseVersion

from .utilities import (generate_machine_id,
                        write_to_disk,
                        write_registered_file,
                        write_unregistered_file,
                        delete_cache_files,
                        determine_hostname,
                        get_version_info)
from .collection_rules import InsightsUploadConf
from .data_collector import DataCollector
from .core_collector import CoreCollector
from .connection import InsightsConnection
from .archive import InsightsArchive
from .support import registration_check
from .constants import InsightsConstants as constants

NETWORK = constants.custom_network_log_level
LOG_FORMAT = ("%(asctime)s %(levelname)8s %(name)s %(message)s")
logger = logging.getLogger(__name__)


class RotatingFileHandlerWithUMask(logging.handlers.RotatingFileHandler, object):
    """ logging.handlers.RotatingFileHandler subclass with a modified
        file permission mask.
    """
    def __init__(self, umask, *args, **kwargs):
        self._umask = umask
        super(RotatingFileHandlerWithUMask, self).__init__(*args, **kwargs)

    def _open(self):
        """
        Overrides the logging library "_open" method with a custom
        file permission mask.
        """
        default_umask = os.umask(self._umask)
        try:
            return super(RotatingFileHandlerWithUMask, self)._open()
        finally:
            os.umask(default_umask)


class FileHandlerWithUMask(logging.FileHandler, object):
    """ logging.FileHandler subclass with a modified
        file permission mask.
    """
    def __init__(self, umask, *args, **kwargs):
        self._umask = umask
        super(FileHandlerWithUMask, self).__init__(*args, **kwargs)

    def _open(self):
        """
        Overrides the logging library "_open" method with a custom
        file permission mask.
        """
        default_umask = os.umask(self._umask)
        try:
            return super(FileHandlerWithUMask, self)._open()
        finally:
            os.umask(default_umask)


def do_log_rotation():
    handler = get_file_handler()
    return handler.doRollover()


def get_file_handler(config):
    '''
    Sets up the logging file handler.
    Returns:
        RotatingFileHandler - client rpm version is older than 3.2.0.
        FileHandler - client rpm version is 3.2.0 or newer.
    '''
    log_file = config.logging_file
    log_dir = os.path.dirname(log_file)
    if not log_dir:
        log_dir = os.getcwd()
    elif not os.path.exists(log_dir):
        os.makedirs(log_dir, 0o700)
    # ensure the legacy rotating file handler is only used in older client versions
    # or if there is a problem retrieving the rpm version.
    rpm_version = get_version_info()['client_version']
    if not rpm_version or (LooseVersion(rpm_version) < LooseVersion(constants.rpm_version_before_logrotate)):
        file_handler = RotatingFileHandlerWithUMask(0o077, log_file, backupCount=3)
    else:
        file_handler = FileHandlerWithUMask(0o077, log_file)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_console_handler(config):
    if config.silent:
        target_level = logging.FATAL
    elif config.verbose:
        target_level = logging.DEBUG
    elif config.net_debug:
        target_level = NETWORK
    elif config.quiet:
        target_level = logging.ERROR
    else:
        target_level = logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(target_level)

    log_format = LOG_FORMAT if config.verbose else "%(message)s"
    handler.setFormatter(logging.Formatter(log_format))

    return handler


def configure_level(config):
    config_level = 'NETWORK' if config.net_debug else config.loglevel
    config_level = 'DEBUG' if config.verbose else config.loglevel

    init_log_level = logging.getLevelName(config_level)
    if type(init_log_level) in six.string_types:
        print("Invalid log level %s, defaulting to DEBUG" % config_level)
        init_log_level = logging.DEBUG

    logger.setLevel(init_log_level)
    logging.root.setLevel(init_log_level)

    if not config.verbose:
        logging.getLogger('insights.core.dr').setLevel(logging.WARNING)


def set_up_logging(config):
    logging.addLevelName(NETWORK, "NETWORK")
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

    # check registration with API
    check = get_registration_status(config, pconn)
    machine_id_present = isfile(constants.machine_id_file)

    if machine_id_present and check['status'] is False:
        logger.info("Machine-id found, insights-client can not be registered."
                    " Please, unregister insights-client first: `insights-client --unregister`")
        return False

    logger.debug('Machine-id: %s', generate_machine_id())

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
            logger.info('This machine has not yet been registered. '
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


def __cleanup_local_files():
    write_unregistered_file()
    delete_cache_files()
    write_to_disk(constants.machine_id_file, delete=True)
    logger.debug('Unregistered and removed machine-id')


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
        if config.force:
            __cleanup_local_files()
            return True
        return None

    if check['status']:
        unreg = pconn.unregister()
    else:
        unreg = True
        logger.info('This system is already unregistered.')
    if unreg:
        # only set if unreg was successful
        __cleanup_local_files()
        logger.debug('Legacy unregistration')
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
    if unreg or config.force:
        # only set if unreg was successful or --force was set
        __cleanup_local_files()
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


def collect(config):
    """
    All the heavy lifting done here
    """
    branch_info = get_branch_info(config)
    pc = InsightsUploadConf(config)

    rm_conf = pc.get_rm_conf()
    blacklist_report = pc.create_report()
    if rm_conf:
        logger.warn("WARNING: Excluding data from files")

    archive = InsightsArchive(config)

    msg_name = determine_hostname(config.display_name)
    if config.core_collect:
        collection_rules = None
        dc = CoreCollector(config, archive)
    else:
        collection_rules = pc.get_conf_file()
        dc = DataCollector(config, archive)
    logger.info('Starting to collect Insights data for %s', msg_name)
    dc.run_collection(collection_rules, rm_conf, branch_info, blacklist_report)
    output = dc.done(collection_rules, rm_conf)
    return output


def get_connection(config):
    return InsightsConnection(config)


def _legacy_upload(config, pconn, tar_file, content_type, collection_duration=None):
    logger.info('Uploading Insights data.')
    api_response = None
    for tries in range(config.retries):
        logger.debug("Legacy upload attempt %d of %d ...", tries + 1, config.retries)
        try:
            upload = pconn.upload_archive(tar_file, '', collection_duration)
        except Exception as e:
            display_upload_error_and_retry(config, tries, str(e))
            continue

        if upload.status_code in (200, 201):
            api_response = json.loads(upload.text)

            # Write to last upload file
            with open(constants.last_upload_results_file, 'w') as handler:
                if six.PY3:
                    handler.write(upload.text)
                else:
                    handler.write(upload.text.encode('utf-8'))
            os.chmod(constants.last_upload_results_file, 0o644)
            write_to_disk(constants.lastupload_file)
            os.chmod(constants.lastupload_file, 0o644)

            msg_name = determine_hostname(config.display_name)
            account_number = config.account_number
            if account_number:
                logger.info("Successfully uploaded report from %s to account %s.",
                            msg_name, account_number)
            else:
                logger.info("Successfully uploaded report for %s.", msg_name)
            if config.register:
                # direct to console after register + upload
                logger.info('View the Red Hat Insights console at https://console.redhat.com/insights/')
            break

        elif upload.status_code in (412, 413):
            pconn.handle_fail_rcs(upload)
            raise RuntimeError('Upload failed.')
        else:
            display_upload_error_and_retry(config, tries, "%s: %s" % (upload.status_code, upload.reason))
    return api_response


def upload(config, pconn, tar_file, content_type, collection_duration=None):
    if config.legacy_upload:
        return _legacy_upload(config, pconn, tar_file, content_type, collection_duration)
    logger.info('Uploading Insights data.')
    for tries in range(config.retries):
        logger.debug("Upload attempt %d of %d ...", tries + 1, config.retries)
        try:
            upload = pconn.upload_archive(tar_file, content_type, collection_duration)
        except Exception as e:
            display_upload_error_and_retry(config, tries, str(e))
            continue

        if upload.status_code in (200, 202):
            write_to_disk(constants.lastupload_file)
            os.chmod(constants.lastupload_file, 0o644)
            msg_name = determine_hostname(config.display_name)
            logger.info("Successfully uploaded report for %s.", msg_name)
            if config.register:
                # direct to console after register + upload
                logger.info('View the Red Hat Insights console at https://console.redhat.com/insights/')
            return
        elif upload.status_code in (413, 415):
            pconn.handle_fail_rcs(upload)
            raise RuntimeError('Upload failed.')
        else:
            err_msg = "%s" % upload.status_code
            if hasattr(upload, 'reason'):
                err_msg += ": %s" % upload.reason
            display_upload_error_and_retry(config, tries, err_msg)


def display_upload_error_and_retry(config, tries, error_message):
    logger.error("Upload attempt %d of %d failed! Reason: %s",
                 tries + 1, config.retries, error_message)
    if tries + 1 < config.retries:
        logger.info("Waiting %d seconds then retrying",
                    constants.sleep_time)
        time.sleep(constants.sleep_time)
    else:
        logger.error("All attempts to upload have failed!")
        print("Please see %s for additional information" % config.logging_file)
        raise RuntimeError('Upload failed.')
