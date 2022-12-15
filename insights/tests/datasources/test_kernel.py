import pytest
from insights.specs.datasources.kernel import current_version
from insights.parsers.uname import Uname
from insights.parsers import uname
from insights.tests import context_wrap

UNAME = """
Linux vm37-130.gsslab.pek2.redhat.com 5.14.0-160.el9.x86_64 #1 SMP PREEMPT_DYNAMIC Thu Aug 25 20:41:37 EDT 2022 x86_64 x86_64 x86_64 GNU/Linux
"""

UNAME_ERROR_BLANK = ""


def test_current_kernel_version():
    uname = Uname(context_wrap(UNAME))

    broker = {
        Uname: uname
    }
    result = current_version(broker)
    assert result is not None
    assert result == '5.14.0-160.el9.x86_64'


def test_current_kernel_version_without_uname():
    with pytest.raises(uname.UnameError) as e_info:
        current_version({Uname: uname.Uname(context_wrap(UNAME_ERROR_BLANK))})
    assert 'Empty uname line' in str(e_info.value)
