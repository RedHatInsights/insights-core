from insights.core import YAMLParser
from insights.tests import context_wrap


class FakeYamlParserClass(YAMLParser):
    """ Class for parsing the content of ``branch_info``."""
    pass


bi_conf_content = """
{"remote_branch": -1, "remote_leaf": -1}
""".strip()


def test_settings_yml():
    ctx = context_wrap(bi_conf_content)
    ctx.content = bi_conf_content
    result = FakeYamlParserClass(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1


def test_settings_yml_list():
    ctx = context_wrap(bi_conf_content)
    result = FakeYamlParserClass(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1
