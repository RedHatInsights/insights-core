"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import

import logging

from insights import collect

from insights.client.archive import InsightsArchive
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import systemd_notify_init_thread

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class CoreCollector(object):
    """
    Collector for new core-collector
    """

    def __init__(self, config, archive_=None, mountpoint=None, spec_conf=None):
        self.config = config
        self.archive = archive_ if archive_ else InsightsArchive(config)
        self.mountpoint = mountpoint if mountpoint else '/'
        self.spec_conf = spec_conf if spec_conf else {}

    def run_collection(self, rm_conf, branch_info, blacklist_report):
        '''
        Initialize core collection here and generate the
        output directory with collected data.
        '''
        # initialize systemd-notify thread
        systemd_notify_init_thread()

        self.archive.create_archive_dir()
        self.archive.create_command_dir()

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

    def done(self):
        """
        Do finalization stuff
        """
        if self.config.output_dir:
            return self.archive.archive_dir
        else:
            return self.archive.create_tar_file()
