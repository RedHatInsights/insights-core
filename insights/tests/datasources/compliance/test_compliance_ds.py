# -*- coding: UTF-8 -*-
import os

try:
    from unittest.mock import patch
except Exception:
    from mock import patch

from pytest import raises
from tempfile import NamedTemporaryFile

from insights.client.config import InsightsConfig
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.specs.datasources.compliance.compliance_ds import (
    os_version,
    package_check,
    compliance,
    compliance_policies,
    compliance_assign,
    compliance_unassign,
)
from insights.tests import context_wrap

OS_RELEASE = """
NAME="Red Hat Enterprise Linux"
VERSION="8.10 (Ootpa)"
ID="rhel"
ID_LIKE="fedora"
VERSION_ID="8.10"
PLATFORM_ID="platform:el8"
PRETTY_NAME="Red Hat Enterprise Linux 8.10 (Ootpa)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:redhat:enterprise_linux:8::baseos"
HOME_URL="https://www.redhat.com/"
DOCUMENTATION_URL="https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
"""
REDHAT_RELEASE = """
Red Hat Enterprise Linux release 8.10 (Ootpa)
"""
RPMS_JSON_NG = """
{"name": "grub2-tools","version": "2.02","epoch": "1","release": "0.34.el7_2","arch": "x86_64","installtime": "Fri 24 Jun 2016 04:18:01 PM EDT","buildtime": "1450199819","rsaheader": "RSA/SHA256, Wed 23 Dec 2015 04:22:27 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "grub2-2.02-0.34.el7_2.src.rpm"}
{"name": "kbd-legacy","version": "1.15.5","epoch": "(none)","release": "11.el7","arch": "noarch","installtime": "Fri 06 May 2016 03:53:32 PM EDT","buildtime": "1412004323","rsaheader": "RSA/SHA256, Tue 16 Dec 2014 10:02:14 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "kbd-1.15.5-11.el7.src.rpm"}
{"name": "jboss-servlet-3.0-api","version": "1.0.1","epoch": "(none)","release": "9.el7","arch": "noarch","installtime": "Thu 02 Jun 2016 05:10:30 PM EDT","buildtime": "1388211302","rsaheader": "RSA/SHA256, Tue 01 Apr 2014 02:51:30 PM EDT, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "jboss-servlet-3.0-api-1.0.1-9.el7.src.rpm"}
{"name": "bash","version": "4.2.46","epoch": "(none)","release": "19.el7","arch": "x86_64","installtime": "Fri 06 May 2016 03:52:13 PM EDT","buildtime": "1436354006","rsaheader": "RSA/SHA256, Wed 07 Oct 2015 01:14:10 PM EDT, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "bash-4.2.46-19.el7.src.rpm"}
{"name": "ca-certificates","version": "2015.2.6","epoch": "(none)","release": "70.1.el7_2","arch": "noarch","installtime": "Fri 24 Jun 2016 04:18:04 PM EDT","buildtime": "1453976868","rsaheader": "RSA/SHA256, Tue 02 Feb 2016 09:45:04 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "ca-certificates-2015.2.6-70.1.el7_2.src.rpm"}
"""
RPMS_JSON = (
    RPMS_JSON_NG
    + """
{"name": "scap-security-guide","version": "0.1.72","epoch": "(none)","release": "1.el7_2","arch": "noarch","installtime": "Fri 24 Jun 2016 04:18:04 PM EDT","buildtime": "1453976868","rsaheader": "RSA/SHA256, Tue 02 Feb 2016 09:45:04 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "ca-certificates-2015.2.6-70.1.el7_2.src.rpm"}
{"name": "openscap-scanner","version": "1.3.10","epoch": "(none)","release": "1.el7_2","arch": "noarch","installtime": "Fri 24 Jun 2016 04:18:04 PM EDT","buildtime": "1453976868","rsaheader": "RSA/SHA256, Tue 02 Feb 2016 09:45:04 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "ca-certificates-2015.2.6-70.1.el7_2.src.rpm"}
{"name": "openscap","version": "1.3.10","epoch": "(none)","release": "1.el7_2","arch": "noarch","installtime": "Fri 24 Jun 2016 04:18:04 PM EDT","buildtime": "1453976868","rsaheader": "RSA/SHA256, Tue 02 Feb 2016 09:45:04 AM EST, Key ID 199e2f91fd431d51","dsaheader": "(none)","srpm": "ca-certificates-2015.2.6-70.1.el7_2.src.rpm"}
"""
)


def test_os_version():
    os_good = OsRelease(context_wrap(OS_RELEASE))
    rh_good = RedhatRelease(context_wrap(REDHAT_RELEASE))
    broker = {OsRelease: os_good, RedhatRelease: rh_good}
    result = os_version(broker)
    assert result == ['8', '10']

    os_ng = OsRelease(context_wrap('test=abc'))
    broker = {OsRelease: os_ng, RedhatRelease: rh_good}
    result = os_version(broker)
    assert result == ['8', '10']

    rh_ng = RedhatRelease(context_wrap('test abc'))
    broker = {OsRelease: os_good, RedhatRelease: rh_ng}
    result = os_version(broker)
    assert result == ['8', '10']

    broker = {OsRelease: os_ng, RedhatRelease: rh_ng}
    with raises(SystemExit):
        os_version(broker)


def test_package_check():
    rpms = InstalledRpms(context_wrap(RPMS_JSON))
    broker = {InstalledRpms: rpms}
    result = package_check(broker)
    assert result == '0.1.72'

    rpms = InstalledRpms(context_wrap(RPMS_JSON_NG))
    broker = {InstalledRpms: rpms}
    with raises(SystemExit):
        package_check(broker)


@patch("insights.specs.datasources.compliance.compliance_ds.NamedTemporaryFile")
@patch("insights.specs.datasources.compliance.ComplianceClient.run_scan", return_value=None)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.download_tailoring_file",
    return_value=None,
)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.get_system_policies",
    return_value=[{'ref_id': 'foo', 'id': 'def76af0-9b6f-4b37-ac6c-db61354acbb5'}],
)
@patch(
    "insights.client.config.InsightsConfig",
    base_url='localhost/app',
    systemid='',
    proxy=None,
    compressor='gz',
    compliance=True,
    obfuscation_list=[],
)
def test_compliance_ds(config, policies, dt_file, run_scan, ntmpf):
    content = """
<xml>
    <TestResult xmlns="http://checklists.nist.gov/xccdf/1.2">
      <target-address>obfuscate</target-address>
      <target-facts>
        <fact name="urn:xccdf:fact:asset:identifier:ipv4" type="string">obfuscate</fact>
        <fact name="urn:xccdf:fact:asset:identifier:ipv6" type="string">obfuscate</fact>
      </target-facts>
    </TestResult>
    <arf xmlns="http://scap.nist.gov/schema/asset-identification/1.1">
      <ip-address>
        <ip-v4>obfuscate</ip-v4>
      </ip-address>
      <ip-address>
        <ip-v6>obfuscate</ip-v6>
      </ip-address>
      <mac-address>obfuscate</mac-address>
    </arf>
    <oval xmlns="http://oval.mitre.org/XMLSchema/oval-system-characteristics-5">
      <system-info>
        <interfaces>
          <interface>
            <ip_address>obfuscate</ip_address>
            <mac_address>obfuscate</mac_address>
          </interface>
        </interfaces>
      </system-info>
    </oval>
</xml>
    """
    tmp_file = NamedTemporaryFile(mode='w', delete=False)
    tmp_file.write(content)
    tmp_file.close()
    ntmpf.return_value = tmp_file
    broker = {os_version: ['8', '10'], package_check: '0.1.73', 'client_config': config}
    ret = compliance(broker)
    os.remove(tmp_file.name)
    assert len(ret) == 1
    assert ret[0].relative_path == 'oscap_results-foo.xml'
    assert ret[0].content == content.splitlines()


@patch("insights.specs.datasources.compliance.compliance_ds.NamedTemporaryFile")
@patch("insights.specs.datasources.compliance.ComplianceClient.run_scan", return_value=None)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.download_tailoring_file",
    return_value=None,
)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.get_system_policies",
    return_value=[{'ref_id': 'foo', 'id': 'def76af0-9b6f-4b37-ac6c-db61354acbb5'}],
)
@patch(
    "insights.client.config.InsightsConfig",
    base_url='localhost/app',
    systemid='',
    proxy=None,
    compressor='gz',
    compliance=True,
    obfuscation_list=['ipv4', 'ipv6'],
)
def test_compliance_ds_with_obfuscation(config, policies, dt_file, run_scan, ntmpf):
    content = """
<xml>
    <TestResult xmlns="http://checklists.nist.gov/xccdf/1.2">
      <target-address>obfuscate</target-address>
      <target-facts>
        <fact name="urn:xccdf:fact:asset:identifier:ipv4" type="string">obfuscate</fact>
        <fact name="urn:xccdf:fact:asset:identifier:ipv6" type="string">obfuscate</fact>
      </target-facts>
    </TestResult>
    <arf xmlns="http://scap.nist.gov/schema/asset-identification/1.1">
      <ip-address>
        <ip-v4>obfuscate</ip-v4>
      </ip-address>
      <ip-address>
        <ip-v6>obfuscate</ip-v6>
      </ip-address>
      <mac-address>obfuscate</mac-address>
    </arf>
    <oval xmlns="http://oval.mitre.org/XMLSchema/oval-system-characteristics-5">
      <system-info>
        <interfaces>
          <interface>
            <ip_address>obfuscate</ip_address>
            <mac_address>obfuscate</mac_address>
          </interface>
        </interfaces>
      </system-info>
    </oval>
</xml>
    """
    tmp_file = NamedTemporaryFile(mode='w', delete=False)
    tmp_file.write(content)
    ntmpf.return_value = tmp_file
    tmp_file.close()
    broker = {os_version: ['8', '10'], package_check: '0.1.73', 'client_config': config}
    ret = compliance(broker)
    assert ret[0].relative_path == 'oscap_results-foo.xml'

    obfuscated_results = open(str(tmp_file.name)).read()
    assert '<target-address>obfuscate</target-address>' not in obfuscated_results
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:ipv4" type="string">obfuscate</fact>'
        not in obfuscated_results
    )
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:ipv6" type="string">obfuscate</fact>'
        not in obfuscated_results
    )
    assert '<ip-v4>obfuscate</ip-v4>' not in obfuscated_results
    assert '<ip-v6>obfuscate</ip-v6>' not in obfuscated_results
    assert '<mac-address>obfuscate</mac-address>' not in obfuscated_results
    assert '<ip_address>obfuscate</ip_address>' not in obfuscated_results
    assert '<mac_address>obfuscate</mac_address>' not in obfuscated_results

    content = ' '.join(ret[0].content)
    assert '<target-address>obfuscate</target-address>' not in content
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:ipv4" type="string">obfuscate</fact>'
        not in content
    )
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:ipv6" type="string">obfuscate</fact>'
        not in content
    )
    assert '<ip-v4>obfuscate</ip-v4>' not in content
    assert '<ip-v6>obfuscate</ip-v6>' not in content
    assert '<mac-address>obfuscate</mac-address>' not in content
    assert '<ip_address>obfuscate</ip_address>' not in content
    assert '<mac_address>obfuscate</mac_address>' not in content
    os.remove(tmp_file.name)


@patch("insights.specs.datasources.compliance.compliance_ds.NamedTemporaryFile")
@patch("insights.specs.datasources.compliance.ComplianceClient.run_scan", return_value=None)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.download_tailoring_file",
    return_value=None,
)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.get_system_policies",
    return_value=[{'ref_id': 'foo', 'id': 'def76af0-9b6f-4b37-ac6c-db61354acbb5'}],
)
@patch(
    "insights.client.config.InsightsConfig",
    base_url='localhost/app',
    systemid='',
    proxy=None,
    compressor='gz',
    compliance=True,
    obfuscation_list=['ipv4', 'ipv6', 'hostname'],
)
def test_compliance_ds_with_hostname_obfuscation(config, policies, dt_file, run_scan, ntmpf):
    content = """
<xml>
    <TestResult xmlns="http://checklists.nist.gov/xccdf/1.2">
      <target>obfuscate</target>
      <target-address>obfuscate</target-address>
      <target-facts>
        <fact name="urn:xccdf:fact:asset:identifier:fqdn" type="string">obfuscate</fact>
        <fact name="urn:xccdf:fact:asset:identifier:host_name" type="string">obfuscate</fact>
      </target-facts>
    </TestResult>
    <arf xmlns="http://scap.nist.gov/schema/asset-identification/1.1">
      <ip-address>
        <ip-v4>obfuscate</ip-v4>
      </ip-address>
      <ip-address>
        <ip-v6>obfuscate</ip-v6>
      </ip-address>
      <mac-address>obfuscate</mac-address>
    </arf>
    <oval xmlns="http://oval.mitre.org/XMLSchema/oval-system-characteristics-5">
      <system_info>
        <interfaces>
          <interface>
            <ip_address>obfuscate</ip_address>
            <mac_address>obfuscate</mac_address>
          </interface>
        </interfaces>
        <primary_host_name>obfuscate</primary_host_name>
        <node_name>obfuscate</node_name>
      </system_info>
    </oval>
    <ai xmlns="http://scap.nist.gov/schema/asset-identification/1.1">
      <hostname>obfuscate</hostname>
    </ai>
</xml>
    """
    tmp_file = NamedTemporaryFile(mode='w', delete=False)
    tmp_file.write(content)
    ntmpf.return_value = tmp_file
    tmp_file.close()
    broker = {os_version: ['8', '10'], package_check: '0.1.73', 'client_config': config}
    ret = compliance(broker)

    obfuscated_results = open(str(tmp_file.name)).read()
    assert '<target-address>obfuscate</target-address>' not in obfuscated_results
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:fqdn" type="string">obfuscate</fact>'
        not in obfuscated_results
    )
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:host_name" type="string">obfuscate</fact>'
        not in obfuscated_results
    )
    assert '<ip-v4>obfuscate</ip-v4>' not in obfuscated_results
    assert '<ip-v6>obfuscate</ip-v6>' not in obfuscated_results
    assert '<mac-address>obfuscate</mac-address>' not in obfuscated_results
    assert '<ip_address>obfuscate</ip_address>' not in obfuscated_results
    assert '<mac_address>obfuscate</mac_address>' not in obfuscated_results
    assert '<fqdn>obfuscate</fqdn>' not in obfuscated_results
    assert '<hostname>obfuscate</hostname>' not in obfuscated_results
    assert '<target>obfuscate</target>' not in obfuscated_results
    assert '<primary_host_name>obfuscate</primary_host_name>' not in obfuscated_results
    assert '<node_name>obfuscate</node_name>' not in obfuscated_results

    content = ' '.join(ret[0].content)
    assert '<target-address>obfuscate</target-address>' not in content
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:fqdn" type="string">obfuscate</fact>'
        not in content
    )
    assert (
        '<fact name="urn:xccdf:fact:asset:identifier:host_name" type="string">obfuscate</fact>'
        not in content
    )
    assert '<ip-v4>obfuscate</ip-v4>' not in content
    assert '<ip-v6>obfuscate</ip-v6>' not in content
    assert '<mac-address>obfuscate</mac-address>' not in content
    assert '<ip_address>obfuscate</ip_address>' not in content
    assert '<mac_address>obfuscate</mac_address>' not in content
    assert '<fqdn>obfuscate</fqdn>' not in content
    assert '<hostname>obfuscate</hostname>' not in content
    assert '<target>obfuscate</target>' not in content
    assert '<primary_host_name>obfuscate</primary_host_name>' not in content
    assert '<node_name>obfuscate</node_name>' not in content
    os.remove(tmp_file.name)


@patch("insights.specs.datasources.compliance.compliance_ds.NamedTemporaryFile")
@patch("insights.specs.datasources.compliance.ComplianceClient.run_scan", return_value=None)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.download_tailoring_file",
    return_value=None,
)
@patch(
    "insights.specs.datasources.compliance.ComplianceClient.get_system_policies",
    return_value=[{'ref_id': 'foo', 'id': 'def76af0-9b6f-4b37-ac6c-db61354acbb5'}],
)
@patch(
    "insights.client.config.InsightsConfig",
    base_url='localhost/app',
    systemid='',
    proxy=None,
    compressor='gz',
    compliance=True,
)
def test_compliance_ds_with_results_repaired(config, policies, dt_file, run_scan, ntmpf):
    tmp_file = NamedTemporaryFile(mode='w', delete=False)
    tmp_file.write(
        """
<xml>
  <version>0.9</version>
</xml>
    """
    )
    ntmpf.return_value = tmp_file
    tmp_file.close()
    broker = {os_version: ['8', '10'], package_check: '0.1.25', 'client_config': config}
    ret = compliance(broker)
    os.remove(tmp_file.name)

    # repaired data is not write back to the file
    content = ' '.join(ret[0].content)
    assert '<version>0.1.25</version>' in content


@patch("insights.specs.datasources.compliance.compliance_ds.sys")
@patch("insights.specs.datasources.compliance.ComplianceClient.assignable_policies")
def test_compliance_policies(assignable_policies, sys):
    config = InsightsConfig(compliance_policies=True)
    broker = {os_version: ['9', '3'], package_check: '0.1.25', 'client_config': config}
    compliance_policies(broker)
    assignable_policies.assert_called_with()
    sys.exit.assert_called_with(assignable_policies.return_value)


@patch("insights.specs.datasources.compliance.compliance_ds.sys")
@patch("insights.specs.datasources.compliance.ComplianceClient.policy_link")
def test_policy_link_assign(policy_link, sys):
    config = InsightsConfig(compliance_assign='123abc')
    broker = {os_version: ['9', '3'], package_check: '0.1.25', 'client_config': config}
    compliance_assign(broker)
    policy_link.assert_called_with('123abc', 'patch')
    sys.exit.assert_called_with(policy_link.return_value)


@patch("insights.specs.datasources.compliance.compliance_ds.sys")
@patch("insights.specs.datasources.compliance.ComplianceClient.policy_link")
def test_policy_link_unassign(policy_link, sys):
    config = InsightsConfig(compliance_unassign='123abc')
    broker = {os_version: ['9', '3'], package_check: '0.1.25', 'client_config': config}
    compliance_unassign(broker)
    policy_link.assert_called_with('123abc', 'delete')
    sys.exit.assert_called_with(policy_link.return_value)
