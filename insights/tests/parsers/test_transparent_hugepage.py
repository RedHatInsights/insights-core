import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import transparent_hugepage
from insights.parsers.transparent_hugepage import ThpEnabled, ThpUseZeroPage, ThpShmemEnabled
from insights.tests import context_wrap

ZEROPAGE_0 = "0"
ZEROPAGE_1 = "1"
ZEROPAGE_INVALID = """
bla
ble
asdf


"""

ENABLED_INVALID = """

asdf fda asdfdsaf
"""

ENABLED_MADVISE = """
always [madvise] never
"""

ENABLED_NEVER = """
always madvise [never]
"""

# testing without newlines
ENABLED_ALWAYS = """[always] madvise never"""

THP_SHMEM_ENABLED_ALWAYS = """[always] within_size advise never deny force"""
THP_SHMEM_ENABLED_NEVER = """always within_size advise [never] deny force"""
THP_SHMEM_ENABLED_ENABLE_EMPTY = """always within_size advise [] deny force"""
THP_SHMEM_ENABLED_ENABLE_EMPTY2 = """always within_size advise [ ] deny force"""
THP_SHMEM_ENABLED_ENABLE_EMPTY3 = """always within_size advise deny force"""
THP_SHMEM_ENABLED_EMPTY = """ """


def test_zeropage():
    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_0))
    assert conf is not None
    assert "0" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_1))
    assert conf is not None
    assert "1" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_INVALID))
    assert conf is not None
    assert ZEROPAGE_INVALID.replace("\n", " ").strip() == conf.use_zero_page


def test_enabled():
    conf = ThpEnabled(context_wrap(ENABLED_INVALID))
    assert conf is not None
    assert None is conf.active_option
    assert ENABLED_INVALID.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_MADVISE))
    assert conf is not None
    assert "madvise" == conf.active_option
    assert ENABLED_MADVISE.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_NEVER))
    assert conf is not None
    assert "never" == conf.active_option
    assert ENABLED_NEVER.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_ALWAYS))
    assert conf is not None
    assert "always" == conf.active_option
    assert ENABLED_ALWAYS.strip() == conf.line


def test_thp_shmem_enabled():
    conf = ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_ALWAYS))
    assert conf is not None
    assert "always" == conf.active_option
    assert THP_SHMEM_ENABLED_ALWAYS.strip() == conf.line

    conf = ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_NEVER))
    assert conf is not None
    assert "never" == conf.active_option
    assert THP_SHMEM_ENABLED_NEVER.strip() == conf.line

    conf = ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_ENABLE_EMPTY))
    assert conf is not None
    assert conf.active_option is None
    assert THP_SHMEM_ENABLED_ENABLE_EMPTY.strip() == conf.line

    conf = ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_ENABLE_EMPTY2))
    assert conf is not None
    assert conf.active_option is None
    assert THP_SHMEM_ENABLED_ENABLE_EMPTY2.strip() == conf.line

    conf = ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_ENABLE_EMPTY3))
    assert conf is not None
    assert conf.active_option is None
    assert THP_SHMEM_ENABLED_ENABLE_EMPTY3.strip() == conf.line

    with pytest.raises(ParseException) as e:
        transparent_hugepage.ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_EMPTY))
    assert "Error: " in str(e)


def test_transparent_hugepage_doc_examples():
    env = {
        'thp_use_zero_page': transparent_hugepage.ThpUseZeroPage(context_wrap(ZEROPAGE_0)),
        'thp_enabled': transparent_hugepage.ThpEnabled(context_wrap(ENABLED_MADVISE)),
        'thp_shmem_enabled': transparent_hugepage.ThpShmemEnabled(context_wrap(THP_SHMEM_ENABLED_NEVER)),
    }
    failed, total = doctest.testmod(transparent_hugepage, globs=env)
    assert failed == 0
