from insights.components.rhel import RHEL
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.subscription_manager import SubscriptionManagerID
from insights.parsers.uname import Uname
from insights.tests import context_wrap


UNAME = "Linux localhost.localdomain 3.10.0-327.204.el7.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

RHSM_ID = """
system identity: 00000000-8f8c-4cb1-8023-111111111111
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
""".strip()

RPMS_JSON_RH = '''
{"name":"kernel", "epoch":"(none)", "version":"3.10.0", "release":"327.204.el7", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 199e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"3.10.0", "release":"327.204.1.el7", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 199e2f91fd431d51"}
'''.strip()

RPMS_JSON_OL = '''
{"name":"kernel", "epoch":"(none)", "version":"3.10.0", "release":"327.204.el7", "arch":"x86_64", "vendor":"Oracle America", "sigpgp":"RSA/SHA256, Tue Nov  8 18:10:54 2022, Key ID 82562ea9ad986da3"}
{"name":"kernel", "epoch":"(none)", "version":"4.18.0", "release":"425.3.1.el8", "arch":"x86_64", "vendor":"Oracle America", "sigpgp":"RSA/SHA256, Tue Nov  8 18:10:54 2022, Key ID 82562ea9ad986da3"}
'''.strip()


# RHEL Test
def test_is_rhel():
    uname = Uname(context_wrap(UNAME))
    rhsm_id = SubscriptionManagerID(context_wrap(RHSM_ID))
    result = RHEL(uname, rhsm_id, None)
    assert isinstance(result, RHEL)
    assert result.is_rhel is True

    rpms = InstalledRpms(context_wrap(RPMS_JSON_RH))
    result = RHEL(uname, None, rpms)
    assert isinstance(result, RHEL)
    assert result.is_rhel is True


def test_not_rhel():
    rpms = InstalledRpms(context_wrap(RPMS_JSON_OL))
    uname = Uname(context_wrap(UNAME))
    result = RHEL(uname, None, rpms)
    assert isinstance(result, RHEL)
    assert result.is_rhel is False

    result = RHEL(None, None, None)
    assert isinstance(result, RHEL)
    assert result.is_rhel is False
