from insights.tests import context_wrap
from insights.parsers.rsyslog_conf import RsyslogConf

RSYSLOG_CONF_0 = """
:fromhost-ip, regex, "10.0.0.[0-9]" /tmp/my_syslog.log
$ModLoad imtcp
$InputTCPServerRun 10514
$template SpiceTmpl,"%TIMESTAMP%.%TIMESTAMP:::date-subseconds% %syslogtag% %syslogseverity-text%:%msg:::sp-if-no-1st-sp%%msg:::drop-last-lf%\\n"
$WorkDirectory /var/opt/rsyslog # where to place spool files
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
    assert len(m) == 5
    assert len(d) == 5
    # Test configuration item detection in dictionary
    assert hasattr(m, 'config_items')
    assert isinstance(m.config_items, dict)
    assert 'ModLoad' in m.config_items
    assert m.config_items['ModLoad'] == 'imtcp'
    assert m.config_items['InputTCPServerRun'] == '10514'
    assert m.config_items['template'] == 'SpiceTmpl,"%TIMESTAMP%.%TIMESTAMP:::date-subseconds% %syslogtag% %syslogseverity-text%:%msg:::sp-if-no-1st-sp%%msg:::drop-last-lf%\\n"'
    assert 'ForwardSyslogHost' not in m.config_items
    # configuration items should not include the comment.
    assert 'WorkDirectory' in m.config_items
    assert m.config_items['WorkDirectory'] == '/var/opt/rsyslog'
    # Test configuration item accessor
    assert hasattr(m, 'config_val')
    assert m.config_val('ModLoad') == 'imtcp'
    assert m.config_val('ForwardSyslogHost', 'syslog.example.com') == 'syslog.example.com'


def test_rsyslog_conf_1():
    ctx = context_wrap(RSYSLOG_CONF_1)
    m = RsyslogConf(ctx)
    d = list(m)
    assert len(m) == 1
    assert len(d) == 1
    # Test that commented-out config items are not detected
    assert 'ModLoad' not in m.config_items
    assert 'InputTCPServerRun' not in m.config_items
