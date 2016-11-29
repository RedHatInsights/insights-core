from .. import Mapper, mapper


@mapper('chkconfig')
class ChkConfig(Mapper):
    """
    A mapper for working with data gathered from `chkconfig` utility.
    """
    def __init__(self, *args, **kwargs):
        self.services = {}
        self.parsed_lines = {}
        super(ChkConfig, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content
        """
        valid_states = {':on', ':off'}
        for line in content:
            if any(state in line for state in valid_states):
                service = line.split()[0].strip()
                enabled = ':on' in line  # Store boolean value
                self.services[service] = enabled
                self.parsed_lines[service] = line

    def is_on(self, service_name):
        """
        Checks if the service is enabled in chkconfig.

        Args:
            service_name (str): service name

        Returns:
            bool: True if service is enabled, False otherwise
        """
        return self.services.get(service_name, False)
