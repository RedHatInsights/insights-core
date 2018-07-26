"""
dmsetup commands - Command ``dmsetup``
======================================

Parsers for parsing and extracting data from output of commands related to
``dmsetup``.
Parsers contained in this module are:

DmsetupInfo - command ``dmsetup info -C``
-----------------------------------------

"""

from insights import parser, CommandParser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


@parser(Specs.dmsetup_info)
class DmsetupInfo(CommandParser):
    """
    ``dmsetup info -C`` command output

    Example input::

        Name               Maj Min Stat Open Targ Event  UUID
        VG00-tmp           253   8 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4
        VG00-home          253   3 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxCqXOnbGe2zjhX923dFiIdl1oi7mO9tXp
        VG00-var           253   6 L--w    1    2      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxicvyvt67113nTb8vMlGfgdEjDx0LKT2O
        VG00-swap          253   1 L--w    2    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax3Ll2XhOYZkylx1CjOQi7G4yHgrIOsyqG
        VG00-root          253   0 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxKpnAKYhrYMYMNMwjegkW965bUgtJFTRY
        VG00-var_log_audit 253   5 L--w    1    1      0 LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTaxwQ8R0XWJRm86QX3befq1cHRy47Von6ZW

    Example data structure produced::

        data = [
          {
            'Stat': 'L--w',
            'Name': 'VG00-tmp',
            'Min': '8',
            'Targ': '1',
            'Maj': '253',
            'Open': '1',
            'Event': '0',
            'UUID': 'LVM-gy9uAwD7LuTIApplr2sogbOx5iS0FTax6lLmBji2ueSbX49gxcV76M29cmukQiw4'
          },...
        ]

    Attributes:
        data (list): List of devices found, in order
        names (list): Device names, in order found
        uuids (list): UUID
        by_name (dict): Access to each device by devicename
        by_uuid (dict): Access to each device by uuid

    Example:
        >>> len(info)
        6
        >>> info.names[0]
        'VG00-tmp'
        >>> info[1]['Maj']
        '253'
        >>> info[1]['Stat']
        'L--w'
    """

    def parse_content(self, content):
        self.data = parse_delimited_table(content)

        self.names = [dm['Name'] for dm in self.data if 'Name' in dm]
        self.by_name = dict((dm['Name'], dm) for dm in self.data if 'Name' in dm)
        self.uuids = [dm['UUID'] for dm in self.data if 'UUID' in dm]
        self.by_uuid = dict((dm['UUID'], dm) for dm in self.data if 'UUID' in dm)

    def __len__(self):
        """
        The length of the devices list
        """
        return len(self.data)

    def __iter__(self):
        """
        Iterate through the devices list
        """
        for dm in self.data:
            yield dm

    def __getitem__(self, idx):
        """
        Fetch a device by index in devices list
        """
        return self.data[idx]
