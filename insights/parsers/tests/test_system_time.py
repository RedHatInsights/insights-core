from insights.tests import context_wrap
from insights.parsers import system_time


CHRONY_CONF = """
# Use public servers from the pool.ntp.org project.
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
server 0.rhel.pool.ntp.org iburst
server 1.rhel.pool.ntp.org iburst
server 2.rhel.pool.ntp.org iburst
server 3.rhel.pool.ntp.org iburst

# Ignore stratum in source selection.
stratumweight 0

# Record the rate at which the system clock gains/losses time.
driftfile /var/lib/chrony/drift

# Enable kernel RTC synchronization.
rtcsync

# In first three updates step the system clock instead of slew
# if the adjustment is larger than 10 seconds.
makestep 10 3

# Allow NTP client access from local network.
#allow 192.168/16

# Listen for commands only on localhost.
bindcmdaddress 127.0.0.1
bindcmdaddress ::1

# Serve time even if not synchronized to any NTP server.
#local stratum 10

keyfile /etc/chrony.keys

# Specify the key used as password for chronyc.
commandkey 1

# Generate command key if missing.
generatecommandkey

# Disable logging of client accesses.
noclientlog

# Send a message to syslog if a clock adjustment is larger than 0.5 seconds.
logchange 0.5

logdir /var/log/chrony
#log measurements statistics tracking

leapsecmode slew
maxslewrate 1000
smoothtime 400 0.001 leaponly
"""

STANDARD_NTP_CONF = """
# For more information about this file, see the man pages
# ntp.conf(5), ntp_acc(5), ntp_auth(5), ntp_clock(5), ntp_misc(5), ntp_mon(5).

driftfile /var/lib/ntp/drift

# Permit time synchronization with our time source, but do not
# permit the source to query or modify the service on this system.
restrict default nomodify notrap nopeer noquery

# Permit all access over the loopback interface.  This could
# be tightened as well, but to do so would effect some of
# the administrative functions.
restrict 127.0.0.1
restrict ::1

# Hosts on local network are less restricted.
#restrict 192.168.1.0 mask 255.255.255.0 nomodify notrap

# Use public servers from the pool.ntp.org project.
# Please consider joining the pool (http://www.pool.ntp.org/join.html).
#server 0.rhel.pool.ntp.org iburst
#server 1.rhel.pool.ntp.org iburst
#server 2.rhel.pool.ntp.org iburst

#broadcast 192.168.1.255 autokey        # broadcast server
#broadcastclient                        # broadcast client
#broadcast 224.0.1.1 autokey            # multicast server
#multicastclient 224.0.1.1              # multicast client
#manycastserver 239.255.254.254         # manycast server
#manycastclient 239.255.254.254 autokey # manycast client

# Enable public key cryptography.
#crypto

includefile /etc/ntp/crypto/pw

# Key file containing the keys and key identifiers used when operating
# with symmetric key cryptography.
keys /etc/ntp/keys

# Specify the key identifiers which are trusted.
#trustedkey 4 8 42

# Specify the key identifier to use with the ntpdc utility.
#requestkey 8

# Specify the key identifier to use with the ntpq utility.
#controlkey 8

# Enable writing of statistics records.
#statistics clockstats cryptostats loopstats peerstats

# Disable the monitoring facility to prevent amplification attacks using ntpdc
# monlist command when default restrict does not include the noquery flag. See
# CVE-2013-5211 for more details.
# Note: Monitoring will not be disabled with the limited restriction flag.
#disable monitor

# Set a couple of single keyword options:
broadcastclient
iburst

### Added by IPA Installer ###
server 127.127.1.0
fudge 127.127.1.0 stratum 10

server 10.20.30.40
server 192.168.1.111

### Added by IPA Installer ###
peer ntp1.example.com
peer ntp2.example.com
peer ntp3.example.com

"""

ZERO_HOSTS_NTP_CONF = """
broadcastclient
"""

NTP_TINKER_CONF = """
driftfile /var/lib/ntp/ntp.drift
restrict default kod nomodify notrap nopeer noquery
restrict 127.0.0.1
server 192.168.17.62 iburst
tinker step 0.9
tinker step step
tinker step 0.4
"""


def test_chrony_conf():
    ntp_obj = system_time.ChronyConf(context_wrap(CHRONY_CONF))
    result = ntp_obj.data
    assert result['server'] == ["0.rhel.pool.ntp.org iburst",
            "1.rhel.pool.ntp.org iburst",
            "2.rhel.pool.ntp.org iburst",
            "3.rhel.pool.ntp.org iburst"]
    # keywords that are present but single word are present but equal None
    assert 'rtcsync' in result
    assert result.get('rtcsync') is None
    assert result['leapsecmode'] == ['slew']
    assert result['smoothtime'] == ['400 0.001 leaponly']

    # Test get_param method:
    # - nonexistent keyword
    assert ntp_obj.get_param('device') == [None]
    assert ntp_obj.get_param('device', 'embn0') == [None]
    assert ntp_obj.get_param('device', default='bad') == ['bad']
    assert ntp_obj.get_param('device', param='embn0', default='bad') == ['bad']
    assert ntp_obj.get_param('device', 'embn0', 'bad') == ['bad']
    # - simple keyword with no value - default and param ignored
    assert ntp_obj.get_param('noclientlog') == [None]
    assert ntp_obj.get_param('noclientlog', 'true') == [None]
    assert ntp_obj.get_param('noclientlog', default='yes') == [None]
    assert ntp_obj.get_param('noclientlog', param='true', default='yes') == [None]
    assert ntp_obj.get_param('noclientlog', 'true', 'yes') == [None]
    # - simple keyword with value - default and param ignored
    assert ntp_obj.get_param('commandkey') == ['1']
    assert ntp_obj.get_param('commandkey', '0') == ['1']
    assert ntp_obj.get_param('commandkey', default='2') == ['1']
    assert ntp_obj.get_param('commandkey', param='0', default='2') == ['1']
    assert ntp_obj.get_param('commandkey', '0', '2') == ['1']

    # Test get_last method:
    # - nonexistent keyword
    assert ntp_obj.get_last('device') is None
    assert ntp_obj.get_last('device', 'embn0') is None
    assert ntp_obj.get_last('device', default='bad') == 'bad'
    assert ntp_obj.get_last('device', param='embn0', default='bad') == 'bad'
    assert ntp_obj.get_last('device', 'embn0', 'bad') == 'bad'
    # - simple keyword with no value - default and param ignored
    assert ntp_obj.get_last('noclientlog') is None
    assert ntp_obj.get_last('noclientlog', 'true') is None
    assert ntp_obj.get_last('noclientlog', default='yes') is None  # present, so no default
    assert ntp_obj.get_last('noclientlog', param='true', default='yes') is None
    assert ntp_obj.get_last('noclientlog', 'true', 'yes') is None
    # - simple keyword with value - default and param ignored
    assert ntp_obj.get_last('commandkey') == '1'
    assert ntp_obj.get_last('commandkey', '0') == '1'
    assert ntp_obj.get_last('commandkey', default='2') == '1'
    assert ntp_obj.get_last('commandkey', param='0', default='2') == '1'
    assert ntp_obj.get_last('commandkey', '0', '2') == '1'
    # More testing in ntp_tinker_conf


LOCALTIME = "/etc/localtime: timezone data, version 2, 5 gmt time flags, \
5 std time flags, no leap seconds, 69 transition times, 5 abbreviation chars"

LOCALTIME_BAD = "/etc/localtime: file not found"


def test_localtime():
    result = system_time.LocalTime(context_wrap(LOCALTIME)).data
    assert result['name'] == "/etc/localtime"
    assert result['version'] == "2"
    assert result['gmt_time_flag'] == "5"
    assert result['std_time_flag'] == "5"
    assert result['leap_second'] == "no"
    assert result['transition_time'] == "69"
    assert result['abbreviation_char'] == "5"


def test_bad_localtime():
    result = system_time.LocalTime(context_wrap(LOCALTIME_BAD)).data
    assert result == {'name': '/etc/localtime'}


NTPTIME = """
ntp_gettime() returns code 0 (OK)
  time dbbc595d.1adbd720  Thu, Oct 27 2016 18:45:49.104, (.104917550),
  maximum error 263240 us, estimated error 102 us, TAI offset 0
ntp_adjtime() returns code 0 (OK)
  modes 0x0 (),
  offset 0.000 us, frequency 4.201 ppm, interval 1 s,
  maximum error 263240 us, estimated error 102 us,
  status 0x2011 (PLL,INS,NANO),
  time constant 2, precision 0.001 us, tolerance 500 ppm,
""".strip()

NTPTIME_STATUS = """
ntp_gettime() returns code 5 (ERROR)
  time ddb6c4ae.e3485000  Wed, Nov 15 2017 13:50:38.887, (.887822),
  maximum error 16000000 us, estimated error 16000000 us, TAI offset 0
ntp_adjtime() returns code 5 (ERROR)
  modes 0x0 (),
  offset 0.000 us, frequency 0.000 ppm, interval 1 s,
  maximum error 16000000 us, estimated error 16000000 us,
  status 0x50 (INS,UNSYNC),
  time constant 2, precision 1.000 us, tolerance 500 ppm,
""".strip()


def test_ntptime():
    result = system_time.NtpTime(context_wrap(NTPTIME)).data
    assert result['ntp_gettime'] == '0'
    assert result['ntp_adjtime'] == '0'
    assert result['status'] == '0x2011'
    assert result['flags'] == ['PLL', 'INS', 'NANO']

    assert result['timecode'] == 'dbbc595d.1adbd720'
    assert result['timestamp'] == 'Thu, Oct 27 2016 18:45:49.104, (.104917550)'
    assert result['maximum error'] == 263240
    assert result['estimated error'] == 102
    assert result['TAI offset'] == 0
    assert result['modes'] == 0x0
    assert result['offset'] == 0.000
    assert result['frequency'] == 4.201
    assert result['interval'] == 1
    assert result['time constant'] == 2
    assert result['precision'] == 0.001
    assert result['tolerance'] == 500


def test_ntptime_status():
    result = system_time.NtpTime(context_wrap(NTPTIME_STATUS)).data
    assert result['ntp_gettime'] == '5'
    assert result['ntp_adjtime'] == '5'
    assert result['status'] == '0x50'
    assert result['flags'] == ['INS', 'UNSYNC']


def test_standard_ntp_conf():
    ntp_obj = system_time.NTPConf(context_wrap(STANDARD_NTP_CONF))
    assert ntp_obj
    assert hasattr(ntp_obj, 'data')

    # Test configuration dictionary
    data = ntp_obj.data
    assert data == {
        'driftfile': ['/var/lib/ntp/drift'],
        'restrict': [
            'default nomodify notrap nopeer noquery',
            '127.0.0.1',
            '::1',
        ],
        'includefile': ['/etc/ntp/crypto/pw'],
        'keys': ['/etc/ntp/keys'],
        'broadcastclient': None,
        'iburst': None,
        'server': [
            '127.127.1.0',
            '10.20.30.40',
            '192.168.1.111',
        ],
        'fudge': ['127.127.1.0 stratum 10'],
        'peer': [
            'ntp1.example.com',
            'ntp2.example.com',
            'ntp3.example.com',
        ]
    }

    # Test other attributes
    assert hasattr(ntp_obj, 'servers')
    assert ntp_obj.servers == \
        ['10.20.30.40', '127.127.1.0', '192.168.1.111']
    assert hasattr(ntp_obj, 'peers')
    assert ntp_obj.peers == \
        ['ntp1.example.com', 'ntp2.example.com', 'ntp3.example.com']

    # Test get_last with parameter not found
    assert ntp_obj.get_last('tinker', 'panic') is None


def test_zero_hosts_ntp_conf():
    ntp_obj = system_time.NTPConf(context_wrap(ZERO_HOSTS_NTP_CONF))
    assert ntp_obj
    assert hasattr(ntp_obj, 'data')
    assert ntp_obj.data == {
        'broadcastclient': None
    }
    assert hasattr(ntp_obj, 'servers')
    assert ntp_obj.servers == []
    assert hasattr(ntp_obj, 'peers')
    assert ntp_obj.peers == []


def test_ntp_get_tinker():
    ntp_obj = system_time.NTPConf(context_wrap(NTP_TINKER_CONF))
    assert ntp_obj
    assert hasattr(ntp_obj, 'data')
    assert 'tinker' in ntp_obj.data
    # tinker defined but panic not one of its parameters
    assert ntp_obj.get_last('tinker', 'panic') is None
    # tinker step defined
    assert ntp_obj.get_last('tinker', 'step') == '0.4'

    # - keyword parameter value - param not found
    assert ntp_obj.get_last('tinker', 'panic') is None
    assert ntp_obj.get_last('tinker', default='1') == 'step 0.4'  # No param: just find last line
    assert ntp_obj.get_last('tinker', param='panic', default='1') == '1'
    assert ntp_obj.get_last('tinker', 'panic', '1') == '1'

    # - keyword parameter value - param found
    assert ntp_obj.get_last('tinker', 'step') == '0.4'
    assert ntp_obj.get_last('tinker', param='step', default='1') == '0.4'  # Value from config
    assert ntp_obj.get_last('tinker', 'step', '1') == '0.4'
