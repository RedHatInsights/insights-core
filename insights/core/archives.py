#!/usr/bin/env python

import logging
import os
import tempfile
from contextlib import contextmanager
from insights.util import content_type, fs, subproc

from insights.util.content_type import from_file
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


class ZipExtractor(object):
    def __init__(self, timeout=None):
        self.content_type = "application/zip"
        self.timeout = timeout
        self.tmp_dir = None
        self.created_tmp_dir = False

    def from_path(self, path, extract_dir=None, content_type=None):
        self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
        self.created_tmp_dir = True
        command = "unzip -n -q -d %s %s" % (self.tmp_dir, path)
        subproc.call(command, timeout=self.timeout)
        return self


class TarExtractor(object):

    def __init__(self, timeout=None):
        self.timeout = timeout
        self.tmp_dir = None

    TAR_FLAGS = {
        "application/x-xz": "-J",
        "application/x-gzip": "-z",
        "application/gzip": "-z",
        "application/x-bzip2": "-j",
        "application/x-tar": ""
    }

    def _archive_type(self, _input):
        _type = content_type.from_file(_input)
        if _type not in self.TAR_FLAGS:
            raise InvalidContentType(_type)
        return _type

    def from_path(self, path, extract_dir=None, content_type=None):
        if os.path.isdir(path):
            self.tmp_dir = path
        else:
            self.content_type = content_type or self._archive_type(path)
            tar_flag = self.TAR_FLAGS.get(self.content_type)
            self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
            self.created_tmp_dir = True
            command = "tar %s -x --exclude=*/dev/null -f %s -C %s" % (tar_flag, path, self.tmp_dir)
            logging.debug("Extracting files in '%s'", self.tmp_dir)
            subproc.call(command, timeout=self.timeout)
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
def extract(path, timeout=None, extract_dir=None, content_type=None):
    """
    Extract path into a temporary directory in `extract_dir`.

    Yields an object containing the temporary path and the content type of the
    original archive.

    If the extraction takes longer than `timeout` seconds, the temporary path
    is removed, and an exception is raised.
    """
    content_type = content_type or from_file(path)
    if content_type == "application/zip":
        extractor = ZipExtractor(timeout=timeout)
    else:
        extractor = TarExtractor(timeout=timeout)

    try:
        ctx = extractor.from_path(path, extract_dir=extract_dir, content_type=content_type)
        content_type = extractor.content_type
        yield Extraction(ctx.tmp_dir, content_type)
    finally:
        if extractor.created_tmp_dir:
            fs.remove(extractor.tmp_dir, chmod=True)
