"""
KatelloServiceStatus - command ``katello-service status``
=========================================================

The KatelloServiceStatus parser only reads the last line of command
``katello-service status`` to get the list of the failed services.

Note:
    Since we only care about the failed services, this parser only process the
    last line which contains the list of the failed services.

The last line of the output of ``katello-service status``::

    Some services failed to status: tomcat6,httpd


Examples:

    >>> kss_ = shared[KatelloServiceStatus]
    >>> kss.is_ok
    False
    >>> kss.failed_services
    ['tomcat6', 'httpd']

"""
from .. import parser, add_filter, CommandParser
from insights.specs import Specs

add_filter(Specs.katello_service_status, ['Some services failed to status',
                                      'Success'])


@parser(Specs.katello_service_status)
class KatelloServiceStatus(CommandParser):
    """
    Read the ``katello-service status`` and get the list of ``failed_services``.

    Attributes:
        failed_services (list): The list of failed services.
        is_ok (bool): Is there no failed service?

    """
    def parse_content(self, content):
        self.failed_services = []
        self.is_ok = False

        for line in content[::-1]:
            if 'Some services failed to status:' in line:
                failed_services = line.split(':')[-1].strip()
                self.failed_services = [s for s in failed_services.split(',') if s]

        self.is_ok = len(self.failed_services) == 0
