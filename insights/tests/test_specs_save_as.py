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
from insights.core.spec_factory import (
        RawFileProvider, RegistryPoint, SpecSet,
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
    'smpl_file': (None, None),
    'smpl_file_w_filter': ('smpl_filtered_file/', 'smpl_filtered_file/'),
    'first_of_spec_w_filter': ('/first.file', 'first.file'),
}

here = os.path.abspath(os.path.dirname(__file__))

# hack to find this source file and not the .pyc version of it
this_file = os.path.abspath(__file__).rstrip("c")
with open(this_file) as f:
    file_content = f.read().splitlines()


class Specs(SpecSet):
    many_glob = RegistryPoint(multi_output=True)
    many_foreach = RegistryPoint(multi_output=True)
    smpl_cmd = RegistryPoint()
    smpl_cmd_w_filter = RegistryPoint(filterable=True)
    smpl_file = RegistryPoint()
    smpl_file_w_filter = RegistryPoint(filterable=True)
    first_of_spec_w_filter = RegistryPoint(filterable=True)


class Stuff(Specs):
    many_glob = glob_file(here + "/*.py", save_as=SAVE_AS_MAP['many_glob'][0])

    @datasource(HostContext)
    def files(broker):
        """ Return a list of directories from the spec filter """
        return [this_file, here + "/__init__.py"]

    many_foreach = foreach_collect(files, "%s", save_as=SAVE_AS_MAP['many_foreach'][0])
    smpl_cmd = simple_command("/usr/bin/uptime", save_as=SAVE_AS_MAP['smpl_cmd'][0])
    smpl_cmd_w_filter = simple_command("echo -n ' hello '", save_as=SAVE_AS_MAP['smpl_cmd_w_filter'][0])
    smpl_file = simple_file(this_file, save_as=SAVE_AS_MAP['smpl_file'][0])
    smpl_file_w_filter = simple_file(this_file, kind=RawFileProvider, save_as=SAVE_AS_MAP['smpl_file_w_filter'][0])  # RAW file won't filter
    first_of_spec_w_filter = first_file([this_file, "/etc/os-release"], save_as=SAVE_AS_MAP['first_of_spec_w_filter'][0])


class stage(dr.ComponentType):
    def invoke(self, broker):
        return self.component(broker)

#
# TEST
#


def teardown_function(func):
    filters._CACHE = {}

    if func in [test_specs_save_as_collect, test_specs_save_as_no_collect]:
        del filters.FILTERS[Stuff.smpl_cmd_w_filter]
        del filters.FILTERS[Stuff.smpl_file_w_filter]
        del filters.FILTERS[Stuff.first_of_spec_w_filter]


@stage(Stuff.many_glob,
       Stuff.many_foreach,
       Stuff.smpl_file,
       Stuff.smpl_file_w_filter,
       Stuff.smpl_cmd,
       Stuff.smpl_cmd_w_filter,
       Stuff.first_of_spec_w_filter)
def dostuff(broker):
    assert Stuff.many_glob in broker
    assert Stuff.many_foreach in broker
    assert Stuff.smpl_cmd in broker
    assert Stuff.smpl_cmd_w_filter in broker
    assert Stuff.smpl_file in broker
    assert Stuff.smpl_file_w_filter in broker
    assert Stuff.first_of_spec_w_filter in broker


def test_specs_save_as_no_collect():
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_of_spec_w_filter, [" hello ", "def test"])
    broker = dr.Broker()
    broker[HostContext] = HostContext()
    broker = dr.run(dr.get_dependency_graph(dostuff), broker)
    # general tests
    assert dostuff in broker, broker.tracebacks
    assert broker[Stuff.smpl_file].content == file_content
    assert not any(l.endswith("\n") for l in broker[Stuff.smpl_file].content)
    assert "hello" in broker[Stuff.smpl_cmd_w_filter].content[0]
    assert len(broker[Stuff.smpl_cmd_w_filter].content) == 1  # RawFileProvdier
    assert len(broker[Stuff.first_of_spec_w_filter].content) == 9
    # test "Save As"
    assert broker[Stuff.many_glob][-1].save_as == SAVE_AS_MAP['many_glob'][1]
    assert broker[Stuff.many_foreach][0].save_as == SAVE_AS_MAP['many_foreach'][1]
    assert broker[Stuff.many_foreach][1].save_as == SAVE_AS_MAP['many_foreach'][1]
    assert broker[Stuff.smpl_cmd].save_as == SAVE_AS_MAP['smpl_cmd'][1]
    assert broker[Stuff.smpl_cmd_w_filter].save_as == SAVE_AS_MAP['smpl_cmd_w_filter'][1]
    assert broker[Stuff.smpl_file].save_as == SAVE_AS_MAP['smpl_file'][1]
    assert broker[Stuff.smpl_file_w_filter].save_as == SAVE_AS_MAP['smpl_file_w_filter'][1]
    assert broker[Stuff.first_of_spec_w_filter].save_as == SAVE_AS_MAP['first_of_spec_w_filter'][1]


@mark.parametrize("obfuscate", [True, False])
@patch('insights.core.spec_cleaner.Cleaner.generate_report', Mock())
def test_specs_save_as_collect(obfuscate):
    add_filter(Stuff.smpl_cmd_w_filter, " hello ")
    add_filter(Stuff.smpl_file_w_filter, "def test")
    add_filter(Stuff.first_of_spec_w_filter, [" hello ", "def test"])

    manifest = collect.load_manifest(specs_save_as_manifest)
    for pkg in manifest.get("plugins", {}).get("packages", []):
        dr.load_components(pkg, exclude=None)

    conf = InsightsConfig(obfuscate=obfuscate, obfuscate_hostname=obfuscate)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()
    output_path, errors = collect.collect(
            manifest=specs_save_as_manifest,
            tmp_path=arch.tmp_dir,
            archive_name=arch.archive_name,
            client_config=conf)
    meta_data_root = os.path.join(output_path, 'meta_data')

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
                    # Save As
                    assert result['object']['save_as'] is True
                    # relative_path is started with "save_as"
                    rel = result['object']['relative_path']
                    if "insights_commands" in rel:
                        rel = rel.replace('insights_commands/', '')
                    if SAVE_AS_MAP[spec][1] is None:
                        assert rel == this_file.lstrip('/')
                    else:
                        assert rel.startswith(SAVE_AS_MAP[spec][1])
    assert count == len(SAVE_AS_MAP)

    arch.delete_archive_dir()

    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)
