import pytest

from insights.combiners.httpd_conf import HttpdConfTree
from insights.combiners.nginx_conf import NginxConfTree
from insights.core.exceptions import SkipComponent
from insights.parsers.httpd_conf import HttpdConf
from insights.parsers.mssql_conf import MsSQLConf
from insights.parsers.nginx_conf import NginxConfPEG
from insights.parsers.rsyslog_conf import RsyslogConf
from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.specs.datasources.ssl_certificate import (
    httpd_ssl_certificate_files, nginx_ssl_certificate_files,
    mssql_tls_cert_file, httpd_certificate_info_in_nss,
    rsyslog_tls_cert_file
)
from insights.tests import context_wrap


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

HTTPD_SSL_CONF_2 = """
<VirtualHost *:443>
  ## SSL directives
  ServerName a.b.c.com
  SSLEngine on
  SSLCertificateFile      "/etc/pki/katello/certs/katello-apache.crt"
  SSLCertificateKeyFile   "/etc/pki/katello/private/katello-apache.key"
  SSLCertificateChainFile "/etc/pki/katello/certs/katello-server-ca.crt"
  SSLVerifyClient         optional
  SSLCACertificateFile    "/etc/pki/katello/certs/katello-default-ca.crt"
  SSLVerifyDepth          3
  SSLOptions +StdEnvVars +ExportCertData
</VirtualHost>
<VirtualHost *:443>
  ## SSL directives
  ServerName  d.c.e.com
  SSLEngine on
  SSLCertificateFile      "/etc/pki/katello/certs/katello-apache_d.crt"
  SSLCertificateKeyFile   "/etc/pki/katello/private/katello-apache_d.key"
  SSLCertificateChainFile "/etc/pki/katello/certs/katello-server-ca_d.crt"
  SSLVerifyClient         optional
  SSLCACertificateFile    "/etc/pki/katello/certs/katello-default-ca_d.crt"
  SSLVerifyDepth          3
  SSLOptions +StdEnvVars +ExportCertData
</VirtualHost>
<VirtualHost *:443>
  ## SSL directives
  ServerName  f.g.e.com
  SSLEngine off
  SSLCertificateFile      "/etc/pki/katello/certs/katello-apache_e.crt"
  SSLCertificateKeyFile   "/etc/pki/katello/private/katello-apache_e.key"
  SSLCertificateChainFile "/etc/pki/katello/certs/katello-server-ca_e.crt"
  SSLVerifyClient         optional
  SSLCACertificateFile    "/etc/pki/katello/certs/katello-default-ca_e.crt"
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

MSSQL_WITH_TLS = """
[sqlagent]
enabled = true
[EULA]
accepteula = Y
[memory]
memorylimitmb = 2048
[network]
tlscert = /tmp/mssql.pem
""".strip()

MSSQL_WITHOUT_TLS = """
[sqlagent]
enabled = true
[EULA]
accepteula = Y
[memory]
memorylimitmb = 2048
""".strip()

HTTPD_NSS_CERT_ENDATE = """
Not After : Mon Jan 18 07:02:43 2038
""".strip()

HTTPD_WITH_NSS = """
Listen 8443
<VirtualHost _default_:8443>
ServerName www.examplea.com:8443
NSSEngine on
NSSCertificateDatabase /etc/httpd/aliasa
NSSNickname testcerta
</VirtualHost>
<VirtualHost :8443>
ServerName www.exampleb.com:8443
NSSEngine on
NSSCertificateDatabase /etc/httpd/aliasb
NSSNickname testcertb
</VirtualHost>
<VirtualHost :8443>
ServerName www.examplec.com:8443
NSSEngine off
NSSCertificateDatabase /etc/httpd/aliasc
NSSNickname testcertc
</VirtualHost>
""".strip()

HTTPD_WITH_NSS_OFF = """
Listen 8443
<VirtualHost _default_:8443>
NSSEngine off
NSSCertificateDatabase /etc/httpd/alias
NSSNickname testcert
</VirtualHost>
""".strip()

RSYSLOG_TLS_CFG1 = """
$ActionQueueFileName abc
$DefaultNetstreamDriver gtls
$DefaultNetstreamDriverCAFile /etc/pki/rsyslog/ca-cert.pem
$DefaultNetstreamDriverCertFile /etc/pki/rsyslog/sender-cert.pem
$DefaultNetstreamDriverKeyFile /etc/pki/rsyslog/sender-key.pem
$ActionSendStreamDriverAuthMode anon
"""

RSYSLOG_TLS_CFG2 = """
global(
workDirectory="/var/lib/rsyslog"
DefaultNetstreamDriverCAFile="/etc/rsyslog.d/certificates/crt/ca.crt"
DefaultNetstreamDriverCertFile="/etc/rsyslog.d/certificates/crt/cert.crt"
DefaultNetstreamDriverKeyFile="/etc/rsyslog.d/certificates/key/driver.key"
)
include(file="/etc/rsyslog.d/*.conf" mode="optional")
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
"""

RSYSLOG_CFG3 = """
global(
workDirectory="/var/lib/rsyslog"
)
include(file="/etc/rsyslog.d/*.conf" mode="optional")
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
"""


def test_httpd_certificate():
    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_SSL_CONF, path='/etc/httpd/conf.d/ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])

    broker = {
        HttpdConfTree: conf_tree
    }
    result = httpd_ssl_certificate_files(broker)
    assert result == ['/etc/pki/katello/certs/katello-apache.crt']

    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_SSL_CONF_2, path='/etc/httpd/conf.d/ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])

    broker = {
        HttpdConfTree: conf_tree
    }
    result = httpd_ssl_certificate_files(broker)
    # "/etc/pki/katello/certs/katello-apache_e.crt" not in the result
    assert result == ['/etc/pki/katello/certs/katello-apache.crt', '/etc/pki/katello/certs/katello-apache_d.crt']


def test_nginx_certificate():
    conf1 = NginxConfPEG(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = NginxConfPEG(context_wrap(NGINX_SSL_CONF, path='/etc/nginx/conf.d/ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])

    broker = {
        NginxConfTree: conf_tree
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/c.rsa.crt', '/a/b/c.cecdsa.crt']

    conf1 = NginxConfPEG(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = NginxConfPEG(context_wrap(NGINX_SSL_CONF_MULTIPLE_SERVERS, path='/etc/nginx/conf.d/ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])

    broker = {
        NginxConfTree: conf_tree
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/www.example.com.crt', '/a/b/www.example.com.cecdsa.crt', '/a/b/www.example.org.crt']


def test_httpd_ssl_cert_exception():
    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_CONF_WITHOUT_SSL, path='/etc/httpd/conf.d/no_ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker1 = {
        HttpdConfTree: conf_tree
    }
    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_SSL_CONF_NO_VALUE, path='/etc/httpd/conf.d/no_ssl.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker2 = {
        HttpdConfTree: conf_tree
    }
    with pytest.raises(SkipComponent):
        httpd_ssl_certificate_files(broker1)
        httpd_ssl_certificate_files(broker2)


def test_nginx_ssl_cert_exception():
    conf1 = NginxConfPEG(context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf'))
    conf2 = NginxConfPEG(context_wrap(NGINX_CONF_WITHOUT_SSL, path='/etc/nginx/conf.d/no_ssl.conf'))
    conf_tree = NginxConfTree([conf1, conf2])
    broker1 = {
        NginxConfTree: conf_tree
    }
    with pytest.raises(SkipComponent):
        nginx_ssl_certificate_files(broker1)


def test_mssql_tls_cert_exception():
    conf1 = MsSQLConf(context_wrap(MSSQL_WITH_TLS, path='/var/opt/mssql/mssql.conf'))
    broker1 = {
        MsSQLConf: conf1
    }
    result = mssql_tls_cert_file(broker1)
    assert result == "/tmp/mssql.pem"


def test_mssql_tls_no_cert_exception():
    conf1 = MsSQLConf(context_wrap(MSSQL_WITHOUT_TLS, path='/var/opt/mssql/mssql.conf'))
    broker1 = {
        MsSQLConf: conf1
    }
    with pytest.raises(SkipComponent):
        mssql_tls_cert_file(broker1)


def test_httpd_certificate_info_in_nss():
    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_WITH_NSS, path='/etc/httpd/conf.d/nss.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker = {
        HttpdConfTree: conf_tree
    }
    result = httpd_certificate_info_in_nss(broker)
    assert result == [('/etc/httpd/aliasa', 'testcerta'), ('/etc/httpd/aliasb', 'testcertb')]


def test_httpd_certificate_info_in_nss_exception():
    conf1 = HttpdConf(context_wrap(HTTPD_CONF, path='/etc/httpd/conf/httpd.conf'))
    conf2 = HttpdConf(context_wrap(HTTPD_WITH_NSS_OFF, path='/etc/httpd/conf.d/nss.conf'))
    conf_tree = HttpdConfTree([conf1, conf2])
    broker = {
        HttpdConfTree: conf_tree
    }
    with pytest.raises(SkipComponent):
        httpd_certificate_info_in_nss(broker)


def test_rsyslog_certification():
    rsys_par = RsyslogConf(context_wrap(RSYSLOG_TLS_CFG1, path='/etc/rsyslog.conf'))
    rsys_com = RsyslogAllConf([rsys_par])
    broker = {
        RsyslogAllConf: rsys_com
    }
    result = rsyslog_tls_cert_file(broker)
    assert result == '/etc/pki/rsyslog/sender-cert.pem'

    rsys_par = RsyslogConf(context_wrap(RSYSLOG_TLS_CFG2, path='/etc/rsyslog.conf'))
    rsys_com = RsyslogAllConf([rsys_par])
    broker = {
        RsyslogAllConf: rsys_com
    }
    result = rsyslog_tls_cert_file(broker)
    assert result == '/etc/rsyslog.d/certificates/crt/cert.crt'


def test_rsyslog_certification_exception():
    rsys_par = RsyslogConf(context_wrap(RSYSLOG_CFG3, path='/etc/rsyslog.conf'))
    rsys_com = RsyslogAllConf([rsys_par])
    broker = {
        RsyslogAllConf: rsys_com
    }
    with pytest.raises(SkipComponent):
        rsyslog_tls_cert_file(broker)
