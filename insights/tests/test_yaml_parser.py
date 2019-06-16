#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

from insights.core import YAMLParser, ParseException
from insights.tests import context_wrap


bi_conf_content = """
{"remote_branch": -1, "remote_leaf": -1}
""".strip()


class FakeYamlParser(YAMLParser):
    """ Class for parsing the content of ``branch_info``."""
    pass


class MyYamlParser(YAMLParser):
    pass


def test_json_parser_success():
    ctx = context_wrap('a: 2')
    assert FakeYamlParser(ctx)


def test_json_parser_failure():
    ctx = context_wrap("boom /")
    with pytest.raises(ParseException) as ex:
        FakeYamlParser(ctx)

    assert "FakeYamlParser" in ex.value.args[0]


def test_settings_yml():
    ctx = context_wrap(bi_conf_content)
    ctx.content = bi_conf_content
    result = FakeYamlParser(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1


def test_settings_yml_list():
    ctx = context_wrap(bi_conf_content)
    result = FakeYamlParser(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1
