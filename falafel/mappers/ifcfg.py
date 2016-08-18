from falafel.mappers import get_active_lines
from falafel.core.plugins import mapper
import json

JSON_FIELDS = ["TEAM_CONFIG", "TEAM_PORT_CONFIG"]

QUOTES = "\"'"


@mapper("ifcfg")
def ifcfg(context):
    """
    Parse `ifcfg-` file,return a dict contain ifcfg config file info.
    "iface" key is interface name parse from file name
    `TEAM_CONFIG`, `TEAM_PORT_CONFIG` will return a dict with user config dict
    `BONDING_OPTS` also will return a dict
    """
    result = {
        "iface": context.path.rsplit("-", 1)[1]
    }
    for line in get_active_lines(context.content):
        key, _, value = line.partition("=")
        key = key.strip().strip(QUOTES)

        # In some cases we want to know what the actual value-side
        # of the key is
        if key == "BONDING_OPTS":
            result["raw_bonding_value"] = value

        value = value.strip().strip(QUOTES)
        if key in JSON_FIELDS:
            value = json.loads(value.replace("\\", ""))
        if key == "BONDING_OPTS":
            value_map = {}
            for key_value_pair in value.split():
                sub_key, _, sub_value = key_value_pair.partition("=")
                value_map[sub_key.strip()] = sub_value.strip()
            value = value_map
        result[key] = value
    return result
