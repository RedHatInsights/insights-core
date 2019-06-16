#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
SCSIFWver - file ``/sys/class/scsi_host/host[0-9]*/fwrev``
==========================================================

This parser parses the content from fwver file from individual
SCSI hosts. This parser will return data in dictionary format.

Sample Content from ``/sys/class/scsi_host/host0/fwrev``::

    2.02X12 (U3H2.02X12), sli-3


Examples:
    >>> type(scsi_obj)
    <class 'insights.parsers.scsi_fwver.SCSIFWver'>
    >>> scsi_obj.data
    {'host0': ['2.02X12 (U3H2.02X12)', 'sli-3']}
    >>> scsi_obj.scsi_host
    'host0'
"""

from insights import Parser, parser, get_active_lines, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.scsi_fwver)
class SCSIFWver(LegacyItemAccess, Parser):
    """
    Parse `/sys/class/scsi_host/host[0-9]*/fwrev` file, return a dict
    contain `fwver` scsi host file info. "scsi_host" key is scsi host file
    parse from scsi host file name.

    Properties:
        scsi_host (str): scsi host file name derived from file path.
    """

    def __init__(self, context):
        self.data = {}
        self.scsi_host = context.path.rsplit("/")[-2]
        super(SCSIFWver, self).__init__(context)

    def parse_content(self, content):
        for line in get_active_lines(content):
            self.data[self.scsi_host] = [mode.strip() for mode in line.split(',')]

    @property
    def host_mode(self):
        """
        (list): It will return the scsi host modes when set else `None`.
        """
        return self.data[self.scsi_host]
