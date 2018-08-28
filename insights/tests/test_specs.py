import os

from insights import add_filter, dr
from insights.core.context import HostContext
from insights.core.plugins import ContentException
from insights.core.spec_factory import simple_file, simple_command, glob_file, SpecSet
import tempfile
import pytest
import glob

here = os.path.abspath(os.path.dirname(__file__))

DATA = """
Some test data
"""
MAX_GLOBS = 1001


# fixture to set up max glob file test
@pytest.fixture
def max_globs():
    for f in range(MAX_GLOBS):
        tmpfile = tempfile.NamedTemporaryFile(prefix='tmp_', suffix='_glob', delete=False)
        tmpfile.close()
        with open(tmpfile.name, 'w') as fd:
            fd.write(DATA)
    yield tempfile.gettempdir()
    for fle in glob.glob1(tempfile.gettempdir(), "tmp_*_glob"):
        os.remove(tempfile.gettempdir() + "/" + fle)


# hack to find this source file and not the .pyc version of it
this_file = os.path.abspath(__file__).rstrip("c")
with open(this_file) as f:
    file_content = f.read().splitlines()


class Stuff(SpecSet):
    smpl_file = simple_file(this_file, filterable=True)
    many = glob_file(here + "/*.py")
    smpl_cmd = simple_command("/usr/bin/uptime")
    smpl_cmd_list_of_lists = simple_command("echo -n ' hello '", filterable=True)


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


@stage(Stuff.smpl_file, Stuff.many, Stuff.smpl_cmd, Stuff.smpl_cmd_list_of_lists)
def dostuff(broker):
    assert Stuff.smpl_file in broker
    assert Stuff.many in broker
    assert Stuff.smpl_cmd in broker
    assert Stuff.smpl_cmd_list_of_lists in broker


def test_spec_factory():
    add_filter(Stuff.smpl_cmd_list_of_lists, " hello ")
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)
    assert "hello" in broker[Stuff.smpl_cmd_list_of_lists].content[0]
    assert len(broker[Stuff.smpl_cmd_list_of_lists].content) == 1


def test_line_terminators():
    add_filter(Stuff.smpl_file, "def test")
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    content = broker[Stuff.smpl_file].content
    assert all("def test" in l for l in content), content
    assert not any(l.endswith("\n") for l in content)


def test_glob_max(max_globs):
    too_many = glob_file(max_globs + "/tmp_*_glob")
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    with pytest.raises(ContentException):
        too_many(broker)
