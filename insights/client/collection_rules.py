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
from six.moves import configparser as ConfigParser

from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from .constants import InsightsConstants as constants

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
net_logger = logging.getLogger('network')


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

    def get_rm_conf(self):
        """
        Get excluded files config from remove_file.
        """
        if not os.path.isfile(self.remove_file):
            return None

        # Convert config object into dict
        parsedconfig = ConfigParser.RawConfigParser()
        parsedconfig.read(self.remove_file)
        rm_conf = {}

        for item, value in parsedconfig.items('remove'):
            if six.PY3:
                rm_conf[item] = value.strip().encode('utf-8').decode('unicode-escape').split(',')
            else:
                rm_conf[item] = value.strip().decode('string-escape').split(',')

        return rm_conf


if __name__ == '__main__':
    from .config import InsightsConfig
    print(InsightsUploadConf(InsightsConfig().load_all()))
