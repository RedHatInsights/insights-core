from insights.client.session import InsightsSession
from mock.mock import MagicMock, Mock, patch


@patch("insights.client.session.InsightsSession.request", MagicMock())
@patch("insights.client.session.InsightsSession._set_proxy_authorization",
        MagicMock())
def test_proxy_request():
    """
    If proxy authentication is enabled, the failing hacky request is issued
    with correct timeout set.
    """
    config = Mock()

    config.user_agent = None
    config.systemid = None
    config.authmethod = "BASIC"
    config.username = "some username"
    config.password = "some password"
    config.cert_verify = None
    config.proxy = "https://foo:bar@www.example.com"
    config.base_url = "cert-api.access.redhat.com/r/insights"
    config.insecure_connection = True
    session = InsightsSession.from_config(config)

    session.request.assert_called_once_with(
        "GET",
        "https://cert-api.access.redhat.com/r/insights"
    )
