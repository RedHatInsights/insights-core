import doctest
import pytest

from insights.tests import context_wrap
from insights.parsers.insights_client_tags import InsightsClientTags
from insights.parsers import SkipException, insights_client_tags


INSIGHTS_CLIENT_TAGS_YAML_CONTENT = """
group: user_test
location: Brisbane/Australia
description:
- RHEL8
- qa_env
security: sensitive
""".strip()

INSIGHTS_CLIENT_TAGS_EMPTY = """
""".strip()

insights_client_tags_yaml_path = "/etc/insights-client/tags.yaml"


def test_satellite_yaml():
    result = insights_client_tags.InsightsClientTags(
        context_wrap(INSIGHTS_CLIENT_TAGS_YAML_CONTENT, path=insights_client_tags_yaml_path)
    )
    assert 'group' in result
    assert result['group'] == 'user_test'
    assert result['description'] == ['RHEL8', 'qa_env']


def test_content_empty():
    with pytest.raises(SkipException):
        InsightsClientTags(context_wrap(INSIGHTS_CLIENT_TAGS_EMPTY))


def test_losetup_doc_examples():
    env = {'tags_yaml': InsightsClientTags(context_wrap(INSIGHTS_CLIENT_TAGS_YAML_CONTENT))}
    failed, total = doctest.testmod(insights_client_tags, globs=env)
    assert failed == 0
