import doctest
from insights.parsers import hexdump
from insights.parsers.hexdump import HexDump
from insights.tests import context_wrap


CONTENT_HEXDUMP = """
00000000  01 00 00 00                                       |....|
00000004
""".strip()


def test_doc_examples():
    env = {'hex_dump': HexDump(context_wrap(CONTENT_HEXDUMP))}
    failed, total = doctest.testmod(hexdump, globs=env)
    assert failed == 0


def test_HexDump():
    d = HexDump(context_wrap(CONTENT_HEXDUMP))
    assert len(d.data) == 2
    assert d.data[0] == '00000000  01 00 00 00                                       |....|'
    assert d.data[1] == '00000004'
    assert d.hex_value == '00 00 00 01'
    assert d.dec_value == 1
