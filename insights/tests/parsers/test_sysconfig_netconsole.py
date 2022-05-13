from insights.parsers.sysconfig import NetconsoleSysconfig
from insights.tests import context_wrap


netconsole = '''
# This is the configuration file for the netconsole service.  By starting
# this service you allow a remote syslog daemon to record console output
# from this system.

# The local port number that the netconsole module will use
LOCALPORT=6666

# The ethernet device to send console messages out of (only set this if it
# can't be automatically determined)
# DEV=

# The IP address of the remote syslog server to send messages to
# SYSLOGADDR=

# The listening port of the remote syslog daemon
SYSLOGPORT=514

# The MAC address of the remote syslog server (only set this if it can't
# be automatically determined)
# SYSLOGMACADDR=
'''.strip()


def test_netconsole():
    result = NetconsoleSysconfig(context_wrap(netconsole))
    assert result["LOCALPORT"] == '6666'
    assert result.get("DEV") is None
    assert result['SYSLOGPORT'] == "514"
