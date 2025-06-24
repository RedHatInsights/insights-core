import json
import os
from collections import defaultdict

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

tmp_file_path = "/tmp/empty_insights_unittest_with_pattern"

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
        - name: insights.tests.specs.test_specs_content_redaction_empty.Specs
          enabled: true

    run_strategy:
        name: serial
        args:
            max_workers: null

plugins:
    default_component_enabled: false

    packages:
        - insights.tests.specs.test_specs_content_redaction_empty

    configs:
        - name: insights.tests.specs.test_specs_content_redaction_empty.Specs
          enabled: true
        - name: insights.tests.specs.test_specs_content_redaction_empty.Stuff
          enabled: true
""".strip()


class Specs(SpecSet):
    file_no_redact = RegistryPoint(no_redact=True)
    file_w_redact = RegistryPoint(no_redact=False)


class Stuff(Specs):
    file_no_redact = simple_file(tmp_file_path, save_as=tmp_file_path + '_1')
    file_w_redact = simple_file(tmp_file_path)


#
# TEST
#


def setup_function(func):
    with safe_open(tmp_file_path, "w+", encoding=encoding, errors="surrogateescape") as f:
        f.write('\n'.join(["KEEEY {0}".format(i) for i in range(3)]))


def teardown_function(func):
    if os.path.exists(tmp_file_path):
        os.remove(tmp_file_path)
    # Reset Test ENV
    dr.COMPONENTS = defaultdict(lambda: defaultdict(set))
    dr.TYPE_OBSERVERS = defaultdict(set)
    dr.ENABLED = defaultdict(lambda: True)


@patch('insights.cleaner.Cleaner.generate_report')
def test_specs_ds_with_hn_collect(mock_fun):
    # Preparation
    manifest = collect.load_manifest(specs_manifest)
    for pkg in manifest.get("plugins", {}).get("packages", []):
        dr.load_components(pkg, exclude=None)
    # For verifying convenience, test obfuscate=False only
    conf = InsightsConfig(manifest=manifest)
    arch = InsightsArchive(conf)
    arch.create_archive_dir()
    rm_conf = {'patterns': {'regex': ['KEEEY']}, 'keywords': ['TeST']}
    output_path, errors = collect.collect(
        tmp_path=arch.tmp_dir, archive_name=arch.archive_name, rm_conf=rm_conf, client_config=conf
    )
    meta_data_root = os.path.join(output_path, 'meta_data')
    data_root = os.path.join(output_path, 'data')

    assert not errors
    spec_count = 0
    line_count = 0
    for spec in Specs.__dict__:
        if not spec.startswith(('__', 'context_handlers', 'registry')):
            file_name = (
                "insights.tests.specs.test_specs_content_redaction_empty.Specs.{0}.json".format(
                    spec
                )
            )
            meta_data = os.path.join(meta_data_root, file_name)
            with open(meta_data, 'r') as fp:
                mdata = json.load(fp)
                results = mdata.get('results')
                if 'file_no_redact' in spec:
                    spec_count += 1
                    assert not mdata.get('errors')
                    assert results
                    if not isinstance(results, list):
                        results = [results]
                    for result in results:
                        rel = result['object']['relative_path']
                        with open(os.path.join(data_root, rel), 'r') as fp:
                            for line in fp:
                                line_count += 1
                                assert "KEEEY" in line
                else:
                    spec_count += 1
                    # file_w_redact is not collected as it's redacted to empty
                    assert mdata.get('errors')
                    assert not results
                    assert not os.path.exists(os.path.join(data_root, tmp_file_path.lstrip('/')))

    assert spec_count == 2  # Number of Specs
    assert line_count == 3  # Number of Lines in "file_no_redact"

    arch.delete_archive_dir()
