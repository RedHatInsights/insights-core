import sys
import getpass
import json
import logging
import logging.handlers
import os
import shutil
import time
# import atexit
from utilities import (generate_machine_id,
                       generate_analysis_target_id,
                       write_lastupload_file,
                       write_registered_file,
                       write_unregistered_file,
                       delete_registered_file,
                       delete_unregistered_file,
                       determine_hostname,
                       modify_config_file)
from collection_rules import InsightsConfig
from data_collector import DataCollector
from connection import InsightsConnection
from archive import InsightsArchive
from support import registration_check
from constants import InsightsConstants as constants
from client_config import InsightsClient

__author__ = 'Richard Brantley <rbrantle@redhat.com>, Jeremy Crafts <jcrafts@redhat.com>, Dan Varga <dvarga@redhat.com>'

LOG_FORMAT = ("%(asctime)s %(levelname)s %(message)s")
APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)
handler = None


def set_up_logging():
    # TODO: come back to this
    """
    Initialize Logging
    """
    global handler
    if not handler:
        log_dir = constants.log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, 0700)
        logging_file = os.path.join(log_dir, APP_NAME + '.log')
        if InsightsClient.config.get(APP_NAME, 'logging_file'):
            logging_file = InsightsClient.config.get(APP_NAME, 'logging_file')
        if InsightsClient.options.logging_file:
            logging_file = InsightsClient.options.logging_file
        valid_levels = ['ERROR', 'DEBUG', 'INFO', 'WARNING', 'CRITICAL']
        handler = logging.handlers.RotatingFileHandler(logging_file,
                                                       backupCount=3)

        # from_stdin mode implies to_stdout
        InsightsClient.options.to_stdout = (InsightsClient.options.to_stdout or
                                            InsightsClient.options.from_stdin or
                                            InsightsClient.options.from_file)
        if InsightsClient.options.to_stdout and not InsightsClient.options.verbose:
            InsightsClient.options.quiet = True

        # Send anything INFO+ to stdout and log
        stdout_handler = logging.StreamHandler(sys.stdout)
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setLevel(logging.ERROR)
        logging.root.addHandler(stderr_handler)
        if not InsightsClient.options.verbose:
            stdout_handler.setLevel(logging.INFO)
        if InsightsClient.options.quiet:
            stdout_handler.setLevel(logging.ERROR)
        if not InsightsClient.options.silent:
            logging.root.addHandler(stdout_handler)

        logging.root.addHandler(handler)

        formatter = logging.Formatter(LOG_FORMAT)
        handler.setFormatter(formatter)
        logging.root.setLevel(logging.WARNING)
        if InsightsClient.options.verbose:
            config_level = 'DEBUG'
        else:
            config_level = InsightsClient.config.get(APP_NAME, 'loglevel')

        if config_level in valid_levels:
            init_log_level = logging.getLevelName(config_level)
        else:
            print "Invalid log level %s, defaulting to DEBUG" % config_level
            init_log_level = logging.getLevelName("DEBUG")

        logger.setLevel(init_log_level)
        logging.root.setLevel(init_log_level)
        logger.debug("Logging initialized")
    return handler


def _is_client_registered():
    msg_notyet = 'This machine has not yet been registered.'
    msg_unreg = 'This machine has been unregistered.'
    msg_doreg = 'Use --register to register this machine.'
    msg_rereg = 'Use --force-register if you would like to re-register this machine.'
    msg_exit = 'Exiting...'
    # check reg status w/ API
    reg_check = registration_check()
    if not reg_check['status']:
        # not registered
        if reg_check['unreg_date']:
            # system has been unregistered from the UI
            msg = '\n'.join([msg_unreg, msg_rereg, msg_exit])
            write_unregistered_file(reg_check['unreg_date'])
            return msg, False
        else:
            # no record of system in remote
            msg = '\n'.join([msg_notyet, msg_doreg, msg_exit])
            # clear any local records
            delete_registered_file()
            delete_unregistered_file()
            return msg, False
    else:
        # API confirms reg
        if not os.path.isfile(constants.registered_file):
            write_registered_file()
        # delete any stray unregistered
        delete_unregistered_file()
        return '', True


def try_register():
    if os.path.isfile(constants.registered_file):
        logger.info('This host has already been registered.')
        return
    # check reg status with API
    reg_check = registration_check()
    if reg_check['status']:
        logger.info('This host has already been registered.')
        # regenerate the .registered file
        write_registered_file()
        return
    message, hostname, group, display_name = register()
    if InsightsClient.options.display_name is None and InsightsClient.options.group is None:
        logger.info('Successfully registered host %s', hostname)
    elif InsightsClient.options.display_name is None:
        logger.info('Successfully registered host %s in group %s', hostname, group)
    else:
        logger.info('Successfully registered host %s as %s in group %s',
                    hostname, display_name, group)
    if message:
        logger.info(message)


def register():
    """
    Do registration using basic auth
    """
    username = InsightsClient.config.get(APP_NAME, 'username')
    password = InsightsClient.config.get(APP_NAME, 'password')
    authmethod = InsightsClient.config.get(APP_NAME, 'authmethod')
    # TODO validate this is boolean somewhere in config load
    auto_config = InsightsClient.config.getboolean(APP_NAME, 'auto_config')
    if not username and not password and not auto_config and authmethod == 'BASIC':
        print 'Please enter your Red Hat Customer Portal Credentials'
        sys.stdout.write('Username: ')
        username = raw_input().strip()
        password = getpass.getpass()
        sys.stdout.write('Would you like to save these credentials? (y/n) ')
        save = raw_input().strip()
        InsightsClient.config.set(APP_NAME, 'username', username)
        InsightsClient.config.set(APP_NAME, 'password', password)
        logger.debug('savestr: %s', save)
        if save.lower() == 'y' or save.lower() == 'yes':
            logger.debug('Writing user/pass to config')
            modify_config_file({'username': username, 'password': password})
    pconn = InsightsConnection()
    return pconn.register()


def _delete_archive(archive):
    # delete archive on unexpected exit
    if not (InsightsClient.options.keep_archive or
            InsightsClient.options.offline or
            InsightsClient.options.no_upload or
            InsightsClient.options.no_tar_file or
            InsightsClient.config.getboolean(APP_NAME, "obfuscate")):
        archive.delete_tmp_dir()
        archive.delete_archive_file()


def fetch_rules():
    pconn = InsightsConnection()
    pc = InsightsConfig(pconn)
    return pc.get_conf(InsightsClient.options.update, {})


def collect(rc=0):
    """
    All the heavy lifting done here
    Run through "targets" - could be just ONE (host, default) or ONE (container/image)
    """
    # initialize collection targets
    # for now we do either containers OR host -- not both at same time
    targets = constants.default_target

    # if there are no targets to scan then bail
    if not len(targets):
        logger.debug("No targets were found. Exiting.")
        return False

    logger.warning("Assuming remote branch and leaf value of -1")
    branch_info = constants.default_branch_info

    pc = InsightsConfig()
    tar_file = None

    # load config from stdin/file if specified
    try:
        stdin_config = {}
        if InsightsClient.options.from_file:
            with open(InsightsClient.options.from_file, 'r') as f:
                stdin_config = json.load(f)
        elif InsightsClient.options.from_stdin:
            stdin_config = json.load(sys.stdin)
        if ((InsightsClient.options.from_file or InsightsClient.options.from_stdin) and
            ('uploader.json' not in stdin_config or
             'sig' not in stdin_config)):
            raise ValueError
        if ((InsightsClient.options.from_file or InsightsClient.options.from_stdin) and
                'branch_info' in stdin_config and stdin_config['branch_info'] is not None):
            branch_info = stdin_config['branch_info']
    except:
        logger.error('ERROR: Invalid config for %s! Exiting...',
                     ('--from-file' if InsightsClient.options.from_file else '--from-stdin'))
        return False

    collection_rules, rm_conf = pc.get_conf(InsightsClient.options.update, stdin_config)
    individual_archives = []

    for t in targets:
        # defaults
        archive = None
        container_connection = None
        mp = None
        # archive metadata
        archive_meta = {}

        try:
            logging_name = determine_hostname()
            archive_meta['display_name'] = determine_hostname(InsightsClient.options.display_name)
            archive_meta['type'] = t['type'].replace('docker_', '')
            archive_meta['product'] = 'Docker'
            archive_meta['system_id'] = generate_analysis_target_id(t['type'], t['name'])

            if InsightsClient.options.container_mode:
                compressor = "none"
            else:
                compressor = InsightsClient.options.compressor

            archive = InsightsArchive(compressor=compressor, target_name=t['name'])
            # atexit.register(_delete_archive, archive)
            dc = DataCollector(archive,
                               InsightsClient.config,
                               mountpoint=mp,
                               target_name=t['name'],
                               target_type=t['type'])

            logger.info('Starting to collect Insights data for %s', logging_name)
            dc.run_collection(collection_rules, rm_conf, branch_info)

            # add custom metadata about a host if provided by from_file
            # use in the OSE case
            if InsightsClient.options.from_file:
                with open(InsightsClient.options.from_file, 'r') as f:
                    stdin_config = json.load(f)
                    if 'metadata' in stdin_config:
                        archive.add_metadata_to_archive(json.dumps(stdin_config['metadata']), 'metadata.json')

            if InsightsClient.options.no_tar_file:
                logger.info('See Insights data in %s', dc.archive.archive_dir)
                return dc.archive.archive_dir

            tar_file = dc.done(collection_rules, rm_conf)

            # add archives to list of individual uploads
            archive_meta['tar_file'] = tar_file
            individual_archives.append(archive_meta)

        finally:
            # called on loop iter end or unexpected exit
            if container_connection:
                container_connection.close()

    return tar_file


def upload(tar_file, collection_duration=None):
    logger.info('Uploading Insights data. This may take a few minutes.')
    pconn = InsightsConnection()
    upload_status = False
    for tries in range(InsightsClient.options.retries):
        upload = pconn.upload_archive(tar_file, collection_duration,
                                      cluster=generate_machine_id(
                                          docker_group=InsightsClient.options.container_mode))
        upload_status = upload.status_code
        if upload.status_code == 201:
            with open(constants.last_upload_results_file, 'w') as handler:
                handler.write(upload.text)
            write_lastupload_file()
            machine_id = generate_machine_id()
            try:
                logger.info("You successfully uploaded a report from %s to account %s." % (machine_id, InsightsClient.account_number))
            except:
                pass
            logger.info("Upload completed successfully!")
            break
        elif upload.status_code == 412:
            pconn.handle_fail_rcs(upload)
        else:
            logger.error("Upload attempt %d of %d failed! Status Code: %s",
                         tries + 1, InsightsClient.options.retries, upload.status_code)
            if tries + 1 != InsightsClient.options.retries:
                logger.info("Waiting %d seconds then retrying",
                            constants.sleep_time)
                time.sleep(constants.sleep_time)
            else:
                logger.error("All attempts to upload have failed!")
                logger.error("Please see %s for additional information",
                             constants.default_log_file)
    return upload_status


def delete_archive(path):
    import os
    import shutil
    removed_archive = False

    try:
        logger.info("Removing archive %s", path)
        removed_archive = os.remove(path)

        dirname = os.path.dirname
        abspath = os.path.abspath
        parent_tmp_dir = dirname(abspath(path))

        logger.info("Detected parent temporary directory %s", parent_tmp_dir)
        if parent_tmp_dir != "/var/tmp" and parent_tmp_dir != "/var/tmp/":
            logger.info("Removing %s", parent_tmp_dir)
            shutil.rmtree(parent_tmp_dir)
    except:
        logger.info("Error removing %s", path)

    return removed_archive


def handle_file_output(tar_file, archive):
    if InsightsClient.options.to_stdout:
        shutil.copyfileobj(open(tar_file, 'rb'), sys.stdout)
        archive.delete_tmp_dir()
        archive.delete_archive_dir()
        archive.delete_archive_file()
    else:
        logger.info('See Insights data in %s', tar_file)
