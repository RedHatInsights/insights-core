from .. import Mapper, mapper
from ..mappers import get_active_lines


@mapper("vdsm_id")
class VDSMId(Mapper):
    """Class for VDSM IDs."""

    def parse_content(self, content):
        """
        Returns the UUID of this Host
        - E.g.: F7D9D983-6233-45C2-A387-9B0C33CB1306
        """
        lines = get_active_lines(content)
        self.uuid = lines[0].strip() if len(lines) > 0 else None
        self.data = self.uuid


@mapper("vdsm_id")
def get_vdsm_id(context):
    """Deprecated, do not use."""
    return VDSMId(context).uuid
