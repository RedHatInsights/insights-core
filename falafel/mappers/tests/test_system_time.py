from falafel.tests import context_wrap
from falafel.mappers import system_time

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


def test_sysconfig_ntpd():
    result = system_time.NTPDService(context_wrap(NTPD)).data
    assert result['OPTIONS'] == '"-x -g"'
    assert result.get('HIDE') is None
