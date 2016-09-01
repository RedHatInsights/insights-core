from falafel.core import MapperOutput
from falafel.core.plugins import mapper
from falafel.mappers import get_active_lines


@mapper('systemctl_list-unit-files')
class UnitFiles(MapperOutput):
    @staticmethod
    def parse_content(content):

        # static means "on" to fulfill dependency of something else that
        # is on
        states = set(['enabled', 'static', 'disabled'])
        on = states - set(['disabled'])

        data = {}

        for line in get_active_lines(content):
            parts = line.split(None)
            if len(parts) != 2 or not any(p in states for p in parts):
                continue
            k, v = [p.strip() for p in parts]
            value = any(s == v for s in on)
            data[k] = value
        return data

    def is_on(self, service):
        return self.get(service)
