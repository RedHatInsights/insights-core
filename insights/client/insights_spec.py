from __future__ import absolute_import
import os
import errno
import shlex
import logging
import six
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from insights.util import mangle

from .constants import InsightsConstants as constants
from .utilities import determine_hostname

logger = logging.getLogger(__name__)


class InsightsSpec(object):
    '''
    A spec loaded from the uploader.json
    '''
    def __init__(self, config, spec, exclude):
        self.config = config
        # exclusions patterns for this spec
        self.exclude = exclude
        # pattern for spec collection
        self.pattern = spec['pattern'] if spec['pattern'] else None


class InsightsCommand(InsightsSpec):
    '''
    A command spec
    '''
    def __init__(self, config, spec, exclude, mountpoint):
        InsightsSpec.__init__(self, config, spec, exclude)
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
        timeout_command = 'timeout -s KILL %s %s' % (
            self.config.cmd_timeout, self.command)

        # ensure consistent locale for collected command output
        cmd_env = {'LC_ALL': 'C'}
        args = shlex.split(timeout_command)

        # never execute this stuff
        if set.intersection(set(args), constants.command_blacklist):
            raise RuntimeError("Command Blacklist: " + self.command)

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

        dirty = False

        cmd = "sed -rf " + constants.default_sed_file
        sedcmd = Popen(shlex.split(cmd),
                       stdin=proc0.stdout,
                       stdout=PIPE)
        proc0.stdout.close()
        proc0 = sedcmd

        if self.exclude is not None:
            exclude_file = NamedTemporaryFile()
            exclude_file.write("\n".join(self.exclude).encode('utf-8'))
            exclude_file.flush()
            cmd = "grep -F -v -f %s" % exclude_file.name
            proc1 = Popen(shlex.split(cmd),
                          stdin=proc0.stdout,
                          stdout=PIPE)
            proc0.stdout.close()
            stderr = None
            if self.pattern is None or len(self.pattern) == 0:
                stdout, stderr = proc1.communicate()

            # always log return codes for debug
            logger.debug('Proc1 Status: %s', proc1.returncode)
            logger.debug('Proc1 stderr: %s', stderr)
            proc0 = proc1

            dirty = True

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

        # Required hack while we still pass shell=True to Popen; a Popen
        # call with shell=False for a non-existant binary will raise OSError.
        if proc0.returncode == 126 or proc0.returncode == 127:
            stdout = "Could not find cmd: %s", self.command

        logger.debug("Proc0 Status: %s", proc0.returncode)
        logger.debug("Proc0 stderr: %s", stderr)
        return stdout.decode('utf-8', 'ignore').strip()


class InsightsFile(InsightsSpec):
    '''
    A file spec
    '''
    def __init__(self, spec, exclude, mountpoint):
        InsightsSpec.__init__(self, None, spec, exclude)
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

        cmd = []
        cmd.append('sed')
        cmd.append('-rf')
        cmd.append(constants.default_sed_file)
        cmd.append(self.real_path)
        sedcmd = Popen(cmd,
                       stdout=PIPE)

        if self.exclude is not None:
            exclude_file = NamedTemporaryFile()
            exclude_file.write("\n".join(self.exclude).encode('utf-8'))
            exclude_file.flush()

            cmd = "grep -v -F -f %s" % exclude_file.name
            args = shlex.split(cmd)
            proc = Popen(args, stdin=sedcmd.stdout, stdout=PIPE)
            sedcmd.stdout.close()
            stdin = proc.stdout
            if self.pattern is None:
                output = proc.communicate()[0]
            else:
                sedcmd = proc

        if self.pattern is not None:
            pattern_file = NamedTemporaryFile()
            pattern_file.write("\n".join(self.pattern).encode('utf-8'))
            pattern_file.flush()

            cmd = "grep -F -f %s" % pattern_file.name
            args = shlex.split(cmd)
            proc1 = Popen(args, stdin=sedcmd.stdout, stdout=PIPE)
            sedcmd.stdout.close()

            if self.exclude is not None:
                stdin.close()

            output = proc1.communicate()[0]

        if self.pattern is None and self.exclude is None:
            output = sedcmd.communicate()[0]

        return output.decode('utf-8', 'ignore').strip()
