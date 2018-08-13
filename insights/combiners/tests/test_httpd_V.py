from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.ps import PsAuxcww
from insights.parsers.httpd_V import HttpdV as HV
from insights.parsers.httpd_V import HttpdWorkerV as HWV
from insights.parsers.httpd_V import HttpdEventV as HEV
from insights.combiners.httpd_V import HttpdV
from insights.tests import context_wrap, RHEL6, RHEL7
from insights import SkipComponent
import pytest

HTTPDV1 = """
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

HTTPDV2 = """
Server version: Apache/2.4.6 (Red Hat Enterprise Linux)
Server built:   Aug  3 2016 08:33:27
Server's Module Magic Number: 20120211:24
Server loaded:  APR 1.4.8, APR-UTIL 1.5.2
Compiled using: APR 1.4.8, APR-UTIL 1.5.2
Architecture:   64-bit
Server MPM:     worker
  threaded:     no
    forked:     yes (variable process count)
Server compiled with....
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

HTTPDV3 = """
Server version: Apache/2.4.6 (Red Hat Enterprise Linux)
Server built:   Aug  3 2016 08:33:27
Server's Module Magic Number: 20120211:24
Server loaded:  APR 1.4.8, APR-UTIL 1.5.2
Compiled using: APR 1.4.8, APR-UTIL 1.5.2
Architecture:   64-bit
Server MPM:     event
  threaded:     no
    forked:     yes (variable process count)
Server compiled with....
 -D APR_HAS_MMAP
""".strip()

PS_WORKER = """
USER  PID %CPU %MEM    VSZ   RSS TTY STAT START   TIME COMMAND
root   41  0.0  0.0  21452  1536 ?   Ss   Mar09   0:01 httpd.worker
root   75  0.0  0.0      0     0 ?   S    Mar09   0:00 [kthreadd]
""".strip()

PS_EVENT = """
USER  PID %CPU %MEM    VSZ   RSS TTY STAT START   TIME COMMAND
root   41  0.0  0.0  21452  1536 ?   Ss   Mar09   0:01 httpd.event
root   75  0.0  0.0      0     0 ?   S    Mar09   0:00 [kthreadd]
""".strip()


def test_httpd_V_RHEL6():
    hv1 = HV(context_wrap(HTTPDV1))
    hv2 = HWV(context_wrap(HTTPDV2, path='httpd.worker_-V'))
    hv3 = HEV(context_wrap(HTTPDV3, path='httpd.event_-V'))
    ps = PsAuxcww(context_wrap(PS_WORKER))
    rh = RedhatRelease(context_wrap(RHEL6))
    result = HttpdV(rh, ps, hv1, hv3, hv2)
    assert result["Server MPM"] == "worker"
    assert result["Server version"] == "apache/2.4.6 (red hat enterprise linux)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True
    assert result['Server compiled with']['APR_HAVE_IPV6'] == "IPv4-mapped addresses enabled"
    assert result['Server compiled with']['DEFAULT_PIDLOG'] == "/run/httpd/httpd.pid"

    ps = PsAuxcww(context_wrap(PS_EVENT))
    result = HttpdV(rh, ps, hv1, hv3, hv2)
    assert result["Server MPM"] == "event"
    assert result["Server version"] == "apache/2.4.6 (red hat enterprise linux)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" not in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True


def test_httpd_V_RHEL7():
    hv1 = HV(context_wrap(HTTPDV1))
    hv2 = HWV(context_wrap(HTTPDV2, path='httpd.worker_-V'))
    hv3 = HEV(context_wrap(HTTPDV3, path='httpd.event_-V'))
    ps = PsAuxcww(context_wrap(PS_WORKER))
    rh = RedhatRelease(context_wrap(RHEL7))
    result = HttpdV(rh, ps, hv1, hv3, hv2)
    assert result["Server MPM"] == "prefork"
    assert result["Server version"] == "apache/2.2.15 (unix)"
    assert result["forked"] == "yes (variable process count)"
    assert "APR_HAVE_IPV6" in result['Server compiled with']
    assert result['Server compiled with']['APR_HAS_MMAP'] is True
    assert result['Server compiled with']['APR_HAVE_IPV6'] == "IPv4-mapped addresses enabled"
    assert result['Server compiled with']['DEFAULT_PIDLOG'] == "run/httpd.pid"


def test_httpd_V_failed():
    hv1 = HV(context_wrap(HTTPDV1))
    hv2 = HWV(context_wrap(HTTPDV2, path='httpd.worker_-V'))
    ps = PsAuxcww(context_wrap(PS_EVENT))
    rh = RedhatRelease(context_wrap(RHEL6))
    with pytest.raises(SkipComponent) as sc:
        HttpdV(rh, ps, hv1, None, hv2)
    assert "Unable to get the valid `httpd -V` command" in str(sc)
