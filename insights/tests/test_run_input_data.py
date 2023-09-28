import pytest

from insights.core.plugins import component
from insights.core.exceptions import SkipComponent
from insights.tests import InputData
from insights.tests import run_input_data


@component()
def some_component():
    raise SkipComponent


@pytest.mark.parametrize(
    "store_skips, exceptions_count",
    ((False, 0), (True, 1)),
)
def test_store_skips_false(store_skips, exceptions_count):
    broker = run_input_data(some_component, InputData(), store_skips=store_skips)
    assert len(broker.exceptions) == exceptions_count
