import glob
import os
import json
import pytest
import tempfile

from collections import defaultdict
from mock.mock import patch, Mock

from insights import collect
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core import Parser, dr
from insights.core import filters
from insights.core.context import HostContext
from insights.core.exceptions import ContentException
from insights.core.filters import add_filter
from insights.core.plugins import datasource
from insights.core.spec_cleaner import Cleaner
from insights.core.spec_factory import (
        DatasourceProvider, RegistryPoint, SpecSet,
        foreach_collect, foreach_execute,
        glob_file, simple_command, simple_file, first_file, first_of)

here = os.path.abspath(os.path.dirname(__file__))

DATA = """
Some test data
"""
MAX_GLOBS = 1001

this_file = os.path.abspath(__file__).rstrip("c")

test_empty_file = '/tmp/_insights_test.empty_file'
test_empty_after_filter = '/tmp/_insights_test.empty_after_filter'
test_empty_after_redact = '/tmp/_insights_test.empty_after_redact'

specs_manifest = """
---
version: 0

client:
    context:
        class: insights.core.context.HostContext
        args:
            timeout: 5

    # commands and files to ignore
    blacklist:
        files: []
        commands: []
        patterns: ['TeSt_']
        keywords: []

    persist:
        - name: insights.tests.test_specs.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.test_specs

    configs:
        - name: insights.core.spec_factory
          enabled: true
        - name: insights.tests.test_specs.Specs
          enabled: true
        - name: insights.tests.test_specs.Stuff
          enabled: true
        - name: insights.tests.test_specs.dostuff
          enabled: true
""".strip()


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


class Specs(SpecSet):
    many_glob = RegistryPoint(multi_output=True, no_redact=True)
    many_foreach_exe = RegistryPoint(multi_output=True)
    many_foreach_clc = RegistryPoint(multi_output=True)
    smpl_cmd = RegistryPoint()
    smpl_cmd_w_filter = RegistryPoint(filterable=True)
    smpl_file = RegistryPoint()
    smpl_file_w_filter = RegistryPoint(filterable=True)
    first_file_spec_w_filter = RegistryPoint(filterable=True)
    first_of_spec_w_filter = RegistryPoint(filterable=True)
    no_such_cmd = RegistryPoint()
    no_such_file = RegistryPoint()
    empty_orig = RegistryPoint()
    empty_after_filter = RegistryPoint(filterable=True)
    empty_after_redact = RegistryPoint()


class Stuff(Specs):
    many_glob = glob_file(here + "/test*.py")

    @datasource(HostContext)
    def files(broker):
        """ Return a list of directories from the spec filter """
        return [here + "/__init__.py", here + "/integration.py"]

    many_foreach_exe = foreach_execute(files, 'ls %s')
    many_foreach_clc = foreach_collect(files, "%s", no_redact=True)
    smpl_cmd = simple_command("/usr/bin/uptime")
    smpl_cmd_w_filter = simple_command("echo -n ' hello 1'")
    smpl_file = simple_file(here + "/helpers.py")
    smpl_file_w_filter = simple_file(here + "/mock_web_server.py")
    first_file_spec_w_filter = first_file([here + "/spec_tests.py", "/etc/os-release"])
    first_of_spec_w_filter = first_of(
        [
            simple_command("echo -n ' hello 1'"),
            simple_file(this_file),
        ]
    )
    no_such_cmd = simple_command("/usr/bin/no_such_cmd args")
    no_such_file = simple_file("/no/such/_file")

    empty_orig = simple_file(test_empty_file)
    empty_after_filter = simple_file(test_empty_after_filter)
    empty_after_redact = simple_file(test_empty_after_redact)


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


@stage(
    Stuff.many_glob,
    Stuff.many_foreach_exe,
    Stuff.many_foreach_clc,
    Stuff.smpl_cmd,
    Stuff.smpl_cmd_w_filter,
    Stuff.smpl_file,
    Stuff.smpl_file_w_filter,
    Stuff.first_file_spec_w_filter,
    Stuff.first_of_spec_w_filter,
    optional=[Stuff.no_such_cmd,
              Stuff.empty_orig,
              Stuff.empty_after_filter,
              Stuff.empty_after_redact,
              Stuff.no_such_file, ])
def dostuff(broker):
    assert Stuff.many_glob in broker
    assert Stuff.many_foreach_exe in broker
    assert Stuff.many_foreach_clc in broker
    assert Stuff.smpl_cmd in broker
    assert Stuff.smpl_cmd_w_filter in broker
    assert Stuff.smpl_file in broker
    assert Stuff.smpl_file_w_filter in broker
    assert Stuff.first_file_spec_w_filter in broker
    assert Stuff.first_of_spec_w_filter in broker

    assert Stuff.empty_orig not in broker
    assert Stuff.empty_after_filter not in broker
    assert Stuff.empty_after_redact not in broker
    assert Stuff.no_such_cmd not in broker
    assert Stuff.no_such_file not in broker


# File content
with open(here + "/helpers.py") as f:
    smpl_file_content = f.read().splitlines()
with open(here + "/mock_web_server.py") as f:
    smpl_file_w_filter_content = [l for l in f.read().splitlines() if "def get" in l]
with open(here + "/spec_tests.py") as f:
    first_file_w_filter_content = [l for l in f.read().splitlines() if any(i in l for i in ["def report_", "rhel"])]

#
# TEST
#


def setup_function(func):
    if func == test_specs_collect:
        # empty relevant files
        open(test_empty_file, 'a').close()
        with open(test_empty_after_filter, 'w') as t:
            t.write('no-filter')
        with open(test_empty_after_redact, 'w') as t:
            t.write('TeSt_')


def teardown_function(func):
    filters._CACHE = {}

    if func in [test_spec_factory, test_specs_collect, test_line_terminators]:
        del filters.FILTERS[Stuff.smpl_cmd_w_filter]
        del filters.FILTERS[Stuff.smpl_file_w_filter]
        del filters.FILTERS[Stuff.first_file_spec_w_filter]
        del filters.FILTERS[Stuff.first_of_spec_w_filter]

    if func == test_specs_collect:
        os.remove(test_empty_file)
        os.remove(test_empty_after_filter)
        os.remove(test_empty_after_redact)


def test_spec_factory():
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, ["def report_", "rhel"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == smpl_file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)
    # "filter" works when loading
    assert "hello" in broker[Stuff.smpl_cmd_w_filter].content[0]
    assert len(broker[Stuff.smpl_cmd_w_filter].content) == 1
    assert broker[Stuff.smpl_file_w_filter].content == smpl_file_w_filter_content
    assert broker[Stuff.first_file_spec_w_filter].content == first_file_w_filter_content
    assert len(broker[Stuff.first_of_spec_w_filter].content) == 1
    assert len(broker.exceptions) == 5
    for exp in broker.exceptions:
        if "no_such" in str(exp):
            assert "args" not in str(exp)
        else:
            assert "/no/such" not in str(exp)
    assert len(broker.tracebacks) == 5


def test_line_terminators():
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, ["def report_", "rhel"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    content = broker[Stuff.smpl_file_w_filter].content
    assert not any(l.endswith("\n") for l in content)
    # "filter" works only when writing
    # assert all("def get" in l for l in content), content
    assert "hello" in broker[Stuff.smpl_cmd_w_filter].content[0]
    assert len(broker[Stuff.smpl_cmd_w_filter].content) == 1
    assert len(broker[Stuff.smpl_file_w_filter].content) == len(smpl_file_w_filter_content)
    assert len(broker[Stuff.first_file_spec_w_filter].content) == len(first_file_w_filter_content)
    assert len(broker[Stuff.first_of_spec_w_filter].content) == 1


def test_glob_max(max_globs):
    too_many = glob_file(max_globs + "/tmp_*_glob")
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
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
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    assert dostuff not in broker
    exception_cnt = 0
    for spec, info in broker.exceptions.items():
        # warning of lacking filters
        if any("due to" in str(msg) for msg in info):
            if "smpl_file_w_filter" in str(spec):
                exception_cnt += 1
            elif "smpl_cmd_w_filter" in str(spec):
                exception_cnt += 10
            elif "first_file_spec_w_filter" in str(spec):
                exception_cnt += 100
            elif "first_of_spec_w_filter" in str(spec):
                exception_cnt += 1000
    assert exception_cnt == 1111


@pytest.mark.parametrize("obfuscate", [True, False])
@patch('insights.core.spec_cleaner.Cleaner.generate_report', Mock())
def test_specs_collect(obfuscate):
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, [" hello ", "Test"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    # Preparation
    manifest = collect.load_manifest(specs_manifest)
    for pkg in manifest.get("plugins", {}).get("packages", []):
        dr.load_components(pkg, exclude=None)
    # For verifying convenience, test obfuscate=False only
    conf = InsightsConfig(
            obfuscate=obfuscate, obfuscate_hostname=obfuscate,
            manifest=manifest)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()
    output_path, errors = collect.collect(
            tmp_path=arch.tmp_dir,
            archive_name=arch.archive_name,
            client_config=conf)
    meta_data_root = os.path.join(output_path, 'meta_data')
    data_root = os.path.join(output_path, 'data')

    assert not errors
    count = 0
    for spec in Specs.__dict__:
        if not spec.startswith(('__', 'context_handlers', 'registry')):
            file_name = "insights.tests.test_specs.Specs.{0}.json".format(spec)
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                count += 1
                mdata = json.load(fp)
                results = mdata.get('results')
                if 'no_such' in spec:
                    assert results is None
                    continue
                if "empty" in spec:
                    assert results is None
                    assert ": Empty " in mdata.get('errors')[0]
                    continue
                if not isinstance(results, list):
                    results = [results]
                for result in results:
                    if not result:
                        continue
                    rel = result['object']['relative_path']
                    org_content = new_content = None
                    with open(os.path.join(data_root, rel), 'r') as fp:
                        new_content = fp.readlines()
                    if "insights_commands" not in rel:
                        # check files only
                        with open("/" + rel, 'r') as fp:
                            org_content = fp.readlines()
                        if "_filter" not in spec:
                            if org_content:
                                if obfuscate:
                                    assert len(org_content) == len(new_content)
                                    continue
                                    # Test below only for obfuscate=False
                                assert org_content[:-1] == new_content[:-1]
                                # Special: no '\n' in last line of collected data
                                assert org_content[-1].strip() == new_content[-1].strip()
                            else:
                                # Both Empty
                                assert not new_content
                        else:
                            # "filter" works in archive result files
                            assert len(org_content) > len(new_content)
    assert count == 14  # Number of Specs

    arch.delete_archive_dir()

    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)
