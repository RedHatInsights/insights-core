from .. import mapper


@mapper("nova.conf")
def parse_nova_conf(context):
    """
    parsing nova.conf and return dict.
    :return: a dict(dict)   Example:
    {'DEFAULT': {'firewall_driver': 'nova.virt.firewall.NoopFirewallDriver', 'verbose': 'False', 'novncproxy_port': '6080',
     'metadata_listen': 'fd00:4888:1000:f901::c1', 'state_path': '/var/lib/nova', 'metadata_workers': '32',
     'identity_uri': 'http://192.168.1.107:35357', 'ovs_bridge': 'br-int', 'rabbit_use_ssl': 'False'}}
    """
    nova_dict = {}
    section_dict = {}
    for line in context.content:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        if line.startswith("["):
            # new section beginning
            section_dict = {}
            nova_dict[line[1:-1]] = section_dict
        elif '=' in line:
            key, value = line.split("=", 1)
            section_dict[key.strip()] = value.strip()
    return nova_dict
