"""
OpenVmTools - Commands ``open-vm-tools``
========================================

Parsers that parse the output of command ``open-mv-tools`` are included in this
module:

OpenVmToolsStatRawTextSession - Command ``vmware-toolbox-cmd stat raw text session``
------------------------------------------------------------------------------------

"""

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.open_vm_tools_stat_raw_text_session)
class OpenVmToolsStatRawTextSession(CommandParser, dict):
    """
    Class to parse the output of command ``vmware-toolbox-cmd stat raw text session``

    Sample input::

        session = 4004861987670969122
        uptime = 1036293956
        version = VMware ESXi 6.0.0 build-12345
        provider =
        uuid.bios = 00 00 00 00 00 00 66 8e-00 00 00 00 51 1e 23 f3

    Examples:
        >>> type(ovmt)
        <class 'insights.parsers.open_vm_tools.OpenVmToolsStatRawTextSession'>
        >>> ovmt['version'] == 'VMware ESXi 6.0.0 build-12345'
        True
    """

    def parse_content(self, content):
        if not content or 'must be run inside a virtual machine' in content[0]:
            raise SkipException

        data = dict()
        for line in content:
            if '=' in line:
                key, value = [i.strip() for i in line.split('=', 1)]
                data[key] = value

        if not data:
            raise SkipException

        self.update(data)
