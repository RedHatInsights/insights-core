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
        UNIT FILE                                     STATE
        mariadb.service                               enabled
        neutron-openvswitch-agent.service             enabled
        neutron-ovs-cleanup.service                   enabled
        neutron-server.service                        enabled
        runlevel0.target                              disabled
        runlevel1.target                              disabled
        runlevel2.target                              enabled

    Example:

        >>> conf.is_on('mariadb.service')
        True
        >>> conf.is_on('runlevel0.target')
        False
        >>> conf.exists('neutron-server.service')
        True
        >>> conf.exists('runlevel1.target')
        True
        >>> 'mariadb.service' in conf.services
        True
        >>> 'runlevel0.target' in conf.services
        True
        >>> 'nonexistent-service.service' in conf.services
        False
        >>> conf.services['mariadb.service']
        True
        >>> conf.services['runlevel1.target']
        False
        >>> conf.services['nonexistent-service.service']
        Traceback (most recent call last):
          File "<doctest insights.parsers.systemd.unitfiles.UnitFiles[11]>", line 1, in <module>
            conf.services['nonexistent-service.service']
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

        UNIT                                LOAD   ACTIVE SUB       DESCRIPTION
        sockets.target                      loaded active active    Sockets
        swap.target                         loaded active active    Swap
        systemd-shutdownd.socket            loaded active listening Delayed Shutdown Socket
        neutron-dhcp-agent.service          loaded active running   OpenStack Neutron DHCP Agent
        neutron-openvswitch-agent.service   loaded active running   OpenStack Neutron Open vSwitch Agent
        ...
        unbound-anchor.timer                loaded active waiting   daily update of the root trust anchor for DNSSEC

        LOAD   = Reflects whether the unit definition was properly loaded.
        ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
        SUB    = The low-level unit activation state, values depend on unit type.

        161 loaded units listed. Pass --all to see loaded but inactive units, too.
        To show all installed unit files use 'systemctl list-unit-files'.

    Example:

        >>> units.get_service_details('swap.target') == {'LOAD': 'loaded', 'ACTIVE': 'active', 'SUB': 'active', 'UNIT': 'swap.target', 'DESCRIPTION': 'Swap'}
        True
        >>> units.unit_list['swap.target'] == {'LOAD': 'loaded', 'ACTIVE': 'active', 'SUB': 'active', 'UNIT': 'swap.target', 'DESCRIPTION': 'Swap'}
        True
        >>> units.is_active('swap.target')
        True
        >>> units.get_service_details('random.service') == {'LOAD': None, 'ACTIVE': None, 'SUB': None, 'UNIT': None, 'DESCRIPTION': None}
        True
    """
    EMPTY_DETAILS = {'LOAD': None, 'ACTIVE': None, 'SUB': None, 'UNIT': None, 'DESCRIPTION': None}

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

        service_details = {}
        if (len(parts) >= 4 and any(part in valid_states for part in parts) and
                any(unit in parts[0] for unit in valid_units)):
            service_details['UNIT'] = parts[0]
            service_details['LOAD'] = parts[1]
            service_details['ACTIVE'] = parts[2]
            service_details['SUB'] = parts[3]
            service_details['DESCRIPTION'] = ' '.join(parts[4:]) if len(parts) > 4 else None

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
            # If this is a heading line, then ignore this line
            if line.startswith('UNIT '):
                continue

            parts = line.split(None)  # AWK like split, strips whitespaces
            first_part = 0
            if parts[0] == BULLET_CHAR_U or parts[0].encode('utf-8') == BULLET_CHAR_B or parts[0] == '*':
                first_part = 1

            # If past the end of the list then quit
            if parts[first_part] in ['LOAD', 'ACTIVE', 'SUB']:
                break

            service_details = self.parse_service_details(parts[first_part:])
            if service_details:
                self.unit_list[parts[first_part]] = service_details

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
        return self.unit_list.get(service_name, ListUnits.EMPTY_DETAILS)

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

    def is_failed(self, service_name):
        """
        Return the ACTIVE state of service managed by systemd.

        Args:
            service_name (str): service name including its extension.

        Returns:
            bool: True if service is failed, False in all other states.
        """
        return self.get_service_details(service_name)['ACTIVE'] == 'failed'

    @property
    def service_names(self):
        """list: Returns a list of all UNIT names."""
        return list(self.unit_list.keys())
