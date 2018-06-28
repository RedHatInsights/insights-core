"""
LsPci - Command ``/usr/sbin/lspci``
===================================

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
from .. import LogFileOutput, parser, CommandParser
from insights.specs import Specs


@parser(Specs.lspci)
class LsPci(CommandParser, LogFileOutput):
    """Parses output of the ``lspci`` command.

    .. note::
        Please refer to the super-class :class:`insights.core.LogFileOutput`
    """
    pass
