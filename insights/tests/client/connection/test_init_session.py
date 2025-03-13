from insights.client.connection import InsightsConnection
from mock.mock import Mock, patch
from os import environ as os_environ


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

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com", "NO_PROXY": "redhat.com,example.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies is None

    with patch.dict(os_environ, {"HTTPS_PROXY": "env.proxy.example.com", "NO_PROXY": "url.com,example.com"}, clear=True):
        connection.get_proxies()
    assert connection.proxies == {'https': 'env.proxy.example.com'}

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

    config.no_proxy = "example.com,url.com"
    connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}

    config.no_proxy = "example.com, url.com"
    connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}

    config.no_proxy = "example.com , url.com"
    connection.get_proxies()
    assert connection.proxies == {"https": config.proxy}

    config.no_proxy = "redhat.com, example.com"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "example.com, redhat.com"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "redhat.com,example.com"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "example.com,redhat.com"
    connection.get_proxies()
    assert connection.proxies is None

    config.no_proxy = "example.com , redhat.com"
    connection.get_proxies()
    assert connection.proxies is None


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
