"""
Custom datasources for ``nmcli`` command
"""
from insights.core.plugins import datasource
from insights.parsers.nmcli import NmcliConnShow


@datasource(NmcliConnShow)
def nmcli_conn_show_uuids(broker):
    """  Return a list of connection uuids """
    nmcli_conn_show = broker[NmcliConnShow]
    return [item["UUID"] for item in nmcli_conn_show.data]
