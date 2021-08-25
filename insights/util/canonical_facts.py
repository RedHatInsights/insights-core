#!/usr/bin/env python

from __future__ import print_function

import re
import socket

from insights import rule, make_metadata, run
from insights.specs import Specs
from insights.core import Parser
from insights.core.plugins import parser
from insights.core.dr import set_enabled
import uuid


def valid_uuid_or_None(s):
    """
    Returns  if `s` is a valid UUID string.
    """
    if not s:
        return None
    try:
        return str(uuid.UUID(s))
    except Exception:
        return None


def valid_ipv4_address_or_None(addr):
    """ str: Returns the input value if it is a valid IPV4 address """
    try:
        socket.inet_pton(socket.AF_INET, addr)
        return addr
    except socket.error:
        return None


def valid_mac_addresses(mac_address_datasources):
    """ list: Return a list of valid mac addresses from a list of datasources """
    valid_addrs = []
    for ds in mac_address_datasources:
        try:
            addr = ds.content[0].strip()
        except Exception:
            continue
        # Only look for addresses in the form 00:00:00:00:00:00
        match = re.match("^([0-9a-f]{2}:){5}[0-9a-f]{2}$", addr)
        if match is not None:
            valid_addrs.append(addr)

    return valid_addrs


@parser(Specs.ip_addresses)
class IPs(Parser):
    """
    Reads the output of ``hostname -I`` and constructs a list of all assigned IP
    addresses. This command should only output IPV4 addresses and should not
    include localhost, but sometimes it does.  The validation function removes
    those from the list.

    Example output::
       192.168.1.71 10.88.0.1 172.17.0.1 172.18.0.1 10.10.121.131

    Resultant data structure::
        [
            "192.168.1.71",
            "10.88.0.1",
            "172.17.0.1",
            "172.18.0.1",
            "10.10.121.131",
        ]
    """
    def parse_content(self, content):
        self.data = list(filter(None, [valid_ipv4_address_or_None(addr) for addr in content[0].rstrip().split()]))


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


def _filter_falsy(dict_):
    return dict((k, v) for k, v in dict_.items() if v)


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

    facts = dict(
        insights_id=valid_uuid_or_None(_safe_parse(insights_id)),
        machine_id=valid_uuid_or_None(_safe_parse(machine_id)),
        bios_uuid=valid_uuid_or_None(_safe_parse(bios_uuid)),
        subscription_manager_id=valid_uuid_or_None(submanid.data if submanid else None),
        ip_addresses=ips.data if ips else [],
        mac_addresses=valid_mac_addresses(mac_addresses) if mac_addresses else [],
        fqdn=_safe_parse(fqdn),
    )

    return make_metadata(**_filter_falsy(facts))


def get_canonical_facts(path=None):
    set_enabled(canonical_facts, True)
    set_enabled(SubscriptionManagerID, True)
    set_enabled(IPs, True)
    br = run(canonical_facts, root=path)
    d = br[canonical_facts]
    del d["type"]
    return d


if __name__ == "__main__":
    import json
    from insights import dr
    dr.load_components("insights.specs.default", "insights.specs.insights_archive")

    print(json.dumps(get_canonical_facts()))
