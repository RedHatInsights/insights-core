from ...parsers import saphostctrl_instances
from ...tests import context_wrap
from doctest import testmod

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
'''


def test_saphostctrl_docs():
    parser_under_test = saphostctrl_instances.SAPHostInstances(
        context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS)
    )
    globs = {
        'SAPHostInstances': saphostctrl_instances.SAPHostInstances,
        'shared': {
            saphostctrl_instances.SAPHostInstances: parser_under_test,
        },
        'instances': parser_under_test,
    }
    failed, total = testmod(saphostctrl_instances, globs=globs)
    assert failed == 0


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


def test_saphostctrl():
    sap = saphostctrl_instances.SAPHostInstances(
        context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD)
    )
    assert hasattr(sap, 'data')
    assert isinstance(sap.data, list)
    assert len(sap.data) == 10
    assert hasattr(sap, 'running_inst_types')
    assert isinstance(sap.running_inst_types, set)
    assert hasattr(sap, 'ignored_lines')
    assert isinstance(sap.ignored_lines, list)
    assert sap.ignored_lines == []

    # Test Lssap-compatible properties
    assert sap.version('D54') == '749, patch 401, changelist 1806777'
    assert sap.version('D55') is None
    assert sap.instances == [
        'HDB88', 'HDB90', 'ERS08', 'ASCS07', 'DVEBMGS09', 'SCS10', 'HDB62',
        'ASCS52', 'D54', 'SMDA91'
    ]
    # Can't test sid content directly because it's using a set and the output
    # is in random order.
    # assert sap.sid == [
    #     'D89', 'D90', 'D79', 'D79', 'D79', 'D80', 'D62', 'D52', 'D52', 'SMA'
    # ]
    for sid in ['D89', 'D90', 'D79', 'D80', 'D62', 'D52', 'SMA']:
        assert sid in sap.sid
    assert sap.is_netweaver()
    assert sap.is_hana()
    assert sap.is_ascs()

    # Test search interface


SAPHOSTCTRL_HOSTINSTANCES_BAD = '''
 CreationClassName , String
 SID , String , D89
 SystemNumber , String , 88
'''


def test_saphostctrl_bad():
    sap = saphostctrl_instances.SAPHostInstances(
        context_wrap(SAPHOSTCTRL_HOSTINSTANCES_BAD)
    )
    assert hasattr(sap, 'data')
    assert isinstance(sap.data, list)
    assert len(sap.data) == 1
    assert hasattr(sap, 'running_inst_types')
    assert isinstance(sap.running_inst_types, set)
    assert sap.running_inst_types == set()
    assert hasattr(sap, 'ignored_lines')
    assert isinstance(sap.ignored_lines, list)
    assert sap.ignored_lines == ['CreationClassName , String']

    sap = saphostctrl_instances.SAPHostInstances(context_wrap(''))
    assert hasattr(sap, 'data')
    assert isinstance(sap.data, list)
    assert sap.data == []
    assert hasattr(sap, 'running_inst_types')
    assert isinstance(sap.running_inst_types, set)
    assert sap.running_inst_types == set()
    assert hasattr(sap, 'ignored_lines')
    assert isinstance(sap.ignored_lines, list)
    assert sap.ignored_lines == []
