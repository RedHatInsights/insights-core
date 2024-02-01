"""
Collect all the interesting data for analysis
"""
from __future__ import absolute_import
import copy
import errno
import glob
import json
import logging
import os
import shlex
import six

from itertools import chain
from subprocess import Popen, PIPE, STDOUT

from insights.client.archive import InsightsArchive
from insights.client.constants import InsightsConstants as constants
from insights.client.insights_spec import InsightsFile, InsightsCommand
from insights.client.utilities import (_expand_paths, get_version_info,
                                       systemd_notify_init_thread, get_tags)
from insights.core.blacklist import BLACKLISTED_SPECS
from insights.core.dr import get_component_by_name
from insights.core.spec_cleaner import Cleaner

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class DataCollector(object):
    '''
    Run commands and collect files
    '''

    def __init__(self, config, archive_=None, mountpoint=None, spec_conf=None):
        self.config = config
        self.archive = archive_ if archive_ else InsightsArchive(config)
        self.mountpoint = mountpoint if mountpoint else '/'
        self.spec_conf = spec_conf if spec_conf else {}

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
        tags = get_tags()
        # NOTE:
        # The following code is also used by datasource 'tags'
        # - insights.specs.datasources.tags
        # Please keep them consistence before removing this.
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
            logger.debug("Writing tags to archive...")
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

    def _write_blacklisted_specs(self):
        if BLACKLISTED_SPECS:
            logger.debug("Writing blacklisted specs to archive...")
            self.archive.add_metadata_to_archive(
                json.dumps({"specs": BLACKLISTED_SPECS}), '/blacklisted_specs')

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

    def _write_rhsm_facts(self, hashed_fqdn, ip_csv):
        logger.info('Writing RHSM facts to %s ...', constants.rhsm_facts_file)

        hn_block = []
        for k, v in self.hn_db.items():
            hn_block.append({'original': k, 'obfuscated': v})

        kw_block = []
        for k, v in self.kw_db.items():
            kw_block.append({'original': k, 'obfuscated': v})

        ip_block = []
        for k, v in self.ip_db.items():
            ip_block.append(
                {
                    'original': self._int2ip(v),
                    'obfuscated': self._int2ip(k)
                })

        facts = {
            'insights_client.hostname': self.obfuscated_fqdn,
            'insights_client.obfuscate_ip_enabled': 'ip' in self.obfuscate,
            'insights_client.ips': json.dumps(ip_block),
            'insights_client.obfuscate_hostname_enabled': 'hostname' in self.obfuscate,
            'insights_client.hostnames': json.dumps(hn_block),
            'insights_client.keywords': json.dumps(kw_block),
        }

        try:
            with open(constants.rhsm_facts_file, 'w') as fil:
                json.dump(facts, fil)
        except (IOError, OSError) as e:
            logger.error('Could not write to %s: %s', constants.rhsm_facts_file, str(e))

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

    def run_collection(self, rm_conf, branch_info, blacklist_report):
        '''
        Run specs and collect all the data
        '''
        def _get_spec_info(symbolic_name):
            if symbolic_name:
                symbolic_comp = get_component_by_name('insights.specs.Specs.{0}'.format(symbolic_name))
                if symbolic_comp:
                    return symbolic_comp.no_obfuscate, symbolic_comp.no_redact
            return [], False

        # initialize systemd-notify thread
        systemd_notify_init_thread()

        self.archive.create_archive_dir()
        self.archive.create_command_dir()

        collection_stats = {}

        logger.debug('Beginning to run spec collection ...')

        rm_conf = rm_conf or {}
        cleaner = Cleaner(self.config, rm_conf)
        rm_commands = rm_conf.get('commands', [])
        rm_files = rm_conf.get('files', [])

        for c in self.spec_conf['commands']:
            symbolic_name = c.get('symbolic_name')
            command = c.get('command')
            spec_info = _get_spec_info(symbolic_name)
            if command in rm_commands or symbolic_name in rm_commands:
                logger.warn("WARNING: Skipping command %s", command)
                BLACKLISTED_SPECS.append(symbolic_name)
            elif self.mountpoint == "/" or c.get("image"):
                cmd_specs = self._parse_command_spec(c, self.spec_conf['pre_commands'])
                for s in cmd_specs:
                    if s['command'] in rm_commands:
                        logger.warn("WARNING: Skipping command %s", s['command'])
                        BLACKLISTED_SPECS.append(s['symbolic_name'])
                        continue
                    cmd_spec = InsightsCommand(self.config, s, self.mountpoint)
                    self.archive.add_to_archive(cmd_spec, cleaner, spec_info)
                    collection_stats[s['command']] = {
                        'return_code': cmd_spec.return_code,
                        'exec_time': cmd_spec.exec_time,
                        'output_size': cmd_spec.output_size
                    }
        for f in self.spec_conf['files']:
            symbolic_name = f.get('symbolic_name')
            spec_info = _get_spec_info(symbolic_name)
            if f['file'] in rm_files or symbolic_name in rm_files:
                logger.warn("WARNING: Skipping file %s", f['file'])
                BLACKLISTED_SPECS.append(symbolic_name)
            else:
                file_specs = self._parse_file_spec(f)
                for s in file_specs:
                    # filter files post-wildcard parsing
                    if s['file'] in rm_files:
                        logger.warn("WARNING: Skipping file %s", s['file'])
                        BLACKLISTED_SPECS.append(s['symbolic_name'])
                    else:
                        file_spec = InsightsFile(s, self.mountpoint)
                        self.archive.add_to_archive(file_spec, cleaner, spec_info)
                        collection_stats[s['file']] = {
                            'exec_time': file_spec.exec_time,
                            'output_size': file_spec.output_size
                        }
        if 'globs' in self.spec_conf:
            for g in self.spec_conf['globs']:
                symbolic_name = g.get('symbolic_name')
                spec_info = _get_spec_info(symbolic_name)
                if symbolic_name in rm_files:
                    # ignore glob via symbolic name
                    logger.warn("WARNING: Skipping file %s", g['glob'])
                    BLACKLISTED_SPECS.append(symbolic_name)
                else:
                    glob_specs = self._parse_glob_spec(g)
                    for s in glob_specs:
                        if s['file'] in rm_files:
                            logger.warn("WARNING: Skipping file %s", s['file'])
                            BLACKLISTED_SPECS.append(s['symbolic_name'])
                        else:
                            glob_spec = InsightsFile(s, self.mountpoint)
                            self.archive.add_to_archive(glob_spec, cleaner, spec_info)
                            collection_stats[s['file']] = {
                                'exec_time': glob_spec.exec_time,
                                'output_size': glob_spec.output_size
                            }
        cleaner.generate_report(self.archive.archive_name, constants.rhsm_facts_file)
        logger.debug('Spec collection finished.')

        # collect metadata
        logger.debug('Collecting metadata ...')
        self._write_branch_info(branch_info)
        self._write_display_name()
        self._write_ansible_host()
        self._write_version_info()
        self._write_tags()
        self._write_blacklist_report(blacklist_report)
        self._write_blacklisted_specs()
        self._write_egg_release()
        self._write_collection_stats(collection_stats)
        logger.debug('Metadata collection finished.')

    def done(self):
        """
        Do finalization stuff
        """
        if self.config.output_dir:
            return self.archive.archive_dir
        else:
            return self.archive.create_tar_file()
