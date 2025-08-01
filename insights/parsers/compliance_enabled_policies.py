"""
ComplianceEnablePolicies - datasource ``compliance_advisor_rule_enabled``
=========================================================================
This parser is used to parse the output of datasouce compliance_ds.compliance_advisor_rule_enabled
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.compliance_advisor_rule_enabled_policies)
class ComplianceEnablePolicies(JSONParser):
    """
    Parses the output of datasouce compliance_ds.compliance_advisor_rule_enabled

    Typical output of the datasouce::

    {
        "enabled_policies": [
            {
                "id": "717539de-3c90-473b-acca-c8ee95bb6cc3",
                "title": "advisor rule test - CIS Red Hat Enterprise Linux 8 Benchmark for Level 1 - Server",
                "description": "This profile defines a baseline that aligns to the Level 1 - Server",
                "business_objective": null,
                "compliance_threshold": 100.0,
                "total_system_count": 1,
                "type": "policy",
                "os_major_version": 8,
                "profile_title": "CIS Red Hat Enterprise Linux 8 Benchmark for Level 1 - Server",
                "ref_id": "xccdf_org.ssgproject.content_profile_cis_server_l1"
            },
            {
                "id": "bc11fd8a-9c76-484c-ac63-14b29414a455",
                "title": "CIS Red Hat Enterprise Linux 8 Benchmark for Level 2 - Server",
                "description": "This profile defines a baseline that aligns to the Level 2 - Server",
                "business_objective": null,
                "compliance_threshold": 100.0,
                "total_system_count": 1,
                "type": "policy",
                "os_major_version": 8,
                "profile_title": "CIS Red Hat Enterprise Linux 8 Benchmark for Level 2 - Server",
                "ref_id": "xccdf_org.ssgproject.content_profile_cis"
            }
        ],
        "tailoring_policies": [
            {
                "ref_id": "xccdf_org.ssgproject.content_profile_cis_server_l1",
                "check_items": [
                    {
                        "idref": "xccdf_org.ssgproject.content_rule_bios_disable_usb_boot",
                        "selected": "true"
                    },
                    {
                        "idref": "xccdf_org.ssgproject.content_rule_ssh_keys_passphrase_protected",
                        "selected": "true"
                    },
                    {
                        "idref": "xccdf_org.ssgproject.content_rule_sysctl_net_ipv4_conf_all_shared_media",
                        "selected": "true"
                    },
                    {
                        "idref": "xccdf_org.ssgproject.content_rule_accounts_password_pam_ocredit",
                        "selected": "false"
                    }
                ]
            }
        ]
    }

    Examples:
        >>> type(compliance_enabled_policies)
        <class 'insights.parsers.compliance_enabled_policies.ComplianceEnablePolicies'>
        >>> compliance_enabled_policies['enabled_policies'][0]['ref_id']
        'xccdf_org.ssgproject.content_profile_cis_server_l1'
        >>> compliance_enabled_policies['tailoring_policies'][0]['ref_id']
        'xccdf_org.ssgproject.content_profile_cis_server_l1'
    """
    pass
