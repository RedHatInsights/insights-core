from .. import Mapper, mapper


@mapper("hostname")
class Hostname(Mapper):

    def parse_content(self, content):
        content = content[0].strip()
        self.fqdn = content
        self.hostname = content.split(".")[0]
        self.domain = ".".join(content.split(".")[1:])
