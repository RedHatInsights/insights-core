from falafel.mappers import ntp_sources
from falafel.tests import context_wrap

chrony_output = """
210 Number of sources = 3
MS Name/IP address Stratum Poll Reach LastRx Last sample
===============================================================================
#* GPS0            0        4    377   11  -479ns[ -621ns]  +/- 134ns
^? a.b.c 2 6 377 23 -923us[ -924us] +/- 43ms
^+ d.e.f 1 6 377 21 -2629us[-2619us] +/- 86ms
""".strip()

ntpd_output = """
     remote           refid      st t when poll reach   delay   offset  jitter
==============================================================================
*ntp103.cm4.tbsi 10.225.208.100   2 u  225  256  377    0.464    0.149   0.019
+ntp104.cm4.tbsi 10.228.209.150   2 u  163  256  377    0.459   -0.234   0.05
""".strip()


def test_get_chrony_sources():
    mapper_result = ntp_sources.get_chrony_sources(context_wrap(chrony_output))
    assert mapper_result[1].get("source") == "a.b.c"
    assert mapper_result[2].get("state") == "+"
    assert mapper_result[2].get("mode") == "^"


def test_get_ntpd_sources():
    mapper_result = ntp_sources.get_ntpd_sources(context_wrap(ntpd_output))
    assert mapper_result[0].get("source") == "ntp103.cm4.tbsi"
    assert mapper_result[1].get("flag") == "+"
    assert mapper_result[1].get("source") == "ntp104.cm4.tbsi"