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
         keep_rc=False, output_encoding="utf-8", **kwargs):
    """Call cmd with an optional timeout in seconds.

    If `timeout` is supplied and expires, the process is killed with
    SIGKILL (kill -9) and an exception is raised. Otherwise, the command
    output is returned.

    If `shell` is False, `shlex.split` is applied to cmd, which itself may have
    been prefixed by a timeout command if a timeout was provided.

    Parameters
    ----------
    cmd : str or [[stderr]]
        The command(s) to execute.
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
        if not shell:
            if type(cmd) is list:
                command = cmd
                if timeout is not None and sys.platform != "darwin":
                    cmd[0] = ['timeout', '-s', '{0}'.format(signum), '{0}'.format(timeout)] + cmd[0]
                cmd = []
                for cl in command:
                    cmd += [[c.encode('utf-8', 'replace') for c in cl]]
            else:
                if timeout is not None and sys.platform != "darwin":
                    cmd = "timeout -s {0} {1} {2}".format(signum, timeout, cmd)
                command = [shlex.split(cmd)]
                cmd = []
                for cl in command:
                    cmd += [[c.encode('utf-8', 'replace') for c in cl]]

        log.debug(cmd)

        if not shell:
            if len(cmd) > 1:
                cout = Popen(cmd[0], stdout=stdout, **kwargs)
                del cmd[0]

                for next in cmd:
                    cout = Popen(next, stdout=stdout, stderr=stderr, stdin=cout.stdout, **kwargs)
            else:
                cout = Popen(cmd[0], stdout=stdout, stderr=stderr, shell=shell, **kwargs)
        else:
            cout = Popen(cmd, stdout=stdout, stderr=stderr, shell=shell, **kwargs)
        output = cout.communicate()[0]
        rc = cout.poll()
    except Exception as e:
        six.reraise(CalledProcessError, CalledProcessError(rc, cmd, str(e)), sys.exc_info()[2])

    cmd_stdout_str = output.decode(output_encoding, 'ignore') if output_encoding else output

    if keep_rc:
        return rc, cmd_stdout_str
    if rc:
        raise CalledProcessError(rc, cmd, output)
    return cmd_stdout_str
