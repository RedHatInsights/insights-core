"""
MAC Address
===========
"""
import re

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.mac_addresses)
class MacAddress(Parser):
    """
    Parse the machine info in the file "insights-commands/duplidate_machine_info".

    Sample input::

        00:5b:ea:09:00:00

    Attributes:
        address(str): the MAC address

    Examples:
        >>> type(mac_addr)
        <class 'insights.parsers.mac.MacAddress'>
        >>> mac_addr.address
        '00:5b:ea:09:00:00'

    Raises:
        SkipComponent: when there is no expected content in the file
    """
    def parse_content(self, content):
        if not content or len(content) != 1:
            raise SkipComponent('Invalid Content')

        addr = content[0].strip()
        match = re.match("^([0-9a-f]{2}:){5}[0-9a-f]{2}$", addr)
        if match is None:
            raise SkipComponent('Invalid Content')

        self.address = addr
