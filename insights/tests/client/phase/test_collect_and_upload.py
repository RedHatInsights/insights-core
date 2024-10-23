# -*- coding: UTF-8 -*-

from insights.client.phase.v1 import collect_and_output
from mock.mock import patch
from pytest import raises


def patch_insights_config(old_function):
    patcher = patch("insights.client.phase.v1.InsightsConfig",
                    **{"return_value.load_all.return_value.status": False,
                       "return_value.load_all.return_value.unregister": False,
                       "return_value.load_all.return_value.offline": False,
                       "return_value.load_all.return_value.enable_schedule": False,
                       "return_value.load_all.return_value.disable_schedule": False,
                       "return_value.load_all.return_value.analyze_container": False,
                       "return_value.load_all.return_value.display_name": False,
                       "return_value.load_all.return_value.to_stdout": False,
                       "return_value.load_all.return_value.no_upload": False,
                       "return_value.load_all.return_value.to_json": False,
                       "return_value.load_all.return_value.keep_archive": False,
                       "return_value.load_all.return_value.register": False,
                       "return_value.load_all.return_value.diagnosis": None,
                       "return_value.load_all.return_value.payload": None,
                       "return_value.load_all.return_value.manifest": None,
                       "return_value.load_all.return_value.content_type": None,
                       "return_value.load_all.return_value.compliance": False,
                       "return_value.load_all.return_value.compliance_policies": False,
                       "return_value.load_all.return_value.compliance_assign": None,
                       "return_value.load_all.return_value.compliance_unassign": None,
                       "return_value.load_all.return_value.module": False,
                       "return_value.load_all.return_value.output_dir": None,
                       "return_value.load_all.return_value.output_file": None})
    return patcher(old_function)


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_collect_and_output_payload_on(insights_config, insights_client):
    """
    Collection is not done when a payload is uploaded
    Payload is sent to upload function
    Archive is not deleted
    """
    insights_config.return_value.load_all.return_value.payload = 'testp'
    insights_config.return_value.load_all.return_value.content_type = 'testct'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.collect.assert_not_called()
    insights_client.return_value.upload.assert_called_with(payload='testp', content_type='testct')
    insights_client.return_value.delete_cached_branch_info.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_collect_and_output_payload_off(insights_config, insights_client):
    """
    Collection is done and uploaded in normal operation (no payload)
    Archive deleted after upload
    """
    insights_config.return_value.load_all.return_value.payload = False
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.collect.assert_called_once()
    insights_client.return_value.upload.assert_called_with(
        payload=insights_client.return_value.collect.return_value,
        content_type='application/vnd.redhat.advisor.collection+tgz')
    insights_client.return_value.delete_cached_branch_info.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_collect_and_output_payload_on_default(insights_config, insights_client):
    insights_config.return_value.load_all.return_value.content_type = 'bz2'
    insights_config.return_value.load_all.return_value.payload = 'testct.bz2'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.collect.assert_not_called()
    insights_client.return_value.upload.assert_called_with(payload='testct.bz2', content_type='application/vnd.redhat.advisor.collection+bz2')
    insights_client.return_value.delete_cached_branch_info.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_collect_and_output_different_payload_type(insights_config, insights_client):
    insights_config.return_value.load_all.return_value.content_type = 'bz2'
    insights_config.return_value.load_all.return_value.payload = 'testct.tgz'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.collect.assert_not_called()
    insights_client.return_value.upload.assert_not_called()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_collect_and_output_none_payload_type(insights_config, insights_client):
    insights_config.return_value.load_all.return_value.payload = 'testct'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.collect.assert_not_called()
    insights_client.return_value.upload.assert_called_with(payload='testct', content_type=None)
    insights_client.return_value.delete_cached_branch_info.assert_called_once()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
# @patch("insights.client.phase.v1.InsightsClient")
def test_exit_ok(insights_config, insights_client):
    """
    Support collection replaces the normal client run.
    """
    with raises(SystemExit) as exc_info:
        collect_and_output()
    assert exc_info.value.code == 0


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_no_upload(insights_config, insights_client):
    '''
    Copy collected data to a specified file and do not upload.
    '''
    insights_config.return_value.load_all.return_value.no_upload = True
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.upload.assert_not_called()


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_output_file(insights_config, insights_client):
    '''
    Copy collected data to a specified file and do not upload.
    '''
    insights_config.return_value.load_all.return_value.no_upload = True
    insights_config.return_value.load_all.return_value.output_file = '/var/tmp/test.tar.gz'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.copy_to_output_file.assert_called_with(insights_client.return_value.collect.return_value)


@patch("insights.client.phase.v1.InsightsClient")
@patch_insights_config
def test_output_dir(insights_config, insights_client):
    '''
    Copy collected data to a specified directory and do not upload.
    '''
    insights_config.return_value.load_all.return_value.no_upload = True
    insights_config.return_value.load_all.return_value.output_dir = '/var/tmp/test'
    try:
        collect_and_output()
    except SystemExit:
        pass
    insights_client.return_value.copy_to_output_dir.assert_called_with(insights_client.return_value.collect.return_value)
