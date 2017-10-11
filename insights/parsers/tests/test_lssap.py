from ...parsers import lssap, ParseException
from ...tests import context_wrap
from ...util import keys_in
import pytest

Lssap_BAD = """
 - lssap version 1.0 -
 ==========================================
   SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
   HA2|  16|       D16|         lu0417
==========================================
""".strip()

Lssap_BAD1 = """
   HA2|  16|       D16|         lu0417
""".strip()

Lssap_BAD2 = ""

Lssap_nw_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  50|       D50|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D50/exe
  HA2|  51|       D51|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D51/exe
  HA2|  52|       D52|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D52/exe
==========================================
""".strip()

Lssap_hana_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       HDB16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/HDB16/exe
==========================================
""".strip()

Lssap_ascs_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       ASCS16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/ASCS16/exe
==========================================
""".strip()

Lssap_bad_instance_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       B16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       QR22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  50|       DS0|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D50/exe
==========================================
""".strip()

Lssap_runAll_Test = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  16|       HDB16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/HDB16/exe
  HA2|  16|       ASCS16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/ASCS16/exe
==========================================
""".strip()

Lssap_BAD = """
/usr/sap/hostctrl/lssap: command or file not found
"""

Lssap_BAD_2 = """
HA2 | N16|  D16
""".strip()

Lssap_BAD_3 = """
HA2 | N16 | D16
HB2 | foo | bar
""".strip()


def test_lists():
    sap = lssap.Lssap(context_wrap(Lssap_runAll_Test))
    assert sap.instances == ["D16", "D22", "HDB16", "ASCS16"]
    assert sap.sid == ["HA2"]
    assert sap.version("D16") == "749, patch 10, changelist 1698137"


def test_lssap_netweaver():
    sap = lssap.Lssap(context_wrap(Lssap_nw_TEST))
    data = sap.data
    assert keys_in(["SID", "Nr", "Instance", "SAPLOCALHOST", "Version", "DIR_EXECUTABLE"], data[0])
    assert data[0] == {"SID": "HA2", "Nr": "16", "Instance": "D16", "SAPLOCALHOST": "lu0417",
                       "Version": "749, patch 10, changelist 1698137",
                       "DIR_EXECUTABLE": "/usr/sap/HA2/D16/exe"}
    assert data[2]["Instance"] == "D50"
    assert data[-1]["SAPLOCALHOST"] == "lu0417"
    assert sap.is_netweaver() is True
    assert sap.is_hana() is False
    assert sap.is_ascs() is False


def test_lssap_hana():
    sap = lssap.Lssap(context_wrap(Lssap_hana_TEST))
    data = sap.data
    assert data[0] == {"SID": "HA2", "Nr": "16", "Instance": "HDB16", "SAPLOCALHOST": "lu0417",
                       "Version": "749, patch 10, changelist 1698137",
                       "DIR_EXECUTABLE": "/usr/sap/HA2/HDB16/exe"}
    assert data[0]["SAPLOCALHOST"] == "lu0417"
    assert sap.is_hana() is True
    assert sap.is_netweaver() is False
    assert sap.is_ascs() is False


def test_lssap_ascs():
    sap = lssap.Lssap(context_wrap(Lssap_ascs_TEST))
    assert sap.is_hana() is False
    assert sap.is_netweaver() is False
    assert sap.is_ascs() is True


def test_all():
    sap = lssap.Lssap(context_wrap(Lssap_runAll_Test))
    data = sap.data
    assert data[1] == {"SID": "HA2", "Nr": "22", "Instance": "D22", "SAPLOCALHOST": "lu0417",
                       "Version": "749, patch 10, changelist 1698137",
                       "DIR_EXECUTABLE": "/usr/sap/HA2/D22/exe"}
    assert sap.is_netweaver() is True
    assert sap.is_hana() is True
    assert sap.is_ascs() is True


def test_fail():
    with pytest.raises(ParseException) as excinfo:
        lssap.Lssap(context_wrap(Lssap_BAD))
    assert "Lssap: Unable to parse 1 line(s) of content: (['/usr/sap/hostctrl/lssap: command or file not found'])" in str(excinfo)

    with pytest.raises(ParseException) as excinfo:
        lssap.Lssap(context_wrap('test'))
    assert "Lssap: Unable to parse 1 line(s) of content: (['test'])" in str(excinfo)

    with pytest.raises(ParseException) as excinfo:
        lssap.Lssap(context_wrap(Lssap_BAD_2))
    assert "Lssap: Unable to parse 1 line(s) of content: (['HA2 | N16|  D16'])" in str(excinfo)

    with pytest.raises(ParseException) as excinfo:
        lssap.Lssap(context_wrap(Lssap_BAD_3))
    assert "Lssap: Unable to parse 2 line(s) of content: (['HA2 | N16 | D16', 'HB2 | foo | bar'])" in str(excinfo)

    with pytest.raises(ParseException) as excinfo:
        lssap.Lssap(context_wrap(Lssap_bad_instance_TEST))
    assert "Lssap: Invalid instance parsed in content: ['B', 'QR', 'DS']" in str(excinfo)
