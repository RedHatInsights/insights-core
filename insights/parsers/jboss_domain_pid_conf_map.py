"""
JbossDomainPidConfMap - command ``/bin/echo {jboss_domain_pid_conf_maps}``
==========================================================================

This command reads the output of datasource ``jboss_domain_pid_conf_maps``.

It looks for all the running domain-controller, host-controller and process-controller progresses
and store the parsed data in a dict. The key of dict is ``pid`` and value is ``(path_of_host_xml, path_of_domain_xml)``

host.xml and domain.xml are combined to configure a host-controller or domain-controller. If the same property
is defined both in host.xml and domain.xml, value in host.xml will overwrite the value set in domain.xml.
The reason to keep pid as key here is that it's easier to get property for a certain JBoss progress in insights plugin.

Typical contents of the pre_command::

    '2043|/home/jboss/jboss/machine1/domain/host-master.xml|/home/jboss/jboss/machine1/domain/domain.xml'

Parsed result::

    self.data = {2043: (/home/jboss/jboss/machine1/domain/host-master.xml, /home/jboss/jboss/machine1/domain/domain.xml)}

Examples:

    >>> jboss_pid_conf_map.get(2043)
    ('/home/jboss/jboss/machine1/domain/host-master.xml', '/home/jboss/jboss/machine1/domain/domain.xml')

Raises:
    insights.parsers.ParseException: if there is no running JBoss domain-controller, host-controller and process-controller progress
"""

from .. import parser, Parser, LegacyItemAccess

from insights.specs import Specs
from ..parsers import ParseException


@parser(Specs.jboss_domain_pid_conf_map)
class JbossDomainPidConfMap(Parser, LegacyItemAccess):
    def parse_content(self, content):
        self.data = {}
        if len(content) == 0:
            raise ParseException("Error: ",
                                 'there is no running JBoss domain-controller, host-controller and process-controller progress')
        l = content[0].split("|")
        self.data[int(l[0])] = (l[1], l[2])
