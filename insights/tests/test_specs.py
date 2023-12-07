import glob
import os
import pytest
import tempfile

from insights.core import Parser, dr
from insights.core import filters
from insights.core.context import HostContext
from insights.core.exceptions import ContentException
from insights.core.filters import add_filter
from insights.core.spec_factory import (
        DatasourceProvider, RegistryPoint, SpecSet,
        glob_file, simple_command, simple_file, first_of)

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


class Specs(SpecSet):
    many = RegistryPoint(multi_output=True)
    no_such_cmd = RegistryPoint()
    no_such_file = RegistryPoint()
    smpl_cmd = RegistryPoint()
    smpl_cmd_list_of_lists = RegistryPoint(filterable=True)
    smpl_file = RegistryPoint()
    smpl_file_w_filter = RegistryPoint(filterable=True)
    first_of_spec = RegistryPoint(filterable=True)


class Stuff(Specs):
    many = glob_file(here + "/*.py")
    no_such_cmd = simple_command("/usr/bin/no_such_cmd args")
    no_such_file = simple_file("/no/such/_file")
    smpl_cmd = simple_command("/usr/bin/uptime")
    smpl_cmd_list_of_lists = simple_command("echo -n ' hello '")
    smpl_file = simple_file(this_file)
    smpl_file_w_filter = simple_file(this_file)
    first_of_spec = first_of([
        simple_command("echo -n ' hello '"),
        simple_file(this_file)
    ])


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)

#
# TEST
#


def teardown_function(func):
    filters._CACHE = {}

    if func in [test_spec_factory, test_line_terminators]:
        del filters.FILTERS[Stuff.smpl_file_w_filter]
        del filters.FILTERS[Stuff.first_of_spec]


@stage(Stuff.smpl_file, Stuff.smpl_file_w_filter, Stuff.many, Stuff.smpl_cmd,
       Stuff.smpl_cmd_list_of_lists, Stuff.first_of_spec,
       optional=[Stuff.no_such_cmd, Stuff.no_such_file])
def dostuff(broker):
    assert Stuff.smpl_file in broker
    assert Stuff.smpl_file_w_filter in broker
    assert Stuff.many in broker
    assert Stuff.smpl_cmd in broker
    assert Stuff.smpl_cmd_list_of_lists in broker
    assert Stuff.no_such_cmd not in broker
    assert Stuff.no_such_file not in broker
    assert Stuff.first_of_spec in broker


def test_spec_factory():
    add_filter(Stuff.smpl_cmd_list_of_lists, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_of_spec, [" hello ", "def test"])
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)
    assert "hello" in broker[Stuff.smpl_cmd_list_of_lists].content[0]
    assert len(broker[Stuff.smpl_cmd_list_of_lists].content) == 1
    assert len(broker[Stuff.first_of_spec].content) == 1
    assert len(broker.exceptions) == 2
    for exp in broker.exceptions:
        if "no_such" in str(exp):
            assert "args" not in str(exp)
        else:
            assert "/no/such" not in str(exp)
    assert len(broker.tracebacks) == 2


def test_line_terminators():
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_of_spec, [" hello ", "def test"])
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    content = broker[Stuff.smpl_file_w_filter].content
    assert all("def test" in l for l in content), content
    assert not any(l.endswith("\n") for l in content)

    content = broker[Stuff.first_of_spec].content
    assert len(broker[Stuff.first_of_spec].content) == 1


def test_glob_max(max_globs):
    too_many = glob_file(max_globs + "/tmp_*_glob")
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    with pytest.raises(ContentException):
        too_many(broker)


def test_datasource_provider():
    data = "blahblah\nblahblah2"

    class MyParser(Parser):
        def parse_content(self, content):
            self.content = content

    ds = DatasourceProvider(data, relative_path="things")
    p = MyParser(ds)
    assert p.content == data.splitlines()
    assert list(ds.stream()) == data.splitlines()


def test_exp_no_filters():
    hn = HostContext()
    broker = dr.Broker()
    broker[HostContext] = hn
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff not in broker
    exception_cnt = 0
    for spec, info in broker.exceptions.items():
        if any("due to" in str(msg) for msg in info):
            if "smpl_file_w_filter" in str(spec):
                exception_cnt += 1
            elif "first_of_spec" in str(spec):
                exception_cnt += 10
    assert exception_cnt == 11
