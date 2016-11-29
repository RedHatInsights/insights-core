from .. import reducer
from ..mappers import chkconfig
from ..mappers.systemd import unitfiles


SERVICE_ENABLED = 'SERVICE_ENABLED'
SERVICES_ENABLED = 'SERVICES_ENABLED'


@reducer(requires=[[chkconfig.ChkConfig, unitfiles.UnitFiles]], shared=True)
class Services(object):
    """
    A reducer for working with enabled services independently on utility which checks for them.
    """
    def __init__(self, local, shared):
        self.services = {}
        self.parsed_lines = {}
        chk = shared.get(chkconfig.ChkConfig)
        svc = shared.get(unitfiles.UnitFiles)
        if chk:
            self.services.update(chk.services)
            self.parsed_lines.update(chk.parsed_lines)
        if svc:
            self.services.update(svc.services)
            self.parsed_lines.update(svc.parsed_lines)

    def is_on(self, service_name):
        """
        Checks if the service is enabled on the system.

        Args:
            service_name (str): service name

        Returns:
            bool: True if service is enabled, False otherwise
        """
        return self.services.get(service_name,
                                 self.services.get(service_name + '.service', False))

    def service_is_enabled(self, service_name):
        """
        Check for enabled system service.

        For debugging purposes returns the matched line.

        Args:
            service_name (str): service name to look for

        Returns:
            dict: the matched line in the following format, otherwise empty dict:

                  {SERVICE_ENABLED: line}
        """
        if self.is_on(service_name):
            line = self.parsed_lines.get(service_name,
                                         self.parsed_lines.get(service_name + '.service'))
            return {SERVICE_ENABLED: line}
        else:
            return {}

    def services_are_enabled(self, *service_names):
        """
        Check for system services enabled.

        For debugging purposes returns the matched lines.

        Args:
            *service_names (str): service names to look for

        Returns:
            dict: list of found service names and their matched lines in the following format,
                  otherwise empty dict:

                  {SERVICES_ENABLED: {service_1: line_1, service_2: line_2}}
        """
        services = {}

        for service_name in service_names:
            if self.is_on(service_name):
                line = self.parsed_lines.get(service_name,
                                             self.parsed_lines.get(service_name + '.service'))
                services[service_name] = line

        if services:
            return {SERVICES_ENABLED: services}
        else:
            return {}
