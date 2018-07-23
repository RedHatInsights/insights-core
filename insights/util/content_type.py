import shlex
import subprocess
from subprocess import PIPE
import six

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


def from_file(name):
    if magic_loaded:
        return six.b(_magic.file(name)).decode("unicode-escape").splitlines()[0].strip()
    else:
        cmd = "file --mime-type -b %s"
        p = subprocess.Popen(shlex.split(cmd % name), stdout=subprocess.PIPE)
        stdout, _ = p.communicate()
        return stdout.strip().decode("utf-8")


def from_buffer(b):
    if magic_loaded:
        return _magic.buffer(b)
    else:
        cmd = "file --mime-type -b -"
        p = subprocess.Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate(b)
        return stdout.strip().decode("utf-8")
