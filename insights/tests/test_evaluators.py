from insights.core.specs import SpecMapper
from insights.core.evaluators import InsightsEvaluator, InsightsMultiEvaluator, SingleEvaluator
from insights.core import dr
from insights.core.archives import TarExtractor
from insights.plugins.insights_heartbeat import is_insights_heartbeat
from insights.parsers.multinode import osp, OSPChild
from . import insights_heartbeat, HEARTBEAT_ID, HEARTBEAT_NAME
import json
import os
import shutil
import subprocess
import tarfile
import tempfile

HERE = os.path.abspath(os.path.dirname(__file__))

CLUSTER_UPLOAD = """
./
./insights-overcloud-compute-0.localdomain-20150930193932.tar
./insights-overcloud-compute-1.localdomain-20150930193956.tar
./insights-overcloud-controller-1.localdomain-20150930193924.tar
./insights-overcloud-controller-2.localdomain-20150930193927.tar
./insights-overcloud-controller-0.localdomain-20150930193931.tar
./cluster_id
""".strip()

SOSCLEANER_SINGLE_NODE_UPLOAD = """
soscleaner-7704572305004757/branch_info
soscleaner-7704572305004757/insights_commands/ethtool_-k_bond0
soscleaner-7704572305004757/insights_commands/ethtool_-S_eth1
soscleaner-7704572305004757/insights_commands/netstat_-neopa
soscleaner-7704572305004757/insights_commands/ethtool_-i_bond0
soscleaner-7704572305004757/insights_commands/hostname
soscleaner-7704572305004757/insights_commands/ovs-vsctl_show
soscleaner-7704572305004757/insights_commands/ethtool_-i_eth1
soscleaner-7704572305004757/insights_commands/ethtool_bond0
soscleaner-7704572305004757/insights_commands/hponcfg_-g
soscleaner-7704572305004757/insights_commands/ps_auxcww
soscleaner-7704572305004757/insights_commands/sestatus_-b
soscleaner-7704572305004757/insights_commands/lsmod
soscleaner-7704572305004757/insights_commands/blkid_-c_.dev.null
soscleaner-7704572305004757/insights_commands/rpm_-qa_--qf_NAME_-_VERSION_-_RELEASE_._ARCH_INSTALLTIME_date_BUILDTIME_RSAHEADER_pgpsig_DSAHEADER_pgpsig
soscleaner-7704572305004757/insights_commands/ethtool_eth1
soscleaner-7704572305004757/insights_commands/lspci
soscleaner-7704572305004757/insights_commands/ip_route_show_table_all
soscleaner-7704572305004757/insights_commands/chkconfig_--list
soscleaner-7704572305004757/insights_commands/ethtool_-k_eth0
soscleaner-7704572305004757/insights_commands/rpm_-V_coreutils_procps_procps-ng_shadow-utils_passwd_sudo
soscleaner-7704572305004757/insights_commands/ifconfig_-a
soscleaner-7704572305004757/insights_commands/df_-alP
soscleaner-7704572305004757/insights_commands/vgdisplay
soscleaner-7704572305004757/insights_commands/netstat_-s
soscleaner-7704572305004757/insights_commands/uname_-a
soscleaner-7704572305004757/insights_commands/ethtool_eth0
soscleaner-7704572305004757/insights_commands/date
soscleaner-7704572305004757/insights_commands/ethtool_-k_eth1
soscleaner-7704572305004757/insights_commands/dmesg
soscleaner-7704572305004757/insights_commands/parted_-s
soscleaner-7704572305004757/insights_commands/ethtool_-g_eth1
soscleaner-7704572305004757/insights_commands/lsof
soscleaner-7704572305004757/insights_commands/ethtool_-i_eth0
soscleaner-7704572305004757/insights_commands/ls_-lanR_.boot
soscleaner-7704572305004757/insights_commands/mount
soscleaner-7704572305004757/insights_commands/systemctl_list-unit-files
soscleaner-7704572305004757/insights_commands/uptime
soscleaner-7704572305004757/insights_commands/ethtool_-S_bond0
soscleaner-7704572305004757/insights_commands/ethtool_-g_bond0
soscleaner-7704572305004757/insights_commands/free
soscleaner-7704572305004757/insights_commands/sysctl_-a
soscleaner-7704572305004757/insights_commands/dmidecode
soscleaner-7704572305004757/insights_commands/ethtool_-g_eth0
soscleaner-7704572305004757/insights_commands/yum_-C_repolist
soscleaner-7704572305004757/insights_commands/ethtool_-S_eth0
soscleaner-7704572305004757/proc/interrupts
soscleaner-7704572305004757/proc/cmdline
soscleaner-7704572305004757/proc/cpuinfo
soscleaner-7704572305004757/proc/meminfo
soscleaner-7704572305004757/proc/net/bonding/bond0
soscleaner-7704572305004757/proc/scsi/scsi
soscleaner-7704572305004757/etc/sysctl.conf
soscleaner-7704572305004757/etc/hosts
soscleaner-7704572305004757/etc/kdump.conf
soscleaner-7704572305004757/etc/redhat-release
soscleaner-7704572305004757/etc/rsyslog.conf
soscleaner-7704572305004757/etc/redhat-access-insights/machine-id
soscleaner-7704572305004757/etc/pam.d/password-auth
soscleaner-7704572305004757/etc/ssh/sshd_config
soscleaner-7704572305004757/etc/security/limits.conf
soscleaner-7704572305004757/etc/security/limits.d/90-nproc.conf
soscleaner-7704572305004757/etc/selinux/config
soscleaner-7704572305004757/etc/lvm/lvm.conf
soscleaner-7704572305004757/etc/udev/rules.d/70-persistent-net.rules
soscleaner-7704572305004757/etc/rc.d/rc.local
soscleaner-7704572305004757/etc/sysconfig/kdump
soscleaner-7704572305004757/etc/sysconfig/netconsole
soscleaner-7704572305004757/etc/sysconfig/network-scripts/ifcfg-eth0
soscleaner-7704572305004757/etc/sysconfig/network-scripts/ifcfg-lo
soscleaner-7704572305004757/etc/sysconfig/network-scripts/ifcfg-bond0
soscleaner-7704572305004757/etc/sysconfig/network-scripts/ifcfg-eth1
soscleaner-7704572305004757/var/log/yum.log
soscleaner-7704572305004757/var/log/redhat-access-insights/redhat-access-insights.log
soscleaner-7704572305004757/sys/devices/system/clocksource/clocksource0/current_clocksource
soscleaner-7704572305004757/boot/grub/grub.conf
""".strip()

SINGLE_NODE_UPLOAD = """
insights-davxapasnp03-20151007031606/insights_commands/date
insights-davxapasnp03-20151007031606/insights_commands/dmesg
insights-davxapasnp03-20151007031606/insights_commands/hostname
insights-davxapasnp03-20151007031606/insights_commands/netstat_-neopa
insights-davxapasnp03-20151007031606/insights_commands/netstat_-s
insights-davxapasnp03-20151007031606/insights_commands/ps_auxcww
insights-davxapasnp03-20151007031606/insights_commands/rpm_-V_coreutils_procps_procps-ng_shadow-utils_passwd_sudo
insights-davxapasnp03-20151007031606/insights_commands/rpm_-qa_--qf_NAME_-_VERSION_-_RELEASE_._ARCH_INSTALLTIME_date_BUILDTIME_RSAHEADER_pgpsig_DSAHEADER_pgpsig
insights-davxapasnp03-20151007031606/insights_commands/uname_-a
insights-davxapasnp03-20151007031606/insights_commands/chkconfig_--list
insights-davxapasnp03-20151007031606/insights_commands/ethtool_eth0
insights-davxapasnp03-20151007031606/insights_commands/ethtool_-S_eth0
insights-davxapasnp03-20151007031606/insights_commands/ethtool_-g_eth0
insights-davxapasnp03-20151007031606/insights_commands/ethtool_-i_eth0
insights-davxapasnp03-20151007031606/insights_commands/ethtool_-k_eth0
insights-davxapasnp03-20151007031606/insights_commands/ifconfig_-a
insights-davxapasnp03-20151007031606/insights_commands/ip_route_show_table_all
insights-davxapasnp03-20151007031606/insights_commands/lsmod
insights-davxapasnp03-20151007031606/insights_commands/lspci
insights-davxapasnp03-20151007031606/insights_commands/sysctl_-a
insights-davxapasnp03-20151007031606/insights_commands/df_-alP
insights-davxapasnp03-20151007031606/insights_commands/free
insights-davxapasnp03-20151007031606/insights_commands/ls_-lanR_.boot
insights-davxapasnp03-20151007031606/insights_commands/mount
insights-davxapasnp03-20151007031606/insights_commands/ovs-vsctl_show
insights-davxapasnp03-20151007031606/insights_commands/uptime
insights-davxapasnp03-20151007031606/insights_commands/yum_-C_repolist
insights-davxapasnp03-20151007031606/insights_commands/blkid_-c_.dev.null
insights-davxapasnp03-20151007031606/insights_commands/dmidecode
insights-davxapasnp03-20151007031606/insights_commands/parted_-s
insights-davxapasnp03-20151007031606/insights_commands/hponcfg_-g
insights-davxapasnp03-20151007031606/insights_commands/lsof
insights-davxapasnp03-20151007031606/insights_commands/sestatus_-b
insights-davxapasnp03-20151007031606/insights_commands/systemctl_list-unit-files
insights-davxapasnp03-20151007031606/insights_commands/vgdisplay
insights-davxapasnp03-20151007031606/boot/grub2/grub.cfg
insights-davxapasnp03-20151007031606/etc/hosts
insights-davxapasnp03-20151007031606/etc/kdump.conf
insights-davxapasnp03-20151007031606/etc/lvm/lvm.conf
insights-davxapasnp03-20151007031606/etc/pam.d/password-auth
insights-davxapasnp03-20151007031606/etc/rc.d/rc.local
insights-davxapasnp03-20151007031606/etc/redhat-access-insights/
insights-davxapasnp03-20151007031606/etc/redhat-access-insights/machine-id
insights-davxapasnp03-20151007031606/etc/redhat-release
insights-davxapasnp03-20151007031606/etc/rsyslog.conf
insights-davxapasnp03-20151007031606/etc/security/limits.conf
insights-davxapasnp03-20151007031606/etc/selinux/config
insights-davxapasnp03-20151007031606/etc/ssh/sshd_config
insights-davxapasnp03-20151007031606/etc/sysconfig/kdump
insights-davxapasnp03-20151007031606/etc/sysconfig/netconsole
insights-davxapasnp03-20151007031606/etc/sysconfig/network-scripts/ifcfg-lo
insights-davxapasnp03-20151007031606/etc/sysconfig/network-scripts/ifcfg-eth0
insights-davxapasnp03-20151007031606/etc/sysctl.conf
insights-davxapasnp03-20151007031606/proc/cmdline
insights-davxapasnp03-20151007031606/proc/cpuinfo
insights-davxapasnp03-20151007031606/proc/interrupts
insights-davxapasnp03-20151007031606/proc/meminfo
insights-davxapasnp03-20151007031606/proc/scsi/scsi
insights-davxapasnp03-20151007031606/sys/devices/system/clocksource/clocksource0/current_clocksource
insights-davxapasnp03-20151007031606/sys/kernel/kexec_crash_loaded
insights-davxapasnp03-20151007031606/var/log/messages
insights-davxapasnp03-20151007031606/var/log/yum.log
insights-davxapasnp03-20151007031606/var/log/redhat-access-insights/
insights-davxapasnp03-20151007031606/var/log/redhat-access-insights/redhat-access-insights.log
insights-davxapasnp03-20151007031606/branch_info
""".strip()

DEEP_ROOT = """
tmp/sdc-appblx002-15.corp.com_sosreport/free
tmp/sdc-appblx002-15.corp.com_sosreport/meminfo
tmp/sdc-appblx002-15.corp.com_sosreport/date
tmp/sdc-appblx002-15.corp.com_sosreport/dmesg
tmp/sdc-appblx002-15.corp.com_sosreport/fdisk
tmp/sdc-appblx002-15.corp.com_sosreport/chkconfig
tmp/sdc-appblx002-15.corp.com_sosreport/netstat
tmp/sdc-appblx002-15.corp.com_sosreport/ps
tmp/sdc-appblx002-15.corp.com_sosreport/rpm-Va
tmp/sdc-appblx002-15.corp.com_sosreport/df
tmp/sdc-appblx002-15.corp.com_sosreport/cpuinfo
tmp/sdc-appblx002-15.corp.com_sosreport/rpm-qa
tmp/sdc-appblx002-15.corp.com_sosreport/hostname
tmp/sdc-appblx002-15.corp.com_sosreport/ulimit
tmp/sdc-appblx002-15.corp.com_sosreport/dmidecode
tmp/sdc-appblx002-15.corp.com_sosreport/ifconfig
tmp/sdc-appblx002-15.corp.com_sosreport/lsmod
tmp/sdc-appblx002-15.corp.com_sosreport/mount
tmp/sdc-appblx002-15.corp.com_sosreport/var/log/messages
tmp/sdc-appblx002-15.corp.com_sosreport/var/log/messages-20140413
tmp/sdc-appblx002-15.corp.com_sosreport/var/log/messages-20140330
tmp/sdc-appblx002-15.corp.com_sosreport/var/log/messages-20140406
tmp/sdc-appblx002-15.corp.com_sosreport/uname
""".strip()


class MockTarFile(object):
    """
    Creates a tarfile filled with zero-byte files.
    names should be a list of paths to files, directories should be omitted.
    """

    def __init__(self, names):
        self.tmp_file = tempfile.TemporaryFile()
        self.tf = tarfile.open(fileobj=self.tmp_file, mode="w")
        with tempfile.NamedTemporaryFile() as zero_byte_file:
            filename = zero_byte_file.name
            for name in names.splitlines():
                self.tf.add(filename, arcname=name)

    def getnames(self):
        return self.tf.getnames()

    def issym(self, name):
        return self.tf.getmember(name).issym()

    def isdir(self, name):
        return self.tf.getmember(name).isdir()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tf.close()
        self.tmp_file.close()


def test_single_node():
    with MockTarFile(SINGLE_NODE_UPLOAD) as mtf:
        spec = SpecMapper(mtf)
        assert spec.root == "insights-davxapasnp03-20151007031606/"


def test_multi_node():
    with MockTarFile(CLUSTER_UPLOAD) as mtf:
        spec = SpecMapper(mtf)
        assert spec.root == "./"


def test_soscleaned():
    with MockTarFile(SOSCLEANER_SINGLE_NODE_UPLOAD) as mtf:
        spec = SpecMapper(mtf)
        assert spec.root == "soscleaner-7704572305004757/"


def test_deep_root():
    with MockTarFile(DEEP_ROOT) as mtf:
        spec = SpecMapper(mtf)
        assert spec.root == "tmp/sdc-appblx002-15.corp.com_sosreport/"


def make_cluster_archive(fd, content_type):
    tmp_dir = tempfile.mkdtemp()

    metadata_path = os.path.join(tmp_dir, "metadata.json")
    inner_path = os.path.join(tmp_dir, "inner.tar")

    with open(metadata_path, "w") as mdf:
        json.dump({
            "systems": [
                {
                    "system_id": HEARTBEAT_ID,
                    "product": "OSP",
                    "type": "Director",
                    "links": []
                }
            ],
            "system_id": "test-id",
            "name": "test",
            "product": "OSP",
            "display_name": "insights-heartbeat"
        }, mdf)

    with open(inner_path, "wb") as fp:
        fp.write(fd.read())

    def re_path(p):
        return os.path.join(os.path.basename(os.path.dirname(p)),
                            os.path.basename(p))

    with tempfile.TemporaryFile() as cluster_tar_fp:
        with tarfile.open(fileobj=cluster_tar_fp, mode="w") as tf:
            tf.add(metadata_path, arcname=re_path(metadata_path))
            tf.add(inner_path, arcname=re_path(inner_path))

        shutil.rmtree(tmp_dir)
        cluster_tar_fp.flush()
        cluster_tar_fp.seek(0)
        return cluster_tar_fp.read()


def _unpack_archive(ex, cls):
    dr.load_components("insights.plugins")
    spec_mapper = SpecMapper(ex)
    assert spec_mapper.get_content("machine-id", split=False) == HEARTBEAT_ID
    p = cls(spec_mapper)
    p.process()
    assert p.broker.get(is_insights_heartbeat) == {
        "type": "rule", "error_key": "INSIGHTS_HEARTBEAT"}
    return p


def _common_tests(p):
    assert "insights_heartbeat|INSIGHTS_HEARTBEAT" in [r.get("rule_id") for r in p.rule_results]
    r = p.get_response()
    assert "system" in r
    assert "reports" in r
    assert r["system"]["hostname"] == HEARTBEAT_NAME
    return r


def test_single_evaluator():
    arc_path = insights_heartbeat(metadata={"product_code": "ocp", "role": "node"})
    with TarExtractor().from_path(arc_path) as ex:
        p = _unpack_archive(ex, SingleEvaluator)
        _common_tests(p)
    subprocess.call("rm -rf %s" % arc_path, shell=True)


def test_insights_evaluator():
    arc_path = insights_heartbeat(metadata={"product_code": "ocp", "role": "node"})
    with TarExtractor().from_path(arc_path) as ex:
        p = _unpack_archive(ex, InsightsEvaluator)
        r = _common_tests(p)
        system = r["system"]
        assert system["product"] == "ocp"
        assert system["type"] == "node"
        assert system["system_id"] == HEARTBEAT_ID
    subprocess.call("rm -rf %s" % arc_path, shell=True)


def test_unpack():
    dr.load_components("insights.plugins")
    arc_path = insights_heartbeat()
    with open(arc_path, "rb") as fd:
        cluster_arc = make_cluster_archive(fd, "application/x-gzip")
        with TarExtractor().from_buffer(cluster_arc) as ex:
            spec_mapper = SpecMapper(ex)
            p = InsightsMultiEvaluator(spec_mapper)
            assert p.archive_metadata["system_id"] == "test-id"
            response = p.process()
            assert len(response["archives"]) == 1
            assert response["system"]["type"] == "cluster"
            assert osp in p.broker
            assert HEARTBEAT_ID in p.broker[OSPChild]

    subprocess.call("rm -rf %s" % arc_path, shell=True)
