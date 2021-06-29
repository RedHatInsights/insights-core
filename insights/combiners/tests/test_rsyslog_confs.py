from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.combiners import rsyslog_confs
from insights.parsers.rsyslog_conf import RsyslogConf
from insights.tests import context_wrap
import doctest


RSYSLOG_CONF_MAIN_7 = r"""
$ModLoad imuxsock # provides support for local system logging (e.g. via logger command)
$ModLoad imjournal # provides access to the systemd journal
$WorkDirectory /var/lib/rsyslog
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$IncludeConfig /etc/rsyslog.d/*.conf
$OmitLocalLogging on
$IMJournalStateFile imjournal.state
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
*.emerg                                                 :omusrmsg:*
uucp,news.crit                                          /var/log/spooler
local7.*                                                /var/log/boot.log
""".strip()

RSYSLOG_CONF_MAIN_NO_INCLUDE_7 = r"""
$ModLoad imuxsock # provides support for local system logging (e.g. via logger command)
$ModLoad imjournal # provides access to the systemd journal
$WorkDirectory /var/lib/rsyslog
$ActionFileDefaultTemplate RSYSLOG_TraditionalFileFormat
$OmitLocalLogging on
$IMJournalStateFile imjournal.state
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
*.emerg                                                 :omusrmsg:*
uucp,news.crit                                          /var/log/spooler
local7.*                                                /var/log/boot.log
""".strip()

RSYSLOG_CONF_MAIN_CONF_DIR_7 = r"""
$WorkDirectory /tmp
*.info -/var/log/test.log
""".strip()

RSYSLOG_CONF_MAIN_8 = r"""
module(load="imuxsock"    # provides support for local system logging (e.g. via logger command)
       SysSock.Use="off") # Turn off message reception via local log socket;
module(load="imjournal"             # provides access to the systemd journal
       StateFile="imjournal.state") # File to store the position in the journal
global(workDirectory="/var/lib/rsyslog")
module(load="builtin:omfile" Template="RSYSLOG_TraditionalFileFormat")
include(file="/etc/rsyslog.d/*.conf" mode="optional")
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
if $programname == 'prog1' then {
   action(type="omfile" file="/var/log/prog1.log")
   if $msg contains 'test' then
     action(type="omfile" file="/var/log/prog1test.log")
   else
     action(type="omfile" file="/var/log/prog1notest.log")
}
""".strip()

RSYSLOG_CONF_MAIN_NO_INCLUDE_8 = r"""
module(load="imuxsock"    # provides support for local system logging (e.g. via logger command)
       SysSock.Use="off") # Turn off message reception via local log socket;
module(load="imjournal"             # provides access to the systemd journal
       StateFile="imjournal.state") # File to store the position in the journal
global(workDirectory="/var/lib/rsyslog")
module(load="builtin:omfile" Template="RSYSLOG_TraditionalFileFormat")
*.info;mail.none;authpriv.none;cron.none                /var/log/messages
authpriv.*                                              /var/log/secure
mail.*                                                  -/var/log/maillog
cron.*                                                  /var/log/cron
if $programname == 'prog1' then {
   action(type="omfile" file="/var/log/prog1.log")
   if $msg contains 'test' then
     action(type="omfile" file="/var/log/prog1test.log")
   else
     action(type="omfile" file="/var/log/prog1notest.log")
}
""".strip()

RSYSLOG_CONF_MAIN_CONF_DIR_8 = r"""
*.info {
   action(
     type="omfile"
     name="hehe"
     file="/tmp/test")
}
""".strip()


def test_conf_7_include_dir():
    rsyslog1 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_7, path="/etc/rsyslog.conf"))
    rsyslog2 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_CONF_DIR_7, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog1, rsyslog2])
    assert len(result) == 2
    assert result['/etc/rsyslog.conf'][0] == '$ModLoad imuxsock'


def test_conf_7_no_include_dir():
    rsyslog1 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_NO_INCLUDE_7, path="/etc/rsyslog.conf"))
    rsyslog2 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_CONF_DIR_7, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog1, rsyslog2])
    assert len(result) == 1
    assert result['/etc/rsyslog.conf'][0] == '$ModLoad imuxsock'


def test_conf_8_include_dir():
    rsyslog1 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_8, path="/etc/rsyslog.conf"))
    rsyslog2 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_CONF_DIR_8, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog1, rsyslog2])
    assert len(result) == 2
    assert result['/etc/rsyslog.d/test.conf'] == ['*.info { action( type="omfile" name="hehe" file="/tmp/test") }']


def test_conf_8_no_include_dir():
    rsyslog1 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_NO_INCLUDE_8, path="/etc/rsyslog.conf"))
    rsyslog2 = RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_CONF_DIR_8, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog1, rsyslog2])
    assert len(result) == 1
    assert result['/etc/rsyslog.conf'][2] == 'global(workDirectory="/var/lib/rsyslog")'


def test_rsyslog_confs_doc_examples():
    env = {
            'confs': RsyslogAllConf(
                [
                    RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_7, path='/etc/rsyslog.conf')),
                    RsyslogConf(context_wrap(RSYSLOG_CONF_MAIN_CONF_DIR_7, path='/etc/rsyslog.d/test.conf'))
                ])
          }
    failed, total = doctest.testmod(rsyslog_confs, globs=env)
    assert failed == 0
