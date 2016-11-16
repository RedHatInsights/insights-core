from .. import mapper, parse_table, get_active_lines


@mapper('route')
def route(context):
    '''
    Return a list of dicts.
    The content of "route -n" command output looks like:
    ~~~~~~~~~~~
    Kernel IP routing table
    Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    10.66.208.0     0.0.0.0         255.255.255.0   U     0      0        0 eth0
    169.254.0.0     0.0.0.0         255.255.0.0     U     1002   0        0 eth0
    0.0.0.0         10.66.208.254   0.0.0.0         UG    0      0        0 eth0
    ~~~~~~~~~~~
    The return list will looks like:
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

    '''
    # Ignore first line to use "parse_table"
    content = get_active_lines(context.content, "COMMAND>")
    return parse_table(content[1:])
