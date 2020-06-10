"""
Rules for data collection
"""
from __future__ import absolute_import
import logging
import six
import os
import yaml
import stat
import pkgutil
import json
import insights
from six.moves import configparser as ConfigParser

from .constants import InsightsConstants as constants
from collections import defaultdict
from insights import datasource, dr, parse_plugins, load_packages
from insights.core import spec_factory as sf
# from insights.specs.default import DefaultSpecs

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
NETWORK = constants.custom_network_log_level


def resolve(d):
    """
    Categorizes a datasource's command, path, or template information.
    The categorization ignores first_of, head, and find since they depend on other
    datasources that will get resolved anyway. Ignore the listdir helper and explicit
    @datasource functions since they're pure python.
    """
    if isinstance(d, sf.simple_file):
        return ("file_static", [d.path])

    if isinstance(d, sf.first_file):
        return ("file_static", d.paths)

    if isinstance(d, sf.glob_file):
        return ("file_glob", d.patterns)

    if isinstance(d, sf.foreach_collect):
        return ("file_template", [d.path])

    if isinstance(d, sf.simple_command):
        return ("command_static", [d.cmd])

    if isinstance(d, sf.command_with_args):
        return ("command_template", [d.cmd])

    if isinstance(d, sf.foreach_execute):
        return ("command_template", [d.cmd])

    return (None, None)


def categorize(ds):
    """
    Extracts commands, paths, and templates from datasources and cateorizes them
    based on their type.
    """
    results = defaultdict(set)
    for d in ds:
        (cat, res) = resolve(d)
        if cat is not None:
            results[cat] |= set(res)
    return dict((k, sorted(v)) for k, v in results.items())


def get_spec_report():
    """
    You'll need to already have the specs loaded, and then you can call this
    procedure to get a categorized dict of the commands we might run and files
    we might collect.
    """
    load("insights.specs.default")
    ds = dr.get_components_of_type(datasource)
    return categorize(ds)


def load(p):
    plugins = parse_plugins(p)
    load_packages(plugins)


def correct_format(parsed_data, expected_keys, filename):
    '''
    Ensure the parsed file matches the needed format
    Returns True, <message> on error
    Returns False, None on success
    '''
    # validate keys are what we expect
    def is_list_of_strings(data):
        '''
        Helper function for correct_format()
        '''
        if data is None:
            # nonetype, no data to parse. treat as empty list
            return True
        if not isinstance(data, list):
            return False
        for l in data:
            if not isinstance(l, six.string_types):
                return False
        return True

    keys = parsed_data.keys()
    invalid_keys = set(keys).difference(expected_keys)
    if invalid_keys:
        return True, ('Unknown section(s) in %s: ' % filename + ', '.join(invalid_keys) +
                      '\nValid sections are ' + ', '.join(expected_keys) + '.')

    # validate format (lists of strings)
    for k in expected_keys:
        if k in parsed_data:
            if k == 'patterns' and isinstance(parsed_data['patterns'], dict):
                if 'regex' not in parsed_data['patterns']:
                    return True, 'Patterns section contains an object but the "regex" key was not specified.'
                if 'regex' in parsed_data['patterns'] and len(parsed_data['patterns']) > 1:
                    return True, 'Unknown keys in the patterns section. Only "regex" is valid.'
                if not is_list_of_strings(parsed_data['patterns']['regex']):
                    return True, 'regex section under patterns must be a list of strings.'
                continue
            if not is_list_of_strings(parsed_data[k]):
                return True, '%s section must be a list of strings.' % k
    return False, None


def load_yaml(filename):
    try:
        with open(filename) as f:
            loaded_yaml = yaml.safe_load(f)
        if loaded_yaml is None:
            logger.debug('%s is empty.', filename)
            return {}
    except (yaml.YAMLError, yaml.parser.ParserError) as e:
        # can't parse yaml from conf
        raise RuntimeError('ERROR: Cannot parse %s.\n'
                           'If using any YAML tokens such as [] in an expression, '
                           'be sure to wrap the expression in quotation marks.\n\nError details:\n%s\n' % (filename, e))
    if not isinstance(loaded_yaml, dict):
        # loaded data should be a dict with at least one key
        raise RuntimeError('ERROR: Invalid YAML loaded.')
    return loaded_yaml


def verify_permissions(f):
    '''
    Verify 600 permissions on a file
    '''
    mode = stat.S_IMODE(os.stat(f).st_mode)
    if not mode == 0o600:
        raise RuntimeError("Invalid permissions on %s. "
                           "Expected 0600 got %s" % (f, oct(mode)))
    logger.debug("Correct file permissions on %s", f)


class InsightsUploadConf(object):
    """
    Insights spec configuration from uploader.json
    Now only loads remove.conf, consider renaming/refactor
    """

    def __init__(self, config, conn=None):
        """
        Load config from parent
        """
        self.config = config
        self.remove_file = config.remove_file
        self.redaction_file = config.redaction_file
        self.content_redaction_file = config.content_redaction_file
        self.tags_file = config.tags_file

        # set rm_conf as a class attribute so we can observe it
        #   in create_report
        self.rm_conf = None

        # attribute to set when using file-redaction.yaml instead of
        #   remove.conf, for reporting purposes. True by default
        #   since new format is favored.
        self.using_new_format = True

    def get_rm_conf_old(self):
        """
        Get excluded files config from remove_file.
        """
        # Convert config object into dict
        self.using_new_format = False
        parsedconfig = ConfigParser.RawConfigParser()
        if not self.remove_file:
            # no filename defined, return nothing
            logger.debug('remove_file is undefined')
            return None
        if not os.path.isfile(self.remove_file):
            logger.debug('%s not found. No data files, commands,'
                         ' or patterns will be ignored, and no keyword obfuscation will occur.', self.remove_file)
            return None
        try:
            verify_permissions(self.remove_file)
        except RuntimeError as e:
            if self.config.validate:
                # exit if permissions invalid and using --validate
                raise RuntimeError('ERROR: %s' % e)
            logger.warning('WARNING: %s', e)
        try:
            parsedconfig.read(self.remove_file)
            sections = parsedconfig.sections()

            if not sections:
                # file has no sections, skip it
                logger.debug('Remove.conf exists but no parameters have been defined.')
                return None

            if sections != ['remove']:
                raise RuntimeError('ERROR: invalid section(s) in remove.conf. Only "remove" is valid.')

            expected_keys = ('commands', 'files', 'patterns', 'keywords')
            rm_conf = {}
            for item, value in parsedconfig.items('remove'):
                if item not in expected_keys:
                    raise RuntimeError('ERROR: Unknown key in remove.conf: ' + item +
                                       '\nValid keys are ' + ', '.join(expected_keys) + '.')
                if six.PY3:
                    rm_conf[item] = [v.strip() for v in value.strip().encode('utf-8').decode('unicode-escape').split(',')]
                else:
                    rm_conf[item] = [v.strip() for v in value.strip().decode('string-escape').split(',')]
            self.rm_conf = rm_conf
        except ConfigParser.Error as e:
            # can't parse config file at all
            logger.debug(e)
            logger.debug('To configure using YAML, please use file-redaction.yaml and file-content-redaction.yaml.')
            raise RuntimeError('ERROR: Cannot parse the remove.conf file.\n'
                               'See %s for more information.' % self.config.logging_file)
        logger.warning('WARNING: remove.conf is deprecated. Please use file-redaction.yaml and file-content-redaction.yaml. See https://access.redhat.com/articles/4511681 for details.')
        return self.rm_conf

    def load_redaction_file(self, fname):
        '''
        Load the YAML-style file-redaction.yaml
            or file-content-redaction.yaml files
        '''
        if fname not in (self.redaction_file, self.content_redaction_file):
            # invalid function use, should never get here in a production situation
            return None
        if not fname:
            # no filename defined, return nothing
            logger.debug('redaction_file or content_redaction_file is undefined')
            return None
        if not fname or not os.path.isfile(fname):
            if fname == self.redaction_file:
                logger.debug('%s not found. No files or commands will be skipped.', self.redaction_file)
            elif fname == self.content_redaction_file:
                logger.debug('%s not found. '
                             'No patterns will be skipped and no keyword obfuscation will occur.', self.content_redaction_file)
            return None
        try:
            verify_permissions(fname)
        except RuntimeError as e:
            if self.config.validate:
                # exit if permissions invalid and using --validate
                raise RuntimeError('ERROR: %s' % e)
            logger.warning('WARNING: %s', e)
        loaded = load_yaml(fname)
        if fname == self.redaction_file:
            err, msg = correct_format(loaded, ('commands', 'files', 'components'), fname)
        elif fname == self.content_redaction_file:
            err, msg = correct_format(loaded, ('patterns', 'keywords'), fname)
        if err:
            # YAML is correct but doesn't match the format we need
            raise RuntimeError('ERROR: ' + msg)
        return loaded

    def get_rm_conf(self):
        '''
        Try to load the the "new" version of
        remove.conf (file-redaction.yaml and file-redaction.yaml)
        '''
        rm_conf = {}
        redact_conf = self.load_redaction_file(self.redaction_file)
        content_redact_conf = self.load_redaction_file(self.content_redaction_file)

        if redact_conf:
            rm_conf.update(redact_conf)
        if content_redact_conf:
            rm_conf.update(content_redact_conf)

        if not redact_conf and not content_redact_conf:
            # no file-redaction.yaml or file-content-redaction.yaml defined,
            #   try to use remove.conf
            self.get_rm_conf_old()
            self.map_rm_conf_classic_to_core()
            return self.rm_conf

        # remove Nones, empty strings, and empty lists
        filtered_rm_conf = dict((k, v) for k, v in rm_conf.items() if v)
        self.rm_conf = filtered_rm_conf
        self.map_rm_conf_classic_to_core()
        return self.rm_conf

    def get_tags_conf(self):
        '''
        Try to load the tags.conf file
        '''
        if not os.path.isfile(self.tags_file):
            logger.info("%s does not exist", self.tags_file)
            return None
        else:
            try:
                load_yaml(self.tags_file)
                logger.info("%s loaded successfully", self.tags_file)
            except RuntimeError:
                logger.warning("Invalid YAML. Unable to load %s", self.tags_file)
                return None

    def validate(self):
        '''
        Validate remove.conf and tags.conf
        '''
        self.get_tags_conf()
        logger.info('Commands and files specified in blacklist configuration will be automatically mapped to insights-core components if possible.')
        success = self.get_rm_conf()
        if not success:
            logger.info('No contents in the blacklist configuration to validate.')
            return None
        # Using print here as this could contain sensitive information
        print('Blacklist configuration parsed contents:')
        print(json.dumps(success, indent=4))
        logger.info('Parsed successfully.')
        return True

    def create_report(self):
        def length(lst):
            '''
            Because of how the INI remove.conf is parsed,
            an empty value in the conf will produce
            the value [''] when parsed. Do not include
            these in the report
            '''
            if len(lst) == 1 and lst[0] == '':
                return 0
            return len(lst)

        num_commands = 0
        num_files = 0
        num_components = 0
        num_patterns = 0
        num_keywords = 0
        using_regex = False

        if self.rm_conf:
            for key in self.rm_conf:
                if key == 'commands':
                    num_commands = length(self.rm_conf['commands'])
                if key == 'files':
                    num_files = length(self.rm_conf['files'])
                if key == 'components':
                    num_components = length(self.rm_conf['components'])
                if key == 'patterns':
                    if isinstance(self.rm_conf['patterns'], dict):
                        num_patterns = length(self.rm_conf['patterns']['regex'])
                        using_regex = True
                    else:
                        num_patterns = length(self.rm_conf['patterns'])
                if key == 'keywords':
                    num_keywords = length(self.rm_conf['keywords'])

        return {
            'obfuscate': self.config.obfuscate,
            'obfuscate_hostname': self.config.obfuscate_hostname,
            'commands': num_commands,
            'files': num_files,
            'components': num_components,
            'patterns': num_patterns,
            'keywords': num_keywords,
            'using_new_format': self.using_new_format,
            'using_patterns_regex': using_regex
        }

    def map_rm_conf_classic_to_core(self):
        '''
        In order to maximize compatibility between "classic" remove.conf
        configurations and core collection, do the following mapping
        strategy:

        1. If remove.conf entry matches a symbolic name, disable the
            corresponding core component.
        2. If remove.conf entry is a raw command or file, do a reverse
            lookup on the symbolic name based on stored uploader.json data,
            then continue as in step 1.
        3. If neither conditions 1 or 2 are matched it is either
            a) a mistyped command/file, or
            b) an arbitrary file.

            For (a), classic remove.conf configs require an exact match to
                uploader.json. We can carry that condition into our
                compatibility with core.
            For (b), classic collection had the ability to skip arbitrary
                files based on filepaths in uploader.json post-expansion
                (i.e. a specific repo file in /etc/yum.repos.d).
                Core checks all files collected against the file
                blacklist filters, so these files will be omitted
                just by the nature of core collection.
        '''
        updated_commands = []
        updated_files = []
        updated_components = []
        # core_specs = vars(DefaultSpecs).keys()

        uploader_json_file = pkgutil.get_data(insights.__name__, "uploader_json_map.json")
        uploader_json = json.loads(uploader_json_file)

        if not self.rm_conf:
            return

        logger.warning("If possible, commands and files specified in the blacklist configuration will be converted to Insights component specs that will be disabled as needed.")

        # save matches to a dict for informative logging
        cmds_files_names_map = {}
        longest_key = 0

        # loop
        #   match command/symbol with symbolic name
        #   get component from symbolic name
        #   add component to components blacklist (with prefix)
        #   add command and result (without prefix) to map for logging at the end

        def _get_component_by_symbolic_name(sname):
            # match a component to a symbolic name
            # some symbolic names need to be renamed to fit specs
            spec_prefix = "insights.specs.default.DefaultSpecs."
            spec_conversion = {
                'getconf_pagesize': 'getconf_page_size',
                'lspci_kernel': 'lspci',
                'netstat__agn': 'netstat_agn',
                'rpm__V_packages': 'rpm_V_packages',
                'ss_tupna': 'ss',
                'systemd_analyze_blame': None,

                'machine_id1': 'machine_id',
                'machine_id2': 'machine_id',
                'machine_id3': 'machine_id',
                'grub2_efi_grubenv': None,
                'grub2_grubenv': None,
                'limits_d': 'limits_conf',
                'modprobe_conf': 'modprobe',
                'modprobe_d': 'modprobe',
                'ps_auxwww': 'insights.specs.sos_archive.SosSpecs.ps_auxww',  # special case
                'rh_mongodb26_conf': 'mongod_conf',
                'sysconfig_rh_mongodb26': 'sysconfig_mongod',
                'redhat_access_proactive_log': None,

                'krb5_conf_d': 'krb5'
            }

            if sname in spec_conversion:
                if sname == 'ps_auxwww':
                    return spec_conversion[sname]
                return spec_prefix + spec_conversion[sname]
            return spec_prefix + sname

        for c in self.rm_conf.get('commands', []):
            matched = False
            for spec in uploader_json['commands']:
                if c == spec['symbolic_name'] or c == spec['command']:
                    # matches to a symbolic name or raw command, cache the symbolic name
                    sname = spec['symbolic_name']
                    if not six.PY3:
                        sname = sname.encode('utf-8')
                    component = _get_component_by_symbolic_name(sname)
                    cmds_files_names_map[c] = component
                    if len(c) > longest_key:
                        longest_key = len(c)
                    updated_components.append(component)
                    matched = True
                    break
            if not matched:
                # could not match the command to anything, keep in config as-is
                updated_commands.append(c)

        for f in self.rm_conf.get('files', []):
            matched = False
            for spec in uploader_json['files']:
                if f == spec['symbolic_name'] or f == spec['file']:
                    # matches to a symbolic name or raw command, cache the symbolic name
                    sname = spec['symbolic_name']
                    if not six.PY3:
                        sname = sname.encode('utf-8')
                    component = _get_component_by_symbolic_name(sname)
                    cmds_files_names_map[c] = component
                    if len(c) > longest_key:
                        longest_key = len(c)
                    updated_components.append(component)
                    matched = True
                    break
            for spec in uploader_json['globs']:
                if f == spec['symbolic_name']:
                    # matches only to a symbolic name for globs
                    sname = spec['symbolic_name']
                    if not six.PY3:
                        sname = sname.encode('utf-8')
                    component = _get_component_by_symbolic_name(sname)
                    cmds_files_names_map[c] = component
                    if len(c) > longest_key:
                        longest_key = len(c)
                    updated_components.append(component)
                    matched = True
                    break
            if not matched:
                # could not match the file to anything, keep in config as-is
                updated_files.append(f)

        for n in cmds_files_names_map:
            spec_name_no_prefix = cmds_files_names_map[n].rsplit('.', 1)[-1]
            logger.warning('{0:{1}}\t=> {2}'.format(n, longest_key, spec_name_no_prefix))

        updated_components = list(dict.fromkeys(updated_components))

        self.rm_conf['commands'] = updated_commands
        self.rm_conf['files'] = updated_files
        self.rm_conf['components'] = updated_components

        return self.rm_conf


if __name__ == '__main__':
    from .config import InsightsConfig
    config = InsightsConfig().load_all()
    uploadconf = InsightsUploadConf(config)
    # uploadconf.get_rm_conf()
    # uploadconf.map_rm_conf_classic_to_core()
    uploadconf.validate()
    # report = uploadconf.create_report()

    # print(report)
