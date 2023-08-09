import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import grubby
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyDefaultKernel
from insights.tests import context_wrap

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '1'
ABDEFAULT_INDEX_EMPTY = ''
DEFAULT_INDEX_AB = '-2'

DEFAULT_KERNEL = "/boot/vmlinuz-2.6.32-573.el6.x86_64"
DEFAULT_KERNEL_EMPTY = ""
DEFAULT_KERNEL_AB = """
/boot/vmlinuz-2.6.32-573.el6.x86_64"
/boot/vmlinuz-2.6.32-573.el6.x86_64"
""".strip()
DEFAULT_KERNEL_INVALID = 'rpm-sort: Invalid input'
DEFAULT_KERNEL_INVALID_2 = 'rpm-sort: Invalid input '
DEFAULT_KERNEL_INVALID_3 = """
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
""".strip()

DEFAULT_KERNEL_WITH_ERRORS_MSGS_1 = """
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/usr/libexec/grubby/grubby-bls: fork: retry: Resource temporarily unavailable
/boot/vmlinuz-4.18.0-147.5.1.el8_1.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_2 = """
grub2-editenv: error: cannot rename the file /boot/grub2/grubenv.new to /boot/grub2/grubenv: No such file or directory.
/boot/vmlinuz-3.10.0-862.el7.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_3 = """
grep: /boot/grub2/grubenv: No such file or directory
/boot/cm/images/dell-rhel8.2/boot/vmlinuz-4.18.0-348.23.1.el8_5.x86_64
""".strip()
DEFAULT_KERNEL_WITH_ERRORS_MSGS_4 = """
/etc/os-release: line 5: VERSION_ID-Peter=8.7: command not found
/etc/os-release: line 6: PLATFORM_ID-Peter=platform:el8: command not found
/boot/vmlinuz-4.18.0-425.10.1.el8_7.x86_64
""".strip()


def test_grubby_default_index():
    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    assert res.default_index == 0

    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    assert res.default_index == 1


def test_grubby_default_index_ab():
    with pytest.raises(SkipComponent) as excinfo:
        GrubbyDefaultIndex(context_wrap(ABDEFAULT_INDEX_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_AB))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel():
    res = GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL))
    assert res.default_kernel == DEFAULT_KERNEL

    content_with_error_msgs = [
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_1,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_2,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_3,
        DEFAULT_KERNEL_WITH_ERRORS_MSGS_4,
    ]
    for content in content_with_error_msgs:
        this_res = GrubbyDefaultKernel(context_wrap(content))
        assert this_res.default_kernel == content.split()[-1].strip()


def test_grubby_default_kernel_ab():
    with pytest.raises(SkipComponent) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_AB))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID_2))
    assert 'Invalid output:' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_INVALID_3))
    assert 'Invalid output:' in str(excinfo.value)


def test_doc_examples():
    env = {
            'grubby_default_index': GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1)),
            'grubby_default_kernel': GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL)),
          }
    failed, total = doctest.testmod(grubby, globs=env)
    assert failed == 0
