"""
Services - check ChkConfig and systemd UnitFiles
================================================

This shared reducer provides information about whether a given service is
enabled, using mappers for ``chkconfig`` (for RHEL 5 and 6) and ``systemd
list-unit-files`` (for RHEL 7 and above).

Examples:

    >>> svcs = shared[Services]
    >>> svcs.is_on('atd') # Can be 'atd' or 'atd.service'.
    True
    >>> svcs.is_on('systemd-journald.service')
    True
    >>> 'atd' in svcs
    True
    >>> svcs.service_line('atd')
    'atd.service                                 enabled'
    >>> 'disabled_service' in svcs
    False
    >>> 'nonexistent_service' in svcs
    False
"""

from .. import reducer
from ..mappers import chkconfig
from ..mappers.systemd import unitfiles


class ServicesReducer(object):
    """
    A reducer for working with enabled services, independent of which
    version of RHEL is in use.

    The interface closely follows the models of ChkConfig and UnitFiles:

    * ``is_on(service_name)`` and the ``service_name in Services``
      method return whether the service given is present **and enabled**.
    * ``service_line(service_name)`` returns the actual line that contained
      the service name.
    """
    def __init__(self, local, shared):
        self.services = {}
        self.parsed_lines = {}
        chk = shared.get(chkconfig.ChkConfig)
        svc = shared.get(unitfiles.UnitFiles)
        # PJW 2017-02-28 - It seems completely bizarre that a system would
        # have systemd installed and also have chkconfig output.  But I'm
        # leaving these as updates instead of equals just in case...
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
            service_name (str): service name (with or without '.service'
                suffix).

        Returns:
            bool: True if service is enabled, False otherwise.
        """
        return self.services.get(service_name + '.service',
                                 self.services.get(service_name, False))

    def service_line(self, service_name):
        """
        Returns the relevant line from the service listing.

        Args:
            service_name (str): service name (with or without '.service'
                suffix).

        Returns:
            str: True if service is enabled, False otherwise.
        """
        return self.parsed_lines.get(service_name + '.service',
                                     self.parsed_lines.get(service_name, ''))

    def __contains__(self, service_name):
        """
        Checks if the service **is enabled** in systemctl.  If you want
        to check whether a service is present but disabled, use the
        ``service_line`` method.

        Args:
            service_name (str): service name including '.service'

        Returns:
            bool: True if service is enabled, False otherwise
        """
        return self.is_on(service_name)


@reducer(requires=[[chkconfig.ChkConfig, unitfiles.UnitFiles]], shared=True)
class Services(ServicesReducer):
    """See `ServicesReducer` for attributes and methods."""
    pass
