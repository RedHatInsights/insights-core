import doctest

from insights.parsr.query import first, last
from insights.parsers import httpd_conf
from insights.tests import context_wrap

HTTPD_CONF_1 = """
ServerRoot "/etc/httpd"
<Directory />
    Options FollowSymLinks
    AllowOverride None
</Directory>

SSLProtocol -ALL +SSLv3
#SSLProtocol all -SSLv2

NSSProtocol SSLV3 TLSV1.0
#NSSProtocol ALL

# prefork MPM
 <IfModule prefork.c>
StartServers       8
MinSpareServers    5
MaxSpareServers   20
ServerLimit      256
MaxClients       256
MaxRequestsPerChild  200
 </IfModule>

# worker MPM
<IfModule worker.c>
StartServers         4
MaxClients         300
MinSpareThreads     25
MaxSpareThreads     75
ThreadsPerChild     25
MaxRequestsPerChild  0
</IfModule>
LoadModule auth_basic_module modules/mod_auth_basic.so
LoadModule auth_digest_module modules/mod_auth_digest.so
""".strip()

HTTPD_CONF_PATH = "/etc/httpd/conf/httpd.conf"
HTTPD_CONF_D_PATH = "/etc/httpd/conf.d/default.conf"

HTTPD_CONF_D_1 = """
SSLProtocol -ALL +SSLv3
#SSLProtocol all -SSLv2

#SSLCipherSuite ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW
SSLCipherSuite ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW

# MaxClients: maximum number of server processes allowed to start
   MaxClients
""".strip()

HTTPD_CONF_SPLIT = '''
LogLevel warn
IncludeOptional conf.d/*.conf
EnableSendfile on
'''.strip()

HTTPD_CONF_MORE = '''
UserDir disable
UserDir enable bob
'''.strip()

HTTPD_CONF_NEST_1 = """
<VirtualHost 192.0.2.1> 
    <Directory /var/www/example>
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <IfModule mod_php4.c>
        php_admin_flag safe_mode Off
        php_admin_value register_globals    0
        php_value magic_quotes_gpc  0
        php_value magic_quotes_runtime  0
        php_value allow_call_time_pass_reference 0
    </IfModule>
    DirectoryIndex index.php
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteRule .* /index.php
    </IfModule>
    <IfModule mod_rewrite.c>
        RewriteEngine Off
    </IfModule>
    DocumentRoot /var/www/example
    ServerName www.example.com
    ServerAlias admin.example.com
</VirtualHost>
""".strip()  # noqa W291

HTTPD_CONF_NO_NAME_SEC = """
<RequireAll>
    AuthName "NAME Access"
    Require valid-user
</RequireAll>
""".strip()

HTTPD_CONF_DOC = '''
ServerRoot "/etc/httpd"
LoadModule auth_basic_module modules/mod_auth_basic.so
LoadModule auth_digest_module modules/mod_auth_digest.so

<Directory />
    Options FollowSymLinks
    AllowOverride None
</Directory>

<IfModule mod_mime_magic.c>
#   MIMEMagicFile /usr/share/magic.mime
    MIMEMagicFile conf/magic
</IfModule>

ErrorLog "|/usr/sbin/httplog -z /var/log/httpd/error_log.%Y-%m-%d"

SSLProtocol -ALL +SSLv3
#SSLProtocol all -SSLv2

NSSProtocol SSLV3 TLSV1.0
#NSSProtocol ALL

# prefork MPM
 <IfModule prefork.c>
StartServers       8
MinSpareServers    5
MaxSpareServers   20
ServerLimit      256
MaxClients       256
MaxRequestsPerChild  200
 </IfModule>

# worker MPM
<IfModule worker.c>
StartServers         4
MaxClients         300
MinSpareThreads     25
MaxSpareThreads     75
ThreadsPerChild     25
MaxRequestsPerChild  0
</IfModule>
'''.strip()


def test_get_httpd_conf_nest_1():
    context = context_wrap(HTTPD_CONF_NEST_1, path=HTTPD_CONF_PATH)
    result = httpd_conf.HttpdConf(context)
    assert result["VirtualHost", "192.0.2.1"]["IfModule", "mod_php4.c"]['php_admin_flag'][last].value == "safe_mode Off"
    assert result["VirtualHost", "192.0.2.1"]["IfModule", "mod_rewrite.c"]['RewriteEngine'][last].value is False
    assert result["VirtualHost", "192.0.2.1"]["IfModule", "mod_rewrite.c"]['RewriteRule'][last].value == ".* /index.php"
    assert result["VirtualHost", "192.0.2.1"]['ServerName'][last].value == "www.example.com"


def test_get_httpd_conf_1():
    context = context_wrap(HTTPD_CONF_1, path=HTTPD_CONF_PATH)
    result = httpd_conf.HttpdConf(context)

    assert "SSLCipherSuite" not in result
    assert result['ServerRoot'][first].value == '/etc/httpd'
    assert result["NSSProtocol"][first].value == "SSLV3 TLSV1.0"
    assert result["IfModule", "prefork.c"]["MaxClients"][last].value == 256
    assert result["IfModule", "worker.c"]["MaxClients"][last].value == 300
    assert result.file_path == HTTPD_CONF_PATH
    assert 'ThreadsPerChild' not in result['IfModule', 'prefork.c']
    assert result['IfModule', 'prefork.c']['MaxRequestsPerChild'][last].value == 200
    assert result.file_name == "httpd.conf"
    assert result['LoadModule'][first].value == 'auth_basic_module modules/mod_auth_basic.so'
    assert result['LoadModule'][last].value == 'auth_digest_module modules/mod_auth_digest.so'
    assert result['Directory', '/']['Options'][last].value == 'FollowSymLinks'


def test_get_httpd_conf_2():
    context = context_wrap(HTTPD_CONF_D_1, path=HTTPD_CONF_D_PATH)
    result = httpd_conf.HttpdConf(context)

    except_SSLC = 'ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW'
    assert result["SSLCipherSuite"][last].value == except_SSLC
    assert "NSSProtocol" not in result
    assert result.file_path == HTTPD_CONF_D_PATH
    assert result.file_name == "default.conf"
    assert result["SSLProtocol"][last].value == '-ALL +SSLv3'
    assert result["SSLProtocol"][last].line == 'SSLProtocol -ALL +SSLv3'


def test_main_config_splitting():
    context = context_wrap(HTTPD_CONF_SPLIT, path=HTTPD_CONF_PATH)
    result = httpd_conf.HttpdConf(context)

    assert result.file_path == HTTPD_CONF_PATH
    assert result.file_name == "httpd.conf"
    assert result['LogLevel'][-1].value == 'warn'
    assert result['LogLevel'][-1].line == 'LogLevel warn'
    assert result['EnableSendfile'][-1].value is True


def test_multiple_values_for_directive():
    context = context_wrap(HTTPD_CONF_MORE, path=HTTPD_CONF_PATH)
    result = httpd_conf.HttpdConf(context)

    assert result.file_path == HTTPD_CONF_PATH
    assert result.file_name == "httpd.conf"
    assert len(result['UserDir']) == 2
    assert result['UserDir'][0].value == 'disable'
    assert result['UserDir'][1].value == 'enable bob'


def test_no_name_section():
    context = context_wrap(HTTPD_CONF_NO_NAME_SEC, path=HTTPD_CONF_PATH)
    result = httpd_conf.HttpdConf(context)

    assert result["RequireAll"]["AuthName"][last].value == "NAME Access"
    assert result["RequireAll"]["Require"][last].value == "valid-user"


def test_doc():
    env = {
            'httpd_conf.HttpdConf': httpd_conf.HttpdConf,
            'httpd_conf': httpd_conf.HttpdConf(context_wrap(HTTPD_CONF_DOC, path='/path')),
          }
    failed, total = doctest.testmod(httpd_conf, globs=env)
    assert failed == 0
