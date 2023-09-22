"""
A method to get the spec name of some special symbolic_name in the uploader.json
"""

SPECIAL_SYMBOLIC_NAME_IN_UPLODER_JSON = {
    'getconf_pagesize': 'getconf_page_size',
    'krb5_conf_d': 'krb5',
    'limits_d': 'limits_conf',
    'machine_id1': 'machine_id',
    'machine_id2': 'machine_id',
    'machine_id3': 'machine_id',
    'modprobe_conf': 'modprobe',
    'modprobe_d': 'modprobe',
    'ps_auxwww': None,
    'redhat_access_proactive_log': None,
    'rh_mongodb26_conf': 'mongod_conf',
    'rpm__V_packages': 'rpm_V_packages',
}


def get_spec_name_by_symbolic_name(sname):
    # match a spec name to a symbolic name
    # some symbolic names need to be renamed to fit specs
    return SPECIAL_SYMBOLIC_NAME_IN_UPLODER_JSON.get(sname, sname)
