import pytest
from insights.parsers.grubby import GrubbyDefaultIndex
from insights.tests import context_wrap
from insights.parsers import SkipException

DEFAULT_INDEX_1 = '0'
DEFAULT_INDEX_2 = '1'
DEFAULT_INDEX_3 = ''
DEFAULT_INDEX_4 = '-2'


def test_grub2_default_index_1():
    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_1))
    assert res.default_index == 0

    res = GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_2))
    assert res.default_index == 1


def test_grub2_default_index_2():
    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_3))
        assert 'Invalid default index value.' in str(excinfo.value)

    with pytest.raises(SkipException) as excinfo:
        GrubbyDefaultIndex(context_wrap(DEFAULT_INDEX_4))
        assert 'Invalid default index value.' in str(excinfo.value)
