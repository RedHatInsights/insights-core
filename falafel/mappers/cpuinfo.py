from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
from falafel.mappers import get_active_lines
from collections import defaultdict
from falafel.util import defaults


@mapper('cpuinfo')
class CpuInfo(MapperOutput):

    @staticmethod
    def parse_content(content):

        def split(line):
            return [p.strip() for p in line.split(":", 1)]

        data = defaultdict(list)
        mappings = {
            "processor": "cpus",
            "physical id": "sockets",
            "vendor_id": "vendors",
            "model name": "models",
            "model": "model_ids",
            "cpu family": "families",
            "cpu MHz": "clockspeeds",
            "cache size": "cache_sizes"
        }

        for line in get_active_lines(content, comment_char="COMMAND>"):
            key, value = split(line)
            if key in mappings:
                data[mappings[key]].append(value)

        return data

    def __iter__(self):
        for idx in range(len(self["cpus"])):
            yield self.get_processor_by_index(idx)

    @computed
    @defaults()
    def cpu_speed(self):
        return self["clockspeeds"][0]

    @computed
    @defaults()
    def cache_size(self):
        return self["cache_sizes"][0]

    @computed
    @defaults()
    def cpu_count(self):
        return len(self["cpus"])

    @computed
    @defaults()
    def socket_count(self):
        return len(self["sockets"])

    @computed
    @defaults()
    def model_name(self):
        return self["models"][0]

    @computed
    @defaults()
    def model_number(self):
        return self["model_ids"][0]

    @computed
    @defaults()
    def vendor(self):
        return self["vendors"][0]

    def get_processor_by_index(self, index):
        return {k: v[index] for k, v in self.data.items()}
