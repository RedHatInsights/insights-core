# -*- coding: utf-8 -*-

import pytest
try:
    from unittest.mock import patch, mock_open
    builtin_open = "builtins.open"
except Exception:
    from mock import patch, mock_open
    builtin_open = "__builtin__.open"

from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.core.exceptions import SkipComponent
from insights.parsers.mssql_conf import MsSQLConf
from insights.parsers.rsyslog_conf import RsyslogConf
from insights.specs import Specs
from insights.specs.datasources import httpd
from insights.specs.datasources.ssl_certificate import (
    httpd_ssl_certificate_files, nginx_ssl_certificate_files,
    mssql_tls_cert_file, httpd_certificate_info_in_nss,
    rsyslog_tls_cert_file, rsyslog_tls_ca_cert_file
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
  SSLCertificateFile      "/etc/pki/katello/certs/gént-katello-apache.crt"
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
  # SSLCertificateFile    "/etc/pki/katello/certs/old_katello-apache.crt"
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
  # bellow is SSLCertificateFile configuration
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
# NSSCertificateDatabase old_path
NSSCertificateDatabase /etc/httpd/aliasa
# bellow is the NSSNickname configuration
NSSNickname testcertaê
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

RSYSLOG_CLIENT_TLS_CA_CFG1 = """
global(
DefaultNetstreamDriverCAFile = "/usr/share/pki/ca-trust-source/anchors/ca.cer"
)
template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
"""

RSYSLOG_CLIENT_TLS_CA_CFG2 = """
authpriv.*                                              /var/log/secure
#action(type="omfwd"
#queue.maxdiskspace="1g"         # 1gb space limit (use as much as possible)
#queue.type="LinkedList"         # run asynchronously
# Remote Logging (we use TCP for reliable delivery)
#Target="remote_host" Port="XXX" Protocol="tcp")
global(DefaultNetstreamDriverCAFile="/opt/services/dlc/keystore/public.cert.pem")
auth,authpriv.* action(type="omfwd" protocol="tcp" target="abc.def.com" port="6514"
    StreamDriver="gtls" StreamDriverMode="1" StreamDriverAuthMode="anon")
"""

RSYSLOG_CLIENT_TLS_CA_CFG3 = """
$DefaultNetstreamDriverCAFile /usr/share/pki/ca-trust-source/anchors/ca.cer

template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
include(file="/etc/rsyslog.d/*.conf" mode="optional")
"""

RSYSLOG_CLIENT_TLS_CA_BAD_CFG3 = """
global(
DefaultNetstreamDriverCAFile  "/usr/share/pki/ca-trust-source/anchors/ca.cer"
)
template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
"""

RSYSLOG_CLIENT_TLS_CA_BAD_CFG4 = """
global(
DefaultNetstreamDriverCAFile =
)
template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
"""

RSYSLOG_CLIENT_TLS_CA_BAD_CFG5 = """
global(
DefaultNetstreamDriverCAFile
)
template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
"""

RSYSLOG_CLIENT_TLS_CA_BAD_CFG6 = """
template(
type="string"
)
action(
type = "omfwd"
queue.type = "LinkedList"
)
"""


@patch("os.path.exists", return_value=True)
@patch(builtin_open, new_callable=mock_open, read_data=HTTPD_CONF)
def test_httpd_certificate(m_open, m_exist):
    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_SSL_CONF).return_value]
    broker = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/ssl.conf']
    }
    result = httpd_ssl_certificate_files(broker)
    assert result == ['/etc/pki/katello/certs/gént-katello-apache.crt']

    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_SSL_CONF_2).return_value]
    broker = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/ssl.conf']
    }
    result = httpd_ssl_certificate_files(broker)
    # "/etc/pki/katello/certs/katello-apache_e.crt" not in the result
    assert result == ['/etc/pki/katello/certs/katello-apache.crt', '/etc/pki/katello/certs/katello-apache_d.crt']


def test_nginx_certificate():
    conf1 = context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf')
    conf2 = context_wrap(NGINX_SSL_CONF, path='/etc/nginx/conf.d/ssl.conf')

    broker = {
        Specs.nginx_conf: [conf1, conf2]
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/c.cecdsa.crt', '/a/b/c.rsa.crt']

    conf1 = context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf')
    conf2 = context_wrap(NGINX_SSL_CONF_MULTIPLE_SERVERS, path='/etc/nginx/conf.d/ssl.conf')

    broker = {
        Specs.nginx_conf: [conf1, conf2]
    }
    result = nginx_ssl_certificate_files(broker)
    assert result == ['/a/b/www.example.com.cecdsa.crt', '/a/b/www.example.com.crt', '/a/b/www.example.org.crt']


@patch("os.path.exists", return_value=True)
@patch(builtin_open, new_callable=mock_open, read_data=HTTPD_CONF)
def test_httpd_ssl_cert_exception(m_open, m_exists):
    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_CONF_WITHOUT_SSL).return_value]
    broker1 = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/no_ssl.conf']
    }
    with pytest.raises(SkipComponent):
        httpd_ssl_certificate_files(broker1)

    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_SSL_CONF_NO_VALUE).return_value]
    broker2 = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/no_ssl.conf']
    }
    with pytest.raises(SkipComponent):
        httpd_ssl_certificate_files(broker2)


def test_nginx_ssl_cert_exception():
    conf1 = context_wrap(NGINX_CONF, path='/etc/nginx/nginx.conf')
    conf2 = context_wrap(NGINX_CONF_WITHOUT_SSL, path='/etc/nginx/conf.d/no_ssl.conf')
    broker1 = {
        Specs.nginx_conf: [conf1, conf2]
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


@patch("os.path.exists", return_value=True)
@patch(builtin_open, new_callable=mock_open, read_data=HTTPD_CONF)
def test_httpd_certificate_info_in_nss(m_open, m_exists):
    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_WITH_NSS).return_value]
    broker = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/nss.conf']
    }
    result = httpd_certificate_info_in_nss(broker)
    assert result == [('/etc/httpd/aliasa', 'testcertaê'), ('/etc/httpd/aliasb', 'testcertb')]


@patch("os.path.exists", return_value=True)
@patch(builtin_open, new_callable=mock_open, read_data=HTTPD_CONF)
def test_httpd_certificate_info_in_nss_exception(m_open, m_exists):
    m_open.side_effect = [m_open.return_value, mock_open(read_data=HTTPD_WITH_NSS_OFF).return_value]
    broker = {
        httpd.httpd_configuration_files: ['/etc/httpd/conf/httpd.conf', '/etc/httpd/conf.d/nss.conf']
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


def test_rsyslog_ca_certification():
    rsys_par = RsyslogConf(context_wrap(RSYSLOG_CLIENT_TLS_CA_CFG1, path='/etc/rsyslog.conf'))
    rsys_com = RsyslogAllConf([rsys_par])
    broker = {
        RsyslogAllConf: rsys_com
    }
    result = rsyslog_tls_ca_cert_file(broker)
    assert result == '/usr/share/pki/ca-trust-source/anchors/ca.cer'

    rsys_par = RsyslogConf(context_wrap(RSYSLOG_CLIENT_TLS_CA_CFG2, path='/etc/rsyslog.conf'))
    rsys_com = RsyslogAllConf([rsys_par])
    broker = {
        RsyslogAllConf: rsys_com
    }
    result = rsyslog_tls_ca_cert_file(broker)
    assert result == '/opt/services/dlc/keystore/public.cert.pem'

    rsys_par = RsyslogConf(context_wrap(RSYSLOG_CLIENT_TLS_CA_CFG3, path='/etc/rsyslog.conf'))
    rsys_par2 = RsyslogConf(context_wrap(RSYSLOG_CLIENT_TLS_CA_BAD_CFG6, path='/etc/rsyslog.d/a.conf'))
    rsys_com = RsyslogAllConf([rsys_par, rsys_par2])
    broker = {
        RsyslogAllConf: rsys_com
    }
    result = rsyslog_tls_ca_cert_file(broker)
    assert result == '/usr/share/pki/ca-trust-source/anchors/ca.cer'


def test_rsyslog_ca_certification_exception():
    bad_example_confs = [
        RSYSLOG_CLIENT_TLS_CA_BAD_CFG3,
        RSYSLOG_CLIENT_TLS_CA_BAD_CFG4,
        RSYSLOG_CLIENT_TLS_CA_BAD_CFG5,
        RSYSLOG_CLIENT_TLS_CA_BAD_CFG6
    ]
    for bad_conf in bad_example_confs:
        rsys_par = RsyslogConf(context_wrap(bad_conf, path='/etc/rsyslog.conf'))
        rsys_com = RsyslogAllConf([rsys_par])
        broker = {
            RsyslogAllConf: rsys_com
        }
        with pytest.raises(SkipComponent):
            rsyslog_tls_ca_cert_file(broker)
