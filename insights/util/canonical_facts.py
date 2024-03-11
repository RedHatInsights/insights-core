#!/usr/bin/env python

from __future__ import print_function

from insights import rule, run, make_metadata, add_filter
from insights.combiners.cloud_instance import CloudInstance
from insights.combiners.cloud_provider import CloudProvider
from insights.core.dr import set_enabled, load_components
from insights.parsers.aws_instance_id import AWSInstanceIdDoc
from insights.parsers.azure_instance import AzureInstanceID, AzureInstanceType
from insights.parsers.client_metadata import MachineID
from insights.parsers.dmidecode import DMIDecode
from insights.parsers.etc_machine_id import EtcMachineId
from insights.parsers.gcp_instance_type import GCPInstanceType
from insights.parsers.hostname import Hostname
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.ip import IPs
from insights.parsers.mac import MacAddress
from insights.parsers.rhsm_conf import RHSMConf
from insights.parsers.subscription_manager import SubscriptionManagerID, SubscriptionManagerFacts
from insights.parsers.yum import YumRepoList


add_filter(SubscriptionManagerFacts, 'instance_id')
add_filter(RHSMConf, ['server', 'hostname'])


def _filter_falsy(dict_):
    return dict((k, v) for k, v in dict_.items() if v)


@rule(
    optional=[
        MachineID,
        EtcMachineId,
        DMIDecode,
        SubscriptionManagerID,
        IPs,
        Hostname,
        MacAddress,
        CloudInstance,
    ]
)
def canonical_facts(
    insights_id, machine_id, dmidecode, submanid, ips, hostname, mac_addresses,
    cloud_instance,
):

    facts = dict(
        insights_id=insights_id.uuid if insights_id else None,
        machine_id=machine_id.uuid if machine_id else None,
        bios_uuid=dmidecode.system_uuid if dmidecode else None,
        subscription_manager_id=submanid.uuid if submanid else None,
        ip_addresses=ips.ipv4_addresses if ips else [],
        mac_addresses=list(filter(None, [mc.address for mc in mac_addresses or []])),
        fqdn=hostname.fqdn if hostname else None,
        provider_id=cloud_instance.id if cloud_instance else None,
        provider_type=cloud_instance.provider if cloud_instance else None,
    )

    return make_metadata(**_filter_falsy(facts))


def get_canonical_facts(path=None):
    load_components("insights.specs.default", "insights.specs.insights_archive")

    required_components = [
        AWSInstanceIdDoc,
        AzureInstanceID,
        AzureInstanceType,
        CloudInstance,
        CloudProvider,
        DMIDecode,
        EtcMachineId,
        GCPInstanceType,
        Hostname,
        IPs,
        InstalledRpms,
        MacAddress,
        MachineID,
        RHSMConf,
        SubscriptionManagerFacts,
        SubscriptionManagerID,
        YumRepoList,
        canonical_facts,
    ]
    for comp in required_components:
        set_enabled(comp, True)

    br = run(canonical_facts, root=path)
    d = br[canonical_facts]
    del d["type"]
    return d


if __name__ == "__main__":
    import json

    print(json.dumps(get_canonical_facts()))
