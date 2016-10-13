from falafel.mappers.virt_what import VirtWhat
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
    v1 = VirtWhat(context_wrap(T1))
    assert v1.is_virtual is True
    assert v1.generic == "kvm"
    assert v1.specific == "kvm"
    assert v1.has_specific is False


def test_bEaR_metal():
    v2 = VirtWhat(context_wrap(T2))
    assert v2.is_virtual is False
    assert v2.generic == "Baremetal"
    assert v2.has_specific is False


def test_has_specific():
    v3 = VirtWhat(context_wrap(T3))
    assert v3.is_virtual is True
    assert v3.generic == "xen"
    assert v3.specific == "xen-dom0"
    assert v3.has_specific is True
