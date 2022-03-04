import pytest

from insights.parsers import ParseException
from insights.parsers.insights_client_tags import InsightsClientTags
from insights.tests import context_wrap

TAGS = '''
group: eastern-sap
location: Boston
description:
- RHEL8
- SAP
key 4: value
'''.strip()

TAGS_UNPARSABLE = '''
group: eastern-sap
location=Boston
'''.strip()

TAGS_WITHOUT_GROUP = '''
location: Boston
description:
- RHEL8
- SAP
key 4: value
'''.strip()


def test_insights_client_tags():

    tags = InsightsClientTags(context_wrap(TAGS))
    assert tags.group == 'eastern-sap'
    assert tags.get('location') == 'Boston'
    assert tags.get('description') == ['RHEL8', 'SAP']
    assert tags.get('key 1') is None

    cls = tags.__class__
    name = ".".join([cls.__module__, cls.__name__])
    with pytest.raises(ParseException) as e:
        InsightsClientTags(context_wrap(TAGS_UNPARSABLE))
    assert "{0} couldn't parse yaml.".format(name) in str(e.value)

    tags = InsightsClientTags(context_wrap(TAGS_WITHOUT_GROUP))
    assert tags.group is None
    assert tags.get('location') == 'Boston'
    assert tags.get('description') == ['RHEL8', 'SAP']
    assert tags.get('key 1') is None
