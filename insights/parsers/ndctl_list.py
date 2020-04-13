"""
NdctlListNi - command ``/usr/bin/ndctl list -Ni``
=================================================
"""

from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ndctl_list)
class NdctlListNi(JSONParser):
    """
    Class for parsing the command of ``/usr/bin/ndctl list -Ni``

    Sample output::

        [
            {
                "dev":"namespace1.0",
                "mode":"fsdax",
                "map":"mem",
                "size":811746721792,
                "uuid":"6a7d93f5-60c4-461b-8d19-0409bd323a94",
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
        >>> ndctl_list.blockdev_list
        ['pmem1']
        >>> ndctl_list.get_attr_by_dev('pmem1', 'mode')
        'fsdax'
    """

    @property
    def blockdev_list(self):
        return [item['blockdev'] for item in self.data if 'blockdev' in item]

    def get_attr_by_dev(self, dev_name, attr_name):
        for item in self.data:
            if dev_name == item.get('blockdev', ''):
                return item.get(attr_name, '')
