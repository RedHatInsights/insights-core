"""
Neutron vlan type tenant network limit
======================================

As an OSP administrator, I would like to be alerted when approaching the limit
of 4094 VLANs per OSP environment so that I can avoid breaching the limit of
the 802.1q VLAN specification.

This plugin will fire if total tenant networks is over 70% of the limit.
"""

from insights.core.plugins import dr, make_response, rule
from insights.parsers.multinode import OSP

ERROR_KEY = 'NEUTRON_VLAN_4094_LIMIT'
VLAN_LIMIT = int(4094 * 0.7)


@rule(OSP, group=dr.GROUPS.cluster)
def report(osp):
    networks = osp.overcloud_networks or []
    if any(n.get("provider:network_type") == "vlan" for n in networks):
        ton = osp.total_overcloud_networks
        if ton > VLAN_LIMIT:
            return make_response(ERROR_KEY, total_vlan_tenant=ton)
