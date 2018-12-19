"""
Nmcli parsers
=============

This file will parse the output of command line tools used to manage
NetworkManager.

Parsers provided by this module include:

NmcliDevShow - command ``/usr/bin/nmcli dev show``
--------------------------------------------------
NmcliConnShow - command ''/usr/bin/nmcli conn show``
----------------------------------------------------
"""


import re
from .. import parser, LegacyItemAccess, get_active_lines, CommandParser
from insights.specs import Specs
from insights.parsers import parse_delimited_table


@parser(Specs.nmcli_dev_show)
class NmcliDevShow(CommandParser, LegacyItemAccess):
    """
    This class will parse the output of command ``nmcli dev show``, and the information
    will be stored in dictionary format.

    NetworkManager displays all the devices and their current states along with network
    configuration and connection status.

    Attributes:
        data (dict): Dictionary of keys with values in dict.
        connected_devices(list): list of devices who's state is connected.

    Sample input for ``/usr/bin/nmcli dev show``::

        GENERAL.DEVICE:                         em3
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:2A:72:DE:F8:B9
        GENERAL.MTU:                            1500
        GENERAL.STATE:                          100 (connected)
        GENERAL.CONNECTION:                     em3
        GENERAL.CON-PATH:                       /org/freedesktop/NetworkManager/ActiveConnection/1
        WIRED-PROPERTIES.CARRIER:               on
        IP4.ADDRESS[1]:                         10.16.184.98/22
        IP4.GATEWAY:                            10.16.187.254
        IP4.DNS[1]:                             10.16.36.29
        IP4.DNS[2]:                             10.11.5.19
        IP4.DNS[3]:                             10.5.30.160
        IP4.DOMAIN[1]:                          khw.lab.eng.bos.example.com
        IP6.ADDRESS[1]:                         2620:52:0:10bb:ba2a:72ff:fede:f8b9/64
        IP6.ADDRESS[2]:                         fe80::ba2a:72ff:fede:f8b9/64
        IP6.GATEWAY:                            fe80:52:0:10bb::fc
        IP6.ROUTE[1]:                           dst = 2620:52:0:10bb::/64, nh = ::, mt = 100

        GENERAL.DEVICE:                         em1
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:2A:72:DE:F8:BB
        GENERAL.MTU:                            1500
        GENERAL.STATE:                          30 (disconnected)
        GENERAL.CONNECTION:                     --
        GENERAL.CON-PATH:                       --
        WIRED-PROPERTIES.CARRIER:               off

        GENERAL.DEVICE:                         em2
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:2A:72:DE:F8:BC
        GENERAL.MTU:                            1500
        GENERAL.STATE:                          30 (disconnected)
        GENERAL.CONNECTION:                     --
        GENERAL.CON-PATH:                       --
        WIRED-PROPERTIES.CARRIER:               off

    Sample Output::

        {
            'em3':
                {
                  'IP4_DNS3': '10.5.30.160',
                  'IP4_DNS2': '10.11.5.19',
                  'IP4_DNS1': '10.16.36.29',
                  'IP6_ADDRESS2': 'fe80::ba2a:72ff:fede:f8b9/64',
                  'CONNECTION': 'em3',
                  'IP6_ADDRESS1': '2620:52:0:10bb:ba2a:72ff:fede:f8b9/64',
                  'CON-PATH': '/org/freedesktop/NetworkManager/ActiveConnection/1',
                  'IP4_ADDRESS1': '10.16.184.98/22',
                  'MTU': '1500',
                  'IP4_GATEWAY': '10.16.187.254',
                  'STATE': 'connected',
                  'CARRIER': 'on',
                  'IP4_DOMAIN1': 'khw.lab.eng.bos.example.com',
                  'IP6_ROUTE1': 'dst = 2620:52:0:10bb::/64, nh = ::, mt = 100',
                  'HWADDR': 'B8:2A:72:DE:F8:B9',
                  'IP6_GATEWAY': 'fe80:52:0:10bb::fc',
                  'TYPE': 'ethernet'
                },
              'em2':
                {
                  'STATE': 'connected',
                  'CARRIER': 'off',
                  'HWADDR': 'B8:2A:72:DE:F8:BC',
                  'CON-PATH': '--',
                  ...
                  ...
                }
            ...
            ...
        }

    Examples:
        >>> type(nmcli_obj)
        <class 'insights.parsers.nmcli.NmcliDevShow'>
        >>> nmcli_obj.data['em3']['STATE']
        'connected'
        >>> nmcli_obj.data['em2']['HWADDR']
        'B8:2A:72:DE:F8:BC'
        >>> sorted(nmcli_obj.connected_devices)
        ['em1', 'em2', 'em3']

    """

    def parse_content(self, content):
        self.data = {}
        per_device = {}
        current_dev = ""
        for line in get_active_lines(content):
            if not ("not found" in line or "Error" in line or "No such file" in line):
                key, val = line.split(": ")
                if "IP" in key:
                    proto = re.sub(r'\[|\]', r'', key.split('.')[1])
                    key = key.split('.')[0] + "_" + proto
                else:
                    key = key.split('.')[1]
                val = re.sub(r'\d+\s|\(|\)', r'', val.strip())

                # Device configuration details starts here
                if key == "DEVICE" and not current_dev:
                    current_dev = val
                    continue
                elif key == "DEVICE" and current_dev:
                    self.data[current_dev] = per_device
                    current_dev = val
                    per_device = {}
                    continue
                per_device.update({key: val})
        if current_dev and per_device:
            # Last device configuration details
            self.data[current_dev] = per_device

    @property
    def connected_devices(self):
        """(list): The list of devices who's state is connected and managed by NetworkManager"""
        con_dev = []
        for key in self.data:
            if 'STATE' in self.data[key] and self.data[key]['STATE'] == 'connected':
                con_dev.append(key)
        return con_dev


@parser(Specs.nmcli_conn_show)
class NmcliConnShow(CommandParser):
    """
    This file will parse the output of all the nmcli connections.

    Sample configuration from a teamed interface in file ``/usr/bin/nmcli conn show``::

       NAME      UUID                                  TYPE      DEVICE
       enp0s3    320d4923-c410-4b22-b7e9-afc5f794eecc  ethernet  enp0s3
       virbr0    7c7dec66-4a8c-4b49-834a-889194b3b83c  bridge    virbr0
       test-net  f858b1cc-d149-4de0-93bc-b1826256847a  ethernet  --

    Examples:
        >>> type(static_conn)
        <class 'insights.parsers.nmcli.NmcliConnShow'>
        >>> static_conn.disconnected_connection
        ['test-net-1']

    Attributes:
        data (list): list of connections wrapped in dictionaries

    """
    def parse_content(self, content):
        self.data = parse_delimited_table(content)
        self._disconnected_connection = []
        for all_connection in self.data:
            if all_connection['DEVICE'] == "--":
                self._disconnected_connection.append(all_connection['NAME'])

    @property
    def disconnected_connection(self):
        """(list): It will return all the disconnected static route connections."""
        return self._disconnected_connection
