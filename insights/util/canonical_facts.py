#!/usr/bin/env python

from __future__ import print_function

from insights import rule, make_metadata, run
from insights.specs import Specs
from insights.core import Parser
from insights.core.plugins import parser


@parser(Specs.ip_addresses)
class IPs(Parser):
    """
    Reads the output of hostname -I and constructs a list of all assigned IP
    addresses.

    Example output::
       192.168.1.71 10.88.0.1 172.17.0.1 172.18.0.1 10.10.121.131 2600:1700:720:7e30:e4ef:e9d0:7ea1:c8a7

    Resultant data structure::
        [
            "192.168.1.71",
            "10.88.0.1",
            "172.17.0.1",
            "172.18.0.1",
            "10.10.121.131",
            "2600:1700:720:7e30:e4ef:e9d0:7ea1:c8a7"
        ]
    """

    def parse_content(self, content):
        self.data = content[0].rstrip().split()


@parser(Specs.subscription_manager_id)
class SubscriptionManagerID(Parser):
    """
    Reads the output of subscription-manager identity and retrieves the UUID

    Example output::
        system identity: 6655c27c-f561-4c99-a23f-f53e5a1ef311
        name: rhel7.localdomain
        org name: 1234567
        org ID: 1234567

    Resultant data::

        6655c27c-f561-4c99-a23f-f53e5a1ef311
    """

    def parse_content(self, content):
        self.data = content[0].split(":")[-1].strip()


def _safe_parse(ds):
    try:
        return ds.content[0]

    except Exception:
        return None


@rule(
    optional=[
        Specs.machine_id,
        Specs.etc_machine_id,
        Specs.bios_uuid,
        SubscriptionManagerID,
        IPs,
        Specs.hostname,
        Specs.mac_addresses,
    ]
)
def canonical_facts(
    insights_id, machine_id, bios_uuid, submanid, ips, fqdn, mac_addresses
):
    return make_metadata(
        insights_id=_safe_parse(insights_id),
        machine_id=_safe_parse(machine_id),
        bios_uuid=_safe_parse(bios_uuid),
        subscription_manager_id=submanid.data if submanid else None,
        ip_addresses=ips.data if ips else [],
        mac_addresses=list(
            filter(None, (_safe_parse(c) for c in mac_addresses))
        ) if mac_addresses else [],
        fqdn=_safe_parse(fqdn),
    )


def get_canonical_facts(path=None):
    br = run(canonical_facts, root=path)
    d = br[canonical_facts]
    del d["type"]
    return d


if __name__ == "__main__":
    import json

    print(json.dumps(get_canonical_facts()))
