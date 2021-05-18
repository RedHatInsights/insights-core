from insights.parsers import yum_updateinfo
from insights.tests import context_wrap
import doctest

YUM_UPDATEINFO_INPUT = """
FEDORA-2020-777f43619c bugfix         firefox-83.0-13.fc32.x86_64
FEDORA-2020-786c7010d2 bugfix         flatpak-libs-1.8.3-1.fc32.x86_64
FEDORA-2020-786c7010d2 bugfix         flatpak-selinux-1.8.3-1.fc32.noarch
FEDORA-2020-786c7010d2 bugfix         flatpak-session-helper-1.8.3-1.fc32.x86_64
FEDORA-2020-3e2cd487ea bugfix         fuse-overlayfs-1.3.0-1.fc32.x86_64
FEDORA-2020-79e9f139fe bugfix         gnome-control-center-3.36.5-1.fc32.x86_64
FEDORA-2020-79e9f139fe bugfix         gnome-control-center-filesystem-3.36.5-1.fc32.noarch
FEDORA-2020-352b61ce72 bugfix         iwl100-firmware-39.31.5.1-115.fc32.noarch
FEDORA-2020-352b61ce72 bugfix         iwl1000-firmware-1:39.31.5.1-115.fc32.noarch
FEDORA-2020-352b61ce72 bugfix         iwl105-firmware-18.168.6.1-115.fc32.noarch
FEDORA-2020-352b61ce72 bugfix         iwl135-firmware-18.168.6.1-115.fc32.noarch
FEDORA-2020-352b61ce72 Moderate/Sec.  iwl2000-firmware-18.168.6.1-115.fc32.noarch
"""

TEST_DATA = """
RSHA-2020-0001 security       firefox-83.0-13.fc32.x86_64
RHBA-2020-0002 bugfix         flatpak-libs-1.8.3-1.fc32.x86_64
RHEA-2020-0003 enhancement    flatpak-selinux-1.8.3-1.fc32.noarch
"""


def test_yum_updateinfo():
    info = yum_updateinfo.YumUpdateinfo(context_wrap(YUM_UPDATEINFO_INPUT))
    assert info is not None
    assert info.items[0]['advisory'] == 'FEDORA-2020-777f43619c'
    assert info.items[0]['type'] == 'bugfix'
    assert info.items[0]['package'] == 'firefox-83.0-13.fc32.x86_64'
    assert len(info.items) == 12


def test_yum_updateinfo_docs():
    env = {
        'updateinfo': yum_updateinfo.YumUpdateinfo(context_wrap(TEST_DATA))
    }
    failed, total = doctest.testmod(yum_updateinfo, globs=env)
    assert failed == 0
