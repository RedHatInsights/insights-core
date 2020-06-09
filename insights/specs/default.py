"""
This module defines all datasources used by standard Red Hat Insight components.

To define data sources that override the components in this file, create a
`insights.core.spec_factory.SpecFactory` with "insights.specs" as the constructor
argument. Data sources created with that factory will override components in
this file with the same `name` keyword argument. This allows overriding the
data sources that standard Insights `Parsers` resolve against.
"""

import logging
import os
import re

from insights.core.context import ClusterArchiveContext
from insights.core.context import DockerImageContext
from insights.core.context import HostContext
from insights.core.context import HostArchiveContext
from insights.core.context import OpenShiftContext

from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import CommandOutputProvider, ContentException, DatasourceProvider, RawFileProvider
from insights.core.spec_factory import simple_file, simple_command, glob_file, command_with_args
from insights.core.spec_factory import first_of, foreach_collect, foreach_execute
from insights.core.spec_factory import first_file, listdir
from insights.parsers.mount import Mount, ProcMounts
from insights.parsers.dnf_module import DnfModuleList
from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.satellite_version import SatelliteVersion
from insights.combiners.services import Services
from insights.components.rhel_version import IsRhel8, IsRhel7
from insights.specs import Specs


from grp import getgrgid
from os import stat
from pwd import getpwuid


logger = logging.getLogger(__name__)


def get_owner(filename):
    st = stat(filename)
    name = getpwuid(st.st_uid).pw_name
    group = getgrgid(st.st_gid).gr_name
    return (name, group)


def get_cmd_and_package_in_ps(broker, target_command):
        ps = broker[DefaultSpecs.ps_auxww].content
        ctx = broker[HostContext]
        results = set()
        for p in ps:
            p_splits = p.split(None, 10)
            cmd = p_splits[10].split()[0] if len(p_splits) == 11 else ''
            which = ctx.shell_out("which {0}".format(cmd)) if target_command in os.path.basename(cmd) else None
            resolved = ctx.shell_out("readlink -e {0}".format(which[0])) if which else None
            pkg = ctx.shell_out("/bin/rpm -qf {0}".format(resolved[0])) if resolved else None
            if cmd and pkg is not None:
                results.add("{0} {1}".format(cmd, pkg[0]))
        return results


def _make_rpm_formatter(fmt=None):
    if fmt is None:
        fmt = [
            '"name":"%{NAME}"',
            '"epoch":"%{EPOCH}"',
            '"version":"%{VERSION}"',
            '"release":"%{RELEASE}"',
            '"arch":"%{ARCH}"',
            '"installtime":"%{INSTALLTIME:date}"',
            '"buildtime":"%{BUILDTIME}"',
            '"vendor":"%{VENDOR}"',
            '"buildhost":"%{BUILDHOST}"',
            '"sigpgp":"%{SIGPGP:pgpsig}"'
        ]

    def inner(idx=None):
        if idx:
            return "\{" + ",".join(fmt[:idx]) + "\}\n"
        else:
            return "\{" + ",".join(fmt) + "\}\n"
    return inner


format_rpm = _make_rpm_formatter()


class DefaultSpecs(Specs):
    abrt_status_bare = simple_command("/usr/bin/abrt status --bare=True")
    amq_broker = glob_file("/var/opt/amq-broker/*/etc/broker.xml")
    auditctl_status = simple_command("/sbin/auditctl -s")
    auditd_conf = simple_file("/etc/audit/auditd.conf")
    audit_log = simple_file("/var/log/audit/audit.log")
    autofs_conf = simple_file("/etc/autofs.conf")
    avc_hash_stats = simple_file("/sys/fs/selinux/avc/hash_stats")
    avc_cache_threshold = simple_file("/sys/fs/selinux/avc/cache_threshold")

    @datasource(CloudProvider)
    def is_aws(broker):
        cp = broker[CloudProvider]
        if cp and cp.cloud_provider == CloudProvider.AWS:
            return True
        raise SkipComponent()

    aws_instance_id_doc = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/document --connect-timeout 5", deps=[is_aws])
    aws_instance_id_pkcs7 = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/pkcs7 --connect-timeout 5", deps=[is_aws])

    @datasource(CloudProvider)
    def is_azure(broker):
        cp = broker[CloudProvider]
        if cp and cp.cloud_provider == CloudProvider.AZURE:
            return True
        raise SkipComponent()

    azure_instance_type = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2018-10-01&format=text --connect-timeout 5", deps=[is_azure])
    bios_uuid = simple_command("/usr/sbin/dmidecode -s system-uuid")
    blkid = simple_command("/sbin/blkid -c /dev/null")
    bond = glob_file("/proc/net/bonding/bond*")
    bond_dynamic_lb = glob_file("/sys/class/net/bond[0-9]*/bonding/tlb_dynamic_lb")
    boot_loader_entries = glob_file("/boot/loader/entries/*.conf")
    branch_info = simple_file("/branch_info", kind=RawFileProvider)
    brctl_show = simple_command("/usr/sbin/brctl show")
    candlepin_log = simple_file("/var/log/candlepin/candlepin.log")
    candlepin_error_log = simple_file("/var/log/candlepin/error.log")
    cgroups = simple_file("/proc/cgroups")
    checkin_conf = simple_file("/etc/splice/checkin.conf")
    ps_alxwww = simple_command("/bin/ps alxwww")
    ps_aux = simple_command("/bin/ps aux")
    ps_auxcww = simple_command("/bin/ps auxcww")
    ps_auxww = simple_command("/bin/ps auxww")
    ps_ef = simple_command("/bin/ps -ef")
    ps_eo = simple_command("/usr/bin/ps -eo pid,ppid,comm")

    @datasource(ps_auxww)
    def tomcat_base(broker):
        """Path: Tomcat base path"""
        ps = broker[DefaultSpecs.ps_auxww].content
        results = []
        findall = re.compile(r"\-Dcatalina\.base=(\S+)").findall
        for p in ps:
            found = findall(p)
            if found:
                # Only get the path which is absolute
                results.extend(f for f in found if f[0] == '/')
        return list(set(results))

    catalina_out = foreach_collect(tomcat_base, "%s/catalina.out")
    catalina_server_log = foreach_collect(tomcat_base, "%s/catalina*.log")
    cciss = glob_file("/proc/driver/cciss/cciss*")
    cdc_wdm = simple_file("/sys/bus/usb/drivers/cdc_wdm/module/refcnt")
    ceilometer_central_log = simple_file("/var/log/ceilometer/central.log")
    ceilometer_collector_log = first_file(["/var/log/containers/ceilometer/collector.log", "/var/log/ceilometer/collector.log"])
    ceilometer_compute_log = first_file(["/var/log/containers/ceilometer/compute.log", "/var/log/ceilometer/compute.log"])
    ceilometer_conf = first_file(["/var/lib/config-data/puppet-generated/ceilometer/etc/ceilometer/ceilometer.conf", "/etc/ceilometer/ceilometer.conf"])
    ceph_socket_files = listdir("/var/run/ceph/ceph-*.*.asok", context=HostContext)
    ceph_conf = first_file(["/var/lib/config-data/puppet-generated/ceph/etc/ceph/ceph.conf", "/etc/ceph/ceph.conf"])
    ceph_config_show = foreach_execute(ceph_socket_files, "/usr/bin/ceph daemon %s config show")
    ceph_df_detail = simple_command("/usr/bin/ceph df detail -f json")
    ceph_health_detail = simple_command("/usr/bin/ceph health detail -f json")

    @datasource(ps_auxww)
    def is_ceph_monitor(broker):
        ps = broker[DefaultSpecs.ps_auxww].content
        findall = re.compile(r"ceph\-mon").findall
        if any(findall(p) for p in ps):
            return True
        raise SkipComponent()

    ceph_insights = simple_command("/usr/bin/ceph insights", deps=[is_ceph_monitor])
    ceph_log = glob_file(r"var/log/ceph/ceph.log*")
    ceph_osd_dump = simple_command("/usr/bin/ceph osd dump -f json")
    ceph_osd_df = simple_command("/usr/bin/ceph osd df -f json")
    ceph_osd_ec_profile_ls = simple_command("/usr/bin/ceph osd erasure-code-profile ls")
    ceph_osd_ec_profile_get = foreach_execute(ceph_osd_ec_profile_ls, "/usr/bin/ceph osd erasure-code-profile get %s -f json")
    ceph_osd_log = glob_file(r"var/log/ceph/ceph-osd*.log")
    ceph_osd_tree = simple_command("/usr/bin/ceph osd tree -f json")
    ceph_s = simple_command("/usr/bin/ceph -s -f json")
    ceph_v = simple_command("/usr/bin/ceph -v")
    certificates_enddate = simple_command("/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \; -exec echo 'FileName= {}' \;")
    chkconfig = simple_command("/sbin/chkconfig --list")
    chrony_conf = simple_file("/etc/chrony.conf")
    chronyc_sources = simple_command("/usr/bin/chronyc sources")
    cib_xml = simple_file("/var/lib/pacemaker/cib/cib.xml")
    cinder_api_log = first_file(["/var/log/containers/cinder/cinder-api.log", "/var/log/cinder/cinder-api.log"])
    cinder_conf = first_file(["/var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf", "/etc/cinder/cinder.conf"])
    cinder_volume_log = simple_file("/var/log/cinder/volume.log")
    cloud_init_custom_network = simple_file("/etc/cloud/cloud.cfg.d/99-custom-networking.cfg")
    cloud_init_log = simple_file("/var/log/cloud-init.log")
    cluster_conf = simple_file("/etc/cluster/cluster.conf")
    cmdline = simple_file("/proc/cmdline")
    cni_podman_bridge_conf = simple_file("/etc/cni/net.d/87-podman-bridge.conflist")
    cpe = simple_file("/etc/system-release-cpe")
    # are these locations for different rhel versions?
    cobbler_settings = first_file(["/etc/cobbler/settings", "/conf/cobbler/settings"])
    cobbler_modules_conf = first_file(["/etc/cobbler/modules.conf", "/conf/cobbler/modules.conf"])
    corosync = simple_file("/etc/sysconfig/corosync")

    @datasource([IsRhel7, IsRhel8])
    def corosync_cmapctl_cmd_list(broker):
        if broker.get(IsRhel7):
            return ["/usr/sbin/corosync-cmapctl", 'corosync-cmapctl -d runtime.schedmiss.timestamp', 'corosync-cmapctl -d runtime.schedmiss.delay']
        if broker.get(IsRhel8):
            return ["/usr/sbin/corosync-cmapctl", '/usr/sbin/corosync-cmapctl -m stats', '/usr/sbin/corosync-cmapctl -C schedmiss']
        raise SkipComponent()
    corosync_cmapctl = foreach_execute(corosync_cmapctl_cmd_list, "%s")
    corosync_conf = simple_file("/etc/corosync/corosync.conf")
    cpu_cores = glob_file("sys/devices/system/cpu/cpu[0-9]*/online")
    cpu_siblings = glob_file("sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list")
    cpu_smt_active = simple_file("sys/devices/system/cpu/smt/active")
    cpu_smt_control = simple_file("sys/devices/system/cpu/smt/control")
    cpu_vulns = glob_file("sys/devices/system/cpu/vulnerabilities/*")
    cpu_vulns_meltdown = simple_file("sys/devices/system/cpu/vulnerabilities/meltdown")
    cpu_vulns_spectre_v1 = simple_file("sys/devices/system/cpu/vulnerabilities/spectre_v1")
    cpu_vulns_spectre_v2 = simple_file("sys/devices/system/cpu/vulnerabilities/spectre_v2")
    cpu_vulns_spec_store_bypass = simple_file("sys/devices/system/cpu/vulnerabilities/spec_store_bypass")
    cpuinfo = simple_file("/proc/cpuinfo")
    cpuinfo_max_freq = simple_file("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")
    cpupower_frequency_info = simple_command("/usr/bin/cpupower -c all frequency-info")
    cpuset_cpus = simple_file("/sys/fs/cgroup/cpuset/cpuset.cpus")
    cron_daily_rhsmd = simple_file("/etc/cron.daily/rhsmd")
    crypto_policies_config = simple_file("/etc/crypto-policies/config")
    crypto_policies_state_current = simple_file("/etc/crypto-policies/state/current")
    crypto_policies_opensshserver = simple_file("/etc/crypto-policies/back-ends/opensshserver.config")
    crypto_policies_bind = simple_file("/etc/crypto-policies/back-ends/bind.config")
    current_clocksource = simple_file("/sys/devices/system/clocksource/clocksource0/current_clocksource")
    date = simple_command("/bin/date")
    date_iso = simple_command("/bin/date --iso-8601=seconds")
    date_utc = simple_command("/bin/date --utc")
    df__al = simple_command("/bin/df -al")
    df__alP = simple_command("/bin/df -alP")
    df__li = simple_command("/bin/df -li")
    dig = simple_command("/usr/bin/dig +dnssec . DNSKEY")
    dig_dnssec = simple_command("/usr/bin/dig +dnssec . SOA")
    dig_edns = simple_command("/usr/bin/dig +edns=0 . SOA")
    dig_noedns = simple_command("/usr/bin/dig +noedns . SOA")
    dirsrv = simple_file("/etc/sysconfig/dirsrv")
    dirsrv_access = glob_file("var/log/dirsrv/*/access*")
    dirsrv_errors = glob_file("var/log/dirsrv/*/errors*")
    display_java = simple_command("/usr/sbin/alternatives --display java")
    dmesg = simple_command("/bin/dmesg")
    dmesg_log = simple_file("/var/log/dmesg")
    dmidecode = simple_command("/usr/sbin/dmidecode")
    dmsetup_info = simple_command("/usr/sbin/dmsetup info -C")
    dnf_modules = glob_file("/etc/dnf/modules.d/*.module")
    dnf_module_list = simple_command("/usr/bin/dnf -C --noplugins module list", deps=[IsRhel8])

    @datasource(DnfModuleList)
    def dnf_module_names(broker):
        dml = broker[DnfModuleList]
        if dml:
            return (' ').join(dml)
        raise SkipComponent()

    dnf_module_info = command_with_args("/usr/bin/dnf -C --noplugins module info %s", dnf_module_names, deps=[IsRhel8])
    dnsmasq_config = glob_file(["/etc/dnsmasq.conf", "/etc/dnsmasq.d/*.conf"])
    docker_info = simple_command("/usr/bin/docker info")
    docker_list_containers = simple_command("/usr/bin/docker ps --all --no-trunc")
    docker_list_images = simple_command("/usr/bin/docker images --all --no-trunc --digests")

    @datasource(docker_list_images)
    def docker_image_ids(broker):
        """Command: docker_image_ids"""
        images = broker[DefaultSpecs.docker_list_images]
        try:
            result = set()
            for l in images.content[1:]:
                result.add(l.split(None)[3].strip())
        except:
            raise ContentException("No docker images.")
        if result:
            return list(result)
        raise ContentException("No docker images.")

    # TODO: This parsing is broken.
    @datasource(docker_list_containers)
    def docker_container_ids(broker):
        """Command: docker_container_ids"""
        containers = broker[DefaultSpecs.docker_list_containers]
        try:
            result = set()
            for l in containers.content[1:]:
                result.add(l.split(None)[3].strip())
        except:
            raise ContentException("No docker containers.")
        if result:
            return list(result)
        raise ContentException("No docker containers.")

    docker_host_machine_id = simple_file("/etc/redhat-access-insights/machine-id")
    docker_image_inspect = foreach_execute(docker_image_ids, "/usr/bin/docker inspect %s")
    docker_container_inspect = foreach_execute(docker_container_ids, "/usr/bin/docker inspect %s")
    docker_network = simple_file("/etc/sysconfig/docker-network")
    docker_storage = simple_file("/etc/sysconfig/docker-storage")
    docker_storage_setup = simple_file("/etc/sysconfig/docker-storage-setup")
    docker_sysconfig = simple_file("/etc/sysconfig/docker")

    @datasource(ProcMounts)
    def dumpdev(broker):
        mnt = broker[ProcMounts]
        mounted_dev = [m.mounted_device for m in mnt if m.mount_type in ('ext2', 'ext3', 'ext4')]
        if mounted_dev:
            return mounted_dev
        raise SkipComponent()

    dracut_kdump_capture_service = simple_file("/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service")
    dumpe2fs_h = foreach_execute(dumpdev, "/sbin/dumpe2fs -h %s")
    engine_config_all = simple_command("/usr/bin/engine-config --all")
    engine_log = simple_file("/var/log/ovirt-engine/engine.log")
    etc_journald_conf = simple_file(r"etc/systemd/journald.conf")
    etc_journald_conf_d = glob_file(r"etc/systemd/journald.conf.d/*.conf")
    etc_machine_id = simple_file("/etc/machine-id")
    etcd_conf = simple_file("/etc/etcd/etcd.conf")
    ethernet_interfaces = listdir("/sys/class/net", context=HostContext)
    dcbtool_gc_dcb = foreach_execute(ethernet_interfaces, "/sbin/dcbtool gc %s dcb")
    ethtool = foreach_execute(ethernet_interfaces, "/sbin/ethtool %s")
    ethtool_S = foreach_execute(ethernet_interfaces, "/sbin/ethtool -S %s")
    ethtool_T = foreach_execute(ethernet_interfaces, "/sbin/ethtool -T %s")
    ethtool_a = foreach_execute(ethernet_interfaces, "/sbin/ethtool -a %s")
    ethtool_c = foreach_execute(ethernet_interfaces, "/sbin/ethtool -c %s")
    ethtool_g = foreach_execute(ethernet_interfaces, "/sbin/ethtool -g %s")
    ethtool_i = foreach_execute(ethernet_interfaces, "/sbin/ethtool -i %s")
    ethtool_k = foreach_execute(ethernet_interfaces, "/sbin/ethtool -k %s")
    exim_conf = simple_file("etc/exim.conf")
    facter = simple_command("/usr/bin/facter")
    fc_match = simple_command("/bin/fc-match -sv 'sans:regular:roman' family fontformat")
    fcoeadm_i = simple_command("/usr/sbin/fcoeadm -i")
    fdisk_l = simple_command("/sbin/fdisk -l")
    findmnt_lo_propagation = simple_command("/bin/findmnt -lo+PROPAGATION")
    firewall_cmd_list_all_zones = simple_command("/usr/bin/firewall-cmd --list-all-zones")
    firewalld_conf = simple_file("/etc/firewalld/firewalld.conf")
    foreman_production_log = simple_file("/var/log/foreman/production.log")
    foreman_proxy_conf = simple_file("/etc/foreman-proxy/settings.yml")
    foreman_proxy_log = simple_file("/var/log/foreman-proxy/proxy.log")
    foreman_satellite_log = simple_file("/var/log/foreman-installer/satellite.log")
    foreman_ssl_access_ssl_log = simple_file("var/log/httpd/foreman-ssl_access_ssl.log")
    foreman_rake_db_migrate_status = simple_command('/usr/sbin/foreman-rake db:migrate:status')
    foreman_tasks_config = first_file(["/etc/sysconfig/foreman-tasks", "/etc/sysconfig/dynflowd"])
    freeipa_healthcheck_log = simple_file("/var/log/ipa/healthcheck/healthcheck.log")
    fstab = simple_file("/etc/fstab")
    galera_cnf = first_file(["/var/lib/config-data/puppet-generated/mysql/etc/my.cnf.d/galera.cnf", "/etc/my.cnf.d/galera.cnf"])
    getconf_page_size = simple_command("/usr/bin/getconf PAGE_SIZE")
    getenforce = simple_command("/usr/sbin/getenforce")
    getsebool = simple_command("/usr/sbin/getsebool -a")
    glance_api_conf = first_file(["/var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-api.conf", "/etc/glance/glance-api.conf"])
    glance_api_log = first_file(["/var/log/containers/glance/api.log", "/var/log/glance/api.log"])
    glance_cache_conf = first_file(["/var/lib/config-data/puppet-generated/glance_api/etc/glance/glance-cache.conf", "/etc/glance/glance-cache.conf"])
    glance_registry_conf = simple_file("/etc/glance/glance-registry.conf")
    gluster_v_info = simple_command("/usr/sbin/gluster volume info")
    gluster_v_status = simple_command("/usr/sbin/gluster volume status")
    gluster_peer_status = simple_command("/usr/sbin/gluster peer status")
    gnocchi_conf = first_file(["/var/lib/config-data/puppet-generated/gnocchi/etc/gnocchi/gnocchi.conf", "/etc/gnocchi/gnocchi.conf"])
    gnocchi_metricd_log = first_file(["/var/log/containers/gnocchi/gnocchi-metricd.log", "/var/log/gnocchi/metricd.log"])
    grub_conf = simple_file("/boot/grub/grub.conf")
    grub_config_perms = simple_command("/bin/ls -l /boot/grub2/grub.cfg")  # only RHEL7 and updwards
    grub_efi_conf = simple_file("/boot/efi/EFI/redhat/grub.conf")
    grub1_config_perms = simple_command("/bin/ls -l /boot/grub/grub.conf")  # RHEL6
    grub2_cfg = simple_file("/boot/grub2/grub.cfg")
    grub2_efi_cfg = simple_file("boot/efi/EFI/redhat/grub.cfg")
    grubby_default_index = simple_command("/usr/sbin/grubby --default-index")  # only RHEL7 and updwards
    grubby_default_kernel = simple_command("/sbin/grubby --default-kernel")
    hammer_ping = simple_command("/usr/bin/hammer ping")
    hammer_task_list = simple_command("/usr/bin/hammer --config /root/.hammer/cli.modules.d/foreman.yml --output csv task list --search 'state=running AND ( label=Actions::Candlepin::ListenOnCandlepinEvents OR label=Actions::Katello::EventQueue::Monitor )'")
    haproxy_cfg = first_file(["/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.cfg"])
    heat_api_log = first_file(["/var/log/containers/heat/heat_api.log", "/var/log/heat/heat-api.log", "/var/log/heat/heat_api.log"])
    heat_conf = first_file(["/var/lib/config-data/puppet-generated/heat/etc/heat/heat.conf", "/etc/heat/heat.conf"])
    heat_crontab = simple_command("/usr/bin/crontab -l -u heat")
    heat_crontab_container = simple_command("docker exec heat_api_cron /usr/bin/crontab -l -u heat")
    heat_engine_log = first_file(["/var/log/containers/heat/heat-engine.log", "/var/log/heat/heat-engine.log"])
    hostname = simple_command("/bin/hostname -f")
    hostname_default = simple_command("/bin/hostname")
    hostname_short = simple_command("/bin/hostname -s")
    hosts = simple_file("/etc/hosts")
    hponcfg_g = simple_command("/sbin/hponcfg -g")
    httpd_access_log = simple_file("/var/log/httpd/access_log")
    httpd_conf = glob_file(
        [
            "/etc/httpd/conf/httpd.conf",
            "/etc/httpd/conf.d/*.conf",
            "/etc/httpd/conf.d/*/*.conf",
            "/etc/httpd/conf.modules.d/*.conf"
        ]
    )
    httpd_conf_scl_httpd24 = glob_file(
        [
            "/opt/rh/httpd24/root/etc/httpd/conf/httpd.conf",
            "/opt/rh/httpd24/root/etc/httpd/conf.d/*.conf",
            "/opt/rh/httpd24/root/etc/httpd/conf.d/*/*.conf",
            "/opt/rh/httpd24/root/etc/httpd/conf.modules.d/*.conf"
        ]
    )
    httpd_conf_scl_jbcs_httpd24 = glob_file(
        [
            "/opt/rh/jbcs-httpd24/root/etc/httpd/conf/httpd.conf",
            "/opt/rh/jbcs-httpd24/root/etc/httpd/conf.d/*.conf",
            "/opt/rh/jbcs-httpd24/root/etc/httpd/conf.d/*/*.conf",
            "/opt/rh/jbcs-httpd24/root/etc/httpd/conf.modules.d/*.conf"
        ]
    )
    httpd_error_log = simple_file("var/log/httpd/error_log")
    httpd24_httpd_error_log = simple_file("/opt/rh/httpd24/root/etc/httpd/logs/error_log")
    jbcs_httpd24_httpd_error_log = simple_file("/opt/rh/jbcs-httpd24/root/etc/httpd/logs/error_log")
    httpd_pid = simple_command("/usr/bin/pgrep -o httpd")
    httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")

    @datasource(SatelliteVersion)
    def is_sat(broker):
        sat = broker[SatelliteVersion]
        if sat:
            return True
        raise SkipComponent()

    satellite_enabled_features = simple_command("/usr/bin/curl -sk https://localhost:9090/features --connect-timeout 5", deps=[is_sat])
    virt_uuid_facts = simple_file("/etc/rhsm/facts/virt_uuid.facts")

    @datasource(ps_auxww)
    def httpd_cmd(broker):
        """Command: httpd_command"""
        ps = broker[DefaultSpecs.ps_auxww].content
        ps_httpds = set()
        for p in ps:
            p_splits = p.split(None, 10)
            if len(p_splits) >= 11:
                cmd = p_splits[10].split()[0]
                # Should compatible with RHEL6
                # e.g. /usr/sbin/httpd, /usr/sbin/httpd.worker and /usr/sbin/httpd.event
                #      and SCL's httpd24-httpd
                if os.path.basename(cmd).startswith('httpd'):
                    ps_httpds.add(cmd)
        # Running multiple httpd instances on RHEL is supported
        # https://access.redhat.com/solutions/21680
        return list(ps_httpds)

    @datasource(Mount)
    def httpd_on_nfs(broker):
        import json
        mnt = broker[Mount]
        mps = mnt.search(mount_type='nfs4')
        # get nfs 4.0 mount points
        nfs_mounts = [m.mount_point for m in mps if m['mount_options'].get("vers") == "4.0"]
        if nfs_mounts:
            # get all httpd ps
            httpd_pids = broker[HostContext].shell_out("pgrep httpd")
            if httpd_pids:
                open_nfs_files = 0
                lsof_cmds = ["lsof -p {}".format(pid) for pid in httpd_pids if pid]
                # maybe there are thousands open files
                httpd_open_files = broker[HostContext].shell_out(lsof_cmds)
                for line in httpd_open_files:
                    items = line.split()
                    if len(items) > 8 and items[8].startswith(tuple(nfs_mounts)):
                        open_nfs_files += 1
                result_dict = {"http_ids": httpd_pids, "nfs_mounts": nfs_mounts, "open_nfs_files": open_nfs_files}
                return DatasourceProvider(content=json.dumps(result_dict), relative_path="httpd_open_nfsV4_files")
        raise SkipComponent()

    httpd_M = foreach_execute(httpd_cmd, "%s -M")
    httpd_ssl_access_log = simple_file("/var/log/httpd/ssl_access_log")
    httpd_ssl_error_log = simple_file("/var/log/httpd/ssl_error_log")
    httpd_V = foreach_execute(httpd_cmd, "%s -V")
    ifcfg = glob_file("/etc/sysconfig/network-scripts/ifcfg-*")
    ifcfg_static_route = glob_file("/etc/sysconfig/network-scripts/route-*")
    ifconfig = simple_command("/sbin/ifconfig -a")
    imagemagick_policy = glob_file(["/etc/ImageMagick/policy.xml", "/usr/lib*/ImageMagick-6.5.4/config/policy.xml"])
    init_ora = simple_file("${ORACLE_HOME}/dbs/init.ora")
    initscript = glob_file(r"etc/rc.d/init.d/*")
    init_process_cgroup = simple_file("/proc/1/cgroup")
    interrupts = simple_file("/proc/interrupts")
    ip_addr = simple_command("/sbin/ip addr")
    ip_addresses = simple_command("/bin/hostname -I")
    ip_route_show_table_all = simple_command("/sbin/ip route show table all")
    ip_s_link = simple_command("/sbin/ip -s -d link")
    ipaupgrade_log = simple_file("/var/log/ipaupgrade.log")
    ipcs_m = simple_command("/usr/bin/ipcs -m")
    ipcs_m_p = simple_command("/usr/bin/ipcs -m -p")
    ipcs_s = simple_command("/usr/bin/ipcs -s")

    @datasource(ipcs_s)
    def semid(broker):
        """Command: semids"""
        source = broker[DefaultSpecs.ipcs_s].content
        results = set()
        for s in source:
            s_splits = s.split()
            # key        semid      owner      perms      nsems
            # 0x00000000 65536      apache     600        1
            if len(s_splits) == 5 and s_splits[1].isdigit():
                results.add(s_splits[1])
        return results

    ipcs_s_i = foreach_execute(semid, "/usr/bin/ipcs -s -i %s")
    iptables = simple_command("/sbin/iptables-save")
    iptables_permanent = simple_file("etc/sysconfig/iptables")
    ip6tables = simple_command("/sbin/ip6tables-save")
    ip6tables_permanent = simple_file("etc/sysconfig/ip6tables")
    ipv4_neigh = simple_command("/sbin/ip -4 neighbor show nud all")
    ipv6_neigh = simple_command("/sbin/ip -6 neighbor show nud all")
    ironic_inspector_log = simple_file("/var/log/ironic-inspector/ironic-inspector.log")
    ironic_conf = first_file(["/var/lib/config-data/puppet-generated/ironic/etc/ironic/ironic.conf", "/etc/ironic/ironic.conf"])
    iscsiadm_m_session = simple_command("/usr/sbin/iscsiadm -m session")
    katello_service_status = simple_command("/usr/bin/katello-service status")
    kdump_conf = simple_file("/etc/kdump.conf")
    kerberos_kdc_log = simple_file("var/log/krb5kdc.log")
    kernel_config = glob_file("/boot/config-*")
    kexec_crash_loaded = simple_file("/sys/kernel/kexec_crash_loaded")
    kexec_crash_size = simple_file("/sys/kernel/kexec_crash_size")
    keystone_conf = first_file(["/var/lib/config-data/puppet-generated/keystone/etc/keystone/keystone.conf", "/etc/keystone/keystone.conf"])
    keystone_crontab = simple_command("/usr/bin/crontab -l -u keystone")
    keystone_crontab_container = simple_command("docker exec keystone_cron /usr/bin/crontab -l -u keystone")
    keystone_log = first_file(["/var/log/containers/keystone/keystone.log", "/var/log/keystone/keystone.log"])
    kpatch_list = simple_command("/usr/sbin/kpatch list")
    krb5 = glob_file([r"etc/krb5.conf", r"etc/krb5.conf.d/*"])
    ksmstate = simple_file("/sys/kernel/mm/ksm/run")
    kubepods_cpu_quota = glob_file("/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod[a-f0-9_]*.slice/cpu.cfs_quota_us")
    last_upload_globs = ["/etc/redhat-access-insights/.lastupload", "/etc/insights-client/.lastupload"]
    lastupload = glob_file(last_upload_globs)
    libkeyutils = simple_command("/usr/bin/find -L /lib /lib64 -name 'libkeyutils.so*'")
    libkeyutils_objdumps = simple_command('/usr/bin/find -L /lib /lib64 -name libkeyutils.so.1 -exec objdump -x "{}" \;')
    libvirtd_log = simple_file("/var/log/libvirt/libvirtd.log")
    libvirtd_qemu_log = glob_file(r"/var/log/libvirt/qemu/*.log")
    limits_conf = glob_file(["/etc/security/limits.conf", "/etc/security/limits.d/*.conf"])
    locale = simple_command("/usr/bin/locale")
    localtime = simple_command("/usr/bin/file -L /etc/localtime")
    logrotate_conf = glob_file(["/etc/logrotate.conf", "/etc/logrotate.d/*"])
    lpstat_p = simple_command("/usr/bin/lpstat -p")
    ls_boot = simple_command("/bin/ls -lanR /boot")
    ls_dev = simple_command("/bin/ls -lanR /dev")
    ls_disk = simple_command("/bin/ls -lanR /dev/disk")
    ls_docker_volumes = simple_command("/bin/ls -lanR /var/lib/docker/volumes")
    ls_edac_mc = simple_command("/bin/ls -lan /sys/devices/system/edac/mc")
    etc_and_sub_dirs = sorted(["/etc", "/etc/pki/tls/private", "/etc/pki/tls/certs",
        "/etc/pki/ovirt-vmconsole", "/etc/nova/migration", "/etc/sysconfig",
        "/etc/cloud/cloud.cfg.d"])
    ls_etc = simple_command("ls -lan {0}".format(' '.join(etc_and_sub_dirs)))
    ls_lib_firmware = simple_command("/bin/ls -lanR /lib/firmware")
    ls_ocp_cni_openshift_sdn = simple_command("/bin/ls -l /var/lib/cni/networks/openshift-sdn")
    ls_origin_local_volumes_pods = simple_command("/bin/ls -l /var/lib/origin/openshift.local.volumes/pods")
    ls_osroot = simple_command("/bin/ls -lan /")
    ls_run_systemd_generator = simple_command("/bin/ls -lan /run/systemd/generator")
    ls_R_var_lib_nova_instances = simple_command("/bin/ls -laR /var/lib/nova/instances")
    ls_sys_firmware = simple_command("/bin/ls -lanR /sys/firmware")
    ls_usr_lib64 = simple_command("/bin/ls -lan /usr/lib64")
    ls_usr_sbin = simple_command("/bin/ls -ln /usr/sbin")
    ls_var_lib_mongodb = simple_command("/bin/ls -la /var/lib/mongodb")
    ls_var_lib_nova_instances = simple_command("/bin/ls -laRZ /var/lib/nova/instances")
    ls_var_log = simple_command("/bin/ls -la /var/log /var/log/audit")
    ls_var_opt_mssql = simple_command("/bin/ls -ld /var/opt/mssql")
    ls_var_opt_mssql_log = simple_command("/bin/ls -la /var/opt/mssql/log")
    ls_var_spool_clientmq = simple_command("/bin/ls -ln /var/spool/clientmqueue")
    ls_var_spool_postfix_maildrop = simple_command("/bin/ls -ln /var/spool/postfix/maildrop")
    ls_var_tmp = simple_command("/bin/ls -ln /var/tmp")
    ls_var_run = simple_command("/bin/ls -lnL /var/run")
    ls_var_www = simple_command("/bin/ls -la /dev/null /var/www")  # https://github.com/RedHatInsights/insights-core/issues/827
    lsblk = simple_command("/bin/lsblk")
    lsblk_pairs = simple_command("/bin/lsblk -P -o NAME,KNAME,MAJ:MIN,FSTYPE,MOUNTPOINT,LABEL,UUID,RA,RO,RM,MODEL,SIZE,STATE,OWNER,GROUP,MODE,ALIGNMENT,MIN-IO,OPT-IO,PHY-SEC,LOG-SEC,ROTA,SCHED,RQ-SIZE,TYPE,DISC-ALN,DISC-GRAN,DISC-MAX,DISC-ZERO")
    lscpu = simple_command("/usr/bin/lscpu")
    lsinitrd = simple_command("/usr/bin/lsinitrd")
    lsinitrd_lvm_conf = first_of([
                                 simple_command("/sbin/lsinitrd -f /etc/lvm/lvm.conf"),
                                 simple_command("/usr/bin/lsinitrd -f /etc/lvm/lvm.conf")
                                 ])
    lsmod = simple_command("/sbin/lsmod")
    lsof = simple_command("/usr/sbin/lsof")
    lspci = simple_command("/sbin/lspci -k")
    lssap = simple_command("/usr/sap/hostctrl/exe/lssap")
    lsscsi = simple_command("/usr/bin/lsscsi")
    lvdisplay = simple_command("/sbin/lvdisplay")
    lvm_conf = simple_file("/etc/lvm/lvm.conf")
    lvs = None  # simple_command('/sbin/lvs -a -o +lv_tags,devices --config="global{locking_type=0}"')
    lvs_noheadings = simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor --config=\"global{locking_type=0}\"")
    lvs_noheadings_all = simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype --config='global{locking_type=0} devices{filter=[\"a|.*|\"]}'")
    mac_addresses = glob_file("/sys/class/net/*/address")
    machine_id = first_file(["etc/insights-client/machine-id", "etc/redhat-access-insights/machine-id", "etc/redhat_access_proactive/machine-id"])
    manila_conf = first_file(["/var/lib/config-data/puppet-generated/manila/etc/manila/manila.conf", "/etc/manila/manila.conf"])
    mariadb_log = simple_file("/var/log/mariadb/mariadb.log")
    max_uid = simple_command("/bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd")
    md5chk_files = foreach_execute(
        ["/etc/pki/product/69.pem", "/etc/pki/product-default/69.pem", "/usr/lib/libsoftokn3.so", "/usr/lib64/libsoftokn3.so", "/usr/lib/libfreeblpriv3.so", "/usr/lib64/libfreeblpriv3.so"],
        "/usr/bin/md5sum %s")
    mdstat = simple_file("/proc/mdstat")
    meminfo = first_file(["/proc/meminfo", "/meminfo"])
    messages = simple_file("/var/log/messages")
    metadata_json = simple_file("metadata.json", context=ClusterArchiveContext, kind=RawFileProvider)
    mistral_executor_log = simple_file("/var/log/mistral/executor.log")
    mlx4_port = glob_file("/sys/bus/pci/devices/*/mlx4_port[0-9]")
    modinfo_i40e = simple_command("/sbin/modinfo i40e")
    modinfo_igb = simple_command("/sbin/modinfo igb")
    modinfo_ixgbe = simple_command("/sbin/modinfo ixgbe")
    modinfo_veth = simple_command("/sbin/modinfo veth")
    modinfo_vmxnet3 = simple_command("/sbin/modinfo vmxnet3")

    @datasource(lsmod, context=HostContext)
    def lsmod_only_names(broker):
        lsmod = broker[DefaultSpecs.lsmod].content
        # skip the title
        return [line.split()[0] for line in lsmod[1:] if line.strip()]

    modinfo = foreach_execute(lsmod_only_names, "modinfo %s")

    @datasource(lsmod_only_names, context=HostContext)
    def lsmod_all_names(broker):
        mod_list = broker[DefaultSpecs.lsmod_only_names]
        if mod_list:
            return ' '.join(mod_list)
        raise SkipComponent()

    modinfo_all = command_with_args("modinfo %s", lsmod_all_names)

    modprobe = glob_file(["/etc/modprobe.conf", "/etc/modprobe.d/*.conf"])
    sysconfig_mongod = glob_file([
                                 "etc/sysconfig/mongod",
                                 "etc/opt/rh/rh-mongodb26/sysconfig/mongod"
                                 ])
    mongod_conf = glob_file([
                            "/etc/mongod.conf",
                            "/etc/mongodb.conf",
                            "/etc/opt/rh/rh-mongodb26/mongod.conf"
                            ])
    mount = simple_command("/bin/mount")
    mounts = simple_file("/proc/mounts")
    mssql_conf = simple_file("/var/opt/mssql/mssql.conf")
    multicast_querier = simple_command("/usr/bin/find /sys/devices/virtual/net/ -name multicast_querier -print -exec cat {} \;")
    multipath_conf = simple_file("/etc/multipath.conf")
    multipath_conf_initramfs = simple_command("/bin/lsinitrd -f /etc/multipath.conf")
    multipath__v4__ll = simple_command("/sbin/multipath -v4 -ll")
    mysqladmin_status = simple_command("/bin/mysqladmin status")
    mysqladmin_vars = simple_command("/bin/mysqladmin variables")
    mysql_log = glob_file([
                          "/var/log/mysql/mysqld.log",
                          "/var/log/mysql.log",
                          "/var/opt/rh/rh-mysql*/log/mysql/mysqld.log"
                          ])
    mysqld_pid = simple_command("/usr/bin/pgrep -n mysqld")
    mysqld_limits = foreach_collect(mysqld_pid, "/proc/%s/limits")
    named_checkconf_p = simple_command("/usr/sbin/named-checkconf -p")
    namespace = simple_command("/bin/ls /var/run/netns")
    ndctl_list_Ni = simple_command("/usr/bin/ndctl list -Ni")
    ip_netns_exec_namespace_lsof = foreach_execute(namespace, "/sbin/ip netns exec %s lsof -i")
    netconsole = simple_file("/etc/sysconfig/netconsole")
    netstat = simple_command("/bin/netstat -neopa")
    netstat_agn = simple_command("/bin/netstat -agn")
    netstat_i = simple_command("/bin/netstat -i")
    netstat_s = simple_command("/bin/netstat -s")
    networkmanager_dispatcher_d = glob_file("/etc/NetworkManager/dispatcher.d/*-dhclient")
    neutron_conf = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf", "/etc/neutron/neutron.conf"])
    neutron_dhcp_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/dhcp_agent.ini", "/etc/neutron/dhcp_agent.ini"])
    neutron_l3_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini", "/etc/neutron/l3_agent.ini"])
    neutron_l3_agent_log = simple_file("/var/log/neutron/l3-agent.log")
    neutron_metadata_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/metadata_agent.ini", "/etc/neutron/metadata_agent.ini"])
    neutron_metadata_agent_log = first_file(["/var/log/containers/neutron/metadata-agent.log", "/var/log/neutron/metadata-agent.log"])
    neutron_ml2_conf = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/ml2_conf.ini", "/etc/neutron/plugins/ml2/ml2_conf.ini"])
    neutron_ovs_agent_log = first_file(["/var/log/containers/neutron/openvswitch-agent.log", "/var/log/neutron/openvswitch-agent.log"])
    neutron_plugin_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugin.ini", "/etc/neutron/plugin.ini"])
    neutron_server_log = first_file(["/var/log/containers/neutron/server.log", "/var/log/neutron/server.log"])
    nfnetlink_queue = simple_file("/proc/net/netfilter/nfnetlink_queue")
    nfs_exports = simple_file("/etc/exports")
    nfs_exports_d = glob_file("/etc/exports.d/*.exports")
    nginx_conf = glob_file([
                           "/etc/nginx/*.conf", "/etc/nginx/conf.d/*", "/etc/nginx/default.d/*",
                           "/opt/rh/nginx*/root/etc/nginx/*.conf", "/opt/rh/nginx*/root/etc/nginx/conf.d/*", "/opt/rh/nginx*/root/etc/nginx/default.d/*",
                           "/etc/opt/rh/rh-nginx*/nginx/*.conf", "/etc/opt/rh/rh-nginx*/nginx/conf.d/*", "/etc/opt/rh/rh-nginx*/nginx/default.d/*"
                           ])
    nmcli_conn_show = simple_command("/usr/bin/nmcli conn show")
    nmcli_dev_show = simple_command("/usr/bin/nmcli dev show")
    nova_api_log = first_file(["/var/log/containers/nova/nova-api.log", "/var/log/nova/nova-api.log"])
    nova_compute_log = first_file(["/var/log/containers/nova/nova-compute.log", "/var/log/nova/nova-compute.log"])
    nova_conf = first_file([
                           "/var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf",
                           "/var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf",
                           "/etc/nova/nova.conf"
                           ])
    nova_crontab = simple_command("/usr/bin/crontab -l -u nova")
    nova_crontab_container = simple_command("docker exec nova_api_cron /usr/bin/crontab -l -u nova")
    nova_uid = simple_command("/usr/bin/id -u nova")
    nova_migration_uid = simple_command("/usr/bin/id -u nova_migration")
    nscd_conf = simple_file("/etc/nscd.conf")
    nsswitch_conf = simple_file("/etc/nsswitch.conf")
    ntp_conf = simple_file("/etc/ntp.conf")
    ntpq_leap = simple_command("/usr/sbin/ntpq -c 'rv 0 leap'")
    ntpq_pn = simple_command("/usr/sbin/ntpq -pn")
    ntptime = simple_command("/usr/sbin/ntptime")
    numa_cpus = glob_file("/sys/devices/system/node/node[0-9]*/cpulist")
    numeric_user_group_name = simple_command("/bin/grep -c '^[[:digit:]]' /etc/passwd /etc/group")
    nvme_core_io_timeout = simple_file("/sys/module/nvme_core/parameters/io_timeout")
    oc_get_bc = simple_command("/usr/bin/oc get bc -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_build = simple_command("/usr/bin/oc get build -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_clusterrole_with_config = simple_command("/usr/bin/oc get clusterrole --config /etc/origin/master/admin.kubeconfig")
    oc_get_clusterrolebinding_with_config = simple_command("/usr/bin/oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig")
    oc_get_dc = simple_command("/usr/bin/oc get dc -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_egressnetworkpolicy = simple_command("/usr/bin/oc get egressnetworkpolicy -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_endpoints = simple_command("/usr/bin/oc get endpoints -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_event = simple_command("/usr/bin/oc get event -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_node = simple_command("/usr/bin/oc get nodes -o yaml", context=OpenShiftContext)
    oc_get_pod = simple_command("/usr/bin/oc get pod -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_project = simple_command("/usr/bin/oc get project -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_pv = simple_command("/usr/bin/oc get pv -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_pvc = simple_command("/usr/bin/oc get pvc -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_rc = simple_command("/usr/bin/oc get rc -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_role = simple_command("/usr/bin/oc get role -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_rolebinding = simple_command("/usr/bin/oc get rolebinding -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_route = simple_command("/usr/bin/oc get route -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_service = simple_command("/usr/bin/oc get service -o yaml --all-namespaces", context=OpenShiftContext)
    oc_get_configmap = simple_command("/usr/bin/oc get configmap -o yaml --all-namespaces", context=OpenShiftContext)
    octavia_conf = simple_file("/var/lib/config-data/puppet-generated/octavia/etc/octavia/octavia.conf")
    odbc_ini = simple_file("/etc/odbc.ini")
    odbcinst_ini = simple_file("/etc/odbcinst.ini")
    crt = simple_command("/usr/bin/find /etc/origin/node /etc/origin/master -type f -path '*.crt'")
    openshift_certificates = foreach_execute(crt, "/usr/bin/openssl x509 -noout -enddate -in %s")
    openshift_fluentd_pid = simple_command("/usr/bin/pgrep -n fluentd")
    openshift_fluentd_environ = foreach_collect(openshift_fluentd_pid, "/proc/%s/environ")
    openshift_hosts = simple_file("/root/.config/openshift/hosts")
    openshift_router_pid = simple_command("/usr/bin/pgrep -n openshift-route")
    openshift_router_environ = foreach_collect(openshift_router_pid, "/proc/%s/environ")
    openvswitch_other_config = simple_command("/usr/bin/ovs-vsctl -t 5 get Open_vSwitch . other_config")
    openvswitch_server_log = simple_file('/var/log/openvswitch/ovsdb-server.log')
    openvswitch_daemon_log = simple_file('/var/log/openvswitch/ovs-vswitchd.log')
    os_release = simple_file("etc/os-release")
    osa_dispatcher_log = first_file([
                                    "/var/log/rhn/osa-dispatcher.log",
                                    "/rhn-logs/rhn/osa-dispatcher.log"
                                    ])
    ose_master_config = simple_file("/etc/origin/master/master-config.yaml")
    ose_node_config = simple_file("/etc/origin/node/node-config.yaml")
    ovirt_engine_confd = glob_file("/etc/ovirt-engine/engine.conf.d/*")
    ovirt_engine_server_log = simple_file("/var/log/ovirt-engine/server.log")
    ovirt_engine_ui_log = simple_file("/var/log/ovirt-engine/ui.log")
    ovirt_engine_boot_log = simple_file("/var/log/ovirt-engine/boot.log")
    ovirt_engine_console_log = simple_file("/var/log/ovirt-engine/console.log")
    ovs_vsctl_list_br = simple_command("/usr/bin/ovs-vsctl list-br")
    ovs_appctl_fdb_show_bridge = foreach_execute(ovs_vsctl_list_br, "/usr/bin/ovs-appctl fdb/show %s")
    ovs_ofctl_dump_flows = foreach_execute(ovs_vsctl_list_br, "/usr/bin/ovs-ofctl dump-flows %s")
    ovs_vsctl_list_bridge = simple_command("/usr/bin/ovs-vsctl list bridge")
    ovs_vsctl_show = simple_command("/usr/bin/ovs-vsctl show")
    ovs_vswitchd_pid = simple_command("/usr/bin/pgrep -o ovs-vswitchd")
    ovs_vswitchd_limits = foreach_collect(ovs_vswitchd_pid, "/proc/%s/limits")
    pacemaker_log = first_file(["/var/log/pacemaker.log", "/var/log/pacemaker/pacemaker.log"])
    pci_rport_target_disk_paths = simple_command("/usr/bin/find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f")

    @datasource(Services, context=HostContext)
    def pcp_enabled(broker):
        if not broker[Services].is_on("pmproxy"):
            raise SkipComponent("pmproxy not enabled")

    pcp_metrics = simple_command("/usr/bin/curl -s http://127.0.0.1:44322/metrics --connect-timeout 5", deps=[pcp_enabled])

    @datasource(ps_auxww, context=HostContext)
    def package_and_java(broker):
        """Command: package_and_java"""
        return get_cmd_and_package_in_ps(broker, 'java')

    package_provides_java = foreach_execute(package_and_java, "echo %s")

    @datasource(ps_auxww, context=HostContext)
    def package_and_httpd(broker):
        """Command: package_and_httpd"""
        return get_cmd_and_package_in_ps(broker, 'httpd')

    package_provides_httpd = foreach_execute(package_and_httpd, "echo %s")
    pam_conf = simple_file("/etc/pam.conf")
    parted__l = simple_command("/sbin/parted -l -s")
    partitions = simple_file("/proc/partitions")
    passenger_status = simple_command("/usr/bin/passenger-status")
    password_auth = simple_file("/etc/pam.d/password-auth")
    pcs_config = simple_command("/usr/sbin/pcs config")
    pcs_quorum_status = simple_command("/usr/sbin/pcs quorum status")
    pcs_status = simple_command("/usr/sbin/pcs status")
    pluginconf_d = glob_file("/etc/yum/pluginconf.d/*.conf")
    postgresql_conf = first_file([
                                 "/var/lib/pgsql/data/postgresql.conf",
                                 "/opt/rh/postgresql92/root/var/lib/pgsql/data/postgresql.conf",
                                 "database/postgresql.conf"
                                 ])
    postgresql_log = first_of([
                              glob_file("/var/lib/pgsql/data/pg_log/postgresql-*.log"),
                              glob_file("/opt/rh/postgresql92/root/var/lib/pgsql/data/pg_log/postgresql-*.log"),
                              glob_file("/database/postgresql-*.log")
                              ])
    puppetserver_config = simple_file("/etc/sysconfig/puppetserver")
    prev_uploader_log = simple_file("var/log/redhat-access-insights/redhat-access-insights.log.1")
    proc_netstat = simple_file("proc/net/netstat")
    proc_slabinfo = simple_file("proc/slabinfo")
    proc_snmp_ipv4 = simple_file("proc/net/snmp")
    proc_snmp_ipv6 = simple_file("proc/net/snmp6")
    proc_stat = simple_file("proc/stat")
    pulp_worker_defaults = simple_file("etc/default/pulp_workers")
    pvs = simple_command('/sbin/pvs -a -v -o +pv_mda_free,pv_mda_size,pv_mda_count,pv_mda_used_count,pe_count --config="global{locking_type=0}"')
    pvs_noheadings = simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config=\"global{locking_type=0}\"")
    pvs_noheadings_all = simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config='global{locking_type=0} devices{filter=[\"a|.*|\"]}'")
    qemu_conf = simple_file("/etc/libvirt/qemu.conf")
    qemu_xml = glob_file(r"/etc/libvirt/qemu/*.xml")
    qpid_stat_g = simple_command("/usr/bin/qpid-stat -g --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671")
    qpid_stat_q = simple_command("/usr/bin/qpid-stat -q --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671")
    qpid_stat_u = simple_command("/usr/bin/qpid-stat -u --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671")
    qpidd_conf = simple_file("/etc/qpid/qpidd.conf")
    rabbitmq_env = simple_file("/etc/rabbitmq/rabbitmq-env.conf")
    rabbitmq_logs = glob_file("/var/log/rabbitmq/rabbit@*.log", ignore=".*rabbit@.*(?<!-sasl).log$")
    rabbitmq_policies = simple_command("/usr/sbin/rabbitmqctl list_policies")
    rabbitmq_queues = simple_command("/usr/sbin/rabbitmqctl list_queues name messages consumers auto_delete")
    rabbitmq_report = simple_command("/usr/sbin/rabbitmqctl report")
    rabbitmq_startup_err = simple_file("/var/log/rabbitmq/startup_err")
    rabbitmq_startup_log = simple_file("/var/log/rabbitmq/startup_log")
    rabbitmq_users = simple_command("/usr/sbin/rabbitmqctl list_users")
    rc_local = simple_file("/etc/rc.d/rc.local")
    rdma_conf = simple_file("/etc/rdma/rdma.conf")
    readlink_e_etc_mtab = simple_command("/usr/bin/readlink -e /etc/mtab")
    readlink_e_shift_cert_client = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-client-current.pem")
    readlink_e_shift_cert_server = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-server-current.pem")
    redhat_release = simple_file("/etc/redhat-release")
    resolv_conf = simple_file("/etc/resolv.conf")
    rhosp_release = simple_file("/etc/rhosp-release")

    @datasource(HostContext)
    def rhev_data_center(broker):
        import json
        root = broker[HostContext].root
        relative_path = "rhev/data-center"
        path = os.path.join(root, relative_path)
        bad_apples = []
        for dirpath, dirnames, filenames in os.walk(path):
            for p in dirnames + filenames:
                tmp = os.path.join(dirpath, p)
                try:
                    name, group = get_owner(tmp)
                    good = ("vdsm", "kvm")
                    if (name, group) != good:
                        bad_apples.append({"name": name, "group": group, "path": tmp})
                except:
                    logger.error(tmp)
        if bad_apples:
            return DatasourceProvider(content=json.dumps(bad_apples), relative_path=relative_path)
        raise SkipComponent()

    rhv_log_collector_analyzer = simple_command("rhv-log-collector-analyzer --json")
    rhn_charsets = simple_command("/usr/bin/rhn-charsets")
    rhn_conf = first_file(["/etc/rhn/rhn.conf", "/conf/rhn/rhn/rhn.conf"])
    rhn_entitlement_cert_xml = first_of([glob_file("/etc/sysconfig/rhn/rhn-entitlement-cert.xml*"),
                                   glob_file("/conf/rhn/sysconfig/rhn/rhn-entitlement-cert.xml*")])
    rhn_hibernate_conf = first_file(["/usr/share/rhn/config-defaults/rhn_hibernate.conf", "/config-defaults/rhn_hibernate.conf"])
    rhn_schema_stats = simple_command("/usr/bin/rhn-schema-stats -")
    rhn_schema_version = simple_command("/usr/bin/rhn-schema-version")
    rhn_server_satellite_log = simple_file("var/log/rhn/rhn_server_satellite.log")
    rhn_server_xmlrpc_log = first_file(["/var/log/rhn/rhn_server_xmlrpc.log",
                                           "/rhn-logs/rhn/rhn_server_xmlrpc.log"])
    rhn_search_daemon_log = first_file(["/var/log/rhn/search/rhn_search_daemon.log",
                                           "/rhn-logs/rhn/search/rhn_search_daemon.log"])
    rhn_taskomatic_daemon_log = first_file(["/var/log/rhn/rhn_taskomatic_daemon.log",
                                               "rhn-logs/rhn/rhn_taskomatic_daemon.log"])
    rhsm_conf = simple_file("/etc/rhsm/rhsm.conf")
    rhsm_log = simple_file("/var/log/rhsm/rhsm.log")
    rhsm_releasever = simple_file('/var/lib/rhsm/cache/releasever.json')
    rndc_status = simple_command("/usr/sbin/rndc status")
    root_crontab = simple_command("/usr/bin/crontab -l -u root")
    route = simple_command("/sbin/route -n")
    rpm_V_packages = simple_command("/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo", keep_rc=True)
    rsyslog_conf = simple_file("/etc/rsyslog.conf")
    samba = simple_file("/etc/samba/smb.conf")
    saphostctrl_listinstances = simple_command("/usr/sap/hostctrl/exe/saphostctrl -function ListInstances")

    @datasource(saphostctrl_listinstances, hostname)
    def sap_sid_nr(broker):
        """
        Get the SID and Instance Number

        Typical output of saphostctrl_listinstances::
        # /usr/sap/hostctrl/exe/saphostctrl -function ListInstances
        Inst Info : SR1 - 01 - liuxc-rhel7-hana-ent - 749, patch 418, changelist 1816226

        Returns:
            (list): List of tuple of SID and Instance Number.

        """
        insts = broker[DefaultSpecs.saphostctrl_listinstances].content
        hn = broker[DefaultSpecs.hostname].content[0].split('.')[0].strip()
        results = set()
        for ins in insts:
            ins_splits = ins.split(' - ')
            # Local Instance
            if ins_splits[2].strip() == hn:
                # (sid, nr)
                results.add((ins_splits[0].split()[-1].lower(), ins_splits[1].strip()))
        return list(results)

    @datasource(sap_sid_nr)
    def sap_sid(broker):
        """
        Get the SID

        Returns:
            (list): List of SID.

        """
        return list(set(sn[0] for sn in broker[DefaultSpecs.sap_sid_nr]))

    sap_hdb_version = foreach_execute(sap_sid, "/usr/bin/sudo -iu %sadm HDB version", keep_rc=True)
    sap_host_profile = simple_file("/usr/sap/hostctrl/exe/host_profile")
    sapcontrol_getsystemupdatelist = foreach_execute(sap_sid_nr, "/usr/bin/sudo -iu %sadm sapcontrol -nr %s -function GetSystemUpdateList", keep_rc=True)
    saphostctl_getcimobject_sapinstance = simple_command("/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance")
    saphostexec_status = simple_command("/usr/sap/hostctrl/exe/saphostexec -status")
    saphostexec_version = simple_command("/usr/sap/hostctrl/exe/saphostexec -version")
    sat5_insights_properties = simple_file("/etc/redhat-access/redhat-access-insights.properties")
    satellite_mongodb_storage_engine = simple_command("/usr/bin/mongo pulp_database --eval 'db.serverStatus().storageEngine'")
    satellite_version_rb = simple_file("/usr/share/foreman/lib/satellite/version.rb")
    satellite_custom_hiera = simple_file("/etc/foreman-installer/custom-hiera.yaml")
    block_devices = listdir("/sys/block")
    scheduler = foreach_collect(block_devices, "/sys/block/%s/queue/scheduler")
    sched_rt_runtime_us = simple_file("/proc/sys/kernel/sched_rt_runtime_us")
    scsi = simple_file("/proc/scsi/scsi")
    scsi_eh_deadline = glob_file('/sys/class/scsi_host/host[0-9]*/eh_deadline')
    scsi_fwver = glob_file('/sys/class/scsi_host/host[0-9]*/fwrev')
    sctp_asc = simple_file('/proc/net/sctp/assocs')
    sctp_eps = simple_file('/proc/net/sctp/eps')
    sctp_snmp = simple_file('/proc/net/sctp/snmp')
    sealert = simple_command('/usr/bin/sealert -l "*"')
    secure = simple_file("/var/log/secure")
    selinux_config = simple_file("/etc/selinux/config")
    sestatus = simple_command("/usr/sbin/sestatus -b")
    setup_named_chroot = simple_file("/usr/libexec/setup-named-chroot.sh")

    @datasource(HostContext)
    def block(broker):
        """Path: /sys/block directories starting with . or ram or dm- or loop"""
        remove = (".", "ram", "dm-", "loop")
        tmp = "/dev/%s"
        return[(tmp % f) for f in os.listdir("/sys/block") if not f.startswith(remove)]

    smbstatus_p = simple_command("/usr/bin/smbstatus -p")
    smbstatus_S = simple_command("/usr/bin/smbstatus -S")
    smartctl = foreach_execute(block, "/sbin/smartctl -a %s", keep_rc=True)
    smartpdc_settings = simple_file("/etc/smart_proxy_dynflow_core/settings.yml")
    sockstat = simple_file("/proc/net/sockstat")
    softnet_stat = simple_file("proc/net/softnet_stat")
    software_collections_list = simple_command('/usr/bin/scl --list')
    spfile_ora = glob_file("${ORACLE_HOME}/dbs/spfile*.ora")
    ss = simple_command("/usr/sbin/ss -tupna")
    ssh_config = simple_file("/etc/ssh/ssh_config")
    ssh_foreman_config = simple_file("/usr/share/foreman/.ssh/ssh_config")
    ssh_foreman_proxy_config = simple_file("/usr/share/foreman-proxy/.ssh/ssh_config")
    sshd_config = simple_file("/etc/ssh/sshd_config")
    sshd_config_perms = simple_command("/bin/ls -l /etc/ssh/sshd_config")
    sssd_config = simple_file("/etc/sssd/sssd.conf")
    subscription_manager_id = simple_command("/usr/sbin/subscription-manager identity")  # use "/usr/sbin" here, BZ#1690529
    subscription_manager_installed_product_ids = simple_command("/usr/bin/find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;")
    subscription_manager_release_show = simple_command('/usr/sbin/subscription-manager release --show')  # use "/usr/sbin" here, BZ#1690529
    swift_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/swift.conf", "/etc/swift/swift.conf"])
    swift_log = first_file(["/var/log/containers/swift/swift.log", "/var/log/swift/swift.log"])
    swift_object_expirer_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/object-expirer.conf", "/etc/swift/object-expirer.conf"])
    swift_proxy_server_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/proxy-server.conf", "/etc/swift/proxy-server.conf"])
    sys_kernel_sched_features = simple_file("/sys/kernel/debug/sched_features")
    sysconfig_chronyd = simple_file("/etc/sysconfig/chronyd")
    sysconfig_httpd = simple_file("/etc/sysconfig/httpd")
    sysconfig_irqbalance = simple_file("etc/sysconfig/irqbalance")
    sysconfig_kdump = simple_file("etc/sysconfig/kdump")
    sysconfig_libvirt_guests = simple_file("etc/sysconfig/libvirt-guests")
    sysconfig_memcached = first_file(["/var/lib/config-data/puppet-generated/memcached/etc/sysconfig/memcached", "/etc/sysconfig/memcached"])
    sysconfig_network = simple_file("etc/sysconfig/network")
    sysconfig_ntpd = simple_file("/etc/sysconfig/ntpd")
    sysconfig_prelink = simple_file("/etc/sysconfig/prelink")
    sysconfig_sshd = simple_file("/etc/sysconfig/sshd")
    sysconfig_virt_who = simple_file("/etc/sysconfig/virt-who")
    sysctl = simple_command("/sbin/sysctl -a")
    sysctl_conf = simple_file("/etc/sysctl.conf")
    sysctl_conf_files = listdir("/boot/initramfs-*kdump.img")
    sysctl_conf_initramfs = foreach_execute(sysctl_conf_files, "/bin/lsinitrd /boot/%s -f /etc/sysctl.conf /etc/sysctl.d/*.conf")
    systemctl_cat_rpcbind_socket = simple_command("/bin/systemctl cat rpcbind.socket")
    systemctl_cinder_volume = simple_command("/bin/systemctl show openstack-cinder-volume")
    systemctl_httpd = simple_command("/bin/systemctl show httpd")
    systemctl_nginx = simple_command("/bin/systemctl show nginx")
    systemctl_list_unit_files = simple_command("/bin/systemctl list-unit-files")
    systemctl_list_units = simple_command("/bin/systemctl list-units")
    systemctl_mariadb = simple_command("/bin/systemctl show mariadb")
    systemctl_pulp_workers = simple_command("/bin/systemctl show pulp_workers")
    systemctl_pulp_resmg = simple_command("/bin/systemctl show pulp_resource_manager")
    systemctl_pulp_celerybeat = simple_command("/bin/systemctl show pulp_celerybeat")
    systemctl_qpidd = simple_command("/bin/systemctl show qpidd")
    systemctl_qdrouterd = simple_command("/bin/systemctl show qdrouterd")
    systemctl_show_all_services = simple_command("/bin/systemctl show *.service")
    systemctl_show_target = simple_command("/bin/systemctl show *.target")
    systemctl_smartpdc = simple_command("/bin/systemctl show smart_proxy_dynflow_core")
    systemd_analyze_blame = simple_command("/bin/systemd-analyze blame")
    systemd_docker = simple_command("/usr/bin/systemctl cat docker.service")
    systemd_logind_conf = simple_file("/etc/systemd/logind.conf")
    systemd_openshift_node = simple_command("/usr/bin/systemctl cat atomic-openshift-node.service")
    systemd_system_conf = simple_file("/etc/systemd/system.conf")
    systemd_system_origin_accounting = simple_file("/etc/systemd/system.conf.d/origin-accounting.conf")
    systemid = first_of([
        simple_file("/etc/sysconfig/rhn/systemid"),
        simple_file("/conf/rhn/sysconfig/rhn/systemid")
    ])
    systool_b_scsi_v = simple_command("/bin/systool -b scsi -v")
    tags = simple_file("/tags.json", kind=RawFileProvider)
    teamdctl_config_dump = foreach_execute(ethernet_interfaces, "/usr/bin/teamdctl %s config dump")
    teamdctl_state_dump = foreach_execute(ethernet_interfaces, "/usr/bin/teamdctl %s state dump")
    thp_use_zero_page = simple_file("/sys/kernel/mm/transparent_hugepage/use_zero_page")
    thp_enabled = simple_file("/sys/kernel/mm/transparent_hugepage/enabled")
    tmpfilesd = glob_file(["/etc/tmpfiles.d/*.conf", "/usr/lib/tmpfiles.d/*.conf", "/run/tmpfiles.d/*.conf"])
    tomcat_web_xml = first_of([glob_file("/etc/tomcat*/web.xml"),
                                  glob_file("/conf/tomcat/tomcat*/web.xml")])
    tomcat_server_xml = first_of([foreach_collect(tomcat_base, "%s/conf/server.xml"),
                                     glob_file("conf/tomcat/tomcat*/server.xml", context=HostArchiveContext)])

    @datasource(ps_auxww)
    def tomcat_home_base(broker):
        """Command: tomcat_home_base_paths"""
        ps = broker[DefaultSpecs.ps_auxww].content
        results = []
        findall = re.compile(r"\-Dcatalina\.(home|base)=(\S+)").findall
        for p in ps:
            found = findall(p)
            if found:
                # Only get the path which is absolute
                results.extend(f[1] for f in found if f[1][0] == '/')
        return list(set(results))

    tomcat_vdc_targeted = foreach_execute(tomcat_home_base, "/bin/grep -R -s 'VirtualDirContext' --include '*.xml' %s")
    tomcat_vdc_fallback = simple_command("/usr/bin/find /usr/share -maxdepth 1 -name 'tomcat*' -exec /bin/grep -R -s 'VirtualDirContext' --include '*.xml' '{}' +")
    tuned_adm = simple_command("/usr/sbin/tuned-adm list")
    tuned_conf = simple_file("/etc/tuned.conf")
    udev_persistent_net_rules = simple_file("/etc/udev/rules.d/70-persistent-net.rules")
    udev_fc_wwpn_id_rules = simple_file("/usr/lib/udev/rules.d/59-fc-wwpn-id.rules")
    uname = simple_command("/usr/bin/uname -a")
    up2date = simple_file("/etc/sysconfig/rhn/up2date")
    up2date_log = simple_file("/var/log/up2date")
    uploader_log = simple_file("/var/log/redhat-access-insights/redhat-access-insights.log")
    uptime = simple_command("/usr/bin/uptime")
    usr_journald_conf_d = glob_file(r"usr/lib/systemd/journald.conf.d/*.conf")  # note that etc_journald.conf.d also exists
    vdo_status = simple_command("/usr/bin/vdo status")
    vgdisplay = simple_command("/sbin/vgdisplay")
    vdsm_conf = simple_file("etc/vdsm/vdsm.conf")
    vdsm_id = simple_file("etc/vdsm/vdsm.id")
    vdsm_log = simple_file("var/log/vdsm/vdsm.log")
    vdsm_logger_conf = simple_file("etc/vdsm/logger.conf")
    vma_ra_enabled = simple_file("/sys/kernel/mm/swap/vma_ra_enabled")
    vmware_tools_conf = simple_file("etc/vmware-tools/tools.conf")
    vgs = None  # simple_command('/sbin/vgs -v -o +vg_mda_count,vg_mda_free,vg_mda_size,vg_mda_used_count,vg_tags --config="global{locking_type=0}"')
    vgs_noheadings = simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config=\"global{locking_type=0}\"")
    vgs_noheadings_all = simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config='global{locking_type=0} devices{filter=[\"a|.*|\"]}'")
    virsh_list_all = simple_command("/usr/bin/virsh --readonly list --all")
    virt_what = simple_command("/usr/sbin/virt-what")
    virt_who_conf = glob_file([r"etc/virt-who.conf", r"etc/virt-who.d/*.conf"])
    virtlogd_conf = simple_file("/etc/libvirt/virtlogd.conf")
    vmcore_dmesg = glob_file("/var/crash/*/vmcore-dmesg.txt")
    vsftpd = simple_file("/etc/pam.d/vsftpd")
    vsftpd_conf = simple_file("/etc/vsftpd/vsftpd.conf")
    woopsie = simple_command(r"/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report' -print -quit")
    x86_pti_enabled = simple_file("sys/kernel/debug/x86/pti_enabled")
    x86_ibpb_enabled = simple_file("sys/kernel/debug/x86/ibpb_enabled")
    x86_ibrs_enabled = simple_file("sys/kernel/debug/x86/ibrs_enabled")
    x86_retp_enabled = simple_file("sys/kernel/debug/x86/retp_enabled")

    @datasource(Mount)
    def xfs_mounts(broker):
        mnt = broker[Mount]
        mps = mnt.search(mount_type='xfs')
        return [m.mount_point for m in mps]

    xfs_info = foreach_execute(xfs_mounts, "/usr/sbin/xfs_info %s")
    xinetd_conf = glob_file(["/etc/xinetd.conf", "/etc/xinetd.d/*"])
    yum_conf = simple_file("/etc/yum.conf")
    yum_list_available = simple_command("yum -C --noplugins list available")
    yum_list_installed = simple_command("yum -C --noplugins list installed")
    yum_log = simple_file("/var/log/yum.log")
    yum_repolist = simple_command("/usr/bin/yum -C --noplugins repolist")
    yum_repos_d = glob_file("/etc/yum.repos.d/*")
    zdump_v = simple_command("/usr/sbin/zdump -v /etc/localtime -c 2019,2039")
    zipl_conf = simple_file("/etc/zipl.conf")

    rpm_format = format_rpm()

    host_installed_rpms = simple_command("/bin/rpm -qa --qf '%s'" % rpm_format, context=HostContext)

    @datasource(DockerImageContext)
    def docker_installed_rpms(broker):
        """ Command: /bin/rpm -qa --root `%s` --qf `%s`"""
        ctx = broker[DockerImageContext]
        root = ctx.root
        fmt = DefaultSpecs.rpm_format
        cmd = "/bin/rpm -qa --root %s --qf '%s'" % (root, fmt)
        result = ctx.shell_out(cmd)
        return CommandOutputProvider(cmd, ctx, content=result)

    # unify the different installed rpm provider types
    installed_rpms = first_of([host_installed_rpms, docker_installed_rpms])

    @datasource(ps_auxww, context=HostContext)
    def jboss_home(broker):
        """Command: JBoss home progress command content paths"""
        ps = broker[DefaultSpecs.ps_auxww].content
        results = []
        findall = re.compile(r"\-Djboss\.home\.dir=(\S+)").findall
        # JBoss progress command content should contain jboss.home.dir
        # and any of string ['-D[Standalone]', '-D[Host Controller]', '-D[Server:']
        for p in ps:
            if any(i in p for i in ['-D[Standalone]', '-D[Host Controller]', '-D[Server:']):
                found = findall(p)
                if found:
                    # Only get the path which is absolute
                    results.extend(f for f in found if f[0] == '/')
        return list(set(results))

    jboss_version = foreach_collect(jboss_home, "%s/version.txt")

    @datasource(ps_auxww, context=HostContext, multi_output=True)
    def jboss_domain_server_log_dir(broker):
        """Command: JBoss domain server log directory"""
        ps = broker[DefaultSpecs.ps_auxww].content
        results = []
        findall = re.compile(r"\-Djboss\.server\.log\.dir=(\S+)").findall
        # JBoss domain server progress command content should contain jboss.server.log.dir
        for p in ps:
            if '-D[Server:' in p:
                found = findall(p)
                if found:
                    # Only get the path which is absolute
                    results.extend(f for f in found if f[0] == '/')
        return list(set(results))

    jboss_domain_server_log = foreach_collect(jboss_domain_server_log_dir, "%s/server.log*")

    @datasource(ps_auxww, context=HostContext, multi_output=True)
    def jboss_standalone_main_config_files(broker):
        """Command: JBoss standalone main config files"""
        ps = broker[DefaultSpecs.ps_auxww].content
        results = []
        search = re.compile(r"\-Djboss\.server\.base\.dir=(\S+)").search
        # JBoss progress command content should contain jboss.home.dir
        for p in ps:
            if '-D[Standalone]' in p:
                match = search(p)
                # Only get the path which is absolute
                if match and match.group(1)[0] == "/":
                    main_config_path = match.group(1)
                    main_config_file = "standalone.xml"
                    if " -c " in p:
                        main_config_file = p.split(" -c ")[1].split()[0]
                    elif "--server-config" in p:
                        main_config_file = p.split("--server-config=")[1].split()[0]
                    results.append(main_config_path + "/" + main_config_file)
        return list(set(results))

    jboss_standalone_main_config = foreach_collect(jboss_standalone_main_config_files, "%s")
