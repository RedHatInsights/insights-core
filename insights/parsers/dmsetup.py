"""
dmsetup commands - Command ``dmsetup``
======================================

Parsers for parsing and extracting data from output of commands related to
``dmsetup``.
Parsers contained in this module are:

DmsetupInfo - command ``dmsetup info -C``
-----------------------------------------

"""
from collections import namedtuple
from insights import parser, CommandParser
from insights.parsers import parse_delimited_table
from insights.specs import Specs


SetupInfo = namedtuple('SetupInfo', [
    'name', 'major', 'minor', 'open', 'segments', 'events',
    'live_table', 'inactive_table', 'suspended', 'readonly', 'uuid']
)
""" Data structure to represent dmsetup information """


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
        info (list): List of devices found, in order using SetupInfo structure

    Example:
        >>> len(setup_info)
        6
        >>> setup_info.names[0]
        'VG00-tmp'
        >>> setup_info[1]['Maj']
        '253'
        >>> setup_info[1]['Stat']
        'L--w'
        >>> setup_info.info[-1].name
        'VG00-var_log_audit'
        >>> setup_info.info[-1].major
        253
        >>> setup_info.info[-1].live_table
        True
        >>> setup_info.info[-1].readonly
        False
    """

    def parse_content(self, content):
        self.data = parse_delimited_table(content)

        self.names = [dm['Name'] for dm in self.data if 'Name' in dm]
        self.by_name = dict((dm['Name'], dm) for dm in self.data if 'Name' in dm)
        self.uuids = [dm['UUID'] for dm in self.data if 'UUID' in dm]
        self.by_uuid = dict((dm['UUID'], dm) for dm in self.data if 'UUID' in dm)
        self.info = []
        for dm in self.data:
            self.info.append(SetupInfo(
                name=dm.get('Name'),
                major=int(dm.get('Maj')) if 'Maj' in dm and dm.get('Maj').isdigit() else None,
                minor=int(dm.get('Min')) if 'Min' in dm and dm.get('Min').isdigit() else None,
                open=int(dm.get('Open')) if 'Open' in dm and dm.get('Open').isdigit() else None,
                segments=int(dm.get('Targ')) if 'Targ' in dm and dm.get('Targ').isdigit() else None,
                events=int(dm.get('Event')) if 'Event' in dm and dm.get('Event').isdigit() else None,
                live_table=dm.get('Stat', '----')[0] == 'L',
                inactive_table=dm.get('Stat', '----')[1] == 'I',
                suspended=dm.get('Stat', '----')[2] == 's',
                readonly=dm.get('Stat', '----')[3] == 'r',
                uuid=dm.get('UUID')
            ))

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
