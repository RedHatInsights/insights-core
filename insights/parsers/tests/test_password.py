from insights.parsers.password import PasswordAuthPam
from insights.parsers.pam import PamConfEntry
from insights.tests import context_wrap

PW_AUTH_PAM_CONF = """
#%PAM-1.0
# This file is auto-generated.
# User changes will be destroyed the next time authconfig is run.
auth        required      pam_env.so
auth        sufficient    pam_unix.so nullok try_first_pass
auth        requisite     pam_succeed_if.so uid >= 500 quiet
auth        required      pam_deny.so
auth        [default=die] pam_faillock.so authfail deny=3 unlock_time=604800 fail_interval=900
auth        required      pam_faillock.so authsucc deny=3 unlock_time=604800 fail_interval=900

account     required      pam_unix.so
account     sufficient    pam_localuser.so
account     sufficient    pam_succeed_if.so uid < 500 quiet
account     required      pam_permit.so

password    requisite     pam_cracklib.so try_first_pass retry=3 lcredit=-1 ucredit=-1 dcredit=-1 ocredit=-1 minlen=12
password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok
password    required      pam_deny.so

session     optional      pam_keyinit.so revoke
session     required      pam_limits.so
session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
session     required      pam_unix.so
""".strip()


def test_password_auth_pam_conf():
    pam_conf = PasswordAuthPam(context_wrap(PW_AUTH_PAM_CONF, path='etc/pam.d/password-auth'))
    assert len(pam_conf) == 17
    assert pam_conf[0].service == 'password-auth'
    assert pam_conf[0].interface == 'auth'
    assert len(pam_conf[0].control_flags) == 1
    assert pam_conf[0].control_flags[0].flag == 'required'
    assert pam_conf[0].module_name == 'pam_env.so'
    assert pam_conf[0].module_args is None

    # session     [success=1 default=ignore] pam_succeed_if.so service in crond quiet use_uid
    assert pam_conf[15].interface == 'session'
    assert len(pam_conf[15].control_flags) == 2
    assert pam_conf[15].control_flags == [PamConfEntry.ControlFlag(flag='success', value='1'),
                                         PamConfEntry.ControlFlag(flag='default', value='ignore')]
    assert pam_conf[15].module_name == 'pam_succeed_if.so'
    assert pam_conf[15].module_args == 'service in crond quiet use_uid'
