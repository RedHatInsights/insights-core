"""
VDSMId - file ``/etc/vdsm/vdsm.id``
===================================

Module for parsing the content of file ``vdsm.id``, which is a simple file.

Typical content of "vdsm.id" is::

    # VDSM UUID info
    #
    F7D9D983-6233-45C2-A387-9B0C33CB1306

Examples:
    >>> vd = shared[VDSMId]
    >>> vd.uuid
    "F7D9D983-6233-45C2-A387-9B0C33CB1306"

"""
from .. import Parser, parser
from ..parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.vdsm_id)
class VDSMId(Parser):
    """Class for parsing `vdsm.id` file."""

    def parse_content(self, content):
        """
        Returns the UUID of this Host
        - E.g.: F7D9D983-6233-45C2-A387-9B0C33CB1306
        """
        lines = get_active_lines(content)
        self.uuid = lines[0].strip() if len(lines) > 0 else None
