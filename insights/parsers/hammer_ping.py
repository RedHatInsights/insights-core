"""
HammerPing - command ``/usr/bin/hammer ping``
=============================================

The hammer ping parser reads the output of ``hammer ping``.  The list
of services is given in the ``service_list`` property by order.

Sample output of ``hammer ping``::

    candlepin:
        Status:          FAIL
        Server Response: Message: 404 Resource Not Found
    elasticsearch:
        Status:          ok
        Server Response: Duration: 35ms
    foreman_tasks:
        Status:          ok
        Server Response: Duration: 1ms

Examples:

    >>> hammer = shared[HammerPing]
    >>> 'unknown_service' in hammer.service_list
    False
    >>> hammer['candlepin']['Status']
    'FAIL'
    >>> hammer['candlepin']['Server Response']
    'Message: 404 Resource Not Found'
    >>> hammer.are_all_ok
    False
    >>> hammer.services_of_status('OK')
    ['elasticsearch', 'foreman_tasks']
"""
from insights import parser, CommandParser
from insights.parsers import get_active_lines
from insights.specs import Specs


@parser(Specs.hammer_ping)
class HammerPing(CommandParser, dict):
    """
    Read the ``hammer ping`` status and convert it to dictionaries of
    status and response information.

    Attributes:
        service_list (list): The list of service names in order
        errors (list): Any error messages encountered during parsing
        are_all_ok (bool): Are all services read correctly and are they all in 'ok' state?

    """
    def services_of_status(self, status='ok'):
        """
        List of the services in the given status.

        Arguments:
            status (str): the status code to search for, defaulting to 'ok'.
                The value is converted to lower case.

        Returns: List of service names having that status.
        """
        return sorted([svc for svc in self if self[svc]['Status'].lower() == status.lower()])

    def parse_content(self, content):
        self.service_list = []
        self.errors = []

        content = get_active_lines(content, comment_char="COMMAND>")
        service_name = None
        for line in content:
            items = [item.strip() for item in line.split(':', 1)]
            if len(items) == 2 and items[0]:
                if not items[1] and items[0] not in ['Status', 'Server Response']:
                    service_name = items[0]
                    self[service_name] = {}
                    continue
                elif service_name is not None:
                    self[service_name][items[0]] = items[1]
                    continue
            self.errors.append(line)
        self.are_all_ok = (
            not self.errors and
            all(self[item]['Status'] == 'ok' for item in self)
        )
        self.service_list = sorted(list(self.keys()))
