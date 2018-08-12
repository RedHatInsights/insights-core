import shlex
import signal
from contextlib import contextmanager
from subprocess import Popen, PIPE

from insights.util import which

stream_options = {
    "bufsize": -1,  # use OS defaults. Non buffered if not set.
    "universal_newlines": True,  # convert all to "\n"
    "stdout": PIPE  # pipe to Popen.stdout instead of literally stdout
}


def reader(stream):
    for line in stream:
        yield line.rstrip("\n")


timeout_command = [which("timeout"), "-s", str(signal.SIGKILL)]


@contextmanager
def stream(command, stdin=None, env=None, timeout=None):
    if not isinstance(command, list):
        command = shlex.split(command)

    cmd = which(command[0])
    if cmd is None:
        raise Exception("Couldn't execute: %s" % command)

    command[0] = cmd

    if timeout:
        if not timeout_command[0]:
            raise Exception("Timeout specified but timeout command not available.")
        command = timeout_command + [str(timeout)] + command

    output = None
    try:
        output = Popen(command, env=env, stdin=stdin, **stream_options)
        yield output.stdout
    finally:
        if output:
            output.wait()


@contextmanager
def connect(*cmds, **kwargs):
    stdin = kwargs.get("stdin")
    env = kwargs.get("env")
    timeout = kwargs.get("timeout")
    end = len(cmds) - 1

    @contextmanager
    def inner(idx, inp):
        with stream(cmds[idx], stdin=inp, env=env, timeout=timeout) as s:
            if idx == end:
                yield s
            else:
                with inner(idx + 1, s) as c:
                    yield c

    with inner(0, stdin) as s:
        yield s
