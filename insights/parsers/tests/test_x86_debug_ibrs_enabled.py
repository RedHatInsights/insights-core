from insights.parsers import SkipException
from insights.parsers import ParseException
from insights.parsers import x86_debug_ibrs_enabled
from insights.parsers.x86_debug_ibrs_enabled import X86IBRSEnabled
from insights.tests import context_wrap
import pytest
import doctest

X86_DEBUG_INPUT1 = '1'
X86_DEBUG_INPUT2 = '0'
X86_DEBUG_INPUT_INVALID1 = 'abdjes'
X86_DEBUG_INPUT_INVALID2 = '-765'
X86_DEBUG_INPUT_INVALID2 = ''


def test_x86_ibrs_enabled():
    result = X86IBRSEnabled(context_wrap(X86_DEBUG_INPUT1))
    assert result.value == 1
    assert isinstance(result.value, int)


def test_x86_ibrs_enabled_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/sys/kernel/debug/x86/ibrs_enabled' output
    that has been passed in as a parameter to the rule declaration.
    """
    env = {'dval': X86IBRSEnabled(context_wrap(X86_DEBUG_INPUT1))}
    failed, total = doctest.testmod(x86_debug_ibrs_enabled, globs=env)
    assert failed == 0


def test_x86_ibrs_enabled_exp():
    """
    Here test the examples cause expections
    """

    with pytest.raises(SkipException) as sc:
        X86IBRSEnabled(context_wrap(""))
    assert "Input content is empty" in str(sc)

    with pytest.raises(ParseException) as sc:
        X86IBRSEnabled(context_wrap("ERROR"))
    assert "No useful data parsed in content" in str(sc)
