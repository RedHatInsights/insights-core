# -*- coding: UTF-8 -*-

from insights.client.apps.compliance import ComplianceClient, COMPLIANCE_CONTENT_TYPE
from mock.mock import patch, Mock, mock_open
from pytest import raises
import os
import six

PATH = '/usr/share/xml/scap/ref_id.xml'


@patch("insights.client.apps.compliance.ComplianceClient._assert_oscap_rpms_exist")
@patch("insights.client.apps.compliance.ComplianceClient.get_ssg_version", return_value=None)
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None, compressor='gz', obfuscate=False)
@patch("insights.client.archive.atexit", Mock())
def test_oscap_scan(config, ssg_version, assert_rpms):
    compliance_client = ComplianceClient(config)
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo', 'tailored': False}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml, output_path, tailoring_file_path: None
    compliance_client.archive.archive_tmp_dir = '/tmp'
    compliance_client.archive.archive_name = 'insights-compliance-test'
    archive, content_type = compliance_client.oscap_scan()
    assert archive == '/tmp/insights-compliance-test.tar.gz'
    assert content_type == COMPLIANCE_CONTENT_TYPE


@patch("insights.client.apps.compliance.ComplianceClient._assert_oscap_rpms_exist")
@patch("insights.client.apps.compliance.ComplianceClient.get_ssg_version", return_value=None)
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None, compressor='gz', obfuscate=True)
@patch("insights.client.archive.atexit", Mock())
def test_oscap_scan_with_obfuscation(config, ssg_version, assert_rpms, tmpdir):
    results_file = tmpdir.mkdir('results').join('result.xml')
    results_file.write("""
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
    """)

    compliance_client = ComplianceClient(config)
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo', 'tailored': False}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client._results_file = lambda archive_dir, profile: str(results_file)
    compliance_client.run_scan = lambda ref_id, policy_xml, output_path, tailoring_file_path: None
    compliance_client.archive.archive_tmp_dir = '/tmp'
    compliance_client.archive.archive_name = 'insights-compliance-test'
    archive, content_type = compliance_client.oscap_scan()
    assert archive == '/tmp/insights-compliance-test.tar.gz'
    assert content_type == COMPLIANCE_CONTENT_TYPE
    obfuscated_results = open(str(results_file)).read()
    assert '<target-address>obfuscate</target-address>' not in obfuscated_results
    assert '<fact name="urn:xccdf:fact:asset:identifier:ipv4" type="string">obfuscate</fact>' not in obfuscated_results
    assert '<fact name="urn:xccdf:fact:asset:identifier:ipv6" type="string">obfuscate</fact>' not in obfuscated_results
    assert '<ip-v4>obfuscate</ip-v4>' not in obfuscated_results
    assert '<ip-v6>obfuscate</ip-v6>' not in obfuscated_results
    assert '<mac-address>obfuscate</mac-address>' not in obfuscated_results
    assert '<ip_address>obfuscate</ip_address>' not in obfuscated_results
    assert '<mac_address>obfuscate</mac_address>' not in obfuscated_results


@patch("insights.client.apps.compliance.ComplianceClient._assert_oscap_rpms_exist")
@patch("insights.client.apps.compliance.ComplianceClient.get_ssg_version", return_value=None)
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None, compressor='gz', obfuscate=True, obfuscate_hostname=True)
@patch("insights.client.archive.atexit", Mock())
def test_oscap_scan_with_hostname_obfuscation(config, ssg_version, assert_rpms, tmpdir):
    results_file = tmpdir.mkdir('results').join('result.xml')
    results_file.write("""
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
    """)

    compliance_client = ComplianceClient(config)
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo', 'tailored': False}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client._results_file = lambda archive_dir, profile: str(results_file)
    compliance_client.run_scan = lambda ref_id, policy_xml, output_path, tailoring_file_path: None
    compliance_client.archive.archive_tmp_dir = '/tmp'
    compliance_client.archive.archive_name = 'insights-compliance-test'
    archive, content_type = compliance_client.oscap_scan()
    assert archive == '/tmp/insights-compliance-test.tar.gz'
    assert content_type == COMPLIANCE_CONTENT_TYPE

    obfuscated_results = open(str(results_file)).read()
    assert '<target-address>obfuscate</target-address>' not in obfuscated_results
    assert '<fact name="urn:xccdf:fact:asset:identifier:fqdn" type="string">obfuscate</fact>' not in obfuscated_results
    assert '<fact name="urn:xccdf:fact:asset:identifier:host_name" type="string">obfuscate</fact>' not in obfuscated_results
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


@patch("insights.client.apps.compliance.ComplianceClient._assert_oscap_rpms_exist")
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None, compressor='gz')
@patch("insights.client.archive.atexit", Mock())
def test_oscap_scan_with_results_repaired(config, assert_rpms, tmpdir):
    results_file = tmpdir.mkdir('results').join('result.xml')
    results_file.write("""
<xml>
  <version>0.9</version>
</xml>
    """)

    compliance_client = ComplianceClient(config)
    compliance_client._ssg_version = '0.1.25'
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo', 'tailored': False}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client._results_file = lambda archive_dir, profile: str(results_file)
    compliance_client.run_scan = lambda ref_id, policy_xml, output_path, tailoring_file_path: None
    compliance_client.archive.archive_tmp_dir = '/tmp'
    compliance_client.archive.archive_name = 'insights-compliance-test'
    archive, content_type = compliance_client.oscap_scan()
    assert archive == '/tmp/insights-compliance-test.tar.gz'
    assert content_type == COMPLIANCE_CONTENT_TYPE

    repaired_results = open(str(results_file)).read()
    assert '<version>0.1.25</version>' in repaired_results


@patch("insights.client.apps.compliance.call", return_value=(0, ''))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_missing_packages(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo'}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml: None
    with raises(SystemExit):
        compliance_client.oscap_scan()


@patch("insights.client.apps.compliance.call", return_value=(1, ''))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_errored_rpm_call(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client._get_inventory_id = lambda: ''
    compliance_client.get_initial_profiles = lambda: [{'attributes': {'ref_id': 'foo'}}]
    compliance_client.get_profiles_matching_os = lambda: []
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml: None
    with raises(SystemExit):
        compliance_client.oscap_scan()


@patch("insights.client.apps.compliance.call", return_value=(0, '1.2.3'))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_ssg_version(config, call):
    ssg_version = ComplianceClient(config).ssg_version
    assert ssg_version == '1.2.3'
    call.assert_called_with('rpm -qa --qf "%{VERSION}" scap-security-guide', keep_rc=True)


@patch("insights.client.apps.compliance.call", return_value=(1, '0.0.0'))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_ssg_version_with_failure(config, call):
    ssg_version = ComplianceClient(config).ssg_version
    assert not ssg_version
    call.assert_called_with('rpm -qa --qf "%{VERSION}" scap-security-guide', keep_rc=True)


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles(config):
    compliance_client = ComplianceClient(config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_profiles('search string') == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_no_profiles(config):
    compliance_client = ComplianceClient(config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': []})))
    assert compliance_client.get_profiles('search string') == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_error(config):
    compliance_client = ComplianceClient(config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=500))
    assert compliance_client.get_profiles('search string') == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_initial_profiles(config):
    compliance_client = ComplianceClient(config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_initial_profiles() == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_ids=068040f1-08c8-43e4-949f-7d6470e9111c canonical=false external=false', 'relationships': 'false'})


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_matching_os(config, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_profiles_matching_os() == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_ids=068040f1-08c8-43e4-949f-7d6470e9111c canonical=false os_minor_version=5', 'relationships': 'false'})


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_os_release(config, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    assert compliance_client.os_release() == '6.5'


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/tests')
def test_os_minor_version(config, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    assert compliance_client.os_minor_version() == '5'


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_os_major_version(config, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    assert compliance_client.os_major_version() == '6'


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_profile_files(config):
    compliance_client = ComplianceClient(config)
    compliance_client.os_release = lambda: '7'
    assert compliance_client.profile_files() == []


@patch("insights.client.apps.compliance.call", return_value=(0, PATH))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') == PATH


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_with_one_datastream_file(config, tmpdir):
    compliance_client = ComplianceClient(config)
    dir1 = tmpdir.mkdir('scap')
    file = dir1.join('test_file.xml')
    file.write("""
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_anssi_bp28_high">
    </xccdf-1.2:Profile>
        """)
    compliance_client.profile_files = lambda: [str(file)]
    with patch("insights.client.apps.compliance.SCAP_DATASTREAMS_PATH", str(dir1) + "/"):
        assert compliance_client.find_scap_policy('content_profile_anssi_bp28_high') == file


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_with_two_datastream_file(config, tmpdir):
    compliance_client = ComplianceClient(config)
    dir1 = tmpdir.mkdir('scap')
    file1 = dir1.join('test_file1.xml')
    file1.write("""
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_anssi_bp28_high">
    </xccdf-1.2:Profile>
        """)
    file2 = dir1.join('test_file2.xml')
    file2.write("""
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_anssi_bp28_high">
    </xccdf-1.2:Profile>
        """)
    compliance_client.profile_files = lambda: [str(file1), str(file2)]
    with patch("insights.client.apps.compliance.SCAP_DATASTREAMS_PATH", str(dir1) + "/"):
        assert compliance_client.find_scap_policy('content_profile_anssi_bp28_high') == file1


@patch("insights.client.apps.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_not_found(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') is None


@patch("insights.client.apps.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results-arf " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results-arf " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.client.apps.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan_fail(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    with raises(SystemExit):
        compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results-arf " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results-arf " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.client.apps.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan_missing_profile(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    assert compliance_client.run_scan('ref_id', None, output_path) is None
    call.assert_not_called()


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_not_needed(config):
    compliance_client = ComplianceClient(config)
    assert compliance_client.download_tailoring_file({'attributes': {'tailored': False}}) is None


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_tailored_is_missing(config):
    compliance_client = ComplianceClient(config)
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'ref_id': 'aaaaa'}}) is None


@patch("insights.client.apps.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_downloaded_from_initial_profile_if_os_minor_version_is_missing(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert 'oscap_tailoring_file-aaaaa' in compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}})
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa'}}) is None


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_os_minor_version_mismatches(config, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa', 'os_minor_version': '2'}}) is None
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa', 'os_minor_version': '2'}}) is None


@patch("insights.client.apps.compliance.os_release_info", return_value=(None, '6.5'))
@patch("insights.client.apps.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_downloaded_if_needed(config, call, os_release_info_mock):
    compliance_client = ComplianceClient(config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert 'oscap_tailoring_file-aaaaa' in compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa', 'os_minor_version': '5'}})
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa', 'os_minor_version': '5'}}) is None


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_build_oscap_command_does_not_append_tailoring_path(config):
    compliance_client = ComplianceClient(config)
    expected_command = 'oscap xccdf eval --profile aaaaa --results-arf output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', None)


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_build_oscap_command_append_tailoring_path(config):
    compliance_client = ComplianceClient(config)
    expected_command = 'oscap xccdf eval --profile aaaaa --tailoring-file tailoring_path --results-arf output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', 'tailoring_path')


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test__get_inventory_id(config):
    compliance_client = ComplianceClient(config)
    compliance_client.conn._fetch_system_by_machine_id = lambda: []
    with raises(SystemExit):
        compliance_client._get_inventory_id()

    compliance_client.conn._fetch_system_by_machine_id = lambda: [{}]
    with raises(SystemExit):
        compliance_client._get_inventory_id()

    compliance_client.conn._fetch_system_by_machine_id = lambda: [{'id': '12345'}]
    assert compliance_client._get_inventory_id() == '12345'
