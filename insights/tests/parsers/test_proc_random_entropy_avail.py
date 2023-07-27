import doctest
import pytest

from insights.tests import context_wrap
from insights.parsers import proc_random_entropy_avail
from insights.core.exceptions import SkipComponent

ENTROPY_CONTENT = """3137"""

WRONG_CONTENT_1 = ""

WRONG_CONTENT_2 = """
abc
def
""".strip()


def test_duplicate_id():
    entropy_obj = proc_random_entropy_avail.RandomEntropyAvail(context_wrap(ENTROPY_CONTENT))
    assert entropy_obj.avail_entropy == 3137


def test_exception():
    with pytest.raises(SkipComponent):
        proc_random_entropy_avail.RandomEntropyAvail(context_wrap(WRONG_CONTENT_1))

    with pytest.raises(SkipComponent):
        proc_random_entropy_avail.RandomEntropyAvail(context_wrap(WRONG_CONTENT_2))


def test_doc():
    random_entropy_obj = proc_random_entropy_avail.RandomEntropyAvail(context_wrap(ENTROPY_CONTENT))
    env = {'random_entropy_obj': random_entropy_obj}
    failed, total = doctest.testmod(proc_random_entropy_avail, globs=env)
    assert failed == 0
