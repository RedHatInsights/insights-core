import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import open_vm_tools
from insights.parsers.open_vm_tools import OpenVmToolsStatRawTextSession
from insights.tests import context_wrap

V_OUT1 = """
vmware-toolbox-cmd must be run inside a virtual machine.
""".strip()

V_OUT2 = """
test
""".strip()

V_OUT3 = """
session = 4004861987670969122
uptime = 1036293956
version = VMware ESXi 6.0.0 build-12345
provider =
uuid.bios = 00 00 00 00 00 00 66 8e-00 00 00 00 51 1e 23 f3
""".strip()


def test_OpenVmToolsStatRawTextSession():
    with pytest.raises(SkipComponent):
        OpenVmToolsStatRawTextSession(context_wrap(V_OUT1))

    with pytest.raises(SkipComponent):
        OpenVmToolsStatRawTextSession(context_wrap(V_OUT2))

    o1 = OpenVmToolsStatRawTextSession(context_wrap(V_OUT3))
    assert o1['version'] == 'VMware ESXi 6.0.0 build-12345'
    assert o1['provider'] == ''


def test_doc_examples():
    env = {
            'ovmt': OpenVmToolsStatRawTextSession(context_wrap(V_OUT3)),
          }
    failed, total = doctest.testmod(open_vm_tools, globs=env)
    assert failed == 0
