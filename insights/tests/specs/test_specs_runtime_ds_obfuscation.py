import json
import os
from collections import defaultdict

import pytest
from mock.mock import patch

from insights import collect
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core import dr
from insights.core.context import HostContext
from insights.core.plugins import datasource
from insights.core.spec_factory import command_with_args
from insights.core.spec_factory import RegistryPoint
from insights.core.spec_factory import SpecSet
from insights.parsers.hostname import Hostname
from insights.util.hostname import determine_hostname

orig_hostname = determine_hostname().split('.')[0]
base_path = "/tmp/empty_insights_unittest_"
# file path include the original hostname which is not obfuscated
tmp_file_path = "{0}{1}".format(base_path, orig_hostname)
collected_file = "localhost_empty"

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
        patterns: []
        keywords: []

    persist:
        # add Specs.hostname here, as only 'persist' items will be collected
        - name: insights.specs.Specs.hostname
          enabled: true

        - name: insights.tests.specs.test_specs_runtime_ds_obfuscation.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.specs.test_specs_runtime_ds_obfuscation

    configs:
        - name: insights.core.spec_factory
          enabled: true
        - name: insights.specs.Specs.hostname
          enabled: true
        - name: insights.specs.default.DefaultSpecs.hostname
          enabled: true
        - name: insights.parsers.hostname.Hostname
          enabled: true
        - name: insights.tests.specs.test_specs_runtime_ds_obfuscation.Specs
          enabled: true
        - name: insights.tests.specs.test_specs_runtime_ds_obfuscation.Stuff
          enabled: true
""".strip()


class Specs(SpecSet):
    # datasource spec
    # - no need to filter
    # - must be obfuscated
    # - must be redacted
    ds_read_hostname = RegistryPoint(filterable=False, no_obfuscate=[], no_redact=False)


class Stuff(Specs):

    @datasource(Hostname, HostContext)
    def path_with_hostname(broker):
        hn = broker.get(Hostname).hostname
        # the hostname must be not obfuscated
        return '{0}{1}'.format(base_path, hn)

    ds_read_hostname = command_with_args('ls -l  %s', path_with_hostname, save_as='localhost_empty')


#
# TEST
#


def setup_function(func):
    open(tmp_file_path, 'w+').close()


def teardown_function(func):
    os.remove(tmp_file_path)
    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)


@pytest.mark.parametrize("obfuscate", [True, False])
@patch('insights.cleaner.Cleaner.generate_report')
def test_specs_ds_with_hn_collect(mock_fun, obfuscate):
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
        if not spec.startswith(('__', 'context_handlers', 'registry')):
            file_name = (
                "insights.tests.specs.test_specs_runtime_ds_obfuscation.Specs.{0}.json".format(spec)
            )
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                mdata = json.load(fp)
                assert not mdata.get('errors')

                results = mdata.get('results')
                assert results

                if not isinstance(results, list):
                    results = [results]
                count += 1
                for result in results:
                    rel = result['object']['relative_path']
                    # save_as is used
                    assert result['object']['save_as'] is True
                    assert orig_hostname not in rel
                    assert rel.endswith(collected_file)
                    with open(os.path.join(data_root, rel), 'r') as fp:
                        new_content = ''.join(fp.readlines())
                        if obfuscate:
                            # hostname is obfuscated
                            assert orig_hostname not in new_content
                        else:
                            # hostname is not obfuscated
                            assert orig_hostname in new_content

    assert count == 1  # Number of Specs

    arch.delete_archive_dir()
