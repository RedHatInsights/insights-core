from insights.parsers.current_clocksource import CurrentClockSource
from insights.tests import context_wrap

CLKSRC = """
tsc
"""


def test_get_current_clksr():
    clksrc = CurrentClockSource(context_wrap(CLKSRC))
    assert clksrc.data == "tsc"
    assert clksrc.is_kvm is False
    assert clksrc.is_vmi_timer != clksrc.is_tsc
