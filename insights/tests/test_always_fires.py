from insights.core.plugins import make_pass
from insights.tests import InputData, run_test

from insights.plugins import always_fires


def test_always_fires():
    i = InputData()
    expected = make_pass("ALWAYS_FIRES", kernel="this is junk")
    run_test(always_fires.report, i, expected)
