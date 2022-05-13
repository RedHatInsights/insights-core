from insights.parsers.os_release import OsRelease
from insights.tests import context_wrap

REHL_OS_RELEASE = """
NAME="Red Hat Enterprise Linux Server"
VERSION="7.2 (Maipo)"
ID="rhel"
ID_LIKE="fedora"
VERSION_ID="7.2"
PRETTY_NAME="Employee SKU"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:redhat:enterprise_linux:7.2:GA:server"
HOME_URL="https://www.redhat.com/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"

REDHAT_BUGZILLA_PRODUCT="Red Hat Enterprise Linux 7"
REDHAT_BUGZILLA_PRODUCT_VERSION=7.2
REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux"
REDHAT_SUPPORT_PRODUCT_VERSION="7.2"
""".strip()

RHEVH_RHV40_OS_RELEASE = """
NAME="Red Hat Enterprise Linux"
VERSION="7.3"
VERSION_ID="7.3"
ID="rhel"
ID_LIKE="fedora"
VARIANT="Red Hat Virtualization Host"
VARIANT_ID="ovirt-node"
PRETTY_NAME="Red Hat Virtualization Host 4.0 (el7.3)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:redhat:enterprise_linux:7.3:GA:hypervisor"
HOME_URL="https://www.redhat.com/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"

# FIXME
# REDHAT_BUGZILLA_PRODUCT="Red Hat Virtualization"
# REDHAT_BUGZILLA_PRODUCT_VERSION=7.3
# REDHAT_SUPPORT_PRODUCT="Red Hat Virtualization"
# REDHAT_SUPPORT_PRODUCT_VERSION=7.3
""".strip()

FEDORA_OS_RELEASE = """
NAME=Fedora
VERSION="24 (Server Edition)"
ID=fedora
VERSION_ID=24
PRETTY_NAME="Fedora 24 (Server Edition)"
ANSI_COLOR="0;34"
CPE_NAME="cpe:/o:fedoraproject:fedora:24"
HOME_URL="https://fedoraproject.org/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_BUGZILLA_PRODUCT="Fedora"
REDHAT_BUGZILLA_PRODUCT_VERSION=24
REDHAT_SUPPORT_PRODUCT="Fedora"
REDHAT_SUPPORT_PRODUCT_VERSION=24
PRIVACY_POLICY_URL=https://fedoraproject.org/wiki/Legal:PrivacyPolicy
VARIANT="Server Edition"
VARIANT_ID=server
""".strip()


def test_rhel():
    rls = OsRelease(context_wrap(REHL_OS_RELEASE))
    data = rls.data
    assert data.get("VARIANT_ID") is None
    assert data.get("VERSION") == "7.2 (Maipo)"


def test_rhevh():
    rls = OsRelease(context_wrap(RHEVH_RHV40_OS_RELEASE))
    data = rls.data
    assert data.get("VARIANT_ID") == "ovirt-node"
    assert data.get("VERSION") == "7.3"
    assert data.get("PRETTY_NAME") == "Red Hat Virtualization Host 4.0 (el7.3)"


def test_fedora24():
    rls = OsRelease(context_wrap(FEDORA_OS_RELEASE))
    data = rls.data
    assert data.get("VARIANT_ID") == "server"
    assert data.get("VERSION") == "24 (Server Edition)"
    assert data.get("PRETTY_NAME") == "Fedora 24 (Server Edition)"
