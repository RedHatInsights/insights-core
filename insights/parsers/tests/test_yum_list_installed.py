from insights.parsers.yum_list_installed import YumListInstalled
from insights.tests import context_wrap


SIMPLE = """
bash.x86_64                               4.4.23-1.fc28                 @updates
""".strip()

WRAPPED_LINE = """
NetworkManager-bluetooth.x86_64           1:1.10.10-1.fc28              @updates
NetworkManager-config-connectivity-fedora.noarch
                                          1:1.10.10-1.fc28              @updates
NetworkManager-glib.x86_64                1:1.10.10-1.fc28              @updates
NetworkManager-libnm.x86_64               1:1.10.10-1.fc28              @updates
""".strip()

COMMANDLINE = """
jdk1.8.0_121.x86_64                       2000:1.8.0_121-fcs            @@commandline
"""


def test_simple():
    ctx = context_wrap(SIMPLE)
    rpms = YumListInstalled(ctx)
    bash = rpms.newest("bash")
    assert bash is not None
    assert bash.epoch == "0"
    assert bash.version == "4.4.23"
    assert bash.release == "1.fc28"
    assert bash.arch == "x86_64"


def test_wrapped():
    ctx = context_wrap(WRAPPED_LINE)
    rpms = YumListInstalled(ctx)
    nmb = rpms.newest("NetworkManager-bluetooth")
    assert nmb is not None
    assert nmb.epoch == "1"
    assert nmb.version == "1.10.10"
    assert nmb.release == "1.fc28"
    assert nmb.arch == "x86_64"

    nmccf = rpms.newest("NetworkManager-config-connectivity-fedora")
    assert nmccf is not None
    assert nmccf.epoch == "1"
    assert nmccf.version == "1.10.10"
    assert nmccf.release == "1.fc28"
    assert nmb.arch == "x86_64"


def test_commandline():
    ctx = context_wrap(COMMANDLINE)
    rpms = YumListInstalled(ctx)

    jdk = rpms.newest("jdk1.8.0_121")
    assert jdk is not None
    assert jdk.epoch == "2000"
    assert jdk.version == "1.8.0_121"
    assert jdk.release == "fcs"
    assert jdk.arch == "x86_64"
