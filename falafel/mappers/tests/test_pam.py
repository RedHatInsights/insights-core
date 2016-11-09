import pytest
from falafel.mappers.pam import PamConf, PamDConf, PamConfEntry
from falafel.tests import context_wrap

PAM_CONF_DATA = """
#%PAM-1.0
vsftpd      auth        required    pam_securetty.so
vsftpd      auth        requisite   pam_unix.so nullok
vsftpd      auth        sufficient  pam_nologin.so
vsftpd      account     optional    pam_unix.so
other       password    include     pam_cracklib.so retry=3 logging=verbose
other       password    required    pam_unix.so shadow nullok use_authtok
other       session     required    pam_unix.so
""".strip()
PAMD_CONF_DATA = """
#%PAM-1.0
auth        required    pam_securetty.so
auth        requisite   pam_unix.so nullok
auth        sufficient  pam_nologin.so
auth        [success=2 default=ok]  pam_debug.so auth=perm_denied cred=success
account     optional    pam_unix.so
password    include     pam_cracklib.so retry=3 logging=verbose
password    required    pam_unix.so shadow nullok use_authtok
auth        required    pam_listfile.so \
                   onerr=succeed item=user sense=deny file=/etc/ftpusers
session     required    pam_unix.so
""".strip()
PAMD_CONF_DATA_BAD_INTERFACE = """
#%PAM-1.0
authz       required    pam_securetty.so
auth        requisite   pam_unix.so nullok
""".strip()
PAMD_CONF_DATA_BAD_FLAG = """
#%PAM-1.0
auth        preferred   pam_securetty.so
auth        requisite   pam_unix.so nullok
""".strip()
PAMD_CONF_DATA_BAD_MODULE = """
#%PAM-1.0
auth        required
auth        requisite   pam_unix.so nullok
""".strip()
PAMD_MISC = """
password  required pam_cracklib.so \
                       difok=3 minlen=15 dcredit= 2 ocredit=2
auth    requisite       pam_permit.so
auth    [success=2 default=ok]  pam_debug.so auth=perm_denied cred=success
auth    [default=reset]         pam_debug.so auth=success cred=perm_denied
auth    [success=done default=die] pam_debug.so
auth    optional        pam_debug.so auth=perm_denied cred=perm_denied
auth    sufficient      pam_debug.so auth=success cred=success
auth    required    pam_listfile.so \
                   onerr=succeed item=user sense=deny file=/etc/ftpusers
password optional pam_exec.so seteuid /usr/bin/make -C /var/yp
""".strip()


def test_pamd_conf():

    pam_conf = PamConf(context_wrap(PAM_CONF_DATA))
    assert len(pam_conf) == 7
    assert pam_conf[0].service == 'vsftpd'
    assert pam_conf[0].interface == 'auth'
    assert len(pam_conf[0].control_flags) == 1
    assert pam_conf[0].control_flags[0].flag == 'required'
    assert pam_conf[0].control_flags[0].value is None
    assert pam_conf[0].module_name == 'pam_securetty.so'
    assert pam_conf[0].module_args is None

    assert pam_conf[5].service == 'other'
    assert pam_conf[5].interface == 'password'
    assert len(pam_conf[5].control_flags) == 1
    assert pam_conf[5].control_flags[0].flag == 'required'
    assert pam_conf[5].control_flags[0].value is None
    assert pam_conf[5].module_name == 'pam_unix.so'
    assert pam_conf[5].module_args == "shadow nullok use_authtok"

    pamd_conf = PamDConf(context_wrap(PAMD_CONF_DATA, path='etc/pamd.d/vsftpd'))
    assert len(pamd_conf) == 9
    assert pamd_conf[0].service == 'vsftpd'
    assert pamd_conf[0].interface == 'auth'
    assert len(pamd_conf[0].control_flags) == 1
    assert pamd_conf[0].control_flags[0].flag == 'required'
    assert pamd_conf[0].control_flags[0].value is None
    assert pamd_conf[0].module_name == 'pam_securetty.so'
    assert pamd_conf[0].module_args is None

    # auth        [success=2 default=ok]  pam_debug.so auth=perm_denied cred=success
    assert len(pamd_conf[3].control_flags) == 2
    assert pamd_conf[3].control_flags == [PamConfEntry.ControlFlag(flag='success', value='2'),
                                          PamConfEntry.ControlFlag(flag='default', value='ok')]

    # auth        required    pam_listfile.so \
    #                   onerr=succeed item=user sense=deny file=/etc/ftpusers
    assert pamd_conf[7].interface == 'auth'
    assert len(pamd_conf[7].control_flags) == 1
    assert pamd_conf[7].control_flags[0].flag == 'required'
    assert pamd_conf[7].control_flags[0].value is None
    assert pamd_conf[7].module_name == 'pam_listfile.so'
    assert pamd_conf[7].module_args == 'onerr=succeed item=user sense=deny file=/etc/ftpusers'

    with pytest.raises(ValueError):
        pamd_conf = PamDConf(context_wrap(PAMD_CONF_DATA_BAD_MODULE))
