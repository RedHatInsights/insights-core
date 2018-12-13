""" Test the query tool. """
import inspect

from insights import dr
from insights.tests import InputData
from insights.tools.query import load_obj, get_source, get_pydoc


def test_load_obj():
    assert load_obj("insights.dr") is dr
    assert load_obj("insights.tests.InputData") is InputData
    assert load_obj("foo.bar") is None


def test_get_source():
    assert get_source("insights.dr") == inspect.getsource(dr)
    assert get_source("insights.tests.InputData") == inspect.getsource(InputData)
    assert get_source("foo.bar") is None


def test_get_pydoc():
    assert get_pydoc("insights.dr") is not None
    assert get_pydoc("insights.tests.InputData") is not None
    assert get_pydoc("foo.bar") is None
