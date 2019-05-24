import doctest
from insights.tests import context_wrap
from insights.parsers import rsyslog_conf
from insights.parsers.rsyslog_conf import RsyslogConf, RsyslogConf8


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

RSYSLOG_CONF_RHEL8 = """
# rsyslog configuration file

# For more information see /usr/share/doc/rsyslog-*/rsyslog_conf.html
# or latest version online at http://www.rsyslog.com/doc/rsyslog_conf.html
# If you experience problems, see http://www.rsyslog.com/doc/troubleshoot.html

#### MODULES ####

module(load="imuxsock" 	  # provides support for local system logging (e.g. via logger command)
\t\tSysSock.Use="off") # Turn off message reception via local log socket;
\t\t# local messages are retrieved through imjournal now.
module(load="imjournal" 	    # provides access to the systemd journal
\t\tStateFile="imjournal.state") # File to store the position in the journal
#module(load="imklog") # reads kernel messages (the same are read from journald)
#module(load"immark") # provides --MARK-- message capability

module(load="abc" xyz="on")
# Provides UDP syslog reception
# for parameters see http://www.rsyslog.com/doc/imudp.html
module(load="imudp") # needs to be done just once
input(type="imudp" port="514")

# Provides TCP syslog reception
# for parameters see http://www.rsyslog.com/doc/imtcp.html
#module(load="imtcp") # needs to be done just once
#input(type="imtcp" port="514")

#### GLOBAL DIRECTIVES ####

# Where to place auxiliary files
global(workDirectory="/var/lib/rsyslog")

# Use default timestamp format
module(load="builtin:omfile" Template="RSYSLOG_TraditionalFileFormat")

# Include all config files in /etc/rsyslog.d/
include(file="/etc/rsyslog.d/*.conf" mode="optional")


#### RULES ####

# Log all kernel messages to the console.
# Logging much else clutters up the screen.
kern.*                                                 /dev/console

# Log anything (except mail) of level info or higher.
# Don't log private authentication messages!
*.info;mail.none;authpriv.none;cron.none                /var/log/messages

# The authpriv file has restricted access.
authpriv.*                                              /var/log/secure

# Log all the mail messages in one place.
mail.*                                                  -/var/log/maillog


# Log cron stuff
cron.*                                                  /var/log/cron

# Everybody gets emergency messages
*.emerg                                                 :omusrmsg:*

# Save news errors of level crit and higher in a special file.
uucp,news.crit                                          /var/log/spooler

# Save boot messages also to boot.log
local7.*                                                /var/log/boot.log
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

    ctx = context_wrap(RSYSLOG_CONF_RHEL8)
    rsys = RsyslogConf8(ctx)
    assert rsys.module_details == {'imuxsock': {'SysSock.Use': 'off'},
                                   'imjournal': {'StateFile': 'imjournal.state'},
                                   'abc': {'xyz': 'on'},
                                   'imudp': {},
                                   'builtin:omfile': {'Template': 'RSYSLOG_TraditionalFileFormat'}}
    d = list(rsys)
    assert len(d) == 18
    assert len(rsys.module_details) == 5
    assert len(rsys.log_details) == 8
    assert rsys.global_details == {'workDirectory': '/var/lib/rsyslog'}
    assert rsys.input_details == {'imudp': '514'}
    assert rsys.include_details == {'/etc/rsyslog.d/*.conf': {'mode': 'optional'}}


def test_rsyslog_conf_1():
    ctx = context_wrap(RSYSLOG_CONF_1)
    m = RsyslogConf(ctx)
    d = list(m)
    assert len(m) == 1
    assert len(d) == 1
    # Test that commented-out config items are not detected
    assert 'ModLoad' not in m.config_items
    assert 'InputTCPServerRun' not in m.config_items


def test_rsyslog_rhel8_doc_examples():
    env = {
        'rsl': RsyslogConf(context_wrap(RSYSLOG_CONF_0)),
        'rsys': RsyslogConf8(context_wrap(RSYSLOG_CONF_RHEL8))
    }
    failed, total = doctest.testmod(rsyslog_conf, globs=env)
    assert failed == 0
