import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import max_uid
from insights.parsers.max_uid import MaxUID
from insights.tests import context_wrap


def test_max_uid():
    with pytest.raises(SkipComponent):
        MaxUID(context_wrap(""))

    with pytest.raises(ParseException):
        MaxUID(context_wrap("1a"))

    max_uid = MaxUID(context_wrap("65536"))
    assert max_uid is not None
    assert max_uid.value == 65536


def test_doc_examples():
    env = {
        'max_uid': MaxUID(context_wrap("65534")),
    }
    failed, total = doctest.testmod(max_uid, globs=env)
    assert failed == 0
