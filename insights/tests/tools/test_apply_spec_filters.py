import json
import os
import yaml

from collections import defaultdict

import insights

from insights.core import filters
from insights.specs import Specs
from insights.tools import apply_spec_filters


JSON_content = """
{
    "commands": [
        {
            "command": "/bin/ps alxwww",
            "pattern": [],
            "symbolic_name": "ps_alxwww"
        },
        {
            "command": "/bin/ps aux",
            "pattern": [],
            "symbolic_name": "ps_aux"
        },
        {
            "command": "/bin/ps auxcww",
            "pattern": [],
            "symbolic_name": "ps_auxcww"
        }
    ],
    "files": [
        {
            "file": "/etc/redhat-release",
            "pattern": [],
            "symbolic_name": "redhat_release"
        },
        {
            "file": "/etc/yum.conf",
            "pattern": [],
            "symbolic_name": "yum_conf"
        },
        {
            "file": "/var/log/yum.log",
            "pattern": [],
            "symbolic_name": "yum_log"
        }
    ],
    "globs": [
        {
            "glob": "/etc/nginx/*.conf",
            "pattern": [],
            "symbolic_name": "nginx_conf"
        }
    ],
    "version": "2024-11-21T03:08:24.937321"
}
""".strip()
JSON_file = '/tmp/_test_just_test_uploader.json'
YAML_file = '/tmp/_test_just_test_filters_yaml.yaml'
yaml_file = os.path.join(os.path.dirname(insights.__file__), filters._filename)


def setup_function():
    filters.add_filter(Specs.ps_alxwww, ['COMMAND', 'CMD'])
    filters.add_filter(Specs.ps_aux, 'COMMAND')
    filters.add_filter(Specs.yum_conf, '[')
    filters.add_filter(Specs.yum_log, ['Installed', 'Updated', 'Erased'])
    with open(JSON_file, 'w') as f:
        f.write(JSON_content)


def teardown_function():
    if os.path.exists(JSON_file):
        os.remove(JSON_file)
    if os.path.exists(YAML_file):
        os.remove(YAML_file)
    if os.path.exists(yaml_file):
        os.remove(yaml_file)

    filters._CACHE = {}
    filters.FILTERS = defaultdict(dict)


def test_apply_specs_filters_json():
    apply_spec_filters.apply_filters("json", 'insights.parsers', JSON_file)

    count = 0
    with open(JSON_file, 'r') as f:
        ret = json.load(f)
        # ps_alxwww
        assert len(ret['commands'][0]['pattern']) == 2
        count += 1
        # ps_aux
        assert len(ret['commands'][1]['pattern']) == 1
        count += 1
        # ps_auxcww
        assert len(ret['commands'][2]['pattern']) == 0
        count += 1
        # redhat_release
        assert len(ret['files'][0]['pattern']) == 0
        count += 1
        # yum_conf
        assert len(ret['files'][1]['pattern']) == 1
        count += 1
        # yum_log
        assert len(ret['files'][2]['pattern']) == 3
        count += 1

    assert count == 6


def test_apply_specs_filters_yaml():
    apply_spec_filters.apply_filters("yaml", 'insights.parsers', YAML_file)

    count = 0
    with open(YAML_file, 'r') as f:
        ret = yaml.safe_load(f)
        # ps_alxwww
        assert len(ret['insights.specs.Specs.ps_alxwww']) == 2
        count += 1
        # ps_aux
        assert len(ret['insights.specs.Specs.ps_aux']) == 1
        count += 1
        # ps_auxcww
        assert 'insights.specs.Specs.ps_auxcww' not in ret
        count += 1
        # redhat_release
        assert 'insights.specs.Specs.redhat_release' not in ret
        count += 1
        # yum_conf
        assert len(ret['insights.specs.Specs.yum_conf']) == 1
        count += 1
        # yum_log
        assert len(ret['insights.specs.Specs.yum_log']) == 3
        count += 1

    assert count == 6

    apply_spec_filters.apply_filters("yaml", 'insights.parsers')

    count = 0
    with open(yaml_file, 'r') as f:
        ret = yaml.safe_load(f)
        # ps_alxwww
        assert len(ret['insights.specs.Specs.ps_alxwww']) == 2
        count += 1
        # ps_aux
        assert len(ret['insights.specs.Specs.ps_aux']) == 1
        count += 1
        # ps_auxcww
        assert 'insights.specs.Specs.ps_auxcww' not in ret
        count += 1
        # redhat_release
        assert 'insights.specs.Specs.redhat_release' not in ret
        count += 1
        # yum_conf
        assert len(ret['insights.specs.Specs.yum_conf']) == 1
        count += 1
        # yum_log
        assert len(ret['insights.specs.Specs.yum_log']) == 3
        count += 1

    assert count == 6


def test_apply_specs_filters_ab():
    ret = apply_spec_filters.apply_filters("test", 'insights.parsers', YAML_file)
    assert ret == 1

    ret = apply_spec_filters.apply_filters("yaml", '', YAML_file)
    assert ret == 1

    ret = apply_spec_filters.apply_filters("json", 'insights.parsers')
    assert ret == 1

    ret = apply_spec_filters.apply_filters("json", 'insights.parsers', './abc_test')
    assert ret == 1
