from insights.parsers import httpd_V
from insights.parsers import SkipException
from insights.parsers.httpd_V import HttpdV
from insights.tests import context_wrap
import pytest
import doctest

HTTPD_V_22 = """
Server version: Apache/2.2.15 (Unix)
Server built:   Feb  4 2016 02:44:09
Server's Module Magic Number: 20051115:25
Server loaded:  APR 1.3.9, APR-Util 1.3.9
Compiled using: APR 1.3.9, APR-Util 1.3.9
Architecture:   64-bit
Server MPM:     Prefork
  threaded:     no
    forked:     yes (variable process count)
Server compiled with....
 -D APACHE_MPM_DIR="server/mpm/prefork"
 -D APR_HAS_SENDFILE
 -D APR_HAS_MMAP
 -D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
 -D APR_USE_SYSVSEM_SERIALIZE
 -D APR_USE_PTHREAD_SERIALIZE
 -D SINGLE_LISTEN_UNSERIALIZED_ACCEPT
 -D APR_HAS_OTHER_CHILD
 -D AP_HAVE_RELIABLE_PIPED_LOGS
 -D DYNAMIC_MODULE_LIMIT=128
 -D HTTPD_ROOT="/etc/httpd"
 -D SUEXEC_BIN="/usr/sbin/suexec"
 -D DEFAULT_PIDLOG="run/httpd.pid"
 -D DEFAULT_SCOREBOARD="logs/apache_runtime_status"
 -D DEFAULT_LOCKFILE="logs/accept.lock"
 -D DEFAULT_ERRORLOG="logs/error_log"
 -D AP_TYPES_CONFIG_FILE="conf/mime.types"
 -D SERVER_CONFIG_FILE="conf/httpd.conf"
""".strip()

HTTPD_V_24 = """
Server version: Apache/2.4.6 (Red Hat Enterprise Linux)
Server built:   Aug  3 2016 08:33:27
Server's Module Magic Number: 20120211:24
Server loaded:  APR 1.4.8, APR-UTIL 1.5.2
Compiled using: APR 1.4.8, APR-UTIL 1.5.2
Architecture:   64-bit
Server MPM:     Worker
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


HTTPDV_DOC = """
Server version: Apache/2.2.6 (Red Hat Enterprise Linux)
Server's Module Magic Number: 20120211:24
Compiled using: APR 1.4.8, APR-UTIL 1.5.2
Architecture:   64-bit
Server MPM:     Prefork
Server compiled with....
-D APR_HAS_SENDFILE
-D APR_HAVE_IPV6 (IPv4-mapped addresses enabled)
-D AP_TYPES_CONFIG_FILE="conf/mime.types"
-D SERVER_CONFIG_FILE="conf/httpd.conf"
""".strip()


def test_httpd_V():
    result = HttpdV(context_wrap(HTTPD_V_22, path='/usr/sbin/httpd_-V'))
    assert result["Server MPM"] == "prefork"
    assert result["Server version"] == "apache/2.2.15 (unix)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True
    assert result['Server compiled with']['APR_HAVE_IPV6'] == "IPv4-mapped addresses enabled"
    assert result['Server compiled with']['DEFAULT_PIDLOG'] == "run/httpd.pid"
    assert result.httpd_command == "/usr/sbin/httpd"
    assert result.mpm == "prefork"
    assert result.version == "apache/2.2.15 (unix)"

    result = HttpdV(context_wrap(HTTPD_V_24, path='/usr/sbin/httpd.worker_-V'))
    assert result["Server MPM"] == "worker"
    assert result["Server version"] == "apache/2.4.6 (red hat enterprise linux)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True
    assert result['Server compiled with']['APR_HAVE_IPV6'] == "IPv4-mapped addresses enabled"
    assert result['Server compiled with']['DEFAULT_PIDLOG'] == "/run/httpd/httpd.pid"
    assert result.httpd_command == "/usr/sbin/httpd.worker"
    assert result.mpm == "worker"
    assert result.version == "apache/2.4.6 (red hat enterprise linux)"


def test_httpd_V_exp():
    with pytest.raises(SkipException) as sc:
        HttpdV(context_wrap(""))
    assert "Input content is empty" in str(sc)

    with pytest.raises(SkipException) as sc:
        HttpdV(context_wrap("TEST"))
    assert "Input content is not empty but there is no useful parsed data." in str(sc)


def test_httpd_V_doc():
    env = {
            'hv': HttpdV(context_wrap(HTTPDV_DOC))
          }
    failed, total = doctest.testmod(httpd_V, globs=env)
    assert failed == 0
