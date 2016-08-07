import json
from falafel.core.plugins import mapper
from falafel.mappers import get_active_lines

FILTER_LIST = list()

"""
ERROR_KEY = "CMIRROR_PERF_ISSUE"
ERROR_KEY = "CMIRROR_PERF_ISSUE"
"""
FILTER_LIST.append("locking_type")


"""
ERROR_KEY = "LVM_CONF_REMOVE_BOOTDEV"
ERROR_KEY = "HA_LVM_RELOCATE_ISSUE"
ERROR_KEY = "LVM_FILTER_ISSUE"
"""
FILTER_LIST.append("filter")

"""
ERROR_KEY = "HA_LVM_RELOCATE_ISSUE"
"""
FILTER_LIST.append("volume_list")


@mapper('lvm.conf', FILTER_LIST)
def get_lvm_conf(context):
    """
    Returns a dict:
    locking_type : 1
    filter : ['a/sda[0-9]*$/', 'r/sd.*/']
    volume_list : ['vg2', 'vg3/lvol3', '@tag2', '@*']
    """
    lvm_conf_dict = {}
    for line in get_active_lines(context.content, "#"):
        if "=" in line:
            (key, value) = [item.strip() for item in line.split('=', 1)]
            try:
                lvm_conf_dict[key] = json.loads(value)
            except Exception:
                lvm_conf_dict[key] = value
    return lvm_conf_dict
