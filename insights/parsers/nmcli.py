"""
Nmcli parsers
=============

This file will parse the output of command line tools used to manage
NetworkManager.

Parsers provided by this module include:

NmcliDevShow - command ``/usr/bin/nmcli dev show``
--------------------------------------------------
NmcliConnShow - command ``/usr/bin/nmcli conn show``
----------------------------------------------------
"""


import re
from insights import parser, get_active_lines, CommandParser
from insights.specs import Specs
from insights.parsers import parse_delimited_table, SkipException


@parser(Specs.nmcli_dev_show)
class NmcliDevShow(CommandParser, dict):
    """
    .. warning::
        This parser may be for a single device, please use
        :py:class:`insights.combiners.nmcli.AllNmcliDevShow` instead for all the
        devices.

    This class will parse the output of command ``nmcli dev show``, and the information
    will be stored in dictionary format.

    NetworkManager displays all the devices and their current states along with network
    configuration and connection status.

    This parser works like a python dictionary, all parsed data can be accessed
    via the ``dict`` interfaces.

    Sample input for ``/usr/bin/nmcli dev show``::

        GENERAL.DEVICE:                         em3
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:AA:BB:DE:F8:B9
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
        IP4.DOMAIN[1]:                          abc.lab.eng.example.com
        IP6.ADDRESS[1]:                         2620:52:0:10bb:ba2a:72ff:fede:f8b9/64
        IP6.ADDRESS[2]:                         fe80::ba2a:72ff:fede:f8b9/64
        IP6.GATEWAY:                            fe80:52:0:10bb::fc
        IP6.ROUTE[1]:                           dst = 2620:52:0:10bb::/64, nh = ::, mt = 100

        GENERAL.DEVICE:                         em1
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:AA:BB:DE:F8:BB
        GENERAL.MTU:                            1500
        GENERAL.STATE:                          30 (disconnected)
        GENERAL.CONNECTION:                     --
        GENERAL.CON-PATH:                       --
        WIRED-PROPERTIES.CARRIER:               off

        GENERAL.DEVICE:                         em2
        GENERAL.TYPE:                           ethernet
        GENERAL.HWADDR:                         B8:AA:BB:DE:F8:BC
        GENERAL.MTU:                            1500
        GENERAL.STATE:                          30 (disconnected)
        GENERAL.CONNECTION:                     --
        GENERAL.CON-PATH:                       --
        WIRED-PROPERTIES.CARRIER:               off

    Examples:
        >>> type(nmcli_obj)
        <class 'insights.parsers.nmcli.NmcliDevShow'>
        >>> nmcli_obj['em3']['STATE']
        'connected'
        >>> nmcli_obj.get('em2')['HWADDR']
        'B8:AA:BB:DE:F8:BC'
        >>> sorted(nmcli_obj.connected_devices)
        ['em1', 'em2', 'em3']

    """
    def parse_content(self, content):
        if not content:
            raise SkipException()

        data = {}
        per_device = {}
        current_dev = ""
        for line in get_active_lines(content):
            if (not ("not found" in line or "Error" in line or "No such file" in line or "Warning" in line)):
                if len(line.split(": ")) >= 2:
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
                        data[current_dev] = per_device
                        current_dev = val
                        per_device = {}
                        continue
                    per_device.update({key: val})
        if current_dev and per_device:
            # Last device configuration details
            data[current_dev] = per_device

        if not data:
            raise SkipException()
        self.update(data)
        self._con_dev = [k for k, v in data.items()
                         if 'STATE' in v and v['STATE'] == 'connected']

    @property
    def connected_devices(self):
        """(list): The list of devices who's state is connected and managed by NetworkManager"""
        return self._con_dev

    @property
    def data(self):
        """(dict): Dict with the device name as the key and device details as the value."""
        return self


@parser(Specs.nmcli_dev_show_sos)
class NmcliDevShowSos(NmcliDevShow):
    """
    .. warning::
        This parser may be for a single device, please use
        :py:class:`insights.combiners.nmcli.AllNmcliDevShow` instead for all the
        devices.

    In some versions of sosreport, the ``nmcli dev show`` command is separated
    to individual files for different devices. While in some versions, it's
    still a whole file.  The base class :py:class:`NmcliDevShow` could handle
    both of them, except that the parsing results is stored into a list for
    separated files.

    """
    pass


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
        try:
            self.data = parse_delimited_table(content, heading_ignore=["NAME", "UUID", "TYPE", "DEVICE"])
        except:
            raise SkipException("Invalid Contents!")
        self._disconnected_connection = []
        for all_connection in self.data:
            if all_connection['DEVICE'] == "--":
                self._disconnected_connection.append(all_connection['NAME'])

    @property
    def disconnected_connection(self):
        """(list): It will return all the disconnected static route connections."""
        return self._disconnected_connection
