import pytest
import doctest
from insights.core.dr import SkipComponent
from insights.parsers import ntp_sources
from insights.parsers.ntp_sources import ChronycSources, NtpqPn, NtpqLeap
from insights.tests import context_wrap

chrony_output = """
210 Number of sources = 3
MS Name/IP address Stratum Poll Reach LastRx Last sample
===============================================================================
#* GPS0            0        4    377   11  -479ns[ -621ns]  +/- 134ns
^? a.b.c 2 6 377 23 -923us[ -924us] +/- 43ms
^+ d.e.f 1 6 377 21 -2629us[-2619us] +/- 86ms
""".strip()

chrony_output_doc = """
210 Number of sources = 6
MS Name/IP address         Stratum Poll Reach LastRx Last sample
===============================================================================
^- 10.20.30.40                   2   9   377    95  -1345us[-1345us] +/-   87ms
^- 10.56.72.8                    2  10   377   949  -3449us[-3483us] +/-  120ms
^* 10.64.108.95                  2  10   377   371    -91us[ -128us] +/-   30ms
^- 10.8.205.17                   2   8   377    27  +7161us[+7161us] +/-   52ms
""".strip()

empty_chrony_source = ""

empty_ntpq_leap = ""

ntpq_leap_output = """
leap=00
""".strip()

ntpq_leap_output_2 = """
assID=0 status=06f4 leap_none, sync_ntp, 15 events, event_peer/strat_chg,
leap=00
""".strip()

ntpd_output = """
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*ntp103.cm4.tbsi 10.225.208.100   2 u  225  256  377    0.464    0.149   0.019
+ntp104.cm4.tbsi 10.228.209.150   2 u  163  256  377    0.459   -0.234   0.05
""".strip()

ntpd_qn = """
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
 202.118.1.81    .INIT.          16 u    - 1024    0    0.000    0.000   0.000
""".strip()

ntpd_qn_doc = """
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
+10.20.30.40     192.231.203.132  3 u  638 1024  377    0.242    2.461   1.886
*2001:388:608c:8 .GPS.            1 u  371 1024  377   29.323    1.939   1.312
-2001:44b8:1::1  216.218.254.202  2 u  396 1024  377   37.869   -3.340   6.458
+150.203.1.10    202.6.131.118    2 u  509 1024  377   20.135    0.800   3.260
""".strip()

empty_ntpq_pn = ""

ntp_connection_issue = """
/usr/sbin/ntpq: read: Connection refused
""".strip()


def test_get_chrony_sources():
    parser_result = ChronycSources(context_wrap(chrony_output))
    assert parser_result.data[1].get("source") == "a.b.c"
    assert parser_result.data[2].get("state") == "+"
    assert parser_result.data[2].get("mode") == "^"

    with pytest.raises(SkipComponent):
        NtpqPn(context_wrap(empty_chrony_source))


def test_get_ntpq_leap():
    parser_result = NtpqLeap(context_wrap(ntpq_leap_output))
    assert parser_result.leap == "00"

    parser_result = NtpqLeap(context_wrap(ntpq_leap_output_2))
    assert parser_result.leap == "00"

    with pytest.raises(SkipComponent) as e:
        NtpqLeap(context_wrap(ntp_connection_issue))
    assert "NTP service is down" in str(e)

    with pytest.raises(SkipComponent):
        NtpqLeap(context_wrap(empty_ntpq_leap))


def test_get_ntpd_sources():
    parser_result = NtpqPn(context_wrap(ntpd_output))
    assert parser_result.data[0].get("source") == "ntp103.cm4.tbsi"
    assert parser_result.data[1].get("flag") == "+"
    assert parser_result.data[1].get("source") == "ntp104.cm4.tbsi"

    parser_result2 = NtpqPn(context_wrap(ntpd_qn))
    assert parser_result2.data[0].get("source") == "202.118.1.81"
    assert parser_result2.data[0].get("flag") == " "

    with pytest.raises(SkipComponent) as e:
        NtpqPn(context_wrap(ntp_connection_issue))
    assert "NTP service is down" in str(e)

    with pytest.raises(SkipComponent):
        NtpqPn(context_wrap(empty_ntpq_pn))


def test_ntp_sources_doc_examples():
    env = {
        'chrony_sources': ChronycSources(context_wrap(chrony_output_doc)),
        'ntpq': NtpqLeap(context_wrap(ntpq_leap_output)),
        'ntp_sources': NtpqPn(context_wrap(ntpd_qn_doc)),
    }
    failed, total = doctest.testmod(ntp_sources, globs=env)
    assert failed == 0
