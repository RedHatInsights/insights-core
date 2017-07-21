import platform
import os

from insights.core import dr
from insights.core.context import HostContext
from insights.core.spec_factory import SpecFactory

here = os.path.abspath(os.path.dirname(__file__))

sf = SpecFactory(__name__)
this_file = os.path.abspath(__file__)
with open(this_file) as f:
    file_content = [l.rstrip() for l in f.readlines()]


smpl_file = sf.simple_file(this_file)
many = sf.glob_file(here + "/*.py")
smpl_cmd = sf.simple_command("/usr/bin/uptime")
ethernet_interfaces = sf.listdir("/sys/class/net")
ethtool = ethtool = sf.with_args_from(ethernet_interfaces, "ethtool %s")

stage = dr.new_component_type()


@stage(requires=[smpl_file, many, smpl_cmd, ethtool])
def dostuff(broker):
    assert smpl_file in broker
    assert many in broker
    assert smpl_cmd in broker
    assert ethernet_interfaces in broker
    assert ethtool in broker
    assert len(broker[ethtool]) == len(broker[ethernet_interfaces])


def test_spec_factory():
    hn = HostContext(platform.node())
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff in broker
    assert broker[smpl_file].content == file_content
