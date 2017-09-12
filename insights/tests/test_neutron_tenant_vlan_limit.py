import copy

from insights.core.plugins import make_response
from insights.tests import archive_provider, InputData
from insights.plugins import neutron_tenant_vlan_limit

osp_metadata = {
    "coordinator_version": "1.0.21",
    "display_name": "instack",
    "insights_version": "redhat-access-insights-1.0.11-1.el7.centos.noarch",
    "nova_client_api_version": "3.1.0",
    "overcloud_networks": [
        {
            "admin_state_up": "true",
            "id": "653cab00-ce12-45de-9d19-8aa1f01f9c89",
            "mtu": 0,
            "name": "net 1",
            "port_security_enabled": "true",
            "provider:network_type": "vlan",
            "provider:physical_network": "null",
            "provider:segmentation_id": 35,
            "qos_policy_id": "null",
            "router:external": "false",
            "shared": "false",
            "status": "ACTIVE",
            "subnets": [
                "84906d60-6c92-4e5d-9c15-d0efc369e351"
            ],
            "tenant_id": "983596887a3f42bfac3343e716e6cb55"
        },
        {
            "admin_state_up": "true",
            "id": "132fd405-6c08-4c08-930e-810dfbe06d96",
            "mtu": 0,
            "name": "HA network tenant 983596887a3f42bfac3343e716e6cb55",
            "port_security_enabled": "true",
            "provider:network_type": "vlan",
            "provider:physical_network": "null",
            "provider:segmentation_id": 69,
            "qos_policy_id": "null",
            "router:external": "false",
            "shared": "false",
            "status": "ACTIVE",
            "subnets": [
                "72702b59-0b38-43b5-a008-28b738924f1b"
            ],
            "tenant_id": ""
        },
        {
            "admin_state_up": "true",
            "id": "474bcfb7-01aa-4bfc-9754-3e81d5be3205",
            "mtu": 0,
            "name": "default",
            "port_security_enabled": "true",
            "provider:network_type": "vlan",
            "provider:physical_network": "null",
            "provider:segmentation_id": 14,
            "qos_policy_id": "null",
            "router:external": "false",
            "shared": "false",
            "status": "ACTIVE",
            "subnets": [
                "a90bfb77-e4fc-487d-909e-6e4bc86b513b"
            ],
            "tenant_id": "983596887a3f42bfac3343e716e6cb55"
        }
    ],
    "product": "OSP",
    "rhel_version": "Red Hat Enterprise Linux Server release 7.2 (Maipo)",
    "rhosp_version": "12.0.4",
    "stack_networks": [
        {
            "admin_state_up": "true",
            "id": "081aa336-f07f-46a6-aa10-a82bd46a1bbf",
            "mtu": 0,
            "name": "ctlplane",
            "provider:network_type": "flat",
            "provider:physical_network": "ctlplane",
            "provider:segmentation_id": "null",
            "router:external": "false",
            "shared": "false",
            "status": "ACTIVE",
            "subnets": [
                "11e02060-4f17-4490-9402-82478d96368f"
            ],
            "tenant_id": "3f1d231437784bb1ae5d27a38fd5bf40"
        }
    ],
    "system_id": "433ea86e-edda-485f-910c-cc42566701f7",
    "systems": [
        {
            "blacklisted": "false",
            "display_name": "overcloud-controller-2",
            "ip": "192.0.2.12",
            "links": [
                {
                    "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
                    "type": "director"
                }
            ],
            "product": "OSP",
            "status": "ACTIVE",
            "system_id": "0b629938-2166-577d-b852-d5258cadde16",
            "type": "controller"
        },
        {
            "blacklisted": "false",
            "display_name": "overcloud-controller-0",
            "ip": "192.0.2.11",
            "links": [
                {
                    "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
                    "type": "director"
                }
            ],
            "product": "OSP",
            "status": "ACTIVE",
            "system_id": "b3a4e6b2-c357-5ac5-a35f-daea39ee0409",
            "type": "controller"
        },
        {
            "blacklisted": "false",
            "display_name": "overcloud-controller-1",
            "ip": "192.0.2.10",
            "links": [
                {
                    "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
                    "type": "director"
                }
            ],
            "product": "OSP",
            "status": "ACTIVE",
            "system_id": "7cdbb6de-a457-5c3c-80ad-0321a07658ce",
            "type": "controller"
        },
        {
            "blacklisted": "false",
            "display_name": "overcloud-compute-0",
            "ip": "192.0.2.9",
            "links": [
                {
                    "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
                    "type": "director"
                }
            ],
            "product": "OSP",
            "status": "ACTIVE",
            "system_id": "4e01792e-48d8-5b3e-b971-bba625566943",
            "type": "compute"
        },
        {
            "blacklisted": "false",
            "display_name": "overcloud-compute-1",
            "ip": "192.0.2.8",
            "links": [
                {
                    "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
                    "type": "director"
                }
            ],
            "product": "OSP",
            "status": "ACTIVE",
            "system_id": "95850848-0db0-5714-a201-4f64828af6dc",
            "type": "compute"
        },
        {
            "blacklisted": "false",
            "display_name": "instack",
            "links": [],
            "product": "OSP",
            "system_id": "f94ab2d6-cda5-4861-92f3-39f1d2a26046",
            "type": "director"
        }
    ],
    "total_overcloud_networks": 3900,
    "total_stack_networks": 1
}


@archive_provider(neutron_tenant_vlan_limit.report)
def integration_tests():
    input_data = InputData("test1", hostname="overcloud-controller-1",
                           machine_id="b3a4e6b2-c357-5ac5-a35f-daea39ee0409")
    expected_result = make_response(neutron_tenant_vlan_limit.ERROR_KEY, total_vlan_tenant=3900)
    yield [osp_metadata, input_data], [expected_result]

    input_data = InputData("test1", hostname="overcloud-controller-1",
                           machine_id="b3a4e6b2-c357-5ac5-a35f-daea39ee0409")
    update_metadata = copy.deepcopy(osp_metadata)
    update_metadata["total_overcloud_networks"] = 2000
    yield [update_metadata, input_data], []
