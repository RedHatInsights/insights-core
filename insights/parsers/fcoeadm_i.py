"""
FcoeadmI - command ``fcoeadm -i``
=============================

Module for parsing the output of command ``fcoeadm -i``. The bulk of the
content is split on the colon and keys are kept as is. Lines beginning
with 'Description', 'Revision', 'Manufacturer', 'Serial Number', 'Driver'
,'Number of Ports' are kept in a dictionary keyed under each of these names.
Lines beginning with 'Symbolic Name', 'OS Device Name', 'Node Name', 'Port Name',
'FabricName', 'Speed', 'Supported Speed', 'MaxFrameSize', 'FC-ID (Port ID)',
'State' are kept in a sub-dictionary keyed under each these names. All the
sub-dictionaries are kept in a list keyed in 'Interfaces'.
"""

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import ParseException, SkipException


@parser(Specs.fcoeadm_i)
class FcoeadmI(CommandParser):
    """
    Class for parsing ``fcoeadm -i`` command output.

    Typical output of command ``fcoeadm -i`` looks like::

        Description:      NetXtreme II BCM57810 10 Gigabit Ethernet
        Revision:         10
        Manufacturer:     Broadcom Corporation
        Serial Number:    2C44FD8F4418
        Driver:           bnx2x 1.712.30-0
        Number of Ports:  1

            Symbolic Name:     bnx2fc (QLogic BCM57810) v2.9.6 over eth8.0-fcoe
            OS Device Name:    host6
            Node Name:         0x50060B0000C26237
            Port Name:         0x50060B0000C26236
            FabricName:        0x0000000000000000
            Speed:             Unknown
            Supported Speed:   1 Gbit, 10 Gbit
            MaxFrameSize:      2048
            FC-ID (Port ID):   0xFFFFFFFF
            State:             Online

            Symbolic Name:     bnx2fc (QLogic BCM57810) v2.9.6 over eth6.0-fcoe
            OS Device Name:    host7
            Node Name:         0x50060B0000C26235
            Port Name:         0x50060B0000C26234
            FabricName:        0x0000000000000000
            Speed:             Unknown
            Supported Speed:   1 Gbit, 10 Gbit
            MaxFrameSize:      2048
            FC-ID (Port ID):   0xFFFFFFFF
            State:             Offline

    Examples:
        >>> type(fi)
        <class 'insights.parsers.fcoeadm_i.FcoeadmI'>
        >>> fi.fcoe["Description"]
        'NetXtreme II BCM57810 10 Gigabit Ethernet'
        >>> fi.fcoe["Driver"]
        'bnx2x 1.712.30-0'
        >>> fi.fcoe['Serial Number']
        '2C44FD8F4418'
        >>> fi.get_iface
        ['eth8.0-fcoe', 'eth6.0-fcoe']
        >>> fi.get_nic
        ['eth8', 'eth6']
        >>> fi.get_stat
        ['Online', 'Offline']
        >>> fi.get_stat_from_nic('eth6')
        'Offline'
        >>> fi.get_host_from_nic('eth8')
        'host6'

    Attributes:
        fcoe (dict): Parse the command of '/usr/sbin/fcoeadm -i'
        iface_lenth (int): The length of fcoe interfaces
        driver_name (str): Driver name
        driver_version (str): Driver version

    Raises:
        ParseException: When input content is empty or there is no parsed data.
    """

    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in content: '{0}'".format(content)

        if not content:
            raise SkipException(EMPTY)

        if len(content) < 6 and len(content) > 0:
            raise ParseException(BADWD)

        iface_list = []
        iface = {}
        self.iface_lenth = None
        self.driver_name = ''
        self.driver_version = ''
        self.fcoe = {}
        self.fcoe['Interfaces'] = iface_list
        symb = False

        for line in content:
            line = line.strip()

            if 'Symbolic Name:' in line:
                symb = True

            if ':' in line:
                key, val = [s.strip() for s in line.split(': ', 1)]
                if not symb:
                    self.fcoe[key] = val
                else:
                    iface[key] = val

            if 'State:' in line:
                iface_list.append(iface)
                iface = {}

        self.iface_lenth = len(self.fcoe['Interfaces'])
        self.driver_name = self.fcoe['Driver'].split(' ', 1)[0]
        self.driver_version = self.fcoe['Driver'].split(' ', 1)[-1]
        return self.fcoe

    @property
    def get_iface(self):
        """int: the major version of this OS."""
        iface_list = []
        for iface in self.fcoe['Interfaces']:
            iface_list.append(iface['Symbolic Name'].split(' ')[-1])
        return iface_list

    @property
    def get_nic(self):
        """list: the nic of fcoe iface"""
        nic_list = []
        for nic in self.get_iface:
            nic_list.append(nic.split('.', 1)[0])
        return nic_list

    @property
    def get_stat(self):
        """list: the state of fcoe ifaces"""
        stat_list = []
        for iface in self.fcoe['Interfaces']:
            stat_list.append(iface['State'])
        return stat_list

    def get_stat_from_nic(self, nic):
        """str: the fcoe state"""
        ret = None
        for iface in self.fcoe['Interfaces']:
            if nic in iface['Symbolic Name']:
                ret = iface['State']
        return ret

    def get_host_from_nic(self, nic):
        """str: the fcoe host"""
        ret = None
        for iface in self.fcoe['Interfaces']:
            if nic in iface['Symbolic Name']:
                ret = iface['OS Device Name']
        return ret
