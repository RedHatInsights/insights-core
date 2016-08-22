from falafel.core import MapperOutput
from falafel.core.plugins import mapper


@mapper('systemctl_list-unit-files')
class UnitFiles(MapperOutput):
    @classmethod
    def parse_content(cls, content):
        # static means "on" to fulfill dependency of something else that
        # is on
        on = ['enabled', 'static']
        data = {}

        #skip header
        for line in content[1:]:
            key = line.split()[0].strip()
            value = any(v in line for v in on)
            data[key] = value
        return data

    def is_on(self, service):
        return self.get(service)
