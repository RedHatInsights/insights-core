from insights.configtree import first, last  # noqa: F401
from insights.combiners.httpd_conf import _HttpdConf, HttpdConfTree
from insights.tests import context_wrap


HTTPD_CONF_MIXED = '''
JustFotTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfMoDuLe>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_1 = '''
JustFotTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_2 = '''
JustForTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      1024
JustForTest      "ABC"
MaxClients       1024
</IfModule>
'''.strip()

HTTPD_CONF_3 = '''
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
MaxClients       512
</IfModule>
'''.strip()

HTTPD_CONF_SHADOWTEST_1 = '''
Foo 1A
Foo 1B
Foo 1C
<IfModule prefork.c>
Foo 1xA
Foo 1xB
Foo 1xC
Bar 1A
Bar 1B
Bar 1C
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_SHADOWTEST_2 = '''
Foo 2A
Foo 2B
Foo 2C
<IfModule ASDF.prefork.c.ASDF>
Foo 2xA
Foo 2xB
Foo 2xC
Bar 2A
Bar 2B
Bar 2C
</IfModule>
'''.strip()

HTTPD_CONF_SHADOWTEST_3 = '''
Foo 3A
Foo 3B
Foo 3C
<IfModule prefork.c>
Foo 3xA
Foo 3xB
Foo 3xC
Bar 3A
Bar 3B
Bar 3C
</IfModule>
'''.strip()

HTTPD_CONF_WITH_NONSTANDARD_INCLUDE_PATH = '''
JustFotTest_NoSec "/var/www/cgi"
Include blaaaa.blaaa.blabla.d/*.conf
Include conf.modules.d/*.conf
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_MAIN_1 = '''
ServerRoot "/etc/httpd"
Listen 80

# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_MAIN_2 = '''
# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf

ServerRoot "/etc/httpd"
Listen 80
'''.strip()

HTTPD_CONF_MAIN_3 = '''
ServerRoot "/etc/httpd"

# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf

Listen 80
'''.strip()

HTTPD_CONF_FILE_1 = '''
ServerRoot "/home/skontar/httpd"
Listen 8080
'''.strip()

HTTPD_CONF_FILE_2 = '''
ServerRoot "/home/skontar/www"
'''.strip()

HTTPD_CONF_MORE = '''
UserDir disable
UserDir enable bob
'''.strip()

HTTPD_CONF_NEST_1 = """
<VirtualHost 128.39.140.28>
    <Directory /var/www/example>
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <IfModule mod_php4.c>
        php_admin_flag safe_mode Off
        php_admin_value register_globals    0
    </IfModule>
    DirectoryIndex index.php
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteRule .* /index.php
    </IfModule>
    <IfModule mod_rewrite.c>
        RewriteEngine Off
    </IfModule>
    <IfModule !php5_module>
        <IfModule !php4_module>
            <FilesMatch ".php[45]?$">
                Order allow,deny
                Deny from all
            </FilesMatch>
            <FilesMatch ".php[45]?$">
                Order deny,allow
            </FilesMatch>
        </IfModule>
    </IfModule>
    DocumentRoot /var/www/example
    ServerName www.example.com
    ServerAlias admin.example.com
</VirtualHost>
<IfModule !php5_module>
  <IfModule !php4_module>
    <Location />
        <FilesMatch ".php[45]">
            Order allow,deny
            Deny from all
        </FilesMatch>
    </Location>
  </IfModule>
</IfModule>
<IfModule mod_rewrite.c>
    RewriteEngine Off
</IfModule>
LogLevel warn
DocumentRoot "/var/www/html_cgi"
IncludeOptional conf.d/*.conf
EnableSendfile on
""".strip()

HTTPD_CONF_NEST_2 = """
DocumentRoot "/var/www/html"
<VirtualHost 128.39.140.30>
    <IfModule !php5_module>
        <IfModule !php4_module>
            <FilesMatch ".php[45]?$">
                Order allow,deny
                Deny from all
            </FilesMatch>
            <FilesMatch ".php[45]?$">
                Order deny,allow
            </FilesMatch>
        </IfModule>
    </IfModule>
    DocumentRoot /var/www/example1
    ServerName www.example1.com
    ServerAlias admin.example1.com
</VirtualHost>
<IfModule !php5_module>
  <IfModule !php4_module>
    <Location />
        <FilesMatch test>
            Order deny,allow
            Allow from all
        </FilesMatch>
        <FilesMatch ".php[45]">
            Order deny,allow
        </FilesMatch>
    </Location>
  </IfModule>
</IfModule>
<IfModule mod_rewrite.c>
    RewriteEngine On
</IfModule>
EnableSendfile off
""".strip()

HTTPD_CONF_NEST_3 = """
<VirtualHost 128.39.140.28>
    <IfModule !php5_module>
        Testphp php5_v3_1
        <IfModule !php4_module>
            Testphp php4_v3_1
        </IfModule>
        Testphp php5_v3_2
    </IfModule>
</VirtualHost>
<IfModule !php5_module>
  Testphp php5_3_a
  <IfModule !php4_module>
    Testphp php4_3_a
  </IfModule>
</IfModule>
""".strip()

HTTPD_CONF_NEST_4 = """
<VirtualHost 128.39.140.30>
    <IfModule !php5_module>
        Testphp php5_v4_1
        <IfModule !php4_module>
            Testphp php4_v4_1
        </IfModule>
        Testphp php5_v4_2
    </IfModule>
</VirtualHost>
<IfModule !php5_module>
  Testphp php5_4_b
  <IfModule !php4_module>
    Testphp php4_4_b
  </IfModule>
</IfModule>
""".strip()


# TODO
# These are real-world config files - you can delete them after reviewing the MR, I provide them in case the minimum crashing example seems inscrutable to you.
# There are at least 983 customer machines with such a config file.

BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_HTTPD_CONF = "/etc/httpd/conf/httpd.conf"
BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT = r"""
ServerTokens OS
ServerRoot "/etc/httpd"
PidFile run/httpd.pid
Timeout 60
KeepAlive Off
MaxKeepAliveRequests 100
KeepAliveTimeout 15
<IfModule prefork.c>
StartServers       8
MinSpareServers    5
MaxSpareServers   20
ServerLimit      256
MaxClients       256
MaxRequestsPerChild  4000
</IfModule>
<IfModule worker.c>
StartServers         4
MaxClients         300
MinSpareThreads     25
MaxSpareThreads     75
ThreadsPerChild     25
MaxRequestsPerChild  0
</IfModule>
Listen 80
LoadModule auth_basic_module modules/mod_auth_basic.so
LoadModule auth_digest_module modules/mod_auth_digest.so
LoadModule authn_file_module modules/mod_authn_file.so
LoadModule authn_alias_module modules/mod_authn_alias.so
LoadModule authn_anon_module modules/mod_authn_anon.so
LoadModule authn_dbm_module modules/mod_authn_dbm.so
LoadModule authn_default_module modules/mod_authn_default.so
LoadModule authz_host_module modules/mod_authz_host.so
LoadModule authz_user_module modules/mod_authz_user.so
LoadModule authz_owner_module modules/mod_authz_owner.so
LoadModule authz_groupfile_module modules/mod_authz_groupfile.so
LoadModule authz_dbm_module modules/mod_authz_dbm.so
LoadModule authz_default_module modules/mod_authz_default.so
LoadModule ldap_module modules/mod_ldap.so
LoadModule authnz_ldap_module modules/mod_authnz_ldap.so
LoadModule include_module modules/mod_include.so
LoadModule log_config_module modules/mod_log_config.so
LoadModule logio_module modules/mod_logio.so
LoadModule env_module modules/mod_env.so
LoadModule ext_filter_module modules/mod_ext_filter.so
LoadModule mime_magic_module modules/mod_mime_magic.so
LoadModule expires_module modules/mod_expires.so
LoadModule deflate_module modules/mod_deflate.so
LoadModule headers_module modules/mod_headers.so
LoadModule usertrack_module modules/mod_usertrack.so
LoadModule setenvif_module modules/mod_setenvif.so
LoadModule mime_module modules/mod_mime.so
LoadModule dav_module modules/mod_dav.so
LoadModule status_module modules/mod_status.so
LoadModule autoindex_module modules/mod_autoindex.so
LoadModule info_module modules/mod_info.so
LoadModule dav_fs_module modules/mod_dav_fs.so
LoadModule vhost_alias_module modules/mod_vhost_alias.so
LoadModule negotiation_module modules/mod_negotiation.so
LoadModule dir_module modules/mod_dir.so
LoadModule actions_module modules/mod_actions.so
LoadModule speling_module modules/mod_speling.so
LoadModule userdir_module modules/mod_userdir.so
LoadModule alias_module modules/mod_alias.so
LoadModule substitute_module modules/mod_substitute.so
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
LoadModule proxy_ftp_module modules/mod_proxy_ftp.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_ajp_module modules/mod_proxy_ajp.so
LoadModule proxy_connect_module modules/mod_proxy_connect.so
LoadModule cache_module modules/mod_cache.so
LoadModule suexec_module modules/mod_suexec.so
LoadModule disk_cache_module modules/mod_disk_cache.so
LoadModule cgi_module modules/mod_cgi.so
LoadModule version_module modules/mod_version.so
Include conf.d/*.conf
User apache
Group apache
ServerAdmin root@localhost
UseCanonicalName Off
DocumentRoot "/var/www/html"
<Directory />
Options FollowSymLinks
AllowOverride None
</Directory>
<Directory "/var/www/html">
Options Indexes FollowSymLinks
AllowOverride None
Order allow,deny
Allow from all
</Directory>
<IfModule mod_userdir.c>
UserDir disabled
</IfModule>
DirectoryIndex index.html index.html.var
AccessFileName .htaccess
<Files ~ "^.ht">
Order allow,deny
Deny from all
Satisfy All
</Files>
TypesConfig /etc/mime.types
DefaultType text/plain
<IfModule mod_mime_magic.c>
MIMEMagicFile conf/magic
</IfModule>
HostnameLookups Off
ErrorLog logs/error_log
LogLevel warn
LogFormat "%h %l %u %t "%r" %>s %b "%{Referer}i" "%{User-Agent}i"" combined
LogFormat "%h %l %u %t "%r" %>s %b" common
LogFormat "%{Referer}i -> %U" referer
LogFormat "%{User-agent}i" agent
CustomLog logs/access_log combined
ServerSignature On
Alias /icons/ "/var/www/icons/"
<Directory "/var/www/icons">
Options Indexes MultiViews FollowSymLinks
AllowOverride None
Order allow,deny
Allow from all
</Directory>
<IfModule mod_dav_fs.c>
DAVLockDB /var/lib/dav/lockdb
</IfModule>
ScriptAlias /cgi-bin/ "/var/www/cgi-bin/"
<Directory "/var/www/cgi-bin">
AllowOverride None
Options None
Order allow,deny
Allow from all
</Directory>
IndexOptions FancyIndexing VersionSort NameWidth=* HTMLTable Charset=UTF-8
AddIconByEncoding (CMP,/icons/compressed.gif) x-compress x-gzip
AddIconByType (TXT,/icons/text.gif) text/*
AddIconByType (IMG,/icons/image2.gif) image/*
AddIconByType (SND,/icons/sound2.gif) audio/*
AddIconByType (VID,/icons/movie.gif) video/*
AddIcon /icons/binary.gif .bin .exe
AddIcon /icons/binhex.gif .hqx
AddIcon /icons/tar.gif .tar
AddIcon /icons/world2.gif .wrl .wrl.gz .vrml .vrm .iv
AddIcon /icons/compressed.gif .Z .z .tgz .gz .zip
AddIcon /icons/a.gif .ps .ai .eps
AddIcon /icons/layout.gif .html .shtml .htm .pdf
AddIcon /icons/text.gif .txt
AddIcon /icons/c.gif .c
AddIcon /icons/p.gif .pl .py
AddIcon /icons/f.gif .for
AddIcon /icons/dvi.gif .dvi
AddIcon /icons/uuencoded.gif .uu
AddIcon /icons/script.gif .conf .sh .shar .csh .ksh .tcl
AddIcon /icons/tex.gif .tex
AddIcon /icons/bomb.gif /core
AddIcon /icons/back.gif ..
AddIcon /icons/hand.right.gif README
AddIcon /icons/folder.gif ^^DIRECTORY^^
AddIcon /icons/blank.gif ^^BLANKICON^^
DefaultIcon /icons/unknown.gif
ReadmeName README.html
HeaderName HEADER.html
IndexIgnore .??* *~ *
AddLanguage ca .ca
AddLanguage cs .cz .cs
AddLanguage da .dk
AddLanguage de .de
AddLanguage el .el
AddLanguage en .en
AddLanguage eo .eo
AddLanguage es .es
AddLanguage et .et
AddLanguage fr .fr
AddLanguage he .he
AddLanguage hr .hr
AddLanguage it .it
AddLanguage ja .ja
AddLanguage ko .ko
AddLanguage ltz .ltz
AddLanguage nl .nl
AddLanguage nn .nn
AddLanguage no .no
AddLanguage pl .po
AddLanguage pt .pt
AddLanguage pt-BR .pt-br
AddLanguage ru .ru
AddLanguage sv .sv
AddLanguage zh-CN .zh-cn
AddLanguage zh-TW .zh-tw
LanguagePriority en ca cs da de el eo es et fr he hr it ja ko ltz nl nn no pl pt pt-BR ru sv zh-CN zh-TW
ForceLanguagePriority Prefer Fallback
AddDefaultCharset UTF-8
AddType application/x-compress .Z
AddType application/x-gzip .gz .tgz
AddType application/x-x509-ca-cert .crt
AddType application/x-pkcs7-crl    .crl
AddHandler type-map var
AddType text/html .shtml
AddOutputFilter INCLUDES .shtml
Alias /error/ "/var/www/error/"
<IfModule mod_negotiation.c>
<IfModule mod_include.c>
<Directory "/var/www/error">
AllowOverride None
Options IncludesNoExec
AddOutputFilter Includes html
AddHandler type-map var
Order allow,deny
Allow from all
LanguagePriority en es de fr
ForceLanguagePriority Prefer Fallback
</Directory>
</IfModule>
</IfModule>
BrowserMatch "Mozilla/2" nokeepalive
BrowserMatch "MSIE 4.0b2;" nokeepalive downgrade-1.0 force-response-1.0
BrowserMatch "RealPlayer 4.0" force-response-1.0
BrowserMatch "Java/1.0" force-response-1.0
BrowserMatch "JDK/1.0" force-response-1.0
BrowserMatch "Microsoft Data Access Internet Publishing Provider" redirect-carefully
BrowserMatch "MS FrontPage" redirect-carefully
BrowserMatch "^WebDrive" redirect-carefully
BrowserMatch "^WebDAVFS/1.[0123]" redirect-carefully
BrowserMatch "^gnome-vfs/1.0" redirect-carefully
BrowserMatch "^XML Spy" redirect-carefully
BrowserMatch "^Dreamweaver-WebDAV-SCM1" redirect-carefully
""".strip()

BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_SSL_CONF = "/etc/httpd/conf.d/ssl.conf"
BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_SSL_CONF_CONTENT = r"""
LoadModule ssl_module modules/mod_ssl.so
Listen 443
SSLPassPhraseDialog  builtin
SSLSessionCache         shmcb:/var/cache/mod_ssl/scache(512000)
SSLSessionCacheTimeout  300
SSLMutex default
SSLRandomSeed startup file:/dev/urandom  256
SSLRandomSeed connect builtin
SSLCryptoDevice builtin
<VirtualHost _default_:443>
ErrorLog logs/ssl_error_log
TransferLog logs/ssl_access_log
LogLevel warn
SSLEngine on
SSLProtocol all -SSLv2
SSLCipherSuite DEFAULT:!EXP:!SSLv2:!DES:!IDEA:!SEED:+3DES
SSLCertificateFile /etc/pki/tls/certs/localhost.crt
SSLCertificateKeyFile /etc/pki/tls/private/localhost.key
<Files ~ ".(cgi|shtml|phtml|php3?)$">
SSLOptions +StdEnvVars
</Files>
<Directory "/var/www/cgi-bin">
SSLOptions +StdEnvVars
</Directory>
SetEnvIf User-Agent ".*MSIE.*" 
nokeepalive ssl-unclean-shutdown 
downgrade-1.0 force-response-1.0
CustomLog logs/ssl_request_log 
"%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b"
</VirtualHost>
""".strip()

BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_WELCOME_CONF = "/etc/httpd/conf.d/welcome.conf"
BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_WELCOME_CONF_CONTENT = r"""
<LocationMatch "^/+$">
Options -Indexes
ErrorDocument 403 /error/noindex.html
</LocationMatch>
""".strip()

# And their minimized variant

BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_HTTPD_CONF = "/etc/httpd/conf/httpd.conf"
BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT = r"""
<IfModule prefork.c>
</IfModule>
<IfModule worker.c>
</IfModule>
LoadModule include_module modules/mod_include.so
Include conf.d/*.conf
<Directory />
</Directory>
<Directory "/var/www/html">
</Directory>
<IfModule mod_userdir.c>
</IfModule>
<Files ~ "^.ht">
</Files>
<IfModule mod_mime_magic.c>
</IfModule>
<Directory "/var/www/icons">
</Directory>
<IfModule mod_dav_fs.c>
</IfModule>
<Directory "/var/www/cgi-bin">
</Directory>
AddOutputFilter INCLUDES .shtml
<IfModule mod_negotiation.c>
<IfModule mod_include.c>
<Directory "/var/www/error">
Options IncludesNoExec
AddOutputFilter Includes html
</Directory>
</IfModule>
</IfModule>
""".strip()

# this line makes it crash - "%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b"
BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_SSL_CONF = "/etc/httpd/conf.d/ssl.conf"
BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_SSL_CONF_CONTENT = r"""
<VirtualHost _default_:443>
SSLProtocol all -SSLv2
<Files ~ ".(cgi|shtml|phtml|php3?)$">
</Files>
<Directory "/var/www/cgi-bin">
</Directory>
CustomLog logs/ssl_request_log 
"%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b"
</VirtualHost>
""".strip()

BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_WELCOME_CONF = "/etc/httpd/conf.d/welcome.conf"
BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_WELCOME_CONF_CONTENT = r"""
<LocationMatch "^/+$">
</LocationMatch>
""".strip()


# TODO
# Just a crashing line without any context - ' and " characters make it crash
# This test doesn't really make sense, but I think it should not crash at least
BZ1591241C7_CRASHING_ULTRAMINIMAL_ETC_HTTPD_CONF_HTTPD_CONF = "/etc/httpd/conf/httpd.conf"
BZ1591241C7_CRASHING_ULTRAMINIMAL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT = r"""
<VirtualHost>
' ' ' '
SSLProtocol all -SSLv2
</VirtualHost>
""".strip()


# NOTE: You can use this test to be merged into master with the fix, probably.
HTTPD_CONF_QUOTES = r"""
<VirtualHost>
CustomLog logs/blabla_request_log 
' ' ' '
CustomLog logs/ssl_request_log 
"%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b"
SSLProtocol all -SSLv2
</VirtualHost>
""".strip()


def test_bz1591241c7_crashing_full():
    httpd1 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT, path=BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_HTTPD_CONF))
    httpd2 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_SSL_CONF_CONTENT, path=BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_SSL_CONF))
    httpd3 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_WELCOME_CONF_CONTENT, path=BZ1591241C7_CRASHING_FULL_ETC_HTTPD_CONF_D_WELCOME_CONF))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert result['VirtualHost']['SSLProtocol'][first].value == 'all -SSLv2'


def test_bz1591241c7_crashing_minimal():
    httpd1 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT, path=BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_HTTPD_CONF))
    httpd2 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_SSL_CONF_CONTENT, path=BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_SSL_CONF))
    httpd3 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_WELCOME_CONF_CONTENT, path=BZ1591241C7_CRASHING_MINIMAL_ETC_HTTPD_CONF_D_WELCOME_CONF))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert result['VirtualHost']['SSLProtocol'][first].value == 'all -SSLv2'


def test_bz1591241c7_crashing_ultraminimal():
    httpd1 = _HttpdConf(context_wrap(BZ1591241C7_CRASHING_ULTRAMINIMAL_ETC_HTTPD_CONF_HTTPD_CONF_CONTENT, path=BZ1591241C7_CRASHING_ULTRAMINIMAL_ETC_HTTPD_CONF_HTTPD_CONF))
    result = HttpdConfTree([httpd1])
    assert result['VirtualHost']['SSLProtocol'][first].value == 'all -SSLv2'


def test_superfluous_quotes():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_QUOTES, path="/etc/httpd/conf/httpd.conf"))
    result = HttpdConfTree([httpd1])
    assert result['VirtualHost']['SSLProtocol'][first].value == 'all -SSLv2'


def test_mixed_case_tags():
    httpd = _HttpdConf(context_wrap(HTTPD_CONF_MIXED, path='/etc/httpd/conf/httpd.conf'))
    httpd.find("ServerLimit").value == 256

def test_nopath():
    # no path
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2))
    try:
        result = HttpdConfTree([httpd2])
        # assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024
        exception_happened = False
    except:
        exception_happened = True
    assert exception_happened

    # no httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    try:
        result = HttpdConfTree([httpd2])
        # assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024
        exception_happened = False
    except:
        exception_happened = True
    assert exception_happened

    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd2])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/laaalalalala/blablabla/httpd.conf'))
    result = HttpdConfTree([httpd2])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # no include in httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd2, httpd3])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # no include in httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/aaa.conf'))
    result = HttpdConfTree([httpd3, httpd2])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 1
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 1024
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # with an include
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 2
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # colliding filenames
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 3
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['ServerLimit'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 256   # httpd3
    assert len(result['IfModule', 'prefork.c']['MaxClients']) == 3
    assert result['IfModule', 'prefork.c']['MaxClients'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['MaxClients'][last].value == 512   # httpd3

    # testing other ways to access the same indices
    assert result['IfModule', 'prefork.c']['MaxClients'][0].value == 256   # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][2].value == 512   # httpd3
    assert result['IfModule', 'prefork.c']['MaxClients'][-1].value == 512  # httpd3


def test_nonstandard_include_path():

    # with an include
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_WITH_NONSTANDARD_INCLUDE_PATH, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 2
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # colliding filenames
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_WITH_NONSTANDARD_INCLUDE_PATH, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 3
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['ServerLimit'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 256   # httpd3
    assert len(result['IfModule', 'prefork.c']['MaxClients']) == 3
    assert result['IfModule', 'prefork.c']['MaxClients'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['MaxClients'][last].value == 512   # httpd3

    # testing other ways to access the same indices
    assert result['IfModule', 'prefork.c']['MaxClients'][0].value == 256   # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][2].value == 512   # httpd3
    assert result['IfModule', 'prefork.c']['MaxClients'][-1].value == 512  # httpd3

def test_active_httpd():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    assert result['IfModule', 'prefork.c']['MaxClients'][last].value == 512
    assert result['IfModule', 'prefork.c']['MaxClients'][last].file_path == '/etc/httpd/conf.d/z-z.conf'
    assert result['IfModule', 'prefork.c']['ThreadsPerChild'][last].value == 16
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 256
    assert result['IfModule', 'prefork.c']['JustForTest'][last].file_name == '00-z.conf'
    assert result['JustForTest_NoSec'][first].line == 'JustForTest_NoSec "/var/www/cgi"'


def test_shadowing():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    assert len(result["Foo"]) == 9
    assert len(result["IfModule"]) == 3
    assert len(result["IfModule"]["Foo"]) == 9
    assert len(result["IfModule"]["Bar"]) == 9
    assert len(result["IfModule", "prefork.c"]) == 2
    assert len(result["IfModule", "prefork.c"]["Foo"]) == 6
    assert len(result["IfModule", "prefork.c"]["Bar"]) == 6
    assert len(result["IfModule", "prefork.c"][0]["Foo"]) == 3
    assert len(result["IfModule", "prefork.c"][1]["Foo"]) == 3
    assert len(result["IfModule", "prefork.c"][0]["Bar"]) == 3
    assert len(result["IfModule", "prefork.c"][1]["Bar"]) == 3


def test_splits():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/home/skontar/www'
    assert server_root.line == 'ServerRoot "/home/skontar/www"'
    assert server_root.file_name == '01-b.conf'
    assert server_root.file_path == '/etc/httpd/conf.d/01-b.conf'

    listen = result["Listen"][last]
    assert listen.value == 8080
    assert listen.line == 'Listen 8080'
    assert listen.file_name == '00-a.conf'
    assert listen.file_path == '/etc/httpd/conf.d/00-a.conf'

    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_2, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/etc/httpd'
    assert server_root.line == 'ServerRoot "/etc/httpd"'
    assert server_root.file_name == 'httpd.conf'
    assert server_root.file_path == '/etc/httpd/conf/httpd.conf'

    listen = result["Listen"][last]
    assert listen.value == 80
    assert listen.line == 'Listen 80'
    assert listen.file_name == 'httpd.conf'
    assert listen.file_path == '/etc/httpd/conf/httpd.conf'

    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_3, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/home/skontar/www'
    assert server_root.line == 'ServerRoot "/home/skontar/www"'
    assert server_root.file_name == '01-b.conf'
    assert server_root.file_path == '/etc/httpd/conf.d/01-b.conf'
    assert listen.value == 80
    assert listen.line == 'Listen 80'
    assert listen.file_name == 'httpd.conf'
    assert listen.file_path == '/etc/httpd/conf/httpd.conf'


def test_httpd_one_file_overwrites():
    httpd = _HttpdConf(context_wrap(HTTPD_CONF_MORE, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd])

    active_setting = result['UserDir'][last]
    assert active_setting.value == 'enable bob'
    assert active_setting.line == 'UserDir enable bob'
    assert active_setting.file_path == '/etc/httpd/conf/httpd.conf'
    assert active_setting.file_name == 'httpd.conf'

    setting_list = result['UserDir']
    assert len(setting_list) == 2
    assert setting_list[0].value == 'disable'
    assert setting_list[0].line == 'UserDir disable'
    assert setting_list[0].file_path == '/etc/httpd/conf/httpd.conf'
    assert setting_list[0].file_name == 'httpd.conf'
    assert setting_list[0].section is None
    assert setting_list[1].value == 'enable bob'
    assert setting_list[1].line == 'UserDir enable bob'
    assert setting_list[1].file_path == '/etc/httpd/conf/httpd.conf'
    assert setting_list[1].file_name == 'httpd.conf'
    assert setting_list[1].section_name is None
