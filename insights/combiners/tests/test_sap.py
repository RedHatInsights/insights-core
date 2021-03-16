from insights.parsers.hostname import Hostname as HnF
from insights import SkipComponent
from insights.parsers.lssap import Lssap
from insights.parsers.saphostctrl import SAPHostCtrlInstances
from insights.combiners import sap
from insights.combiners.sap import Sap
from insights.combiners.hostname import Hostname
from insights.tests import context_wrap
import pytest
import doctest

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

SAPHOSTCTRL_HOSTINSTANCES = '''
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String , HDB88
 Hostname , String , lu0417
 FullQualifiedHostname , String , lu0417.example.com
 IPAddress , String , 10.0.0.88
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D90
 SystemNumber , String , 90
 InstanceName , String , HDB90
 Hostname , String , lu0418
 FullQualifiedHostname , String , lu0418.example.com
 IPAddress , String , 10.0.0.90
 SapVersionInfo , String , 749, patch 211, changelist 1754007
'''

SAPHOSTCTRL_HOSTINSTANCES_GOOD = '''
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String , HDB88
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D90
 SystemNumber , String , 90
 InstanceName , String , HDB90
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D79
 SystemNumber , String , 08
 InstanceName , String , ERS08
 Hostname , String , d79ers
 FullQualifiedHostname , String , d79ers.example.com
 IPAddress , String , 10.0.0.15
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D79
 SystemNumber , String , 07
 InstanceName , String , ASCS07
 Hostname , String , d79ascs
 FullQualifiedHostname , String , d79ascs.example.com
 IPAddress , String , 10.0.0.14
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D79
 SystemNumber , String , 09
 InstanceName , String , DVEBMGS09
 Hostname , String , d79pas
 FullQualifiedHostname , String , d79pas.example.com
 IPAddress , String , 10.0.0.16
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D80
 SystemNumber , String , 10
 InstanceName , String , SCS10
 Hostname , String , d80scs
 FullQualifiedHostname , String , d80scs.example.com
 IPAddress , String , 10.0.0.17
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D62
 SystemNumber , String , 62
 InstanceName , String , HDB62
 Hostname , String , d62dbsrv
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.1.12
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D52
 SystemNumber , String , 52
 InstanceName , String , ASCS52
 Hostname , String , d52ascs
 FullQualifiedHostname , String , d52ascs.example.com
 IPAddress , String , 10.0.0.20
 SapVersionInfo , String , 749, patch 401, changelist 1806777
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D52
 SystemNumber , String , 54
 InstanceName , String , D54
 Hostname , String , d52pas
 FullQualifiedHostname , String , d52pas.example.com
 IPAddress , String , 10.0.0.22
 SapVersionInfo , String , 749, patch 401, changelist 1806777
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , SMA
 SystemNumber , String , 91
 InstanceName , String , SMDA91
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 200, changelist 1746260
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , B15
 SystemNumber , String , 00
 InstanceName , String , HDB00
 Hostname , String , sapb15hdba1
 FullQualifiedHostname , String , li-ld-1810.example.com
 SapVersionInfo , String , 749, patch 418, changelist 1816226
*********************************************************
'''

SAPHOSTCTRL_HOSTINSTANCES_R_CASE = '''
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , R4D
 SystemNumber , String , 12
 InstanceName , String , DVEBMGS12
 Hostname , String , r4d00
 FullQualifiedHostname , String , r4d00.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , R4D
 SystemNumber , String , 10
 InstanceName , String , ASCS10
 Hostname , String , r4d01
 FullQualifiedHostname , String , r4d01.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , WDX
 SystemNumber , String , 20
 InstanceName , String , W20
 Hostname , String , r4d02
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 773, patch 121, changelist 1917131
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , SMD
 SystemNumber , String , 98
 InstanceName , String , SMDA98
 Hostname , String , r4d01
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , SMD
 SystemNumber , String , 97
 InstanceName , String , SMDA97
 Hostname , String , r4d00
 FullQualifiedHostname , String , host_97.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
'''

HOSTNAME2 = 'host_97.example.corp'


def test_lssap_netweaver():
    lssap = Lssap(context_wrap(Lssap_nw_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
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
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
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
    hn = Hostname(HnF(context_wrap(HOSTNAME1)), None, None, None, None)
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
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_lssap_hana():
    lssap = Lssap(context_wrap(Lssap_hana_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
    sap = Sap(hn, None, lssap)
    assert 'D50' not in sap
    assert sap.is_netweaver is False
    assert sap.is_hana is True
    assert sap.is_ascs is False


def test_lssap_ascs():
    lssap = Lssap(context_wrap(Lssap_ascs_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
    sap = Sap(hn, None, lssap)
    assert sap['ASCS16'].sid == 'HA2'
    # ASCS is also a kind of NetWeaver
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_all():
    lssap = Lssap(context_wrap(Lssap_all_TEST))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
    sap = Sap(hn, None, lssap)
    assert sap['D16'].version == '749, patch 10, changelist 1698137'
    assert sap['ASCS16'].hostname == 'lu0417'
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_r_case():
    saphostctrl = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE))
    hn = Hostname(HnF(context_wrap(HOSTNAME2)), None, None, None, None)
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
                Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None),
                None,
                Lssap(context_wrap(Lssap_doc_TEST))
            )
          }
    failed, total = doctest.testmod(sap, globs=env)
    assert failed == 0


def test_ab():
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None, None)
    with pytest.raises(SkipComponent) as se:
        Sap(hn, None, None)
    assert 'No SAP instance.' in str(se)
