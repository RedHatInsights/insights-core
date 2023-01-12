from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.cmdline import CmdLine
from insights.parsers.systemd.unitfiles import ListUnits
from insights.parsers.redhat_release import RedhatRelease
from insights.combiners.rhel_for_edge import RhelForEdge
from insights.combiners import rhel_for_edge
from insights.tests import context_wrap
import doctest

CONTENT_REDHAT_RELEASE_RHEL = """
Red Hat Enterprise Linux release 8.4 (Ootpa)
""".strip()

CONTENT_REDHAT_RELEASE_COREOS = """
Red Hat Enterprise Linux CoreOS release 4.12
""".strip()

CMDLINE_RHEL = """
BOOT_IMAGE=/vmlinuz-4.18.0-80.el8.x86_64 root=/dev/mapper/rootvg-rootlv ro crashkernel=184M rd.lvm.lv=rootvg/rootlv biosdevname=0 printk.time=1 numa=off audit=1 transparent_hugepage=always LANG=en_US.UTF-8
""".strip()

CMDLINE_EDGE = """
BOOT_IMAGE=(hd0,msdos1)/ostree/rhel-323453435435234234232534534/vmlinuz-4.18.0-348.20.1.el8_5.x86_64 root=/dev/mapper/rhel-root ro crashkernel=auto rd.lvm.lv=rhel/root rd.lvm.lv=rhel/swap ostree=/ostree/boot.1/rhel/08987978979/0 rhgb quiet LANG=en_US.UTF-8
""".strip()

CONTENT_SYSTEMCTL_LIST_UNITS_NO_AUTOMATED = """
postgresql.service                                                                               loaded active running   PostgreSQL database server
""".strip()

CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED = """
postgresql.service                                                                               loaded active running   PostgreSQL database server
rhcd.service                                                                                     loaded active running   Red Hat connector daemon
""".strip()

CONTENT_INSTALLED_RPMS_RHEL = """
kernel-4.18.0-305.19.1.el8_4.x86_64
""".strip()

CONTENT_INSTALLED_RPMS_EDGE = """
kernel-4.18.0-305.19.1.el8_4.x86_64
rpm-ostree-2021.5-2.el8.x86_64
""".strip()


def test_rhel_for_edge_true_1():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_NO_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
    assert result.is_edge is True
    assert result.is_automated is False


def test_rhel_for_edge_true_2():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
    assert result.is_edge is True
    assert result.is_automated is True


def test_rhel_for_edge_false_1():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_RHEL))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_2():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_RHEL))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_3():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_COREOS))

    result = RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_doc_examples():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    env = {
            'rhel_for_edge_obj': RhelForEdge(install_rpms, cmdline, list_units, redhat_release)
          }
    failed, total = doctest.testmod(rhel_for_edge, globs=env)
    assert failed == 0
