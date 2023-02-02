import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import saphostctrl
from insights.parsers.saphostctrl import SAPHostCtrlInstances
from insights.tests import context_wrap

SAPHOSTCTRL_HOSTINSTANCES_DOCS = '''
*********************************************************
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String , HDB88
 InstanceType , String , HANA Test
 Hostname , String , lu0417
 FullQualifiedHostname , String , lu0417.example.com
 IPAddress , String , 10.0.0.88
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 SID , String , D90
 SystemNumber , String , 90
 InstanceName , String , HDB90
 InstanceType , String , HANA Test
 Hostname , String , lu0418
 FullQualifiedHostname , String , lu0418.example.com
 IPAddress , String , 10.0.0.90
 SapVersionInfo , String , 749, patch 211, changelist 1754007
'''

SAPHOSTCTRL_HOSTINSTANCES_DOCS_OLD = '''
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D89
 SystemNumber , String , 88
 InstanceType , String , HANA Test
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
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String , HDB88
 InstanceType , String , HANA
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 SID , String , D90
 SystemNumber , String , 90
 InstanceName , String , HDB90
 InstanceType , String , HANA
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 SID , String , D79
 SystemNumber , String , 08
 InstanceName , String , ERS08
 InstanceType , String , Enqueue Replication Server
 Hostname , String , d79ers
 FullQualifiedHostname , String , d79ers.example.com
 IPAddress , String , 10.0.0.15
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 SID , String , D79
 SystemNumber , String , 07
 InstanceName , String , ASCS07
 InstanceType , String , ABAP Central Services
 Hostname , String , d79ascs
 FullQualifiedHostname , String , d79ascs.example.com
 IPAddress , String , 10.0.0.14
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 SID , String , D79
 SystemNumber , String , 09
 InstanceName , String , DVEBMGS09
 InstanceType , String , Primary Application Server
 Hostname , String , d79pas
 FullQualifiedHostname , String , d79pas.example.com
 IPAddress , String , 10.0.0.16
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 SID , String , D80
 SystemNumber , String , 10
 InstanceName , String , SCS10
 InstanceType , String , Java Central Services
 Hostname , String , d80scs
 FullQualifiedHostname , String , d80scs.example.com
 IPAddress , String , 10.0.0.17
 SapVersionInfo , String , 749, patch 301, changelist 1779613
*********************************************************
 SID , String , D62
 SystemNumber , String , 62
 InstanceName , String , HDB62
 InstanceType , String , HANA
 Hostname , String , d62dbsrv
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.1.12
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 SID , String , D52
 SystemNumber , String , 52
 InstanceName , String , ASCS52
 InstanceType , String , ABAP Central Services
 Hostname , String , d52ascs
 FullQualifiedHostname , String , d52ascs.example.com
 IPAddress , String , 10.0.0.20
 SapVersionInfo , String , 749, patch 401, changelist 1806777
*********************************************************
 SID , String , D52
 SystemNumber , String , 54
 InstanceName , String , D54
 InstanceType , String , ABAP Dialog Instance
 Hostname , String , d52pas
 FullQualifiedHostname , String , d52pas.example.com
 IPAddress , String , 10.0.0.22
 SapVersionInfo , String , 749, patch 401, changelist 1806777
*********************************************************
 SID , String , SMA
 SystemNumber , String , 91
 InstanceName , String , SMDA91
 InstanceType , String , Solution Manager Diagnostic Agent
 Hostname , String , li-ld-1810
 FullQualifiedHostname , String , li-ld-1810.example.com
 IPAddress , String , 10.0.0.1
 SapVersionInfo , String , 749, patch 200, changelist 1746260
*********************************************************
 SID , String , B15
 SystemNumber , String , 00
 InstanceName , String , HDB00
 InstanceType , String , HANA
 Hostname , String , sapb15hdba1
 FullQualifiedHostname , String , li-ld-1810.example.com
 SapVersionInfo , String , 749, patch 418, changelist 1816226
'''

SAPHOSTCTRL_HOSTINSTANCES_BAD = '''
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String
'''


def test_saphostctrl_docs():
    globs = {
        'sap_inst': SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS))
    }
    failed, total = doctest.testmod(saphostctrl, globs=globs)
    assert failed == 0


def test_saphostctrl():
    sap = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD))
    assert len(sap) == 11
    assert sap.data[-3]['SapVersionInfo'] == '749, patch 401, changelist 1806777'
    assert sap[-3]['SapVersionInfo'] == '749, patch 401, changelist 1806777'
    assert sorted(sap.instances) == sorted([
        'HDB88', 'HDB90', 'ERS08', 'ASCS07', 'DVEBMGS09', 'SCS10', 'HDB62',
        'HDB00', 'ASCS52', 'D54', 'SMDA91'
    ])
    for sid in ['D89', 'D90', 'D79', 'D80', 'D62', 'D52', 'SMA']:
        assert sid in sap.sids
    assert sorted(sap.types) == sorted([
        'HDB', 'ERS', 'ASCS', 'DVEBMGS', 'SCS', 'D', 'SMDA'
    ])


def test_saphostctrl_old():
    sap = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS_OLD))
    assert sap.types == ['HDB']  # short types only
    assert sap[0]['InstanceType'] == 'HANA Test'
    assert sap[1]['InstanceType'] == 'HDB'


def test_saphostctrl_bad():
    with pytest.raises(SkipComponent):
        SAPHostCtrlInstances(context_wrap(''))

    with pytest.raises(ParseException):
        SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_BAD))
