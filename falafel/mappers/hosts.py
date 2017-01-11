from collections import defaultdict
from .. import Mapper, mapper


@mapper("hosts")
class Hosts(Mapper):

    def parse_content(self, content):
        host_data = defaultdict(list)
        for line in content:
            line = line.strip()
            if "#" in line:
                line, _, _ = line.partition("#")
            if line:
                try:
                    ip, hostnames = line.split(None, 1)
                    host_data[ip].extend(hostnames.split())
                except:
                    pass
        self.data = dict(host_data)

    @property
    def all_names(self):
        names = set()
        for host_set in self.data.values():
            names.update(host_set)
        return names

    def get_nonlocal(self):
        return {ip: host_list
                for ip, host_list in self.data.items()
                if ip not in ("127.0.0.1", "::1")}
