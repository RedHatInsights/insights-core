from insights.parsers import dcbtool_gc_dcb
from insights.tests import context_wrap


DCBTOOL_GC_OUTPUT = """

    Command:    Get Config
    Feature:    DCB State
    Port:       eth0
    Status:     Off
    DCBX Version: FORCED CIN

"""

DCBTOOL_GC_DCB_FAILED = """
connect: Connection refused
Failed to connect to lldpad - clif_open: Connection refused
"""


def test_dcbtool_gc():
    result = dcbtool_gc_dcb.Dcbtool(context_wrap(DCBTOOL_GC_OUTPUT))
    assert len(result.data) == 5
    assert result["command"] == "Get Config"
    assert result["feature"] == "DCB State"
    assert result["port"] == "eth0"
    assert result["status"] == "Off"
    assert result["dcbx_version"] == "FORCED CIN"

    assert not result.is_on

    result = dcbtool_gc_dcb.Dcbtool(context_wrap(DCBTOOL_GC_DCB_FAILED))
    assert len(result.data) == 0
