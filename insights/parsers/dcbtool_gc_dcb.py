"""
Dcbtool - Command ``/sbin/dcbtool gc {interface} dcb``
======================================================

    Parse Lines from the `dcbtool gc eth1 dcb` to check DCBX if enabled

    Successful completion of the command returns data similar to::

        Command:    Get Config
        Feature:    DCB State
        Port:       eth0
        Status:     Off
        DCBX Version: FORCED CIN

    The keys in this data are converted to lower case and spaces are converted
    to underscores.

    An `is_on` attribute is also provided to indicate if the status is 'On'.

    Examples:

        >>> dcbstate = shared[Dcbtool]
        >>> dcb.data
        {
            "command": "Get Config",
            "feature": "DCB State",
            "port": "eth0",
            "status": "Off"
            "dcbx_version":"FORCED CIN"
        }
        >>> dcb['port']
        'eth0'
        >>> dcb['state']
        'Off'
        >>> dcb.is_on
        False

    If a "Connection refused" error is encountered,
    an empty dictionary is returned`.

"""

from .. import parser, LegacyItemAccess, CommandParser, get_active_lines
from insights.specs import Specs


@parser(Specs.dcbtool_gc_dcb)
class Dcbtool(LegacyItemAccess, CommandParser):
    """
    Parse the output of the `dcbtool` command.

    If the command output contains 'Connection refused', no data is stored.
    The LegacyItemAccess mixin class is used to provide direct access to the
    data.

    Attributes:
        data (dict): A dictionary of the content of the command output.
        is_on: (bool): Is the status of the interface 'On'?
    """
    def parse_content(self, content):
        self.data = {}
        if "Connection refused" in content[0]:
            return

        for line in get_active_lines(content):
            key, value = line.split(":", 1)
            key = key.lower().replace(" ", "_")
            self.data[key] = value.strip()

        self.is_on = (self.data['status'] == 'On')
