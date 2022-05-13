from insights.parsers.tags import Tags
from insights.tests.parsers import skip_exception_check
from insights.tests import context_wrap

tags_json_content = """
{"zone": "east", "owner": "test", "exclude": "true", "group": "app-db-01"}
""".strip()


def test_tags_json():
    ctx = context_wrap(tags_json_content)
    ctx.content = tags_json_content
    result = Tags(ctx)
    assert result.data['zone'] == "east"
    assert result.data['owner'] == "test"
    assert result.data['exclude'] == "true"
    assert result.data['group'] == "app-db-01"


def test_tags_json_bytes():
    bytes_content = bytes(str(tags_json_content).encode("utf-8"))
    ctx = context_wrap(bytes_content)
    ctx.content = bytes_content
    result = Tags(ctx)
    assert result.data['zone'] == "east"
    assert result.data['owner'] == "test"
    assert result.data['exclude'] == "true"
    assert result.data['group'] == "app-db-01"


def test_tags_empty():
    assert 'Empty output.' in skip_exception_check(Tags)
