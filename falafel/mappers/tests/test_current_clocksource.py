from falafel.mappers import current_clocksource
from falafel.tests import context_wrap

CLKSRC = """
tsc
"""

def test_get_current_clksr():
    clksrc = current_clocksource.get_current_clksrc(context_wrap(CLKSRC))
    assert clksrc == "tsc"
