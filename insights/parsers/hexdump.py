"""
HexDump - command ``/usr/bin/hexdump -C /dev/cpu_dma_latency``
==============================================================

This module provides the class ``HexDump`` which processes
``/usr/bin/hexdump -C /dev/cpu_dma_latency`` command output.
"""
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.hexdump)
class HexDump(CommandParser):
    """
    Class for parsing the output of `/usr/bin/hexdump -C /dev/cpu_dma_latency` command.

    Typical output of is::

        00000000  01 00 00 00                                       |....|
        00000004

    Attributes:
        data(list): A string containing hexadecimal value on first line of the output.
        hex_value (string): The hexadecimal value of force_latency.
        dec_value (int): The decimal value of force_latency.

    Examples:
        >>> type(hex_dump)
        <class 'insights.parsers.hexdump.HexDump'>
        >>> hex_dump.data
        ['00000000  01 00 00 00                                       |....|', '00000004']
        >>> hex_dump.hex_value
        '00 00 00 01'
        >>> hex_dump.dec_value
        1
    """

    def parse_content(self, content):
        # The self.data returns the raw output of the command.
        self.data = content

        # The self.hex_value returns the hexadecimal value of force_latency
        # from the output of the command.
        self.hex_value = self.data[0][10:21].split(' ')[::-1]
        self.hex_value = ' '.join(map(str, self.hex_value))

        # The self.dec_value returns the decimal value of force_latency
        # from the output of the command.
        self.dec_value = self.hex_value.replace(' ', '')
        self.dec_value = int(self.dec_value, 16)
