"""
Custom datasources for SAP information
"""
from insights.combiners.sap import Sap
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider


@datasource(Sap, HostContext)
def summary(broker):
    """
    dict: Returns a dict of information needed by other SAP datasources
    """
    info = {}
    info['instances'] = list(v for v in broker[Sap].values())
    info['hana_instances'] = list(v for v in info['instances'] if v.type == 'HDB')
    info['sids'] = list(set(h.sid.lower() for h in info['instances']))
    info['hana_sids'] = list(set(h.sid.lower() for h in info['hana_instances']))
    info['hana_sid_SID_nr'] = list((h.sid.lower(), h.sid, h.number) for h in info['hana_instances'])
    return info


@datasource(summary, HostContext)
def hana_sid(broker):
    """
    list: List of the SID of SAP HANA Instances.
    """
    return broker[summary]['hana_sids']


@datasource(summary, HostContext)
def hana_sid_SID_nr(broker):
    """
    list: List of tuples (sid, SID, Nr) of SAP HANA Instances.
    """
    return broker[summary]['hana_sid_SID_nr']


@datasource(summary, HostContext)
def ld_library_path_of_user(broker):
    """
    Returns: The list of LD_LIBRARY_PATH of specified users.
                Username is combined from SAP <SID> and 'adm' and is also stored.
    """
    sids = broker[summary].get('sids', [])
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
