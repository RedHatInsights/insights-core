from insights.parsers.php_ini import PHPConf
from insights.parsers import SkipException, ParseException
from insights.tests import context_wrap
import pytest

# Latest production php.ini from php git repository. Comments stripped out.
# https://git.php.net/?p=php-src.git;a=blob;f=php.ini-production;hb=HEAD
INI_DEFAULT = """
[PHP]
engine = On
short_open_tag = Off
precision = 14
output_buffering = 4096
zlib.output_compression = Off
implicit_flush = Off
unserialize_callback_func =
serialize_precision = -1
disable_functions =
; This is a comment.
disable_classes =
zend.enable_gc = On
zend.exception_ignore_args = On
zend.exception_string_param_max_len = 0
expose_php = On
max_execution_time = 30
max_input_time = 60
memory_limit = 128M

error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT

display_errors = Off
display_startup_errors = Off
log_errors = On
log_errors_max_len = 1024
ignore_repeated_errors = Off
ignore_repeated_source = Off
report_memleaks = On
variables_order = "GPCS"
request_order = "GP"
register_argc_argv = Off
auto_globals_jit = On

post_max_size = 8M

auto_prepend_file =
auto_append_file =
default_mimetype = "text/html"
default_charset = "UTF-8"
doc_root =
user_dir =
enable_dl = Off
file_uploads = On
upload_max_filesize = 2M
max_file_uploads = 20
allow_url_fopen = On
allow_url_include = Off
default_socket_timeout = 60

[CLI Server]
cli_server.color = On

[Date]

[filter]

[iconv]

[imap]

[intl]

[sqlite3]

[Pcre]

[Pdo]

[Pdo_mysql]
pdo_mysql.default_socket=

[Phar]

[mail function]
SMTP = localhost
smtp_port = 25
mail.add_x_header = Off

[ODBC]
odbc.allow_persistent = On
odbc.check_persistent = On
odbc.max_persistent = -1
odbc.max_links = -1
odbc.defaultlrl = 4096
odbc.defaultbinmode = 1

[MySQLi]
mysqli.max_persistent = -1
mysqli.allow_persistent = On
mysqli.max_links = -1
mysqli.default_port = 3306
mysqli.default_socket =
mysqli.default_host =
mysqli.default_user =
mysqli.default_pw =
mysqli.reconnect = Off

[mysqlnd]
mysqlnd.collect_statistics = On
mysqlnd.collect_memory_statistics = Off

[OCI8]

[PostgreSQL]
pgsql.allow_persistent = On
pgsql.auto_reset_persistent = Off
pgsql.max_persistent = -1
pgsql.max_links = -1
pgsql.ignore_notice = 0
pgsql.log_notice = 0

[bcmath]
bcmath.scale = 0

[browscap]

[Session]
session.save_handler = files
session.use_strict_mode = 0
session.use_cookies = 1
session.use_only_cookies = 1
session.name = PHPSESSID
session.auto_start = 0
session.cookie_lifetime = 0
session.cookie_path = /
session.cookie_domain =
session.cookie_httponly =
session.cookie_samesite =
session.serialize_handler = php
session.gc_probability = 1
session.gc_divisor = 1000
session.gc_maxlifetime = 1440
session.referer_check =
session.cache_limiter = nocache
session.cache_expire = 180
session.use_trans_sid = 0
session.sid_length = 26
session.trans_sid_tags = "a=href,area=href,frame=src,form="
session.sid_bits_per_character = 5

[Assertion]
zend.assertions = -1

[COM]

[mbstring]

[gd]

[exif]

[Tidy]
tidy.clean_output = Off

[soap]
soap.wsdl_cache_enabled=1
soap.wsdl_cache_dir="/tmp"
soap.wsdl_cache_ttl=86400
soap.wsdl_cache_limit = 5

[sysvshm]

[ldap]
ldap.max_links = -1

[dba]

[opcache]

[curl]

[openssl]

[ffi]

""".strip()

INI_EMPTY = ""
INI_INVALID = "bla bla foo ha [] ^&*@#$%"


def test_php_conf_default():
    php_c = PHPConf(context_wrap(INI_DEFAULT))
    assert php_c['PHP']['default_mimetype'].value == 'text/html'
    assert php_c.data['PHP']['default_mimetype'] == 'text/html'
    assert php_c.data['Session']['session.cache_limiter'] == 'nocache'
    assert php_c['PHP']['engine'].value is True
    assert php_c['PHP']['precision'].value == 14
    assert php_c['PHP']['disable_classes'].value == ''
    assert php_c['PHP']['memory_limit'].value == 128 * 2**20  # Conversion of 128M to bytes.
    assert php_c['PHP']['post_max_size'].value == 8 * 2**20  # Conversion of 8M to bytes.


def test_php_conf_empty():
    with pytest.raises(SkipException):
        PHPConf(context_wrap(INI_EMPTY))


def test_php_conf_invalid():
    with pytest.raises(ParseException):
        PHPConf(context_wrap(INI_INVALID))
