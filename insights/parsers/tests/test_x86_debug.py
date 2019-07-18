from insights.parsers import SkipException
from insights.parsers import ParseException
from insights.parsers import x86_debug
from insights.parsers.x86_debug import X86IBPBEnabled
from insights.parsers.x86_debug import X86PTIEnabled
from insights.parsers.x86_debug import X86IBRSEnabled
from insights.parsers.x86_debug import X86RETPEnabled
from insights.tests import context_wrap
import pytest
import doctest

X86_DEBUG_INPUT = '1'


def test_x86_enabled():
    ibpb = X86IBPBEnabled(context_wrap(X86_DEBUG_INPUT))
    pti = X86PTIEnabled(context_wrap(X86_DEBUG_INPUT))
    ibrs = X86IBRSEnabled(context_wrap(X86_DEBUG_INPUT))
    retp = X86RETPEnabled(context_wrap(X86_DEBUG_INPUT))
    assert ibpb.value == 1
    assert pti.value == 1
    assert ibrs.value == 1
    assert retp.value == 1
    assert isinstance(ibpb.value, int)
    assert isinstance(pti.value, int)
    assert isinstance(ibrs.value, int)
    assert isinstance(retp.value, int)


def test_x86_enabled_documentation():
    """
    Here we test the examples in the documentation automatically using
    doctest.  We set up an environment which is similar to what a rule
    writer might see - a '/sys/kernel/debug/x86/*_enabled' output
    that has been passed in as a parameter to the rule declaration.
    """
    env1 = {'dval': X86IBPBEnabled(context_wrap(X86_DEBUG_INPUT))}
    env2 = {'dval': X86PTIEnabled(context_wrap(X86_DEBUG_INPUT))}
    env3 = {'dval': X86IBRSEnabled(context_wrap(X86_DEBUG_INPUT))}
    env4 = {'dval': X86RETPEnabled(context_wrap(X86_DEBUG_INPUT))}
    failed1, total1 = doctest.testmod(x86_debug, globs=env1)
    failed2, total2 = doctest.testmod(x86_debug, globs=env2)
    failed3, total3 = doctest.testmod(x86_debug, globs=env3)
    failed4, total4 = doctest.testmod(x86_debug, globs=env4)
    assert failed1 == 0
    assert failed2 == 0
    assert failed3 == 0
    assert failed4 == 0


def test_x86_enabled_exp():
    """
    Here test the examples cause expections
    """
    # ibpb
    with pytest.raises(SkipException) as sc1:
        X86IBPBEnabled(context_wrap(""))
    assert "Input content is empty" in str(sc1)

    with pytest.raises(ParseException) as sc1:
        X86IBPBEnabled(context_wrap("ERROR"))
    assert "No useful data parsed in content" in str(sc1)

    # pti
    with pytest.raises(SkipException) as sc2:
        X86PTIEnabled(context_wrap(""))
    assert "Input content is empty" in str(sc2)

    with pytest.raises(ParseException) as sc2:
        X86IBPBEnabled(context_wrap("ERROR"))
    assert "No useful data parsed in content" in str(sc2)

    # ibrs
    with pytest.raises(SkipException) as sc3:
        X86IBRSEnabled(context_wrap(""))
    assert "Input content is empty" in str(sc3)

    with pytest.raises(ParseException) as sc3:
        X86IBRSEnabled(context_wrap("ERROR"))
    assert "No useful data parsed in content" in str(sc3)

    # retp
    with pytest.raises(SkipException) as sc4:
        X86RETPEnabled(context_wrap(""))
    assert "Input content is empty" in str(sc4)

    with pytest.raises(ParseException) as sc4:
        X86RETPEnabled(context_wrap("ERROR"))
    assert "No useful data parsed in content" in str(sc4)
