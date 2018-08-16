"""
LsPci - Command ``lspci -k``
============================

To parse the PCI device information gathered from the ``/sbin/lspci -k`` command.

"""

from .. import LogFileOutput, parser, CommandParser, get_active_lines
from insights.specs import Specs


@parser(Specs.lspci)
class LsPci(CommandParser, LogFileOutput):
    """
    Class to parse the PCI device information gathered from the
    ``/sbin/lspci -k`` command.

    Typical output of the ``lspci -k`` command is::

        00:00.0 Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)
                Subsystem: Cisco Systems Inc Device 0101
        00:01.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 1 (rev 13)
                Kernel driver in use: pcieport
                Kernel modules: shpchp
        00:02.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 2 (rev 13)
                Kernel driver in use: pcieport
                Kernel modules: shpchp
        03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
                Subsystem: Cisco Systems Inc Device 004a
                Kernel driver in use: ixgbe
                Kernel modules: ixgbe
        06:00.0 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
                Subsystem: Cisco Systems Inc Device 004a
                Kernel driver in use: ixgbe
                Kernel modules: ixgbe

    Examples:
        >>> type(lspci)
        <class 'insights.parsers.lspci.LsPci'>
        >>> lspci.get("Intel Corporation")[0]['raw_message']
        '00:00.0 Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)'
        >>> len(lspci.get("Network controller"))
        1
        >>> "Centrino Advanced-N 6205" in lspci
        True
        >>> "0d:00.0" in lspci
        False
        >>> sorted(lspci.pci_dev_list)
        ['00:00.0', '00:01.0', '00:02.0', '03:00.0', '06:00.0']
        >>> lspci.pci_dev_details('00:00.0')['Subsystem']
        'Cisco Systems Inc Device 0101'
        >>> lspci.pci_dev_details('00:00.0')['Dev_Details']
        'Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)'

    Attributes:
        data (dict): Dict where the keys are the device number and values are
            details of the device.
        lines (list): List of details of each listed device, the same to the
            values of `self.data`

    """
    def parse_content(self, content):
        # Use all the defined scanners to search the log file, setting the
        # properties defined in the scanner.
        self.lines = [l for l in content if len(l) > 0 and l[0].isdigit()]
        for scanner in self.scanners:
            scanner(self)
        # Parse kernel driver lines
        self.data = {}
        bus_device_function = ""
        for line in get_active_lines(content):
            parts = line.split(None)
            if parts[0] and parts[0] not in ['Subsystem:', 'Kernel'] \
                    and len(parts[0].split(':')) == 2 and len(parts[0].split('.')) == 2:
                bus_device_function = parts[0]
                device_details = ' '.join(map(str, parts[1:]))
                self.data[bus_device_function] = {'Dev_Details': device_details.lstrip()}
            elif bus_device_function:
                parts = line.split(':')
                self.data[bus_device_function][parts[0]] = parts[1].lstrip()

    def pci_dev_details(self, dev_name):
        """
        It will return the PCI device and it's details.

        Args:
            PCI Bus Device function number eg: '00:01:0'

        Returns:
            (dict): Returns device details along with 'Subsystem', 'Kernel Driver in Use', 'Kernel Modules'.
            Returns `None` if device doesn't exists
        """
        return self.data.get(dev_name, None)

    @property
    def pci_dev_list(self):
        """
        The list of PCI devices.
        """
        return self.data.keys()
