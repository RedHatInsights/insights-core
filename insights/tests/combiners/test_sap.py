import pytest
import doctest

from insights.parsers.hostname import Hostname as HnF
from insights import SkipComponent
from insights.parsers.lssap import Lssap
from insights.parsers.saphostctrl import SAPHostCtrlInstances
from insights.combiners import sap
from insights.combiners.sap import Sap
from insights.combiners.hostname import Hostname
from insights.tests import context_wrap
from insights.tests.parsers.test_saphostctrl import SAPHOSTCTRL_HOSTINSTANCES_DOCS, SAPHOSTCTRL_HOSTINSTANCES_GOOD

Lssap_nw_TEST = """
 - lssap version 1.0 -
==========================================
  SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
  HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
  HA2|  22|       D22|         lu0416|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  50|       D50|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D50/exe
  HA2|  51|       D51|         lu0418|749, patch 10, changelist 1698137|          /usr/sap/HA2/D51/exe
  HA2|  52|       D52|         lu0418|749, patch 10, changelist 1698137|          /usr/sap/HA2/D52/exe
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
  HA2|  22|       D22|         lu0418|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
  HA2|  16|       HDB16|       lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/HDB16/exe
==========================================
""".strip()

HOSTNAME = 'lu0417.example.com'
HOSTNAME1 = 'li-ld-1810.example.com'

SAPHOSTCTRL_HOSTINSTANCES_R_CASE = '''
*********************************************************
 SID , String , R4D
 SystemNumber , String , 12
 InstanceName , String , DVEBMGS12
 InstanceType , String , Primary Application Server
 Hostname , String , r4d00
 FullQualifiedHostname , String , r4d00.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , R4D
 SystemNumber , String , 10
 InstanceName , String , ASCS10
 InstanceType , String , ABAP Central Services
 Hostname , String , r4d01
 FullQualifiedHostname , String , r4d01.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , WDX
 SystemNumber , String , 20
 InstanceName , String , W20
 InstanceType , String , WebDispatcher
 Hostname , String , r4d02
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 773, patch 121, changelist 1917131
*********************************************************
 SID , String , SMD
 SystemNumber , String , 98
 InstanceName , String , SMDA98
 InstanceType , String , Solution Manager Diagnostic Agent
 Hostname , String , r4d01
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
*********************************************************
 SID , String , SMD
 SystemNumber , String , 97
 InstanceName , String , SMDA97
 InstanceType , String , Solution Manager Diagnostic Agent
 Hostname , String , r4d00
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
'''

HOSTNAME2 = 'host_97.example.corp'


def test_lssap_netweaver():
    lssap = Lssap(context_wrap(Lssap_nw_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, None, lssap)
    assert sap['D50'].number == '50'
    assert 'D16' in sap.local_instances
    assert 'D51' in sap.all_instances
    assert 'D51' not in sap.local_instances
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is False


def test_saphostcrtl_hana():
    lssap = Lssap(context_wrap(Lssap_nw_TEST))
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, lssap)
    assert 'D50' not in sap
    assert sap.local_instances == ['HDB88']
    assert 'HDB90' in sap.all_instances
    assert sap['HDB88'].number == '88'
    assert sap['HDB90'].hostname == 'lu0418'
    assert sap['HDB90'].version == '749, patch 211, changelist 1754007'
    assert sap.number('HDB90') == '90'
    assert sap.sid('HDB88') == 'D89'
    assert sap.is_netweaver is False
    assert sap.is_hana is True
    assert sap.is_ascs is False


def test_saphostcrtl_hana_2():
    lssap = Lssap(context_wrap(Lssap_all_TEST))
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD))
    hn = Hostname(HnF(context_wrap(HOSTNAME1)), None, None, None)
    sap = Sap(hn, inst, lssap)
    assert 'D50' not in sap
    assert 'HDB00' in sap
    assert sorted(sap.local_instances) == sorted(['HDB88', 'HDB90', 'SMDA91', 'HDB62', 'HDB00'])
    assert sorted(sap.all_instances) == sorted([
        'ASCS07', 'ASCS52', 'D54', 'DVEBMGS09', 'ERS08', 'HDB00', 'HDB62',
        'HDB88', 'HDB90', 'SCS10', 'SMDA91'])
    assert sorted(sap.business_instances) == sorted([
        'ASCS07', 'ASCS52', 'D54', 'DVEBMGS09', 'ERS08', 'HDB00', 'HDB62',
        'HDB88', 'HDB90', 'SCS10'])
    assert sorted(sap.function_instances) == sorted(['SMDA91'])
    assert sap['HDB88'].number == '88'
    assert sap['HDB90'].hostname == 'li-ld-1810'
    assert sap['DVEBMGS09'].version == '749, patch 301, changelist 1779613'
    assert sap.version('HDB90') == '749, patch 211, changelist 1754007'
    assert sap.hostname('HDB62') == 'd62dbsrv'
    assert sap.type('SCS10') == 'SCS'
    assert sap.full_type('SCS10') == 'Java Central Services'
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_lssap_hana():
    lssap = Lssap(context_wrap(Lssap_hana_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, None, lssap)
    assert 'D50' not in sap
    assert sap.is_netweaver is False
    assert sap.is_hana is True
    assert sap.is_ascs is False


def test_lssap_ascs():
    lssap = Lssap(context_wrap(Lssap_ascs_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, None, lssap)
    assert sap['ASCS16'].sid == 'HA2'
    # ASCS is also a kind of NetWeaver
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_all():
    lssap = Lssap(context_wrap(Lssap_all_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, None, lssap)
    assert sap['D16'].version == '749, patch 10, changelist 1698137'
    assert sap['ASCS16'].hostname == 'lu0417'
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_r_case():
    saphostctrl = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE))
    hn = Hostname(HnF(context_wrap(HOSTNAME2)), None, None, None)
    sap = Sap(hn, saphostctrl, None)
    assert sorted(sap.local_instances) == sorted(['W20', 'SMDA98', 'SMDA97'])
    assert sap['DVEBMGS12'].version == '753, patch 501, changelist 1967207'
    assert sap['ASCS10'].hostname == 'r4d01'
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_doc_examples():
    env = {
            'saps': Sap(
                Hostname(HnF(context_wrap(HOSTNAME)), None, None, None),
                None,
                Lssap(context_wrap(Lssap_doc_TEST))
            )
          }
    failed, total = doctest.testmod(sap, globs=env)
    assert failed == 0


def test_ab():
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    with pytest.raises(SkipComponent) as se:
        Sap(hn, None, None)
    assert 'No SAP instance.' in str(se)
