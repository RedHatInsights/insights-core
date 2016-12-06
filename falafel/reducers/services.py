from .. import reducer
from ..mappers import chkconfig
from ..mappers.systemd import unitfiles


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
