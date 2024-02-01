"""
Custom datasources for SAP related specs
"""
from insights.combiners.sap import Sap
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT


class LocalSpecs(Specs):
    """ Local specs used only by sap datasources """

    @datasource(Sap, HostContext)
    def sap_instance(broker):
        """
        list: List of all SAP Instances.
        """
        sap = broker[Sap]
        return sorted(v for v in sap.values())

    @datasource(sap_instance, HostContext)
    def sap_hana_instance(broker):
        """
        list: List of the SAP HANA Instances.
        """
        sap = broker[LocalSpecs.sap_instance]
        insts = sorted(v for v in sap if v.type == 'HDB')
        if insts:
            return insts
        raise SkipComponent()


@datasource(LocalSpecs.sap_instance, HostContext)
def sap_sid(broker):
    """
    list: List of the SID of all the SAP Instances.
    """
    sap = broker[LocalSpecs.sap_instance]
    return sorted(set(h.sid.lower() for h in sap))


@datasource(LocalSpecs.sap_hana_instance, HostContext)
def sap_hana_sid(broker):
    """
    list: List of the SID of SAP HANA Instances.  """
    hana = broker[LocalSpecs.sap_hana_instance]
    sids = sorted(set(h.sid.lower() for h in hana))
    if sids:
        return sids
    raise SkipComponent()


@datasource(LocalSpecs.sap_hana_instance, HostContext)
def sap_hana_sid_SID_nr(broker):
    """
    list: List of tuples (sid, SID, Nr) of SAP HANA Instances.
    """
    hana = broker[LocalSpecs.sap_hana_instance]
    sids = sorted((h.sid.lower(), h.sid, h.number) for h in hana)
    if sids:
        return sids
    raise SkipComponent()


@datasource(sap_sid, HostContext)
def ld_library_path_of_user(broker):
    """
    list: The list of "Username LD_LIBRARY_PATH", e.g.::

          [
            'sr1adm /usr/sap/RH1/SYS/exe/run:/usr/lib/',
            'sr2adm /usr/sap/RH2/SYS/exe/run',
          ]

    .. note::
        Currently, only Sap users are supported.
    """
    ctx = broker[HostContext]

    llds = []
    for sid in broker[sap_sid]:
        usr = '{0}adm'.format(sid)
        ret, vvs = ctx.shell_out("/bin/su -l {0} -c /bin/env".format(usr), keep_rc=True, timeout=DEFAULT_SHELL_TIMEOUT)
        if ret != 0:
            continue
        for v in vvs:
            if "LD_LIBRARY_PATH=" in v:
                llds.append('{0} {1}'.format(usr, v.split('=', 1)[-1]))
    if llds:
        return DatasourceProvider(
            '\n'.join(llds),
            cleaner=broker.get('cleaner'),
            relative_path='insights_commands/echo_user_LD_LIBRARY_PATH')
    raise SkipComponent('')
