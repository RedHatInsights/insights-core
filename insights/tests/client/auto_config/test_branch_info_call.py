from insights.client.auto_config import set_auto_configuration
from mock.mock import Mock, patch


@patch("insights.client.auto_config.InsightsConnection")
def test_sat_branch_info_called(connection):
    '''
    When is_satellite is True, means we're on sat. get_branch_info should be called.
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    set_auto_configuration(config, 'test.com:443/redhat_access', 'some_cert', None, True)
    connection.return_value.get_branch_info.assert_called_once()


@patch("insights.client.auto_config.InsightsConnection")
def test_rhsm_branch_info_not_called(connection):
    '''
    When is_satellite is False, means we're on direct RHSM. get_branch_info should not be called.
    '''
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    set_auto_configuration(config, 'cert-api.access.redhat.com', None, None, False)
    connection.return_value.get_branch_info.assert_not_called()
