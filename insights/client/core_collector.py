"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import

import logging

from insights import collect
from insights.client.constants import InsightsConstants as constants
from insights.client.data_collector import DataCollector
from insights.client.utilities import systemd_notify_init_thread

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class CoreCollector(DataCollector):
    """
    Collectoer for new core-collector
    """

    def run_collection(self, rm_conf, branch_info, blacklist_report):
        '''
        Initialize core collection here and generate the
        output directory with collected data.
        '''
        # initialize systemd-notify thread
        systemd_notify_init_thread()

        self.archive.create_archive_dir()

        logger.debug('Beginning to run core collection ...')
        manifest = collect.default_manifest
        if hasattr(self.config, 'manifest') and self.config.manifest:
            if self.config.app is None:
                with open(self.config.manifest, 'r') as f:
                    manifest = f.read()
            else:
                manifest = self.config.manifest

        collect.collect(
            manifest=manifest,
            tmp_path=self.archive.tmp_dir,
            archive_name=self.archive.archive_name,
            rm_conf=rm_conf or {},
            client_config=self.config,
        )
        logger.debug('Core collection finished.')

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
        logger.debug('Metadata collection finished.')
