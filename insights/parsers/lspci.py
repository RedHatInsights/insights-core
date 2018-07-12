"""
Lists ALL the PCI Devices With Details
======================================

Parsers included in this module are:

LsPci - command ``/sbin/lspci``
-------------------------------

LsPciDriver - command ``/sbin/lspci -k``
----------------------------------------

"""

from .. import LogFileOutput, parser, CommandParser, get_active_lines
from insights.specs import Specs


@parser(Specs.lspci_kernel)
class LsPciDriver(CommandParser):
    """
    This module provides methods to access driver information of PCI devices from
    the ``/sbin/lspci -k`` command.

    Typical output of the ``lspci -k`` command is::

        00:00.0 Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)
                Subsystem: Cisco Systems Inc Device 0101
        00:01.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 1 (rev 13)
                Kernel driver in use: pcieport
                Kernel modules: shpchp
        00:02.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 2 (rev 13)
                Kernel driver in use: pcieport
                Kernel modules: shpchp
        06:00.0 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
                Subsystem: Cisco Systems Inc Device 004a
                Kernel driver in use: ixgbe
                Kernel modules: ixgbe
        06:00.1 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
                Subsystem: Cisco Systems Inc Device 004a
                Kernel driver in use: ixgbe
                Kernel modules: ixgbe

    Example:

        >>> lspcidriv = shared[LsPciDriver]
        >>> lspcidriv.pci_dev_list
        ['00:00.0', '00:01.0', '00:02.0', '06:00.0', '06:00.1']
        >>> lspcidriv.pci_dev_details('00:00.0')
        {'Subsystem': 'Cisco Systems Inc Device 0101', 'Dev_Details': 'Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)'}
    """

    def __init__(self, *args, **kwargs):
        self.data = {}
        """dict: Dictionary service detail like active, running, exited, dead"""
        super(LsPciDriver, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
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
        It will return list of PCI devices.

        Returns:
            (list): Returns device list on successes. Returns `None` if device doesn't exists
        """
        return self.data.keys()


@parser(Specs.lspci)
class LsPci(CommandParser, LogFileOutput):
    """
    This module provides plugins access to the PCI device information gathered from
    the ``/usr/sbin/lspci`` command.

    Typical output of the ``lspci`` command is::

        00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
        00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
        03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
        0d:00.0 System peripheral: Ricoh Co Ltd PCIe SDXC/MMC Host Controller (rev 07)

    The data is exposed via the ``obj.lines`` attribute which is a list containing
    each line in the output.  The data may also be filtered using the
    ``obj.get("filter string")`` method.  This method will return a list of lines
    containing only "filter string".  The ``in`` operator may also be used to test
    whether a particular string is in the ``lspci`` output.  Other methods/operators
    are also supported, see the :py:class:`insights.core.LogFileOutput` class for more information.

    .. note::

        The examples in this module may be executed with the following command:
        ``python -m insights.parsers.lspci``

    Examples:
        >>> lspci_content = '''
        ... 00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
        ... 00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
        ... 03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
        ... 0d:00.0 System peripheral: Ricoh Co Ltd PCIe SDXC/MMC Host Controller (rev 07)
        ... '''.strip()
        >>> from insights.tests import context_wrap
        >>> shared = {LsPci: LsPci(context_wrap(lspci_content))}
        >>> pci_info = shared[LsPci]
        >>> pci_info.get("Intel Corporation")[0]['raw_message']
        '00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)', '00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)', '03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)'
        >>> len(pci_info.get("Network controller"))
        1
        >>> "Centrino Advanced-N 6205" in pci_info
        True
        >>> "0d:00.0" in pci_info
        True
    """
    pass
