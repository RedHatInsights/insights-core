"""
EtcMachineId - file ``/etc/machine-id``
=======================================
"""
import uuid

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.etc_machine_id)
class EtcMachineId(Parser):
    """
    Class for parsing the file ``/etc/machine-id``

    Sample file content::

        4f3fbfda59ff4aea969255a73342d439

    Examples:
        >>> type(machine_id)
        <class 'insights.parsers.etc_machine_id.EtcMachineId'>
        >>> machine_id.machine_id
        '4f3fbfda59ff4aea969255a73342d439'
        >>> machine_id.uuid
        '4f3fbfda-59ff-4aea-9692-55a73342d439'
    """

    def parse_content(self, content):
        content = get_active_lines(content)
        if not content or len(content) != 1:
            raise SkipComponent('Invalid Content')
        self.id = self.machine_id = content[0]
        self.uuid = str(uuid.UUID(self.id))
