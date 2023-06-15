from insights.tests import context_wrap
from insights.parsers.sysconfig import StonithSysconfig

STONITH_SYSCONFIG = """
retry=3
retry-sleep=2
verbose=yes    # optional
""".strip()


def test_sysconfig_sshd():
    result = StonithSysconfig(context_wrap(STONITH_SYSCONFIG))
    assert result["retry"] == '3'
    assert result.get("retry-sleep") == '2'
    assert result.get("verbose") == 'yes'
