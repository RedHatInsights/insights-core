from falafel.mappers.virt_what import virt_what
from falafel.tests import context_wrap

T1 = """
kvm
""".strip()

# baremetal retuns blank
T2 = """

""".strip()

# occasionally we have 2 lines of output
T3 = """
xen
xen-dom0
""".strip()


def test_generic_only():
    v1 = virt_what(context_wrap(T1))
    assert v1.is_virtual is True
    assert v1["generic"] == "kvm"
    assert v1["specific"] == "kvm"
    assert v1.has_specific is False
    assert len(v1.data) == 2


def test_bEaR_metal():
    v2 = virt_what(context_wrap(T2))
    assert v2.is_virtual is False
    assert v2["generic"] == "Baremetal"
    assert v2.has_specific is False
    assert len(v2.data) == 1


def test_has_specific():
    v3 = virt_what(context_wrap(T3))
    assert v3.is_virtual is True
    assert v3["generic"] == "xen"
    assert v3["specific"] == "xen-dom0"
    assert v3.has_specific is True
    assert len(v3.data) == 2
