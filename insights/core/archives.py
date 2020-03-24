#!/usr/bin/env python

import logging
import os
import tempfile
from contextlib import contextmanager
from insights.util import fs, subproc
from insights.util.content_type import from_file as content_type_from_file

logger = logging.getLogger(__name__)


COMPRESSION_TYPES = ("zip", "tar", "gz", "bz2", "xz")


class InvalidArchive(Exception):
    def __init__(self, msg):
        super(InvalidArchive, self).__init__(msg)
        self.msg = msg


class InvalidContentType(InvalidArchive):
    def __init__(self, content_type):
        self.msg = 'Invalid content type: "%s"' % content_type
        super(InvalidContentType, self).__init__(self.msg)
        self.content_type = content_type


class Extractor(object):
    """Base class for different extractor types."""
    def __init__(self, timeout=None, memory_limit=None):
        """Creates an extractor object with a given timeout and memory_limit."""
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.tmp_dir = None
        self.created_tmp_dir = False

    def from_path(selfself, path, extract_dir=None, content_type=None):
        """Abstract method for child classes"""
        raise NotImplementedError()


class ZipExtractor(Extractor):
    """Extractor implementation for ZIP archives."""
    def __init__(self, timeout=None, memory_limit=None):
        """Create a ZipExtractor object."""
        super(ZipExtractor, self).__init__(timeout, memory_limit)
        self.content_type = "application/zip"

    def from_path(self, path, extract_dir=None, content_type=None):
        self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
        self.created_tmp_dir = True
        command = "unzip -n -q -d %s %s" % (self.tmp_dir, path)
        subproc.call(command, timeout=self.timeout, memory_limit=self.memory_limit)
        return self


class TarExtractor(Extractor):
    """Extractor implementation for TAR archives."""
    TAR_FLAGS = {
        "application/x-xz": "-J",
        "application/x-gzip": "-z",
        "application/gzip": "-z",
        "application/x-bzip2": "-j",
        "application/x-tar": ""
    }

    def __init__(self, timeout=None, memory_limit=None):
        super(TarExtractor, self).__init__(timeout, memory_limit)
        self.content_type = "application/tar"

    def _tar_flag_for_content_type(self, content_type):
        """Return the tar command flag for the given content-type or raise an Exception."""
        flag = self.TAR_FLAGS.get(content_type)
        if flag is None:
            raise InvalidContentType(content_type)
        return flag

    def from_path(self, path, extract_dir=None, content_type=None):
        if os.path.isdir(path):
            self.tmp_dir = path
        else:
            self.content_type = content_type or content_type_from_file(path)
            tar_flag = self._tar_flag_for_content_type(self.content_type)
            self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
            self.created_tmp_dir = True
            command = "tar --delay-directory-restore %s -x --exclude=*/dev/null -f %s -C %s" % (tar_flag, path, self.tmp_dir)
            logging.debug("Extracting files in '%s'", self.tmp_dir)
            subproc.call(command, timeout=self.timeout, memory_limit=self.memory_limit)
        return self


def get_all_files(path):
    names = []
    for root, dirs, files in os.walk(path):
        for dirname in dirs:
            names.append(os.path.join(root, dirname) + "/")
        for filename in files:
            names.append(os.path.join(root, filename))
    return names


class Extraction(object):
    def __init__(self, tmp_dir, content_type):
        self.tmp_dir = tmp_dir
        self.content_type = content_type


@contextmanager
def extract(path, timeout=None, memory_limit=None, extract_dir=None, content_type=None):
    """
    Extract path into a temporary directory in `extract_dir`.

    Yields an object containing the temporary path and the content type of the
    original archive.

    If the extraction takes longer than `timeout` seconds or the child process
    tries to use more than `memory_limit` RAM, the temporary path is removed,
    and an exception is raised.
    """
    content_type = content_type or content_type_from_file(path)
    if content_type == "application/zip":
        extractor = ZipExtractor(timeout=timeout, memory_limit=memory_limit)
    else:
        extractor = TarExtractor(timeout=timeout, memory_limit=memory_limit)

    try:
        ctx = extractor.from_path(path, extract_dir=extract_dir, content_type=content_type)
        content_type = extractor.content_type
        yield Extraction(ctx.tmp_dir, content_type)
    finally:
        if extractor.created_tmp_dir:
            fs.remove(extractor.tmp_dir, chmod=True)
