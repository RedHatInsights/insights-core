import pytest

from insights.combiners.hostname import Hostname
from insights.combiners.sap import Sap
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.parsers.hostname import Hostname as HostnameParser
from insights.parsers.saphostctrl import SAPHostCtrlInstances
from insights.specs.datasources.sap import (LocalSpecs, ld_library_path_of_user, sap_hana_sid,
                                            sap_hana_sid_SID_nr, sap_sid)
from insights.tests.combiners.test_sap import (HOSTNAME1, SAPHOSTCTRL_HOSTINSTANCES_GOOD,
                                               SAPHOSTCTRL_HOSTINSTANCES_R_CASE)
from insights.tests import context_wrap

SAPHOSTCTRL_HOSTINSTANCES = '''
*********************************************************
 SID , String , RH1
 SystemNumber , String , 01
 InstanceName , String , ASCS01
 InstanceType , String , ABAP Central Services
 Hostname , String , vm37-39
 FullQualifiedHostname , String , vm37-39.pek2.com
 IPAddress , String , 10.72.37.39
 SapVersionInfo , String , 745, patch 100, changelist 1652052
*********************************************************
 SID , String , RH1
 SystemNumber , String , 00
 InstanceName , String , D00
 InstanceType , String , ABAP Dialog Instance
 Hostname , String , vm37-39
 FullQualifiedHostname , String , vm37-39.pek2.com
 IPAddress , String , 10.72.37.39
 SapVersionInfo , String , 745, patch 100, changelist 1652052
*********************************************************
 SID , String , SR1
 SystemNumber , String , 02
 InstanceName , String , HDB02
 InstanceType , String , HANA
 Hostname , String , vm37-39
 FullQualifiedHostname , String , vm37-39.pek2.com
 IPAddress , String , 10.72.37.39
 SapVersionInfo , String , 749, patch 418, changelist 1816226
*********************************************************
 SID , String , RH2
 SystemNumber , String , 04
 InstanceName , String , ASCS04
 InstanceType , String , ABAP Central Services
 Hostname , String , vm37-39
 FullQualifiedHostname , String , vm37-39.pek2.com
 IPAddress , String , 10.72.37.39
 SapVersionInfo , String , 745, patch 100, changelist 1652052
*********************************************************
 SID , String , RH2
 SystemNumber , String , 03
 InstanceName , String , D03
 InstanceType , String , ABAP Dialog Instance
 Hostname , String , vm37-39
 FullQualifiedHostname , String , vm37-39.pek2.com
 IPAddress , String , 10.72.37.39
 SapVersionInfo , String , 745, patch 100, changelist 1652052
'''.strip()

RH1ADM_ENV = '''
TERM=screen-256color
HOME=/home/rh1adm
SHELL=/bin/csh
USER=rh1adm
LOGNAME=rh1adm
PATH=/sapdb/clients/RH1/bin:/sapdb/programs/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/usr/sap/RH1/SYS/exe/run:/home/rh1adm:.
XDG_SESSION_ID=6682
HOSTTYPE=x86_64-linux
VENDOR=unknown
OSTYPE=linux
MACHTYPE=x86_64
SHLVL=1
PWD=/home/rh1adm
GROUP=sapsys
HOST=vm37-39
REMOTEHOST=10.66.136.143
MAIL=/var/spool/mail/rh1adm
HOSTNAME=vm37-39
LANG=en_US.UTF-8
LESSOPEN=||/usr/bin/lesspipe.sh %s
SAPSYSTEMNAME=RH1
DIR_LIBRARY=/usr/sap/RH1/SYS/exe/run
RSEC_SSFS_DATAPATH=/usr/sap/RH1/SYS/global/security/rsecssfs/data
RSEC_SSFS_KEYPATH=/usr/sap/RH1/SYS/global/security/rsecssfs/key
rsdb_ssfs_connect=0
LD_LIBRARY_PATH=/usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib
dbms_type=ADA
'''.strip()

RH2ADM_ENV = '''
TERM=screen-256color
HOME=/home/rh2adm
SHELL=/bin/csh
USER=rh2adm
LOGNAME=rh2adm
PATH=/sapdb/clients/RH2/bin:/sapdb/programs/bin:/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/usr/sap/RH2/SYS/exe/uc/linuxx86_64:/usr/sap/RH2/SYS/exe/run:/home/rh2adm:.
XDG_SESSION_ID=6682
HOSTTYPE=x86_64-linux
VENDOR=unknown
OSTYPE=linux
MACHTYPE=x86_64
SHLVL=1
PWD=/home/rh2adm
GROUP=sapsys
HOST=vm37-39
REMOTEHOST=10.66.136.143
MAIL=/var/spool/mail/rh2adm
HOSTNAME=vm37-39
LANG=en_US.UTF-8
LESSOPEN=||/usr/bin/lesspipe.sh %s
SAPSYSTEMNAME=RH2
DIR_LIBRARY=/usr/sap/RH2/SYS/exe/run
RSEC_SSFS_DATAPATH=/usr/sap/RH2/SYS/global/security/rsecssfs/data
RSEC_SSFS_KEYPATH=/usr/sap/RH2/SYS/global/security/rsecssfs/key
rsdb_ssfs_connect=0
LD_LIBRARY_PATH=/usr/sap/RH2/SYS/exe/run:/usr/sap/RH2/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH2/lib
dbms_type=ADA
'''.strip()

HOSTNAME = 'vm37-39.pek2.com'


class FakeContext(object):
    def shell_out(self, cmd, split=True, timeout=None, keep_rc=False, env=None, signum=None):
        tmp_cmd = cmd.strip().split()
        if 'rh1adm' in tmp_cmd[2]:
            return 0, RH1ADM_ENV.splitlines()
        if 'rh2adm' in tmp_cmd[2]:
            return 0, RH2ADM_ENV.splitlines()
        return -1, []


def test_hana_instance_skip():
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_R_CASE))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    with pytest.raises(SkipComponent):
        LocalSpecs.sap_hana_instance(broker)


def test_sid():
    # Good
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    result = sap_sid(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == sorted(set(v.sid.lower() for v in sap.values()))


def test_hana_sid():
    # Good
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    broker.update({LocalSpecs.sap_hana_instance: LocalSpecs.sap_hana_instance(broker)})
    result = sap_hana_sid(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == list(set(v.sid.lower() for v in sap.values() if v.type == 'HDB'))

    # Bad
    broker.update({LocalSpecs.sap_hana_instance: []})
    with pytest.raises(SkipComponent):
        sap_hana_sid(broker)


def test_hana_sid_SID_nr():
    # Good
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    broker.update({LocalSpecs.sap_hana_instance: LocalSpecs.sap_hana_instance(broker)})
    result = sap_hana_sid_SID_nr(broker)
    assert result is not None
    assert isinstance(result, list)
    assert result == list((v.sid.lower(), v.sid, v.number) for v in sap.values() if v.type == 'HDB')

    # Bad
    broker.update({LocalSpecs.sap_hana_instance: []})
    with pytest.raises(SkipComponent):
        sap_hana_sid_SID_nr(broker)


def test_ld_library_path_of_user():
    # Good
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap, HostContext: FakeContext()}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    broker.update({sap_sid: sap_sid(broker)})
    result = ld_library_path_of_user(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    assert sorted(result.content) == [
        'rh1adm /usr/sap/RH1/SYS/exe/run:/usr/sap/RH1/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH1/lib',
        'rh2adm /usr/sap/RH2/SYS/exe/run:/usr/sap/RH2/SYS/exe/uc/linuxx86_64:/sapdb/clients/RH2/lib',
    ]
    assert result.relative_path == 'insights_commands/echo_user_LD_LIBRARY_PATH'

    # Bad
    inst = SAPHostCtrlInstances(context_wrap(SAPHOSTCTRL_HOSTINSTANCES_GOOD))
    hn = Hostname(HostnameParser(context_wrap(HOSTNAME1)), None, None, None)
    sap = Sap(hn, inst, None)
    broker = {Sap: sap, HostContext: FakeContext()}
    broker.update({LocalSpecs.sap_instance: LocalSpecs.sap_instance(broker)})
    broker.update({sap_sid: sap_sid(broker)})
    with pytest.raises(SkipComponent):
        result = ld_library_path_of_user(broker)
        assert result is None
