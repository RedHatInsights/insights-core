import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.kernel import current_version, default_version
from insights.parsers.uname import Uname
from insights.parsers import uname
from insights.specs import Specs
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


def test_default_version():
    grubby_command = Mock()
    grubby_command.content = ['/boot/vmlinuz-4.18.0-305.el8.x86_64']
    broker = {Specs.grubby_default_kernel: grubby_command}
    result = default_version(broker)
    assert result is not None
    assert result == '4.18.0-305.el8.x86_64'


def test_default_version_with_error():
    grubby_command = Mock()
    grubby_command.content = ['grep: /boot/grub2/grubenv: Permission denied']
    broker = {Specs.grubby_default_kernel: grubby_command}
    with pytest.raises(SkipComponent):
        default_version(broker)
