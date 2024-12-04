"""
Collect all the interesting data for analysis - Core version
"""
from __future__ import absolute_import

import json
import logging
import os

from itertools import chain

from insights import collect
from insights.client.archive import InsightsArchive
from insights.client.constants import InsightsConstants as constants
from insights.client.utilities import systemd_notify_init_thread, get_version_info, get_tags
from insights.core.blacklist import BLACKLISTED_SPECS

APP_NAME = constants.app_name
logger = logging.getLogger(__name__)


class CoreCollector(object):
    """
    Collectoer for new core-collector
    """
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

    def run_collection(self, rm_conf, branch_info, blacklist_report):
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

    def done(self):
        """
        Do finalization stuff
        """
        if self.config.output_dir:
            return self.archive.archive_dir
        else:
            return self.archive.create_tar_file()
