from falafel.core.plugins import mapper


@mapper("cinder.conf")
def parse_cinder_conf(context):
    """
    parsing cinder.conf and return dict.
    :return: a dict(dict)   Example:  {"DEFAULT": {"storage_availability_zone":"nova", glance_num_retries: 0},
    "lvm": {"volumes_dir":"/var/lib/cider/columes"}}
    """
    role = context.osp.role
    if role is None or role.lower() != "controller":
        # just parser cinder.conf on OSP controller
        return
    cinder_dict = {}
    section_dict = {}
    for line in context.content:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        if line.startswith("["):
            # new section beginning
            section_dict = {}
            cinder_dict[line[1:-1]] = section_dict
        elif '=' in line:
            key, value = line.split("=", 1)
            section_dict[key.strip()] = value.strip()
    return cinder_dict
