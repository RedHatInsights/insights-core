from __future__ import absolute_import
import os
import errno
import shlex
import logging
import six
import time
import sys
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from insights.util import mangle, which

from .constants import InsightsConstants as constants
from .utilities import determine_hostname

logger = logging.getLogger(__name__)


class InsightsSpec(object):
    '''
    A spec loaded from the uploader.json
    '''
    def __init__(self, config, spec):
        self.config = config
        self.pattern = spec['pattern'] if spec['pattern'] else None
        self.return_code = None
        self.exec_time = None
        self.output_size = None


class InsightsCommand(InsightsSpec):
    '''
    A command spec
    '''
    def __init__(self, config, spec, mountpoint):
        super(InsightsCommand, self).__init__(config, spec)
        self.command = spec['command'].replace(
            '{CONTAINER_MOUNT_POINT}', mountpoint)
        self.archive_path = mangle.mangle_command(self.command)
        self.is_hostname = spec.get('symbolic_name') == 'hostname'
        if not six.PY3:
            self.command = self.command.encode('utf-8', 'ignore')

    def get_output(self):
        '''
        Execute a command through system shell. First checks to see if
        the requested command is executable. Returns (returncode, stdout, 0)
        '''
        if self.is_hostname:
            # short circuit for hostame with internal method
            return determine_hostname()

        # all commands should timeout after a long interval so the client does not hang
        # prepend native nix 'timeout' implementation

        # use TERM for rpm/yum commands, KILL for everything else
        if (self.command.startswith('/bin/rpm') or
           self.command.startswith('dnf') or
           self.command.startswith('/bin/dnf') or
           self.command.startswith('/usr/bin/dnf') or
           self.command.startswith('yum') or
           self.command.startswith('/usr/bin/yum')):
            signal = 'TERM'
        else:
            signal = 'KILL'

        # ensure consistent locale for collected command output
        cmd_env = {'LC_ALL': 'C',
                   'PATH': '/sbin:/bin:/usr/sbin:/usr/bin',
                   'PYTHONPATH': os.getenv('PYTHONPATH')}

        timeout = which('timeout', env=cmd_env)
        timeout_command = '%s -s %s %s %s' % (
            timeout, signal, self.config.cmd_timeout, self.command)

        args = shlex.split(timeout_command)

        # never execute this stuff
        if set.intersection(set(args), constants.command_blacklist):
            raise RuntimeError("Command Blacklist: " + self.command)

        exec_start = time.time()
        try:
            logger.debug('Executing: %s', args)
            proc0 = Popen(args, shell=False, stdout=PIPE, stderr=STDOUT,
                          bufsize=-1, env=cmd_env, close_fds=True)
        except OSError as err:
            if err.errno == errno.ENOENT:
                logger.debug('Command %s not found', self.command)
                return
            else:
                raise err

        if proc0.returncode == 126 or proc0.returncode == 127:
            stdout = "Could not find cmd: %s", self.command

        dirty = False

        if self.pattern is not None and len(self.pattern):
            pattern_file = NamedTemporaryFile()
            pattern_file.write("\n".join(self.pattern).encode('utf-8'))
            pattern_file.flush()
            cmd = "grep -F -f %s" % pattern_file.name
            proc2 = Popen(shlex.split(cmd),
                          stdin=proc0.stdout,
                          stdout=PIPE)
            proc0.stdout.close()
            stdout, stderr = proc2.communicate()

            # always log return codes for debug
            logger.debug('Proc2 Status: %s', proc2.returncode)
            logger.debug('Proc2 stderr: %s', stderr)
            proc0 = proc2

            dirty = True

        if not dirty:
            stdout, stderr = proc0.communicate()

        logger.debug("Proc0 Status: %s", proc0.returncode)
        logger.debug("Proc0 stderr: %s", stderr)
        self.return_code = proc0.returncode
        self.exec_time = time.time() - exec_start
        self.output_size = sys.getsizeof(stdout)
        return stdout.decode('utf-8', 'ignore').strip()


class InsightsFile(InsightsSpec):
    '''
    A file spec
    '''
    def __init__(self, spec, mountpoint):
        super(InsightsFile, self).__init__(None, spec)
        # substitute mountpoint for collection
        self.real_path = os.path.join(mountpoint, spec['file'].lstrip('/'))
        self.archive_path = spec['file']

    def get_output(self):
        '''
        Get file content, selecting only lines we are interested in
        '''
        if not os.path.isfile(self.real_path):
            logger.debug('File %s does not exist', self.real_path)
            return

        exec_start = time.time()
        sedcmd = Popen(['sed', '', self.real_path], stdout=PIPE)

        if self.pattern is None:
            output = sedcmd.communicate()[0]
        else:
            pattern_file = NamedTemporaryFile()
            pattern_file.write("\n".join(self.pattern).encode('utf-8'))
            pattern_file.flush()

            cmd = "grep -F -f %s" % pattern_file.name
            args = shlex.split(cmd)
            proc1 = Popen(args, stdin=sedcmd.stdout, stdout=PIPE)
            sedcmd.stdout.close()

            output = proc1.communicate()[0]
        self.exec_time = time.time() - exec_start
        self.output_size = sys.getsizeof(output)
        return output.decode('utf-8', 'ignore').strip()
