import pytest
import doctest
from insights.parsers import grubby
from insights.parsers.grubby import GrubbyDefaultIndex, GrubbyDefaultKernel
from insights.tests import context_wrap
from insights.parsers import SkipException, ParseException

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


def test_grubby_default_index():
    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    assert res.default_index == 0

    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    assert res.default_index == 1


def test_grubby_default_index_ab():
    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultIndex(context_wrap(ABDEFAULT_INDEX_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_AB))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel_ab():
    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_EMPTY))
    assert 'Empty output' in str(excinfo.value)

    with pytest.raises(ParseException) as excinfo:
        GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL_AB))
    assert 'Invalid output:' in str(excinfo.value)


def test_grubby_default_kernel():
    res = GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL))
    assert res.default_kernel == DEFAULT_KERNEL


def test_doc_examples():
    env = {
            'grubby_default_index': GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1)),
            'grubby_default_kernel': GrubbyDefaultKernel(context_wrap(DEFAULT_KERNEL)),
          }
    failed, total = doctest.testmod(grubby, globs=env)
    assert failed == 0
