from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_url_guess_legacy(get_proxies, init_session):
    """
    Connection should guess the right URLs if there's nothing in the config (the default)
    """
    config = Mock(base_url=None, upload_url=None, legacy_upload=True, insecure_connection=False, analyze_container=False)

    connection = InsightsConnection(config)
    assert connection.base_url == 'https://cert-api.access.redhat.com/r/insights'
    assert connection.upload_url == 'https://cert-api.access.redhat.com/r/insights/uploads'


@patch("insights.client.connection.InsightsConnection._init_session")
@patch("insights.client.connection.InsightsConnection.get_proxies")
def test_url_guess_platform(get_proxies, init_session):
    """
    Connection should guess the right URLs if there's nothing in the config (the default)
    """
    config = Mock(base_url=None, upload_url=None, legacy_upload=False, insecure_connection=False)

    connection = InsightsConnection(config)
    assert connection.base_url == 'https://cloud.redhat.com/api'
    assert connection.upload_url == 'https://cloud.redhat.com/api/ingress/v1/upload'
