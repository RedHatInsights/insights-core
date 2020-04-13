from __future__ import absolute_import
import os
import logging
import argparse
import copy
import six
import sys
from six.moves import configparser as ConfigParser

try:
    from .constants import InsightsConstants as constants
except:
    from constants import InsightsConstants as constants

logger = logging.getLogger(__name__)

DEFAULT_OPTS = {
    'analyze_container': {
        'default': False,
        'opt': ['--analyze-container'],
        'help': argparse.SUPPRESS,
        'action': 'store_true'
    },
    'analyze_image_id': {
        'default': False,
        'opt': ['--analyze-image-id'],
        'help': argparse.SUPPRESS,
        'const': True,
        'nargs': '?',
    },
    'analyze_file': {
        'default': False,
        'opt': ['--analyze-file'],
        'help': argparse.SUPPRESS,
        'const': True,
        'nargs': '?',
    },
    'analyze_mountpoint': {
        'default': False,
        'opt': ['--analyze-mountpoint'],
        'help': argparse.SUPPRESS,
        'const': True,
        'nargs': '?',
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
        'default': constants.legacy_base_url
    },
    'branch_info': {
        # non-CLI
        'default': constants.default_branch_info
    },
    'branch_info_url': {
        # non-CLI
        'default': None
    },
    'cert_verify': {
        # non-CLI
        'default': None,
    },
    'check_results': {
        'default': False,
        'opt': ['--check-results'],
        'help': "Check for insights results",
        'action': "store_true"
    },
    'cmd_timeout': {
        # non-CLI
        'default': constants.default_cmd_timeout
    },
    'collection_rules_url': {
        # non-CLI
        'default': None
    },
    'compliance': {
        'default': False,
        'opt': ['--compliance'],
        'help': 'Scan the system using openscap and upload the report',
        'action': 'store_true'
    },
    'compressor': {
        'default': 'gz',
        'opt': ['--compressor'],
        'help': argparse.SUPPRESS,
        'action': 'store'
    },
    'conf': {
        'default': constants.default_conf_file,
        'opt': ['--conf', '-c'],
        'help': 'Pass a custom config file',
        'action': 'store'
    },
    'egg_path': {
        # non-CLI
        'default': None
    },
    'debug': {
        'default': False,  # Used by client wrapper script
        'opt': ['--debug-phases'],
        'help': argparse.SUPPRESS,
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
        'help': 'Set a display name for this system. ',
        'action': 'store'
    },
    'enable_schedule': {
        'default': False,
        'opt': ['--enable-schedule'],
        'help': 'Enable automatic scheduling for collection to run',
        'action': 'store_true',
    },
    'gpg': {
        'default': True,
        'opt': ['--no-gpg'],
        'help': argparse.SUPPRESS,
        'action': 'store_false',
        'group': 'debug',
        'dest': 'gpg'
    },
    'egg_gpg_path': {
        # non-CLI
        'default': None
    },
    'group': {
        'default': None,
        'opt': ['--group'],
        'help': 'Group to add this system to during registration',
        'action': 'store',
    },
    'http_timeout': {
        # non-CLI
        'default': 120.0
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
        'default': constants.default_log_file,
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
        'action': 'store_true',
        'group': 'debug'
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
    'output_dir': {
        'default': None,
        'opt': ['--output-dir', '-od'],
        'help': 'Specify a directory to write collected data to (no compression).',
        'action': 'store'
    },
    'output_file': {
        'default': None,
        'opt': ['--output-file', '-of'],
        'help': 'Specify a compressed archive file to write collected data to.',
        'action': 'store'
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
    'remove_file': {
        # non-CLI
        'default': os.path.join(constants.default_conf_dir, 'remove.conf')
    },
    'tags_file': {
        # non-CLI
        'default': os.path.join(constants.default_conf_dir, 'tags.yaml')
    },
    'redaction_file': {
        # non-CLI
        'default': os.path.join(constants.default_conf_dir, 'file-redaction.yaml')
    },
    'content_redaction_file': {
        # non-CLI
        'default': os.path.join(constants.default_conf_dir, 'file-content-redaction.yaml')
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
        'type': int,
        'dest': 'retries'
    },
    'show_results': {
        'default': False,
        'opt': ['--show-results'],
        'help': "Show insights about this host",
        'action': "store_true"
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
    'systemid': {
        'default': None
    },
    'test_connection': {
        'default': False,
        'opt': ['--test-connection'],
        'help': 'Test connectivity to Red Hat',
        'action': 'store_true'
    },
    'to_json': {
        'default': False,
        'opt': ['--to-json'],
        'help': argparse.SUPPRESS,
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
        'help': argparse.SUPPRESS,
        'action': 'store_true',
        'group': 'debug'
    },
    'use_docker': {
        'default': None,
        'opt': ['--use-docker'],
        'help': argparse.SUPPRESS,
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
    },

    # platform options
    # hide help messages with SUPPRESS until we're ready to make them public
    'legacy_upload': {
        # True: upload to insights classic API
        # False: upload to insights platform API
        'default': True
    },
    'payload': {
        'default': None,
        'opt': ['--payload'],
        # 'help': 'Use Insights client to upload an archive',
        'help': argparse.SUPPRESS,
        'action': 'store',
        'group': 'platform'
    },
    'content_type': {
        'default': None,
        'opt': ['--content-type'],
        # 'help': 'Content type of the archive specified with --payload',
        'help': argparse.SUPPRESS,
        'action': 'store',
        'group': 'platform'
    },
    'diagnosis': {
        'default': None,
        'opt': ['--diagnosis'],
        'help': argparse.SUPPRESS,
        'const': True,
        'nargs': '?',
        'group': 'platform'
    },
    # AWS options
    'portal_access': {
        'default': False,
        'opt': ['--portal-access'],
        'group': 'platform',
        'action': 'store_true',
        'help': 'Entitle an AWS instance with Red Hat and register with Red Hat Insights'
    },
    'portal_access_no_insights': {
        'default': False,
        'opt': ['--portal-access-no-insights'],
        'group': 'platform',
        'action': 'store_true',
        'help': 'Entitle an AWS instance with Red Hat, but do not register with Red Hat Insights'
    },
    'portal_access_hydra_url': {
        # non-CLI
        'default': constants.default_portal_access_hydra_url
    }
}

DEFAULT_KVS = dict((k, v['default']) for k, v in DEFAULT_OPTS.items())
DEFAULT_BOOLS = dict(
    (k, v) for k, v in DEFAULT_KVS.items() if type(v) is bool).keys()


class InsightsConfig(object):
    '''
    Insights client configuration
    '''
    def __init__(self, *args, **kwargs):
        # this is only used to print configuration errors upon initial load
        self._print_errors = False
        if '_print_errors' in kwargs:
            self._print_errors = kwargs['_print_errors']

        self._init_attrs = copy.copy(dir(self))
        self._update_dict(DEFAULT_KVS)
        if args:
            self._update_dict(args[0])
        self._update_dict(kwargs)
        self._imply_options()
        self._validate_options()
        self._cli_opts = None

    def __str__(self):
        _str = '    '
        for key in dir(self):
            if not (key.startswith('_') or
               key in self._init_attrs or
               key in ['password', 'proxy']):
                # ignore built-ins, functions, and sensitive items
                val = getattr(self, key)
                _str += key + ': ' + str(val) + '\n    '
        return _str

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def _update_dict(self, dict_):
        '''
        Update without allowing undefined options or overwrite of class methods
        '''
        dict_ = dict((k, v) for k, v in dict_.items() if (
                    k not in self._init_attrs))

        # zzz
        if 'no_gpg' in dict_ and dict_['no_gpg']:
            dict_['gpg'] = False

        unknown_opts = set(dict_.keys()).difference(set(DEFAULT_OPTS.keys()))
        if unknown_opts and self._print_errors:
            # only print error once
            sys.stdout.write(
                'WARNING: Unknown options: ' +
                ', '.join(list(unknown_opts)) + '\n')
            if 'no_schedule' in unknown_opts:
                sys.stdout.write('WARNING: Config option `no_schedule` has '
                                 'been deprecated. To disable automatic '
                                 'scheduling for Red Hat Insights, run '
                                 '`insights-client --disable-schedule`\n')
        for u in unknown_opts:
            dict_.pop(u, None)
        self.__dict__.update(dict_)

    def _load_env(self):
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

        # put this warning here so the error msg only prints once
        if os.environ.get('HTTP_PROXY') and self._print_errors:
            sys.stdout.write('WARNING: HTTP_PROXY is unused by insights-client. Please use HTTPS_PROXY.\n')

        # ignore these env as they are not config vars
        ignore = ['INSIGHTS_PHASE']

        insights_env_opts = dict((k.lower().split("_", 1)[1], _boolify(v))
                                 for k, v in os.environ.items()
                                 if k.upper().startswith("INSIGHTS_") and
                                 k.upper() not in ignore)

        for k in ['retries', 'cmd_timeout', 'http_timeout']:
            if k in insights_env_opts:
                v = insights_env_opts[k]
                try:
                    insights_env_opts[k] = float(v) if k == 'http_timeout' else int(v)
                except ValueError:
                    raise ValueError(
                        'ERROR: Invalid value specified for {0}: {1}.'.format(k, v))
        self._update_dict(insights_env_opts)

    def _load_command_line(self, conf_only=False):
        '''
        Load config from command line switches.
        NOTE: Not all config is available on the command line.
        '''
        # did we already parse cli (i.e. to get conf file)? don't run twice
        if self._cli_opts:
            self._update_dict(self._cli_opts)
            return
        parser = argparse.ArgumentParser()
        debug_grp = parser.add_argument_group('Debug options')
        platf_grp = parser.add_argument_group('Platform options')
        cli_options = dict((k, v) for k, v in DEFAULT_OPTS.items() if (
                       'opt' in v))
        for _, o in cli_options.items():
            group = o.pop('group', None)
            if group == 'debug':
                g = debug_grp
            elif group == 'platform':
                g = platf_grp
            else:
                g = parser
            optnames = o.pop('opt')
            # use argparse.SUPPRESS as CLI defaults so it won't parse
            #  options that weren't specified
            o['default'] = argparse.SUPPRESS
            g.add_argument(*optnames, **o)

        options = parser.parse_args()

        self._cli_opts = vars(options)
        if conf_only and 'conf' in self._cli_opts:
            self._update_dict({'conf': self._cli_opts['conf']})
            return

        self._update_dict(self._cli_opts)

    def _load_config_file(self, fname=None):
        '''
        Load config from config file. If fname is not specified,
        config is loaded from the file named by InsightsConfig.conf
        '''
        parsedconfig = ConfigParser.RawConfigParser()
        try:
            parsedconfig.read(fname or self.conf)
        except ConfigParser.Error:
            if self._print_errors:
                sys.stdout.write(
                    'ERROR: Could not read configuration file, '
                    'using defaults\n')
            return
        try:
            if parsedconfig.has_section(constants.app_name):
                d = dict(parsedconfig.items(constants.app_name))
            elif parsedconfig.has_section('redhat-access-insights'):
                d = dict(parsedconfig.items('redhat-access-insights'))
            else:
                raise ConfigParser.Error
        except ConfigParser.Error:
            if self._print_errors:
                sys.stdout.write(
                    'ERROR: Could not read configuration file, '
                    'using defaults\n')
            return
        for key in d:
            try:
                if key == 'retries' or key == 'cmd_timeout':
                    d[key] = parsedconfig.getint(constants.app_name, key)
                if key == 'http_timeout':
                    d[key] = parsedconfig.getfloat(constants.app_name, key)
                if key in DEFAULT_BOOLS and isinstance(
                        d[key], six.string_types):
                    d[key] = parsedconfig.getboolean(constants.app_name, key)
            except ValueError as e:
                if self._print_errors:
                    sys.stdout.write(
                        'ERROR: {0}.\nCould not read configuration file, '
                        'using defaults\n'.format(e))
                return
        self._update_dict(d)

    def load_all(self):
        '''
        Helper function for actual Insights client use
        '''
        # check for custom conf file before loading conf
        self._load_command_line(conf_only=True)
        self._load_config_file()
        self._load_env()
        self._load_command_line()
        self._imply_options()
        self._validate_options()
        return self

    def _validate_options(self):
        '''
        Make sure there are no conflicting or invalid options
        '''
        if self.analyze_image_id:
            raise ValueError(
                '--analyze-image-id is no longer supported.')
        if self.analyze_file:
            raise ValueError(
                '--analyze-file is no longer supported.')
        if self.analyze_mountpoint:
            raise ValueError(
                '--analyze-mountpoint is no longer supported.')
        if self.analyze_container:
            raise ValueError(
                '--analyze-container is no longer supported.')
        if self.use_atomic:
            raise ValueError(
                '--use-atomic is no longer supported.')
        if self.use_docker:
            raise ValueError(
                '--use-docker is no longer supported.')
        if self.obfuscate_hostname and not self.obfuscate:
            raise ValueError(
                'Option `obfuscate_hostname` requires `obfuscate`')
        if self.enable_schedule and self.disable_schedule:
            raise ValueError(
                'Conflicting options: --enable-schedule and --disable-schedule')
        if self.portal_access and self.portal_access_no_insights:
            raise ValueError('Conflicting options: --portal-access and --portal-access-no-insights')
        if self.payload and not self.content_type:
            raise ValueError(
                '--payload requires --content-type')
        if self.offline:
            if self.to_json:
                raise ValueError('Cannot use --to-json in offline mode.')
            if self.status:
                raise ValueError('Cannot check registration status in offline mode.')
            if self.test_connection:
                raise ValueError('Cannot run connection test in offline mode.')
        if self.output_dir and self.output_file:
            raise ValueError('Specify only one: --output-dir or --output-file.')
        if self.output_dir == '':
            # make sure an empty string is not given
            raise ValueError('--output-dir cannot be empty')
        if self.output_file == '':
            # make sure an empty string is not given
            raise ValueError('--output-file cannot be empty')
        if self.output_dir:
            if os.path.exists(self.output_dir):
                if os.path.isfile(self.output_dir):
                    raise ValueError('%s is a file.' % self.output_dir)
                if os.listdir(self.output_dir):
                    raise ValueError('Directory %s already exists and is not empty.' % self.output_dir)
            parent_dir = os.path.dirname(self.output_dir.rstrip('/'))
            if not os.path.exists(parent_dir):
                raise ValueError('Cannot write to %s. Parent directory %s does not exist.' % (self.output_dir, parent_dir))
            if not os.path.isdir(parent_dir):
                raise ValueError('Cannot write to %s. %s is not a directory.' % (self.output_dir, parent_dir))
            if self.obfuscate:
                if self._print_errors:
                    sys.stdout.write('WARNING: SOSCleaner reports will be created alongside the output directory.\n')
        if self.output_file:
            if os.path.exists(self.output_file):
                raise ValueError('File %s already exists.' % self.output_file)
            parent_dir = os.path.dirname(self.output_file.rstrip('/'))
            if not os.path.exists(parent_dir):
                raise ValueError('Cannot write to %s. Parent directory %s does not exist.' % (self.output_file, parent_dir))
            if not os.path.isdir(parent_dir):
                raise ValueError('Cannot write to %s. %s is not a directory.' % (self.output_file, parent_dir))
            if self.obfuscate:
                if self._print_errors:
                    sys.stdout.write('WARNING: SOSCleaner reports will be created alongside the output archive.\n')

    def _imply_options(self):
        '''
        Some options enable others automatically
        '''
        self.no_upload = self.no_upload or self.offline
        self.auto_update = self.auto_update and not self.offline
        if (self.analyze_container or
           self.analyze_file or
           self.analyze_mountpoint or
           self.analyze_image_id):
            self.analyze_container = True
        self.to_json = self.to_json or self.analyze_container
        self.register = (self.register or self.reregister) and not self.offline
        self.keep_archive = self.keep_archive or self.no_upload
        if self.to_json and self.quiet:
            self.diagnosis = True
        if self.payload or self.diagnosis or self.compliance or self.show_results or self.check_results:
            self.legacy_upload = False
        if self.payload and (self.logging_file == constants.default_log_file):
            self.logging_file = constants.default_payload_log
        if os.path.exists(constants.register_marker_file):
            self.register = True
        if self.output_dir or self.output_file:
            # do not upload in this case
            self.no_upload = True
            # don't keep the archive or files in temp
            #   if we're writing it to a specified location
            self.keep_archive = False
        if self.compressor not in constants.valid_compressors:
            # set default compressor if an invalid one is supplied
            if self._print_errors:
                sys.stdout.write('The compressor {0} is not supported. Using default: gz\n'.format(self.compressor))
            self.compressor = 'gz'
        if self.output_dir:
            # get full path
            self.output_dir = os.path.abspath(self.output_dir)
        if self.output_file:
            # get full path
            self.output_file = os.path.abspath(self.output_file)
            self._determine_filename_and_extension()

    def _determine_filename_and_extension(self):
        '''
        Attempt to automatically determine compressor
        and filename for --output-file based on the given config.
        '''
        def _tar_ext(comp):
            '''
            Helper function to generate .tar file extension
            '''
            ext = '' if comp == 'none' else '.%s' % comp
            return '.tar' + ext

        # make sure we're not attempting to write an existing directory first
        if os.path.isdir(self.output_file):
            raise ValueError('%s is a directory.' % self.output_file)

        # attempt to determine compressor from filename
        for x in constants.valid_compressors:
            if self.output_file.endswith(_tar_ext(x)):
                if self.compressor != x:
                    if self._print_errors:
                        sys.stdout.write('The given output file {0} does not match the given compressor {1}. '
                                         'Setting compressor to match the file extension.\n'.format(self.output_file, self.compressor))
                self.compressor = x
                return

        # if we don't return from the loop, we could
        #   not determine compressor from filename, so
        #   set the filename from the given
        #   compressor
        self.output_file = self.output_file + _tar_ext(self.compressor)


if __name__ == '__main__':
    config = InsightsConfig(_print_errors=True)
    config.load_all()
    print(config)
