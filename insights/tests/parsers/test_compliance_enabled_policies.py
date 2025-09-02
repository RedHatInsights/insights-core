import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import compliance_enabled_policies
from insights.parsers.compliance_enabled_policies import ComplianceEnabledPolicies
from insights.tests import context_wrap

COMPLIANCE_ENABLE_POLICIES = '''
{
    "enabled_policies": [
        {
            "id": "12345678-aaaa-bbbb-cccc-1234567890ab",
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
            "id": "12345678-aaaa-bbbb-cccc-1234567890xy",
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
'''.strip()


def test_compliance_enabled_policies_skip():
    with pytest.raises(SkipComponent) as ex:
        ComplianceEnabledPolicies(context_wrap(""))
    assert "Empty output." in str(ex)


def test_compliance_enabled_policies_malformed_json():
    malformed_json = "{not: valid, json:}"
    with pytest.raises(Exception):
        ComplianceEnabledPolicies(context_wrap(malformed_json))


def test_compliance_enabled_policies():
    compliance_enabled_policies_info = ComplianceEnabledPolicies(context_wrap(COMPLIANCE_ENABLE_POLICIES))
    assert compliance_enabled_policies_info['enabled_policies'][0]['ref_id'] == 'xccdf_org.ssgproject.content_profile_cis_server_l1'
    assert compliance_enabled_policies_info['tailoring_policies'][0]['ref_id'] == 'xccdf_org.ssgproject.content_profile_cis_server_l1'
    assert len(compliance_enabled_policies_info['enabled_policies']) == 2
    assert len(compliance_enabled_policies_info['tailoring_policies'][0]['check_items']) == 4


def test_compliance_enabled_policies_only_enabled():
    """
    Test parser with only enabled_policies and no tailoring_policies.
    """
    only_enabled_policies = '''
    {
        "enabled_policies": [
            {
                "id": "12345678-aaaa-bbbb-cccc-1234567890ab",
                "ref_id": "xccdf_org.ssgproject.content_profile_standard"
            }
        ]
    }
    '''
    compliance_enabled_policies_info = ComplianceEnabledPolicies(context_wrap(only_enabled_policies))
    assert 'enabled_policies' in compliance_enabled_policies_info
    assert compliance_enabled_policies_info['enabled_policies'][0]['ref_id'] == 'xccdf_org.ssgproject.content_profile_standard'
    assert 'tailoring_policies' not in compliance_enabled_policies_info or not compliance_enabled_policies_info.get('tailoring_policies')


def test_compliance_enabled_policies_doc_examples():
    env = {
        "compliance_enabled_policies": ComplianceEnabledPolicies(context_wrap(COMPLIANCE_ENABLE_POLICIES)),
    }
    failed, total = doctest.testmod(compliance_enabled_policies, globs=env)
    assert failed == 0
