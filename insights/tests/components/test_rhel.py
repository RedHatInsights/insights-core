from insights.components.rhel import RHEL
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.subscription_manager import SubscriptionManagerID
from insights.parsers.uname import Uname
from insights.tests import context_wrap


RHSM_ID = """
system identity: 00000000-8f8c-4cb1-8023-111111111111
name: rhel7.localdomain
org name: 1234567
org ID: 1234567
""".strip()

UNAME_79 = "Linux vm-123 3.10.0-957.61.2.el7.x86_64 #1 SMP Sat Oct 17 16:03:06 EDT 2020 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_86 = "Linux vm-123 4.18.0-372.19.1.el8_6.x86_64 #1 SMP Mon Jul 18 11:14:02 EDT 2022 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_91 = "Linux vm-123 5.14.0-162.6.1.el9_1.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Sep 30 07:36:03 EDT 2022 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_NG = "Linux vm-123 5.14.0-10.1.el9.x86_64 #1 SMP PREEMPT RT Thu Oct 29 21:54:23 EDT 2015 x86_64 x86_64 x86_64 GNU/Linux"

RPMS_JSON_9 = '''
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"10.1.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 199e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"70.26.1.el9_0", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 199e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"162.6.1.el9_1", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 03 Oct 2022 04:18:36 PM CST, Key ID 199e2f91fd431d51"}
'''.strip()

RPMS_JSON_NG = '''
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"70.26.1.el9_0", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 99e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"162.6.1.el9_1", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 03 Oct 2022 04:18:36 PM CST, Key ID 99e2f91fd431d51"}
'''.strip()

RPMS_JSON_OL = '''
{"name":"kernel", "epoch":"(none)", "version":"4.18.0", "release":"425.3.1.el8", "arch":"x86_64", "vendor":"Oracle America", "sigpgp":"RSA/SHA256, Tue Nov  8 18:10:54 2022, Key ID 82562ea9ad986da3"}
{"name":"kernel", "epoch":"(none)", "version":"4.18.0", "release":"305.19.1.el8_4", "arch":"x86_64", "vendor":"Oracle America", "sigpgp":"RSA/SHA256, Wed Sep 15 17:11:22 2021, Key ID 82562ea9ad986da3"}
'''.strip()

REDHAT_RELEASE_79 = """
Red Hat Enterprise Linux Server release 7.9 (Maipo)
""".strip()

REDHAT_RELEASE_86 = """
Red Hat Enterprise Linux release 8.6 (Ootpa)
""".strip()

REDHAT_RELEASE_91 = """
Red Hat Enterprise Linux release 9.1 (Plow)
""".strip()

REDHAT_RELEASE_FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()

REDHAT_RELEASE_OL = """
Red Hat Enterprise Linux release 8.6 (Ootpa)
""".strip()

OS_RELEASE_RH = """
NAME="Red Hat Enterprise Linux"
ID="rhel"
""".strip()

OS_RELEASE_OL = """
NAME="Oracle Linux Server"
ID="ol"
""".strip()


# RHEL Test
def test_is_rhel():
    # RHSM Registered RHEL 7
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_79))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_79))
    rhsm_id = SubscriptionManagerID(context_wrap(RHSM_ID))
    result = RHEL(uname, rhr, osr, rhsm_id, None)
    assert result.is_rhel is True

    # RHSM Registered RHEL 8
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_86))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_86))
    rhsm_id = SubscriptionManagerID(context_wrap(RHSM_ID))
    result = RHEL(uname, rhr, osr, rhsm_id, None)
    assert result.is_rhel is True

    # RHSM Registered RHEL 9
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_91))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_91))
    rhsm_id = SubscriptionManagerID(context_wrap(RHSM_ID))
    result = RHEL(uname, rhr, osr, rhsm_id, None)
    assert result.is_rhel is True

    # No RHSM Registered RHEL 9
    rpms = InstalledRpms(context_wrap(RPMS_JSON_9))
    result = RHEL(uname, rhr, osr, None, rpms)
    assert result.is_rhel is True


def test_not_rhel():
    # Nothing
    result = RHEL(None, None, None, None, None)
    assert result.is_rhel is False

    # /etc/redhat_release: Fedora
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_FEDORA))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_79))
    result = RHEL(uname, rhr, osr, None, None)
    assert result.is_rhel is False

    # OLE
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_OL))
    osr = OsRelease(context_wrap(OS_RELEASE_OL))
    uname = Uname(context_wrap(UNAME_86))
    result = RHEL(uname, rhr, osr, None, None)
    assert result.is_rhel is False

    # RHEL 9: unregistered, unsigned kernel
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_91))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_91))
    rpms = InstalledRpms(context_wrap(RPMS_JSON_NG))
    result = RHEL(uname, rhr, osr, None, rpms)
    assert result.is_rhel is False

    # unknown Uname
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_91))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_NG))
    rpms = InstalledRpms(context_wrap(RPMS_JSON_9))
    result = RHEL(uname, rhr, osr, None, rpms)
    assert result.is_rhel is False

    # Is it possible, that RHEL is registered but run a unsigned kernel?
    pass
