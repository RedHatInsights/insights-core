"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import
import os
import six
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

        # only load files, keywords, components into core
        core_blacklist = {
            'commands': rm_conf.get('commands', []),
            'files': rm_conf.get('files', []),
            'components': rm_conf.get('components', [])
        }

        manifest = collect.default_manifest
        if hasattr(self.config, 'manifest') and self.config.manifest:
            if self.config.app is None:
                with open(self.config.manifest, 'r') as f:
                    manifest = f.read()
            else:
                manifest = self.config.manifest
        collected_data_path, exceptions = collect.collect(
            manifest=manifest,
            tmp_path=self.archive.tmp_dir,
            rm_conf=core_blacklist,
            client_timeout=self.config.cmd_timeout
        )

        # update the archive dir with the reported data location from Insights Core
        if not collected_data_path:
            raise RuntimeError('Error running collection: no output path defined.')
        self.archive.archive_dir = collected_data_path
        self.archive.archive_name = os.path.basename(collected_data_path)

        if not six.PY3:
            # collect.py returns a unicode string, and these must be bytestrings
            #   when we call the tar command in 2.6
            self.archive.archive_dir = self.archive.archive_dir.encode('utf-8')
            self.archive.archive_name = self.archive.archive_name.encode('utf-8')

        # set hostname_path for soscleaner
        if os.path.exists(os.path.join(self.archive.archive_dir, 'data', 'insights_commands', 'hostname_-f')):
            self.hostname_path = 'data/insights_commands/hostname_-f'
        else:
            # fall back to hostname if hostname -f not available
            self.hostname_path = 'data/insights_commands/hostname'

        logger.debug('Collection finished.')

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
        logger.debug('Metadata collection finished.')
