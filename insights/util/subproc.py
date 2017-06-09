import logging
import shlex
import signal
import subprocess
import sys

log = logging.getLogger(__name__)

STDOUT = subprocess.PIPE
STDERR = subprocess.STDOUT


class CalledProcessError(IOError):
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

    def __init__(self, returncode, cmd, output):
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


def call(cmd, timeout=None, signum=signal.SIGKILL, shell=False, **kwargs):
    """Call cmd with an optional timeout in seconds.

    If `timeout` is supplied and expires, the process is killed with
    SIGKILL (kill -9) and an exception is raised. Otherwise, the command
    output is returned.

    If `shell` is False, `shlex.split` is applied to cmd, which itself may have
    been prefixed by a timeout command if a timeout was provided.

    Parameters
    ----------
    cmd : str
        The command to execute.
    timeout : int
        Seconds before kill is issued to the process.
    signum : int
        The signal number to issue to the process on timeout.
    **kwargs
        Keyword arguments are passed through to Popen

    Returns
    -------
    str
        Content of stdout of cmd on success.

    Raises
    ------
        CalledProcessError
            Raised when cmd fails
    """

    output = None
    rc = 0
    try:
        cmd = cmd.encode('utf-8', 'replace')
        if timeout is not None:
            cmd = "timeout -s {0} {1} {2}".format(signum, timeout, cmd)
        if not shell:
            cmd = shlex.split(cmd)
        log.debug(cmd)
        p = subprocess.Popen(cmd, stdout=STDOUT, stderr=STDERR, shell=shell, **kwargs)
        output = p.communicate()[0]
        rc = p.poll()
    except BaseException as e:
        log.exception(e)
        raise CalledProcessError(rc, cmd, str(e)), None, sys.exc_info()[2]
    if rc:
        raise CalledProcessError(rc, cmd, output)
    return output
