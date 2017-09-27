import logging
import optparse
import os
from insights.contrib import ConfigParser

from insights import settings
from constants import InsightsConstants as constants

logger = logging.getLogger(__name__)

APP_NAME = 'insights-client'
CONF_DIR = os.path.join('/etc', APP_NAME)
CONF_FILE = os.path.join(CONF_DIR, 'insights-client.conf')

BOOLEAN_KEYS = [
    'analyze_container', 'auto_config', 'auto_update',
    'debug', 'disable_schedule', 'enable_schedule', 'from_file', 'from_stdin',
    'gpg', 'insecure_connection', 'keep_archive', 'net_debug', 'no_gpg',
    'no_tar_file', 'no_upload', 'obfuscate',
    'obfuscate_hostname', 'offline', 'original_style_specs', 'quiet',
    'register', 'reregister', 'silent', 'status', 'support',
    'test_connection', 'to_stdout', 'unregister', 'validate',
    'verbose', 'version', 'to_json'
]

CONFIG = {
    'analyze_container': False,
    'analyze_image_id': None,
    'analyze_file': None,
    'analyze_mountpoint': None,
    'api_url': None,
    'app_name': 'insights-client',
    'authmethod': 'BASIC',
    'auto_config': True,
    'auto_update': True,
    'base_url': 'cert-api.access.redhat.com/r/insights',
    'branch_info_url': None,
    'cert_verify': os.path.join(CONF_DIR, 'cert-api.access.redhat.com.pem'),
    'collection_rules_url': None,
    'compressor': 'gz',
    'conf': os.path.join(CONF_DIR, 'insights-client.conf'),
    'container_mode': None,
    'egg_path': '/v1/static/core/insights-core.egg',
    'debug': False,  # Used by client wrapper script
    'disable_schedule': False,
    'display_name': None,
    'docker_image_name': None,
    'enable_schedule': False,
    'from_file': False,
    'from_stdin': False,
    'gpg': True,
    'egg_gpg_path': '/v1/static/core/insights-core.egg.asc',
    'group': None,
    'insecure_connection': False,
    'keep_archive': False,
    'logging_file': os.path.join(constants.log_dir, APP_NAME) + '.log',
    'loglevel': 'DEBUG',
    'mountpoint': None,
    'net_debug': False,
    'no_gpg': False,  # legacy
    'no_tar_file': False,
    'no_upload': False,
    'obfuscate': False,
    'obfuscate_hostname': False,
    'offline': False,
    'original_style_specs': False,
    'password': '',
    'proxy': None,
    'quiet': False,
    'register': False,
    'reregister': False,
    'retries': 1,
    'run_specific_specs': None,
    'silent': False,
    'status': False,
    'support': False,
    'systemid': None,
    'test_connection': False,
    'to_stdout': False,
    'unregister': False,
    'upload_url': None,
    'use_atomic': None,
    'use_docker': None,
    'username': '',
    'validate': False,
    'verbose': False,
    'version': False,
    'to_json': False
}

OPTS = [{
    'opt': ['--version'],
    'help': "Display version",
    'action': "store_true",
    'dest': "version",
}, {
    'opt': ['--register'],
    'help': 'Register system to the Red Hat Insights Service',
    'action': "store_true",
    'dest': "register",
}, {
    'opt': ['--unregister'],
    'help': 'Unregister system from the Red Hat Insights Service',
    'action': "store_true",
    'dest': "unregister",
}, {
    'opt': ['--display-name'],
    'action': "store",
    'help': 'Display name for this system.  '
    'Must be used with --register',
    'dest': "display_name"
}, {
    'opt': ['--group'],
    'action': "store",
    'help': 'Group to add this system to during registration',
    'dest': "group"
}, {
    'opt': ['--retry'],
    'action': "store",
    'type': "int",
    'help': ('Number of times to retry uploading. %s seconds between tries' %
             constants.sleep_time),
    'dest': "retries"
}, {
    'opt': ['--validate'],
    'help': 'Validate remove.conf',
    'action': "store_true",
    'dest': "validate",
}, {
    'opt': ['--quiet'],
    'help': 'Only display error messages to stdout',
    'action': "store_true",
    'dest': "quiet",
}, {
    'opt': ['--silent'],
    'help': 'Display no messages to stdout',
    'action': "store_true",
    'dest': "silent",
}, {
    'opt': ['--enable-schedule'],
    'help': 'Enable automatic scheduling for collection to run',
    'action': "store_true",
    'dest': 'enable_schedule',
}, {
    'opt': ['--disable-schedule'],
    'help': 'Disable automatic scheduling',
    'action': "store_true",
    'dest': 'disable_schedule',
}, {
    'opt': ['-c', '--conf'],
    'help': "Pass a custom config file",
    'dest': "conf",
}, {
    'opt': ['--to-stdout'],
    'help': 'print archive to stdout; '
    'sets --quiet and --no-upload',
    'dest': 'to_stdout',
    'action': 'store_true'
}, {
    'opt': ['--compressor'],
    'help': optparse.SUPPRESS_HELP,
    'dest': 'compressor',
}, {
    'opt': ['--from-stdin'],
    'help': optparse.SUPPRESS_HELP,
    'dest': 'from_stdin',
    'action': 'store_true',
}, {
    'opt': ['--from-file'],
    'help': optparse.SUPPRESS_HELP,
    'dest': 'from_file',
    'action': 'store',
}, {
    'opt': ['--offline'],
    'help': 'offline mode for OSP use',
    'dest': 'offline',
    'action': 'store_true',
}, {
    'opt': ['--analyze-container'],
    'help': optparse.SUPPRESS_HELP,
    'action': 'store_true',
    'dest': 'analyze_container'
}, {
    'opt': ['--logging-file'],
    'help': 'path to log file location',
    'dest': 'logging_file'
}, {
    'opt': ['--analyze-file'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store",
    'dest': "analyze_file",
}, {
    'opt': ['--analyze-mountpoint'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store",
    'dest': "analyze_mountpoint",
}, {
    'opt': ['--test-connection'],
    'help': 'Test connectivity to Red Hat',
    'action': "store_true",
    'dest': "test_connection",
    'group': 'debug'
}, {
    'opt': ['--force-reregister'],
    'help': "Forcefully reregister this machine to Red Hat. Use only as directed.",
    'action': "store_true",
    'dest': "reregister",
    'group': 'debug'
}, {
    'opt': ['--verbose'],
    'help': "DEBUG output to stdout",
    'action': "store_true",
    'dest': "verbose",
    'group': 'debug'
}, {
    'opt': ['--support'],
    'help': "Create a support logfile for Red Hat Insights",
    'action': "store_true",
    'dest': "support",
    'group': 'debug'
}, {
    'opt': ['--status'],
    'help': "Check this machine's registration status with Red Hat Insights",
    'action': "store_true",
    'dest': "status",
    'group': 'debug'
}, {
    'opt': ['--no-gpg'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store_false",
    'dest': "gpg",
    'group': 'debug'
}, {
    'opt': ['--no-upload'],
    'help': "Do not upload the archive",
    'action': "store_true",
    'dest': "no_upload",
    'group': 'debug'
}, {
    'opt': ['--no-tar-file'],
    'help': "Build the directory, but do not tar",
    'action': "store_true",
    'dest': "no_tar_file",
    'group': 'debug'
}, {
    'opt': ['--keep-archive'],
    'help': "Do not delete archive after upload",
    'action': "store_true",
    'dest': "keep_archive",
    'group': 'debug'
}, {
    'opt': ['--original-style-specs'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store_true",
    'dest': "original_style_specs",
    'group': 'debug'
}, {
    'opt': ['--docker-image-name'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store",
    'dest': "docker_image_name",
    'group': 'debug'
}, {
    'opt': ['--use-docker'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store_true",
    'dest': "use_docker",
    'group': 'debug'
}, {
    'opt': ['--use-atomic'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store_true",
    'dest': "use_atomic",
    'group': 'debug'
}, {
    'opt': ['--run-these'],
    'help': optparse.SUPPRESS_HELP,
    'action': "store",
    'dest': "run_specific_specs",
    'group': 'debug'
}, {
    'opt': ['--debug-phases'],
    'help': optparse.SUPPRESS_HELP,
    'action': 'store_true',
    'dest': 'debug',
    'group': 'debug'
}, {
    'opt': ['--net-debug'],
    'help': "Log the HTTP method and URL every time a network call is made.",
    'action': 'store_true',
    'dest': 'net_debug'
}, {
    'opt': ['--to-json'],
    'help': optparse.SUPPRESS_HELP,
    'action': 'store_true',
    'dest': 'to_json'
}]


def parse_options():
    parser = optparse.OptionParser()
    group = optparse.OptionGroup(parser, "Debug options")
    for d in (dict(d) for d in OPTS):
        g = group if d.pop("group", None) == "debug" else parser
        optnames = d.pop("opt")
        g.add_option(*optnames, default=CONFIG[d["dest"]], **d)

    parser.add_option_group(group)
    options, args = parser.parse_args()
    if len(args) > 0:
        parser.error("Unknown arguments: %s" % args)
    return vars(options)


def parse_config_file(conf_file=constants.default_conf_file):
    parsedconfig = ConfigParser.RawConfigParser(CONFIG)
    try:
        parsedconfig.read(CONF_FILE)
    except ConfigParser.Error:
        logger.error("ERROR: Could not read configuration file, using defaults")
    try:
        # Try to add the insights-client section
        parsedconfig.add_section(APP_NAME)
        # Try to add the redhat_access_insights section for back compat
        parsedconfig.add_section('redhat_access_insights')
    except ConfigParser.Error:
        pass
    d = dict(parsedconfig.items(APP_NAME))
    for key in (k for k in BOOLEAN_KEYS if type(d.get(k)) in (str, unicode)):
        d[key] = parsedconfig.getboolean(APP_NAME, key)
    return d


def apply_legacy_config():
    """
    Map legacy options to the key that's used.
    """
    if CONFIG['no_gpg']:
        CONFIG['gpg'] = False


def boolify(v):
    if v.lower() == "true":
        return True
    elif v.lower() == "false":
        return False
    else:
        return v


def compile_config():
    # Options can be set as environment variables
    # The formula for the key is `"INSIGHTS_%s" % key.upper()`
    # In English, that's the uppercase version of the config key with
    # "INSIGHTS_" prepended to it.
    insights_env_opts = dict((k.lower().split("_", 1)[1], boolify(v))
                             for k, v in os.environ.iteritems()
                             if k.upper().startswith("INSIGHTS_"))
    CONFIG.update(insights_env_opts)

    # TODO: If the defaults.yaml file ever fills in all the client config, then
    # they will clobber the legacy file, even if the user has no insights.yaml
    # defined!!
    CONFIG.update(parse_config_file())

    # This is done here specifically because it's after the legacy config file
    # has been read yet before the new config file and command line arguments
    # have been parsed.
    apply_legacy_config()

    if "client" in settings.config:
        CONFIG.update(settings.config)
    CONFIG.update(parse_options())

    # flags that imply no_upload
    if CONFIG['to_stdout']:
        CONFIG['no_upload'] = True

    if (CONFIG['analyze_image_id'] is not None) and (len(CONFIG['analyze_image_id']) < 12):
        raise ValueError("Image/Container ID must be at least twelve characters long.")

    if CONFIG['from_stdin'] and CONFIG['from_file']:
        raise ValueError("Can't use both --from-stdin and --from-file.")

    # offline implied auto_update=False
    if CONFIG['offline']:
        CONFIG['auto_update'] = False

    # handle container mode stuff
    if (CONFIG['analyze_image_id'] or CONFIG['analyze_file'] or CONFIG['analyze_mountpoint']):
        CONFIG['analyze_container'] = True
        CONFIG['container_mode'] = True

    if CONFIG['no_tar_file'] or CONFIG['offline']:
        CONFIG['no_upload'] = True
