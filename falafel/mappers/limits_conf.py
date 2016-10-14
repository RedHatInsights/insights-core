import os
from .. import mapper, get_active_lines


def parse_line(string):
    domain, type_, item, value = string.split()
    # Special '-1' value for unlimited, also represented as strings
    if value == 'unlimited' or value == 'infinity':
        value = -1
    else:
        value = int(value)
    return {
        "domain": domain,
        "type": type_,
        "item": item,
        "value": value
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
