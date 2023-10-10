import doctest

from insights.combiners import sap
from insights.combiners.hostname import Hostname
from insights.combiners.sap import Sap
from insights.parsers.hostname import Hostname as HnF
from insights.parsers.saphostctrl import SAPHostCtrlInstances
from insights.tests import context_wrap
from insights.tests.parsers.test_saphostctrl import SAPHOSTCTRL_HOSTINSTANCES_DOCS, SAPHOSTCTRL_HOSTINSTANCES_GOOD

HOSTNAME = 'lu0417.example.com'
HOSTNAME1 = 'li-ld-1810.example.com'
HOSTNAME2 = 'host_1.example.corp'
HOSTNAME3 = 'host_2.example.corp'

SAPHOSTCTRL_HOSTINSTANCES_R_CASE = '''
*********************************************************
 SID , String , R4D
 SystemNumber , String , 12
 InstanceName , String , DVEBMGS12
 InstanceType , String , Primary Application Server
 Hostname , String , host_1
 FullQualifiedHostname , String , host_1.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , R4D
 SystemNumber , String , 10
 InstanceName , String , ASCS10
 InstanceType , String , ABAP Central Services
 Hostname , String , host_1
 FullQualifiedHostname , String , host_1.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , WDX
 SystemNumber , String , 20
 InstanceName , String , W20
 InstanceType , String , WebDispatcher
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 773, patch 121, changelist 1917131
*********************************************************
 SID , String , SMD
 SystemNumber , String , 98
 InstanceName , String , SMDA98
 InstanceType , String , Solution Manager Diagnostic Agent
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
*********************************************************
 SID , String , SMD
 SystemNumber , String , 97
 InstanceName , String , SMDA97
 InstanceType , String , Solution Manager Diagnostic Agent
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
'''
SAPHOSTCTRL_HOSTINSTANCES_R_CASE_WO_TYPE = '''
*********************************************************
 SID , String , R4D
 SystemNumber , String , 12
 InstanceName , String , DVEBMGS12
 Hostname , String , host_1
 FullQualifiedHostname , String , host_1.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , R4D
 SystemNumber , String , 10
 InstanceName , String , ASCS10
 Hostname , String , host_1
 FullQualifiedHostname , String , host_1.example.corp
 SapVersionInfo , String , 753, patch 501, changelist 1967207
*********************************************************
 SID , String , WDX
 SystemNumber , String , 20
 InstanceName , String , W20
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 773, patch 121, changelist 1917131
*********************************************************
 SID , String , SMD
 SystemNumber , String , 98
 InstanceName , String , SMDA98
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
*********************************************************
 SID , String , SMD
 SystemNumber , String , 97
 InstanceName , String , SMDA97
 Hostname , String , host_2
 FullQualifiedHostname , String , host_2.example.corp
 SapVersionInfo , String , 745, patch 400, changelist 1734487
'''


def test_saphostcrtl_hana():
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_DOCS))
    hn = Hostname(HnF(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst)
    assert 'D50' not in sap
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
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD))
    hn = Hostname(HnF(context_wrap(HOSTNAME1)), None, None, None)
    sap = Sap(hn, inst)
    assert 'D50' not in sap
    assert 'HDB00' in sap
    assert sorted(sap.all_instances) == sorted([
        'ASCS07', 'ASCS52', 'D54', 'DVEBMGS09', 'ERS08', 'HDB00', 'HDB62',
        'HDB88', 'HDB90', 'SCS10', 'SMDA91'])
    assert sorted(sap.instances) == sorted([
        'ASCS07', 'ASCS52', 'D54', 'DVEBMGS09', 'ERS08', 'HDB00', 'HDB62',
        'HDB88', 'HDB90', 'SCS10'])
    assert sorted(sap.daa_instances) == sorted(['SMDA91'])
    assert sap['HDB88'].number == '88'
    assert sap['HDB90'].hostname == 'li-ld-1810'
    assert sap['DVEBMGS09'].version == '749, patch 301, changelist 1779613'
    assert sap.version('HDB90') == '749, patch 211, changelist 1754007'
    assert sap.hostname('HDB62') == 'd62dbsrv'
    assert sap.type('SCS10') == 'SCS'  # noqa E721
    assert sap.full_type('SCS10') == 'Java Central Services'
    assert sap.is_netweaver is True
    assert sap.is_hana is True
    assert sap.is_ascs is True


def test_r_case():
    saphostctrl = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE))
    hn = Hostname(HnF(context_wrap(HOSTNAME3)), None, None, None)
    sap = Sap(hn, saphostctrl)
    assert sap['DVEBMGS12'].version == '753, patch 501, changelist 1967207'
    assert sap['ASCS10'].hostname == 'host_1'
    assert len(sap.daa_instances) == 2
    assert len(sap.instances) == 3
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_r_case_wo_type():
    saphostctrl = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE_WO_TYPE))
    hn = Hostname(HnF(context_wrap(HOSTNAME3)), None, None, None)
    sap = Sap(hn, saphostctrl)
    assert sap['DVEBMGS12'].version == '753, patch 501, changelist 1967207'
    assert sap['ASCS10'].hostname == 'host_1'
    assert len(sap.daa_instances) == 2
    assert len(sap.instances) == 3
    assert sap.is_netweaver is True
    assert sap.is_hana is False
    assert sap.is_ascs is True


def test_doc_examples():
    env = {
            'saps': Sap(
                Hostname(HnF(context_wrap(HOSTNAME3)), None, None, None),
                SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE))
            )
          }
    failed, total = doctest.testmod(sap, globs=env)
    assert failed == 0
