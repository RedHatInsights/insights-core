from falafel.core.plugins import mapper
from falafel.mappers import get_active_lines
import os


def parse_line(string):
    domain, type_, item, value = string.split()
    return {
        "domain": domain,
        "type": type_,
        "item": item,
        "value": int(value)
    }


@mapper("limits.conf")
@mapper("limits.d")
def get_limits(context):
    result = {}
    cfg_file = os.path.basename(context.path)
    if cfg_file.strip():
        lines = []
        for line in get_active_lines(context.content):
            parsed = parse_line(line)
            lines.append(parsed)
        result[cfg_file] = lines
        return result
