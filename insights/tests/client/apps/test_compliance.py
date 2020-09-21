# -*- coding: UTF-8 -*-

from insights.client.apps.compliance import ComplianceClient, COMPLIANCE_CONTENT_TYPE
from mock.mock import patch, Mock, mock_open
from pytest import raises
import os
import six

PATH = '/usr/share/xml/scap/ref_id.xml'


@patch("insights.client.apps.compliance.ComplianceClient._assert_oscap_rpms_exist")
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None, compressor='gz')
def test_oscap_scan(config, assert_rpms):
    compliance_client = ComplianceClient(config)
    compliance_client.get_policies = lambda: [{'attributes': {'ref_id': 'foo', 'tailored': False}}]
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml, output_path, tailoring_file_path: None
    compliance_client.archive.archive_tmp_dir = '/tmp'
    compliance_client.archive.archive_name = 'insights-compliance-test'
    archive, content_type = compliance_client.oscap_scan()
    assert archive == '/tmp/insights-compliance-test.tar.gz'
    assert content_type == COMPLIANCE_CONTENT_TYPE


@patch("insights.client.apps.compliance.call", return_value=(0, ''))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_missing_packages(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.get_policies = lambda: [{'attributes': {'ref_id': 'foo'}}]
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml: None
    with raises(SystemExit):
        compliance_client.oscap_scan()


@patch("insights.client.apps.compliance.call", return_value=(1, ''))
@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_errored_rpm_call(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.get_policies = lambda: [{'attributes': {'ref_id': 'foo'}}]
    compliance_client.find_scap_policy = lambda ref_id: '/usr/share/xml/scap/foo.xml'
    compliance_client.run_scan = lambda ref_id, policy_xml: None
    with raises(SystemExit):
        compliance_client.oscap_scan()


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_policies(config):
    compliance_client = ComplianceClient(config)
    compliance_client.hostname = 'foo'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    assert compliance_client.get_policies() == [{'attributes': 'data'}]
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_names=foo external=false canonical=false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_policies_no_policies(config):
    compliance_client = ComplianceClient(config)
    compliance_client.hostname = 'foo'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': []})))
    assert compliance_client.get_policies() == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_names=foo external=false canonical=false'})


@patch("insights.client.config.InsightsConfig", base_url='localhost/app', systemid='', proxy=None)
def test_get_policies_error(config):
    compliance_client = ComplianceClient(config)
    compliance_client.hostname = 'foo'
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=500))
    assert compliance_client.get_policies() == []
    compliance_client.conn.session.get.assert_called_with('https://localhost/app/compliance/profiles', params={'search': 'system_names=foo external=false canonical=false'})


@patch("insights.client.apps.compliance.linux_distribution", return_value=(None, '6.5', None))
@patch("insights.client.config.InsightsConfig")
def test_os_release(config, linux_distro_mock):
    compliance_client = ComplianceClient(config)
    assert compliance_client.os_release() == '6'


@patch("insights.client.config.InsightsConfig")
def test_profile_files(config):
    compliance_client = ComplianceClient(config)
    compliance_client.os_release = lambda: '7'
    assert compliance_client.profile_files() == []


@patch("insights.client.apps.compliance.call", return_value=(0, PATH))
@patch("insights.client.config.InsightsConfig")
def test_find_scap_policy(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') == PATH


@patch("insights.client.apps.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig")
def test_find_scap_policy_not_found(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.profile_files = lambda: ['/something']
    assert compliance_client.find_scap_policy('ref_id') is None


@patch("insights.client.apps.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig")
def test_run_scan(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.client.apps.compliance.call", return_value=(1, 'bad things happened'.encode('utf-8')))
@patch("insights.client.config.InsightsConfig")
def test_run_scan_fail(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    with raises(SystemExit):
        compliance_client.run_scan('ref_id', '/nonexistent', output_path)
    if six.PY3:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent'), keep_rc=True, env=env)
    else:
        call.assert_called_with(("oscap xccdf eval --profile ref_id --results " + output_path + ' /nonexistent').encode(), keep_rc=True, env=env)


@patch("insights.client.apps.compliance.call", return_value=(0, ''.encode('utf-8')))
@patch("insights.client.config.InsightsConfig")
def test_run_scan_missing_profile(config, call):
    compliance_client = ComplianceClient(config)
    output_path = '/tmp/oscap_results-ref_id.xml'
    env = os.environ
    env.update({'TZ': 'UTC'})
    assert compliance_client.run_scan('ref_id', None, output_path) is None
    call.assert_not_called()


@patch("insights.client.config.InsightsConfig")
def test_tailored_file_is_not_downloaded_if_not_needed(config):
    compliance_client = ComplianceClient(config)
    assert compliance_client.download_tailoring_file({'attributes': {'tailored': False}}) is None


@patch("insights.client.config.InsightsConfig")
def test_tailored_file_is_not_downloaded_if_tailored_is_missing(config):
    compliance_client = ComplianceClient(config)
    assert compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'ref_id': 'aaaaa'}}) is None


@patch("insights.client.apps.compliance.open", new_callable=mock_open)
@patch("insights.client.config.InsightsConfig")
def test_tailored_file_is_downloaded_if_needed(config, call):
    compliance_client = ComplianceClient(config)
    compliance_client.conn.session.get = Mock(return_value=Mock(status_code=200, json=Mock(return_value={'data': [{'attributes': 'data'}]})))
    tailoring_file_path = "/var/tmp/oscap_tailoring_file-aaaaa.xml"
    assert tailoring_file_path == compliance_client.download_tailoring_file({'id': 'foo', 'attributes': {'tailored': True, 'ref_id': 'aaaaa'}})


@patch("insights.client.config.InsightsConfig")
def test_build_oscap_command_does_not_append_tailoring_path(config):
    compliance_client = ComplianceClient(config)
    expected_command = 'oscap xccdf eval --profile aaaaa --results output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', None)


@patch("insights.client.config.InsightsConfig")
def test_build_oscap_command_append_tailoring_path(config):
    compliance_client = ComplianceClient(config)
    expected_command = 'oscap xccdf eval --profile aaaaa --tailoring-file tailoring_path --results output_path xml_sample'
    assert expected_command == compliance_client.build_oscap_command('aaaaa', 'xml_sample', 'output_path', 'tailoring_path')
