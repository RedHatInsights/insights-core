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

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')

expected_keys = ('commands', 'files', 'patterns', 'keywords')


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
        self.collection_rules_file = constants.collection_rules_file
        self.collection_rules_url = self.config.collection_rules_url
        self.gpg = self.config.gpg
        if conn:
            if self.collection_rules_url is None:
                if config.legacy_upload:
                    self.collection_rules_url = conn.base_url + '/v1/static/uploader.v2.json'
                else:
                    self.collection_rules_url = conn.base_url.split('/platform')[0] + '/v1/static/uploader.v2.json'
                    # self.collection_rules_url = conn.base_url + '/static/uploader.v2.json'
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

        net_logger.info("GET %s", self.collection_rules_url)
        try:
            req = self.conn.session.get(
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
        net_logger.info("GET %s", self.collection_rules_url + '.asc')
        config_sig = self.conn.session.get(self.collection_rules_url + '.asc',
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
            return conf

        raise ValueError("ERROR: Unable to download conf or read it from disk!")

    def get_conf_update(self):
        """
        Get updated config from URL, fallback to local file if download fails.
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
        logger.debug('Trying to parse as INI file.')
        parsedconfig = ConfigParser.RawConfigParser()

        try:
            parsedconfig.read(self.remove_file)
            rm_conf = {}
            for item, value in parsedconfig.items('remove'):
                if item not in expected_keys:
                    raise RuntimeError('Unknown section in remove.conf: ' + item +
                                       '\nValid sections are ' + ', '.join(expected_keys) + '.')
                if six.PY3:
                    rm_conf[item] = value.strip().encode('utf-8').decode('unicode-escape').split(',')
                else:
                    rm_conf[item] = value.strip().decode('string-escape').split(',')
            return rm_conf
        except ConfigParser.Error as e:
            # can't parse config file at all
            logger.debug(e)
            raise RuntimeError('ERROR: Cannot parse the remove.conf file as a YAML file '
                               'nor as an INI file. Please check the file formatting.\n'
                               'See %s for more information.' % self.config.logging_file)

    def get_rm_conf(self):
        '''
        Load remove conf. If it's a YAML-formatted file, try to load
        the "new" version of remove.conf
        '''
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

        def correct_format(parsed_data):
            '''
            Ensure the parsed file matches the needed format
            Returns True, <message> on error
            '''
            # validate keys are what we expect
            keys = parsed_data.keys()
            invalid_keys = set(keys).difference(expected_keys)
            if invalid_keys:
                return True, ('Unknown section(s) in remove.conf: ' + ', '.join(invalid_keys) +
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

        if not os.path.isfile(self.remove_file):
            logger.debug('No remove.conf defined. No files/commands will be ignored.')
            return None
        try:
            with open(self.remove_file) as f:
                rm_conf = yaml.safe_load(f)
            if rm_conf is None:
                logger.warn('WARNING: Remove file %s is empty.', self.remove_file)
                return {}
        except (yaml.YAMLError, yaml.parser.ParserError) as e:
            # can't parse yaml from conf, try old style
            logger.debug('ERROR: Cannot parse remove.conf as a YAML file.\n'
                         'If using any YAML tokens such as [] in an expression, '
                         'be sure to wrap the expression in quotation marks.\n\nError details:\n%s\n', e)
            return self.get_rm_conf_old()
        if not isinstance(rm_conf, dict):
            # loaded data should be a dict with at least one key (commands, files, patterns, keywords)
            logger.debug('ERROR: Invalid YAML loaded.')
            return self.get_rm_conf_old()
        err, msg = correct_format(rm_conf)
        if err:
            # YAML is correct but doesn't match the format we need
            raise RuntimeError('ERROR: ' + msg)
        # remove Nones, empty strings, and empty lists
        filtered_rm_conf = dict((k, v) for k, v in rm_conf.items() if v)
        return filtered_rm_conf

    def validate(self):
        '''
        Validate remove.conf
        '''
        if not os.path.isfile(self.remove_file):
            logger.warn("WARNING: Remove file does not exist")
            return False
        # Make sure permissions are 600
        mode = stat.S_IMODE(os.stat(self.remove_file).st_mode)
        if not mode == 0o600:
            logger.error("ERROR: Invalid remove file permissions. "
                         "Expected 0600 got %s" % oct(mode))
            return False
        else:
            logger.debug("Correct file permissions")
        success = self.get_rm_conf()
        if success is None or success is False:
            logger.error('Could not parse remove.conf')
            return False
        # Using print here as this could contain sensitive information
        print('Remove file parsed contents:')
        print(success)
        logger.info('Parsed successfully.')
        return True


if __name__ == '__main__':
    from .config import InsightsConfig
    print(InsightsUploadConf(InsightsConfig().load_all()))
