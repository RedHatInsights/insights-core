"""
FcoeadmI - command ``fcoeadm -i``
=================================

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
class FcoeadmI(CommandParser, dict):
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
        >>> fi["Description"]
        'NetXtreme II BCM57810 10 Gigabit Ethernet'
        >>> fi.fcoe["Driver"]
        'bnx2x 1.712.30-0'
        >>> fi["Driver"]
        'bnx2x 1.712.30-0'
        >>> fi.fcoe['Serial Number']
        '2C44FD8F4418'
        >>> fi['Serial Number']
        '2C44FD8F4418'
        >>> fi.iface_list
        ['eth8.0-fcoe', 'eth6.0-fcoe']
        >>> fi.nic_list
        ['eth8', 'eth6']
        >>> fi.stat_list
        ['Online', 'Offline']
        >>> fi.get_stat_from_nic('eth6')
        'Offline'
        >>> fi.get_host_from_nic('eth6')
        'host7'

    Attributes:
        driver_name (str): Driver name
        driver_version (str): Driver version
        iface_list (list) : FCoE interface names
        nic_list (list) : Ethernet ports running FCoE interfaces
        stat_list (list): FCoE interface(s) status

    Raises:
        SkipException: When input content is empty
        ParseException: When input content is not available to parse
    """

    def parse_content(self, content):
        EMPTY = "Input content is empty"
        BADWD = "No useful data parsed in content: '{0}'".format(content)

        if not content:
            raise SkipException(EMPTY)

        if len(content) < 6 and len(content) > 0:
            raise ParseException(BADWD)

        iface = {}
        iface_section_list = []

        self.iface_list = []
        self.nic_list = []
        self.stat_list = []
        self.driver_name = ''
        self.driver_version = ''
        fcoe = {'Interfaces': iface_section_list}

        symb = False
        for line in content:
            line = line.strip()

            if 'Symbolic Name:' in line:
                symb = True

            if ':' in line:
                key, val = [s.strip() for s in line.split(': ', 1)]
                if not symb:
                    fcoe[key] = val
                else:
                    iface[key] = val

            if 'State:' in line:
                iface_section_list.append(iface)
                iface = {}

        self.update(fcoe)
        self.driver_name = fcoe['Driver'].split(' ', 1)[0]
        self.driver_version = fcoe['Driver'].split(' ', 1)[-1]

        for iface in fcoe['Interfaces']:
            self.iface_list.append(iface['Symbolic Name'].split(' ')[-1])

        for nic in self.iface_list:
            self.nic_list.append(nic.split('.', 1)[0])

        for iface in fcoe['Interfaces']:
            self.stat_list.append(iface['State'])

    def get_stat_from_nic(self, nic):
        """
        Get 'State' of fcoe interface created on specified ethernet port.

        Parameter:
            nic (str): Ethernet port which provided by FCoE adapter.

        Return:
            str: Return fcoe status. When nic is not valid fcoe port,
                 raise ValueError.

        Raises:
            ValueError: When nic is not valid fcoe port
        """

        ret = ''
        self.__check_nic_valid(nic)

        for iface in self['Interfaces']:
            if nic in iface['Symbolic Name']:
                ret = iface['State']
        return ret

    def get_host_from_nic(self, nic):
        """
        Get 'OS Device Name' for the specified ethernet port.

        Parameter:
            nic (str): Ethernet port which provided by FCoE adapter

        Return:
            str: Return fcoe host, which as 'OS Device Name' to display,
                 when nic is not valid fcoe port, raise ValueError

        Raises:
            ValueError: When nic is not valid fcoe port
        """

        ret = ''
        self.__check_nic_valid(nic)

        for iface in self['Interfaces']:
            if nic in iface['Symbolic Name']:
                ret = iface['OS Device Name']
        return ret

    def __check_nic_valid(self, nic):
        BADNIC = "'%s' is NOT real FCoE port provided by HBA/CNA adapter" % nic

        if nic not in self.nic_list:
            raise ValueError(BADNIC)

    @property
    def fcoe(self):
        """
        (dict): The result parsed of '/usr/sbin/fcoeadm -i'
        """
        return self
