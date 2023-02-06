import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import vma_ra_enabled_s390x
from insights.parsers.vma_ra_enabled_s390x import VmaRaEnabledS390x
from insights.tests import context_wrap

INPUT_VMA_1 = """
True
""".strip()

INPUT_VMA_2 = """
False
""".strip()


def test_vma_ra_enabled_s390x():
    sp1 = VmaRaEnabledS390x(context_wrap(INPUT_VMA_1))
    sp2 = VmaRaEnabledS390x(context_wrap(INPUT_VMA_2))
    assert sp1.ra_enabled is True
    assert sp2.ra_enabled is False


def test_vma_ra_enabled_s390x_exp():
    """
    Here test the examples cause expections
    """
    with pytest.raises(SkipComponent) as sc1:
        VmaRaEnabledS390x(context_wrap(''))
    assert "Input content is empty" in str(sc1)


def test_vma_ra_enabled_s390x__documentation():
    """
    Here we test the examples in the documentation automatically using doctest.
    We set up an environment which is similar to what a rule writer might see -
    a '/sys/kernel/mm/swap/vma_ra_enabled' output that has been passed in as a
    parameter to the rule declaration.
    """
    env = {'vma': VmaRaEnabledS390x(context_wrap(INPUT_VMA_1))}

    failed, total = doctest.testmod(vma_ra_enabled_s390x, globs=env)
    assert failed == 0
