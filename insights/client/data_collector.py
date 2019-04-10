"""
Collect all the interesting data for analysis
"""
from __future__ import absolute_import
import os
import errno
import json
from . import archive
import logging
import copy
import glob
import six
import shlex
from subprocess import Popen, PIPE, STDOUT
from tempfile import NamedTemporaryFile

from insights.util import mangle
from ..contrib.soscleaner import SOSCleaner
from .utilities import _expand_paths
from .constants import InsightsConstants as constants
from .insights_spec import InsightsFile, InsightsCommand

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
# python 2.7
SOSCLEANER_LOGGER = logging.getLogger('soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)
# python 2.6
SOSCLEANER_LOGGER = logging.getLogger('insights-client.soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)


class DataCollector(object):
    '''
    Run commands and collect files
    '''

    def __init__(self, config, archive_=None, mountpoint=None):
        self.config = config
        self.archive = archive_ if archive_ else archive.InsightsArchive()
        self.mountpoint = '/'
        if mountpoint:
            self.mountpoint = mountpoint
        self.hostname_path = None

    def _write_branch_info(self, branch_info):
        logger.debug("Writing branch information to archive...")
        self.archive.add_metadata_to_archive(
            json.dumps(branch_info), '/branch_info')

    def _run_pre_command(self, pre_cmd):
        '''
        Run a pre command to get external args for a command
        '''
        logger.debug('Executing pre-command: %s', pre_cmd)
        try:
            pre_proc = Popen(pre_cmd, stdout=PIPE, stderr=STDOUT, shell=True)
        except OSError as err:
            if err.errno == errno.ENOENT:
                logger.debug('Command %s not found', pre_cmd)
            return
        stdout, stderr = pre_proc.communicate()
        the_return_code = pre_proc.poll()
        logger.debug("Pre-command results:")
        logger.debug("STDOUT: %s", stdout)
        logger.debug("STDERR: %s", stderr)
        logger.debug("Return Code: %s", the_return_code)
        if the_return_code != 0:
            return []
        if six.PY3:
            stdout = stdout.decode('utf-8')
        return stdout.splitlines()

    def _parse_file_spec(self, spec):
        '''
        Separate wildcard specs into more specs
        '''
        # separate wildcard specs into more specs
        if '*' in spec['file']:
            expanded_paths = _expand_paths(spec['file'])
            if not expanded_paths:
                return []
            expanded_specs = []
            for p in expanded_paths:
                _spec = copy.copy(spec)
                _spec['file'] = p
                expanded_specs.append(_spec)
            return expanded_specs

        else:
            return [spec]

    def _parse_glob_spec(self, spec):
        '''
        Grab globs of things
        '''
        some_globs = glob.glob(spec['glob'])
        if not some_globs:
            return []
        el_globs = []
        for g in some_globs:
            _spec = copy.copy(spec)
            _spec['file'] = g
            el_globs.append(_spec)
        return el_globs

    def _blacklist_check(self, cmd):
        def _get_nested_parts(cmd):
            parts = shlex.split(cmd.replace(';', ' '))
            all_parts = parts[:]
            for p in parts:
                if len(shlex.split(p)) > 1:
                    all_parts += _get_nested_parts(p)
            return all_parts

        cmd_parts = _get_nested_parts(cmd)
        return len(set.intersection(set(cmd_parts),
                   constants.command_blacklist)) > 0

    def _parse_command_spec(self, spec, precmds):
        '''
        Run pre_commands
        '''
        if 'pre_command' in spec:
            precmd_alias = spec['pre_command']
            try:
                precmd = precmds[precmd_alias]

                if self._blacklist_check(precmd):
                    raise RuntimeError("Command Blacklist: " + precmd)

                args = self._run_pre_command(precmd)
                logger.debug('Pre-command results: %s', args)

                expanded_specs = []
                for arg in args:
                    _spec = copy.copy(spec)
                    _spec['command'] = _spec['command'] + ' ' + arg
                    expanded_specs.append(_spec)
                return expanded_specs
            except LookupError:
                logger.debug('Pre-command %s not found. Skipping %s...',
                             precmd_alias, spec['command'])
                return []
        else:
            return [spec]

    def run_collection(self, conf, rm_conf, branch_info):
        '''
        Run specs and collect all the data
        '''
        if rm_conf is None:
            rm_conf = {}
        logger.debug('Beginning to run collection spec...')
        exclude = None
        if rm_conf:
            try:
                exclude = rm_conf['patterns']
                logger.warn("WARNING: Skipping patterns found in remove.conf")
            except LookupError:
                logger.debug('Patterns section of remove.conf is empty.')

        for c in conf['commands']:
            # remember hostname archive path
            if c.get('symbolic_name') == 'hostname':
                self.hostname_path = os.path.join(
                    'insights_commands', mangle.mangle_command(c['command']))
            rm_commands = rm_conf.get('commands', [])
            if c['command'] in rm_commands or c.get('symbolic_name') in rm_commands:
                logger.warn("WARNING: Skipping command %s", c['command'])
            elif self.mountpoint == "/" or c.get("image"):
                cmd_specs = self._parse_command_spec(c, conf['pre_commands'])
                for s in cmd_specs:
                    cmd_spec = InsightsCommand(self.config, s, exclude, self.mountpoint)
                    self.archive.add_to_archive(cmd_spec)
        for f in conf['files']:
            rm_files = rm_conf.get('files', [])
            if f['file'] in rm_files or f.get('symbolic_name') in rm_files:
                logger.warn("WARNING: Skipping file %s", f['file'])
            else:
                file_specs = self._parse_file_spec(f)
                for s in file_specs:
                    # filter files post-wildcard parsing
                    if s['file'] in rm_conf.get('files', []):
                        logger.warn("WARNING: Skipping file %s", s['file'])
                    else:
                        file_spec = InsightsFile(s, exclude, self.mountpoint)
                        self.archive.add_to_archive(file_spec)
        if 'globs' in conf:
            for g in conf['globs']:
                glob_specs = self._parse_glob_spec(g)
                for g in glob_specs:
                    if g['file'] in rm_conf.get('files', []):
                        logger.warn("WARNING: Skipping file %s", g)
                    else:
                        glob_spec = InsightsFile(g, exclude, self.mountpoint)
                        self.archive.add_to_archive(glob_spec)
        logger.debug('Spec collection finished.')

        # collect metadata
        logger.debug('Collecting metadata...')
        self._write_branch_info(branch_info)
        logger.debug('Metadata collection finished.')

    def done(self, conf, rm_conf):
        """
        Do finalization stuff
        """
        if self.config.obfuscate:
            cleaner = SOSCleaner(quiet=True)
            clean_opts = CleanOptions(
                self.config, self.archive.tmp_dir, rm_conf, self.hostname_path)
            fresh = cleaner.clean_report(clean_opts, self.archive.archive_dir)
            if clean_opts.keyword_file is not None:
                os.remove(clean_opts.keyword_file.name)
                logger.warn("WARNING: Skipping keywords found in remove.conf")
            return fresh[0]
        return self.archive.create_tar_file()


class CleanOptions(object):
    """
    Options for soscleaner
    """
    def __init__(self, config, tmp_dir, rm_conf, hostname_path):
        self.report_dir = tmp_dir
        self.domains = []
        self.files = []
        self.quiet = True
        self.keyword_file = None
        self.keywords = None

        if rm_conf:
            try:
                keywords = rm_conf['keywords']
                self.keyword_file = NamedTemporaryFile(delete=False)
                self.keyword_file.write("\n".join(keywords))
                self.keyword_file.flush()
                self.keyword_file.close()
                self.keywords = [self.keyword_file.name]
                logger.debug("Attmpting keyword obfuscation")
            except LookupError:
                pass

        if config.obfuscate_hostname:
            # default to its original location
            self.hostname_path = hostname_path or 'insights_commands/hostname'
        else:
            self.hostname_path = None
