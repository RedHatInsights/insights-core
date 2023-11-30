"""
Handle adding files and preparing the archive for upload
"""
from __future__ import absolute_import

import atexit
import logging
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

from signal import SIGTERM, signal

from insights.client.constants import InsightsConstants as constants
from insights.client.insights_spec import InsightsFile, InsightsCommand
from insights.client.utilities import determine_hostname, _expand_paths, write_data_to_file

logger = logging.getLogger(__name__)


class InsightsArchive(object):
    """
    This class is an interface for adding command output
    and files to the insights archive

    Attributes:
        config          - an InsightsConfig object
        tmp_dir         - a temporary directory in /var/tmp
        archive_dir     - location to collect archive data inside tmp_dir
        archive_name    - filename of the archive and archive_dir
        cmd_dir         - insights_commands directory inside archive_dir
        compressor      - tar compression flag to use
        tar_file        - path of the final archive file
    """
    def __init__(self, config):
        """
        Initialize the Insights Archive
        """
        self.config = config
        # clean old temporary archive
        self.cleanup_previous_archive()

        # Create a random temp directory
        # input this to core collector as `tmp_path`
        self.tmp_dir = tempfile.mkdtemp(dir=constants.insights_tmp_path, prefix=constants.insights_tmp_prefix + '-')

        # We should not hint the hostname in the archive if it has to be obfuscated
        if config.obfuscate_hostname:
            # insights-YYYYmmddHHMMSS-dddddd
            self.archive_name = ("insights-{0}-{1}".format(
                                    time.strftime("%Y%m%d%H%M%S"),
                                    uuid.uuid4().hex[:6]))
        else:
            # insights-hostname-YYYYmmddHHMMSS
            self.archive_name = ("insights-{0}-{1}".format(
                                    determine_hostname(),
                                    time.strftime("%Y%m%d%H%M%S")))

        # lazy create these, only if needed when certain
        #   functions are called
        # classic collection and compliance needs these
        # core collection will set "archive_dir" on its own
        self.archive_dir = None
        self.cmd_dir = None

        self.compressor = config.compressor
        self.archive_stored = None
        self.tar_file = None
        self.keep_archive_dir = '/var/cache/insights-client'
        atexit.register(self.cleanup_tmp)
        signal(SIGTERM, self.sigterm_handler)

    def create_archive_dir(self):
        """
        Create the archive directory if it is undefined or does not exist.
        """
        if self.archive_dir and os.path.exists(self.archive_dir):
            # attr defined and exists. move along
            return self.archive_dir

        archive_dir = os.path.join(self.tmp_dir, self.archive_name)
        if not os.path.exists(archive_dir):
            logger.debug('Creating archive directory %s...', archive_dir)
            os.makedirs(archive_dir, 0o700)
        self.archive_dir = archive_dir
        return self.archive_dir

    def create_command_dir(self):
        """
        Create the "insights_commands" dir
        """
        self.create_archive_dir()
        cmd_dir = os.path.join(self.archive_dir, "insights_commands")
        logger.debug('Creating command directory %s...', cmd_dir)
        if not os.path.exists(cmd_dir):
            os.makedirs(cmd_dir, 0o700)
        self.cmd_dir = cmd_dir
        return self.cmd_dir

    def get_full_archive_path(self, path):
        """
        Returns the full archive path
        """
        self.create_archive_dir()
        return os.path.join(self.archive_dir, path.lstrip('/'))

    def _copy_file(self, path):
        """
        Copy just a single file
        """
        full_path = self.get_full_archive_path(path)
        # Try to make the dir, eat exception if it fails
        try:
            os.makedirs(os.path.dirname(full_path))
        except OSError:
            pass
        logger.debug("Copying %s to %s", path, full_path)
        shutil.copyfile(path, full_path)
        return path

    def copy_file(self, path):
        """
        Copy a single file or regex, creating the necessary directories
        """
        if "*" in path:
            paths = _expand_paths(path)
            if paths:
                for path in paths:
                    self._copy_file(path)
        else:
            if os.path.isfile(path):
                return self._copy_file(path)
            else:
                logger.debug("File %s does not exist", path)
                return False

    def copy_dir(self, path):
        """
        Recursively copy directory
        """
        self.create_archive_dir()
        for directory in path:
            if os.path.isdir(path):
                full_path = os.path.join(self.archive_dir, directory.lstrip('/'))
                logger.debug("Copying %s to %s", directory, full_path)
                shutil.copytree(directory, full_path)
            else:
                logger.debug("Not a directory: %s", directory)
        return path

    def get_compression_flag(self, compressor):
        return {
            "gz": "z",
            "xz": "J",
            "bz2": "j",
            "none": ""
        }.get(compressor, "z")

    def create_tar_file(self):
        """
        Create tar file to be compressed
        """
        if not self.tmp_dir:
            # we should never get here but bail out if we do
            raise RuntimeError('Archive temporary directory not defined.')
        tar_file_name = os.path.join(self.tmp_dir, self.archive_name)
        ext = "" if self.compressor == "none" else ".%s" % self.compressor
        tar_file_name = tar_file_name + ".tar" + ext
        logger.debug("Tar File: " + tar_file_name)
        # change cwd to compress the archive directory inside the temporary directory
        # with the correct structure
        return_code = subprocess.call(shlex.split("tar c%sfS %s %s" % (
            self.get_compression_flag(self.compressor),
            tar_file_name, self.archive_name)),
            stderr=subprocess.PIPE, cwd=self.tmp_dir)
        if (self.compressor in ["bz2", "xz"] and return_code != 0):
            logger.error("ERROR: %s compressor is not installed, cannot compress file", self.compressor)
            return None
        self.delete_archive_dir()
        logger.debug("Tar File Size: %s", str(os.path.getsize(tar_file_name)))
        self.tar_file = tar_file_name
        return tar_file_name

    def delete_tmp_dir(self):
        """
        Delete the entire tmp dir
        """
        if self.tmp_dir:
            logger.debug("Deleting: " + self.tmp_dir)
            shutil.rmtree(self.tmp_dir, True)

    def delete_archive_dir(self):
        """
        Delete the entire archive dir
        """
        if self.archive_dir:
            logger.debug("Deleting: " + self.archive_dir)
            shutil.rmtree(self.archive_dir, True)

    def add_to_archive(self, spec, cleaner=None, spec_info=None):
        '''
        Add files and commands to archive
        Use InsightsSpec.get_output() to get data
        '''
        ab_regex = [
            "^timeout: failed to run command .+: No such file or directory$",
            "^Missing Dependencies:"
        ]
        if isinstance(spec, InsightsCommand):
            archive_path = os.path.join(self.cmd_dir, spec.archive_path.lstrip('/'))
        if isinstance(spec, InsightsFile):
            archive_path = self.get_full_archive_path(spec.archive_path.lstrip('/'))
        output = spec.get_output()
        if output and not any(re.search(rg, output) for rg in ab_regex):
            write_data_to_file(output, archive_path)
            if cleaner:
                no_obfuscate, no_redact = spec_info if spec_info else ([], False)
                # Redact and Obfuscate for data collection
                cleaner.clean_file(archive_path,
                                   no_obfuscate=no_obfuscate,
                                   no_redact=no_redact)

    def add_metadata_to_archive(self, metadata, meta_path):
        '''
        Add metadata to archive
        '''
        archive_path = self.get_full_archive_path(meta_path.lstrip('/'))
        write_data_to_file(metadata, archive_path)

    def cleanup_tmp(self):
        '''
        DEPRECATE in favor of systemd-tmpfiles removing files.
        Only used during built-in collection.
        Delete archive and tmp dirs on exit unless --keep-archive is specified
            and tar_file exists.
        '''
        if self.config.keep_archive and self.tar_file:
            self.storing_archive()
            if self.config.no_upload:
                logger.info('Archive saved at %s', self.archive_stored)
            else:
                logger.info('Insights archive retained in %s', self.archive_stored)
        self.delete_tmp_dir()

    def sigterm_handler(_signo, _stack_frame, _context):
        sys.exit(1)

    def cleanup_previous_archive(self):
        '''
        Used at the start, this will clean the temporary directory of previous killed runs
        '''
        try:
            one_day_ago = time.time() - 24 * 60 * 60
            # list insights-client temporary directories
            directories = [os.path.join(constants.insights_tmp_path, directory)
                           for directory in os.listdir(constants.insights_tmp_path)
                           if directory.startswith(constants.insights_tmp_prefix)]
            # filter only those last modified more than 24 hours ago
            directories = [directory
                           for directory in directories
                           if os.path.isdir(directory) and os.path.getmtime(directory) <= one_day_ago]
            # remove the directories
            for directory in directories:
                logger.debug("Deleting previous archive %s", directory)
                shutil.rmtree(directory, True)
        except Exception:
            logger.error("ERROR: Could not remove old temporary directory")

    def storing_archive(self):
        if not os.path.exists(self.keep_archive_dir):
            try:
                os.makedirs(self.keep_archive_dir)
            except OSError:
                logger.error('ERROR: Could not create %s', self.keep_archive_dir)
                raise

        archive_name = os.path.basename(self.tar_file)
        self.archive_stored = os.path.join(self.keep_archive_dir, archive_name)
        logger.info('Copying archive from %s to %s', self.tar_file, self.archive_stored)
        try:
            shutil.copyfile(self.tar_file, self.archive_stored)
        except OSError:
            # file exists already
            logger.error('ERROR: Could not stored archive to %s', self.archive_stored)
            raise
