"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import
import logging
import os
import six

from datetime import datetime

from insights import collect
from insights.client.constants import InsightsConstants as constants
from insights.client.data_collector import DataCollector
from insights.client.utilities import systemd_notify_init_thread
from insights.util import fs

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

        suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        relative_path = "insights-%s-%s" % (self.hostname, suffix)
        output_path = os.path.join(self.archive.tmp_dir, relative_path)
        fs.ensure_path(output_path)
        fs.touch(os.path.join(output_path, "insights_archive.txt"))

        self.archive.archive_dir = output_path
        self.archive.archive_name = relative_path
        # collect the metadata at first for dependency-ship
        self.collect_metadata(branch_info, blacklist_report)

        collect.collect(
            manifest=manifest,
            tmp_path=self.archive.archive_dir,
            rm_conf=core_blacklist,
            client_timeout=self.config.cmd_timeout
        )

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
        self._write_blacklisted_specs()

    def collect_metadata(self, branch_info, blacklist_report):
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
