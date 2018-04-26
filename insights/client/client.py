import sys
import json
import logging
import logging.handlers
import os
import time
import shutil

from auto_config import (_try_satellite6_configuration,
                         _try_satellite5_configuration)
from utilities import (generate_machine_id,
                       generate_analysis_target_id,
                       write_to_disk,
                       write_unregistered_file,
                       determine_hostname)
from collection_rules import InsightsConfig
from data_collector import DataCollector
from connection import InsightsConnection
from archive import InsightsArchive
from support import registration_check
from constants import InsightsConstants as constants
from config import CONFIG as config

LOG_FORMAT = ("%(asctime)s %(levelname)8s %(name)s %(message)s")
INSIGHTS_CONNECTION = None
logger = logging.getLogger(__name__)


def do_log_rotation():
    handler = get_file_handler()
    return handler.doRollover()


def get_file_handler():
    log_file = config['logging_file']
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, 0700)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, backupCount=3)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    return file_handler


def get_console_handler():
    if config['silent']:
        target_level = logging.FATAL
    elif config['verbose']:
        target_level = logging.DEBUG
    elif config['quiet']:
        target_level = logging.ERROR
    else:
        target_level = logging.INFO

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(target_level)

    log_format = LOG_FORMAT if config['verbose'] else "%(message)s"
    handler.setFormatter(logging.Formatter(log_format))

    return handler


def configure_level():
    config_level = 'DEBUG' if config['verbose'] else config['loglevel']

    init_log_level = logging.getLevelName(config_level)
    if type(init_log_level) in (str, unicode):
        print "Invalid log level %s, defaulting to DEBUG" % config_level
        init_log_level = logging.DEBUG

    logger.setLevel(init_log_level)
    logging.root.setLevel(init_log_level)

    net_debug_level = logging.INFO if config['net_debug'] else logging.ERROR
    logging.getLogger('network').setLevel(net_debug_level)


def set_up_logging():
    if len(logging.root.handlers) == 0:
        # from_stdin mode implies to_stdout
        config['to_stdout'] = (config['to_stdout'] or
                               config['from_stdin'] or
                               config['from_file'])

        logging.root.addHandler(get_console_handler())
        logging.root.addHandler(get_file_handler())
        configure_level()
        logger.debug("Logging initialized")


def test_connection():
    """
    Test the connection
    """
    pconn = get_connection()
    return pconn.test_connection()


def _is_client_registered():

    # If the client is running in container mode, bypass this stuff
    msg_container_mode = 'Client running in container/image mode. Bypassing registration check'
    if config['analyze_container']:
        return msg_container_mode, False

    # All other cases
    msg_notyet = 'This machine has not yet been registered.'
    msg_unreg = 'This machine has been unregistered.'
    msg_doreg = 'Use --register to register this machine.'
    msg_rereg = 'Use --register if you would like to re-register this machine.'

    # check reg status w/ API
    reg_check = registration_check(get_connection())
    if not reg_check['status']:
        # not registered
        if reg_check['unreg_date']:
            # system has been unregistered from the UI
            msg = '\n'.join([msg_unreg, msg_rereg])
            write_unregistered_file(reg_check['unreg_date'])
            return msg, False
        else:
            # no record of system in remote
            msg = '\n'.join([msg_notyet, msg_doreg])
            # clear any local records
            write_to_disk(constants.registered_file, delete=True)
            write_to_disk(constants.unregistered_file, delete=True)
            return msg, False
    else:
        # API confirms reg
        if not os.path.isfile(constants.registered_file):
            write_to_disk(constants.registered_file)
        # delete any stray unregistered
        write_to_disk(constants.unregistered_file, delete=True)
        return '', True


def try_register():

    # if we are running an image analysis then dont register
    if config["analyze_container"]:
        logger.info("Running client in Container mode. Bypassing registration.")
        return

    # check reg status with API
    reg_check = registration_check(get_connection())
    if reg_check['status']:
        logger.info('This host has already been registered.')
        # regenerate the .registered file
        write_to_disk(constants.registered_file)
        return True
    if reg_check['unreachable']:
        logger.error(reg_check['messages'][1])
        return None
    message, hostname, group, display_name = register()
    if config['display_name'] is None and config['group'] is None:
        logger.info('Successfully registered host %s', hostname)
    elif config['display_name'] is None:
        logger.info('Successfully registered host %s in group %s', hostname, group)
    else:
        logger.info('Successfully registered host %s as %s in group %s',
                    hostname, display_name, group)
    if message:
        logger.info(message)
    return reg_check, message, hostname, group, display_name


def register():
    """
    Do registration using basic auth
    """
    username = config['username']
    password = config['password']
    authmethod = config['authmethod']
    auto_config = config['auto_config']
    if not username and not password and not auto_config and authmethod == 'BASIC':
        logger.debug('Username and password must be defined in configuration file with BASIC authentication method.')
        return False
    pconn = get_connection()
    return pconn.register()


def handle_registration():
    """
        returns (json): {'success': bool,
                        'machine-id': uuid from API,
                        'response': response from API,
                        'code': http code}
    """
    # force-reregister -- remove machine-id files and registration files
    # before trying to register again
    new = False
    if config['reregister']:
        logger.debug('Re-register set, forcing registration.')
        new = True
        config['register'] = True
        write_to_disk(constants.registered_file, delete=True)
        write_to_disk(constants.unregistered_file, delete=True)
        write_to_disk(constants.machine_id_file, delete=True)
    logger.debug('Machine-id: %s', generate_machine_id(new))

    logger.debug('Trying registration.')
    registration = try_register()
    if registration is None:
        return None
    msg, is_registered = _is_client_registered()

    return {'success': is_registered,
            'machine-id': generate_machine_id(),
            'registration': registration}


def get_registration_status():
    return registration_check(get_connection())


def handle_unregistration():
    """
        returns (bool): True success, False failure
    """
    pconn = get_connection()
    return pconn.unregister()


def get_machine_id():
    return generate_machine_id()


def update_rules():
    pconn = get_connection()
    pc = InsightsConfig(pconn)
    return pc.get_conf(True, {})


def get_branch_info():
    """
    Get branch info for a system
    returns (dict): {'remote_branch': -1, 'remote_leaf': -1}
    """
    branch_info = constants.default_branch_info

    # in the case we are running on offline mode
    # or we are analyzing a running container/image
    # or tar file, mountpoint, simply return the default branch info
    if (config['offline'] or
            config['analyze_container'] or
            config['container_mode']):
        return branch_info

    # otherwise continue reaching out to obtain branch info
    try:
        pconn = get_connection()
        branch_info = pconn.branch_info()
    except LookupError:
        logger.debug("There was an error obtaining branch information.")
        logger.debug("Assuming default branch information %s" % branch_info)
    logger.debug("Obtained branch information: %s" % branch_info)
    return branch_info


def collect(rc=0):
    """
    All the heavy lifting done here
    Run through "targets" - could be just ONE (host, default) or ONE (container/image)
    """
    # initialize collection targets
    # tar files
    if config['analyze_file'] is not None:
        logger.debug("Client analyzing a compress filesystem.")
        targets = [{'type': 'compressed_file',
                    'name': os.path.splitext(
                        os.path.basename(config['analyze_file']))[0],
                    'location': config['analyze_file']}]

    # mountpoints
    elif config['analyze_mountpoint'] is not None:
        logger.debug("Client analyzing a filesystem already mounted.")
        targets = [{'type': 'mountpoint',
                    'name': os.path.splitext(
                        os.path.basename(config['analyze_mountpoint']))[0],
                    'location': config['analyze_mountpoint']}]

    # container mode
    elif config['container_mode']:
        logger.debug("Client running in container/image mode.")
        logger.debug("Scanning for matching container/image.")

        from containers import get_targets
        targets = get_targets()

    # the host
    else:
        logger.debug("Host selected as scanning target.")
        targets = constants.default_target

    # if there are no targets to scan then bail
    if not len(targets):
        logger.debug("No targets were found. Exiting.")
        return False
    logger.debug("Found targets: ")
    logger.debug(targets)

    branch_info = get_branch_info()
    pc = InsightsConfig()
    tar_file = None

    # load config from stdin/file if specified
    try:
        stdin_config = {}
        if config['from_file']:
            with open(config['from_file'], 'r') as f:
                stdin_config = json.load(f)
        elif config['from_stdin']:
            stdin_config = json.load(sys.stdin)
        if ((config['from_file'] or config['from_stdin']) and
            ('uploader.json' not in stdin_config or
             'sig' not in stdin_config)):
            raise ValueError
        if ((config['from_file'] or config['from_stdin']) and
                'branch_info' in stdin_config and stdin_config['branch_info'] is not None):
            branch_info = stdin_config['branch_info']
    except:
        logger.error('ERROR: Invalid config for %s! Exiting...',
                     ('--from-file' if config['from_file'] else '--from-stdin'))
        return False

    collection_rules, rm_conf = pc.get_conf(False, stdin_config)
    individual_archives = []

    for t in targets:
        # defaults
        archive = None
        container_connection = None
        mp = None
        compressed_filesystem = None
        # archive metadata
        archive_meta = {}

        try:

            # analyze docker images
            if t['type'] == 'docker_image':

                from containers import open_image
                container_connection = open_image(t['name'])
                logging_name = 'Docker image ' + t['name']
                archive_meta['docker_id'] = t['name']

                from containers import docker_display_name
                archive_meta['display_name'] = docker_display_name(
                    t['name'], t['type'].replace('docker_', ''))

                logger.debug('Docker display_name: %s', archive_meta['display_name'])
                logger.debug('Docker docker_id: %s', archive_meta['docker_id'])

                if container_connection:
                    mp = container_connection.get_fs()
                else:
                    logger.error('Could not open %s for analysis', logging_name)
                    return False

            # analyze docker containers
            elif t['type'] == 'docker_container':
                from containers import open_container
                container_connection = open_container(t['name'])

                logging_name = 'Docker container ' + t['name']
                archive_meta['docker_id'] = t['name']

                from containers import docker_display_name
                archive_meta['display_name'] = docker_display_name(
                    t['name'], t['type'].replace('docker_', ''))
                logger.debug('Docker display_name: %s', archive_meta['display_name'])
                logger.debug('Docker docker_id: %s', archive_meta['docker_id'])

                if container_connection:
                    mp = container_connection.get_fs()
                else:
                    logger.error('Could not open %s for analysis', logging_name)
                    return False

            # analyze compressed files
            elif t['type'] == 'compressed_file':

                logging_name = 'Compressed file ' + t['name'] + ' at location ' + t['location']

                from compressed_file import InsightsCompressedFile
                compressed_filesystem = InsightsCompressedFile(t['location'])

                if compressed_filesystem.is_tarfile is False:
                    logger.debug("Could not access compressed tar filesystem.")
                    return False

                mp = compressed_filesystem.get_filesystem_path()

            # analyze mountpoints
            elif t['type'] == 'mountpoint':

                logging_name = 'Filesystem ' + t['name'] + ' at location ' + t['location']
                mp = config['analyze_mountpoint']

            # analyze the host
            elif t['type'] == 'host':
                logging_name = determine_hostname()
                archive_meta['display_name'] = determine_hostname(config['display_name'])

            # nothing found to analyze
            else:
                logger.error('Unexpected analysis target: %s', t['type'])
                return False

            archive_meta['type'] = t['type'].replace('docker_', '')
            archive_meta['product'] = 'Docker'

            machine_id = generate_analysis_target_id(t['type'], t['name'])
            archive_meta['system_id'] = machine_id
            archive_meta['machine_id'] = machine_id

            archive = InsightsArchive(compressor=config['compressor']
                                      if not config['container_mode'] else "none",
                                      target_name=t['name'])

            # determine the target type and begin collection
            # we infer "docker_image" SPEC analysis for certain types
            if t['type'] in ["mountpoint", "compressed_file"]:
                target_type = "docker_image"
            else:
                target_type = t['type']
            logger.debug("Inferring target_type '%s' for SPEC collection", target_type)
            logger.debug("Inferred from '%s'", t['type'])
            dc = DataCollector(archive,
                               mountpoint=mp,
                               target_name=t['name'],
                               target_type=target_type)

            logger.info('Starting to collect Insights data for %s', logging_name)
            dc.run_collection(collection_rules, rm_conf, branch_info)

            # add custom metadata about a host if provided by from_file
            # use in the OSE case
            if config['from_file']:
                with open(config['from_file'], 'r') as f:
                    stdin_config = json.load(f)
                    if 'metadata' in stdin_config:
                        archive.add_metadata_to_archive(json.dumps(stdin_config['metadata']), 'metadata.json')

            tar_file = dc.done(collection_rules, rm_conf)

            # add archives to list of individual uploads
            archive_meta['tar_file'] = tar_file
            individual_archives.append(archive_meta)

        finally:
            # called on loop iter end or unexpected exit
            if container_connection:
                container_connection.close()

    # cleanup the temporary stuff for analyzing tar files
    if config['analyze_file'] is not None and compressed_filesystem is not None:
        compressed_filesystem.cleanup_temp_filesystem()

    return tar_file


def get_connection():
    global INSIGHTS_CONNECTION
    if INSIGHTS_CONNECTION is None:
        INSIGHTS_CONNECTION = InsightsConnection()
    return INSIGHTS_CONNECTION


def upload(tar_file, collection_duration=None):
    logger.info('Uploading Insights data.')
    pconn = get_connection()
    api_response = None
    for tries in range(config['retries']):
        upload = pconn.upload_archive(tar_file, collection_duration,
                                      cluster=generate_machine_id(
                                          docker_group=config['container_mode']))

        if upload.status_code in (200, 201):
            api_response = json.loads(upload.text)
            machine_id = generate_machine_id()

            # Write to last upload file
            with open(constants.last_upload_results_file, 'w') as handler:
                handler.write(upload.text.encode('utf-8'))
            write_to_disk(constants.lastupload_file)

            # Write to ansible facts directory
            if os.path.isdir(constants.insights_ansible_facts_dir):
                insights_facts = {}
                insights_facts['last_upload'] = api_response

                sat6 = _try_satellite6_configuration()
                sat5 = None
                if not sat6:
                    sat5 = _try_satellite5_configuration()

                if sat6:
                    connection = 'sat6'
                elif sat5:
                    connection = 'sat5'
                else:
                    connection = 'rhsm'

                insights_facts['conf'] = {'machine-id': machine_id, 'connection': connection}
                with open(constants.insights_ansible_facts_file, 'w') as handler:
                    handler.write(json.dumps(insights_facts))

            account_number = config.get('account_number')
            if account_number:
                logger.info("Successfully uploaded report from %s to account %s." % (
                        machine_id, account_number))
            else:
                logger.info("Successfully uploaded report for %s." % (machine_id))
            break

        elif upload.status_code == 412:
            pconn.handle_fail_rcs(upload)
        else:
            logger.error("Upload attempt %d of %d failed! Status Code: %s",
                         tries + 1, config['retries'], upload.status_code)
            if tries + 1 != config['retries']:
                logger.info("Waiting %d seconds then retrying",
                            constants.sleep_time)
                time.sleep(constants.sleep_time)
            else:
                logger.error("All attempts to upload have failed!")
                logger.error("Please see %s for additional information", config['logging_file'])
    return api_response


def delete_archive(path):
    removed_archive = False

    try:
        logger.debug("Removing archive %s", path)
        removed_archive = os.remove(path)

        dirname = os.path.dirname
        abspath = os.path.abspath
        parent_tmp_dir = dirname(abspath(path))

        logger.debug("Detected parent temporary directory %s", parent_tmp_dir)
        if parent_tmp_dir != "/var/tmp" and parent_tmp_dir != "/var/tmp/":
            logger.debug("Removing %s", parent_tmp_dir)
            shutil.rmtree(parent_tmp_dir)

    except:
        logger.error("Error removing %s", path)

    return removed_archive
