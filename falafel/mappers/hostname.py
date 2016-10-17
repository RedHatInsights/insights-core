from .. import Mapper, mapper


@mapper("facts")
@mapper("hostname")
class Hostname(Mapper):

    def parse_content(self, content):
        fqdn = None
        if len(content) == 1:
            fqdn = content[0].strip()
        elif len(content) > 1:
            for line in content:
                if line.startswith('fqdn'):
                    fqdn = line.split()[-1]
        self.fqdn = fqdn
        self.hostname = fqdn.split(".")[0] if fqdn else None
        self.domain = ".".join(fqdn.split(".")[1:]) if fqdn else None
