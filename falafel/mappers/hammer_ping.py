"""
hammer_ping - command ``/usr/bin/hammer ping``
==============================================

The hammer ping mapper reads the output of ``hammer ping`` and turns it into
a dictionary of service statuses in the ``data`` property.  Each service has
its status stored in the 'status' key and its response in the 'repsonse' key;
the response is trimmed so that it is either the response time in milliseonds
or the HTTP message.

The easier way to access this data is with the two helper methods:

* ``is_ok(service)`` returns True if the service is defined in the ``hammer
  ping`` output and if its status is given as '**ok**', or False otherwise.
* ``response_of(service)`` returns the server response (after the 'Message:'
  or 'Duration:' text) if the service is listed in the ``hammer ping`` output,
  or '' otherwise.

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

    >>> status = shared[HammerPing]
    >>> status.data['candlepin'] # The complete data record
    {'status': 'FAIL', 'response': '404 Resource Not Found'}
    >>> status.data['elasticsearch']
    {'status': 'ok', 'response', '1ms'}
    >>> status.data['candlepin']['status'] == 'on'
    False
    >>> status.is_ok('candlepin_auth') # New style accessor
    False
    >>> status.is_ok('foreman_tasks')
    True
    >>> status.is_ok('unknown_service') # Service not OK if not found
    False
    >>> status.response_of('foreman_tasks')
    '1ms'
    >>> status.response_of('candlepin')
    '404 Resource Not Found'
"""
from .. import mapper, Mapper


@mapper("hammer_ping")
class HammerPing(Mapper):
    """
    Read the ``hammer ping`` status and convert it to a dictionary of
    response statuses and information.

    The status and response information are available in the ``data``
    property keyed to the name of each service, and the ``is_ok`` and
    ``response_of`` methods are provided as conveniences.
    """
    def __len__(self):
        """
        (int): the number of items in the underlying data.
        """
        return len(self.data)

    def is_ok(self, service):
        """
        (bool): is the service defined in the data and is it listed as 'ok'?
        """
        return service in self.data and 'ok' == self.data[service]['status']

    def response_of(self, service):
        """
        (str): the status of the given service, or '' if the service is not
        in the hammer ping output.
        """
        if service not in self.data:
            return ''
        return self.data[service]['response']

    def parse_content(self, content):
        i = 0
        dic = {}
        while i < len(content):
            service_line, status_line, response_line = content[i:i + 3]
            status = status_line.split(':', 1)[1].strip()
            response = response_line.split(':', 2)[2].strip()
            dic[service_line.strip(': ')] = {
                'status': status,
                'response': response
            }
            # status messages are three lines long - skip three lines.
            i += 3
        self.data = dic
