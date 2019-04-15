from insights.client.auto_config import set_auto_configuration
from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.auto_config.InsightsConnection")
def test_sat_branch_info_called(connection):
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    set_auto_configuration(config, 'test.com:443/redhat_access', 'some_cert', None)
    connection.return_value.get_branch_info.assert_called_once()


@patch("insights.client.auto_config.InsightsConnection")
def test_rhsm_branch_info_not_called(connection):
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)
    set_auto_configuration(config, 'test.com', None, None)
    connection.return_value.get_branch_info.assert_not_called()
