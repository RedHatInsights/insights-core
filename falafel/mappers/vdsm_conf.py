import re
from .. import mapper

SECTION_RE = re.compile(r'^\[([a-zA-Z0-9]+)\]$')


@mapper("vdsm.conf")
def check_vdsm_conf(context):
    """
    Returns a dict which have parameter dict as below:
    {'vars': {'ssl': 'true',
              'cpu_affinity': '1'},
     'addresses':{'management_port': '54321'}}

    -- Sample of vdsm.conf --
    [vars]
    ssl = true
    cpu_affinity = 1

    [addresses]
    management_port = 54321

    -----------

    """
    section = None
    vdsm_dict = {}
    tmp = {}
    for line in context.content:
        if not line.strip() or line.startswith('#'):
            continue
        match = SECTION_RE.match(line.strip())
        if match:
            if section and tmp:
                vdsm_dict[section] = tmp
            section = match.group(1)
            tmp = {}
        else:
            key, value = line.strip().split("=", 1)
            tmp[key.strip()] = value.strip()
    vdsm_dict[section] = tmp

    return vdsm_dict
