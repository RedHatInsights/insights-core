"""
Module for executing a command or pipeline of commands and yielding the result
as a generator of lines.
"""
import os
import shlex
import signal
from contextlib import contextmanager
from subprocess import Popen, PIPE, STDOUT

from insights.util import which

stream_options = {
    "bufsize": -1,  # use OS defaults. Non buffered if not set.
    "universal_newlines": True,  # convert all to "\n"
    "stdout": PIPE,  # pipe to Popen.stdout instead of literally stdout
    "stderr": STDOUT  # redirect stderr to stdout for all processes
}


def reader(stream):
    for line in stream:
        yield line.rstrip("\n")


timeout_command = [which("timeout"), "-s", str(signal.SIGKILL)]


@contextmanager
def stream(command, stdin=None, env=os.environ, timeout=None):
    """
    Yields a generator of a command's output. For line oriented commands only.

    Args:
        command (str or list): a command without pipes. If it's not a list,
            ``shlex.split`` is applied.
        stdin (file like object): stream to use as the command's standard input.
        env (dict): The environment in which to execute the command. PATH should
            be defined.
        timeout (int): Amount of time in seconds to give the command to complete.
            The ``timeout`` utility must be installed to use this feature.

    Yields:
        The output stream for the command. It should typically be wrapped in a
        ``reader``.
    """
    if not isinstance(command, list):
        command = shlex.split(command)

    cmd = which(command[0])
    if cmd is None:
        path = env.get("PATH", "")
        raise Exception("Command [%s] not in PATH [%s]" % (command[0], path))

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
    """
    Connects multiple command streams together and yields the final stream.

    Args:
        cmds (list): list of commands to pipe together. Each command will be an
            input to ``stream``.
        stdin (file like object): stream to use as the first command's
            standard input.
        env (dict): The environment in which to execute the commands. PATH
            should be defined.
        timeout (int): Amount of time in seconds to give the pipeline to complete.
            The ``timeout`` utility must be installed to use this feature.

    Yields:
        The output stream for the final command in the pipeline. It should
        typically be wrapped in a ``reader``.
    """
    stdin = kwargs.get("stdin")
    env = kwargs.get("env", os.environ)
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
