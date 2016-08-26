import os
import unittest
from falafel.core.specs import SpecMapper
from falafel.core.evaluators import SingleEvaluator, MultiEvaluator
from falafel.core import plugins
from falafel.core.archives import InMemoryExtractor
from falafel.plugins.insights_heartbeat import is_insights_heartbeat
import tarfile
import tempfile
import json
import shutil

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
insights-davxapasnp03-20151007031606/
insights-davxapasnp03-20151007031606/insights_commands/
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
insights-davxapasnp03-20151007031606/boot/
insights-davxapasnp03-20151007031606/boot/grub2/
insights-davxapasnp03-20151007031606/boot/grub2/grub.cfg
insights-davxapasnp03-20151007031606/etc/
insights-davxapasnp03-20151007031606/etc/hosts
insights-davxapasnp03-20151007031606/etc/kdump.conf
insights-davxapasnp03-20151007031606/etc/lvm/
insights-davxapasnp03-20151007031606/etc/lvm/lvm.conf
insights-davxapasnp03-20151007031606/etc/pam.d/
insights-davxapasnp03-20151007031606/etc/pam.d/password-auth
insights-davxapasnp03-20151007031606/etc/rc.d/
insights-davxapasnp03-20151007031606/etc/rc.d/rc.local
insights-davxapasnp03-20151007031606/etc/redhat-access-insights/
insights-davxapasnp03-20151007031606/etc/redhat-access-insights/machine-id
insights-davxapasnp03-20151007031606/etc/redhat-release
insights-davxapasnp03-20151007031606/etc/rsyslog.conf
insights-davxapasnp03-20151007031606/etc/security/
insights-davxapasnp03-20151007031606/etc/security/limits.conf
insights-davxapasnp03-20151007031606/etc/selinux/
insights-davxapasnp03-20151007031606/etc/selinux/config
insights-davxapasnp03-20151007031606/etc/ssh/
insights-davxapasnp03-20151007031606/etc/ssh/sshd_config
insights-davxapasnp03-20151007031606/etc/sysconfig/
insights-davxapasnp03-20151007031606/etc/sysconfig/kdump
insights-davxapasnp03-20151007031606/etc/sysconfig/netconsole
insights-davxapasnp03-20151007031606/etc/sysconfig/network-scripts/
insights-davxapasnp03-20151007031606/etc/sysconfig/network-scripts/ifcfg-lo
insights-davxapasnp03-20151007031606/etc/sysconfig/network-scripts/ifcfg-eth0
insights-davxapasnp03-20151007031606/etc/sysctl.conf
insights-davxapasnp03-20151007031606/proc/
insights-davxapasnp03-20151007031606/proc/cmdline
insights-davxapasnp03-20151007031606/proc/cpuinfo
insights-davxapasnp03-20151007031606/proc/interrupts
insights-davxapasnp03-20151007031606/proc/meminfo
insights-davxapasnp03-20151007031606/proc/scsi/
insights-davxapasnp03-20151007031606/proc/scsi/scsi
insights-davxapasnp03-20151007031606/sys/
insights-davxapasnp03-20151007031606/sys/devices/
insights-davxapasnp03-20151007031606/sys/devices/system/
insights-davxapasnp03-20151007031606/sys/devices/system/clocksource/
insights-davxapasnp03-20151007031606/sys/devices/system/clocksource/clocksource0/
insights-davxapasnp03-20151007031606/sys/devices/system/clocksource/clocksource0/current_clocksource
insights-davxapasnp03-20151007031606/sys/kernel/
insights-davxapasnp03-20151007031606/sys/kernel/kexec_crash_loaded
insights-davxapasnp03-20151007031606/var/
insights-davxapasnp03-20151007031606/var/log/
insights-davxapasnp03-20151007031606/var/log/messages
insights-davxapasnp03-20151007031606/var/log/yum.log
insights-davxapasnp03-20151007031606/var/log/redhat-access-insights/
insights-davxapasnp03-20151007031606/var/log/redhat-access-insights/redhat-access-insights.log
insights-davxapasnp03-20151007031606/branch_info
""".strip()


class MockTarFile(object):

    def __init__(self, names):
        self.names = names.splitlines()

    def getnames(self):
        return self.names

    def issym(self, name):
        return False

    def isdir(self, name):
        return name.endswith("/")


class TestDetermineRoot(unittest.TestCase):

    def test_single_node(self):
        spec = SpecMapper(MockTarFile(SINGLE_NODE_UPLOAD))
        self.assertEqual(spec._determine_root(), "insights-davxapasnp03-20151007031606/")

    def test_multi_node(self):
        spec = SpecMapper(MockTarFile(CLUSTER_UPLOAD))
        self.assertEqual(spec._determine_root(), "./")

    def test_soscleaned(self):
        spec = SpecMapper(MockTarFile(SOSCLEANER_SINGLE_NODE_UPLOAD))
        self.assertEquals(spec._determine_root(), "soscleaner-7704572305004757/")


def make_cluster_archive(fd, content_type):
    tmp_dir = tempfile.mkdtemp()

    metadata_path = os.path.join(tmp_dir, "metadata.json")
    inner_path = os.path.join(tmp_dir, "inner.tar")

    with open(metadata_path, "w") as mdf:
        json.dump({
            "systems": [
                {
                    "system_id": "insights-heartbeat-9cd6f607-6b28-44ef-8481-62b0e7773614",
                    "type": "Director"
                }
            ],
            "system_id": "test-id",
            "name": "test"
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


class TestSingleEvaluator(unittest.TestCase):

    system_id = "99e26bb4823d770cc3c11437fe075d4d1a4db4c7500dad5707faed3b"

    def test_unpack_archive(self):
        with InMemoryExtractor().from_path(os.path.join(HERE, "insights_heartbeat.tar.gz")) as ex:
            plugins.load("falafel.plugins")
            spec_mapper = SpecMapper(ex)
            self.assertEquals(spec_mapper.get_content("machine-id", split=False), self.system_id)
            p = SingleEvaluator(spec_mapper)
            p.pre_mapping()
            p.run_mappers()
            self.assertEquals(p.mapper_results.get(is_insights_heartbeat),
                              [{"type": "rule", "error_key": "INSIGHTS_HEARTBEAT"}])
            p.run_reducers()
            # print [r.get("rule_id") for r in p.reducer_results]
            self.assertTrue("insights_heartbeat|INSIGHTS_HEARTBEAT"
                            in [r.get("rule_id") for r in p.reducer_results])
            r = p.get_response()
            self.assertTrue("system" in r)
            self.assertTrue("reports" in r)


class TestMultiEvaluator(unittest.TestCase):

    def test_unpack(self):
        plugins.load("falafel.plugins")
        fd = InMemoryExtractor().from_path(os.path.join(HERE, "insights_heartbeat.tar.gz"), raw=True)
        cluster_arc = make_cluster_archive(fd, "application/x-gzip")
        fd.close()
        with InMemoryExtractor().from_buffer(cluster_arc) as ex:
            spec_mapper = SpecMapper(ex)
            p = MultiEvaluator(spec_mapper)
            self.assertEquals(p.archive_metadata["system_id"], "test-id")
            response = p.process()
            self.assertEquals(len(response["archives"]), 1)
            self.assertEquals(response["system"]["type"], "cluster")
