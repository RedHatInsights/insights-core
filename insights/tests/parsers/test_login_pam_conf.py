import doctest
from insights.parsers import login_pam_conf
from insights.parsers.login_pam_conf import LoginPamConf
from insights.tests import context_wrap

LOGIN_PAM_CONF = """
#%PAM-1.0
auth [user_unknown=ignore success=ok ignore=ignore default=bad] pam_securetty.so
auth       substack     system-auth
auth       include      postlogin
account    required     pam_nologin.so
account    include      system-auth
password   include      system-auth
# pam_selinux.so close should be the first session rule
session    required     pam_selinux.so close
session    required     pam_loginuid.so
session    optional     pam_console.so
""".strip()


def test_login_pam_conf():
    pam_conf = LoginPamConf(context_wrap(LOGIN_PAM_CONF, path='etc/pamd.d/login'))
    assert len(pam_conf) == 9
    assert pam_conf[0].service == 'login'
    assert pam_conf[0].interface == 'auth'
    assert len(pam_conf[0].control_flags) == 4
    assert pam_conf[0].control_flags[0].flag == 'user_unknown'
    assert pam_conf[0].control_flags[0].value == 'ignore'
    assert pam_conf[0].module_name == 'pam_securetty.so'
    assert pam_conf[6].interface == 'session'
    assert pam_conf[6].module_args == 'close'


def test_doc():
    env = {
        "login_pam_conf": LoginPamConf(context_wrap(LOGIN_PAM_CONF)),
    }
    failed_count, total = doctest.testmod(login_pam_conf, globs=env)
    assert failed_count == 0
