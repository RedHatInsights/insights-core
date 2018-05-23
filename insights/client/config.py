from __future__ import absolute_import
import os
import logging
import optparse
import copy
import six
from six.moves import configparser as ConfigParser

from .constants import InsightsConstants as constants

logger = logging.getLogger(__name__)

APP_NAME = constants.app_name
DEFAULT_OPTS = {
    'analyze_container': {
        'default': False,
        'opt': ['--analyze-container'],
        'help': optparse.SUPPRESS_HELP,  # ??
        'action': 'store_true'
    },
    'analyze_image_id': {
        'default': None,
        'opt': ['--analyze-image-id'],
        'help': optparse.SUPPRESS_HELP,  # ??
        'action': 'store'
    },
    'analyze_file': {
        'default': None,
        'opt': ['--analyze-file'],
        'help': optparse.SUPPRESS_HELP,  # ??
        'action': 'store'
    },
    'analyze_mountpoint': {
        'default': None,
        'opt': ['--analyze-mountpoint'],
        'help': optparse.SUPPRESS_HELP,  # ??
        'action': 'store'
    },
    'api_url': {
        # non-CLI
        'default': None
    },
    'app_name': {
        # non-CLI
        'default': 'insights-client'
    },
    'authmethod': {
        # non-CLI
        'default': 'BASIC'
    },
    'auto_config': {
        # non-CLI
        'default': True
    },
    'auto_update': {
        # non-CLI
        'default': True
    },
    'base_url': {
        # non-CLI
        'default': 'cert-api.access.redhat.com/r/insights'
    },
    'branch_info_url': {
        # non-CLI
        'default': None
    },
    'cert_verify': {
        # non-CLI
        'default': os.path.join(
            constants.default_conf_dir,
            'cert-api.access.redhat.com.pem'),
    },
    'collection_rules_url': {
        # non-CLI
        'default': None
    },
    'compressor': {
        'default': 'gz',
        'opt': ['--compressor'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_true'
    },
    'conf': {
        'default': constants.default_conf_file,
        'opt': ['--conf', '-c'],
        'help': 'Pass a custom config file',
        'action': 'store'
    },
    'egg_path': {
        # non-CLI
        'default': '/v1/static/core/insights-core.egg'
    },
    'debug': {
        'default': False,  # Used by client wrapper script
        'opt': ['--debug-phases'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_true',
        'dest': 'debug'
    },
    'disable_schedule': {
        'default': False,
        'opt': ['--disable-schedule'],
        'help': 'Disable automatic scheduling',
        'action': 'store_true'
    },
    'display_name': {
        'default': None,
        'opt': ['--display-name'],
        'help': 'Display name for this system. '
                'Must be used with --register',
        'action': 'store'
    },
    'enable_schedule': {
        'default': False,
        'opt': ['--enable-schedule'],
        'help': 'Enable automatic scheduling for collection to run',
        'action': 'store_true',
    },
    'from_file': {
        'default': False,
        'opt': ['--from-file'],
        'help': optparse.SUPPRESS_HELP,  # ?
        'action': 'store'
    },
    'from_stdin': {
        'default': False,
        'opt': ['--from-stdin'],
        'help': optparse.SUPPRESS_HELP,  # ?
        'action': 'store_true',
    },
    'gpg': {
        'default': True,
        'opt': ['--no-gpg'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_false',
        'group': 'debug'
    },
    'egg_gpg_path': {
        # non-CLI
        'default': '/v1/static/core/insights-core.egg.asc'
    },
    'group': {
        'default': None,
        'opt': ['--group'],
        'help': 'Group to add this system to during registration',
        'action': 'store',
    },
    'insecure_connection': {
        # non-CLI
        'default': False
    },
    'keep_archive': {
        'default': False,
        'opt': ['--keep-archive'],
        'help': 'Do not delete archive after upload',
        'action': 'store_true',
        'group': 'debug'
    },
    'logging_file': {
        'default': os.path.join(
            constants.log_dir,
            constants.app_name) + '.log',
        'opt': ['--logging-file'],
        'help': 'Path to log file location',
        'action': 'store'
    },
    'loglevel': {
        # non-CLI
        'default': 'DEBUG'
    },
    'net_debug': {
        'default': False,
        'opt': ['--net-debug'],
        'help': 'Log the HTTP method and URL every time a network call is made.',
        'action': 'store_true'
    },
    'no_gpg': {
        # non-CLI
        'default': False,  # legacy
    },
    'no_upload': {
        'default': False,
        'opt': ['--no-upload'],
        'help': 'Do not upload the archive',
        'action': 'store_true',
        'group': 'debug'
    },
    'obfuscate': {
        # non-CLI
        'default': False
    },
    'obfuscate_hostname': {
        # non-CLI
        'default': False
    },
    'offline': {
        'default': False,
        'opt': ['--offline'],
        'help': 'offline mode for OSP use',
        'action': 'store_true'
    },
    'password': {
        # non-CLI
        'default': ''
    },
    'proxy': {
        # non-CLI
        'default': None
    },
    'quiet': {
        'default': False,
        'opt': ['--quiet'],
        'help': 'Only display error messages to stdout',
        'action': 'store_true'
    },
    'register': {
        'default': False,
        'opt': ['--register'],
        'help': 'Register system to the Red Hat Insights Service',
        'action': 'store_true'
    },
    'reregister': {
        'default': False,
        'opt': ['--force-reregister'],
        'help': 'Forcefully reregister this machine to Red Hat. Use only as directed.',
        'action': 'store_true',
        'group': 'debug',
        'dest': 'reregister'
    },
    'retries': {
        'default': 1,
        'opt': ['--retry'],
        'help': ('Number of times to retry uploading. %s seconds between tries' %
                 constants.sleep_time),
        'action': 'store',
        'type': 'int',
        'dest': 'retries'
    },
    'run_specific_specs': {
        'default': None,
        'opt': ['--run-these'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store',
        'group': 'debug',
        'dest': 'run_specific_specs'
    },
    'silent': {
        'default': False,
        'opt': ['--silent'],
        'help': 'Display no messages to stdout',
        'action': 'store_true'
    },
    'status': {
        'default': False,
        'opt': ['--status'],
        'help': 'Check this machine\'s registration status with Red Hat Insights',
        'action': 'store_true',
        'group': 'debug'
    },
    'support': {
        'default': False,
        'opt': ['--support'],
        'help': 'Create a support logfile for Red Hat Insights',
        'action': 'store_true',
        'group': 'debug'
    },
    # 'systemid': {
    #     'default': None
    # },
    'test_connection': {
        'default': False,
        'opt': ['--test-connection'],
        'help': 'Test connectivity to Red Hat',
        'action': 'store_true'
    },
    'to_json': {
        'default': False,
        'opt': ['--to-json'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_true'
    },
    'to_stdout': {
        'default': False,
        'opt': ['--to-stdout'],
        'help': 'print archive to stdout; '
                'sets --quiet and --no-upload',
        'action': 'store_true'
    },
    'unregister': {
        'default': False,
        'opt': ['--unregister'],
        'help': 'Unregister system from the Red Hat Insights Service',
        'action': 'store_true'
    },
    'upload_url': {
        # non-CLI
        'default': None
    },
    'use_atomic': {
        'default': None,
        'opt': ['--use-atomic'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_true',
        'group': 'debug'
    },
    'use_docker': {
        'default': None,
        'opt': ['--use-docker'],
        'help': optparse.SUPPRESS_HELP,
        'action': 'store_true',
        'group': 'debug'
    },
    'username': {
        # non-CLI
        'default': ''
    },
    'validate': {
        'default': False,
        'opt': ['--validate'],
        'help': 'Validate remove.conf',
        'action': 'store_true'
    },
    'verbose': {
        'default': False,
        'opt': ['--verbose'],
        'help': "DEBUG output to stdout",
        'action': "store_true",
        'group': 'debug'
    },
    'version': {
        'default': False,
        'opt': ['--version'],
        'help': "Display version",
        'action': "store_true"
    }
}

DEFAULT_KVS = {k: v['default'] for k, v in DEFAULT_OPTS.iteritems()}
DEFAULT_BOOLS = [k for k, v in DEFAULT_KVS.iteritems() if type(v) is bool]


class InsightsConfig(object):
    '''
    Insights client configuration
    '''

    def __init__(self, *args, **kwargs):
        self._init_attrs = copy.copy(dir(self))
        self._update_dict(DEFAULT_KVS)
        self._update_dict(args[0])
        self._update_dict(kwargs)

    def __str__(self):
        _str = ''
        for key in dir(self):
            val = getattr(self, key)
            if not key.startswith('_'):
                # ignore built-in/private stuff
                _str += key + ': ' + str(val) + '\n'
        return _str

    def _update_dict(self, dict_):
        '''
        Update without allowing undefined options or overwrite of class methods
        '''
        dict_ = {k: v for k, v in dict_.iteritems() if (
                    k not in self._init_attrs)}

        if set(dict_.keys()).difference(set(DEFAULT_OPTS.keys())):
            raise ValueError
        self.__dict__.update(dict_)

    def load_env(self):
        '''
        Options can be set as environment variables
        The formula for the key is `"INSIGHTS_%s" % key.upper()`
        In English, that's the uppercase version of the config key with
        "INSIGHTS_" prepended to it.
        '''
        def _boolify(v):
            if v.lower() == 'true':
                return True
            elif v.lower() == 'false':
                return False
            else:
                return v

        insights_env_opts = dict((k.lower().split("_", 1)[1], _boolify(v))
                                 for k, v in os.environ.items()
                                 if k.upper().startswith("INSIGHTS_"))
        self._update_dict(insights_env_opts)

    def load_command_line(self):
        '''
        Load config from command line switches.
        NOTE: Not all config is available on the command line.
        '''
        parser = optparse.OptionParser()
        debug_grp = optparse.OptionGroup(parser, "Debug options")
        cli_options = {k: v for k, v in DEFAULT_OPTS.iteritems() if (
                        'opt' in v)}
        for _, o in cli_options.iteritems():
            g = debug_grp if o.pop("group", None) == "debug" else parser
            optnames = o.pop('opt')
            g.add_option(*optnames, **o)

        parser.add_option_group(debug_grp)
        options, args = parser.parse_args()
        if len(args) > 0:
            parser.error("Unknown arguments: %s" % args)

        self._update_dict(vars(options))

    def load_config_file(self, fname=None):
        '''
        Load config from config file. If fname is not specified,
        config is loaded from the file named by InsightsConfig.conf
        '''
        parsedconfig = ConfigParser.RawConfigParser(DEFAULT_KVS)
        try:
            parsedconfig.read(fname or self.conf)
        except ConfigParser.Error:
            logger.error(
                'ERROR: Could not read configuration file, using defaults')
        try:
            # Try to add the insights-client section
            parsedconfig.add_section(APP_NAME)
            # Try to add the redhat_access_insights section for back compat
            parsedconfig.add_section('redhat_access_insights')
        except ConfigParser.Error:
            pass
        d = dict(parsedconfig.items(APP_NAME))
        for key in d:
            if key in DEFAULT_BOOLS and type(d[key]) in six.string_types:
                d[key] = parsedconfig.getboolean(APP_NAME, key)
        self._update_dict(d)

    def _validate_options(self):
        '''
        Make sure there are no conflicting or invalid options
        '''
        if self.obfuscate_hostname and not self.obfuscate:
            raise ValueError(
                'Option `obfuscate_hostname` requires `obfuscate`')
        if self.analyze_image_id is not None and len(self.analyze_image_id < 12):
            raise ValueError(
                'Image/Container ID must be at least twelve characters long.')
        if self.from_stdin and self.from_file:
            raise ValueError('Can\'t use both --from-stdin and --from-file.')

    def _imply_options(self):
        '''
        Some options enable others automatically
        '''
        self.no_upload = self.no_upload or self.to_stdout or self.offline
        self.auto_update = self.auto_update or self.offline
        self.analyze_container = self.analyze_file or self.analyze_mountpoint
        self.to_json = self.analyze_container and not self.to_stdout


if __name__ == '__main__':
    config = InsightsConfig({'username': 'fezzan'})
    print(config)
