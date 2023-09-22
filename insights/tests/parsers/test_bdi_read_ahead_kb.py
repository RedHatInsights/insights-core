import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import bdi_read_ahead_kb
from insights.tests import context_wrap

BDI_READ_AHEAD_KB = """
128
""".strip()

BDI_READ_AHEAD_KB_INVALID = """
invalid
""".strip()


def test_bdi_read_ahead_kb():
    read_ahead_kb = bdi_read_ahead_kb.BDIReadAheadKB(context_wrap(BDI_READ_AHEAD_KB))
    assert read_ahead_kb.read_ahead_kb == 128


def test_invalid_bdi_read_ahead_kb():
    with pytest.raises(ParseException) as e:
        bdi_read_ahead_kb.BDIReadAheadKB(context_wrap(BDI_READ_AHEAD_KB_INVALID))
    assert "Error: " in str(e)


def test_bdi_read_ahead_kb_doc_examples():
    env = {
        'bdi_read_ahead_kb': bdi_read_ahead_kb.BDIReadAheadKB(context_wrap(BDI_READ_AHEAD_KB)),
    }
    failed, total = doctest.testmod(bdi_read_ahead_kb, globs=env)
    assert failed == 0
