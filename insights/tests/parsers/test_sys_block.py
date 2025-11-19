import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import sys_block
from insights.tests import context_wrap

STABLE_WRITES = """
1
""".strip()

CONTENT_INVALID = """
invalid
""".strip()

CONTENT_EMPTY = """
""".strip()

MAX_SEGMENT_SIZE = """
4294967295
""".strip()

FILE_PATH_SDA = "/sys/block/sda/queue/scheduler"
MAX_SEGMENT_SIZE_PATH_SDA = "/sys/block/sda/queue/max_segment_size"
SPECIAL_DEVICE_PATH = "/sys/block/sd@!$/queue/max_segment_size"


def test_stable_writes():
    res = sys_block.StableWrites(context_wrap(STABLE_WRITES, FILE_PATH_SDA))
    assert res.stable_writes == 1
    assert res.device == 'sda'


def test_invalid_stable_writes():
    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(CONTENT_INVALID, FILE_PATH_SDA))
    assert "Error: " in str(e)

    with pytest.raises(ParseException) as e:
        sys_block.StableWrites(context_wrap(CONTENT_EMPTY))
    assert "Error: " in str(e)


def test_max_segment_size():
    res = sys_block.MaxSegmentSize(context_wrap(MAX_SEGMENT_SIZE, MAX_SEGMENT_SIZE_PATH_SDA))
    assert res.max_segment_size == 4294967295
    assert res.device == 'sda'

    res_special = sys_block.MaxSegmentSize(context_wrap(MAX_SEGMENT_SIZE, SPECIAL_DEVICE_PATH))
    assert res_special.max_segment_size == 4294967295
    assert res_special.device == 'sd@!$'


def test_invalid_max_segment_size():
    with pytest.raises(ParseException) as e:
        sys_block.MaxSegmentSize(context_wrap(CONTENT_INVALID, MAX_SEGMENT_SIZE_PATH_SDA))
    assert "Error: " in str(e)

    with pytest.raises(ParseException) as e:
        sys_block.MaxSegmentSize(context_wrap(CONTENT_EMPTY))
    assert "Error: " in str(e)


def test_stable_writes_doc_examples():
    env = {
        'block_stable_writes': sys_block.StableWrites(context_wrap(STABLE_WRITES, FILE_PATH_SDA)),
        'max_segment_size': sys_block.MaxSegmentSize(context_wrap(MAX_SEGMENT_SIZE, MAX_SEGMENT_SIZE_PATH_SDA)),
    }
    failed, total = doctest.testmod(sys_block, globs=env)
    assert failed == 0
