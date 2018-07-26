from insights.configtree import startswith, istartswith
from insights.configtree import endswith, iendswith
from insights.configtree import contains, icontains
from insights.configtree import eq, ieq, le, ile, lt, ilt, ge, ige, gt, igt
from insights.configtree import first, last  # noqa: F401
from insights.combiners.httpd_conf import _HttpdConf, HttpdConfTree
from insights.combiners.httpd_conf import in_network, is_private
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


def test_startswith():
    data = ["abc", "abrd", "ed"]
    assert startswith("ab")(data)
    assert istartswith("AB")(data)
    assert startswith("ab")("abcde")
    assert not startswith("de")(data)


def test_endswith():
    data = ["abc", "abrd", "ed"]
    assert endswith("d")(data)
    assert iendswith("D")(data)
    assert endswith("d")("end")
    assert not endswith("re")(data)


def test_contains():
    data = ["abc", "abrd", "ed"]
    assert contains("b")(data)
    assert icontains("B")(data)
    assert contains("b")("abc")
    assert not contains("x")(data)


def test_equals():
    data = ["abc", "abrd", "ed"]
    assert eq("abc")(data)
    assert ieq("ABC")(data)
    assert eq("b")("b")
    assert eq(10)([1, 2, 10])
    assert eq(10.0)([1, 2, 10.0])
    assert eq(10)(10)
    assert eq(10.1)(10.1)


def test_less_than():
    data = ["abc", "abrd", "ed"]
    assert lt("abd")(data)
    assert ilt("ABD")(data)
    assert lt("b")("a")
    assert lt(10)([1, 2, 10])
    assert lt(10)(9)
    assert lt(10.2)([1, 2, 10.1])
    assert lt(10.2)(9.3)


def test_less_than_equals():
    data = ["abc", "abrd", "ed"]
    assert le("abd")(data)
    assert ile("ABD")(data)
    assert le("abc")(data)
    assert le("b")("b")
    assert le("b")("a")
    assert le(1)([1, 2, 10])
    assert le(10)(9.9)
    assert le(10.0)(10)
    assert le(10.1)([1, 2, 10.01])
    assert le(2.3)([1, 2.3, 10.1])
    assert le(10.2)(9.3)
    assert le(9.3)(9.3)


def test_greater_than():
    data = ["abc", "abrd", "ed"]
    assert gt("abb")(data)
    assert igt("ABB")(data)
    assert gt("b")("c")
    assert gt(10)([1, 2, 11])
    assert gt(10)(11)
    assert gt(10.4)([1, 2, 11.5])
    assert gt(10.9)(11.02)


def test_greater_than_equals():
    data = ["abc", "abrd", "ed"]
    assert ge("abb")(data)
    assert ige("ABB")(data)
    assert ge("abc")(data)
    assert ge("b")("c")
    assert ge("c")("c")
    assert ge(10)([1, 2, 11])
    assert ge(11)([1, 2, 11])
    assert ge(10)(11)
    assert ge(11)(11)
    assert ge(10.4)([1, 2, 11.5])
    assert ge(11.5)([1, 2, 11.5])
    assert ge(10.9)(11.02)
    assert ge(11.02)(11.02)


def test_simple_queries():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_1, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd1])
    assert result["EnableSendfile"][first].value
    assert len(result["VirtualHost"]) == 1
    assert len(result["VirtualHost"]["Directory"]) == 1
    assert len(result["VirtualHost"]["IfModule"]) == 4
    assert len(result["VirtualHost"]["IfModule"]["RewriteEngine"]) == 2
    assert len(result["VirtualHost"]["IfModule", "mod_rewrite.c"]) == 2


def test_complex_queries():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_3, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_4, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert len(result.select("VirtualHost")) == 3
    assert len(result.select(("VirtualHost", "128.39.140.28"))) == 2
    assert len(result.select(("VirtualHost", "128.39.140.30"))) == 1
    assert len(result.select(("VirtualHost", startswith("128.39.140")))) == 3
    assert len(result.select(("VirtualHost", ~startswith("128.39.140")))) == 0
    assert len(result.select(("VirtualHost", endswith("140.30")))) == 1
    assert len(result.select(("VirtualHost", ~endswith("140.30")))) == 2
    assert len(result.select((startswith("Virtual"), ~endswith("140.30")))) == 2
    assert len(result.select("FilesMatch", deep=True, roots=False)) == 3

    # find all IfModule !php5_module stanzas regardless of location
    assert len(result.select(("IfModule", "!php5_module"), deep=True, roots=False)) == 6

    # find all IfModule !php5_module stanzas immediately beneath a VirtualHost
    assert len(result.select("VirtualHost", ("IfModule", "!php5_module"), roots=False)) == 3

    # find all IfModule !php4_module stanzas anywhere beneath a top level VirtualHost
    res = result.select("VirtualHost").select(("IfModule", "!php4_module"), deep=True, roots=False)
    assert len(res) == 3

    assert len(result.select(("VirtualHost", ~is_private))) == 3

    res = result.select(("VirtualHost", in_network("128.39.0.0/16")))
    assert len(res) == 3

    res = result.select(("VirtualHost", ~is_private & in_network("128.39.0.0/16")))
    assert len(res) == 3


def test_directives_and_sections():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_3, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_NEST_4, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert len(result.directives) == 3
    assert len(result.sections) == 7
    assert len(result.find_all(startswith("Dir")).directives) == 1
    assert len(result.find_all(startswith("Dir")).sections) == 1
