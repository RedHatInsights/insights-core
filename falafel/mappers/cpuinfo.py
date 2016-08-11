from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
from collections import defaultdict


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

        for line in content:
            if line.strip():
                key, value = split(line)
                if key in mappings:
                    data[mappings[key]].append(value)

        return data

    def __iter__(self):
        for idx in range(len(self["cpus"])):
            yield self.get_processor_by_index(idx)

    @computed
    def cpu_count(self):
        return len(self["cpus"])

    @computed
    def socket_count(self):
        return len(self["sockets"])

    @computed
    def model_name(self):
        return self["models"][0]

    @computed
    def model_number(self):
        return self["model_ids"][0]

    @computed
    def vendor(self):
        return self["vendors"][0]

    def get_processor_by_index(self, index):
        return {k: v[index] for k, v in self.data.items()}
