from collections import defaultdict
from .. import MapperOutput, mapper, get_active_lines


class ModProbe(MapperOutput):
    pass


@mapper('modprobe.conf')
@mapper('modprobe.d')
def modprobe(context):
    d = defaultdict(dict)
    for line in get_active_lines(context.content):
        for mod_key in ["options", "install"]:
            if line.startswith(mod_key):
                parts = line.split()
                d[mod_key][parts[1]] = parts[2:]
    if d:
        return ModProbe(d)
