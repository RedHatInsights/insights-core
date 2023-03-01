import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import sys_block
from insights.tests import context_wrap

STABLE_WRITES = """
1
""".strip()

STABLE_WRITES_INVALID = """
invalid
""".strip()

STABLE_WRITES_EMPTY = """
""".strip()


def test_stable_writes():
    res = sys_block.StableWrites(context_wrap(STABLE_WRITES))
    assert res.stable_writes == 1


def test_invalid_stable_writes():
    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(STABLE_WRITES_INVALID))
    assert "Error: " in str(e)

    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(STABLE_WRITES_EMPTY))
    assert "Error: " in str(e)


def test_stable_writes_doc_examples():
    env = {
        'block_stable_writes': sys_block.StableWrites(context_wrap(STABLE_WRITES)),
    }
    failed, total = doctest.testmod(sys_block, globs=env)
    assert failed == 0
