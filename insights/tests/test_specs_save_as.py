import os
import json

from collections import defaultdict
from mock.mock import patch, Mock
from pytest import mark

from insights import collect
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core import dr
from insights.core import filters
from insights.core.context import HostContext
from insights.core.filters import add_filter
from insights.core.plugins import datasource
from insights.core.spec_cleaner import Cleaner
from insights.core.spec_factory import (
        RawFileProvider, RegistryPoint, SpecSet, command_with_args,
        glob_file, simple_command, simple_file, first_file, foreach_collect)

specs_save_as_manifest = """
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
        patterns: []
        keywords: []

    persist:
        - name: insights.tests.test_specs_save_as.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.test_specs_save_as

    configs:
        - name: insights.tests.test_specs_save_as.Specs
          enabled: true
        - name: insights.tests.test_specs_save_as.Stuff
          enabled: true
""".strip()

SAVE_AS_MAP = {
    'many_glob': ('/many_glob/one.dir', 'many_glob/one.dir/'),
    'many_foreach': ('many_foreach_dir/', 'many_foreach_dir/'),
    'smpl_cmd': ('/smpl_dir/smpl_cmd', 'smpl_dir/smpl_cmd'),
    'smpl_cmd_w_filter': ('smpl_dir_wf/', 'smpl_dir_wf'),
    'cmd_w_args': ('cmd_with_args/', 'cmd_with_args'),
    'smpl_file': (None, None),
    'smpl_file_w_filter': ('smpl_filtered_file/', 'smpl_filtered_file/'),
    'first_file_spec_w_filter': ('/first.file', 'first.file'),
}

here = os.path.abspath(os.path.dirname(__file__))
this_file = os.path.abspath(__file__).rstrip("c")


class Specs(SpecSet):
    many_glob = RegistryPoint(multi_output=True)
    many_foreach = RegistryPoint(multi_output=True)
    smpl_cmd = RegistryPoint()
    smpl_cmd_w_filter = RegistryPoint(filterable=True)
    cmd_w_args = RegistryPoint()
    smpl_file = RegistryPoint()
    smpl_file_w_filter = RegistryPoint(filterable=True)
    first_file_spec_w_filter = RegistryPoint(filterable=True)


class Stuff(Specs):
    many_glob = glob_file(here + "/*.py", save_as=SAVE_AS_MAP['many_glob'][0])

    @datasource(HostContext)
    def ls_files(broker):
        """ Return a file path """
        return this_file

    @datasource(HostContext)
    def files(broker):
        """ Return a list of directories from the spec filter """
        return [here + "/helpers.py", here + "/__init__.py"]

    many_foreach = foreach_collect(files, "%s", save_as=SAVE_AS_MAP['many_foreach'][0])
    smpl_cmd = simple_command("/usr/bin/uptime", save_as=SAVE_AS_MAP['smpl_cmd'][0])
    smpl_cmd_w_filter = simple_command("echo -n ' hello '", save_as=SAVE_AS_MAP['smpl_cmd_w_filter'][0])
    cmd_w_args = command_with_args("ls %s", ls_files, save_as=SAVE_AS_MAP['cmd_w_args'][0])
    smpl_file = simple_file(this_file, save_as=SAVE_AS_MAP['smpl_file'][0])
    smpl_file_w_filter = simple_file(here + "/mock_web_server.py", kind=RawFileProvider, save_as=SAVE_AS_MAP['smpl_file_w_filter'][0])  # RAW file won't filter
    first_file_spec_w_filter = first_file([here + "/spec_tests.py", "/etc/os-release"], save_as=SAVE_AS_MAP['first_file_spec_w_filter'][0])


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)


# File content
with open(this_file) as f:
    smpl_file_content = f.read().splitlines()
with open(here + "/mock_web_server.py", 'rb') as f:  # RawFileProvider: rb; and no filtering
    smpl_file_w_filter_content = f.read()
with open(here + "/spec_tests.py") as f:
    first_file_w_filter_content = [l for l in f.read().splitlines() if any(i in l for i in [" hello ", "class T"])]

#
# TEST
#


def teardown_function(func):
    filters._CACHE = {}

    if func in [test_specs_save_as_collect, test_specs_save_as_no_collect]:
        del filters.FILTERS[Stuff.smpl_cmd_w_filter]
        del filters.FILTERS[Stuff.smpl_file_w_filter]
        del filters.FILTERS[Stuff.first_file_spec_w_filter]

    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)


@stage(Stuff.many_glob,
       Stuff.many_foreach,
       Stuff.smpl_file,
       Stuff.smpl_file_w_filter,
       Stuff.smpl_cmd,
       Stuff.smpl_cmd_w_filter,
       Stuff.cmd_w_args,
       Stuff.first_file_spec_w_filter)
def dostuff(broker):
    assert Stuff.many_glob in broker
    assert Stuff.many_foreach in broker
    assert Stuff.smpl_cmd in broker
    assert Stuff.smpl_cmd_w_filter in broker
    assert Stuff.cmd_w_args in broker
    assert Stuff.smpl_file in broker
    assert Stuff.smpl_file_w_filter in broker
    assert Stuff.first_file_spec_w_filter in broker


def test_specs_save_as_no_collect():
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_file_spec_w_filter, [" hello ", "class T"])
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker['cleaner'] = Cleaner(None, None)
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    # general tests
    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == smpl_file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)
    # "filter" works when loading
    assert "hello" in broker[Stuff.smpl_cmd_w_filter].content[0]
    assert len(broker[Stuff.smpl_cmd_w_filter].content) == 1
    assert broker[Stuff.smpl_file_w_filter].content == smpl_file_w_filter_content  # RawFileProvdier only one line
    assert broker[Stuff.first_file_spec_w_filter].content == first_file_w_filter_content
    # test "Save As"
    assert broker[Stuff.many_glob][-1].save_as == SAVE_AS_MAP['many_glob'][1]
    assert broker[Stuff.many_foreach][0].save_as == SAVE_AS_MAP['many_foreach'][1]
    assert broker[Stuff.many_foreach][1].save_as == SAVE_AS_MAP['many_foreach'][1]
    assert broker[Stuff.smpl_cmd].save_as == SAVE_AS_MAP['smpl_cmd'][1]
    assert broker[Stuff.smpl_cmd_w_filter].save_as == SAVE_AS_MAP['smpl_cmd_w_filter'][1]
    assert broker[Stuff.cmd_w_args].save_as == SAVE_AS_MAP['cmd_w_args'][1]
    assert broker[Stuff.smpl_file].save_as == SAVE_AS_MAP['smpl_file'][1]
    assert broker[Stuff.smpl_file_w_filter].save_as == SAVE_AS_MAP['smpl_file_w_filter'][1]
    assert broker[Stuff.first_file_spec_w_filter].save_as == SAVE_AS_MAP['first_file_spec_w_filter'][1]


@mark.parametrize("obfuscate", [True, False])
@patch('insights.core.spec_cleaner.Cleaner.generate_report', Mock())
def test_specs_save_as_collect(obfuscate):
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_file_spec_w_filter, [" hello ", "class T"])

    manifest = collect.load_manifest(specs_save_as_manifest)
    for pkg in manifest.get("plugins", {}).get("packages", []):
        dr.load_components(pkg, exclude=None)

    conf = InsightsConfig(
            obfuscate=obfuscate, obfuscate_hostname=obfuscate,
            manifest=specs_save_as_manifest)
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
            file_name = "insights.tests.test_specs_save_as.Specs.{0}.json".format(spec)
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                count += 1
                mdata = json.load(fp)
                results = mdata.get('results')
                if not isinstance(results, list):
                    results = [results]
                for result in results:
                    # 1. Checking Save As
                    assert result['object']['save_as'] is bool(SAVE_AS_MAP[spec][1])
                    # relative_path is started with "save_as"
                    rel = result['object']['relative_path']
                    if SAVE_AS_MAP[spec][1] is None:
                        # smpl_file
                        assert rel == this_file.lstrip('/')
                    else:
                        assert SAVE_AS_MAP[spec][1] in rel
                    # 2. Checking collection results in archive
                    # check particular files only
                    if "smpl_file_w_filter" in spec:
                        with open(os.path.join(data_root, rel), 'rb') as fp:
                            assert smpl_file_w_filter_content == fp.read()
                    elif "smpl_file" in spec:
                        with open(os.path.join(data_root, rel), 'r') as fp:
                            new_content = fp.read().splitlines()
                        assert new_content[:-1] == smpl_file_content[:-1]
                        assert new_content[-1].strip() == smpl_file_content[-1].strip()
                    elif "first_file_spec_w_filter" in spec:
                        with open(os.path.join(data_root, rel), 'r') as fp:
                            new_content = fp.read().splitlines()
                        assert new_content == [line for line in first_file_w_filter_content if "class T" in line]
    assert count == len(SAVE_AS_MAP)

    arch.delete_archive_dir()
