from falafel.core.plugins import mapper


@mapper("corosync")
def parse_corosync(context):
    """
    Parse /etc/sysconfig/corosync
    return dict like {'COROSYNC_OPTIONS': '', 'COROSYNC_INIT_TIMEOUT': '60'}
    """
    corosync_dict = {}
    for line in context.content:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        if "=" in line:
            (key, value) = line.split("=", 1)
            corosync_dict[key.strip()] = value.strip().replace('"', "")
    return corosync_dict
