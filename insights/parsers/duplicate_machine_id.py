"""
DuplicateMachineId - file ``insights-commands/duplidate_machine_id``
====================================================================
"""

from insights.core import Parser
from insights.core.exceptions import SkipException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.duplicate_machine_id)
class DuplicateMachineId(Parser):
    """
    Parse the machine id in the file "insights-commands/duplidate_machine_id".
    And save the result to the `duplicate_machine_id` attribute.

    Sample output::

        dc194312-8cdd-4e75-8cf1-2094bf666f45

    Attributes:
        duplicate_machine_id (str): the duplicate machine id

    Examples:
        >>> type(machine_id_obj)
        <class 'insights.parsers.duplicate_machine_id.DuplicateMachineId'>
        >>> machine_id_obj.duplicate_machine_id
        'dc194312-8cdd-4e75-8cf1-2094bf666f45'

    Raises:
        SkipException: when there is no expected content in the file
    """
    def parse_content(self, content):
        if len(content) == 1:
            self.duplicate_machine_id = content[0].strip()
        else:
            raise SkipException('No expected machine id found.')
