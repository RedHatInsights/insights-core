from .. import Mapper, mapper


@mapper('chkconfig')
class ChkConfig(Mapper):
    def parse_content(self, content):
        # static means "on" to fulfill dependency of something else that
        # is on
        valid = [':on', ':off']
        self.data = {}
        for line in content:
            if any(v in line for v in valid):
                key = line.split()[0].strip()
                value = ':on' in line
                self.data[key] = value

    def is_on(self, service):
        return self.data.get(service, False)
