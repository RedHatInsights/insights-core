# -*- coding: utf-8 -*-
from pytest import mark

from insights.util import posix_regex


@mark.parametrize(("line", "expected"), [
    ("test line what[[:digit:]]?", "test line what[0-9]?"),
    ("test[[:digit:]] line what[[:digit:]]?", "test[0-9] line what[0-9]?"),
    ("test[[:digit:]] line what[[:punct:]]?", r"""test[0-9] line what[!"\#$%&'()*+, \-./:;<=>?@\[ \\\]^_‘{|}~]?"""),
    ("test line[[:ascii:]]what?", r"test line[\x00-\x7F]what?"),
    ("test line what?", "test line what?"),
    ("", ""),
])
def test_replace_posix(line, expected):
    result = posix_regex.replace_posix(line)
    assert r"%s" % result == r"%s" % expected
