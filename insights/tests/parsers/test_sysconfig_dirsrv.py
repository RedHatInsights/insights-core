from insights.parsers.sysconfig import DirsrvSysconfig
from insights.tests import context_wrap

SYSCONFIG = """
# how many seconds to wait for the startpid file to show
# up before we assume there is a problem and fail to start
# if using systemd, omit the "; export VARNAME" at the end
#STARTPID_TIME=10 ; export STARTPID_TIME
# how many seconds to wait for the pid file to show
# up before we assume there is a problem and fail to start
# if using systemd, omit the "; export VARNAME" at the end
#PID_TIME=600 ; export PID_TIME
KRB5CCNAME=/tmp/krb5cc_995
KRB5_KTNAME=/etc/dirsrv/ds.keytab
"""


def test_dirsrv_sysconfig():
    syscfg = DirsrvSysconfig(context_wrap(SYSCONFIG))
    # Standard access through data
    assert 'PID_TIME' not in syscfg.data
    assert syscfg.data['KRB5CCNAME'] == '/tmp/krb5cc_995'
    assert syscfg.data['KRB5_KTNAME'] == '/etc/dirsrv/ds.keytab'
    # pseudo-dictionary accessor
    assert syscfg['KRB5CCNAME'] == '/tmp/krb5cc_995'
    assert syscfg['KRB5_KTNAME'] == '/etc/dirsrv/ds.keytab'
    # No unparsed lines
    assert syscfg.unparsed_lines == []
