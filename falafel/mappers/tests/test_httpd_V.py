from falafel.mappers.httpd_V import HttpdV
from falafel.tests import context_wrap

HTTPD_V = """
Server version: Apache/2.4.6 (Red Hat Enterprise Linux)
Server built:   Aug  3 2016 08:33:27
Server's Module Magic Number: 20120211:24
Server loaded:  APR 1.4.8, APR-UTIL 1.5.2
Compiled using: APR 1.4.8, APR-UTIL 1.5.2
Architecture:   64-bit
Server MPM:     prefork
  threaded:     no
    forked:     yes (variable process count)
Server compiled with....
 -D APR_HAS_SENDFILE
 -D APR_HAS_MMAP
 -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
 -D APR_USE_SYSVSEM_SERIALIZE
 -D APR_USE_PTHREAD_SERIALIZE
 -D SINGLE_LISTEN_UNSERIALIZED_ACCEPT
 -D APR_HAS_OTHER_CHILD
 -D AP_HAVE_RELIABLE_PIPED_LOGS
 -D DYNAMIC_MODULE_LIMIT=256
 -D HTTPD_ROOT="/etc/httpd"
 -D SUEXEC_BIN="/usr/sbin/suexec"
 -D DEFAULT_PIDLOG="/run/httpd/httpd.pid"
 -D DEFAULT_SCOREBOARD="logs/apache_runtime_status"
 -D DEFAULT_ERRORLOG="logs/error_log"
 -D AP_TYPES_CONFIG_FILE="conf/mime.types"
 -D SERVER_CONFIG_FILE="conf/httpd.conf"
""".strip()


def test_httpd_V():
    context = context_wrap(HTTPD_V)
    result = HttpdV(context)

    assert result["Server MPM"] == "prefork"
    assert result["Server version"] == "Apache/2.4.6 (Red Hat Enterprise Linux)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True
    assert result['Server compiled with']['APR_HAVE_IPV6'] == "IPv4-mapped addresses enabled"
    assert result['Server compiled with']['DEFAULT_PIDLOG'] == "/run/httpd/httpd.pid"
