from insights.parsers.insights_client_conf import InsightsClientConf
from insights.tests import context_wrap

CLIENT_CONF = """
[insights-client]
auto_update=False
"""


def test_insights_client_conf():
    conf = InsightsClientConf(context_wrap(CLIENT_CONF))
    assert conf is not None
    assert list(conf.sections()) == ['insights-client']
    assert conf.has_option('insights-client', 'auto_update')
    assert not conf.has_option('yabba', 'dabba_do')
    assert conf.get('insights-client', 'auto_update') == 'False'
