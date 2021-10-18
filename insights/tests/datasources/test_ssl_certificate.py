import pytest

from insights.core.dr import SkipComponent
from insights.tests import context_wrap
from insights.combiners.httpd_conf import _HttpdConf, HttpdConfTree
from insights.specs.datasources.ssl_certificate import httpd_ssl_certificate_file


HTTPD_CONF = """
listen 80
listen 443
IncludeOptional "/etc/httpd/conf.d/*.conf"
""".strip()

HTTPD_SSL_CONF = """
<VirtualHost *:443>
  ## SSL directives
  SSLEngine on
  SSLCertificateFile      "/etc/pki/katello/certs/katello-apache.crt"
  SSLCertificateKeyFile   "/etc/pki/katello/private/katello-apache.key"
  SSLCertificateChainFile "/etc/pki/katello/certs/katello-server-ca.crt"
  SSLVerifyClient         optional
  SSLCACertificateFile    "/etc/pki/katello/certs/katello-default-ca.crt"
  SSLVerifyDepth          3
  SSLOptions +StdEnvVars +ExportCertData
</VirtualHost>
""".strip()

HTTPD_CONF_WITHOUT_SSL = """
<VirtualHost *:80>
    ServerName a.b.c.com
</VirtualHost>
""".strip()

HTTPD_SSL_CONF_NO_VALUE = """
<VirtualHost *:443>
  ## SSL directives
  SSLEngine off
  SSLCertificateFile      ""
  SSLCertificateKeyFile   ""
  SSLCertificateChainFile ""
</VirtualHost>
""".strip()


def test_httpd_certificate():
    conf1 = _HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = _HttpdConf(context_wrap(HTTPD_SSL_CONF, path='/etc/httpd/conf.d/ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])

    broker = {
        HttpdConfTree: conf_tree
    }
    result = httpd_ssl_certificate_file(broker)
    assert result == '/etc/pki/katello/certs/katello-apache.crt'


def test_exception():
    conf1 = _HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = _HttpdConf(context_wrap(HTTPD_CONF_WITHOUT_SSL, path='/etc/httpd/conf.d/no_ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker1 = {
        HttpdConfTree: conf_tree
    }
    conf1 = _HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = _HttpdConf(context_wrap(HTTPD_SSL_CONF_NO_VALUE, path='/etc/httpd/conf.d/no_ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker2 = {
        HttpdConfTree: conf_tree
    }
    with pytest.raises(SkipComponent):
        httpd_ssl_certificate_file(broker1)
        httpd_ssl_certificate_file(broker2)
