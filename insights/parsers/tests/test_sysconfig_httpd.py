from insights.tests import context_wrap
from insights.parsers.sysconfig import HttpdSysconfig

HTTPD = """
# Configuration file for the httpd service.

#
# The default processing model (MPM) is the process-based
# 'prefork' model.  A thread-based model, 'worker', is also
# available, but does not work with some modules (such as PHP).
# The service must be stopped before changing this variable.
#
HTTPD=/usr/sbin/httpd.worker

#
# To pass additional options (for instance, -D definitions) to the
# httpd binary at startup, set OPTIONS here.
#
#OPTIONS=
OPTIONS1=
#
# By default, the httpd process is started in the C locale; to
# change the locale in which the server runs, the HTTPD_LANG
# variable can be set.
#
HTTPD_LANG=C
""".strip()


def test_httpd_service_conf():
    result = HttpdSysconfig(context_wrap(HTTPD))
    assert result["HTTPD"] == '/usr/sbin/httpd.worker'
    assert result.get("OPTIONS") is None
    assert result.get("OPTIONS1") == ''
    assert result['HTTPD_LANG'] == "C"
