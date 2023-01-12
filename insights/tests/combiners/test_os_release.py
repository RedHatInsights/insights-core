from insights.combiners.os_release import OSRelease, RHEL_STR
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.os_release import OsRelease
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.uname import Uname
from insights.tests import context_wrap

UNAME_86 = "Linux vm-123 4.18.0-372.19.1.el8_6.x86_64 #1 SMP Mon Jul 18 11:14:02 EDT 2022 x86_64 x86_64 x86_64 GNU/Linux"
UNAME_91 = "Linux vm-123 5.14.0-162.6.1.el9_1.x86_64 #1 SMP PREEMPT_DYNAMIC Fri Sep 30 07:36:03 EDT 2022 x86_64 x86_64 x86_64 GNU/Linux"

RPMS_JSON_91_WO_KERNEL = '''
{"name":"systemd", "epoch":"(none)", "version":"250", "release":"12.el9_1", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu 29 Sep 2022 05:02:47 PM CST, Key ID 199e2f91fd431d51"}
{"name":"filesystem", "epoch":"(none)", "version":"3.16", "release":"2.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Sat Nov 20 19:51:43 2021, Key ID 199e2f91fd431d51"}
{"name":"basesystem", "epoch":"(none)", "version":"11", "release":"13.el9", "arch":"noarch", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Sat Nov 20 18:50:43 2021, Key ID 199e2f91fd431d51"}
{"name":"gmp", "epoch":"1", "version":"6.2.0", "release":"10.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Sun Nov 21 16:04:10 2021, Key ID 199e2f91fd431d51"}
{"name":"dmidecode", "epoch":"1", "version":"3.3", "release":"7.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Tue Mar 15 15:41:19 2022, Key ID 199e2f91fd431d51"}
{"name":"libacl", "epoch":"(none)", "version":"2.3.1", "release":"3.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Sun Nov 21 08:14:00 2021, Key ID 199e2f91fd431d51"}
{"name":"libgcc", "epoch":"(none)", "version":"11.3.1", "release":"2.1.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu Jul 14 22:56:25 2022, Key ID 199e2f91fd431d51"}
{"name":"bash", "epoch":"(none)", "version":"5.1.8", "release":"5.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu Aug 25 21:46:10 2022, Key ID 199e2f91fd431d51"}
{"name":"glibc", "epoch":"(none)", "version":"2.34", "release":"40.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu Jul 28 15:15:24 2022, Key ID 199e2f91fd431d51"}
{"name":"libselinux", "epoch":"(none)", "version":"3.4", "release":"3.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Tue Jul 26 15:17:57 2022, Key ID 199e2f91fd431d51"}
{"name":"coreutils", "epoch":"(none)", "version":"8.32", "release":"32.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu Jun 16 12:19:44 2022, Key ID 199e2f91fd431d51"}
{"name":"policycoreutils", "epoch":"(none)", "version":"3.4", "release":"4.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Tue Sep 13 16:46:26 2022, Key ID 199e2f91fd431d51"}
{"name":"dbus", "epoch":"1", "version":"1.12.20", "release":"6.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Tue Aug 23 23:01:36 2022, Key ID 199e2f91fd431d51"}
{"name":"dracut", "epoch":"(none)", "version":"057", "release":"13.git20220816.el9", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Wed Aug 17 08:06:56 2022, Key ID 199e2f91fd431d51"}
{"name":"firewalld", "epoch":"(none)", "version":"1.1.1", "release":"3.el9", "arch":"noarch", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon Aug  8 21:31:26 2022, Key ID 199e2f91fd431d51"}
'''.strip()

RPMS_JSON_91_W_KERNEL = RPMS_JSON_91_WO_KERNEL + """
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"70.13.1.el9_0", "arch":"x86_64", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Mon 05 Sep 2022 09:55:09 PM CST, Key ID 199e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"5.14.0", "release":"162.6.1.el9_1", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 03 Oct 2022 04:18:36 PM CST, Key ID 199e2f91fd431d51"}"""

RPMS_JSON_8_NG = '''
{"name":"kernel", "epoch":"(none)", "version":"4.18.0", "release":"425.3.1.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Tue Nov  8 18:10:54 2022, Key ID 199e2f91fd431d51"}
{"name":"kernel", "epoch":"(none)", "version":"4.18.0", "release":"372.19.1.el8_6", "arch":"x86_64", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Wed Sep 15 17:11:22 2021, Key ID 199e2f91fd431d51"}
{"name":"libselinux", "epoch":"(none)", "version":"2.9", "release":"6.el8", "arch":"i686", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Mon 15 Aug 2022 08:55:09 PM CST, Key ID 199e2f91fd431d51"}
{"name":"dbus", "epoch":"1", "version":"1.12.8", "release":"23.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Wed 07 Sep 2022 04:08:12 AM CST, Key ID 199e2f91fd431d51"}
{"name":"dracut", "epoch":"(none)", "version":"049", "release":"209.git20220815.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 15 Aug 2022 09:56:58 PM CST, Key ID 199e2f91fd431d51"}
{"name":"libgcc", "epoch":"(none)", "version":"8.5.0", "release":"15.el8", "arch":"x86_64", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Thu 21 Jul 2022 05:36:25 PM CST, Key ID 199e2f91fd431d51"}
{"name":"policycoreutils", "epoch":"(none)", "version":"2.9", "release":"20.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 15 Aug 2022 08:51:06 PM CST, Key ID 199e2f91fd431d51"}
{"name":"glibc", "epoch":"(none)", "version":"2.28", "release":"211.el8", "arch":"x86_64", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Mon 29 Aug 2022 04:13:20 PM CST, Key ID 199e2f91fd431d51"}
{"name":"libacl", "epoch":"(none)", "version":"2.2.53", "release":"1.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Sat 15 Dec 2018 05:44:36 AM CST, Key ID 199e2f91fd431d51"}
{"name":"glibc", "epoch":"(none)", "version":"2.28", "release":"211.el8", "arch":"i686", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Mon 29 Aug 2022 04:12:26 PM CST, Key ID 199e2f91fd431d51"}
{"name":"libgcc", "epoch":"(none)", "version":"8.5.0", "release":"15.el8", "arch":"i686", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu 21 Jul 2022 05:36:01 PM CST, Key ID 199e2f91fd431d51"}
{"name":"bash", "epoch":"(none)", "version":"4.4.20", "release":"4.el8_6", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 20 Jun 2022 09:20:51 PM CST, Key ID 99e2f91fd431d51"}
{"name":"libselinux", "epoch":"(none)", "version":"2.9", "release":"6.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 15 Aug 2022 08:55:11 PM CST, Key ID 09e2f91fd431d51"}
{"name":"coreutils", "epoch":"(none)", "version":"8.30", "release":"13.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Thu 16 Jun 2022 12:18:02 PM CST, Key ID 09e2f91fd431d51"}
{"name":"firewalld", "epoch":"(none)", "version":"0.9.3", "release":"13.el8", "arch":"noarch", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Fri 25 Feb 2022 09:40:17 PM CST, Key ID 09e2f91fd431d51"}
{"name":"filesystem", "epoch":"(none)", "version":"3.8", "release":"6.el8", "arch":"x86_64", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Mon 21 Jun 2021 07:17:43 PM CST, Key ID 199e2f91fd431d51"}
{"name":"gmp", "epoch":"1", "version":"6.1.2", "release":"10.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Fri 14 Jun 2019 04:58:39 PM CST, Key ID 199e2f91fd431d51"}
{"name":"basesystem", "epoch":"(none)", "version":"11", "release":"5.el8", "arch":"noarch", "vendor":"RH, Inc.", "sigpgp":"RSA/SHA256, Sat 15 Dec 2018 05:49:21 AM CST, Key ID 09e2f91fd431d51"}
{"name":"dmidecode", "epoch":"1", "version":"3.3", "release":"4.el8", "arch":"x86_64", "vendor":"Red Hat, Inc.", "sigpgp":"RSA/SHA256, Mon 14 Mar 2022 02:13:06 PM CST, Key ID 99e2f91fd431d51"}
'''.strip()

REDHAT_RELEASE_86 = """
Red Hat Enterprise Linux release 8.6 (Ootpa)
""".strip()

REDHAT_RELEASE_91 = """
Red Hat Enterprise Linux release 9.1 (Plow)
""".strip()

REDHAT_RELEASE_FEDORA = """
Fedora release 23 (Twenty Three)
""".strip()

OS_RELEASE_RH = """
NAME="Red Hat Enterprise Linux"
ID="rhel"
""".strip()

OS_RELEASE_OL = """
NAME="Oracle Linux Server"
ID="ol"
""".strip()

REDHAT_RELEASE_UNKNOWN = """
Test OS
""".strip()

OS_RELEASE_UNKNOWN = """
NAME="Test OS"
ID="test"
PRETTY_NAME="Test OS"
""".strip()


# RHEL Test
def test_is_rhel():
    # RHEL: redhat-release only
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_91))
    result = OSRelease(None, rhr, None, None)
    assert result.is_rhel is True
    assert result.product == RHEL_STR

    # RHEL: os-release only
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    result = OSRelease(None, None, osr, None)
    assert result.is_rhel is True
    assert result.product == RHEL_STR

    # RHEL 9, rpms only
    rpms = InstalledRpms(context_wrap(RPMS_JSON_91_WO_KERNEL))
    result = OSRelease(rpms, None, None, None)
    assert result.is_rhel is True
    assert result.product == RHEL_STR

    # RHEL 9, rpms and uname
    rpms = InstalledRpms(context_wrap(RPMS_JSON_91_WO_KERNEL))
    uname = Uname(context_wrap(UNAME_91))
    result = OSRelease(rpms, None, None, uname)
    assert result.is_rhel is True
    assert result.product == RHEL_STR

    rpms = InstalledRpms(context_wrap(RPMS_JSON_91_W_KERNEL))
    result = OSRelease(rpms, None, None, uname)
    assert result.is_rhel is True
    assert result.product == RHEL_STR


def test_not_rhel():
    # NON-RHEL: Nothing
    result = OSRelease(None, None, None, None)
    assert result.is_rhel is False
    assert result.product == "Unknown"

    # NON-RHEL: uname only
    uname = Uname(context_wrap(UNAME_91))
    result = OSRelease(None, None, None, uname)
    assert result.is_rhel is False
    assert result.product == "Unknown"

    # NON-RHEL: BAD redhat-release
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_FEDORA))
    result = OSRelease(None, rhr, None, None)
    assert result.is_rhel is False
    assert result.product == "Fedora"

    # NON-RHEL: BAD os-release
    osr = OsRelease(context_wrap(OS_RELEASE_OL))
    result = OSRelease(None, None, osr, None)
    assert result.is_rhel is False
    assert result.product == "Oracle Linux Server"

    # NON-RHEL: BAD redhat-release, Good rpms
    rpms = InstalledRpms(context_wrap(RPMS_JSON_91_W_KERNEL))
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_FEDORA))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_91))
    result = OSRelease(rpms, rhr, osr, uname)
    assert result.is_rhel is False
    assert result.product == "Fedora"

    # NON-RHEL: BAD os-release, Good rpms
    rpms = InstalledRpms(context_wrap(RPMS_JSON_91_W_KERNEL))
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_91))
    osr = OsRelease(context_wrap(OS_RELEASE_OL))
    uname = Uname(context_wrap(UNAME_91))
    result = OSRelease(rpms, rhr, osr, uname)
    assert result.is_rhel is False
    assert result.product == "Oracle Linux Server"

    # NON-RHEL: BAD rpms, Good others
    rpms = InstalledRpms(context_wrap(RPMS_JSON_8_NG))
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_86))
    osr = OsRelease(context_wrap(OS_RELEASE_RH))
    uname = Uname(context_wrap(UNAME_86))
    result = OSRelease(rpms, rhr, osr, uname)
    assert result.is_rhel is False
    assert result.product == "Unknown"

    # NON-RHEL: NO rpms, both os-release  and redhat-release are NG
    rhr = RedhatRelease(context_wrap(REDHAT_RELEASE_UNKNOWN))
    osr = OsRelease(context_wrap(OS_RELEASE_UNKNOWN))
    result = OSRelease(None, rhr, osr, None)
    assert result.is_rhel is False
    assert result.product == "Unknown"
