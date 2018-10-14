import logging
import os
import shlex
import signal
import six
import sys
from subprocess import Popen, PIPE, STDOUT

from insights.util import which

log = logging.getLogger(__name__)


class CalledProcessError(Exception):
    """Raised if call fails.

    Parameters
    ----------
    returncode : int
        The return code of the process executing the command.
    cmd : str
        The command that was executed.
    output : str
        Any output the command produced.

    Attributes
    ----------
    returncode : int
        The return code of the process executing the command.
    cmd : str
        The command that was executed.
    output : str
        Any output the command produced.
     """

    def __init__(self, returncode, cmd, output=None):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        super(CalledProcessError, self).__init__(returncode, cmd, output)

    def __unicode__(self):
        name = self.__class__.__name__
        rc = self.returncode
        cmd = self.cmd
        output = self.output
        return '<{c}({r}, {cmd}, {o})>'.format(c=name, r=rc, cmd=cmd, o=output)


class Pipeline(object):
    """
    Connect a list of lists of commands together with the stdout of one as the
    stdin of the next. The output of the last command is written to out_stream.

    >>> p = Pipeline("ls -lrt", "grep .py")
    >>> output = p()
    >>> p.write("pythons.txt")
    """
    def __init__(self, *cmds, **kwargs):
        """
        cmds (list): one or more commands. Each command will be shlex.split if
            it isn't already split.
        bufsize (int): size of the I/O buffers to use between processes running
            the commands. -1 means to use system defaults. 0 means no buffering.
            Defaults to -1.
        env (dict): environment in which to execute commands. Defaults to
            os.environ.
        timeout (int): number of seconds to wait before killing the command.
            Defaults to None, which waits forever.
        signum (int): signal to send the command on timeout. Defaults to
            signal.SIGKILL
        """

        self.bufsize = kwargs.get("bufsize", -1)
        self.env = kwargs.get("env", os.environ)
        timeout = kwargs.get("timeout")
        signum = kwargs.get("signum", signal.SIGKILL)

        cmds = [shlex.split(c) if not isinstance(c, list) else c for c in cmds]
        timeout_command = which("timeout", env=self.env)
        if timeout:
            if timeout_command:
                to = shlex.split("timeout -s {0} {1}".format(signum, timeout))
                to.extend(cmds[0])
                cmds[0] = to
            else:
                # TODO: Should this raise an exception instead?
                log.warn("Timeout specified but timeout command unavailable.")
        self.cmds = cmds

    def _build_pipes(self, out_stream=PIPE):
        log.debug("Executing: %s" % str(self.cmds))
        if len(self.cmds) == 1:
            return Popen(self.cmds[0], bufsize=self.bufsize, stderr=STDOUT, stdout=out_stream, env=self.env)

        stdout = Popen(self.cmds[0], bufsize=self.bufsize, stderr=STDOUT, stdout=PIPE, env=self.env).stdout
        last = len(self.cmds) - 2
        for i, arg in enumerate(self.cmds[1:]):
            if i < last:
                stdout = Popen(arg, bufsize=self.bufsize, stdin=stdout, stderr=STDOUT, STDOUT=PIPE, env=self.env).stdout
            else:
                return Popen(arg, bufsize=self.bufsize, stdin=stdout, stderr=STDOUT, stdout=out_stream, env=self.env)

    def __call__(self, keep_rc=False):
        """
        Executes the pipeline.

        Returns:
            The final output of the pipeline if keep_rc is False;
            an (exit code, output) tuple if keep_rc is True.
        Raises:
            CalledProcessError if any return code in the pipeline is nonzero
            and keep_rc is False.
        """
        p = self._build_pipes()
        output = p.communicate()[0]
        rc = p.poll()
        if keep_rc:
            return (rc, output)
        if rc:
            raise CalledProcessError(rc, self.cmds[0], output)
        return output

    def write(self, output, mode="w", keep_rc=False):
        """
        Executes the pipeline and writes the results to the supplied output.
        If output is a filename and the file didn't already exist before trying
        to write, the file will be removed if an exception is raised.

        Args:
            output (str or file like object): will create a new file of this
                name or overwrite an existing file. If output is already a file
                like object, it is used.
            mode (str): mode to use when creating or opening the provided file
                name if it is a string. Ignored if output is a file like object.

        Returns:
            The final output of the pipeline.
        Raises:
            CalledProcessError if any return code in the pipeline is nonzero.
        """
        if isinstance(output, six.string_types):
            already_exists = os.path.exists(output)
            try:
                with open(output, mode) as f:
                    p = self._build_pipes(f)
                    rc = p.wait()
                    if keep_rc:
                        return rc
                    if rc:
                        raise CalledProcessError(rc, self.cmds[0], "")
            except BaseException as be:
                if not already_exists and os.path.exists(output):
                    os.remove(output)
                six.reraise(be.__class__, be, sys.exc_info()[2])
        else:
            p = self._build_pipes(output)
            rc = p.wait()
            if keep_rc:
                return rc
            if rc:
                raise CalledProcessError(rc, self.cmds[0], "")


def call(cmd,
         timeout=None,
         signum=signal.SIGKILL,
         keep_rc=False,
         encoding="utf-8",
         env=os.environ):
    """
    Execute a cmd or list of commands with an optional timeout in seconds.

    If `timeout` is supplied and expires, the process is killed with
    SIGKILL (kill -9) and an exception is raised. Otherwise, the command
    output is returned.

    Parameters
    ----------
    cmd: str or [[str]]
        The command(s) to execute
    timeout: int
        Seconds before kill is issued to the process
    signum: int
        The signal number to issue to the process on timeout
    keep_rc: bool
        Whether to return the exit code along with the output
    encoding: str
        unicode decoding scheme to use. Default is "utf-8"
    env: dict
        The environment in which to execute commands. Default is os.environ

    Returns
    -------
    str
        Content of stdout of cmd on success.

    Raises
    ------
        CalledProcessError
            Raised when cmd fails
    """

    if not isinstance(cmd, list):
        cmd = [cmd]

    p = Pipeline(*cmd, timeout=timeout, signum=signum, env=env)
    res = p(keep_rc=keep_rc)

    if keep_rc:
        rc, output = res
        output = output.decode(encoding, 'ignore')
        return rc, output
    return res.decode(encoding, "ignore")
