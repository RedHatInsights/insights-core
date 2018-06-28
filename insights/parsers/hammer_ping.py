"""
HammerPing - command ``/usr/bin/hammer ping``
=============================================

The hammer ping parser reads the output of ``hammer ping`` and turns it into
a dictionary of service statuses in the ``status_of_service`` property and
the corresponding response in the ``response_of_service`` property.  The list
of services by name in the order they were discovered is given in the
``service_list`` property.

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
    >>> hammer.status_of_service['candlepin']
    'FAIL'
    >>> hammer.response_of_service['candlepin']
    'Message: 404 Resource Not Found'
    >>> hammer.are_all_ok
    False
    >>> hammer.services_of_status('OK')
    ['elasticsearch', 'foreman_tasks']
"""
from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.hammer_ping)
class HammerPing(CommandParser):
    """
    Read the ``hammer ping`` status and convert it to dictionaries of
    status and response information.

    Attributes:
        status_of_service (dict): The status of each service, converted to lower case
        response_of_service (dict): The response of each service, as is
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
        status = status.lower()
        return [svc for svc in self.service_list
                if self.status_of_service[svc] == status]

    def parse_content(self, content):
        self.status_of_service = {}
        self.response_of_service = {}
        self.service_list = []
        self.errors = []
        self.are_all_ok = False

        # The first line should be a service
        if len(content[0].split()) > 1:
            self.errors.append(content[0])
        # Each service occupies 3 lines
        elif len(content) % 3 == 0:
            lines = iter(content)
            for service_no in range(0, len(content) // 3):
                service_line = next(lines).strip()
                status_line = next(lines).strip()
                response_line = next(lines).strip()

                service = service_line.split(':')[0]
                status = status_line.split(':', 1)[-1].strip().lower()
                response = response_line.split(':', 1)[-1].strip()

                self.service_list.append(service)
                self.status_of_service[service] = status
                self.response_of_service[service] = response
        else:
            self.errors.extend(content)

        self.are_all_ok = (
            not self.errors and
            all(status == 'ok' for status in self.status_of_service.values())
        )
