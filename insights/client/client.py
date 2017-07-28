import sys
import json
import logging
import logging.handlers
import os
import shutil
import time
import optparse
from auto_config import try_auto_configuration
from utilities import (validate_remove_file,
                       generate_machine_id,
                       generate_analysis_target_id,
                       write_to_disk,
                       write_unregistered_file,
                       determine_hostname,
                       logging_file)
from collection_rules import InsightsConfig
from data_collector import DataCollector
from connection import InsightsConnection
from archive import InsightsArchive
from support import InsightsSupport, registration_check
from constants import InsightsConstants as constants
from client_config import parse_config_file, InsightsClient, set_up_options

LOG_FORMAT = ("%(asctime)s %(levelname)8s %(name)s %(message)s")
APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


def parse_options():
    """
        returns (tuple): returns a tuple with configparser and argparser options
    """
    class NoErrOptionParser(optparse.OptionParser):
        def __init__(self, *args, **kwargs):
            self.valid_args_cre_list = []
            optparse.OptionParser.__init__(self, *args, **kwargs)

        def error(self, msg):
            pass
    parser = NoErrOptionParser()
    set_up_options(parser)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unknown arguments: %s" % args)
    return parse_config_file(options.conf), options


def get_file_handler():
    log_file = logging_file()
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, 0700)
    return logging.handlers.RotatingFileHandler(log_file, backupCount=3)


def get_console_handler(silent, verbose, to_stdout):
    if silent:
        target_level = logging.NOTSET
    elif verbose:
        target_level = logging.DEBUG
    elif to_stdout:
        target_level = logging.ERROR
    else:
        target_level = logging.INFO

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    stdout_handler.setLevel(target_level)

    return stdout_handler


def configure_level(conf, verbose):
    config_level = 'DEBUG' if verbose else conf.get(APP_NAME, 'loglevel')

    init_log_level = logging.getLevelName(config_level)
    if type(init_log_level) in (str, unicode):
        print "Invalid log level %s, defaulting to DEBUG" % config_level
        init_log_level = logging.DEBUG

    logger.setLevel(init_log_level)
    logging.root.setLevel(init_log_level)


def set_up_logging():
    if len(logging.root.handlers) == 0:
        # Just to reduce amount of text
        opts, conf = InsightsClient.options, InsightsClient.config

        # from_stdin mode implies to_stdout
        opts.to_stdout = (opts.to_stdout or opts.from_stdin or opts.from_file)

        verbose = opts.verbose or conf.get(APP_NAME, 'verbose')
        logging.root.addHandler(get_console_handler(opts.silent, verbose, opts.to_stdout))
        logging.root.addHandler(get_file_handler())
        configure_level(conf, verbose)
        logger.debug("Logging initialized")


def test_connection():
    """
    Test the connection
    """
    pconn = InsightsConnection()
    return pconn.test_connection()


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
    if os.path.isfile(constants.registered_file):
        logger.info('This host has already been registered.')
        return
    # check reg status with API
    reg_check = registration_check()
    if reg_check['status']:
        logger.info('This host has already been registered.')
        # regenerate the .registered file
        write_to_disk(constants.registered_file)
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
    return reg_check, message, hostname, group, display_name


def register():
    """
    Do registration using basic auth
    """
    username = InsightsClient.config.get(APP_NAME, 'username')
    password = InsightsClient.config.get(APP_NAME, 'password')
    authmethod = InsightsClient.config.get(APP_NAME, 'authmethod')
    auto_config = InsightsClient.config.getboolean(APP_NAME, 'auto_config')
    if not username and not password and not auto_config and authmethod == 'BASIC':
        logger.debug('Username and password must be defined in configuration file with BASIC authentication method.')
        return False
    pconn = InsightsConnection()
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
    if InsightsClient.options.reregister:
        logger.debug('Re-register set, forcing registration.')
        new = True
        InsightsClient.options.register = True
        write_to_disk(constants.registered_file, delete=True)
        write_to_disk(constants.unregistered_file, delete=True)
        write_to_disk(constants.machine_id_file, delete=True)
    logger.debug('Machine-id: %s', generate_machine_id(new))

    logger.debug('Trying registration.')
    registration = try_register()
    msg, is_registered = _is_client_registered()

    return {'success': is_registered,
            'machine-id': generate_machine_id(),
            'registration': registration}


def get_registration_status():
    return registration_check()


def handle_unregistration():
    """
        returns (bool): True success, False failure
    """
    pconn = InsightsConnection()
    return pconn.unregister()


def get_machine_id():
    return generate_machine_id()


def fetch_rules():
    pconn = InsightsConnection()
    pc = InsightsConfig(pconn)
    return pc.get_conf(InsightsClient.options.update, {})


def update_rules():
    pconn = InsightsConnection()
    pc = InsightsConfig(pconn)
    return pc.get_conf(True, {})


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

    collection_rules, rm_conf = pc.get_conf(False, stdin_config)
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

            machine_id = generate_analysis_target_id(t['type'], t['name'])
            archive_meta['system_id'] = machine_id
            archive_meta['machine_id'] = machine_id

            if InsightsClient.options.container_mode:
                compressor = "none"
            else:
                compressor = InsightsClient.options.compressor

            archive = InsightsArchive(compressor=compressor, target_name=t['name'])
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

    # Write the .lastcollected date
    if tar_file is not None:
        with open(constants.archive_last_collected_date_file, 'w') as the_file:
            import time
            last_collected_time = str(time.time())
            the_file.write(last_collected_time + "\n")
            the_file.write(tar_file)
            logger.debug("Wrote %s to %s as timestamp" %
                (last_collected_time, constants.archive_last_collected_date_file))
            logger.debug("Wrote %s to %s as last collected archive" %
                (tar_file, constants.archive_last_collected_date_file))

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

            machine_id = generate_machine_id()

            # Write to last upload file
            with open(constants.last_upload_results_file, 'w') as handler:
                handler.write(upload.text.encode('utf-8'))
            write_to_disk(constants.lastupload_file)

            # Write to ansible facts directory
            if os.path.isdir(constants.insights_ansible_facts_dir):
                import json
                insights_facts = {}
                insights_facts['last_upload'] = json.loads(upload.text)

                from auto_config import (_try_satellite6_configuration,
                                         _try_satellite5_configuration)

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


def handle_startup():
    """
    Handle startup options
    """
    # ----do X and exit options----
    # show version and exit
    if InsightsClient.options.version:
        return constants.version

    if InsightsClient.options.validate:
        return validate_remove_file()

    # do auto_config here, for connection-related 'do X and exit' options
    if InsightsClient.config.getboolean(APP_NAME, 'auto_config') and not InsightsClient.options.offline:
        # Try to discover if we are connected to a satellite or not
        try_auto_configuration()

    if InsightsClient.options.test_connection:
        pconn = InsightsConnection()
        rc = pconn.test_connection()
        return rc

    if InsightsClient.options.status:
        reg_check = registration_check()
        for msg in reg_check['messages']:
            logger.debug(msg)
        # exit with !status, 0 for True, 1 for False
        return reg_check['status']

    if InsightsClient.options.support:
        support = InsightsSupport()
        support.collect_support_info()
        return True

    if InsightsClient.config.getboolean(APP_NAME, 'auto_update') and not InsightsClient.options.offline:
        # TODO: config updates option, but in GPG option, the option updates
        # the config.  make this consistent
        InsightsClient.options.update = True

    # can't use bofa
    if InsightsClient.options.from_stdin and InsightsClient.options.from_file:
        logger.error('Can\'t use both --from-stdin and --from-file.')
        return False

    if InsightsClient.options.to_stdout:
        InsightsClient.options.no_upload = True

    # ----register options----
    # put this first to avoid conflicts with register
    if InsightsClient.options.unregister:
        pconn = InsightsConnection()
        return pconn.unregister()

    # force-reregister -- remove machine-id files and registration files
    # before trying to register again
    new = False
    if InsightsClient.options.reregister:
        new = True
        InsightsClient.options.register = True
        write_to_disk(constants.registered_file, delete=True)
        write_to_disk(constants.registered_file, delete=True)
        write_to_disk(constants.machine_id_file, delete=True)
    logger.debug('Machine-id: %s', generate_machine_id(new))

    if InsightsClient.options.register:
        try_register()

    # check registration before doing any uploads
    # Ignore if in offline mode
    if not InsightsClient.options.register and not InsightsClient.options.offline:
        msg, is_registered = _is_client_registered()
        if not is_registered:
            logger.error(msg)
            return False
