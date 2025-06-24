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
    Collector for core collection
    """

    def __init__(self, config):
        self.config = config
        self.archive = InsightsArchive(config)

    def run_collection(self, rm_conf):
        '''
        Initialize core collection here and generate the
        output directory with collected data.
        '''
        # initialize systemd-notify thread
        systemd_notify_init_thread()

        self.archive.create_archive_dir()

        logger.debug('Beginning to run core collection ...')

        self.config.rhsm_facts_file = constants.rhsm_facts_file
        collect.collect(
            tmp_path=self.archive.tmp_dir,
            archive_name=self.archive.archive_name,
            rm_conf=rm_conf or {},
            client_config=self.config,
        )

        logger.debug('Core collection finished.')

        # About "metadata":
        #  The following metadata is now collected by core collection when
        #  available, and will be stored under the "./data" directory instead
        #  of the root of the archive.
        #
        #   ansible_host = client_metadata.ansible_host
        #   blacklist_report = client_metadata.blacklist_report
        #   blacklisted_specs = client_metadata.blacklisted_specs
        #   branch_info = client_metadata.branch_info
        #   display_name = client_metadata.display_name
        #   egg_release = client_metadata.egg_release
        #   tags = client_metadata.tags
        #   version_info = client_metadata.version_info
        #
        #  See `insights.specs.datasources.client_metadata`

    def done(self):
        """
        Do finalization stuff
        """
        if self.config.output_dir:
            return self.archive.archive_dir
        else:
            return self.archive.create_tar_file()
