from .. import parser, CommandParser
from . import parse_delimited_table
from insights.specs import Specs


@parser(Specs.route)
class Route(CommandParser):
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
        # heading_ignore is first line we _don't_ want to ignore...
        self.data = parse_delimited_table(content, heading_ignore=['Destination'])

    def __contains__(self, dest):
        return any(dest == line['Destination'] for line in self.data)

    def __iter__(self):
        for row in self.data:
            yield row
