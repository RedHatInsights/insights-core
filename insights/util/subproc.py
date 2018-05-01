import logging
import shlex
import signal
import subprocess
from subprocess import Popen
import sys
import six

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


def call(cmd, timeout=None, signum=signal.SIGKILL, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
         keep_rc=False, **kwargs):
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
        if timeout is not None and sys.platform != "darwin":
            cmd = "timeout -s {0} {1} {2}".format(signum, timeout, cmd)

        log.debug(cmd)

        if not shell:
            print(type(cmd), cmd)
            spltcmd = cmd.split("|")
            if len(spltcmd) > 1:
                cmd = shlex.split(spltcmd[0])
                cout = Popen(cmd, stdout=stdout)
                del spltcmd[0]

                for next in spltcmd:
                    nxt = shlex.split(next)
                    cout = Popen(nxt, stdout=stdout, stderr=stderr, stdin=cout.stdout)
            else:
                cmd = shlex.split(spltcmd[0])
                cout = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
        else:
            cout = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell)
        output = cout.communicate()[0]
        rc = cout.poll()
    except Exception as e:
        six.reraise(CalledProcessError, CalledProcessError(rc, cmd, str(e)), sys.exc_info()[2])
    if keep_rc:
        return rc, output
    if rc:
        raise CalledProcessError(rc, cmd, output)
    return output
