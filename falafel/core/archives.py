#!/usr/bin/env python

import logging
import os
import shlex
import subprocess
import tempfile
from falafel.core.marshalling import Marshaller
from falafel.util import subproc, fs

try:
    import falafel.contrib.magic as magic
except Exception:
    raise ImportError("You need to install the 'file' RPM.")
else:
    _magic = magic.open(magic.MIME_TYPE)
    _magic.load()

logger = logging.getLogger(__name__)
marshaller = Marshaller()


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
    """
    Abstract base class for extraction of archives
    into usable objects.
    """

    def __init__(self, timeout=150):
        self.tmp_dir = None
        self.timeout = timeout

    def from_buffer(self, buf):
        pass

    def from_path(self, path):
        pass

    def getnames(self):
        return self.tar_file.getnames()

    def extractfile(self, name):
        return self.tar_file.extractfile(name)

    def cleanup(self):
        if self.tmp_dir:
            fs.remove(self.tmp_dir, chmod=True)

    def issym(self, name):
        return self.tar_file.issym(name)

    def isdir(self, name):
        return self.tar_file.isdir(name)

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.cleanup()


class ZipExtractor(Extractor):

    def from_buffer(self, buf):
        with tempfile.NamedTemporaryFile() as tf:
            tf.write(buf)
            tf.flush()
            return self.from_path(tf.name)

    def from_path(self, path):
        self.tmp_dir = tempfile.mkdtemp()
        command = "unzip %s -d %s" % (path, self.tmp_dir)
        subprocess.call(shlex.split(command))
        self.tar_file = DirectoryAdapter(self.tmp_dir)
        return self


class TarExtractor(Extractor):

    TAR_FLAGS = {
        "application/x-xz": "-J",
        "application/x-gzip": "-z",
        "application/gzip": "-z",
        "application/x-bzip2": "-j",
        "application/x-tar": ""
    }

    def from_buffer(self, buf):
        self.content_type = _magic.buffer(buf)
        tar_flag = self.TAR_FLAGS.get(self.content_type)
        if tar_flag is None:
            raise InvalidContentType(self.content_type)

        self.tmp_dir = tempfile.mkdtemp()
        command = "tar %s -x -f - -C %s" % (tar_flag, self.tmp_dir)
        p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE)
        p.stdin.write(buf)
        p.stdin.close()
        p.communicate()
        self.tar_file = DirectoryAdapter(self.tmp_dir)
        return self

    def from_path(self, path, extract_dir=None):
        if os.path.isdir(path):
            self.tar_file = DirectoryAdapter(path)
        else:
            self.content_type = _magic.file(path)
            if self.content_type not in self.TAR_FLAGS:
                raise InvalidContentType(self.content_type)

            tar_flag = self.TAR_FLAGS.get(self.content_type)
            self.tmp_dir = tempfile.mkdtemp(dir=extract_dir)
            command = "tar %s -x -f %s -C %s" % (tar_flag, path, self.tmp_dir)

            logging.info("Extracting files in '%s'", self.tmp_dir)
            subproc.call(command, timeout=self.timeout)
            self.tar_file = DirectoryAdapter(self.tmp_dir)
        return self


class DirectoryAdapter(object):
    """
    This class takes a path to a directory and provides a subset of
    the methods that a tarfile object provides.
    """

    def __init__(self, path):
        self.path = path
        self.names = []
        for root, dirs, files in os.walk(self.path):
            for dirname in dirs:
                self.names.append(os.path.join(root, dirname) + "/")
            for filename in files:
                self.names.append(os.path.join(root, filename))

    def getnames(self):
        return self.names

    def extractfile(self, name):
        with open(name, "rb") as fp:
            return fp.read()

    def issym(self, name):
        return os.path.islink(name)

    def isdir(self, name):
        return os.path.isdir(name)

    def close(self):
        pass
