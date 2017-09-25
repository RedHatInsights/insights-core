from insights.tests import context_wrap
from insights.parsers.sysconfig import NtpdSysconfig

NTPD = """
OPTIONS="-x -g"
#HIDE="me"
""".strip()


def test_sysconfig_ntpd():
    result = NtpdSysconfig(context_wrap(NTPD))
    assert result['OPTIONS'] == '-x -g'
    assert result.get('HIDE') is None
