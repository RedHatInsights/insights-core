from insights.tests import context_wrap
from insights.parsers.rsyslog_conf import RsyslogConf

RSYSLOG_CONF_0 = """
:fromhost-ip, regex, "10.0.0.[0-9]" /tmp/my_syslog.log
$ModLoad imtcp
$InputTCPServerRun 10514"
""".strip()

RSYSLOG_CONF_1 = r"""
# Provides TCP syslog reception
#$ModLoad imtcp.so
#$InputTCPServerRun 514
:msg, regex, "\/vob\/.*\.[cpp|c|java]" /var/log/appMessages
""".strip()


def test_rsyslog_conf_0():
    ctx = context_wrap(RSYSLOG_CONF_0)
    m = RsyslogConf(ctx)
    d = list(m)
    assert len(m) == 3
    assert len(d) == 3


def test_rsyslog_conf_1():
    ctx = context_wrap(RSYSLOG_CONF_1)
    m = RsyslogConf(ctx)
    d = list(m)
    assert len(m) == 1
    assert len(d) == 1
