from insights.tests import context_wrap
from insights.parsers.sysconfig.virt_who import SysconfigVirtWho

VIRTWHO = """
# Register ESX machines using vCenter
#VIRTWHO_ESX=0
# Register guests using RHEV-M
 VIRTWHO_RHEVM=1

# Options for RHEV-M mode
VIRTWHO_RHEVM_OWNER=

TEST_OPT="A TEST"
""".strip()


def test_sysconfig_virt_who():
    result = SysconfigVirtWho(context_wrap(VIRTWHO))
    assert result["VIRTWHO_RHEVM"] == '1'
    assert result["VIRTWHO_RHEVM_OWNER"] == ''
    assert result.get("NO_SUCH_OPTIONS") is None
    assert "NOSUCHOPTIONS" not in result
    assert result.get("TEST_OPT") == 'A TEST'
