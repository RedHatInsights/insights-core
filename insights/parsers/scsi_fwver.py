"""
SCSIFWver - file ``/sys/class/scsi_host/host[0-9]*/fwrev``

This parser parses the content from fwver file from individual
SCSI hosts. This parser will return dictionary formated data.

Sample Content from ``/sys/class/scsi_host/host0/fwrev``::

    2.02X12 (U3H2.02X12), sli-3


Sample Output:
    {
        'host0': '2.02X12 (U3H2.02X12), sli-3',
    }

"""

import re
from collections import OrderedDict
from .. import parser, get_active_lines, LegacyItemAccess, CommandParser
from insights.specs import Specs


@parser(Specs.scsi_fwver)
class SCSIFWver(LegacyItemAccess, CommandParser):
    """
    Parse `/sys/class/scsi_host/host[0-9]*/fwrev` file, return a dict
    contain `fwver` scsi host file info. "scsi_host" key is scsi host file
    parse from scsi host file name.

    Properties:
        scsi_host (str): scsi host file name deriver from file path.
    """
    
    def __init__(self, context):
        super(SCSIFWver, self).__init__(context)
        self.data = {}
        self.scsi_host = context.path.rsplit("/")[-2]
    
    def parse_content(self, content):
        for line in get_active_lines(content):
            self.data[self.scsi_host] = line.split(',')

    @property
    def host_mode(self):
        """
        (list) it will return the scsi host modes when set else None.
        """
        return self.data[self.scsi_host]
