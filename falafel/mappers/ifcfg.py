from falafel.mappers import get_active_lines
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed
import json

JSON_FIELDS = ["TEAM_CONFIG", "TEAM_PORT_CONFIG"]

QUOTES = "\"'"

bond_mode_map = {
    'balance-rr': '0',
    'active-backup': '1',
    'balance-xor': '2',
    'broadcast': '3',
    '802.3ad': '4',
    'balance-tlb': '5',
    'balance-alb': '6'
}


@mapper("ifcfg")
class IfCFG(MapperOutput):
    """
    Parse `ifcfg-` file,return a dict contain ifcfg config file info.
    "iface" key is interface name parse from file name
    `TEAM_CONFIG`, `TEAM_PORT_CONFIG` will return a dict with user config dict
    `BONDING_OPTS` also will return a dict
    """

    def __init__(self, data, path):
        super(IfCFG, self).__init__(data, path)
        self.data["iface"] = path.rsplit("-", 1)[1]

    @staticmethod
    def parse_content(content):
        data = {}
        for line in get_active_lines(content):
            key, _, value = line.partition("=")
            key = key.strip().strip(QUOTES)

            # In some cases we want to know what the actual value-side
            # of the key is
            if key == "BONDING_OPTS":
                data["raw_bonding_value"] = value

            value = value.strip().strip(QUOTES)
            if key in JSON_FIELDS:
                value = json.loads(value.replace("\\", ""))
            if key == "BONDING_OPTS":
                value_map = {}
                for key_value_pair in value.split():
                    sub_key, _, sub_value = key_value_pair.partition("=")
                    value_map[sub_key.strip()] = sub_value.strip()
                value = value_map
            data[key] = value
        return data

    @computed
    def bonding_mode(self):
        """
        Returns the numeric value of bonding mode.
        Returns `None` if no bonding mode is found.
        """
        if "BONDING_OPTS" not in self:
            return None

        m = self["BONDING_OPTS"]["mode"]
        return int(m) if m.isdigit() else int(bond_mode_map[m])
