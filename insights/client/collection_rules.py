"""
Rules for data collection
"""
from __future__ import absolute_import
import hashlib
import json
import logging
import six
import shlex
import os
import requests
import yaml
import stat
from six.moves import configparser as ConfigParser

from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from .constants import InsightsConstants as constants
from .map_components import map_rm_conf_to_components

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
NETWORK = constants.custom_network_log_level


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
    """

    def __init__(self, config, conn=None):
        """
        Load config from parent
        """
        self.config = config
        self.fallback_file = constants.collection_fallback_file
        self.remove_file = config.remove_file
        self.redaction_file = config.redaction_file
        self.content_redaction_file = config.content_redaction_file
        self.tags_file = config.tags_file
        self.collection_rules_file = constants.collection_rules_file
        self.collection_rules_url = self.config.collection_rules_url
        self.gpg = self.config.gpg

        # initialize an attribute to store the content of uploader.json
        #   once it is loaded and verified
        self.uploader_json = None

        # set rm_conf as a class attribute so we can observe it
        #   in create_report
        self.rm_conf = None

        # attribute to set when using file-redaction.yaml instead of
        #   remove.conf, for reporting purposes. True by default
        #   since new format is favored.
        self.using_new_format = True

        if conn:
            if self.collection_rules_url is None:
                if config.legacy_upload:
                    self.collection_rules_url = conn.base_url + '/v1/static/uploader.v2.json'
                else:
                    self.collection_rules_url = conn.base_url.split('/platform')[0] + '/v1/static/uploader.v2.json'
            self.conn = conn

    def validate_gpg_sig(self, path, sig=None):
        """
        Validate the collection rules
        """
        logger.debug("Verifying GPG signature of Insights configuration")
        if sig is None:
            sig = path + ".asc"
        command = ("/usr/bin/gpg --no-default-keyring "
                   "--keyring " + constants.pub_gpg_path +
                   " --verify " + sig + " " + path)
        if not six.PY3:
            command = command.encode('utf-8', 'ignore')
        args = shlex.split(command)
        logger.debug("Executing: %s", args)
        proc = Popen(
            args, shell=False, stdout=PIPE, stderr=STDOUT, close_fds=True)
        stdout, stderr = proc.communicate()
        logger.debug("STDOUT: %s", stdout)
        logger.debug("STDERR: %s", stderr)
        logger.debug("Status: %s", proc.returncode)
        if proc.returncode:
            logger.error("ERROR: Unable to validate GPG signature: %s", path)
            return False
        else:
            logger.debug("GPG signature verified")
            return True

    def try_disk(self, path, gpg=True):
        """
        Try to load json off disk
        """
        if not os.path.isfile(path):
            return

        if not gpg or self.validate_gpg_sig(path):
            stream = open(path, 'r')
            json_stream = stream.read()
            if len(json_stream):
                try:
                    json_config = json.loads(json_stream)
                    return json_config
                except ValueError:
                    logger.error("ERROR: Invalid JSON in %s", path)
                    return False
            else:
                logger.warn("WARNING: %s was an empty file", path)
                return

    def get_collection_rules(self, raw=False):
        """
        Download the collection rules
        """
        logger.debug("Attemping to download collection rules from %s",
                     self.collection_rules_url)

        try:
            req = self.conn.get(
                self.collection_rules_url, headers=({'accept': 'text/plain'}))

            if req.status_code == 200:
                logger.debug("Successfully downloaded collection rules")

                json_response = NamedTemporaryFile()
                json_response.write(req.text.encode('utf-8'))
                json_response.file.flush()
            else:
                logger.error("ERROR: Could not download dynamic configuration")
                logger.error("Debug Info: \nConf status: %s", req.status_code)
                logger.error("Debug Info: \nConf message: %s", req.text)
                return None
        except requests.ConnectionError as e:
            logger.error(
                "ERROR: Could not download dynamic configuration: %s", e)
            return None

        if self.gpg:
            self.get_collection_rules_gpg(json_response)

        self.write_collection_data(self.collection_rules_file, req.text)

        if raw:
            return req.text
        else:
            return json.loads(req.text)

    def fetch_gpg(self):
        logger.debug("Attemping to download collection "
                     "rules GPG signature from %s",
                     self.collection_rules_url + ".asc")

        headers = ({'accept': 'text/plain'})
        config_sig = self.conn.get(self.collection_rules_url + '.asc',
                                   headers=headers)
        if config_sig.status_code == 200:
            logger.debug("Successfully downloaded GPG signature")
            return config_sig.text
        else:
            logger.error("ERROR: Download of GPG Signature failed!")
            logger.error("Sig status: %s", config_sig.status_code)
            return False

    def get_collection_rules_gpg(self, collection_rules):
        """
        Download the collection rules gpg signature
        """
        sig_text = self.fetch_gpg()
        sig_response = NamedTemporaryFile(suffix=".asc")
        sig_response.write(sig_text.encode('utf-8'))
        sig_response.file.flush()
        self.validate_gpg_sig(collection_rules.name, sig_response.name)
        self.write_collection_data(self.collection_rules_file + ".asc", sig_text)

    def write_collection_data(self, path, data):
        """
        Write collections rules to disk
        """
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, 'w') as dyn_conf_file:
            dyn_conf_file.write(data)

    def get_conf_file(self):
        """
        Get config from local config file, first try cache, then fallback.
        """
        if self.uploader_json:
            return self.uploader_json

        for conf_file in [self.collection_rules_file, self.fallback_file]:
            logger.debug("trying to read conf from: " + conf_file)
            conf = self.try_disk(conf_file, self.gpg)

            if not conf:
                continue

            version = conf.get('version', None)
            if version is None:
                raise ValueError("ERROR: Could not find version in json")

            conf['file'] = conf_file
            logger.debug("Success reading config")
            logger.debug(json.dumps(conf))
            self.uploader_json = conf
            return conf

        raise RuntimeError("ERROR: Unable to download conf or read it from disk!")

    def get_conf_update(self):
        """
        Get updated config from URL.
        """
        dyn_conf = self.get_collection_rules()

        if not dyn_conf:
            return self.get_conf_file()

        version = dyn_conf.get('version', None)
        if version is None:
            raise ValueError("ERROR: Could not find version in json")

        dyn_conf['file'] = self.collection_rules_file
        logger.debug("Success reading config")
        config_hash = hashlib.sha1(json.dumps(dyn_conf).encode('utf-8')).hexdigest()
        logger.debug('sha1 of config: %s', config_hash)
        return dyn_conf

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
            self.rm_conf = self.get_rm_conf_old()
            if self.config.core_collect:
                self.rm_conf = map_rm_conf_to_components(self.rm_conf, self.get_conf_file())
            return self.rm_conf

        # remove Nones, empty strings, and empty lists
        filtered_rm_conf = dict((k, v) for k, v in rm_conf.items() if v)
        self.rm_conf = filtered_rm_conf
        if self.config.core_collect:
            self.rm_conf = map_rm_conf_to_components(self.rm_conf, self.get_conf_file())
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
