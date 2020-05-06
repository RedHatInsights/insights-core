"""
Collect all the interesting data for analysis
"""
from __future__ import absolute_import
import os
import json
import logging
import copy
from itertools import chain
from tempfile import NamedTemporaryFile
from insights import collect

from ..contrib.soscleaner import SOSCleaner
from .utilities import get_version_info, systemd_notify_init_thread, get_tags
from .constants import InsightsConstants as constants
from .archive import InsightsArchive

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

    def run_collection(self, rm_conf, branch_info, blacklist_report):
        '''
        Run specs and collect all the data
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
        '''
        # initialize systemd-notify thread
        systemd_notify_init_thread()

        if rm_conf is None:
            rm_conf = {}

        # add tokens to limit regex handling
        #   core parses blacklist for files and commands as regex
        if 'files' in rm_conf:
            for idx, f in enumerate(rm_conf['files']):
                rm_conf['files'][idx] = '^' + f + '$'

        if 'commands' in rm_conf:
            for idx, c in enumerate(rm_conf['commands']):
                rm_conf['commands'][idx] = '^' + c + '$'

        logger.debug('Beginning to run collection...')

        if rm_conf:
            try:
                patterns = rm_conf['patterns']
                # handle the None or empty case of the sub-object
                if 'regex' in patterns and not patterns['regex']:
                    raise LookupError
                logger.warn("WARNING: Skipping patterns defined in blacklist configuration")
            except LookupError:
                logger.debug('Patterns section of blacklist configuration is empty.')

        # Do not load keywords into core because core has its own
        #   keyword-hiding stuff we don't want to use.
        #   Obfuscation to be done in soscleaner later,
        #   so pass in a copy of rm_conf with keywords removed.
        filtered_rm_conf = copy.deepcopy(rm_conf)
        if 'keywords' in filtered_rm_conf:
            del filtered_rm_conf['keywords']

        collected_data_path = collect.collect(tmp_path=self.archive.tmp_dir, rm_conf=filtered_rm_conf, insights_client=True)
        # update the archive object with the reported data location from Insights Core
        self.archive.update(collected_data_path)
        logger.debug('Collection finished.')

        # collect metadata
        logger.debug('Collecting metadata...')
        self._write_branch_info(branch_info)
        self._write_display_name()
        self._write_version_info()
        self._write_tags()
        self._write_blacklist_report(blacklist_report)
        logger.debug('Metadata collection finished.')

        if self.config.obfuscate:
            if rm_conf and rm_conf.get('keywords'):
                logger.warning("WARNING: Skipping keywords defined in blacklist configuration")
            cleaner = SOSCleaner(quiet=True)
            clean_opts = CleanOptions(
                self.config, self.archive.tmp_dir, rm_conf, self.hostname_path)
            cleaner.clean_report(clean_opts, self.archive.archive_dir)
            if clean_opts.keyword_file is not None:
                os.remove(clean_opts.keyword_file.name)
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
            self.hostname_path = hostname_path or 'data/insights_commands/hostname'
        else:
            self.hostname_path = None
