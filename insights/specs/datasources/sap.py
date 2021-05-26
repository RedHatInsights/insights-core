from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider


def summary(sap):
    info = {}
    info['instances'] = list(v for v in sap.values())
    info['hana_instances'] = list(v for v in info['instances'] if v.type == 'HDB')
    info['sids'] = list(set(h.sid.lower() for h in info['instances']))
    info['hana_sids'] = list(set(h.sid.lower() for h in info['hana_instances']))
    info['hana_sid_SID_nr'] = list((h.sid.lower(), h.sid, h.number) for h in info['hana_instances'])
    return info


def hana_sids(sap_summary):
    return sap_summary['hana_sids']


def hana_summary(sap_summary):
    return sap_summary['hana_sid_SID_nr']


def ld_library_path(broker, sap_summary):
    """
    Returns: The list of LD_LIBRARY_PATH of specified users.
                Username is combined from SAP <SID> and 'adm' and is also stored.
    """
    sids = broker[sap_summary].get('sids', [])
    ctx = broker[HostContext]
    llds = []
    for sid in sids:
        usr = '{0}adm'.format(sid)
        ret, vvs = ctx.shell_out("/bin/su -l {0} -c /bin/env".format(usr), keep_rc=True)
        if ret != 0:
            continue
        for v in vvs:
            if "LD_LIBRARY_PATH=" in v:
                llds.append('{0} {1}'.format(usr, v.split('=', 1)[-1]))
    if llds:
        return DatasourceProvider('\n'.join(llds), relative_path='insights_commands/echo_user_LD_LIBRARY_PATH')
    raise SkipComponent
