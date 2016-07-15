from falafel.core.plugins import mapper


@mapper('ip_addr')
def get_ip_addr(context):
    """
    QUICK START:
    `ip addr` will return a dict that key is interface name. `addr` key is a array to store all address.
    Different type have different output. Peer ip and general interface have difference type.
    There are some examples:
    CASE 1:
    1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN
        link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
        inet 127.0.0.1/8 scope host lo
        inet6 ::1/128 scope host
        valid_lft forever preferred_lft forever
    RESULT:
    "lo": {
        "qdisc": "noqueue",
        "addr": [
            "127.0.0.1",
        ],
        "addr_v6":[
            "::1",
        ]
        "state": "UNKNOWN",
        "flag": [
            "LOOPBACK",
            "UP",
            "LOWER_UP"
        ],
        "mtu": 16436,
        "mac": "00:00:00:00:00:00",
        "type": "loopback"
    }
    CASE 2:
    2: eth7: <NO-CARRIER,BROADCAST,MULTICAST,SLAVE,UP> mtu 1500 qdisc mq master bond1 state DOWN qlen 1000
        link/ether 00:11:3f:e2:f5:9f brd ff:ff:ff:ff:ff:ff link-netnsid 1
    RESULT:
    "eth7": {
        "qlen": 1000,
        "qdisc": "mq",
        "addr": [ ],
        "addr_v6": [ ],
        "state": "DOWN",
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9f",
        "flag": [
            "NO-CARRIER",
            "BROADCAST",
            "MULTICAST",
            "SLAVE",
            "UP"
        ],
        "master": "bond1",
        "type": "ether"
    }
    CASE 3:
    3: tunl0: <NOARP> mtu 1480 qdisc noop state DOWN
        link/ipip 0.0.0.0 brd 0.0.0.0
    RESULT:
    "tunl0": {
        "qdisc": "noop",
        "addr": [ ],
        "addr_v6", [ ],
        "state": "DOWN",
        "flag": [
            "NOARP"
        ],
        "mtu": 1480,
        "mac": "0.0.0.0",
        "type": "ipip"
    }
    CASE 4:
    4: tunl1: <NOARP> mtu 1480 qdisc noop state DOWN
        link/[65534]
        inet 172.30.0.1 peer 172.30.0.2/32 scope global tun0
    RESULT:
    "tunl1": {
        "qdisc": "noop",
        "addr": [
            "172.30.0.1"
        ],
        "addr_v6": [ ],
        "state": "DOWN",
        "mtu": 1480,
        "flag": [
            "NOARP"
        ],
        "type": "[65534]"
    }
    CASE 5:
    5: bond1.57@bond1: <BROADCAST,MULTICAST,MASTER,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP
        link/ether 00:11:3f:e2:f5:9e brd ff:ff:ff:ff:ff:ff
        inet 10.192.4.171/27 brd 10.192.4.191 scope global bond1.57
        inet6 fe80::211:3fff:fee2:f59e/64 scope link
        valid_lft forever preferred_lft forever
        inet6 2001::211:3fff:fee2:f59e/64 scope global mngtmpaddr dynamic
        valid_lft 2592000sec preferred_lft 6480000sec
    RESULT:
    "bond1.57@bond1": {
        "qdisc": "noqueue",
        "addr": [
            "10.192.4.171",
        ],
        "addr_v6":[
            "fe80::211:3fff:fee2:f59e",
            "2001::211:3fff:fee2:f59e"
        ],
        "state": "UP",
        "flag": [
            "BROADCAST",
            "MULTICAST",
            "MASTER",
            "UP",
            "LOWER_UP"
        ],
        "mtu": 1500,
        "mac": "00:11:3f:e2:f5:9e",
        "type": "ether"
    }
        CASE 6:
    6: ip.tun2: <POINTOPOINT,NOARP,UP,LOWER_UP> mtu 1480 qdisc noqueue state UNKNOWN
        link/ipip 10.192.4.203 peer 10.188.61.108
        inet 192.168.112.5 peer 192.168.122.6/32 scope global ip.tun2
    RESULT:
    "ip.tun2": {
        "qdisc": "noqueue",
        "addr": [
            "192.168.112.5"
        ],
        "addr_v6":[],
        "state": "UNKNOWN",
        "peer_ip": "10.192.4.203",
        "flag": [
            "POINTOPOINT",
            "NOARP",
            "UP",
            "LOWER_UP"
        ],
        "peer": "10.188.61.108",
        "mtu": 1480,
        "type": "ipip"
    }
    """
    r = {}
    iface_name = ""
    iface_pro = {}
    iface_addr_v4 = []
    iface_addr_v6 = []
    line = 0
    if len(context.content)==0:
        return r
    while "Message truncated" == context.content[line].strip():
        line = line + 1
    for content in context.content[line:]:
        split_content = content.strip().split()
        if len(content)>0 and content[0] != " ":    # Parse first line
            # save previous iface info
            if iface_name != "":
                iface_pro["addr"] = iface_addr_v4
                iface_pro["addr_v6"] = iface_addr_v6
                r[iface_name] = iface_pro
                iface_name = ""
                iface_pro = {}
                iface_addr_v4 = []
                iface_addr_v6 = []
            iface_name = content.split(":")[1].strip()
            iface_pro["flag"] = split_content[2].lstrip("<").rstrip(">").split(",")
            # extract property
            for i in range(3, len(split_content), 2):
                if split_content[i] in ["mtu", "qlen"] and "X" not in split_content[i + 1]:  # must be integer
                    iface_pro[split_content[i]] = int(split_content[i + 1])
                else:
                    iface_pro[split_content[i]] = split_content[i + 1]
        elif "link" in split_content[0]:  # parse "link/ether line"
            iface_pro["type"] = split_content[0].split("/")[1]
            if "peer" in content and len(split_content) >= 3:
                iface_pro["peer_ip"] = split_content[1]
                iface_pro["peer"] = split_content[3]
            elif len(split_content) >= 2:
                iface_pro["mac"] = split_content[1]
        elif "inet" in split_content[0]:
            ipinfo = split_content[1].split("/")[0]
            if "inet6" in split_content[0]:
                iface_addr_v6.append(ipinfo)
            else:
                iface_addr_v4.append(ipinfo)
    if iface_name != "":
        iface_pro["addr"] = iface_addr_v4
        iface_pro["addr_v6"] = iface_addr_v6
        r[iface_name] = iface_pro
    return r
