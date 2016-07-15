from collections import defaultdict
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


class Hosts(MapperOutput):

    @computed
    def all_names(self):
        names = set()
        for host_set in self.data.values():
            names.update(host_set)
        return names


@mapper("hosts")
def hosts(context):
    d = defaultdict(list)
    for line in context.content:
        line = line.strip()
        if "#" in line:
            line, _, _ = line.partition("#")
        if line:
            try:
                ip, hostnames = line.split(None, 1)
                d[ip].extend(hostnames.split())
            except:
                pass
    return Hosts(d)
