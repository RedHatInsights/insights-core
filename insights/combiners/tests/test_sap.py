from ...parsers.hostname import Hostname
from ...parsers.lssap import Lssap
from ...combiners import sap
from ...combiners.sap import Sap
from ...combiners.hostname import hostname
from ...tests import context_wrap
import doctest

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

Lssap_all_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  16|       HDB16|       lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/HDB16/exe
  HA2|  16|       ASCS16|      lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/ASCS16/exe
==========================================
""".strip()

Lssap_doc_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  16|       HDB16|       lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/HDB16/exe
==========================================
""".strip()

HOSTNAME = 'lu0417.example.com'


def test_lssap_netweaver():
    lssap = Lssap(context_wrap(Lssap_nw_TEST))
    hn = hostname(Hostname(context_wrap(HOSTNAME)), None, None)
    sap = Sap(hn, lssap)
    assert sap.running_saps == ['netweaver']
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is False


def test_lssap_hana():
    lssap = Lssap(context_wrap(Lssap_hana_TEST))
    hn = hostname(Hostname(context_wrap(HOSTNAME)), None, None)
    sap = Sap(hn, lssap)
    assert sap.running_saps == ['hana']
    assert sap.is_netweaver is False
    assert sap.is_hana is True
    assert sap.is_ascs is False


def test_lssap_ascs():
    lssap = Lssap(context_wrap(Lssap_ascs_TEST))
    hn = hostname(Hostname(context_wrap(HOSTNAME)), None, None)
    sap = Sap(hn, lssap)
    assert sap.running_saps == ['ascs']
    assert sap.is_netweaver is False
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_all():
    lssap = Lssap(context_wrap(Lssap_all_TEST))
    hn = hostname(Hostname(context_wrap(HOSTNAME)), None, None)
    sap = Sap(hn, lssap)
    assert sorted(sap.running_saps) == sorted(['ascs', 'hana', 'netweaver'])
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_doc_examples():
    env = {
            'saps': Sap(
                hostname(Hostname(context_wrap(HOSTNAME)), None, None),
                Lssap(context_wrap(Lssap_doc_TEST))
            )
          }
    failed, total = doctest.testmod(sap, globs=env)
    assert failed == 0
