import doctest

from insights.parsers import insights_client_conf
from insights.tests import context_wrap

CLIENT_CONF = """
[insights-client]
# Change log level, valid options DEBUG, INFO, WARNING, ERROR, CRITICAL. Default DEBUG
loglevel=INFO
# Log each line executed
trace=False
# Attempt to auto configure with Satellite server
auto_config=True
# Automatically update the dynamic configuration
auto_update=False
# Obfuscate IP addresses
obfuscate=False
""".strip()

BASIC_INSIGHTS_CLIENT = """
{"username_set": true, "pass_set": true}
""".strip()


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        insights_client_conf,
        globs={'conf': insights_client_conf.InsightsClientConf(context_wrap(CLIENT_CONF)),
               'basic_conf': insights_client_conf.BasicAuthInsightsClient(context_wrap(BASIC_INSIGHTS_CLIENT))
               }
    )
    assert failed_count == 0


def test_basic_insights_client():
    ret = insights_client_conf.BasicAuthInsightsClient(context_wrap(BASIC_INSIGHTS_CLIENT))
    assert "username_set" in ret
    assert "pass_set" in ret


def test_insights_client_conf():
    conf = insights_client_conf.InsightsClientConf(context_wrap(CLIENT_CONF))
    assert conf is not None
    assert list(conf.sections()) == ['insights-client']
    assert conf.has_option('insights-client', 'auto_update')
    assert not conf.has_option('yabba', 'dabba_do')
    assert conf.get('insights-client', 'auto_update') == 'False'
