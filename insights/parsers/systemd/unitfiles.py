"""
unitfiles - systemctl unit files (services)
===========================================

The UnitFiles class parses the output of `/bin/systemctl list-unit-files` and provides
information about enabled services and existing services.

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

from ... import Parser, parser
from .. import get_active_lines


@parser('systemctl_list-unit-files')
class UnitFiles(Parser):
    """
    A parser for working with data gathered from `systemctl list-unit-files` utility.
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
        # man systemctl - "is-enabled" knows these states
        valid_states = {'enabled', 'enabled-runtime', 'linked', 'linked-runtime', 'masked',
                        'masked-runtime', 'static', 'indirect', 'disabled', 'generated',
                        'transient', 'bad', 'invalid'}
        # man systemctl - "is-enabled" considers these to be enabled
        on_states = {'enabled', 'enabled-runtime', 'static', 'indirect', 'generated', 'transient'}

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
