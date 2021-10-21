import pytest

from insights import SkipComponent
from insights.combiners.virt_what import VirtWhat
from insights.components.virtualization import IsBareMetal
from insights.parsers.virt_what import VirtWhat as VWP
from insights.tests import context_wrap


def test_is_bare_metal():
    virt_what = VirtWhat(None, VWP(context_wrap("")))
    result = IsBareMetal(virt_what)
    assert isinstance(result, IsBareMetal)

    virt_what = VirtWhat(None, VWP(context_wrap("kvm")))
    with pytest.raises(SkipComponent):
        IsBareMetal(virt_what)
