from insights.tests import context_wrap
from insights.parsers.httpd_log import HttpdSSLErrorLog, HttpdErrorLog
from insights.parsers.httpd_log import HttpdSSLAccessLog, HttpdAccessLog

from datetime import datetime

SSL_ACCESS_LOG = """
10.68.5.20 - - [29/Mar/2017:05:57:21 -0400] "GET / HTTP/1.1" 403 202 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:59:38 -0400] "GET / HTTP/1.1" 200 84 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
""".strip()


ACCESS_LOG = """
10.68.5.20 - - [29/Mar/2017:05:57:21 -0400] "GET / HTTP/1.1" 403 202 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:58:54 -0400] "GET / HTTP/1.1" 403 202 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:59:38 -0400] "GET / HTTP/1.1" 200 84 "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:59:41 -0400] "GET / HTTP/1.1" 304 - "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:59:43 -0400] "GET / HTTP/1.1" 304 - "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:05:59:44 -0400] "GET / HTTP/1.1" 304 - "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:06:01:13 -0400] "GET / HTTP/1.1" 304 - "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:06:01:17 -0400] "GET / HTTP/1.1" 304 - "-" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
10.68.5.20 - - [29/Mar/2017:21:47:54 -0400] "GET /favicon.ico HTTP/1.1" 404 209 "http://10.66.208.208/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36"
""".strip()

ERROR_LOG = """
[Tue Mar 28 03:56:00.804140 2017] [core:notice] [pid 4343:tid 139992054929536] AH00094: Command line: '/usr/sbin/httpd -D FOREGROUND'
[Tue Mar 28 03:56:38.610607 2017] [mpm_worker:notice] [pid 4343:tid 139992054929536] AH00296: caught SIGWINCH, shutting down gracefully
[Tue Mar 28 03:56:39.737815 2017] [suexec:notice] [pid 4471:tid 140592082000000] AH01232: suEXEC mechanism enabled (wrapper: /usr/sbin/suexec)
AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using fe80::21a:4aff:fe01:160. Set the 'ServerName' directive globally to suppress this message
[Tue Mar 28 03:56:39.771605 2017] [auth_digest:notice] [pid 4471:tid 140592082000000] AH01757: generating secret for digest authentication ...
[Tue Mar 28 03:56:39.772272 2017] [lbmethod_heartbeat:notice] [pid 4471:tid 140592082000000] AH02282: No slotmem from mod_heartmonitor
[Tue Mar 28 03:56:39.772364 2017] [ssl:warn] [pid 4471:tid 140592082000000] AH01873: Init: Session Cache is not configured [hint: SSLSessionCache]
[Tue Mar 28 03:56:39.775833 2017] [mpm_worker:notice] [pid 4471:tid 140592082000000] AH00292: Apache/2.4.6 (Red Hat Enterprise Linux) OpenSSL/1.0.1e-fips configured -- resuming normal operations
""".strip()

HTTPD24_ERROR_LOG = """
[Fri Mar 29 01:42:23.497294 2019] [suexec:notice] [pid 1967] AH01232: suEXEC mechanism enabled (wrapper: /opt/rh/jbcs-httpd24/root/usr/sbin/suexec)
[Fri Mar 29 01:42:23.498726 2019] [:notice] [pid 1967] ModSecurity for Apache/2.9.1 (http://www.modsecurity.org/) configured.
[Fri Mar 29 01:45:23.498736 2019] [:notice] [pid 1967] ModSecurity: APR compiled version="1.6.3"; loaded version="1.6.3-31"
[Fri Mar 29 01:45:23.498743 2019] [:notice] [pid 1967] ModSecurity: PCRE compiled version="8.32 "; loaded version="8.32 2012-11-30"
[Fri Mar 29 01:45:23.498745 2019] [:notice] [pid 1967] ModSecurity: LUA compiled version="Lua 5.1"
[Fri Mar 29 01:47:23.498747 2019] [:notice] [pid 1967] ModSecurity: LIBXML compiled version="2.9.1"
[Fri Mar 29 01:47:23.498749 2019] [:notice] [pid 1967] ModSecurity: Status engine is currently disabled, enable it by set SecStatusEngine to On.
"""

JBCS_HTTPD24_ERROR_LOG = """
[Wed Apr 03 03:52:39.014686 2019] [core:notice] [pid 4499] SELinux policy enabled; httpd running as context system_u:system_r:httpd_t:s0
[Wed Apr 03 03:54:39.016900 2019] [suexec:notice] [pid 4499] AH01232: suEXEC mechanism enabled (wrapper: /opt/rh/httpd24/root/usr/sbin/suexec)
[Wed Apr 03 03:55:39.038125 2019] [http2:warn] [pid 4499] AH10034: The mpm module (prefork.c) is not supported by mod_http2. The mpm determines how things are processed in your server. HTTP/2 has more demands in this regard and the currently selected mpm will just not do. This is an advisory warning. Your server will continue to work, but the HTTP/2 protocol will be inactive.
[Wed Apr 03 03:56:39.038140 2019] [http2:warn] [pid 4499] AH02951: mod_ssl does not seem to be enabled
[Wed Apr 03 03:57:39.038835 2019] [lbmethod_heartbeat:notice] [pid 4499] AH02282: No slotmem from mod_heartmonitor
"""

SSL_ERROR_LOG = """
[Tue Mar 28 03:56:00.804140 2017] [core:notice] [pid 4343:tid 139992054929536] AH00094: Command line: '/usr/sbin/httpd -D FOREGROUND'
[Tue Mar 28 03:56:38.610607 2017] [mpm_worker:notice] [pid 4343:tid 139992054929536] AH00296: caught SIGWINCH, shutting down gracefully
[Tue Mar 28 03:56:39.737815 2017] [suexec:notice] [pid 4471:tid 140592082000000] AH01232: suEXEC mechanism enabled (wrapper: /usr/sbin/suexec)
AH00558: httpd: Could not reliably determine the server's fully qualified domain name, using fe80::21a:4aff:fe01:160. Set the 'ServerName' directive globally to suppress this message
""".strip()


def test_ssl_access_log():
    log = HttpdSSLAccessLog(context_wrap(SSL_ACCESS_LOG))
    assert 2 == len(log.get("10.68.5.20"))
    assert len(list(log.get_after(datetime(2017, 3, 29, 5, 59, 0)))) == 1


def test_access_log():
    log = HttpdAccessLog(context_wrap(ACCESS_LOG))
    assert 9 == len(log.get("10.68.5.20"))
    assert "favicon.ico" in log
    assert len(list(log.get_after(datetime(2017, 3, 29, 6, 0, 0)))) == 3


def test_ssl_error_log():
    log = HttpdSSLErrorLog(context_wrap(SSL_ERROR_LOG))
    assert 1 == len(log.get("mpm_worker:notice"))
    assert "AH00558" in log
    # Includes continuation line
    assert len(list(log.get_after(datetime(2017, 3, 28, 3, 56, 39)))) == 2


def test_error_log():
    log = HttpdErrorLog(context_wrap(ERROR_LOG))
    assert 2 == len(log.get("mpm_worker:notice"))
    assert "AH00558" in log
    # Includes continuation line
    assert len(list(log.get_after(datetime(2017, 3, 28, 3, 56, 39)))) == 6


def test_httpd24_error_log():
    log = HttpdErrorLog(context_wrap(HTTPD24_ERROR_LOG))
    assert 1 == len(log.get("suexec:notice"))
    assert "ModSecurity" in log
    # Includes continuation line
    assert len(list(log.get_after(datetime(2019, 3, 29, 1, 45, 23)))) == 5


def test_jbcs_httpd24_error_log():
    log = HttpdErrorLog(context_wrap(JBCS_HTTPD24_ERROR_LOG))
    assert 2 == len(log.get("http2:warn"))
    assert "suEXEC" in log
    # Includes continuation line
    assert len(list(log.get_after(datetime(2019, 4, 3, 3, 54, 39)))) == 4
