"""
LsPci - Commands ``lspci``
==========================

The parsers in this module are to parse the PCI device information gathered
from the ``/sbin/lspci`` commands.

LsPci - Command ``lspci -k``
----------------------------

LsPciVmmkn - Command ``lspci -vmmkn``
-------------------------------------

"""
import re

from insights.core import CommandParser, LogFileOutput
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
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
        >>> lspci.pci_dev_details('00:00.0')['Slot']
        '00:00.0'
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
        slot = None
        slot_re = re.compile(r'^[0-9a-f]+:[0-9a-f]+.[0-9a-f]+')

        fields = ["Subsystem", "Kernel driver in use", "Kernel modules"]

        for line in get_active_lines(content):
            parts = line.split()

            if slot_re.match(parts[0]):
                slot = parts[0]
                device_details = line.split(None, 1)[-1]  # keep the raw line
                self.data[slot] = {
                        'Slot': slot,
                        'Dev_Details': device_details.lstrip()}
            elif slot and (line.split(":")[0].strip() in fields):
                parts = line.split(':')
                self.data[slot][parts[0]] = parts[1].lstrip()

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
        return list(self.data.keys())


@parser(Specs.lspci_vmmkn)
class LsPciVmmkn(CommandParser, list):
    """
    Class to parse the PCI device information gathered from the
    ``/sbin/lspci -vmmkn`` command.

    Typical output of the ``lspci -vmmkn`` command is::

        Slot:   00:00.0
        Class:  0600
        Vendor: 8086
        Device: 1237
        SVendor:    1af4
        SDevice:    1100
        Rev:    02

        Slot:   00:01.0
        Class:  0101
        Vendor: 8086
        Device: 7010
        SVendor:    1af4
        SDevice:    1100
        ProgIf: 80
        Driver: ata_piix
        Module: ata_piix
        Module: ata_generic

        Slot:   00:01.1
        Class:  0c03
        Vendor: 8086
        Device: 7020
        SVendor:    1af4
        SDevice:    1100
        Rev:    01
        Driver: uhci_hcd

        Slot:   00:03.0
        Class:  0200
        Vendor: 1af4
        Device: 1000
        SVendor:    1af4
        SDevice:    0001
        PhySlot:    3
        Driver: virtio-pci

    Examples:
        >>> type(lspci_vmmkn)
        <class 'insights.parsers.lspci.LsPciVmmkn'>
        >>> sorted(lspci_vmmkn.pci_dev_list)
        ['00:00.0', '00:01.0', '00:01.1', '00:03.0']
        >>> lspci_vmmkn[0].get('Driver') is None
        True
        >>> lspci_vmmkn[-1].get('Driver')
        'virtio-pci'
        >>> len(lspci_vmmkn[1].get('Module'))
        2

    Attributes:

    """
    def parse_content(self, content):
        # Remove the white-trailing of the output
        while content and not content[-1].strip():
            content.pop(-1)

        dev = {}
        self.append(dev)
        for line in content:
            line = line.strip()
            if not line:
                # Skip empty lines
                if dev:
                    dev = {}
                    self.append(dev)
                continue
            key, val = [i.strip() for i in line.split(':', 1)]
            # Module could have multiple values
            if key == 'Module':
                if key in dev:
                    dev[key].append(val)
                else:
                    dev[key] = [val]
            else:
                dev[key] = val

        if len(self) <= 1 and not dev:
            raise SkipComponent()

    @property
    def pci_dev_list(self):
        """
        The list of PCI devices.
        """
        return [i['Slot'] for i in self]
