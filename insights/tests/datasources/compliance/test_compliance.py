# -*- coding: UTF-8 -*-
import os
import six

from insights.specs.datasources.compliance import ComplianceClient
from mock.mock import patch, Mock, mock_open
from pytest import raises

PATH = '/usr/share/xml/scap/ref_id.xml'


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_profiles('search string') == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_no_profiles(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': []})))
    assert compliance_client.get_profiles('search string') == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_error(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=500))
    assert compliance_client.get_profiles('search string') == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'search string', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_initial_profiles(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_initial_profiles() == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_ids=068040f1-08c8-43e4-949f-7d6470e9111c canonical=false external=false', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_profiles_matching_os(config):
    compliance_client = ComplianceClient(os_version=['6', '5'], config=config)
    compliance_client.inventory_id = '068040f1-08c8-43e4-949f-7d6470e9111c'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_profiles_matching_os() == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_ids=068040f1-08c8-43e4-949f-7d6470e9111c canonical=false os_minor_version=5', 'relationships': 'false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_profile_files(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.os_release = lambda: '7'
    assert compliance_client.profile_files() == []


@patch("insights.specs.datasources.compliance.call", return_value=(0, PATH))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy(config, call):
    compliance_client = ComplianceClient(config=config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') == PATH


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_with_one_datastream_file(config, tmpdir):
    compliance_client = ComplianceClient(config=config)
    dir1 = tmpdir.mkdir('scap')
    file = dir1.join('test_file.xml')
    file.write("""
    <xccdf-1.2:Profile id="xccdf_org.ssgproject.content_profile_anssi_bp28_high">
    </xccdf-1.2:Profile>
        """)
    compliance_client.profile_files = lambda: [str(file)]
    with patch("insights.specs.datasources.compliance.SCAP_DATASTREAMS_PATH", str(dir1) + "/"):
        assert compliance_client.find_scap_policy('content_profile_anssi_bp28_high') == file


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_with_two_datastream_file(config, tmpdir):
    compliance_client = ComplianceClient(config=config)
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
    with patch("insights.specs.datasources.compliance.SCAP_DATASTREAMS_PATH", str(dir1) + "/"):
        assert compliance_client.find_scap_policy('content_profile_anssi_bp28_high') == file1


@patch("insights.specs.datasources.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_find_scap_policy_not_found(config, call):
    compliance_client = ComplianceClient(config=config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') is None


@patch("insights.specs.datasources.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan(config, call):
    compliance_client = ComplianceClient(config=config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.specs.datasources.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan_fail(config, call):
    compliance_client = ComplianceClient(config=config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    with raises(SystemExit):
        compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.specs.datasources.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_run_scan_missing_profile(config, call):
    compliance_client = ComplianceClient(config=config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    assert compliance_client.run_scan('ref_id', None, output_path) is None
    call.assert_not_called()


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_not_needed(config):
    compliance_client = ComplianceClient(config=config)
    assert compliance_client.download_tailoring_file({'attributes': {'tailored': False}}) is None


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_tailored_is_missing(config):
    compliance_client = ComplianceClient(config=config)
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'ref_id': 'aaaaa'}}) is None


@patch("insights.specs.datasources.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_downloaded_from_initial_profile_if_os_minor_version_is_missing(config, call):
    compliance_client = ComplianceClient(config=config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, headers={"Content-Type": "application/xml"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert 'oscap_tailoring_file-aaaaa' in compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}})
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa'}}) is None


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_not_downloaded_if_os_minor_version_mismatches(config):
    compliance_client = ComplianceClient(os_version=['6', '5'], config=config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, headers={"Content-Type": "application/xml"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa', 'os_minor_version': '2'}}) is None
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa', 'os_minor_version': '2'}}) is None


@patch("insights.specs.datasources.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_is_downloaded_if_needed(config, call):
    compliance_client = ComplianceClient(os_version=['6', '5'], config=config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, headers={"Content-Type": "application/xml"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert 'oscap_tailoring_file-aaaaa' in compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa', 'os_minor_version': '5'}})
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': False, 'ref_id': 'aaaaa', 'os_minor_version': '5'}}) is None


@patch("insights.specs.datasources.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_tailored_file_fails_to_download(config, call):
    compliance_client = ComplianceClient(config=config)

    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=403, ok=False, headers={"Content-Type": "application/xml"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}}) is None

    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, headers={"Content-Type": "application/json"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}}) is None

    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, content=None, headers={"Content-Type": "application/xml"}, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}}) is None


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_build_oscap_command_does_not_append_tailoring_path(config):
    compliance_client = ComplianceClient(config=config)
    expected_command = 'oscap xccdf eval --profile aaaaa --results output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', None)


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test_build_oscap_command_append_tailoring_path(config):
    compliance_client = ComplianceClient(config=config)
    expected_command = 'oscap xccdf eval --profile aaaaa --tailoring-file tailoring_path --results output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', 'tailoring_path')


@patch("insights.client.config.InsightsConfig", base_url='localhost.com/app')
def test__get_inventory_id(config):
    compliance_client = ComplianceClient(config=config)
    compliance_client.conn._fetch_system_by_machine_id = lambda: []
    with raises(SystemExit):
        compliance_client._get_inventory_id()

    compliance_client.conn._fetch_system_by_machine_id = lambda: [{}]
    with raises(SystemExit):
        compliance_client._get_inventory_id()

    compliance_client.conn._fetch_system_by_machine_id = lambda: [{'id': '12345'}]
    assert compliance_client._get_inventory_id() == '12345'
