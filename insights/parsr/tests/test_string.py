import string
from insights.parsr import InSet, String, DoubleQuotedString, QuotedString


def test_inset():
    assert InSet("abc", "set of abc")("a") == "a"


def test_string():
    sb = String(string.ascii_letters)
    data = "abcde"
    assert sb(data) == "abcde"


def test_quoted_string():
    data = "'abcde'"
    assert QuotedString(data) == "abcde"


def test_escaped_string():
    data = r"""
    "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
    """.strip()
    assert DoubleQuotedString(data)
