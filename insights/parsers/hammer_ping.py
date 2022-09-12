"""
HammerPing - command ``/usr/bin/hammer ping``
=============================================

The hammer ping parser reads the output of ``hammer ping`` and turns it into
a dictionary. The key is the service name, and the value is a dict of all the
service info.

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

    >>> type(hammer_ping)
    <class 'insights.parsers.hammer_ping.HammerPing'>
    >>> 'unknown_service' in hammer_ping.service_list
    False
    >>> hammer_ping['candlepin']['Status']
    'FAIL'
    >>> hammer_ping['candlepin']['Server Response']
    'Message: 404 Resource Not Found'
    >>> hammer_ping.are_all_ok
    False
    >>> hammer_ping.services_of_status('OK')
    ['elasticsearch', 'foreman_tasks']
"""
from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException


@parser(Specs.hammer_ping)
class HammerPing(CommandParser, dict):
    """
    Read the ``hammer ping`` status and convert it to dictionaries of
    status and response information.

    Attributes:
        errors (list): Any error messages encountered during parsing
        raw_content(list): The original output of hammer ping
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

    @property
    def service_list(self):
        """Return a list of service in order """
        return sorted(self.keys())

    @property
    def are_all_ok(self):
        """Return boolean value to indicate if all the service are running normally"""
        return self._is_normal

    def parse_content(self, content):
        self.status_of_service = {}
        self.response_of_service = {}
        self.errors = []
        self.raw_content = content
        comment_char = "COMMAND>"
        service_name = None
        content = list(filter(None, (line.split(comment_char, 1)[0].rstrip() for line in content)))
        if not content:
            raise SkipException("Empty output.")

        for line in content:
            items = [item for item in line.split(':', 1)]
            if len(items) == 2 and items[0]:
                if not items[1] and len(items[0].split()) == 1 and not items[0][0].isspace():
                    service_name = items[0].strip()
                    self[service_name] = {}
                    continue
                elif service_name is not None and items[0][0].isspace():
                    items[0] = items[0].strip()
                    items[1] = items[1].strip()
                    self[service_name][items[0]] = items[1]
                    if items[0] == 'Status':
                        self.status_of_service[service_name] = items[1].lower()
                    if items[0] == 'Server Response':
                        self.response_of_service[service_name] = items[1]
                    continue

            self.errors.append(line.strip())
        self._is_normal = (not self.errors and all([self[item]['Status'] == 'ok' for item in self]))
