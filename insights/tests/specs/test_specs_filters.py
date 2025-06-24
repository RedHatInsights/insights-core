import os
import json
import pytest

from collections import defaultdict
from mock.mock import patch

from insights import collect
from insights.cleaner import Cleaner
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core import dr
from insights.core import filters
from insights.core.context import HostContext
from insights.core.filters import add_filter
from insights.core.plugins import datasource
from insights.core.spec_factory import (
    RegistryPoint,
    SpecSet,
    command_with_args,
    foreach_collect,
    foreach_execute,
    glob_file,
    simple_command,
    simple_file,
    first_file,
    first_of,
)

here = os.path.abspath(os.path.dirname(__file__))

FILTER_DATA = "Some test data"

this_file = os.path.abspath(__file__).rstrip("c")
test_large_file = '/tmp/_insights_test.large_file_filter'
test_large_file_without_filter = '/tmp/_insights_test.large_file_without_filter'
test_one_line_left = '/tmp/_insights_test.one_line_left'
test_empty_after_filter = '/tmp/_insights_test.empty_after_filter'

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
        - name: insights.tests.specs.test_specs_filters.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.specs.test_specs_filters

    configs:
        - name: insights.core.spec_factory
          enabled: true
        - name: insights.tests.specs.test_specs_filters.Specs
          enabled: true
        - name: insights.tests.specs.test_specs_filters.Stuff
          enabled: true
        - name: insights.tests.specs.test_specs_filters.dostuff
          enabled: true
""".strip()


class Specs(SpecSet):
    many_glob_filter = RegistryPoint(multi_output=True, no_redact=True, filterable=True)
    many_foreach_exe_filter = RegistryPoint(multi_output=True, filterable=True)
    many_foreach_clc_filter = RegistryPoint(multi_output=True, filterable=True)
    smpl_cmd_w_filter = RegistryPoint(filterable=True)
    smpl_file_w_filter = RegistryPoint(filterable=True)
    first_file_spec_w_filter = RegistryPoint(filterable=True)
    first_of_spec_w_filter = RegistryPoint(filterable=True)
    empty_after_filter = RegistryPoint(filterable=True)
    cmd_w_args_filter = RegistryPoint(filterable=True)
    large_filter = RegistryPoint(filterable=True)
    large_file_without_filter = RegistryPoint(filterable=False)
    one_line_left = RegistryPoint(filterable=True)


class Stuff(Specs):
    many_glob_filter = glob_file(here + "/../test_b*.py")

    @datasource(HostContext)
    def files1(broker):
        """Return a list of directories from the spec filter"""
        return [here + "/../test_test.py", here + "/../test_taglang.py"]

    @datasource(HostContext)
    def files2(broker):
        """Return a list of directories from the spec filter"""
        return ' '.join([here + "/../test_test.py", here + "/../test_taglang.py"])

    many_foreach_exe_filter = foreach_execute(files1, 'ls -l %s')
    many_foreach_clc_filter = foreach_collect(files1, "%s", no_redact=True)
    smpl_cmd_w_filter = simple_command("echo -n ' hello 1'")
    smpl_file_w_filter = simple_file(here + "/../mock_web_server.py")
    first_file_spec_w_filter = first_file([here + "/../spec_tests.py", "/etc/os-release"])
    first_of_spec_w_filter = first_of(
        [
            simple_command("echo -n ' hello 1'"),
            simple_file(this_file),
        ]
    )

    empty_after_filter = simple_file(test_empty_after_filter)
    cmd_w_args_filter = command_with_args('ls -lt %s', files2)
    large_filter = simple_file(test_large_file)
    large_file_without_filter = simple_file(test_large_file_without_filter)
    one_line_left = simple_file(test_one_line_left)


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


@stage(
    Stuff.many_glob_filter,
    Stuff.many_foreach_exe_filter,
    Stuff.many_foreach_clc_filter,
    Stuff.smpl_cmd_w_filter,
    Stuff.smpl_file_w_filter,
    Stuff.first_file_spec_w_filter,
    Stuff.first_of_spec_w_filter,
    Stuff.cmd_w_args_filter,
    Stuff.large_filter,
    Stuff.large_file_without_filter,
    Stuff.one_line_left,
    optional=[Stuff.empty_after_filter],
)
def dostuff(broker):
    assert Stuff.many_glob_filter in broker
    assert Stuff.many_foreach_exe_filter in broker
    assert Stuff.many_foreach_clc_filter in broker
    assert Stuff.smpl_cmd_w_filter in broker
    assert Stuff.smpl_file_w_filter in broker
    assert Stuff.first_file_spec_w_filter in broker
    assert Stuff.first_of_spec_w_filter in broker
    assert Stuff.cmd_w_args_filter in broker
    assert Stuff.one_line_left in broker

    assert Stuff.empty_after_filter not in broker


# File content
with open(here + "/../mock_web_server.py") as f:
    smpl_file_w_filter_content = [l for l in f.read().splitlines() if "def get" in l]
with open(here + "/../spec_tests.py") as f:
    first_file_w_filter_content = [
        l for l in f.read().splitlines() if any(i in l for i in ["def report_", "rhel"])
    ]

#
# TEST
#


def setup_function(func):
    if func == test_specs_filters_collect:
        # empty relevant files
        with open(test_empty_after_filter, 'w') as t:
            t.write('no-filter')
    with open(test_large_file, 'w') as fd:
        for i in range(filters.MAX_MATCH + 1):
            fd.write(str(i) + FILTER_DATA + '\n')
    with open(test_large_file_without_filter, 'w') as fd:
        for i in range(filters.MAX_MATCH + 1):
            fd.write(str(i) + FILTER_DATA + '\n')
    with open(test_one_line_left, 'w') as fd:
        for i in range(filters.MAX_MATCH + 1):
            fd.write(str(i) + FILTER_DATA + '\n')


def teardown_function(func):
    # Reset Test ENV
    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)

    if os.path.exists(test_empty_after_filter):
        os.remove(test_empty_after_filter)
    if os.path.exists(test_large_file):
        os.remove(test_large_file)
    if os.path.exists(test_large_file_without_filter):
        os.remove(test_large_file_without_filter)
    if os.path.exists(test_one_line_left):
        os.remove(test_one_line_left)


def test_specs_filters_spec_factory():
    add_filter(Stuff.many_glob_filter, " ")
    add_filter(Stuff.many_foreach_exe_filter, " ")
    add_filter(Stuff.many_foreach_clc_filter, " ")
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, ["def report_", "rhel"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    add_filter(Stuff.cmd_w_args_filter, [" ", ":"])
    add_filter(Stuff.large_filter, ["Some"])
    add_filter(Stuff.one_line_left, ["test data"], 1)
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)

    assert dostuff in broker, broker.tracebacks
    # "filter" works when loading
    assert "hello" in broker[Stuff.smpl_cmd_w_filter].content[0]
    assert len(broker[Stuff.smpl_cmd_w_filter].content) == 1
    assert broker[Stuff.smpl_file_w_filter].content == smpl_file_w_filter_content
    assert broker[Stuff.first_file_spec_w_filter].content == first_file_w_filter_content
    assert len(broker[Stuff.first_of_spec_w_filter].content) == 1
    assert len(broker.exceptions) == 1  # empty_after_filter
    assert len(broker.tracebacks) == 1  # empty_after_filter


def test_line_terminators():
    add_filter(Stuff.many_glob_filter, " ")
    add_filter(Stuff.many_foreach_exe_filter, " ")
    add_filter(Stuff.many_foreach_clc_filter, " ")
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, ["def report_", "rhel"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    add_filter(Stuff.cmd_w_args_filter, [" ", ":"])
    add_filter(Stuff.large_filter, ["Some"])
    add_filter(Stuff.one_line_left, ["test data"], 1)
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
            elif "many_glob_filter" in str(spec):
                exception_cnt += 10000
            elif "many_foreach_exe_filter" in str(spec):
                exception_cnt += 100000
            elif "many_foreach_clc_filter" in str(spec):
                exception_cnt += 1000000
            elif "cmd_w_args_filter" in str(spec):
                exception_cnt += 10000000
            elif "large_filter" in str(spec):
                exception_cnt += 100000000
            elif "one_line_left" in str(spec):
                exception_cnt += 1000000000
    assert exception_cnt == 1111111111


@pytest.mark.parametrize("obfuscate", [True, False])
@patch('insights.cleaner.Cleaner.generate_report', return_value=None)
def test_specs_filters_collect(gen, obfuscate):
    add_filter(Stuff.many_glob_filter, " ")
    add_filter(Stuff.many_foreach_exe_filter, " ")
    add_filter(Stuff.many_foreach_clc_filter, " ")
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def get")
    add_filter(Stuff.first_file_spec_w_filter, [" hello ", "Test"])
    add_filter(Stuff.first_of_spec_w_filter, ["def test", " hello "])
    add_filter(Stuff.empty_after_filter, " hello ")
    add_filter(Stuff.cmd_w_args_filter, [" ", ":"])
    add_filter(Stuff.large_filter, ["Some"])
    add_filter(Stuff.one_line_left, ["test data"], 1)
    # Preparation
    manifest = collect.load_manifest(specs_manifest)
    for pkg in manifest.get("plugins", {}).get("packages", []):
        dr.load_components(pkg, exclude=None)
    # For verifying convenience, test obfuscate=False only
    conf = InsightsConfig(obfuscate=obfuscate, obfuscate_hostname=obfuscate, manifest=manifest)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()
    output_path, errors = collect.collect(
        tmp_path=arch.tmp_dir, archive_name=arch.archive_name, client_config=conf
    )
    meta_data_root = os.path.join(output_path, 'meta_data')
    data_root = os.path.join(output_path, 'data')

    assert not errors
    count = 0
    for spec in Specs.__dict__:
        if str(spec) == "large_file_without_filter":
            # skip the  without filter file
            continue
        if not spec.startswith(('__', 'context_handlers', 'registry')):
            file_name = "insights.tests.specs.test_specs_filters.Specs.{0}.json".format(spec)
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                mdata = json.load(fp)
                results = mdata.get('results')
                if not isinstance(results, list):
                    results = [results]
                count += 1
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
                        assert len(org_content) > len(new_content)
                        if "large_filter" in spec:
                            # if matched lines exceed the MAX_MATCH
                            # collect the last MAX_MATCH lines only
                            assert len(new_content) == filters.MAX_MATCH
                            assert new_content[0] != org_content[0]
                            assert new_content[-1].strip() == org_content[-1].strip()
                        elif "one_line_left" in spec:
                            # only one line is required
                            assert len(new_content) == 1
                            assert new_content[0] != org_content[0]
                            # the last line is kept
                            assert new_content[-1].strip() == org_content[-1].strip()
    assert count == 11  # Number of Specs

    arch.delete_archive_dir()
