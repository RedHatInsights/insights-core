from insights.combiners.rsyslog_confs import RsyslogAllConf
from insights.core.exceptions import SkipComponent
from insights.parsers.rsyslog_conf import RsyslogConf
from insights.specs.datasources.rsyslog_confs import rsyslog_errorfile
from insights.tests import context_wrap
import pytest


RSYSLOG_ALL_CONF_1 = """
#$DebugLevel 2
#RSYSLOG_DEBUGLOG=/opt/data/syslog/tls_logging.log

# For more information see /usr/share/doc/rsyslog-*/rsyslog_conf.html
# If you experience problems, see http://www.rsyslog.com/doc/troubleshoot.html

#### MODULES ####

# Provides UDP syslog reception
#$ModLoad imudp
#$UDPServerRun 514
$ModLoad imtcp.so
$ModLoad imjournal
$InputTCPMaxSessions 10
$IncludeConfig /etc/rsyslog.d/*.conf
if ($.ev_index != "") then {
    if (lookup("es-debug-selector", $.ev_index) == "on") then
    reset $.random = random(300);
    if ($.random >= 0 and $.random < 100) then {
        action(errorfile="/var/log/rsyslog/es-errors1.log")
    }
    else if ($.random >= 100 and $.random < 200) then {
        action(errorfile="/var/log/rsyslog/es-errors2.log")
    }
    else {
        action(errorfile="/var/log/rsyslog/es-errors3.log")
    }
}

# Provides TCP syslog reception
#$ModLoad imtcp
#$InputTCPServerRun 6514

#Configuration for certificte authentication
$DefaultNetstreamDriver gtls
"""

RSYSLOG_ALL_CONF_2 = """
$WorkDirectory /tmp
*.info -/var/log/test.log
"""

RSYSLOG_ALL_CONF_3 = """
module(load="impstats"
)
global(
    # where to store housekeeping data (stat files, queue files, etc)
    oversizemsg.errorfile="/var/log/oversized.log"
)
module(load="imjournal" PersistStateInterval="1000" StateFile="/var/log/imjournal.state" Ratelimit.Interval="1" Ratelimit.Burst="100000")
module(load="imfile" readTimeout="10")
module(load="mmnormalize")
ruleset(name="setvars"){
    set $!ews-trusted!timestamp2=exec_template("timestamp");
}
ruleset(name="set-st"){
    if $!ews-trusted!sourcetype == '' then {
    }
}
ruleset(name="ews-send"){
    action(name="ews-send"
        template="json-fwd")
}
# BUT  because having the most current data is the most important, we use UDP so that if there is a problem, we dont have current data stuck behind old data (we would rather miss some data than be looking at old data)
ruleset(name="pstats" queue.size="2000" queue.type="FixedArray"){
   action(name="pri-send"
        template="json-fwd")
}
"""


def test_rsyslog_errorfiles_1():
    rsyslog1 = RsyslogConf(context_wrap(RSYSLOG_ALL_CONF_1, path="/etc/rsyslog.conf"))
    rsyslog2 = RsyslogConf(context_wrap(RSYSLOG_ALL_CONF_2, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog1, rsyslog2])
    broker = {
        RsyslogAllConf: result
    }
    result = rsyslog_errorfile(broker)
    assert result is not None
    assert result == '/var/log/rsyslog/es-errors1.log /var/log/rsyslog/es-errors2.log /var/log/rsyslog/es-errors3.log'


def test_rsyslog_errorfiles_2():
    rsyslog = RsyslogConf(context_wrap(RSYSLOG_ALL_CONF_2, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog])

    broker = {
        RsyslogAllConf: result
    }
    with pytest.raises(SkipComponent):
        rsyslog_errorfile(broker)


def test_rsyslog_errorfiles_3():
    rsyslog = RsyslogConf(context_wrap(RSYSLOG_ALL_CONF_3, path="/etc/rsyslog.d/test.conf"))
    result = RsyslogAllConf([rsyslog])

    broker = {
        RsyslogAllConf: result
    }
    with pytest.raises(SkipComponent):
        rsyslog_errorfile(broker)
