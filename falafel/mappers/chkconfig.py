from .. import MapperOutput, mapper


@mapper('chkconfig')
class ChkConfig(MapperOutput):
    @classmethod
    def parse_content(cls, content):
        # static means "on" to fulfill dependency of something else that
        # is on
        valid = [':on', ':off']
        data = {}
        for line in content:
            if any(v in line for v in valid):
                key = line.split()[0].strip()
                value = ':on' in line
                data[key] = value
        return data

    def is_on(self, service):
        return self.get(service, False)
