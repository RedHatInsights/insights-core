import os

from insights import add_filter, dr
from insights.core.context import HostContext
from insights.core.spec_factory import simple_file, simple_command, glob_file, SpecSet

here = os.path.abspath(os.path.dirname(__file__))

# hack to find this source file and not the .pyc version of it
this_file = os.path.abspath(__file__).rstrip("c")
with open(this_file) as f:
    file_content = f.read().splitlines()


class Stuff(SpecSet):
    smpl_file = simple_file(this_file)
    many = glob_file(here + "/*.py")
    smpl_cmd = simple_command("/usr/bin/uptime")


stage = dr.new_component_type(executor=dr.broker_executor)


@stage(Stuff.smpl_file, Stuff.many, Stuff.smpl_cmd)
def dostuff(broker):
    assert Stuff.smpl_file in broker
    assert Stuff.many in broker
    assert Stuff.smpl_cmd in broker


def test_spec_factory():
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)


def test_line_terminators():
    add_filter(Stuff.smpl_file, "def test")
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    content = broker[Stuff.smpl_file].content
    assert all(b"def test" in l for l in content), content
    assert not any(l.endswith(b"\n") for l in content)
