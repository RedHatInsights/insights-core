from insights.parsers.vsftpd import VsftpdConf, VsftpdPamConf
from insights.tests import context_wrap

VSFTPD_PAM_CONF = """
#%PAM-1.0
session    optional     pam_keyinit.so    force revoke
auth       required     pam_listfile.so item=user sense=deny file=/etc/vsftpd/ftpusers onerr=succeed
auth       required     pam_shells.so
auth       include      password-auth
account    include      password-auth
session    required     pam_loginuid.so
session    include      password-auth
""".strip()

VSFTPD_CONF = """
# No anonymous login
anonymous_enable=NO
# Let local users login
local_enable=YES

# Write permissions
write_enable=YES
# Commented_option=not_present
""".strip()


def test_vsftpd_pam_conf():
    pam_conf = VsftpdPamConf(context_wrap(VSFTPD_PAM_CONF, path='etc/pamd.d/vsftpd'))
    assert len(pam_conf) == 7
    assert pam_conf[0].service == 'vsftpd'
    assert pam_conf[0].interface == 'session'
    assert len(pam_conf[0].control_flags) == 1
    assert pam_conf[0].control_flags[0].flag == 'optional'
    assert pam_conf[0].module_name == 'pam_keyinit.so'
    assert pam_conf[0].module_args == 'force revoke'
    assert pam_conf[1].module_args == 'item=user sense=deny file=/etc/vsftpd/ftpusers onerr=succeed'
    assert pam_conf[6].interface == 'session'
    assert len(pam_conf[6].control_flags) == 1
    assert pam_conf[6].control_flags[0].flag == 'include'
    assert pam_conf[6].module_name == 'password-auth'
    assert pam_conf[6].module_args is None


def test_vsftpd_conf():
    vsftpd_conf = VsftpdConf(context_wrap(VSFTPD_CONF))
    assert vsftpd_conf.get('anonymous_enable') == 'NO'
    assert vsftpd_conf.get('local_enable') == 'YES'
    assert vsftpd_conf.get('write_enable') == 'YES'
    assert 'Commented_option' not in vsftpd_conf
