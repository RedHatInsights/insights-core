from insights.parsers.virt_what import VirtWhat
from insights.tests import context_wrap

errors = ["virt-what: virt-what-cpuid-helper program not found in $PATH"]


VW_OUT1 = """
kvm
""".strip()

# baremetal retuns blank
VW_OUT2 = """

""".strip()

# occasionally we have more than 1 line of output
VW_OUT3 = """
xen
xen-dom0
aws
""".strip()


def test_kvm():
    v1 = VirtWhat(context_wrap(VW_OUT1))
    assert v1.is_virtual is True
    assert v1.generic == "kvm"
    assert v1.specifics == []
    assert v1.errors == []


def test_bEaR_metal():
    v2 = VirtWhat(context_wrap(VW_OUT2))
    assert v2.is_physical is True
    assert v2.generic == "baremetal"
    assert v2.specifics == []
    assert v2.errors == []


def test_xen():
    v3 = VirtWhat(context_wrap(VW_OUT3))
    assert v3.is_virtual is True
    assert v3.generic == "xen"
    assert "xen-dom0" in v3
    assert "xen" in v3
    assert "aws" in v3
    assert v3.errors == []


def test_error_handling():
    v = VirtWhat(context_wrap(errors[0]))
    assert v.generic == ''
    assert v.specifics == []
    assert v.is_virtual is None
    assert v.is_physical is None
    assert v.errors == errors
