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
from tempfile import NamedTemporaryFile

from insights.core.blacklist import BLACKLISTED_SPECS
from insights.util import mangle
from ..contrib.soscleaner import SOSCleaner
from .utilities import _expand_paths, get_version_info, systemd_notify_init_thread, get_tags
from .constants import InsightsConstants as constants
from .insights_spec import InsightsFile, InsightsCommand
from .archive import InsightsArchive

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)
# python 2.7
SOSCLEANER_LOGGER = logging.getLogger('soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)
# python 2.6
SOSCLEANER_LOGGER = logging.getLogger('insights-client.soscleaner')
SOSCLEANER_LOGGER.setLevel(logging.ERROR)


def _process_content_redaction(filepath, exclude, regex=False):
    '''
    Redact content from a file, based on
    /etc/insights-client/.exp.sed and and the contents of "exclude"

    filepath    file to modify
    exclude     list of strings to redact
    regex       whether exclude is a list of regular expressions

    Returns the file contents with the specified data removed
    '''
    logger.debug('Processing %s...', filepath)

    # password removal
    sedcmd = Popen(['sed', '-rf', constants.default_sed_file, filepath], stdout=PIPE)
    # patterns removal
    if exclude:
        exclude_file = NamedTemporaryFile()
        exclude_file.write("\n".join(exclude).encode('utf-8'))
        exclude_file.flush()
        if regex:
            flag = '-E'
        else:
            flag = '-F'
        grepcmd = Popen(['grep', '-v', flag, '-f', exclude_file.name], stdin=sedcmd.stdout, stdout=PIPE)
        sedcmd.stdout.close()
        stdout, stderr = grepcmd.communicate()
        logger.debug('Process status: %s', grepcmd.returncode)
    else:
        stdout, stderr = sedcmd.communicate()
        logger.debug('Process status: %s', sedcmd.returncode)
    logger.debug('Process stderr: %s', stderr)
    return stdout


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
        self.hostname_path = None

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

        if BLACKLISTED_SPECS:
            self.archive.add_metadata_to_archive(
                json.dumps({"specs": BLACKLISTED_SPECS}), '/blacklisted_specs.txt')

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
        logger.info('Writing RHSM facts to %s...', constants.rhsm_facts_file)
        ips_list = ''
        with open(ip_csv) as fil:
            # create IP list as JSON block with format
            # [
            #   {
            #     original: <original IP>
            #     obfuscated: <obfuscated IP>
            #   }
            # ]

            ips_list = fil.readlines()
            headings = ips_list[0].strip().split(',')
            # set the indices for the IPs
            if 'original' in headings[0].lower():
                # soscleaner 0.4.4, original first
                org = 0
                obf = 1
            else:
                # soscleaner 0.2.2, obfuscated first
                org = 1
                obf = 0

            ip_block = []
            for line in ips_list[1:]:
                ipset = line.strip().split(',')
                ip_block.append(
                    {
                        'original': ipset[org],
                        'obfuscated': ipset[obf]
                    })

        facts = {
            'insights_client.obfuscate_hostname_enabled': self.config.obfuscate_hostname,
            'insights_client.hostname': hashed_fqdn,
            'insights_client.obfuscate_ip_enabled': self.config.obfuscate,
            'insights_client.ips': json.dumps(ip_block)
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
                self.hostname_path = os.path.join(
                    'insights_commands', mangle.mangle_command(c['command']))
            if c['command'] in rm_commands or c.get('symbolic_name') in rm_commands:
                logger.warn("WARNING: Skipping command %s", c['command'])
                BLACKLISTED_SPECS.append(c['symbolic_name'])
            elif self.mountpoint == "/" or c.get("image"):
                cmd_specs = self._parse_command_spec(c, conf['pre_commands'])
                for s in cmd_specs:
                    if s['command'] in rm_commands:
                        logger.warn("WARNING: Skipping command %s", s['command'])
                        BLACKLISTED_SPECS.append(s['symbolic_name'])
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
                BLACKLISTED_SPECS.append(f['symbolic_name'])
            else:
                file_specs = self._parse_file_spec(f)
                for s in file_specs:
                    # filter files post-wildcard parsing
                    if s['file'] in rm_conf.get('files', []):
                        logger.warn("WARNING: Skipping file %s", s['file'])
                        BLACKLISTED_SPECS.append(s['symbolic_name'])
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
                    BLACKLISTED_SPECS.append(g['symbolic_name'])
                else:
                    glob_specs = self._parse_glob_spec(g)
                    for g in glob_specs:
                        if g['file'] in rm_files:
                            logger.warn("WARNING: Skipping file %s", g['file'])
                            BLACKLISTED_SPECS.append(g['symbolic_name'])
                        else:
                            glob_spec = InsightsFile(g, self.mountpoint)
                            self.archive.add_to_archive(glob_spec)
                            collection_stats[g['file']] = {
                                'exec_time': glob_spec.exec_time,
                                'output_size': glob_spec.output_size
                            }
        logger.debug('Spec collection finished.')

        self.redact(rm_conf)

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

    def redact(self, rm_conf):
        '''
        Perform data redaction (password sed command and patterns),
        write data to the archive in place
        '''
        logger.debug('Running content redaction...')

        if not re.match(r'/var/tmp/.+/insights-.+', self.archive.archive_dir):
            # sanity check to make sure we're only modifying
            #   our own stuff in temp
            # we should never get here but just in case
            raise RuntimeError('ERROR: invalid Insights archive temp path')

        if rm_conf is None:
            rm_conf = {}
        exclude = None
        regex = False
        if rm_conf:
            try:
                exclude = rm_conf['patterns']
                if isinstance(exclude, dict) and exclude['regex']:
                    # if "patterns" is a dict containing a non-empty "regex" list
                    logger.debug('Using regular expression matching for patterns.')
                    exclude = exclude['regex']
                    regex = True
                logger.warn("WARNING: Skipping patterns defined in blacklist configuration")
            except LookupError:
                # either "patterns" was undefined in rm conf, or
                #   "regex" was undefined in "patterns"
                exclude = None
        if not exclude:
            logger.debug('Patterns section of blacklist configuration is empty.')

        # TODO: consider implementing redact() in CoreCollector class rather than
        #   special handling here
        if self.config.core_collect:
            # redact only from the 'data' directory
            searchpath = os.path.join(self.archive.archive_dir, 'data')
            if not (os.path.isdir(searchpath) and
                    re.match(r'/var/tmp/.+/insights-.+/data', searchpath)):
                # abort if the dir does not exist and isn't the correct format
                # we should never get here but just in case
                raise RuntimeError('ERROR: invalid Insights archive temp path')
        else:
            searchpath = self.archive.archive_dir

        for dirpath, dirnames, filenames in os.walk(searchpath):
            for f in filenames:
                fullpath = os.path.join(dirpath, f)
                if (fullpath.endswith('etc/insights-client/machine-id') or
                   fullpath.endswith('etc/machine-id') or
                   fullpath.endswith('insights_commands/subscription-manager_identity')):
                    # do not redact the ID files
                    continue
                redacted_contents = _process_content_redaction(fullpath, exclude, regex)
                with open(fullpath, 'wb') as dst:
                    dst.write(redacted_contents)

    def done(self, conf, rm_conf):
        """
        Do finalization stuff

        Returns:
            default:
                path to generated tarfile
            conf.obfuscate==True:
                path to generated tarfile, scrubbed by soscleaner
            conf.output_dir:
                path to a generated directory
            conf.obfuscate==True && conf.output_dir:
                path to generated directory, scubbed by soscleaner
        Ideally, we may want to have separate functions for directories
            and archive files.
        """
        if self.config.obfuscate:
            if rm_conf and rm_conf.get('keywords'):
                logger.warn("WARNING: Skipping keywords defined in blacklist configuration")
            cleaner = SOSCleaner(quiet=True)
            clean_opts = CleanOptions(
                self.config, self.archive.tmp_dir, rm_conf, self.hostname_path)
            cleaner.clean_report(clean_opts, self.archive.archive_dir)
            if clean_opts.keyword_file is not None:
                os.remove(clean_opts.keyword_file.name)

            # generate RHSM facts at this point
            self._write_rhsm_facts(cleaner.hashed_fqdn, cleaner.ip_report)

            if self.config.output_dir:
                # return the entire soscleaner dir
                #   see additions to soscleaner.SOSCleaner.clean_report
                #   for details
                return cleaner.dir_path
            else:
                # return the generated soscleaner archive
                self.archive.tar_file = cleaner.archive_path
                return cleaner.archive_path

        if self.config.output_dir:
            return self.archive.archive_dir
        else:
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
        self.no_tar_file = config.output_dir
        self.core_collect = config.core_collect

        if rm_conf:
            try:
                keywords = rm_conf['keywords']
                self.keyword_file = NamedTemporaryFile(delete=False)
                self.keyword_file.write("\n".join(keywords).encode('utf-8'))
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
