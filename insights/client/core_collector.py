"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import
import os
import logging
from insights import collect

from .constants import InsightsConstants as constants
from .data_collector import DataCollector
from .utilities import systemd_notify_init_thread

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class CoreCollector(DataCollector):
    def __init__(self, *args, **kwargs):
        super(CoreCollector, self).__init__(*args, **kwargs)

    def run_collection(self, conf, rm_conf, branch_info, blacklist_report):
        '''
        Initialize core collection here and generate the
        output directory with collected data.
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

        # TODO: load this blacklist into core
        # only load files, keywords, components into core
        core_blacklist = {
            'commands': rm_conf.get('commands', []),
            'files': rm_conf.get('files', []),
            'components': rm_conf.get('components', [])
        }

        collected_data_path = collect.collect(tmp_path=self.archive.tmp_dir)
        # update the archive dir with the reported data location from Insights Core
        if not collected_data_path:
            raise RuntimeError('Error running collection: no output path defined.')
        self.archive.archive_dir = collected_data_path
        self.archive.archive_name = os.path.basename(collected_data_path)
        logger.debug('Collection finished.')

        self.redact(rm_conf)

        # collect metadata
        logger.debug('Collecting metadata...')
        self._write_branch_info(branch_info)
        self._write_display_name()
        self._write_version_info()
        self._write_tags()
        self._write_blacklist_report(blacklist_report)
        logger.debug('Metadata collection finished.')
