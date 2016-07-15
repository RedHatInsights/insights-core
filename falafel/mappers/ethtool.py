import os
from falafel.core.plugins import mapper


def extract_iface_name_from_path(path, name):
    """
    extract iface name from path
    there are some special name:
    |----------------|----------------|
    |   real name    |   path name    |
    |----------------|----------------|
    | bond0.104@bond0|bond0.104_bond0 |
    |  __tmp1111     |  __tmp1111     |
    |  macvtap@bond0 |  macvlan_bond0 |
    |  prod_bond     |  prod_bond     |
    |----------------|----------------|
    """
    if name in path:
        ifname = os.path.basename(path).split("_", 2)[-1].strip()
        if "." in ifname or "macvtap" in ifname or "macvlan" in ifname:
            ifname = ifname.replace("_", "@")
        return ifname


def extract_iface_name_from_content(content):
    return content.split(" ", 3)[-1][:-1]


@mapper("ethtool-i")
def driver(context):
    d = {}
    for line in context.content:
        if ":" in line:
            key, value = line.strip().split(":", 1)
            value = value.strip()
            value = value if value else None
            d[key.strip()] = value
    d["iface"] = extract_iface_name_from_path(context.path, "ethtool_-i_")
    return d


@mapper("ethtool-k")
def features(context):
    d = {}
    # Need to strip header line that's only on -k
    for line in context.content[1:]:
        if ":" in line:
            key, value = line.strip().split(":", 1)
            value = value.strip()
            fixed = "fixed" in value
            if fixed:
                value = value.split()[0].strip()
            d[key.strip()] = {
                "value": value == "on",
                "fixed": fixed
            }
    d["iface"] = extract_iface_name_from_path(context.path, "ethtool_-k_")
    return d


@mapper("ethtool-a")
def get_ethtool_a(context):
    """
    Return ethtool -a result as a dict.
    If ethtool -a output a error, only return "iface" key as a network interface
    input: "RX: on"
    Output: result["RX"] = true
    """
    result = {}
    if "ethtool" in context.content[0]:
        # ethtool run error, only return iface
        result["iface"]= extract_iface_name_from_path(context.path, "ethtool_-a_")
        return result
    if "Cannot get" in context.content[0]:
        # cannot got pause param in ethtool
        result["iface"] = extract_iface_name_from_content(context.content[1])
        return result

    result["iface"] = extract_iface_name_from_content(context.content[0])
    for line in context.content[1:]:
        if line.strip():
            (key, value) = line.split(":", 1)
            result[key.strip()] = (value.strip() == "on")
    return result


@mapper("ethtool-c")
def get_ethtool_c(context):
    """
    Return ethtool -c result as a dict
    if interface error, only return interface name
    "iface" key is network interface name
    Adaptive rx in "adaptive-rx" key, value is boolean
    Adaptive tx in "adaptive-tx" key, value is boolean
    Other value is int
    """
    result = {}
    if "ethtool" in context.content[0]:
        # ethtool run error, only return iface
        result["iface"]= extract_iface_name_from_path(context.path, "ethtool_-c_")
        return result
    if "Cannot get" in context.content[0]:
        # cannot got pause param in ethtool
        result["iface"] = extract_iface_name_from_content(context.content[1])
        return result

    result["iface"] = extract_iface_name_from_content(context.content[0])

    if len(context.content) > 1:
        second_line_content = context.content[1].split(" ")
        result["adaptive-rx"] = (second_line_content[2]=="on")
        result["adaptive-tx"] = (second_line_content[5] =="on")

        for line in context.content[2:]:
            if line.strip():
                (key, value) = line.split(":", 1)
                result[key.strip()] = int(value.strip())

    return result


@mapper("ethtool-g")
def get_ethtool_g(context):
    """
    Return ethtool -g info into  a dict contain 3 keys which is "max", "current", "iface"
    "max" and "current" dict contain "rx", "rx_mini","rx_jumbo","tx",  type is int
    "iface" contain a interface name
    """
    result = {}
    if "ethtool" in context.content[0]:
        # ethtool run error, only return iface
        result["iface"]= extract_iface_name_from_path(context.path, "ethtool_-g_")
        return result
    if "Cannot get" in context.content[0]:
        # cannot got pause param in ethtool
        result["iface"] = extract_iface_name_from_content(context.content[1])
        return result
    result["iface"] = extract_iface_name_from_content(context.content[0])

    # parse max value
    result["max"] = parse_value(context.content[2:6])
    # parse current value
    result["current"] = parse_value(context.content[7:11])

    return result


def parse_value(content):
    result = {}
    for line in content:
        if line.strip():
            key, value = line.split(":", 1)
            result[key.strip().replace(" ", "-").lower()] = int(value.strip())
    return result


@mapper("ethtool-S")
def get_ethtool_S(context):
    '''
    return the ethtool -S result as a dict
    '''
    info = dict()

    info["iface"] = extract_iface_name_from_path(context.path, "ethtool_-S_")

    if "NIC statistics:" not in context.content[0]:
        # if there's no data, then return info immediately.
        # in this situation, content may looks like:
        # "no stats available" or
        # "Cannot get stats strings information: Operation not supported"
        return info

    for line in context.content[1:]:  # ignore first line
        # the correct description lines look like below, but we will ignore the
        # first line "NIC statistics":
        # ~~~~~
        # NIC statistics:
        #     rx_packets: 7357503
        #     tx_packets: 7159010
        #     rx_bytes: 1687906514
        #     tx_bytes: 2747645082
        # ...
        # ~~~~~
        if line.strip():
            key, value = line.split(':', 1)
            info[key.strip()] = value.strip() if value else ''

    return info
