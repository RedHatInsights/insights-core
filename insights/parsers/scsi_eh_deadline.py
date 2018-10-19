"""
SCSIEhDead - file ``/sys/class/scsi_host/host[0-9]*/eh_deadline``
=================================================================

This parser parses the content from eh_deadline file from
individual SCSI hosts. This parser will return data in
dictionary format.

Sample content from ``/sys/class/scsi_host/host0/eh_deadline``::

    off/10/-1/0

Examples:
    >>> type(scsi_obj0)
    <class 'insights.parsers.scsi_eh_deadline.SCSIEhDead'>
    >>> scsi_obj0.data
    {'host0': 'off'}
    >>> scsi_obj0.scsi_host
    'host0'
    >>> type(scsi_obj1)
    <class 'insights.parsers.scsi_eh_deadline.SCSIEhDead'>
    >>> scsi_obj1.data
    {'host1': '10'}
    >>> scsi_obj1.scsi_host
    'host1'
    >>> type(scsi_obj2)
    <class 'insights.parsers.scsi_eh_deadline.SCSIEhDead'>
    >>> scsi_obj2.data
    {'host2': '-1'}
    >>> scsi_obj2.scsi_host
    'host2'

"""

from insights import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.scsi_eh_deadline)
class SCSIEhDead(LegacyItemAccess, Parser):
    """
    Parse `/sys/class/scsi_host/host[0-9]*/eh_deadline` file, return a dict
    contain `eh_deadline` scsi host file info. "scsi_host" key is scsi host file
    parse from scsi host file name.

    Properties:
        scsi_host (str): scsi host file name derived from file path.
    """

    def __init__(self, context):
        self.data = {}
        self.scsi_host = context.path.rsplit("/")[-2]
        super(SCSIEhDead, self).__init__(context)

    def parse_content(self, content):
        for line in get_active_lines(content):
            self.data[self.scsi_host] = line

    @property
    def host_eh_deadline(self):
        """
        (list): It will return the scsi host modes when set else `None`.
        """
        return self.data[self.scsi_host]
