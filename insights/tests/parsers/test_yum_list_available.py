import pytest

from insights import SkipComponent
from insights.parsers.yum_list import YumListAvailable
from insights.tests import context_wrap


EMPTY = """
Available Packages
""".strip()

EXPIRED_EMPTY = """
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
Available Packages
""".strip()

EXPIRED_WITH_DATA = """
Repodata is over 2 weeks old. Install yum-cron? Or run: yum makecache fast
Available Packages
bash.x86_64                               4.4.23-1.fc28                 @updates
""".strip()

SIMPLE = """
Available Packages
bash.x86_64                               4.4.23-1.fc28                 @updates
""".strip()

WRAPPED_LINE = """
Available Packages
NetworkManager-bluetooth.x86_64           1:1.10.10-1.fc28              @updates
NetworkManager-config-connectivity-fedora.noarch
                                          1:1.10.10-1.fc28              @updates
NetworkManager-glib.x86_64                1:1.10.10-1.fc28              @updates
NetworkManager-libnm.x86_64               1:1.10.10-1.fc28              @updates
clucene-contribs-lib.x86_64               2.3.3.4-31.20130812.e8e3d20git.fc28
                                                                        @fedora
clucene-core.x86_64                       2.3.3.4-31.20130812.e8e3d20git.fc28
                                                                        @fedora
""".strip()

COMMANDLINE = """
Available Packages
jdk1.8.0_121.x86_64                       2000:1.8.0_121-fcs            @@commandline
"""

HEADER_FOOTER_JUNK = """
Loaded plugins: product-id, search-disabled-repos, subscription-manager
Available Packages
GConf2.x86_64                    3.2.6-8.el7             @rhel-7-server-rpms
GeoIP.x86_64                     1.5.0-11.el7            @anaconda/7.3
ImageMagick.x86_64               6.7.8.9-15.el7_2        @rhel-7-server-rpms
NetworkManager.x86_64            1:1.4.0-17.el7_3        installed
NetworkManager.x86_64            1:1.8.0-9.el7           installed
NetworkManager-config-server.noarch
                                 1:1.8.0-9.el7           installed
Uploading Enabled Repositories Report
Loaded plugins: priorities, product-id, rhnplugin, rhui-lb, subscription-
              : manager, versionlock
"""


def test_empty():
    ctx = context_wrap(EMPTY)
    with pytest.raises(SkipComponent):
        YumListAvailable(ctx)


def test_simple():
    ctx = context_wrap(SIMPLE)
    rpms = YumListAvailable(ctx)
    rpm = rpms.newest("bash")
    assert rpm is not None
    assert rpm.epoch == "0"
    assert rpm.version == "4.4.23"
    assert rpm.release == "1.fc28"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "updates"


def test_expired_cache_with_data():
    ctx = context_wrap(EXPIRED_WITH_DATA)
    rpms = YumListAvailable(ctx)
    assert rpms.expired_cache is True


def test_expired_cache_no_data():
    ctx = context_wrap(EXPIRED_EMPTY)
    with pytest.raises(SkipComponent):
        YumListAvailable(ctx)


def test_wrapped():
    ctx = context_wrap(WRAPPED_LINE)
    rpms = YumListAvailable(ctx)
    rpm = rpms.newest("NetworkManager-bluetooth")
    assert rpm is not None
    assert rpm.epoch == "1"
    assert rpm.version == "1.10.10"
    assert rpm.release == "1.fc28"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "updates"

    rpm = rpms.newest("NetworkManager-config-connectivity-fedora")
    assert rpm is not None
    assert rpm.epoch == "1"
    assert rpm.version == "1.10.10"
    assert rpm.release == "1.fc28"
    assert rpm.arch == "noarch"
    assert rpm.repo == "updates"

    rpm = rpms.newest("clucene-contribs-lib")
    assert rpm is not None
    assert rpm.epoch == "0"
    assert rpm.version == "2.3.3.4"
    assert rpm.release == "31.20130812.e8e3d20git.fc28"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "fedora"

    rpm = rpms.newest("clucene-core")
    assert rpm is not None
    assert rpm.epoch == "0"
    assert rpm.version == "2.3.3.4"
    assert rpm.release == "31.20130812.e8e3d20git.fc28"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "fedora"


def test_commandline():
    ctx = context_wrap(COMMANDLINE)
    rpms = YumListAvailable(ctx)

    rpm = rpms.newest("jdk1.8.0_121")
    assert rpm is not None
    assert rpm.epoch == "2000"
    assert rpm.version == "1.8.0_121"
    assert rpm.release == "fcs"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "commandline"


def test_multiple_stanza():
    ctx = context_wrap(HEADER_FOOTER_JUNK)
    rpms = YumListAvailable(ctx)

    rpm = rpms.newest("GConf2")
    assert rpm is not None
    assert rpm.epoch == "0"
    assert rpm.version == "3.2.6"
    assert rpm.release == "8.el7"
    assert rpm.arch == "x86_64"
    assert rpm.repo == "rhel-7-server-rpms"

    rpm = rpms.newest("NetworkManager-config-server")
    assert rpm is not None
    assert rpm.epoch == "1"
    assert rpm.version == "1.8.0"
    assert rpm.release == "9.el7"
    assert rpm.arch == "noarch"
    assert rpm.repo == "installed"
