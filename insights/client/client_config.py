'''
Declare global config here so that other modules can import it
Gets initialized in __init__._main()
'''
import logging
import optparse
import ConfigParser
from constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(APP_NAME)


class InsightsClient:
    pass


def set_up_options(parser):
    """
    Add options to the option parser
    """
    parser.add_option('--register',
                      help=('Register system to the Red Hat '
                            'Insights Service'),
                      action="store_true",
                      dest="register",
                      default=False)
    parser.add_option('--unregister',
                      help=('Unregister system from the Red Hat '
                            'Insights Service'),
                      action="store_true",
                      dest="unregister",
                      default=False)
    parser.add_option('--update-collection-rules',
                      help='Refresh collection rules from Red Hat',
                      action="store_true",
                      dest="update",
                      default=False)
    parser.add_option('--display-name',
                      action="store",
                      help='Display name for this system.  '
                           'Must be used with --register',
                      dest="display_name")
    parser.add_option('--group',
                      action="store",
                      help='Group to add this system to during registration',
                      dest="group")
    parser.add_option('--retry',
                      action="store",
                      type="int",
                      help=('Number of times to retry uploading. '
                            '%s seconds between tries'
                            % constants.sleep_time),
                      default=1,
                      dest="retries")
    parser.add_option('--validate',
                      help='Validate remove.conf',
                      action="store_true",
                      dest="validate",
                      default=False)
    parser.add_option('--quiet',
                      help='Only display error messages to stdout',
                      action="store_true",
                      dest="quiet",
                      default=False)
    parser.add_option('--silent',
                      help='Display no messages to stdout',
                      action="store_true",
                      dest="silent",
                      default=False)
    parser.add_option('--enable-schedule',
                      help='Enable automatic scheduling for collection to run',
                      action="store_true",
                      dest='enable_schedule',
                      default=False)
    parser.add_option('--disable-schedule',
                      help='Disable automatic scheduling',
                      action="store_true",
                      dest='disable_schedule',
                      default=False)
    parser.add_option('-c', '--conf',
                      help="Pass a custom config file",
                      dest="conf",
                      default=constants.default_conf_file)
    parser.add_option('--to-stdout',
                      help='print archive to stdout; '
                           'sets --quiet and --no-upload',
                      dest='to_stdout',
                      default=False,
                      action='store_true')
    parser.add_option('--compressor',
                      help='specify alternate compression '
                           'algorithm (gz, bzip2, xz, none; defaults to gz)',
                      dest='compressor',
                      default='gz')
    parser.add_option('--from-stdin',
                      help='take configuration from stdin',
                      dest='from_stdin', action='store_true',
                      default=False)
    parser.add_option('--from-file',
                      help='take configuration from file',
                      dest='from_file', action='store',
                      default=False)
    parser.add_option('--offline',
                      help='offline mode for OSP use',
                      dest='offline', action='store_true',
                      default=False)
    parser.add_option('--container',
                      help=optparse.SUPPRESS_HELP,
                      action='store_true',
                      dest='container_mode')
    parser.add_option('--logging-file',
                      help='path to log file location',
                      default=constants.default_log_file
                      )
    parser.add_option('--core-url',
                      help='url to core location',
                      default=None
                      )
    group = optparse.OptionGroup(parser, "Debug options")
    parser.add_option('--version',
                      help="Display version",
                      action="store_true",
                      dest="version",
                      default=False)
    group.add_option('--test-connection',
                     help='Test connectivity to Red Hat',
                     action="store_true",
                     dest="test_connection",
                     default=False)
    group.add_option('--force-reregister',
                     help=("Forcefully reregister this machine to Red Hat. "
                           "Use only as directed."),
                     action="store_true",
                     dest="reregister",
                     default=False)
    group.add_option('--verbose',
                     help="DEBUG output to stdout",
                     action="store_true",
                     dest="verbose",
                     default=False)
    group.add_option('--support',
                     help="Create a support logfile for Red Hat Insights",
                     action="store_true",
                     dest="support",
                     default=False)
    group.add_option('--status',
                     help="Check this machine's registration status with Red Hat Insights",
                     action="store_true",
                     dest="status",
                     default=False)
    group.add_option('--no-gpg',
                     help="Do not verify GPG signature",
                     action="store_true",
                     dest="no_gpg",
                     default=False)
    group.add_option('--no-upload',
                     help="Do not upload the archive",
                     action="store_true",
                     dest="no_upload",
                     default=False)
    group.add_option('--no-tar-file',
                     help="Build the directory, but do not tar",
                     action="store_true",
                     dest="no_tar_file",
                     default=False)
    group.add_option('--keep-archive',
                     help="Do not delete archive after upload",
                     action="store_true",
                     dest="keep_archive",
                     default=False)
    group.add_option('--original-style-specs',
                     help=optparse.SUPPRESS_HELP,
                     action="store_true",
                     dest="original_style_specs",
                     default=False)
    group.add_option('--docker-image-name',
                     help=optparse.SUPPRESS_HELP,
                     action="store",
                     dest="docker_image_name",
                     default=None)
    group.add_option('--only',
                     help=optparse.SUPPRESS_HELP,
                     action="store",
                     dest="only",
                     default=None)
    group.add_option('--use-docker',
                     help=optparse.SUPPRESS_HELP,
                     action="store_true",
                     dest="use_docker",
                     default=None)
    group.add_option('--use-atomic',
                     help=optparse.SUPPRESS_HELP,
                     action="store_true",
                     dest="use_atomic",
                     default=None)
    group.add_option('--run-these',
                     help=optparse.SUPPRESS_HELP,
                     action="store",
                     dest="run_specific_specs",
                     default=None)
    # this option is for when we run inside a container, so
    #  that another container is not spawned
    #  undocumented option
    group.add_option('--run-here',
                     help=optparse.SUPPRESS_HELP,
                     action="store_true",
                     dest="run_here",
                     default=False),
    group.add_option('--just-upload',
                     help=optparse.SUPPRESS_HELP,
                     action='store',
                     dest='just_upload')
    parser.add_option_group(group)


def parse_config_file(conf_file=constants.default_conf_file):
    """
    Parse the configuration from the file
    """
    parsedconfig = ConfigParser.RawConfigParser(
        {'loglevel': constants.log_level,
         'trace': 'False',
         'app_name': constants.app_name,
         'auto_config': 'True',
         'authmethod': constants.auth_method,
         'base_url': constants.base_url,
         'upload_url': None,
         'api_url': None,
         'branch_info_url': None,
         'auto_update': 'True',
         'collection_rules_url': None,
         'obfuscate': 'False',
         'obfuscate_hostname': 'False',
         'cert_verify': constants.default_ca_file,
         'gpg': 'True',
         'username': '',
         'password': '',
         'systemid': None,
         'proxy': None,
         'insecure_connection': 'False',
         'no_schedule': 'False',
         'docker_image_name': '',
         'logging_file': constants.default_log_file,
         'display_name': None,
         'verbose': False})
    try:
        parsedconfig.read(conf_file)
    except ConfigParser.Error:
        logger.error("ERROR: Could not read configuration file, using defaults")
    try:
        # Try to add the insights-client section
        parsedconfig.add_section(APP_NAME)
        # Try to add the redhat_access_insights section for back compat
        parsedconfig.add_section('redhat_access_insights')
    except ConfigParser.Error:
        pass
    return parsedconfig
