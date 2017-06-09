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
        # 'static' means 'on' to fulfill dependency of something else that is on
        valid_states = {'enabled', 'static', 'disabled', 'invalid'}
        on_states = {'enabled', 'static'}

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
            bool: True if service is enabled, False otherwise
        """
        return self.services.get(service_name, False)
