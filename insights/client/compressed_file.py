#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Handle compressed filesystems
This replicates functionality that 'archivemount' would provide
"""
import logging
import tempfile
import tarfile
import os
import shutil

logger = logging.getLogger(__name__)


class InsightsCompressedFile(object):

    """
    This class handles uncompressing and mounting compressed filesystems
    """

    def __init__(self, compressed_file_location=None):
        self.compressed_file_location = compressed_file_location
        self.tmp_dir = tempfile.mkdtemp(prefix='/var/tmp/')
        self.is_file = os.path.isfile(self.compressed_file_location)
        self.is_tarfile = (tarfile.is_tarfile(self.compressed_file_location)
                            if self.is_file else False)
        if self.is_file and self.is_tarfile:
            try:
                tar = tarfile.open(self.compressed_file_location)
                tar.extractall(path=self.tmp_dir)
                tar.close()
                logger.debug("Compressed filesystem %s extracted to %s",
                    self.compressed_file_location, self.tmp_dir)
            except:
                logger.debug("Invalid compressed tar filesystem provided. "
                    "Could not extract contents.")
        else:
            logger.debug("Invalid compressed tar filesystem provided.")

    def cleanup_temp_filesystem(self):
        """
        Cleanup the temporary directory
        """
        logger.debug("Deleting compressed file extraction directory: " + self.tmp_dir)
        shutil.rmtree(self.tmp_dir, True)

    def get_filesystem_path(self):
        """
        Get the filesystem path, where it was extracted to
        """
        return self.tmp_dir
