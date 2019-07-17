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

from .utilities import determine_hostname, _expand_paths, write_data_to_file
from .insights_spec import InsightsFile, InsightsCommand

logger = logging.getLogger(__name__)


class InsightsArchive(object):
    """
    This class is an interface for adding command output
    and files to the insights archive
    """

    def __init__(self, compressor="gz", target_name=None):
        """
        Initialize the Insights Archive
        Create temp dir, archive dir, and command dir
        """

        self.tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        self.archive_tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        name = determine_hostname(target_name)
        self.archive_name = ("insights-%s-%s" %
                             (name,
                              time.strftime("%Y%m%d%H%M%S")))
        self.archive_dir = self.create_archive_dir()
        self.cmd_dir = self.create_command_dir()
        self.compressor = compressor

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

    def create_tar_file(self, full_archive=False):
        """
        Create tar file to be compressed
        """
        tar_file_name = os.path.join(self.archive_tmp_dir, self.archive_name)
        ext = "" if self.compressor == "none" else ".%s" % self.compressor
        tar_file_name = tar_file_name + ".tar" + ext
        logger.debug("Tar File: " + tar_file_name)
        subprocess.call(shlex.split("tar c%sfS %s -C %s ." % (
            self.get_compression_flag(self.compressor),
            tar_file_name,
            # for the docker "uber archive,"use archive_dir
            #   rather than tmp_dir for all the files we tar,
            #   because all the individual archives are in there
            self.tmp_dir if not full_archive else self.archive_dir)),
            stderr=subprocess.PIPE)
        self.delete_archive_dir()
        logger.debug("Tar File Size: %s", str(os.path.getsize(tar_file_name)))
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
        logger.debug("Deleting %s", self.archive_tmp_dir)
        shutil.rmtree(self.archive_tmp_dir, True)

    def add_to_archive(self, spec):
        '''
        Add files and commands to archive
        Use InsightsSpec.get_output() to get data
        '''
        cmd_not_found_regex = "^timeout: failed to run command .+: No such file or directory$"
        if isinstance(spec, InsightsCommand):
            archive_path = os.path.join(self.cmd_dir, spec.archive_path.lstrip('/'))
        if isinstance(spec, InsightsFile):
            archive_path = self.get_full_archive_path(spec.archive_path.lstrip('/'))
        output = spec.get_output()
        if output and not re.search(cmd_not_found_regex, output):
            write_data_to_file(output, archive_path)

    def add_metadata_to_archive(self, metadata, meta_path):
        '''
        Add metadata to archive
        '''
        archive_path = self.get_full_archive_path(meta_path.lstrip('/'))
        write_data_to_file(metadata, archive_path)
