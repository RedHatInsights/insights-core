from ...parsers import saphostctrl, ParseException, SkipException
from ...parsers.saphostctrl import SAPHostCtrlInstances
from ...tests import context_wrap
import doctest
import pytest

SAPHOSTCTRL_HOSTINSTANCES_DOCS = '''
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D89
 SystemNumber , String , 88
 InstanceName , String , HDB88
 Hostname , String , hdb88
 FullQualifiedHostname , String , hdb88.example.com
 IPAddress , String , 10.0.0.88
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
 CreationClassName , String , SAPInstance
 SID , String , D90
 SystemNumber , String , 90
 InstanceName , String , HDB90
 Hostname , String , hdb90
 FullQualifiedHostname , String , hdb90.example.com
 IPAddress , String , 10.0.0.90
 SapVersionInfo , String , 749, patch 211, changelist 1754007
*********************************************************
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
'''

SAPHOSTCTRL_HOSTINSTANCES_BAD = '''
 CreationClassName , String
 SID , String , D89
 SystemNumber , String , 88
'''

SAPHOSTCTRL_HOSTINSTANCES_BAD1 = '''
 CreationClassName , String , SAPInstance
 SID , String , D89
 SystemNumber , String , 88
'''


def test_saphostctrl_docs():
    globs = {
        'sap_inst': SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS))
    }
    failed, total = doctest.testmod(saphostctrl, globs=globs)
    assert failed == 0


def test_saphostctrl():
    sap = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD))
    assert len(sap) == 10
    assert sap.data[-2]['SapVersionInfo'] == '749, patch 401, changelist 1806777'
    assert sorted(sap.instances) == sorted([
        'HDB88', 'HDB90', 'ERS08', 'ASCS07', 'DVEBMGS09', 'SCS10', 'HDB62',
        'ASCS52', 'D54', 'SMDA91'
    ])
    for sid in ['D89', 'D90', 'D79', 'D80', 'D62', 'D52', 'SMA']:
        assert sid in sap.sids
    assert sorted(sap.types) == sorted([
        'HDB', 'ERS', 'ASCS', 'DVEBMGS', 'SCS', 'D', 'SMDA'
    ])


def test_saphostctrl_bad():
    with pytest.raises(ParseException) as pe:
        SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_BAD))
    assert "Incorrect line: 'CreationClassName , String'" in str(pe)

    with pytest.raises(SkipException) as pe:
        SAPHostCtrlInstances(context_wrap(''))
    assert "Empty content" in str(pe)

    with pytest.raises(ParseException) as pe:
        SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_BAD1))
    assert "Incorrect content." in str(pe)
