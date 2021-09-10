"""
Collect all the interesting data for analysis
"""
from __future__ import absolute_import
import os
import errno
import json
import logging
import copy
import glob
import six
import shlex
import re
from itertools import chain
from subprocess import Popen, PIPE, STDOUT

from insights.util import mangle
from .utilities import _expand_paths, get_version_info, systemd_notify_init_thread, get_tags
from .constants import InsightsConstants as constants
from .insights_spec import InsightsFile, InsightsCommand
from .archive import InsightsArchive

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class DataCollector(object):
    '''
    Run commands and collect files
    '''

    def __init__(self, config, archive_=None, mountpoint=None):
        self.config = config
        self.archive = archive_ if archive_ else InsightsArchive(config)
        self.mountpoint = '/'
        if mountpoint:
            self.mountpoint = mountpoint

    def _write_branch_info(self, branch_info):
        logger.debug("Writing branch information to archive...")
        self.archive.add_metadata_to_archive(
            json.dumps(branch_info), '/branch_info')

    def _write_display_name(self):
        if self.config.display_name:
            logger.debug("Writing display_name to archive...")
            self.archive.add_metadata_to_archive(
                self.config.display_name, '/display_name')

    def _write_ansible_host(self):
        if self.config.ansible_host:
            logger.debug("Writing ansible_host to archive...")
            self.archive.add_metadata_to_archive(
                self.config.ansible_host, '/ansible_host')

    def _write_version_info(self):
        logger.debug("Writing version information to archive...")
        version_info = get_version_info()
        self.archive.add_metadata_to_archive(
            json.dumps(version_info), '/version_info')

    def _write_tags(self):
        logger.debug("Writing tags to archive...")
        tags = get_tags()
        if tags is not None:
            def f(k, v):
                if type(v) is list:
                    col = []
                    for val in v:
                        col.append(f(k, val))
                    return list(chain.from_iterable(col))
                elif type(v) is dict:
                    col = []
                    for key, val in v.items():
                        col.append(f(k + ":" + key, val))
                    return list(chain.from_iterable(col))
                else:
                    return [{"key": k, "value": v, "namespace": constants.app_name}]
            t = []
            for k, v in tags.items():
                iv = f(k, v)
                t.append(iv)
            t = list(chain.from_iterable(t))
            self.archive.add_metadata_to_archive(json.dumps(t), '/tags.json')

    def _write_blacklist_report(self, blacklist_report):
        logger.debug("Writing blacklist report to archive...")
        self.archive.add_metadata_to_archive(
            json.dumps(blacklist_report), '/blacklist_report')

    def _write_egg_release(self):
        logger.debug("Writing egg release to archive...")
        egg_release = ''
        try:
            with open(constants.egg_release_file) as fil:
                egg_release = fil.read()
        except (IOError, MemoryError) as e:
            logger.debug('Could not read the egg release file: %s', str(e))
        try:
            os.remove(constants.egg_release_file)
        except OSError as e:
            logger.debug('Could not remove the egg release file: %s', str(e))

        try:
            self.archive.add_metadata_to_archive(
                egg_release, '/egg_release')
        except OSError as e:
            logger.debug('Could not add the egg release file to the archive: %s', str(e))
            self.archive.add_metadata_to_archive(
                '', '/egg_release')

    def _write_collection_stats(self, collection_stats):
        logger.debug("Writing collection stats to archive...")
        self.archive.add_metadata_to_archive(
            json.dumps(collection_stats), '/collection_stats')

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

    def run_collection(self, conf, rm_conf, branch_info, blacklist_report):
        '''
        Run specs and collect all the data
        '''
        # initialize systemd-notify thread
        systemd_notify_init_thread()

        self.archive.create_archive_dir()
        self.archive.create_command_dir()

        collection_stats = {}

        if rm_conf is None:
            rm_conf = {}
        logger.debug('Beginning to run collection spec...')

        rm_commands = rm_conf.get('commands', [])
        rm_files = rm_conf.get('files', [])

        for c in conf['commands']:
            # remember hostname archive path
            if c.get('symbolic_name') == 'hostname':
                self.archive.hostname_path = os.path.join(
                    'insights_commands', mangle.mangle_command(c['command']))
            if c['command'] in rm_commands or c.get('symbolic_name') in rm_commands:
                logger.warn("WARNING: Skipping command %s", c['command'])
            elif self.mountpoint == "/" or c.get("image"):
                cmd_specs = self._parse_command_spec(c, conf['pre_commands'])
                for s in cmd_specs:
                    if s['command'] in rm_commands:
                        logger.warn("WARNING: Skipping command %s", s['command'])
                        continue
                    cmd_spec = InsightsCommand(self.config, s, self.mountpoint)
                    self.archive.add_to_archive(cmd_spec)
                    collection_stats[s['command']] = {
                        'return_code': cmd_spec.return_code,
                        'exec_time': cmd_spec.exec_time,
                        'output_size': cmd_spec.output_size
                    }
        for f in conf['files']:
            if f['file'] in rm_files or f.get('symbolic_name') in rm_files:
                logger.warn("WARNING: Skipping file %s", f['file'])
            else:
                file_specs = self._parse_file_spec(f)
                for s in file_specs:
                    # filter files post-wildcard parsing
                    if s['file'] in rm_conf.get('files', []):
                        logger.warn("WARNING: Skipping file %s", s['file'])
                    else:
                        file_spec = InsightsFile(s, self.mountpoint)
                        self.archive.add_to_archive(file_spec)
                        collection_stats[s['file']] = {
                            'exec_time': file_spec.exec_time,
                            'output_size': file_spec.output_size
                        }
        if 'globs' in conf:
            for g in conf['globs']:
                if g.get('symbolic_name') in rm_files:
                    # ignore glob via symbolic name
                    logger.warn("WARNING: Skipping file %s", g['glob'])
                else:
                    glob_specs = self._parse_glob_spec(g)
                    for g in glob_specs:
                        if g['file'] in rm_files:
                            logger.warn("WARNING: Skipping file %s", g['file'])
                        else:
                            glob_spec = InsightsFile(g, self.mountpoint)
                            self.archive.add_to_archive(glob_spec)
                            collection_stats[g['file']] = {
                                'exec_time': glob_spec.exec_time,
                                'output_size': glob_spec.output_size
                            }
        logger.debug('Spec collection finished.')

        # collect metadata
        logger.debug('Collecting metadata...')
        self._write_branch_info(branch_info)
        self._write_display_name()
        self._write_ansible_host()
        self._write_version_info()
        self._write_tags()
        self._write_blacklist_report(blacklist_report)
        self._write_egg_release()
        self._write_collection_stats(collection_stats)
        logger.debug('Metadata collection finished.')

    def done(self):
        return self.archive.create_tar_file()
