from __future__ import absolute_import
import os
import logging
import argparse
import copy
import six
import sys
from six.moves import configparser as ConfigParser
from distutils.version import LooseVersion
from .utilities import get_version_info
from insights.client.apps.manifests import manifests, content_types

try:
    from .constants import InsightsConstants as constants
except:
    from constants import InsightsConstants as constants

logger = logging.getLogger(__name__)


def _core_collect_default():
    '''
    Core collection should be disabled by default, unless
    the RPM version 3.1 or above
    '''
    rpm_version = get_version_info()['client_version']
    if not rpm_version:
        # problem getting the version, default to False
        return False
    if LooseVersion(rpm_version) < LooseVersion(constants.core_collect_rpm_version):
        # rpm version is older than the core collection release
        return False
    else:
        # rpm version is equal to or newer than the core collection release
        return True


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
    'ansible_host': {
        'default': None,
        'opt': ['--ansible-host'],
        'help': 'Set an Ansible hostname for this system. ',
        'action': 'store'
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
        'help': argparse.SUPPRESS,
        'action': "store_true",
        'group': 'actions'
    },
    'checkin': {
        'default': False,
        'opt': ['--checkin'],
        'help': 'Do a lightweight check-in instead of full upload',
        'action': "store_true",
        'group': 'actions'
    },
    'cmd_timeout': {
        # non-CLI
        'default': constants.default_cmd_timeout
    },
    'collection_rules_url': {
        # non-CLI
        'default': None
    },
    'app': {
        'default': None,
        'opt': ['--collector'],
        'help': 'Run the specified app and upload its results archive',
        'action': 'store',
        'group': 'actions',
        'dest': 'app'
    },
    'manifest': {
        'default': None,
        'opt': ['--manifest'],
        'help': 'Collect using the provided manifest',
        'action': 'store',
        'group': 'actions',
        'dest': 'manifest'
    },
    'build_packagecache': {
        'default': False,
        'opt': ['--build-packagecache'],
        'help': 'Refresh the system package manager cache',
        'action': 'store_true',
        'group': 'actions'
    },
    'compliance': {
        'default': False,
        'opt': ['--compliance'],
        'help': 'Scan the system using openscap and upload the report',
        'action': 'store_true',
        'group': 'actions'
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
    'core_collect': {
        'default': False
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
        'action': 'store_true',
        'group': 'actions'
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
        'group': 'actions'
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
    'force': {
        'default': False,
        'opt': ['--force'],
        'help': argparse.SUPPRESS,
        'action': 'store_true'
    },
    'group': {
        'default': None,
        'opt': ['--group'],
        'help': 'Group to add to this system',
        'action': 'store',
    },
    'http_timeout': {
        # non-CLI
        'default': 120.0
    },
    'keep_archive': {
        'default': False,
        'opt': ['--keep-archive'],
        'help': 'Store archive in /var/cache/insights-client/ after upload',
        'action': 'store_true',
        'group': 'debug'
    },
    'list_specs': {
        'default': False,
        'opt': ['--list-specs'],
        'help': 'Show insights-client collection specs',
        'action': 'store_true',
        'group': 'actions'
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
    'no_proxy': {
        # non-CLI
        'default': None
    },
    'no_upload': {
        'default': False,
        'opt': ['--no-upload'],
        'help': 'Do not upload the archive',
        'action': 'store_true',
        'group': 'debug'
    },
    'module': {
        'default': None,
        'opt': ['--module', '-m'],
        'help': argparse.SUPPRESS,
        'action': 'store'
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
        'action': 'store_true',
        'group': 'actions',
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
        'help': ('This flag is deprecated and it will be removed in a future release.'
                 'Forcefully reregister this machine to Red Hat.'
                 'Please use `insights-client --unregister && insights-client --register `instead'),
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
        'action': "store_true",
        'group': 'actions'
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
        'action': 'store_true',
        'group': 'debug'
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
        'action': 'store_true',
        'group': 'actions'
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
        'help': 'Validate remove.conf and tags.yaml',
        'action': 'store_true',
        'group': 'actions'
    },
    'verbose': {
        'default': False,
        'opt': ['--verbose'],
        'help': "DEBUG output to stdout",
        'action': "store_true"
    },
    'version': {
        'default': False,
        'opt': ['--version'],
        'help': "Display version",
        'action': "store_true"
    },
    'legacy_upload': {
        # True: upload to insights classic API
        # False: upload to insights platform API
        'default': True
    },
    'payload': {
        'default': None,
        'opt': ['--payload'],
        'help': 'Use the Insights Client to upload an archive',
        'action': 'store',
        'group': 'actions'
    },
    'content_type': {
        'default': None,
        'opt': ['--content-type'],
        'help': 'Content type of the archive specified with --payload',
        'action': 'store'
    },
    'diagnosis': {
        'default': None,
        'opt': ['--diagnosis'],
        'help': 'Retrieve a diagnosis for this system',
        'const': True,
        'nargs': '?',
        'group': 'actions'
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

        # initialize the real default for core_collect here
        #   instead of inside DEFAULT_KVS because calling
        #   this function at the module scope ignores unit test mocks
        self.core_collect = _core_collect_default()

        if args:
            self._update_dict(args[0])
        self._update_dict(kwargs)
        self._cli_opts = None
        self._imply_options()
        self._validate_options()

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
        if os.environ.get('HTTP_PROXY') and not os.environ.get('HTTPS_PROXY') and self._print_errors:
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
        arg_groups = {
            "actions": parser.add_argument_group("actions"),
            "debug": parser.add_argument_group("optional debug arguments")
        }
        cli_options = dict((k, v) for k, v in DEFAULT_OPTS.items() if (
                       'opt' in v))
        for _, _o in cli_options.items():
            # cli_options contains references to DEFAULT_OPTS, so
            #   make a copy so we don't mutate DEFAULT_OPTS
            o = copy.copy(_o)
            group_name = o.pop('group', None)
            if group_name is None:
                group = parser
            else:
                group = arg_groups[group_name]
            optnames = o.pop('opt')
            # use argparse.SUPPRESS as CLI defaults so it won't parse
            #  options that weren't specified
            o['default'] = argparse.SUPPRESS
            group.add_argument(*optnames, **o)

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
        if self.reregister:
            raise ValueError(
                "`force-reregistration` has been deprecated. Please use `insights-client "
                "--unregister && insights-client --register` instead",
            )
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
            if self.checkin:
                raise ValueError('Cannot check-in in offline mode.')
            if self.unregister:
                raise ValueError('Cannot unregister in offline mode.')
            if self.check_results:
                raise ValueError('Cannot check results in offline mode')
            if self.diagnosis:
                raise ValueError('Cannot diagnosis in offline mode')
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
        if self.module and not self.module.startswith('insights.client.apps.'):
            raise ValueError('You can only run modules within the namespace insights.client.apps.*')
        if self.app and not self.manifest:
            raise ValueError("Unable to find app: %s\nList of available apps: %s"
                             % (self.app, ', '.join(sorted(manifests.keys()))))

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
        self.register = self.register and not self.offline
        self.keep_archive = self.keep_archive or self.no_upload
        if self.to_json and self.quiet:
            self.diagnosis = True
        if self.test_connection:
            self.net_debug = True
        if self.payload or self.diagnosis or self.compliance or self.check_results or self.checkin:
            self.legacy_upload = False
        if self.payload and (self.logging_file == constants.default_log_file):
            self.logging_file = constants.default_payload_log
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
        if self.app:
            # Get the manifest for the specified app
            self.manifest = manifests.get(self.app)
            self.content_type = content_types.get(self.app)
            self.core_collect = True
            self.legacy_upload = False
            self._set_app_config()
        if self.output_dir:
            # get full path
            self.output_dir = os.path.abspath(self.output_dir)
        if self.output_file:
            # get full path
            self.output_file = os.path.abspath(self.output_file)
            self._determine_filename_and_extension()
        if self._cli_opts and "ansible_host" in self._cli_opts and not self.register:
            # Specific use case, explained here:
            #
            #   Ansible hostname is, more or less, a second display name.
            #   However, there is no method in the legacy API to handle
            #   changes to the ansible hostname. So, if a user specifies
            #   --ansible-hostname on the CLI to change it like they would
            #   --display-name, in order to actually change it, we need to
            #   force disable legacy_upload to make the proper HTTP requests.
            #
            #   As of now, registration still needs to be tied to the legacy
            #   API, so if the user has legacy upload enabled (the default),
            #   we can't force disable it when registering. Thus, if
            #   specifying --ansible-hostname alongside --register, all the
            #   necessary legacy API calls will still be made, the
            #   ansible-hostname will be packed into the archive, and the
            #   rest will be handled by ingress. Incidentally, if legacy
            #   upload *is* disabled, the ansible hostname will also be
            #   included in the upload metadata.
            #
            #   The reason to explicitly look for ansible_host in the CLI
            #   parameters *only* is because, due to a customer request from
            #   long ago, a display_name specified in the config file should
            #   be applied as part of the upload, and conversely, specifying
            #   it on the command line (WITHOUT --register) should be a
            #   "once and done" option that does a single HTTP call to modify
            #   it. We are going to mimic that behavior with the Ansible
            #   hostname.
            #
            #   Therefore, only force legacy_upload to False when attempting
            #   to change Ansible hostname from the CLI, when not registering.
            self.legacy_upload = False

    def _set_app_config(self):
        '''
        Set App specific insights config values that differ from the default values
        Config values may have been set manually however, so need to take that into consideration
        '''
        if self.app == 'malware-detection':
            # Add extra retries for malware, mainly because it could take a long time to run
            # and the results archive shouldn't be discarded after a single failed upload attempt
            if self.retries < 3:
                self.retries = 3

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
