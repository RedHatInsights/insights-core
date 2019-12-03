"""
Handle adding files and preparing the archive for upload
"""
from __future__ import absolute_import
import os
import subprocess
import shlex
import logging
import tempfile

from .utilities import write_data_to_file

logger = logging.getLogger(__name__)


class InsightsArchive(object):
    """
    This class is an interface for adding command output
    and files to the insights archive
    """

    def __init__(self, tmp_path, compressor="gz"):
        """
        Initialize the Insights Archive
        Create temp dir, archive dir, and command dir
        """
        # make sure tmp_path is safe
        if (tmp_path == '/'
           or os.path.dirname(tmp_path.rstrip('/')) == '/'):
            # since we delete this later,
            #   if the provided path is either / or one level down,
            #   get out of here
            raise RuntimeError('Disallowed temp path: %s' % tmp_path)
        self.collected_data_dir = tmp_path
        self.compressor = compressor
        self.tar_file_name = None

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
        archive_name = os.path.basename(self.collected_data_dir) or 'insights-archive'

        tar_file_name = os.path.join(tempfile.gettempdir(), archive_name)
        ext = "" if self.compressor == "none" else ".%s" % self.compressor
        tar_file_name = tar_file_name + ".tar" + ext
        logger.debug("Tar File: " + tar_file_name)
        if self.compressor not in ["gz", "xz", "bz2", "none"]:
            logger.error("The compressor %s is not supported.  Using default: gz", self.compressor)
        return_code = subprocess.call(shlex.split("tar c%sfS %s -C %s ." % (
            self.get_compression_flag(self.compressor),
            tar_file_name, self.collected_data_dir)),
            stderr=subprocess.PIPE)
        if (self.compressor in ["bz2", "xz"] and return_code != 0):
            logger.error("ERROR: %s compressor is not installed, cannot compress file", self.compressor)
            return None
        self.delete_collected_data_dir()
        logger.debug("Tar File Size: %s", str(os.path.getsize(tar_file_name)))
        self.tar_file = tar_file_name
        return tar_file_name

    def delete_collected_data_dir(self):
        """
        Delete the dir containing collected data
        """
        logger.debug("Deleting: " + self.collected_data_dir)
        shutil.rmtree(self.collected_data_dir, True)

    def delete_tar_file(self):
        """
        Delete the constructed archive
        """
        logger.debug("Deleting %s", self.tar_file)
        shutil.rmtree(self.tar_file, True)

    def add_metadata_to_archive(self, metadata, meta_path):
        '''
        Add metadata to archive
        '''
        archive_path = os.path.join(self.collected_data_dir, meta_path.lstrip('/'))
        write_data_to_file(metadata, archive_path)
