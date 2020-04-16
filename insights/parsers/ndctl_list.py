"""
Dump the platform nvdimm device topology and attributes in json
===============================================================

This module contains the following parsers:

NdctlListNi - command ``/usr/bin/ndctl list -Ni``
=================================================
"""

from insights.core import JSONParser, CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ndctl_list_Ni)
class NdctlListNi(JSONParser, CommandParser):
    """
    Class for parsing the command of ``/usr/bin/ndctl list -Ni``

    Sample output::

        [
            {
                "dev":"namespace1.0",
                "mode":"fsdax",
                "map":"mem",
                "size":811746721792,
                "uuid":"6a5d93a5-6044-461b-8d19-0409bd323a94",
                "sector_size":512,
                "align":2097152,
                "blockdev":"pmem1"
            },
            {
                "dev":"namespace1.1",
                "mode":"raw",
                "size":0,
                "uuid":"00000000-0000-0000-0000-000000000000",
                "sector_size":512,
                "state":"disabled"
            },
            {
                "dev":"namespace0.0",
                "mode":"raw",
                "size":0,
                "uuid":"00000000-0000-0000-0000-000000000000",
                "sector_size":512,
                "state":"disabled"
            }
        ]

    Examples:

        >>> type(ndctl_list)
        <class 'insights.parsers.ndctl_list.NdctlListNi'>
        >>> 'pmem1' in ndctl_list.blockdev_list
        True
        >>> ndctl_list.get_blockdev('pmem1').get('mode') == 'fsdax'
        True
    """

    def parse_content(self, content):
        super(NdctlListNi, self).parse_content(content)
        self._blockdevs = [item['blockdev'] for item in self.data if 'blockdev' in item]

    @property
    def blockdev_list(self):
        """ Return a list of the blockdev attribute of all the devices if it has the attribute"""
        return self._blockdevs

    def get_blockdev(self, dev_name):
        """
        Return a dict of the block device info

        Args:
            dev_name (str): the blockdev name

        Returns:
            dict: return a dict with all the info if there is the block device else empty dict

        """
        for item in self.data:
            if item.get('blockdev', '') == dev_name:
                return item
        return {}
