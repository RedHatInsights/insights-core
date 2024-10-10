"""
FindmntPropagation - command ``findmnt -lo+PROPAGATION``
========================================================

This module provides status of propagation flag of filesystems using the output
of command ``findmnt -lo+PROPAGATION``.
"""
from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import keyword_search, parse_fixed_table
from insights.specs import Specs


@parser(Specs.findmnt_lo_propagation)
class FindmntPropagation(CommandParser):
    """Parse output of ``findmnt -lo+PROPAGATION``.

    Typical output of ``findmnt -lo+PROPAGATION`` command is::

        TARGET                                                          SOURCE                                FSTYPE          OPTIONS                                                                       PROPAGATION
        /sys                                                            sysfs                                 sysfs           rw,nosuid,nodev,noexec,relatime,seclabel                                      shared
        /proc                                                           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
        /dev                                                            devtmpfs                              devtmpfs        rw,nosuid,seclabel,size=8035516k,nr_inodes=2008879,mode=755                   shared
        /sys/kernel/security                                            securityfs                            securityfs      rw,nosuid,nodev,noexec,relatime                                               shared
        /dev/shm                                                        tmpfs                                 tmpfs           rw,nosuid,nodev,seclabel                                                      shared
        /run/netns                                                      tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             shared
        /netns                                                          tmpfs[/netns]                         tmpfs           rw,nosuid,nodev,seclabel,mode=755                                             shared
        /run/netns/qdhcp-08f32dab-927e-4a61-933d-57d425827b57           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared
        /run/netns/qdhcp-fd138c0a-5ec7-44f8-88df-0501c4c7a968           proc                                  proc            rw,nosuid,nodev,noexec,relatime                                               shared


    Examples:

        >>> output.search_target('shm') == [{'target': '/dev/shm', 'source': 'tmpfs', 'fstype': 'tmpfs', 'options': 'rw,nosuid,nodev,seclabel', 'propagation': 'shared'}]
        True
        >>> len(output.target_startswith('/run/netns')) == 3
        True
        >>> output.target_startswith('/run/netns')[0].get('propagation', None) == 'shared'
        True

    Attributes:
        cols (list): List of key value pair derived from the command.

        keywords (list): keywords(or TARGETs) present in the command
    """
    def parse_content(self, content):
        self.cols = []
        self.keywords = []
        if not content:
            raise SkipComponent("No data.")

        self.cols = parse_fixed_table(content,
                                      header_substitute=[
                                          ('TARGET', 'target'),
                                          ('SOURCE', 'source'),
                                          ('FSTYPE', 'fstype'),
                                          ('OPTIONS', 'options'),
                                          ('PROPAGATION', 'propagation')])
        self.keywords = [col['target'] for col in self.cols]

    def search_target(self, target):
        """Similar to __contains__() but returns the list of targets.

        Example:

            >>> output.search_target('shm') == [{'target': '/dev/shm', 'source': 'tmpfs', 'fstype': 'tmpfs', 'options': 'rw,nosuid,nodev,seclabel', 'propagation': 'shared'}]
            True
        """
        return keyword_search(self.cols, parent=self, target__contains=target)

    def target_startswith(self, target):
        """Return all the targets that starts with 'target'. Useful to find the mountpoints.

        Example:

            >>> len(output.target_startswith('/run/netns')) == 3
            True
        """
        return keyword_search(self.cols, parent=self, target__startswith=target)
