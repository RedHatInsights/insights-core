"""
IBM Proc Files
==============

Parsers for parsing the following proc files of IBM system:

IBMPpcLparCfg - file ``/proc/powerpc/lparcfg``
----------------------------------------------

IBMFirmwareLevel - file ``/proc/device-tree/openprom/ibm,fw-vernum_encoded``
----------------------------------------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ibm_lparcfg)
class IBMPpcLparCfg(Parser, dict):
    """
    Class for parsing the ``/proc/powerpc/lparcfg`` file to a dictionary.

    Typical content looks like::

        serial_number=IBM,123456789
        system_type=IBM,8247-22L

    Examples:
        >>> ibm_mtm['system_type']
        '8247-22L'

    Raises:
        SkipComponent: If nothing need to parse
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")

        for line in content:
            key, value = [l.strip() for l in line.split('=', 1)]
            _, _, value = value.partition(',')
            self[key] = value.strip()

        if len(self) == 0:
            raise SkipComponent("Nothing to parse.")


@parser(Specs.ibm_fw_vernum_encoded)
class IBMFirmwareLevel(Parser):
    """
    Class for parsing the ``/proc/device-tree/openprom/ibm,fw-vernum_encoded``
    file.

    Typical content looks like::

        FW950.30 (VL950_092)\x00

    Attributes:
        raw (str): The RAW content of the `ibm,fw-vernum_encoded` file.
        firmware_level (str): The firmware level required by FLRT.

    Examples:
        >>> ibm_fwl.firmware_level
        'VL950_092'

    Raises:
        SkipComponent: If nothing need to parse
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")

        self.raw = content[0]

        if "(" not in self.raw or ")" not in self.raw:
            raise SkipComponent("Nothing to parse.")

        self.firmware_level = self.raw[self.raw.index('(') + 1:self.raw.index(')')]
