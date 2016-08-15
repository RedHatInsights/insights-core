from falafel.mappers.current_clocksource import CurrentClockSource
from falafel.tests import context_wrap

CLKSRC = """
tsc
"""


def test_get_current_clksr():
    clksrc = CurrentClockSource.parse_context(context_wrap(CLKSRC))
    assert clksrc.data == "tsc"
