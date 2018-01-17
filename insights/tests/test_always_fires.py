from insights.core.plugins import make_response
from insights.tests import InputData, run_test

from insights.plugins import always_fires


def test_always_fires():
    i = InputData()
    expected = make_response("ALWAYS_FIRES", kernel="this is junk")
    run_test(always_fires.report, i, expected)
