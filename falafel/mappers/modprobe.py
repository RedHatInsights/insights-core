from collections import defaultdict
from .. import Mapper, mapper, get_active_lines, LegacyItemAccess


@mapper('modprobe.conf')
@mapper('modprobe.d')
class ModProbe(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        self.data = defaultdict(dict)
        for line in get_active_lines(content):
            for mod_key in ["options", "install"]:
                if line.startswith(mod_key):
                    parts = line.split()
                    self.data[mod_key][parts[1]] = parts[2:]

        self.data = dict(self.data)
