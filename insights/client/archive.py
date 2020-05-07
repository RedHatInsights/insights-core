"""
Handle adding files and preparing the archive for upload
"""
from __future__ import absolute_import
import time
import os
import shutil
import subprocess
import shlex
import logging
import tempfile
import re
import atexit

from .utilities import determine_hostname, _expand_paths, write_data_to_file
from .insights_spec import InsightsFile, InsightsCommand

logger = logging.getLogger(__name__)


class InsightsArchive(object):
    """
    This class is an interface for adding command output
    and files to the insights archive
    """
    def __init__(self, config):
        """
        Initialize the Insights Archive
        Create temp dir, archive dir, and command dir
        """
        self.config = config
        self.tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        self.archive_tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        name = determine_hostname()
        self.archive_name = ("insights-%s-%s" %
                             (name,
                              time.strftime("%Y%m%d%H%M%S")))
        self.archive_dir = self.create_archive_dir()
        self.cmd_dir = self.create_command_dir()
        self.compressor = config.compressor
        self.tar_file = None
        atexit.register(self.cleanup_tmp)

    def create_archive_dir(self):
        """
        Create the archive dir
        """
        archive_dir = os.path.join(self.tmp_dir, self.archive_name)
        os.makedirs(archive_dir, 0o700)
        return archive_dir

    def create_command_dir(self):
        """
        Create the "sos_commands" dir
        """
        cmd_dir = os.path.join(self.archive_dir, "insights_commands")
        os.makedirs(cmd_dir, 0o700)
        return cmd_dir

    def get_full_archive_path(self, path):
        """
        Returns the full archive path
        """
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
        if not self.archive_tmp_dir:
            # we should never get here but bail out if we do
            raise RuntimeError('Archive temporary directory not defined.')
        tar_file_name = os.path.join(self.archive_tmp_dir, self.archive_name)
        ext = "" if self.compressor == "none" else ".%s" % self.compressor
        tar_file_name = tar_file_name + ".tar" + ext
        logger.debug("Tar File: " + tar_file_name)
        return_code = subprocess.call(shlex.split("tar c%sfS %s -C %s ." % (
            self.get_compression_flag(self.compressor),
            tar_file_name, self.tmp_dir)),
            stderr=subprocess.PIPE)
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
        logger.debug("Deleting: " + self.tmp_dir)
        shutil.rmtree(self.tmp_dir, True)

    def delete_archive_dir(self):
        """
        Delete the entire archive dir
        """
        logger.debug("Deleting: " + self.archive_dir)
        shutil.rmtree(self.archive_dir, True)

    def delete_archive_file(self):
        """
        Delete the directory containing the constructed archive
        """
        if self.archive_tmp_dir:
            logger.debug("Deleting %s", self.archive_tmp_dir)
            shutil.rmtree(self.archive_tmp_dir, True)

    def add_to_archive(self, spec):
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

    def add_metadata_to_archive(self, metadata, meta_path):
        '''
        Add metadata to archive
        '''
        archive_path = self.get_full_archive_path(meta_path.lstrip('/'))
        write_data_to_file(metadata, archive_path)

    def cleanup_tmp(self):
        '''
        Only used during built-in collection.
        Delete archive and tmp dirs on exit unless --keep-archive is specified
            and tar_file exists.
        '''
        if self.config.keep_archive and self.tar_file:
            if self.config.no_upload:
                logger.info('Archive saved at %s', self.tar_file)
            else:
                logger.info('Insights archive retained in %s', self.tar_file)
            if self.config.obfuscate:
                return  # return before deleting tmp_dir
        else:
            self.delete_archive_file()
        self.delete_tmp_dir()
