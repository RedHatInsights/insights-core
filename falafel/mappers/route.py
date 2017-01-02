from .. import Mapper, mapper, parse_table, get_active_lines


@mapper('route')
class Route(Mapper):
    """Class to parse the ``route -n`` command

    Attributes:
        data (list): A list of dicts likes
            [
                {
                    "Use": "0",
                    "Iface": "eth0",
                    "Metric": "0",
                    "Destination": "10.66.208.0",
                    "Genmask": "255.255.255.0",
                    "Flags": "U",
                    "Ref": "0",
                    "Gateway": "0.0.0.0"
                },
                ...
            ]
    Usages:
        ru  = Route(...)
        if "10.66.20.0" in ru: # check if specified destination is in the route
            ...

    ---Sample---
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    10.66.208.0     0.0.0.0         255.255.255.0   U     0      0        0 eth0
    169.254.0.0     0.0.0.0         255.255.0.0     U     1002   0        0 eth0
    0.0.0.0         10.66.208.254   0.0.0.0         UG    0      0        0 eth0
    """

    def parse_content(self, content):
        content = get_active_lines(content, "COMMAND>")
        # Ignore first line to use "parse_table"
        self.data = parse_table(content[1:])

    def __contains__(self, dest):
        return any(dest == line['Destination'] for line in self.data)

    def __iter__(self):
        for row in self.data:
            yield row
