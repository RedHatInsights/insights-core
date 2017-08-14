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
from .. import parser, Parser


@parser("hammer_ping")
class HammerPing(Parser):
    """
    Read the ``hammer ping`` status and convert it to dictionaries of
    status and response information.

    """
    def __init__(self, *args, **kwargs):
        self.status_of_service = {}
        """dict: The status of each service, converted to lower case."""
        self.response_of_service = {}
        """dict: The response of each service, as is."""
        self.service_list = []
        """list: The list of service names in order."""
        self.errors = []
        """list: Any error messages encountered during parsing."""
        self.are_all_ok = False
        """bool: Were all services read correctly and are they all in 'ok' state?"""
        self.data = {}
        """
        .. warning::
            Deprecated attribute, please get what you want via accessing other attributes correspondingly.

        data (dict): The status and response information with key to the name of each service
        """
        super(HammerPing, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        # The first line should be a service
        if len(content[0].split()) > 1:
            self.errors.append(content[0])
        # Each service occupies 3 lines
        elif len(content) % 3 == 0:
            lines = iter(content)
            for service_no in range(0, len(content) / 3):
                service_line = lines.next().strip()
                status_line = lines.next().strip()
                response_line = lines.next().strip()

                service = service_line.split(':')[0]
                status = status_line.split(':', 1)[-1].strip().lower()
                response = response_line.split(':', 1)[-1].strip()

                self.service_list.append(service)
                self.status_of_service[service] = status
                self.response_of_service[service] = response

                # Deprecated attribute
                self.data[service] = {'status': status, 'response': response}
        else:
            self.errors.extend(content)

        self.are_all_ok = (
            not self.errors and
            all(status == 'ok' for status in self.status_of_service.values())
        )

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

    def __len__(self):
        """
        .. warning::
            Deprecated function, please get the length of :attr:`service_list` instead.

        int: the number of items in the underlying data.
        """
        return len(self.data)

    def is_ok(self, service):
        """
        .. warning::
            Deprecated function, please use the :attr:`status_of_service` instead.

        bool: is the service defined in the data and is it listed as 'ok'?
        """
        return service in self.data and 'ok' == self.data[service]['status']

    def response_of(self, service):
        """
        .. warning::
            Deprecated function, please use the :attr:`response_of_service` instead.

        str: the status of the given service, or '' if the service is not
        in the hammer ping output.
        """
        if service not in self.data:
            return ''
        return self.data[service]['response']
