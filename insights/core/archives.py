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

    def from_path(self, path, extract_dir=None):
        self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
        command = "unzip -q -d %s %s" % (self.tmp_dir, path)
        subproc.call(command, timeout=self.timeout)
        return self


class TarExtractor(object):

    def __init__(self, timeout=None):
        self.timeout = timeout

    TAR_FLAGS = {
        "application/x-xz": "-J",
        "application/x-gzip": "-z",
        "application/gzip": "-z",
        "application/x-bzip2": "-j",
        "application/x-tar": ""
    }

    def _assert_type(self, _input, is_buffer=False):
        self.content_type = content_type.from_file(_input)

        if self.content_type not in self.TAR_FLAGS:
            raise InvalidContentType(self.content_type)

        inner_type = content_type.from_file_inner(_input)

        if inner_type != 'application/x-tar':
            raise InvalidArchive('No compressed tar archive')

    def from_path(self, path, extract_dir=None):
        if os.path.isdir(path):
            self.tmp_dir = path
        else:
            self._assert_type(path, False)
            tar_flag = self.TAR_FLAGS.get(self.content_type)
            self.tmp_dir = tempfile.mkdtemp(prefix="insights-", dir=extract_dir)
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
def extract(path, timeout=None, extract_dir=None):
    content_type = from_file(path)
    if content_type == "application/zip":
        extractor = ZipExtractor(timeout=timeout)
    else:
        extractor = TarExtractor(timeout=timeout)

    tmp_dir = None
    try:
        tmp_dir = extractor.from_path(path, extract_dir=extract_dir).tmp_dir
        content_type = extractor.content_type
        yield Extraction(tmp_dir, content_type)
    finally:
        if tmp_dir:
            fs.remove(tmp_dir, chmod=True)
