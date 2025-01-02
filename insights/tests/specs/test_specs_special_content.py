# -*- coding: utf-8 -*-
import json
import os
from collections import defaultdict

import pytest
from mock.mock import patch

from insights import collect
from insights.client.archive import InsightsArchive
from insights.client.config import InsightsConfig
from insights.core import dr
from insights.core.spec_factory import encoding
from insights.core.spec_factory import RegistryPoint
from insights.core.spec_factory import safe_open
from insights.core.spec_factory import simple_file
from insights.core.spec_factory import SpecSet
from insights.util.hostname import determine_hostname

tmp_file_path = "/tmp/insights_unittest_unicode_text"
orig_hostname = determine_hostname()

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
        - name: insights.tests.specs.test_specs_special_content.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.specs.test_specs_special_content

    configs:
        - name: insights.core.spec_factory
          enabled: true
        - name: insights.tests.specs.test_specs_special_content.Specs
          enabled: true
        - name: insights.tests.specs.test_specs_special_content.Stuff
          enabled: true
""".strip()


class Specs(SpecSet):
    unicode_file = RegistryPoint()


class Stuff(Specs):
    unicode_file = simple_file(tmp_file_path)


#
# TEST
#


def setup_function(func):
    with safe_open(tmp_file_path, "w+", encoding=encoding, errors="surrogateescape") as f:
        f.write('“！……”\n{0}'.format(orig_hostname))


def teardown_function(func):
    os.remove(tmp_file_path)
    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)


@pytest.mark.parametrize("obfuscate", [True, False])
@patch('insights.cleaner.Cleaner.generate_report')
def test_specs_special_content_collect(report, obfuscate):
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
            file_name = "insights.tests.specs.test_specs_special_content.Specs.{0}.json".format(
                spec
            )
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                mdata = json.load(fp)
                assert not mdata.get('errors')

                results = mdata.get('results')
                if not isinstance(results, list):
                    results = [results]
                assert results

                count += 1
                for result in results:
                    if not result:
                        continue
                    rel = result['object']['relative_path']
                    assert rel == tmp_file_path.strip('/')
                    assert result['object']['save_as'] is False
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
