import shlex
import subprocess
from subprocess import PIPE

try:
    import insights.contrib.magic as magic
except Exception:
    magic_loaded = False
else:
    _magic = magic.open(magic.MIME_TYPE)
    _magic.load()

    _magic_inner = magic.open(magic.MIME_TYPE | magic.MAGIC_COMPRESS)
    _magic_inner.load()
    magic_loaded = True


def from_file(name):
    if magic_loaded:
        return _magic.file(name)
    else:
        cmd = "file --mime-type -b %s"
        return subprocess.check_output(shlex.split(cmd % name)).strip()


def from_buffer(b):
    if magic_loaded:
        return _magic.buffer(b)
    else:
        cmd = "file --mime-type -b -"
        p = subprocess.Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate(b)
        return stdout.strip()


def from_file_inner(name):
    if magic_loaded:
        return _magic_inner.file(name)
    else:
        cmd = "file --mime-type -bz %s"
        return subprocess.check_output(shlex.split(cmd % name)).strip()


def from_buffer_inner(b):
    if magic_loaded:
        return _magic_inner.buffer(b)
    else:
        cmd = "file --mime-type -bz -"
        p = subprocess.Popen(shlex.split(cmd), stdin=PIPE, stdout=PIPE)
        stdout, stderr = p.communicate(b)
        return stdout.strip()
