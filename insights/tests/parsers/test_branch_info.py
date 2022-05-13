from insights.parsers.branch_info import BranchInfo
from insights.tests import context_wrap

bi_conf_content = """
{"remote_branch": -1, "remote_leaf": -1}
""".strip()


def test_settings_yml():
    ctx = context_wrap(bi_conf_content)
    ctx.content = bi_conf_content
    result = BranchInfo(ctx)
    assert result.data['remote_branch'] == -1
    assert result.data['remote_leaf'] == -1
