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

import shlex
import subprocess
from subprocess import PIPE
import six
from threading import Lock

try:
    from insights.contrib import magic
except Exception:
    magic_loaded = False
else:
    # RHEL 6 does not have MAGIC_MIME_TYPE defined, but passing in the value
    # found in RHEL 7 (16, base 10), seems to work.
    mime_flag = magic.MAGIC_MIME_TYPE if hasattr(magic, "MAGIC_MIME_TYPE") else 16
    _magic = magic.open(mime_flag | magic.CONTINUE)
    _magic.load()

    magic_loaded = True


# libmagic is not thread safe so we must lock access to file
magic_lock = Lock()


def from_file(name):
    if magic_loaded:
        with magic_lock:
            return six.b(_magic.file(name)).decode("unicode-escape").splitlines()[0].strip()
    else:
        cmd = "file --mime-type -b %s"
        p = subprocess.Popen(shlex.split(cmd % name), stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        return stdout.strip().decode("utf-8")


def from_buffer(b):
    if magic_loaded:
        with magic_lock:
            return _magic.buffer(b)
    else:
        cmd = "file --mime-type -b -"
        p = subprocess.Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate(b)
        return stdout.strip().decode("utf-8")
