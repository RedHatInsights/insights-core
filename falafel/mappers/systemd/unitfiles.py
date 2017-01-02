from ... import Mapper, mapper
from .. import get_active_lines


@mapper('systemctl_list-unit-files')
class UnitFiles(Mapper):
    """
    A mapper for working with data gathered from `systemctl list-unit-files` utility.
    """
    def __init__(self, *args, **kwargs):
        self.services = {}
        self.parsed_lines = {}
        super(UnitFiles, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content
        """
        # 'static' means 'on' to fulfill dependency of something else that is on
        valid_states = {'enabled', 'static', 'disabled'}
        on_states = valid_states - {'disabled'}

        for line in get_active_lines(content):
            parts = line.split(None)  # AWK like split, strips whitespaces
            if len(parts) == 2 and any(part in valid_states for part in parts):
                service, state = parts
                enabled = state in on_states
                self.services[service] = enabled
                self.parsed_lines[service] = line

    def is_on(self, service_name):
        """
        Checks if the service is enabled in systemctl.

        Args:
            service_name (str): service name including '.service'

        Returns:
            bool: True if service is enabled, False otherwise
        """
        return self.services.get(service_name, False)
