import pytest

from insights.core.dr import SkipComponent
from insights.tests import context_wrap
from insights.combiners.httpd_conf import _HttpdConf, HttpdConfTree
from insights.combiners.nginx_conf import _NginxConf, NginxConfTree
from insights.specs.datasources.ssl_certificate import (
    httpd_ssl_certificate_file, nginx_ssl_certificate_files
)


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

NGINX_CONF = """
http {
    listen 80;
    listen 443;
    include /etc/nginx/conf.d/*.conf;
}
""".strip()

NGINX_SSL_CONF = """
server {
  ssl_certificate      "/a/b/c.rsa.crt";
  ssl_certificate_key   "/a/b/c.rsa.key";

  ssl_certificate     "/a/b/c.cecdsa.crt";
  ssl_certificate_key "/a/b/c.cecdsa.key";
}
""".strip()

NGINX_SSL_CONF_MULTIPLE_SERVERS = """
server {
    listen          443 ssl;
    server_name     www.example.com;
    ssl_certificate      "/a/b/www.example.com.crt";
    ssl_certificate_key   "/a/b/www.example.com.key";
    ssl_certificate     "/a/b/www.example.com.cecdsa.crt";
    ssl_certificate_key "/a/b/www.example.com.cecdsa.key";
}

server {
    listen          443 ssl;
    server_name     www.example.org;
    ssl_certificate      "/a/b/www.example.org.crt";
    ssl_certificate_key   "/a/b/www.example.org.key";
}
""".strip()

NGINX_CONF_WITHOUT_SSL = """
server {
  server_name 'a.b.c.com';
}
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


def test_nginx_certificate():
    conf1 = _NginxConf(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = _NginxConf(context_wrap(NGINX_SSL_CONF, path='/etc/nginx/conf.d/ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])

    broker = {
        NginxConfTree: conf_tree
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/c.rsa.crt', '/a/b/c.cecdsa.crt']

    conf1 = _NginxConf(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = _NginxConf(context_wrap(NGINX_SSL_CONF_MULTIPLE_SERVERS, path='/etc/nginx/conf.d/ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])

    broker = {
        NginxConfTree: conf_tree
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/www.example.com.crt', '/a/b/www.example.com.cecdsa.crt', '/a/b/www.example.org.crt']


def test_httpd_ssl_cert_exception():
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


def test_nginx_ssl_cert_exception():
    conf1 = _NginxConf(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = _NginxConf(context_wrap(NGINX_CONF_WITHOUT_SSL, path='/etc/nginx/conf.d/no_ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])
    broker1 = {
        NginxConfTree: conf_tree
    }
    with pytest.raises(SkipComponent):
        nginx_ssl_certificate_files(broker1)
