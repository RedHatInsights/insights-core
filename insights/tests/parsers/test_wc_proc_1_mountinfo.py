from insights.parsers.wc_proc_1_mountinfo import WcProc1Mountinfo
from insights.parsers import wc_proc_1_mountinfo
from insights.tests import context_wrap
from insights.core.dr import SkipComponent
from insights.parsers import ParseException
import pytest
import doctest

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


def test_doc_examples():
    env = {
            'wc_info': WcProc1Mountinfo(context_wrap(WC_PROC_1_MOUNTINFO)),
          }
    failed, total = doctest.testmod(wc_proc_1_mountinfo, globs=env)
    assert failed == 0
