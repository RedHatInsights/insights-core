import os
import re
import errno
import shlex
import logging
import six
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile
from insights.util import mangle

from constants import InsightsConstants as constants
from config import CONFIG as config

logger = logging.getLogger(__name__)


class InsightsSpec(object):
    '''
    A spec loaded from the uploader.json
    '''
    def __init__(self, spec, exclude):
        # exclusions patterns for this spec
        self.exclude = exclude
        # pattern for spec collection
        self.pattern = spec['pattern'] if spec['pattern'] else None
        # absolute destination inside the archive for this spec
        if 'command' in spec:
            self.archive_path = mangle.mangle_command(spec['command'])
        else:  # 'file'
            self.archive_path = spec['file']


class InsightsCommand(InsightsSpec):
    '''
    A command spec
    '''
    def __init__(self, spec, exclude, mountpoint, target_name):
        InsightsSpec.__init__(self, spec, exclude)
        # substitute mountpoint for collection
        # have to use .replace instead of .format because there are other
        #  braced keys in the collection spec not used here
        self.command = spec['command'].replace(
            '{CONTAINER_MOUNT_POINT}', mountpoint).replace(
            '{DOCKER_IMAGE_NAME}', target_name).replace(
            '{DOCKER_CONTAINER_NAME}', target_name)
        self.mangled_command = self._mangle_command(self.command)
        # have to re-mangle archive path in case there's a pre-command arg
        # Only do this if there is a pre-command in the spec, this preserves
        # the original archive_file_name setting from the spec file
        if "pre-command" in spec:
            self.archive_path = os.path.join(
                os.path.dirname(self.archive_path), self.mangled_command)
        if not six.PY3:
            self.command = self.command.encode('utf-8', 'ignore')
        self.black_list = ['rm', 'kill', 'reboot', 'shutdown']

    def _mangle_command(self, command, name_max=255):
        """
        Mangle the command name, lifted from sos
        """
        mangledname = re.sub(r"^/(usr/|)(bin|sbin)/", "", command)
        mangledname = re.sub(r"[^\w\-\.\/]+", "_", mangledname)
        mangledname = re.sub(r"/", ".", mangledname).strip(" ._-")
        mangledname = mangledname[0:name_max]
        return mangledname

    def get_output(self):
        '''
        Execute a command through system shell. First checks to see if
        the requested command is executable. Returns (returncode, stdout, 0)
        '''
        # all commands should timeout after a long interval so the client does not hang
        # get the command timeout interval
        if 'cmd_timeout' in config:
            timeout_interval = config['cmd_timeout']
        else:
            timeout_interval = constants.default_cmd_timeout

        # prepend native nix 'timeout' implementation
        timeout_command = 'timeout %s %s' % (timeout_interval, self.command)

        cmd = shlex.split(timeout_command)

        # never execute this stuff
        if set.intersection(set(cmd), set(self.black_list)):
            raise RuntimeError("Command Blacklist")

        cmd.extend(shlex.split("/bin/sed -rf " + constants.default_sed_file))

        if self.exclude is not None:
            logger.info("Exclude file: %s", ", ".join('"%s"' % e for e in self.exclude))
            cmd.append("|")
            cmd.extend(shlex.split("/bin/grep -F -v -f {exclude_file}"))

        if self.pattern is not None and len(self.pattern):
            logger.info("Pattern file: %s", ", ".join('"%s"' % p for p in self.pattern))
            cmd.append("|")
            cmd.extend(shlex.split("/bin/grep -F -f {pattern_file}"))

        out = " ".join(cmd).strip()
        logger.info(out)
        return out


class InsightsFile(InsightsSpec):
    '''
    A file spec
    '''
    def __init__(self, spec, exclude, mountpoint, target_name):
        InsightsSpec.__init__(self, spec, exclude)
        # substitute mountpoint for collection
        self.real_path = spec['file'].replace(
            '{CONTAINER_MOUNT_POINT}', mountpoint).replace(
            '{DOCKER_IMAGE_NAME}', target_name).replace(
            '{DOCKER_CONTAINER_NAME}', target_name)
        self.relative_path = spec['file'].replace(
            mountpoint, '', 1).replace(
            '{CONTAINER_MOUNT_POINT}', '').replace(
            '{DOCKER_IMAGE_NAME}', target_name).replace(
            '{DOCKER_CONTAINER_NAME}', target_name)
        self.archive_path = self.archive_path.replace('{EXPANDED_FILE_NAME}', self.relative_path)

    def get_output(self):
        '''
        Get file content, selecting only lines we are interested in
        '''
        if not os.path.isfile(self.real_path):
            logger.debug('File %s does not exist', self.real_path)
            return

        logger.debug('Copying %s to %s with filters %s',
                     self.real_path, self.archive_path, str(self.pattern))

        cmd = []
        cmd.append("/bin/sed")
        cmd.append("-rf")
        cmd.append(constants.default_sed_file)
        cmd.append(self.real_path)

        if self.exclude is not None:
            logger.info("Exclude file: %s", ", ".join('"%s"' % e for e in self.exclude))

            cmd.append("|")
            cmd.extend(shlex.split("/bin/grep -v -F -f {exclude_file}"))

        if self.pattern is not None:
            logger.info("Pattern file: %s", ", ".join('"%s"' % p for p in self.pattern))
            cmd.extend(shlex.split("/bin/grep -F -f {pattern_file}"))

        out = " ".join(cmd).strip()
        logger.info(out)
        return out
