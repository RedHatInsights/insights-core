from insights.parsr.examples.httpd_conf import loads
from insights.parsr.query import ieq


DATA = r"""
<IfModule log_config_module>
    #
    # The following directives define some format nicknames for use with
    # a CustomLog directive (see below).
    #
    LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
    LogFormat "%h %l %u %t \"%r\" %>s %b" common
</IfModule>
    <IfModule logio_module>
      # You need to enable mod_logio.c to use %I and %O
      LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %I %O" combinedio
    </IfModule>

    #
    # The location and format of the access logfile (Common Logfile Format).
    # If you do not define any access logfiles within a <VirtualHost>
    # container, they will be logged here.  Contrariwise, if you *do*
    # define per-<VirtualHost> access logfiles, transactions will be
    # logged therein and *not* in this file.
    #
    #CustomLog "logs/access_log" common
    CustomLog logs/ssl_request_log \
    "%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b"

    #
    # If you prefer a logfile with access, agent, and referer information
    # (Combined Logfile Format) you can use the following directive.
    #
    CustomLog "logs/access_log" combined
"""

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
SSLProtocol -ALL +TLSv1.2  # SSLv3
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


def test_if_module():
    val = loads(DATA)
    assert len(val) == 4


def test_httpd_conf_nest_one():
    val = loads(HTTPD_CONF_NEST_1)
    assert len(val["IfModule"]) == 2
    assert len(val["IfModule", "mod_rewrite.c"]) == 1
    assert len(val["IfModule", "!php5_module"]) == 1
    assert val["IfModule", "mod_rewrite.c"][0].lineno == 43
    assert val["LogLevel"].value == "warn"
    assert val["LogLevel"][0].lineno == 46
    assert val[ieq("loglevel")].value == "warn"
    assert val["SSLProtocol"][0].attrs == ["-ALL", "+TLSv1.2", "#", "SSLv3"]
