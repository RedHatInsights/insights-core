import pytest
from insights.core.exceptions import SkipComponent
from insights.parsers.installed_rpms import InstalledRpms
from insights.parsers.cmdline import CmdLine
from insights.parsers.systemd.unitfiles import ListUnits
from insights.parsers.redhat_release import RedhatRelease
from insights.parsers.rpm_ostree_status import RpmOstreeStatus
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

RPM_OSTREE_STATUS_EDGE = """
{
  "deployments" : [
    {
      "base-commit-meta" : {
        "rpmostree.inputhash" : "156ae2e3ad99777a0b7e48d169ee2f4fa618fd76a4ffc5ba8af8fad8c46ea75d"
      },
      "unlocked" : "none",
      "booted" : true,
      "initramfs-etc" : [
      ],
      "id" : "rhel-7c25253d45a30b05222fba1365fce35263987262c490ad547e66d8541f05293a.0",
      "osname": "rhel",
      "origin" : "edge:rhel/8/x86_64/edge",
    },
    {
      "base-commit-meta" : {
        "rpmostree.inputhash" : "f2ff223ab7b3cc45ca20fadc0a138808cc084a20bc5ce9f22b451a802c652c26",
        "ostree.linux" : "4.18.0-372.9.1.el8.x86_64",
        "ostree.bootable" : true
      },
      "id" : "rhel-e2707b5fc7d4b168d7746678bc228b734dbf6f9f64b8ad97f5c87f7b9e7dfea7.0",
      "osname": "rhel",
      "pending-base-checksum" : "a35ac0ae55eb10f2f29e3f01cc760ae3ad5341d44a285129704749f24233d004",
      "origin" : "edge:rhel/8/x86_64/edge",
      "regenerate-initramfs" : false,
      "checksum" : "e2707b5fc7d4b168d7746678bc228b734dbf6f9f64b8ad97f5c87f7b9e7dfea7",
    }
  ],
  "transaction" : null,
  "cached-update" : null
}
""".strip()

RPM_OSTREE_STATUS_RHCOS = """
{
  "deployments" : [
    {
      "requested-local-packages" : [
      ],
      "base-commit-meta" : {
        "ostree.manifest-digest" : "sha256:90780b08939d913d9cfc5565eecdd12055dd57301b2109985e149830a92ed6b1",
        "ostree.importer.version" : "0.8.7",
        "ostree.tar-filtered" : {
        }
      },
      "base-removals" : [
      ],
      "unlocked" : "none",
      "booted" : true,
      "requested-local-fileoverride-packages" : [
      ],
      "requested-modules-enabled" : [
      ],
      "id" : "rhcos-40948b845a13349cb0d57400eebdcfdf72bb8521636a1f067fb22d92b0b73b41.0",
      "base-remote-replacements" : {
      },
      "osname" : "rhcos",
      "pinned" : false,
      "regenerate-initramfs" : false,
      "base-local-replacements" : [
      ],
      "container-image-reference" : "ostree-unverified-registry:quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:90780b08939d913d9cfc5565eecdd12055dd57301b2109985e149830a92ed6b1",
      "checksum" : "40948b845a13349cb0d57400eebdcfdf72bb8521636a1f067fb22d92b0b73b41",
      "requested-base-local-replacements" : [
      ],
      "requested-modules" : [
      ],
      "requested-packages" : [
      ],
      "serial" : 0,
      "timestamp" : 1674005544,
      "packages" : [
      ],
      "staged" : false,
      "requested-base-removals" : [
      ],
      "modules" : [
      ],
      "container-image-reference-digest" : "sha256:90780b08939d913d9cfc5565eecdd12055dd57301b2109985e149830a92ed6b1"
    }
  ],
  "transaction" : null,
  "cached-update" : null,
  "update-driver" : null
}
""".strip()

RPM_OSTREE_STATUS_EDGE_FALSE = """
{
  "deployments" : [
    {
      "base-commit-meta" : {
        "rpmostree.inputhash" : "156ae2e3ad99777a0b7e48d169ee2f4fa618fd76a4ffc5ba8af8fad8c46ea75d"
      },
      "requested-local-packages" : [
      ],
      "base-removals" : [
      ],
      "unlocked" : "none",
      "booted" : true,
      "initramfs-etc" : [
      ],
      "id" : "rhel-7c25253d45a30b05222fba1365fce35263987262c490ad547e66d8541f05293a.0",
      "layered-commit-meta" : {
        "rpmostree.packages" : [
          "glibc-langpack-en",
          "ksh",
          "wget",
          "rhc"
        ],
        "rpmostree.state-sha512" : "c81ae53960de1009a1bace2d89fe58d42790147ba8018e1799ea22bf6f74e754af57530e04d092ed2975bcfaf7861d20c7133268ad02b8644973710727a1d311",
        "rpmostree.removed-base-packages" : [
        ],
        "ostree.linux" : "4.18.0-348.el8.x86_64",
        "rpmostree.rpmmd-repos" : [
          {
            "id" : "rhel-8-for-x86_64-baseos-rpms",
            "timestamp" : 1665041964
          },
          {
            "id" : "rhel-8-for-x86_64-appstream-rpms",
            "timestamp" : 1665042074
          }
        ],
        "rpmostree.modules" : [
        ],
        "rpmostree.clientlayer_version" : 5,
        "ostree.bootable" : true,
        "rpmostree.clientlayer" : true,
        "rpmostree.replaced-base-packages" : [
        ]
      },
      "osname": "rhel",
      "origin" : "edge:rhel/8/x86_64/falsetest",
      "pinned" : false,
      "regenerate-initramfs" : false,
      "base-timestamp" : 1665394938,
      "base-local-replacements" : [
      ],
      "checksum" : "7c25253d45a30b05222fba1365fce35263987262c490ad547e66d8541f05293a",
      "requested-base-local-replacements" : [
      ],
      "timestamp" : 1665398315,
      "requested-packages" : [
        "glibc-langpack-en",
        "ksh",
        "wget",
        "rhc"
      ],
      "serial" : 0,
      "packages" : [
        "glibc-langpack-en",
        "ksh",
        "wget",
        "rhc"
      ],
      "base-checksum" : "a35ac0ae55eb10f2f29e3f01cc760ae3ad5341d44a285129704749f24233d004",
      "gpg-enabled" : false,
      "requested-base-removals" : [
      ]
    },
    {
      "base-commit-meta" : {
        "rpmostree.inputhash" : "f2ff223ab7b3cc45ca20fadc0a138808cc084a20bc5ce9f22b451a802c652c26",
        "ostree.linux" : "4.18.0-372.9.1.el8.x86_64",
        "ostree.bootable" : true
      },
      "requested-local-packages" : [
      ],
      "base-removals" : [
      ],
      "unlocked" : "none",
      "booted" : false,
      "initramfs-etc" : [
      ],
      "id" : "rhel-e2707b5fc7d4b168d7746678bc228b734dbf6f9f64b8ad97f5c87f7b9e7dfea7.0",
      "layered-commit-meta" : {
        "rpmostree.packages" : [
          "glibc-langpack-en",
          "ksh",
          "wget",
          "rhc"
        ],
        "rpmostree.state-sha512" : "a750200ccd47616f629c5c3c3937b51f561c1f1f7fee7dd94295997e0bf16e756b0eb8517f37e1f78f06bf281c6d831745e82765ffe23dd3248038511ae96df1",
        "rpmostree.removed-base-packages" : [
        ],
        "ostree.linux" : "4.18.0-372.9.1.el8.x86_64",
        "rpmostree.rpmmd-repos" : [
          {
            "id" : "rhel-8-for-x86_64-appstream-rpms",
            "timestamp" : 1663855048
          },
          {
            "id" : "rhel-8-for-x86_64-baseos-rpms",
            "timestamp" : 1663584426
          }
        ],
        "rpmostree.modules" : [
        ],
        "rpmostree.clientlayer_version" : 5,
        "ostree.bootable" : true,
        "rpmostree.clientlayer" : true,
        "rpmostree.replaced-base-packages" : [
        ]
      },
      "osname": "rhel",
      "pending-base-checksum" : "a35ac0ae55eb10f2f29e3f01cc760ae3ad5341d44a285129704749f24233d004",
      "origin" : "edge:rhel/8/x86_64/falsetest",
      "regenerate-initramfs" : false,
      "pending-base-timestamp" : 1665394938,
      "base-timestamp" : 1652270522,
      "base-local-replacements" : [
      ],
      "checksum" : "e2707b5fc7d4b168d7746678bc228b734dbf6f9f64b8ad97f5c87f7b9e7dfea7",
      "requested-base-local-replacements" : [
      ],
      "timestamp" : 1663923873,
      "requested-packages" : [
        "glibc-langpack-en",
        "ksh",
        "wget",
        "rhc"
      ],
      "serial" : 0,
      "packages" : [
        "glibc-langpack-en",
        "ksh",
        "wget",
        "rhc"
      ],
      "pinned" : false,
      "base-checksum" : "d82856c783ddb1c6ad9f728e60bec2b39626eef12984860c4a92fea04b1d396e",
      "gpg-enabled" : false,
      "requested-base-removals" : [
      ]
    }
  ],
  "transaction" : null,
  "cached-update" : null
}
""".strip()


def test_rhel_for_edge_true_1():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_NO_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))
    rpm_ostree_status = RpmOstreeStatus(context_wrap(RPM_OSTREE_STATUS_EDGE))

    result = RhelForEdge(list_units, rpm_ostree_status, install_rpms, cmdline, redhat_release)
    assert result.is_edge is True
    assert result.is_automated is False


def test_rhel_for_edge_true_2():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(list_units, None, install_rpms, cmdline, redhat_release)
    assert result.is_edge is True
    assert result.is_automated is True


def test_rhel_for_edge_false_1():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_RHEL))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(list_units, None, install_rpms, cmdline, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_2():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_RHEL))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    result = RhelForEdge(list_units, None, install_rpms, cmdline, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_3():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_COREOS))

    result = RhelForEdge(list_units, None, install_rpms, cmdline, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_4():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_COREOS))
    rpm_ostree_status = RpmOstreeStatus(context_wrap(RPM_OSTREE_STATUS_RHCOS))

    result = RhelForEdge(list_units, rpm_ostree_status, install_rpms, cmdline, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_5():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_COREOS))
    rpm_ostree_status = RpmOstreeStatus(context_wrap(RPM_OSTREE_STATUS_EDGE_FALSE))

    result = RhelForEdge(list_units, rpm_ostree_status, install_rpms, cmdline, redhat_release)
    assert result.is_edge is False
    assert result.is_automated is False


def test_rhel_for_edge_false_6():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))

    with pytest.raises(SkipComponent) as e:
        RhelForEdge(list_units, None, install_rpms, cmdline, None)
    assert "Unable to determine if this system is created from an edge image" in str(e)


def test_doc_examples():
    install_rpms = InstalledRpms(context_wrap(CONTENT_INSTALLED_RPMS_EDGE))
    cmdline = CmdLine(context_wrap(CMDLINE_EDGE))
    list_units = ListUnits(context_wrap(CONTENT_SYSTEMCTL_LIST_UNITS_AUTOMATED))
    redhat_release = RedhatRelease(context_wrap(CONTENT_REDHAT_RELEASE_RHEL))

    env = {
            'rhel_for_edge_obj': RhelForEdge(list_units, None, install_rpms, cmdline, redhat_release)
          }
    failed, total = doctest.testmod(rhel_for_edge, globs=env)
    assert failed == 0
