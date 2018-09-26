"""
Units Manged By Systemctl (services)
====================================

Parsers included in this module are:

ListUnits - command ``/bin/systemctl list-units``
-------------------------------------------------

UnitFiles - command ``/bin/systemctl list-unit-files``
------------------------------------------------------

"""
from .. import get_active_lines
from ... import Parser, parser
from insights.specs import Specs


@parser(Specs.systemctl_list_unit_files)
class UnitFiles(Parser):
    """
    The UnitFiles class parses the output of ``/bin/systemctl list-unit-files`` and provides
    information about enabled services.

    Output of Command::

        mariadb.service                               enabled
        neutron-openvswitch-agent.service             enabled
        neutron-ovs-cleanup.service                   enabled
        neutron-server.service                        enabled
        runlevel0.target                              disabled
        runlevel1.target                              disabled
        runlevel2.target                              enabled

    Example:

        >>> conf = shared[UnitFiles]
        >>> conf.is_on('existing-enabled-service.service')
        True
        >>> conf.is_on('existing-disabled-service.service')
        False
        >>> conf.is_on('nonexistent-service.service')
        False
        >>> conf.exists('existing-enabled-service.service')
        True
        >>> conf.exists('existing-disabled-service.service')
        True
        >>> conf.exists('nonexistent-service.service')
        False
        >>> 'existing-enabled-service.service' in conf.services
        True
        >>> 'existing-disabled-service.service' in conf.services
        True
        >>> 'nonexistent-service.service' in conf.services
        False
        >>> conf.services['existing-enabled-service.service']
        True
        >>> conf.services['existing-disabled-service.service']
        False
        >>> conf.services['nonexistent-service.service']
        KeyError: 'nonexistent-service.service'
    """

    def __init__(self, *args, **kwargs):
        self.services = {}
        """dict: Dictionary of bool indicating if service is enabled,
        access by service name ."""
        self.service_list = []
        """list: List of service names in order of appearance."""
        self.parsed_lines = {}
        """dict: Dictionary of content lines access by service name."""
        super(UnitFiles, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
        # 'static' means 'on' to fulfill dependency of something else that is on
        # man systemctl - "is-enabled" knows these states
        valid_states = set(['enabled', 'enabled-runtime', 'linked', 'linked-runtime', 'masked',
                            'masked-runtime', 'static', 'indirect', 'disabled', 'generated',
                            'transient', 'bad', 'invalid'])
        # man systemctl - "is-enabled" considers these to be enabled
        on_states = set(['enabled', 'enabled-runtime', 'static', 'indirect', 'generated', 'transient'])

        for line in get_active_lines(content):
            parts = line.split(None)  # AWK like split, strips whitespaces
            if len(parts) == 2 and any(part in valid_states for part in parts):
                service, state = parts
                enabled = state in on_states
                self.services[service] = enabled
                self.parsed_lines[service] = line
                self.service_list.append(service)

    def is_on(self, service_name):
        """
        Checks if the service is enabled in systemctl.

        Args:
            service_name (str): service name including '.service'

        Returns:
            Union[bool, None]: True if service is enabled, False if it is disabled. None if the
            service doesn't exist.
        """
        return self.services.get(service_name, None)

    def exists(self, service_name):
        """
        Checks if the service is listed in systemctl.

        Args:
           service_name (str): service name including '.service'

        Returns:
            bool: True if service exists, False otherwise.
        """
        return service_name in self.service_list


@parser(Specs.systemctl_list_units)
class ListUnits(Parser):

    """
    The ListUnits class parses the output of ``/bin/systemctl list-units`` and provides
    information about all the services listed under it.

    Output of Command::

        sockets.target                      loaded active active    Sockets
        swap.target                         loaded active active    Swap
        systemd-shutdownd.socket            loaded active listening Delayed Shutdown Socket
        neutron-dhcp-agent.service          loaded active running   OpenStack Neutron DHCP Agent
        neutron-openvswitch-agent.service   loaded active running   OpenStack Neutron Open vSwitch Agent

    Example:

        >>> units.get_service_details('swap.target')
        {'LOAD': 'loaded', 'ACTIVE': 'active', 'SUB': 'active', 'UNIT': 'swap.target'}
        >>> units.unit_list['swap.target']
        {'LOAD': 'loaded', 'ACTIVE': 'active', 'SUB': 'active', 'UNIT': 'swap.target'}
        >>> units.is_active('swap.target')
        True
        >>> units.unit_list['random.service']
        {'LOAD': None, 'ACTIVE': None, 'SUB': None, 'UNIT': None}
    """
    def __init__(self, *args, **kwargs):
        self.unit_list = {}
        """dict: Dictionary service detail like active, running, exited, dead"""
        super(ListUnits, self).__init__(*args, **kwargs)

    def parse_service_details(self, parts):
        # man systemctl - "is-enabled" knows these states
        valid_states = set(['invalid', 'loaded', 'inactive', 'active',
                            'exited', 'running', 'failed', 'mounted', 'waiting', 'plugged'])

        valid_units = set(['service', 'socket', 'device', 'mount', 'automount', 'swap', 'target',
                           'path', 'timer', 'slice', 'scope'])

        if any(part in valid_states for part in parts):
            service_details = {}
            service_details['LOAD'] = parts[1]
            service_details['ACTIVE'] = parts[2]
            service_details['SUB'] = parts[3]
            if any(unit in parts[0] for unit in valid_units):
                service_details['UNIT'] = parts[0]
                return service_details

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """
        BULLET_CHAR_U = u'\u25CF'
        BULLET_CHAR_B = b"\xe2\x97\x8f"
        for line in get_active_lines(content):
            parts = line.split(None)  # AWK like split, strips whitespaces
            if parts[0] == BULLET_CHAR_U or parts[0].encode('utf-8') == BULLET_CHAR_B or parts[0] == '*':
                self.unit_list[parts[1]] = self.parse_service_details(parts[1:])
            else:
                self.unit_list[parts[0]] = self.parse_service_details(parts)

    def get_service_details(self, service_name):
        """
        Return the service details collected by systemctl.

        Args:
            service_name (str): service name including its extension.

        Returns:
            dict: Dictionary containing details for the service.
            if service is not present dictonary values will be `None`::

            {'LOAD': 'loaded', 'ACTIVE': 'active', 'SUB': 'running', 'UNIT': 'neutron-dhcp-agent.service'}
        """
        empty_details = {'LOAD': None, 'ACTIVE': None, 'SUB': None, 'UNIT': None}
        return self.unit_list.get(service_name, empty_details)

    def is_loaded(self, service_name):
        """
        Return the LOAD state of service managed by systemd.

        Args:
            service_name (str): service name including its extension.

        Returns:
            bool: True if service is loaded False if not loaded
        """
        return self.get_service_details(service_name)['LOAD'] == 'loaded'

    def is_active(self, service_name):
        """
        Return the ACTIVE state of service managed by systemd.

        Args:
            service_name (str): service name including its extension.

        Returns:
            bool: True if service is active False if inactive
        """
        return self.get_service_details(service_name)['ACTIVE'] == 'active'

    def is_running(self, service_name):
        """
        Return the SUB state of service managed by systemd.

        Args:
            service_name (str): service name including its extension.

        Returns:
            bool: True if service is running False in all other states.
        """
        return self.get_service_details(service_name)['SUB'] == 'running'
