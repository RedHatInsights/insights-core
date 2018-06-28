from insights.parsers.httpd_conf import HttpdConf, ParsedData
from insights.combiners.httpd_conf import HttpdConfAll
from insights.tests import context_wrap

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


def test_active_httpd_directory():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_NEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_NEST_2, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfAll([httpd1, httpd2])
    assert result.get_section_list("Directory") == [(('Directory', '/var/www/example'), 'httpd.conf', '/etc/httpd/conf/httpd.conf')]
    assert result.get_section_list("asdf") == []
    assert result.get_section_list(123456) == []


def test_active_httpd_nest_1():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_NEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_NEST_2, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfAll([httpd1, httpd2])
    assert result.get_setting_list('Order1', ('FilesMatch', 'php')) == []
    assert result.get_setting_list('Order', ('FilesMatch', 'pdf')) == []
    php_fm_order = result.get_setting_list('Order', section=('FilesMatch', 'php'))
    assert {
            ('FilesMatch', '".php[45]?$"'): [
                ('allow,deny', 'Order allow,deny', 'FilesMatch', '".php[45]?$"', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
                ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]?$"', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')]
           } in php_fm_order
    assert {
            ('FilesMatch', '".php[45]"'): [
                ('allow,deny', 'Order allow,deny', 'FilesMatch', '".php[45]"', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
                ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]"', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')],
           } in php_fm_order
    assert {
            ('FilesMatch', '".php[45]?$"'): [
                ('allow,deny', 'Order allow,deny', 'FilesMatch', '".php[45]?$"', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
                ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]?$"', 'httpd.conf', '/etc/httpd/conf/httpd.conf')]
           } in php_fm_order
    re_im = result.get_setting_list('RewriteEngine', 'IfModule')
    assert {
            ('IfModule', 'mod_rewrite.c'): [
                ('On', 'RewriteEngine On', 'IfModule', 'mod_rewrite.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
                ('Off', 'RewriteEngine Off', 'IfModule', 'mod_rewrite.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf')]
           } in re_im
    assert {
            ('IfModule', 'mod_rewrite.c'): [
                ('Off', 'RewriteEngine Off', 'IfModule', 'mod_rewrite.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
                ('On', 'RewriteEngine On', 'IfModule', 'mod_rewrite.c', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')]
           } in re_im
    assert sorted(result.get_setting_list('EnableSendfile')) == sorted([
            ('off', 'EnableSendfile off', None, None, '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ('on', 'EnableSendfile on', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf')])
    assert result.get_setting_list('LogLevel') == [
            ('warn', 'LogLevel warn', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf')]
    assert result.get_setting_list('LogLevel1') == []

    assert result.get_active_setting('Order1', ('FilesMatch', 'php')) == []
    assert result.get_active_setting('Order', ('FilesMatch', 'pdf')) == []
    assert len(result.get_active_setting('Order', ('FilesMatch', '.php[45]?$'))) == 2
    assert len(result.get_active_setting('Order', ('FilesMatch',))) == 4
    assert len(result.get_active_setting('Order', ('FilesMatch', '.php[45]'))) == 3
    assert sorted(result.get_active_setting('Order', section=('FilesMatch', 'php'))) == sorted([
            ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]?$"', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]"', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ('deny,allow', 'Order deny,allow', 'FilesMatch', '".php[45]?$"', 'httpd.conf', '/etc/httpd/conf/httpd.conf')])
    assert sorted(result.get_active_setting('RewriteEngine', section='IfModule')) == sorted([
            ('Off', 'RewriteEngine Off', 'IfModule', 'mod_rewrite.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ('On', 'RewriteEngine On', 'IfModule', 'mod_rewrite.c', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')])
    assert result.get_active_setting('EnableSendfile').line == 'EnableSendfile on'
    assert result.get_active_setting('Deny', ('FilesMatch', 'test')) == []
    assert result.get_active_setting('Allow', ('FilesMatch', 'test'))[0].value == 'from all'
    assert result.get_active_setting('Deny', section=('IfModule',)) == []
    assert result.get_active_setting('MaxClients', section=('IfModule', 'prefork')) == []
    assert result.get_active_setting('RewriteRule', section=('IfModule', 'mod_rewrite.c'))[0].line == "RewriteRule .* /index.php"
    assert result.get_active_setting("DocumentRoot").value == '/var/www/html'
    assert result.get_active_setting('RewriteRule', section=('IfModule', 'mod_rewrite.c', 'invalid_test')) == []
    assert result.get_active_setting('LogLevel') == ('warn', 'LogLevel warn', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf')
    assert result.get_active_setting('LogLevel1') is None


def test_active_httpd_nest_2():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_NEST_3, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_NEST_4, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfAll([httpd1, httpd2])
    testphp_im = result.get_setting_list('Testphp', 'IfModule')
    assert {('IfModule', '!php5_module'): [
            ('php5_v3_1', 'Testphp php5_v3_1', 'IfModule', '!php5_module', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ('php5_v3_2', 'Testphp php5_v3_2', 'IfModule', '!php5_module', 'httpd.conf', '/etc/httpd/conf/httpd.conf')
            ]} in testphp_im
    assert {('IfModule', '!php4_module'): [
            ('php4_v3_1', 'Testphp php4_v3_1', 'IfModule', '!php4_module', 'httpd.conf', '/etc/httpd/conf/httpd.conf')
            ]} in testphp_im
    assert {('IfModule', '!php5_module'): [
            ('php5_v4_1', 'Testphp php5_v4_1', 'IfModule', '!php5_module', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ('php5_v4_2', 'Testphp php5_v4_2', 'IfModule', '!php5_module', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')
            ]} in testphp_im
    assert {('IfModule', '!php4_module'): [
            ('php4_v4_1', 'Testphp php4_v4_1', 'IfModule', '!php4_module', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')
            ]} in testphp_im
    assert {('IfModule', '!php5_module'): [
            ('php5_3_a', 'Testphp php5_3_a', 'IfModule', '!php5_module', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ('php5_4_b', 'Testphp php5_4_b', 'IfModule', '!php5_module', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')
            ]} in testphp_im
    assert {('IfModule', '!php4_module'): [
            ('php4_3_a', 'Testphp php4_3_a', 'IfModule', '!php4_module', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ('php4_4_b', 'Testphp php4_4_b', 'IfModule', '!php4_module', '00-z.conf', '/etc/httpd/conf.d/00-z.conf')
            ]} in testphp_im


def test_active_httpd():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/z-z.conf'))

    result = HttpdConfAll([httpd1, httpd2, httpd3])
    assert result.get_active_setting('MaxClients', section=('IfModule', 'prefork.c'))[0].value == '512'
    assert result.get_active_setting('MaxClients', section=('IfModule', 'prefork.c'))[0].file_path == '/etc/httpd/conf.d/z-z.conf'
    assert result.get_active_setting('ThreadsPerChild', section=('IfModule',
        'prefork.c'))[0].value == '16'
    assert result.get_active_setting("MaxClients", ("IfModule", "prefork")) == [
            ParsedData(value='512', line='MaxClients       512',
                section='IfModule', section_name='prefork.c',
                file_name='z-z.conf', file_path='/etc/httpd/conf.d/z-z.conf')]
    assert result.get_active_setting('ServerLimit', section=('IfModule', 'prefork.c'))[0].value == '256'
    assert result.get_active_setting('JustForTest', section=('IfModule', 'prefork.c'))[-1].file_name == '00-z.conf'
    assert result.get_active_setting('JustForTest_NoSec').line == 'JustForTest_NoSec "/var/www/cgi"'


def test_shadowing():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_3, path='/etc/httpd/conf.d/z-z.conf'))

    result = HttpdConfAll([httpd1, httpd2, httpd3])

    # get_setting_list returns ALL matching data

    assert result.get_setting_list('Foo') == [
        ParsedData('1A', 'Foo 1A', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
        ParsedData('1B', 'Foo 1B', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
        ParsedData('1C', 'Foo 1C', None, None, 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
        ParsedData('2A', 'Foo 2A', None, None, '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
        ParsedData('2B', 'Foo 2B', None, None, '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
        ParsedData('2C', 'Foo 2C', None, None, '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
        ParsedData('3A', 'Foo 3A', None, None, 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
        ParsedData('3B', 'Foo 3B', None, None, 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
        ParsedData('3C', 'Foo 3C', None, None, 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
    ]
    assert result.get_setting_list('Bar', section=('IfModule', 'prefork.c')) == [
        {('IfModule', 'prefork.c'): [
            ParsedData('1A', 'Bar 1A', 'IfModule', 'prefork.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ParsedData('1B', 'Bar 1B', 'IfModule', 'prefork.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ParsedData('1C', 'Bar 1C', 'IfModule', 'prefork.c', 'httpd.conf', '/etc/httpd/conf/httpd.conf'),
            ParsedData('3A', 'Bar 3A', 'IfModule', 'prefork.c', 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
            ParsedData('3B', 'Bar 3B', 'IfModule', 'prefork.c', 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
            ParsedData('3C', 'Bar 3C', 'IfModule', 'prefork.c', 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
        ],
        },
        {('IfModule', 'ASDF.prefork.c.ASDF'): [
            ParsedData('2A', 'Bar 2A', 'IfModule', 'ASDF.prefork.c.ASDF', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ParsedData('2B', 'Bar 2B', 'IfModule', 'ASDF.prefork.c.ASDF', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
            ParsedData('2C', 'Bar 2C', 'IfModule', 'ASDF.prefork.c.ASDF', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
        ],
        },
    ]
    assert result.get_setting_list('Bar') == []

    # get_active_setting returns the last value

    assert result.get_active_setting('Foo') == ('3C', 'Foo 3C', None, None, 'z-z.conf', '/etc/httpd/conf.d/z-z.conf')
    assert result.get_active_setting('Bar', section=('IfModule', 'prefork.c')) == [
        ('3C', 'Bar 3C', 'IfModule', 'prefork.c', 'z-z.conf', '/etc/httpd/conf.d/z-z.conf'),
        ('2C', 'Bar 2C', 'IfModule', 'ASDF.prefork.c.ASDF', '00-z.conf', '/etc/httpd/conf.d/00-z.conf'),
    ]
    assert result.get_active_setting('Bar') is None


def test_httpd_splits():
    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_MAIN_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfAll([httpd1, httpd2, httpd3])
    assert result.get_active_setting('ServerRoot').value == '/home/skontar/www'
    assert result.get_active_setting('ServerRoot').line == 'ServerRoot "/home/skontar/www"'
    assert result.get_active_setting('ServerRoot').file_name == '01-b.conf'
    assert result.get_active_setting('ServerRoot').file_path == '/etc/httpd/conf.d/01-b.conf'
    assert result.get_active_setting('Listen').value == '8080'
    assert result.get_active_setting('Listen').line == 'Listen 8080'
    assert result.get_active_setting('Listen').file_name == '00-a.conf'
    assert result.get_active_setting('Listen').file_path == '/etc/httpd/conf.d/00-a.conf'

    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_MAIN_2, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))

    result = HttpdConfAll([httpd1, httpd2, httpd3])
    assert result.get_active_setting('ServerRoot').value == '/etc/httpd'
    assert result.get_active_setting('ServerRoot').line == 'ServerRoot "/etc/httpd"'
    assert result.get_active_setting('ServerRoot').file_name == 'httpd.conf'
    assert result.get_active_setting('ServerRoot').file_path == '/etc/httpd/conf/httpd.conf'
    assert result.get_active_setting('Listen').value == '80'
    assert result.get_active_setting('Listen').line == 'Listen 80'
    assert result.get_active_setting('Listen').file_name == 'httpd.conf'
    assert result.get_active_setting('Listen').file_path == '/etc/httpd/conf/httpd.conf'

    httpd1 = HttpdConf(context_wrap(HTTPD_CONF_MAIN_3, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))

    result = HttpdConfAll([httpd1, httpd2, httpd3])
    assert result.get_active_setting('ServerRoot').value == '/home/skontar/www'
    assert result.get_active_setting('ServerRoot').line == 'ServerRoot "/home/skontar/www"'
    assert result.get_active_setting('ServerRoot').file_name == '01-b.conf'
    assert result.get_active_setting('ServerRoot').file_path == '/etc/httpd/conf.d/01-b.conf'
    assert result.get_active_setting('Listen').value == '80'
    assert result.get_active_setting('Listen').line == 'Listen 80'
    assert result.get_active_setting('Listen').file_name == 'httpd.conf'
    assert result.get_active_setting('Listen').file_path == '/etc/httpd/conf/httpd.conf'

    # Test is data from inactive configs are also stored
    assert [a.file_name for a in result.config_data] == ['httpd.conf', '00-a.conf', '01-b.conf', 'httpd.conf']
    assert result.config_data[1].file_name == '00-a.conf'
    assert result.config_data[1].file_path == '/etc/httpd/conf.d/00-a.conf'
    assert result.config_data[1].full_data_dict['Listen'][0].value == '8080'
    assert result.config_data[1].full_data_dict['Listen'][0].line == 'Listen 8080'


def test_httpd_no_main_config():
    httpd2 = HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfAll([httpd2, httpd3])
    assert [a.file_name for a in result.config_data] == ['00-a.conf', '01-b.conf']


def test_httpd_one_file_overwrites():
    httpd = HttpdConf(context_wrap(HTTPD_CONF_MORE, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfAll([httpd])

    active_setting = result.get_active_setting('UserDir')
    assert active_setting.value == 'enable bob'
    assert active_setting.line == 'UserDir enable bob'
    assert active_setting.file_path == '/etc/httpd/conf/httpd.conf'
    assert active_setting.file_name == 'httpd.conf'

    setting_list = result.get_setting_list('UserDir')
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
