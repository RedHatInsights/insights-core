"""
DuplicateMachine - file ``insights-commands/duplidate_machine_id``
==================================================================
"""

from insights.core.plugins import parser
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.specs import Specs


@parser(Specs.duplicate_machine_id)
class DuplicateMachine(Parser):
    """
    Parse the machine info in the file "insights-commands/duplidate_machine_info".

    Sample input::

        dc194312-8cdd-4e75-8cf1-2094bf666f45 hostname1,hostname2

    Attributes:
        duplicate_id (str): the duplicate machine id
        hostnames (list): A list of the hostnames with the same machine id

    Examples:
        >>> type(machine_id_obj)
        <class 'insights.parsers.machine_id.DuplicateMachine'>
        >>> machine_id_obj.duplicate_id
        'dc194312-8cdd-4e75-8cf1-2094bf666f45'
        >>> machine_id_obj.hostnames
        ['hostname1', 'hostname2']

    Raises:
        SkipComponent: when there is no expected content in the file
    """
    def parse_content(self, content):
        if len(content) == 1:
            machine_info = content[0].split(None, 1)
            if len(machine_info) == 2:
                self.duplicate_id = machine_info[0].strip()
                self.hostnames = machine_info[1].strip().split(',')
        if not hasattr(self, 'duplicate_id'):
            raise SkipComponent('No expected machine id found.')
