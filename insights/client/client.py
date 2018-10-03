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
                        determine_hostname)
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
    if not os.path.exists(log_dir):
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


def set_up_logging(config):
    if len(logging.root.handlers) == 0:
        logging.root.addHandler(get_console_handler(config))
        logging.root.addHandler(get_file_handler(config))
        configure_level(config)
        logger.debug("Logging initialized")


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


def handle_registration(config, pconn):
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


def get_registration_status(config, pconn):
    '''
        Handle the registration process
        Returns:
            True - machine is registered
            False - machine is unregistered
            None - could not reach the API
    '''
    return registration_check(pconn)


def handle_unregistration(config, pconn):
    """
        returns (bool): True success, False failure
    """
    unreg = pconn.unregister()
    if unreg:
        # only set if unreg was successful
        write_unregistered_file()
        get_scheduler(config).remove_scheduling()
    return unreg


def get_machine_id():
    return generate_machine_id()


def update_rules(config, pconn):
    if not pconn:
        raise ValueError('ERROR: Cannot update rules in --offline mode. '
                         'Disable auto_update in config file.')

    pc = InsightsUploadConf(config, conn=pconn)
    return pc.get_conf_update()


def get_branch_info(config, pconn):
    """
    Get branch info for a system
    returns (dict): {'remote_branch': -1, 'remote_leaf': -1}
    """
    branch_info = constants.default_branch_info

    # in the case we are running on offline mode
    # or we are analyzing a running container/image
    # or tar file, mountpoint, simply return the default branch info
    if (config.offline or
            config.analyze_container):
        return branch_info

    # otherwise continue reaching out to obtain branch info
    try:
        branch_info = pconn.branch_info()
    except LookupError:
        logger.debug("There was an error obtaining branch information.")
        logger.debug("Assuming default branch information %s" % branch_info)
    logger.debug("Obtained branch information: %s" % branch_info)
    return branch_info


def collect(config, pconn):
    """
    All the heavy lifting done here
    """
    # initialize collection target
    # tar files
    if config.analyze_file:
        logger.debug("Client analyzing a compress filesystem.")
        target = {'type': 'compressed_file',
                  'name': os.path.splitext(
                        os.path.basename(config.analyze_file))[0],
                  'location': config.analyze_file}

    # mountpoints
    elif config.analyze_mountpoint:
        logger.debug("Client analyzing a filesystem already mounted.")
        target = {'type': 'mountpoint',
                  'name': os.path.splitext(
                        os.path.basename(config.analyze_mountpoint))[0],
                  'location': config.analyze_mountpoint}

    # image
    elif config.analyze_image_id:
        logger.debug("Client running in image mode.")
        logger.debug("Scanning for matching image.")

        from .containers import get_targets
        targets = get_targets(config)
        if len(targets) == 0:
            sys.exit(constants.sig_kill_bad)
        target = targets[0]

    # host, or inside container
    else:
        if config.analyze_container:
            logger.debug('Client running in container mode.')
        else:
            logger.debug("Host selected as scanning target.")
        target = constants.default_target

    branch_info = get_branch_info(config, pconn)
    pc = InsightsUploadConf(config)
    tar_file = None

    # load config from stdin/file if specified
    try:
        stdin_config = {}
        if config.from_file:
            with open(config.from_file, 'r') as f:
                stdin_config = json.load(f)
        elif config.from_stdin:
            stdin_config = json.load(sys.stdin)
        if ((config.from_file or config.from_stdin) and
            ('uploader.json' not in stdin_config or
             'sig' not in stdin_config)):
            raise ValueError
        if ((config.from_file or config.from_stdin) and
                'branch_info' in stdin_config and stdin_config['branch_info'] is not None):
            branch_info = stdin_config['branch_info']
    except:
        logger.error('ERROR: Invalid config for %s! Exiting...',
                     ('--from-file' if config.from_file else '--from-stdin'))
        return False

    if stdin_config:
        collection_rules = pc.get_conf_stdin(stdin_config)
    else:
        collection_rules = pc.get_conf_file()
    rm_conf = pc.get_rm_conf()
    if rm_conf:
        logger.warn("WARNING: Excluding data from files")

    # defaults
    archive = None
    container_connection = None
    mp = None
    compressed_filesystem = None

    try:
        # analyze docker images
        if target['type'] == 'docker_image':
            from .containers import open_image
            container_connection = open_image(target['name'])
            logging_name = 'Docker image ' + target['name']

            if container_connection:
                mp = container_connection.get_fs()
            else:
                logger.error('Could not open %s for analysis', logging_name)
                return False

        # analyze compressed files
        elif target['type'] == 'compressed_file':
            logging_name = 'Compressed file ' + target['name'] + ' at location ' + target['location']

            from .compressed_file import InsightsCompressedFile
            compressed_filesystem = InsightsCompressedFile(target['location'])

            if compressed_filesystem.is_tarfile is False:
                logger.debug("Could not access compressed tar filesystem.")
                return False

            mp = compressed_filesystem.get_filesystem_path()

        # analyze mountpoints
        elif target['type'] == 'mountpoint':

            logging_name = 'Filesystem ' + target['name'] + ' at location ' + target['location']
            mp = config.analyze_mountpoint

        # analyze the host
        elif target['type'] == 'host':
            logging_name = determine_hostname()

        # nothing found to analyze
        else:
            logger.error('Unexpected analysis target: %s', target['type'])
            return False

        archive = InsightsArchive(compressor=config.compressor,
                                  target_name=target['name'])
        atexit.register(_delete_archive_internal, config, archive)

        # determine the target type and begin collection
        # we infer "docker_image" SPEC analysis for certain types
        if target['type'] in ["mountpoint", "compressed_file"]:
            target_type = "docker_image"
        else:
            target_type = target['type']
        logger.debug("Inferring target_type '%s' for SPEC collection", target_type)
        logger.debug("Inferred from '%s'", target['type'])
        dc = DataCollector(config, archive, mountpoint=mp)

        logger.info('Starting to collect Insights data for %s', logging_name)
        dc.run_collection(collection_rules, rm_conf, branch_info)

        tar_file = dc.done(collection_rules, rm_conf)

    finally:
        # called on loop iter end or unexpected exit
        if container_connection:
            container_connection.close()

    # cleanup the temporary stuff for analyzing tar files
    if config.analyze_file is not None and compressed_filesystem is not None:
        compressed_filesystem.cleanup_temp_filesystem()

    return tar_file


def get_connection(config):
    return InsightsConnection(config)


def upload(config, pconn, tar_file, content_type, collection_duration=None):
    logger.info('Uploading Insights data.')
    api_response = None
    for tries in range(config.retries):
        upload = pconn.upload_archive(tar_file, content_type, collection_duration)

        if upload.status_code in (200, 201):
            api_response = json.loads(upload.text)
            machine_id = generate_machine_id()

            # Write to last upload file
            with open(constants.last_upload_results_file, 'w') as handler:
                if six.PY3:
                    handler.write(upload.text)
                else:
                    handler.write(upload.text.encode('utf-8'))
            write_to_disk(constants.lastupload_file)

            account_number = config.account_number
            if account_number:
                logger.info("Successfully uploaded report from %s to account %s." % (
                            machine_id, account_number))
            else:
                logger.info("Successfully uploaded report for %s." % (machine_id))
            break
        elif upload.status_code == 202:
            machine_id = generate_machine_id()
            logger.info("Successfully uploaded report for %s." % (machine_id))
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
