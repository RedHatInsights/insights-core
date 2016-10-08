from collections import defaultdict
from .. import Mapper, mapper, defaults, get_active_lines, LegacyItemAccess


@mapper('cpuinfo')
class CpuInfo(LegacyItemAccess, Mapper):

    def parse_content(self, content):

        def split(line):
            return [p.strip() for p in line.split(":", 1)]

        self.data = defaultdict(list)
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
                self.data[mappings[key]].append(value)

    def __iter__(self):
        for idx in range(len(self["cpus"])):
            yield self.get_processor_by_index(idx)

    @property
    @defaults()
    def cpu_speed(self):
        return self.data["clockspeeds"][0]

    @property
    @defaults()
    def cache_size(self):
        return self.data["cache_sizes"][0]

    @property
    @defaults()
    def cpu_count(self):
        return len(self.data["cpus"])

    @property
    @defaults()
    def socket_count(self):
        return len(self.data["sockets"])

    @property
    @defaults()
    def model_name(self):
        return self.data["models"][0]

    @property
    @defaults()
    def model_number(self):
        return self.data["model_ids"][0]

    @property
    @defaults()
    def vendor(self):
        return self.data["vendors"][0]

    def get_processor_by_index(self, index):
        return {k: v[index] for k, v in self.data.items()}
