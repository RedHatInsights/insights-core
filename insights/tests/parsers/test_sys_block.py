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

FILE_PATH_SDA = "/sys/block/sda/queue/scheduler"


def test_stable_writes():
    res = sys_block.StableWrites(context_wrap(STABLE_WRITES, FILE_PATH_SDA))
    assert res.stable_writes == 1
    assert res.device == 'sda'


def test_invalid_stable_writes():
    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(STABLE_WRITES_INVALID, FILE_PATH_SDA))
    assert "Error: " in str(e)

    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(STABLE_WRITES_EMPTY))
    assert "Error: " in str(e)


def test_stable_writes_doc_examples():
    env = {
        'block_stable_writes': sys_block.StableWrites(context_wrap(STABLE_WRITES, FILE_PATH_SDA)),
    }
    failed, total = doctest.testmod(sys_block, globs=env)
    assert failed == 0
