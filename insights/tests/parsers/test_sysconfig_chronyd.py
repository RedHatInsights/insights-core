from insights.tests import context_wrap
from insights.parsers.sysconfig import ChronydSysconfig


CHRONYD = """
OPTIONS="-d"
#HIDE="me"
""".strip()


def test_sysconfig_chronyd():
    result = ChronydSysconfig(context_wrap(CHRONYD))
    assert result['OPTIONS'] == '-d'
    assert result.get('HIDE') is None
