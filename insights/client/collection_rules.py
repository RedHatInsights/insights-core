"""
Rules for data collection
"""

from __future__ import absolute_import

import json
import logging
import os
import six
import stat
import yaml

from six.moves import configparser as ConfigParser

from insights.client.constants import InsightsConstants as constants

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
        return True, (
            'Unknown section(s) in %s: ' % filename
            + ', '.join(invalid_keys)
            + '\nValid sections are '
            + ', '.join(expected_keys)
            + '.'
        )

    # validate format (lists of strings)
    for k in expected_keys:
        if k in parsed_data:
            if k == 'patterns' and isinstance(parsed_data['patterns'], dict):
                if 'regex' not in parsed_data['patterns']:
                    return (
                        True,
                        'Patterns section contains an object but the "regex" key was not specified.',
                    )
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
        raise RuntimeError(
            'ERROR: Cannot parse %s.\n'
            'If using any YAML tokens such as [] in an expression, '
            'be sure to wrap the expression in quotation marks.\n\nError details:\n%s\n'
            % (filename, e)
        )
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
        raise RuntimeError("Invalid permissions on %s. " "Expected 0600 got %s" % (f, oct(mode)))
    logger.debug("Correct file permissions on %s", f)


class InsightsUploadConf(object):
    """
    Insights spec configuration
    """

    def __init__(self, config, conn=None):
        """
        Load configuration from parent
        """
        self.config = config
        self.remove_file = config.remove_file
        self.redaction_file = config.redaction_file
        self.content_redaction_file = config.content_redaction_file
        self.tags_file = config.tags_file

        # set rm_conf as a class attribute so we can observe it
        # in blacklist_report
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
            logger.debug(
                '%s not found. No data files, commands,'
                ' or patterns will be ignored, and no keyword obfuscation will occur.',
                self.remove_file,
            )
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
                raise RuntimeError(
                    'ERROR: invalid section(s) in remove.conf. Only "remove" is valid.'
                )

            expected_keys = ('commands', 'files', 'patterns', 'keywords')
            rm_conf = {'new_format': False}
            for item, value in parsedconfig.items('remove'):
                if item not in expected_keys:
                    raise RuntimeError(
                        'ERROR: Unknown key in remove.conf: '
                        + item
                        + '\nValid keys are '
                        + ', '.join(expected_keys)
                        + '.'
                    )
                if six.PY3:
                    rm_conf[item] = [
                        v.strip()
                        for v in value.strip().encode('utf-8').decode('unicode-escape').split(',')
                    ]
                else:
                    rm_conf[item] = [
                        v.strip() for v in value.strip().decode('string-escape').split(',')
                    ]
            self.rm_conf = rm_conf
        except ConfigParser.Error as e:
            # can't parse config file at all
            logger.debug(e)
            logger.debug(
                'To configure using YAML, please use file-redaction.yaml and file-content-redaction.yaml.'
            )
            raise RuntimeError(
                'ERROR: Cannot parse the remove.conf file.\n'
                'See %s for more information.' % self.config.logging_file
            )
        logger.warning(
            'WARNING: remove.conf is deprecated. Please use file-redaction.yaml and file-content-redaction.yaml. See https://access.redhat.com/articles/4511681 for details.'
        )
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
                logger.debug(
                    '%s not found. No files or commands will be skipped.', self.redaction_file
                )
            elif fname == self.content_redaction_file:
                logger.debug(
                    '%s not found. '
                    'No patterns will be skipped and no keyword obfuscation will occur.',
                    self.content_redaction_file,
                )
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
        remove.conf (file-redaction.yaml and file-content-redaction.yaml)
        '''
        rm_conf = {}
        redact_conf = self.load_redaction_file(self.redaction_file)
        content_redact_conf = self.load_redaction_file(self.content_redaction_file)

        if not redact_conf and not content_redact_conf:
            # no file-redaction.yaml or file-content-redaction.yaml defined,
            #   try to use remove.conf
            self.rm_conf = self.get_rm_conf_old()
        else:
            rm_conf.update(new_format=True)
            rm_conf.update(redact_conf or {})
            rm_conf.update(content_redact_conf or {})
            # remove Nones, empty strings, and empty lists
            self.rm_conf = dict((k, v) for k, v in rm_conf.items() if v)

        if self.rm_conf and (
            '/etc/insights-client/machine-id' in self.rm_conf.get('files', [])
            or 'insights.specs.default.DefaultSpecs.machine_id'
            in self.rm_conf.get('components', [])
        ):
            logger.warning(
                "WARNING: Spec machine_id will be skipped for redaction; as it would cause issues, please remove it from %s.",
                self.redaction_file,
            )
        # return the RAW rm_conf
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
