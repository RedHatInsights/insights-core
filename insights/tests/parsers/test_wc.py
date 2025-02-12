import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import wc
from insights.parsers.wc import WcProc1Mountinfo, WcPcpConfigPmda
from insights.tests import context_wrap

WC_PROC_1_MOUNTINFO_ERR1 = """
-bash: /usr/bin/wcq: No such file or directory
""".strip()

WC_PROC_1_MOUNTINFO_ERR2 = """
/usr/bin/wc: /proc/100/mountinfo: No such file or directory
""".strip()

WC_PROC_1_MOUNTINFO_ERR3 = """
unknow /proc/1/mountinfo
""".strip()

WC_PROC_1_MOUNTINFO = """
37 /proc/1/mountinfo
""".strip()

WC_PCP_CONFIG_PMDA = """
6 /var/lib/pcp/config/pmda/144.0.py
3 /var/lib/pcp/config/pmda/60.1
5 /var/lib/pcp/config/pmda/60.10
3 /var/lib/pcp/config/pmda/60.11
275 /var/lib/pcp/config/pmda/60.12
16 /var/lib/pcp/config/pmda/60.17
3 /var/lib/pcp/config/pmda/60.24
6 /var/lib/pcp/config/pmda/60.28
17 /var/lib/pcp/config/pmda/60.3
21 /var/lib/pcp/config/pmda/60.32
974 /var/lib/pcp/config/pmda/60.4
140113 /var/lib/pcp/config/pmda/60.40
24 /var/lib/pcp/config/pmda/62.0
141466 total
""".strip()

WC_PCP_CONFIG_PMDA_ERROR = """
wc: 'var/lib/pcp/config/pmda/*': No such file or directory
""".strip()


def test_wc_proc_1_mountinfo():
    results = WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO))
    assert results.line_count == 37


def test_wc_proc_1_mountinfo_errors():
    with pytest.raises(SkipComponent) as pe:
        WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO_ERR1))
        assert WC_PROC_1_MOUNTINFO_ERR1 in str(pe)

    with pytest.raises(SkipComponent) as pe:
        WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO_ERR2))
        assert WC_PROC_1_MOUNTINFO_ERR2 in str(pe)

    with pytest.raises(ParseException) as pe:
        WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO_ERR3))
        assert WC_PROC_1_MOUNTINFO_ERR3 in str(pe)


def test_wc_var_lib_pcp_config_pmda():
    results = WcPcpConfigPmda(context_wrap(WC_PCP_CONFIG_PMDA))
    assert results['/var/lib/pcp/config/pmda/144.0.py'] == 6


def test_wc_var_lib_pcp_config_pmda_error():
    with pytest.raises(SkipComponent) as pe:
        WcPcpConfigPmda(context_wrap(WC_PCP_CONFIG_PMDA_ERROR))
        assert WC_PCP_CONFIG_PMDA_ERROR in str(pe)


def test_doc_examples():
    env = {
            'wc_info': WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO)),
            'wc_pcp_config_pmda': WcPcpConfigPmda(context_wrap(WC_PCP_CONFIG_PMDA)),
          }
    failed, total = doctest.testmod(wc, globs=env)
    assert failed == 0
