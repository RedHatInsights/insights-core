from .. import Mapper, mapper


@mapper("hostname")
class Hostname(Mapper):
    """Class for parsing ``hostname`` command output.

    Attributes:
        fqdn: The fully qualified domain name of the host. The same to
            ``hostname`` when domain part is not set.
        hostname: The hostname.
        domain: The domain get from the fqdn.
    """

    def parse_content(self, content):
        raw = None
        if len(content) == 1:
            raw = content[0].strip()
        self.fqdn = raw
        self.hostname = raw.split(".")[0] if raw else None
        self.domain = ".".join(raw.split(".")[1:]) if raw else None
