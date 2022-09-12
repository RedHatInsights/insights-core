from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch
from os import environ as os_environ


@patch("insights.client.connection.requests.Session")
@patch("insights.client.connection.InsightsConnection.__init__", return_value=None)
def test_proxy_request(init, session):
    """
    If proxy authentication is enabled, the failing hacky request is issued with correct timeout set.
    """
    config = Mock()

    # The constructor is bypassed, because it itself runs the _init_session method.
    connection = InsightsConnection(None)
    connection.config = config
    connection.systemid = None
    connection.authmethod = "BASIC"
    connection.username = "some username"
    connection.password = "some password"
    connection.cert_verify = None
    connection.proxies = {"https": "some proxy"}
    connection.proxy_auth = True
    connection.base_url = 'https://cert-api.access.redhat.com/r/insights'

    connection._init_session()

    session.return_value.request.assert_called_once_with(
        "GET",
        "https://cert-api.access.redhat.com/r/insights",
        timeout=config.http_timeout
    )


def test_get_proxy_env():
    """
    Test geting proxy configuration through environment, with and without no_proxy setting.
    """
    config = Mock()
    config.no_proxy = None
    config.proxy = None
    config.base_url = "redhat.com"

    connection = InsightsConnection(config)

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies == {'https': 'env.proxy.example.com'}


def test_get_proxy_rhsm():
    """
    Test getting proxy configuration through rhsm (auto-config), with and without no_proxy setting.
    """
    config = Mock()
    config.no_proxy = None
    config.base_url = "redhat.com"
    config.proxy = "rhsm.proxy.example.com"

    connection = InsightsConnection(config)

    connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}


def test_get_no_proxy_env():
    """
    Test geting proxy configuration through environment with no_proxy modification.
    """

    config = Mock()
    config.no_proxy = None
    config.proxy = None
    config.base_url = "redhat.com"

    connection = InsightsConnection(config)

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com", "NO_PROXY": "*"}, clear=True):
        connection.get_proxies()
    assert connection.proxies is None

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com", "NO_PROXY": "redhat.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies is None

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com", "NO_PROXY": "url.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies == {'https': 'env.proxy.example.com'}


def test_get_no_proxy_rhsm():
    """
    Test geting proxy configuration through rhsm (auto-config) with no_proxy modification.
    """
    config = Mock()
    config.proxy = "rhsm.proxy.example.com"
    config.base_url = "redhat.com"
    config.no_proxy = ""

    connection = InsightsConnection(config)

    config.no_proxy = "*"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "redhat.com"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "url.com"
    connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}


@patch("insights.client.connection.logger.debug")
def test_get_rhsm_and_env(logger):
    """
    no_proxy from environment doesn't change the proxy configuration from auto-config
    """
    config = Mock()
    config.proxy = "rhsm.proxy.example.com"
    config.no_proxy = None
    config.base_url = "redhat.com"

    connection = InsightsConnection(config)

    with patch.dict(os_environ, {"NO_PROXY": "redhat.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}
    assert logger.called_with("You have environment variable NO_PROXY set as well as 'proxy' set in your configuration file. NO_PROXY environment variable will be ignored.")
