from falafel.tests import context_wrap
from falafel.mappers import system_time


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

CHRONYD = """
OPTIONS="-d"
#HIDE="me"
""".strip()

LOCALTIME = "/etc/localtime: timezone data, version 2, 5 gmt time flags, \
5 std time flags, no leap seconds, 69 transition times, 5 abbreviation chars"

NTPD = """
OPTIONS="-x -g"
#HIDE="me"
""".strip()

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


def test_chrony_conf():
    result = system_time.ChronyConf(context_wrap(CHRONY_CONF)).data
    assert result['server'] == ["0.rhel.pool.ntp.org iburst",
            "1.rhel.pool.ntp.org iburst",
            "2.rhel.pool.ntp.org iburst",
            "3.rhel.pool.ntp.org iburst"]
    assert result.get('rtcsync') is None
    assert 'rtcsync' in result
    assert result['leapsecmode'] == ['slew']
    assert result['smoothtime'] == ['400 0.001 leaponly']


def test_localtime():
    result = system_time.LocalTime(context_wrap(LOCALTIME)).data
    assert result['name'] == "/etc/localtime"
    assert result['version'] == "2"
    assert result['gmt_time_flag'] == "5"
    assert result['std_time_flag'] == "5"
    assert result['leap_second'] == "no"
    assert result['transition_time'] == "69"
    assert result['abbreviation_char'] == "5"


def test_ntptime():
    result = system_time.NtpTime(context_wrap(NTPTIME)).data
    assert result['ntp_gettime'] == '0'
    assert result['ntp_adjtime'] == '0'
    assert result['status'] == '0x2011'
    assert result['flags'] == ['PLL', 'INS', 'NANO']


def test_sysconfig_chronyd():
    result = system_time.ChronydService(context_wrap(CHRONYD)).data
    assert result['OPTIONS'] == '"-d"'
    assert result.get('HIDE') is None


def test_sysconfig_ntpd():
    result = system_time.NTPDService(context_wrap(NTPD)).data
    assert result['OPTIONS'] == '"-x -g"'
    assert result.get('HIDE') is None
