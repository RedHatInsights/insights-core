from collections import defaultdict
from .. import Mapper, mapper


@mapper("hosts")
class Hosts(Mapper):

    def parse_content(self, content):
        self.data = defaultdict(list)
        for line in content:
            line = line.strip()
            if "#" in line:
                line, _, _ = line.partition("#")
            if line:
                try:
                    ip, hostnames = line.split(None, 1)
                    self.data[ip].extend(hostnames.split())
                except:
                    pass

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
