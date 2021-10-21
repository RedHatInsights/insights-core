import doctest
from insights.tests import context_wrap
from insights.parsers import rsyslog_conf
from insights.parsers.rsyslog_conf import RsyslogConf


RSYSLOG_CONF = r"""
# Provides TCP syslog reception
:msg, regex, "\/vob\/.*\.[cpp|c|java]" /var/log/appMessages
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
$ModLoad imtcp
$InputTCPServerRun 10514
module(load="imuxsock"    # provides support for local system logging (e.g. via logger command)
       SysSock.Use="off") # Turn off message reception via local log socket;
module(load="builtin:omfile" Template="RSYSLOG_TraditionalFileFormat")
include(file="/etc/rsyslog.d/*.conf" mode="optional")
global(workDirectory="/var/lib/rsyslog")
*.info {
   action(
     type="omfile"
     name="hehe"
     file="/tmp/testnimei")
}
if $programname == 'prog1' then {
   action(type="omfile" file="/var/log/prog1.log")
   if $msg contains 'test' then
     action(type="omfile" file="/var/log/prog1test.log")
   else
     action(type="omfile" file="/var/log/prog1notest.log")
}
include(file="/etc/rsyslog.d/*.conf" mode="optional")
cron.*                                                  /var/log/cron
""".strip()


def test_rsyslog_conf_1():
    rsyslogconf = RsyslogConf(context_wrap(RSYSLOG_CONF))
    assert len(rsyslogconf) == 13
    assert rsyslogconf[2] == "authpriv.*                                              /var/log/secure"
    assert rsyslogconf[9] == """*.info { action( type="omfile" name="hehe" file="/tmp/testnimei") }"""


def test_rsyslog_doc_examples():
    env = {
        'rsysconf': RsyslogConf(context_wrap(RSYSLOG_CONF)),
    }
    failed, total = doctest.testmod(rsyslog_conf, globs=env)
    assert failed == 0
