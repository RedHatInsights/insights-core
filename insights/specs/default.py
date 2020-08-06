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

from insights.core.context import HostContext

from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import RawFileProvider
from insights.core.spec_factory import simple_file, simple_command, glob_file
from insights.core.spec_factory import first_of, foreach_collect, foreach_execute
from insights.core.spec_factory import first_file, listdir
from insights.combiners.cloud_provider import CloudProvider
from insights.combiners.services import Services
from insights.combiners.sap import Sap
from insights.specs import Specs


from grp import getgrgid
from os import stat
from pwd import getpwuid


logger = logging.getLogger(__name__)


def get_owner(filename):
    """ tuple: Return tuple containing uid and gid of file filename """
    st = stat(filename)
    name = getpwuid(st.st_uid).pw_name
    group = getgrgid(st.st_gid).gr_name
    return (name, group)


def get_cmd_and_package_in_ps(broker, target_command):
    """
    Search for command in ``ps auxww`` output and determine RPM providing binary

    Arguments:
        broker(dict): Current state of specs collected by Insights
        target_command(str): Command name to search for in ps output

    Returns:
        set: Set including all RPMs that provide the target command
    """
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
    """ function: Returns function that will format output of rpm query command """
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
    avc_hash_stats = simple_file("/sys/fs/selinux/avc/hash_stats")
    avc_cache_threshold = simple_file("/sys/fs/selinux/avc/cache_threshold")

    @datasource(CloudProvider)
    def is_aws(broker):
        """ bool: Returns True if this node is identified as running in AWS """
        cp = broker[CloudProvider]
        if cp and cp.cloud_provider == CloudProvider.AWS:
            return True
        raise SkipComponent()

    aws_instance_id_doc = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/document --connect-timeout 5", deps=[is_aws])
    aws_instance_id_pkcs7 = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/pkcs7 --connect-timeout 5", deps=[is_aws])

    @datasource(CloudProvider)
    def is_azure(broker):
        """ bool: Returns True if this node is identified as running in Azure """
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
    cgroups = simple_file("/proc/cgroups")
    ps_alxwww = simple_command("/bin/ps alxwww")
    ps_aux = simple_command("/bin/ps aux")
    ps_auxcww = simple_command("/bin/ps auxcww")
    ps_auxww = simple_command("/bin/ps auxww")
    ps_ef = simple_command("/bin/ps -ef")
    ps_eo = simple_command("/usr/bin/ps -eo pid,ppid,comm")

    @datasource(ps_auxww)
    def tomcat_base(broker):
        """
        Function to search the output of ``ps auxww`` to find all running tomcat
        processes and extract the base path where the process was started.

        Returns:
            list: List of the paths to each running process
        """
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
    cciss = glob_file("/proc/driver/cciss/cciss*")
    cdc_wdm = simple_file("/sys/bus/usb/drivers/cdc_wdm/module/refcnt")
    ceilometer_collector_log = first_file(["/var/log/containers/ceilometer/collector.log", "/var/log/ceilometer/collector.log"])
    ceilometer_compute_log = first_file(["/var/log/containers/ceilometer/compute.log", "/var/log/ceilometer/compute.log"])
    ceilometer_conf = first_file(["/var/lib/config-data/puppet-generated/ceilometer/etc/ceilometer/ceilometer.conf", "/etc/ceilometer/ceilometer.conf"])
    ceph_conf = first_file(["/var/lib/config-data/puppet-generated/ceph/etc/ceph/ceph.conf", "/etc/ceph/ceph.conf"])
    ceph_df_detail = simple_command("/usr/bin/ceph df detail -f json")
    ceph_health_detail = simple_command("/usr/bin/ceph health detail -f json")

    @datasource(ps_auxww)
    def is_ceph_monitor(broker):
        """ bool: Returns True if ceph monitor process ceph-mon is running on this node """
        ps = broker[DefaultSpecs.ps_auxww].content
        findall = re.compile(r"ceph\-mon").findall
        if any(findall(p) for p in ps):
            return True
        raise SkipComponent()

    ceph_insights = simple_command("/usr/bin/ceph insights", deps=[is_ceph_monitor])
    ceph_log = glob_file(r"var/log/ceph/ceph.log*")
    ceph_osd_dump = simple_command("/usr/bin/ceph osd dump -f json")
    ceph_osd_ec_profile_ls = simple_command("/usr/bin/ceph osd erasure-code-profile ls")
    ceph_osd_log = glob_file(r"var/log/ceph/ceph-osd*.log")
    ceph_osd_tree = simple_command("/usr/bin/ceph osd tree -f json")
    ceph_s = simple_command("/usr/bin/ceph -s -f json")
    ceph_v = simple_command("/usr/bin/ceph -v")
    certificates_enddate = simple_command("/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \; -exec echo 'FileName= {}' \;")
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
    cobbler_settings = first_file(["/etc/cobbler/settings", "/conf/cobbler/settings"])
    cobbler_modules_conf = first_file(["/etc/cobbler/modules.conf", "/conf/cobbler/modules.conf"])
    corosync = simple_file("/etc/sysconfig/corosync")
    corosync_conf = simple_file("/etc/corosync/corosync.conf")
    cpu_cores = glob_file("sys/devices/system/cpu/cpu[0-9]*/online")
    cpu_siblings = glob_file("sys/devices/system/cpu/cpu[0-9]*/topology/thread_siblings_list")
    cpu_smt_active = simple_file("sys/devices/system/cpu/smt/active")
    cpu_vulns = glob_file("sys/devices/system/cpu/vulnerabilities/*")
    cpuinfo = simple_file("/proc/cpuinfo")
    cpupower_frequency_info = simple_command("/usr/bin/cpupower -c all frequency-info")
    cpuset_cpus = simple_file("/sys/fs/cgroup/cpuset/cpuset.cpus")
    cron_daily_rhsmd = simple_file("/etc/cron.daily/rhsmd")
    crypto_policies_config = simple_file("/etc/crypto-policies/config")
    crypto_policies_state_current = simple_file("/etc/crypto-policies/state/current")
    crypto_policies_opensshserver = simple_file("/etc/crypto-policies/back-ends/opensshserver.config")
    crypto_policies_bind = simple_file("/etc/crypto-policies/back-ends/bind.config")
    current_clocksource = simple_file("/sys/devices/system/clocksource/clocksource0/current_clocksource")
    date = simple_command("/bin/date")
    date_utc = simple_command("/bin/date --utc")
    designate_conf = first_file(["/var/lib/config-data/puppet-generated/designate/etc/designate/designate.conf",
                                 "/etc/designate/designate.conf"])
    df__al = simple_command("/bin/df -al")
    df__alP = simple_command("/bin/df -alP")
    df__li = simple_command("/bin/df -li")
    dig_dnssec = simple_command("/usr/bin/dig +dnssec . SOA")
    dig_edns = simple_command("/usr/bin/dig +edns=0 . SOA")
    dig_noedns = simple_command("/usr/bin/dig +noedns . SOA")
    dirsrv_errors = glob_file("var/log/dirsrv/*/errors*")
    dmesg = simple_command("/bin/dmesg")
    dmesg_log = simple_file("/var/log/dmesg")
    dmidecode = simple_command("/usr/sbin/dmidecode")
    dnf_conf = simple_file("/etc/dnf/dnf.conf")
    docker_info = simple_command("/usr/bin/docker info")
    docker_list_containers = simple_command("/usr/bin/docker ps --all --no-trunc")
    docker_list_images = simple_command("/usr/bin/docker images --all --no-trunc --digests")
    docker_storage_setup = simple_file("/etc/sysconfig/docker-storage-setup")
    docker_sysconfig = simple_file("/etc/sysconfig/docker")
    dracut_kdump_capture_service = simple_file("/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service")
    engine_db_query_vdsm_version = simple_command('engine-db-query --statement "SELECT vs.vds_name, rpm_version FROM vds_dynamic vd, vds_static vs WHERE vd.vds_id = vs.vds_id;" --json')
    engine_log = simple_file("/var/log/ovirt-engine/engine.log")
    etc_journald_conf = simple_file(r"etc/systemd/journald.conf")
    etc_journald_conf_d = glob_file(r"etc/systemd/journald.conf.d/*.conf")
    etc_machine_id = simple_file("/etc/machine-id")
    etcd_conf = simple_file("/etc/etcd/etcd.conf")
    ethernet_interfaces = listdir("/sys/class/net", context=HostContext)
    ethtool = foreach_execute(ethernet_interfaces, "/sbin/ethtool %s")
    ethtool_S = foreach_execute(ethernet_interfaces, "/sbin/ethtool -S %s")
    ethtool_T = foreach_execute(ethernet_interfaces, "/sbin/ethtool -T %s")
    ethtool_c = foreach_execute(ethernet_interfaces, "/sbin/ethtool -c %s")
    ethtool_g = foreach_execute(ethernet_interfaces, "/sbin/ethtool -g %s")
    ethtool_i = foreach_execute(ethernet_interfaces, "/sbin/ethtool -i %s")
    ethtool_k = foreach_execute(ethernet_interfaces, "/sbin/ethtool -k %s")
    facter = simple_command("/usr/bin/facter")
    fc_match = simple_command("/bin/fc-match -sv 'sans:regular:roman' family fontformat")
    fcoeadm_i = simple_command("/usr/sbin/fcoeadm -i")
    findmnt_lo_propagation = simple_command("/bin/findmnt -lo+PROPAGATION")
    firewall_cmd_list_all_zones = simple_command("/usr/bin/firewall-cmd --list-all-zones")
    firewalld_conf = simple_file("/etc/firewalld/firewalld.conf")
    fstab = simple_file("/etc/fstab")
    galera_cnf = first_file(["/var/lib/config-data/puppet-generated/mysql/etc/my.cnf.d/galera.cnf", "/etc/my.cnf.d/galera.cnf"])
    getconf_page_size = simple_command("/usr/bin/getconf PAGE_SIZE")
    getenforce = simple_command("/usr/sbin/getenforce")
    getsebool = simple_command("/usr/sbin/getsebool -a")
    gluster_v_info = simple_command("/usr/sbin/gluster volume info")
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
    hammer_task_list = simple_command("/usr/bin/hammer --config /root/.hammer/cli.modules.d/foreman.yml --output csv task list --search 'state=running AND ( label=Actions::Candlepin::ListenOnCandlepinEvents OR label=Actions::Katello::EventQueue::Monitor )'")
    haproxy_cfg = first_file(["/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.cfg"])
    heat_api_log = first_file(["/var/log/containers/heat/heat_api.log", "/var/log/heat/heat-api.log", "/var/log/heat/heat_api.log"])
    heat_conf = first_file(["/var/lib/config-data/puppet-generated/heat/etc/heat/heat.conf", "/etc/heat/heat.conf"])
    hostname = simple_command("/bin/hostname -f")
    hostname_default = simple_command("/bin/hostname")
    hostname_short = simple_command("/bin/hostname -s")
    hosts = simple_file("/etc/hosts")
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
    virt_uuid_facts = simple_file("/etc/rhsm/facts/virt_uuid.facts")

    @datasource(ps_auxww)
    def httpd_cmd(broker):
        """
        Function to search the output of ``ps auxww`` to find all running Apache
        webserver processes and extract the binary path.

        Returns:
            list: List of the binary paths to each running process
        """
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

    httpd_M = foreach_execute(httpd_cmd, "%s -M")
    httpd_V = foreach_execute(httpd_cmd, "%s -V")
    ifcfg = glob_file("/etc/sysconfig/network-scripts/ifcfg-*")
    ifcfg_static_route = glob_file("/etc/sysconfig/network-scripts/route-*")
    imagemagick_policy = glob_file(["/etc/ImageMagick/policy.xml", "/usr/lib*/ImageMagick-6.5.4/config/policy.xml"])
    initctl_lst = simple_command("/sbin/initctl --system list")
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
    iptables = simple_command("/sbin/iptables-save")
    iptables_permanent = simple_file("etc/sysconfig/iptables")
    ip6tables = simple_command("/sbin/ip6tables-save")
    ipv4_neigh = simple_command("/sbin/ip -4 neighbor show nud all")
    ipv6_neigh = simple_command("/sbin/ip -6 neighbor show nud all")
    ironic_inspector_log = simple_file("/var/log/ironic-inspector/ironic-inspector.log")
    iscsiadm_m_session = simple_command("/usr/sbin/iscsiadm -m session")
    kdump_conf = simple_file("/etc/kdump.conf")
    kernel_config = glob_file("/boot/config-*")
    kexec_crash_size = simple_file("/sys/kernel/kexec_crash_size")
    keystone_crontab = simple_command("/usr/bin/crontab -l -u keystone")
    kpatch_list = simple_command("/usr/sbin/kpatch list")
    krb5 = glob_file([r"etc/krb5.conf", r"etc/krb5.conf.d/*"])
    ksmstate = simple_file("/sys/kernel/mm/ksm/run")
    kubepods_cpu_quota = glob_file("/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod[a-f0-9_]*.slice/cpu.cfs_quota_us")
    last_upload_globs = ["/etc/redhat-access-insights/.lastupload", "/etc/insights-client/.lastupload"]
    lastupload = glob_file(last_upload_globs)
    libkeyutils = simple_command("/usr/bin/find -L /lib /lib64 -name 'libkeyutils.so*'")
    libkeyutils_objdumps = simple_command('/usr/bin/find -L /lib /lib64 -name libkeyutils.so.1 -exec objdump -x "{}" \;')
    libvirtd_log = simple_file("/var/log/libvirt/libvirtd.log")
    limits_conf = glob_file(["/etc/security/limits.conf", "/etc/security/limits.d/*.conf"])
    localtime = simple_command("/usr/bin/file -L /etc/localtime")
    logrotate_conf = glob_file(["/etc/logrotate.conf", "/etc/logrotate.d/*"])
    lpstat_p = simple_command("/usr/bin/lpstat -p")
    ls_boot = simple_command("/bin/ls -lanR /boot")
    ls_dev = simple_command("/bin/ls -lanR /dev")
    ls_disk = simple_command("/bin/ls -lanR /dev/disk")
    etc_and_sub_dirs = sorted(["/etc", "/etc/pki/tls/private", "/etc/pki/tls/certs",
        "/etc/pki/ovirt-vmconsole", "/etc/nova/migration", "/etc/sysconfig",
        "/etc/cloud/cloud.cfg.d", "/etc/rc.d/init.d"])
    ls_etc = simple_command("/bin/ls -lan {0}".format(' '.join(etc_and_sub_dirs)))
    ls_lib_firmware = simple_command("/bin/ls -lanR /lib/firmware")
    ls_ocp_cni_openshift_sdn = simple_command("/bin/ls -l /var/lib/cni/networks/openshift-sdn")
    ls_origin_local_volumes_pods = simple_command("/bin/ls -l /var/lib/origin/openshift.local.volumes/pods")
    ls_osroot = simple_command("/bin/ls -lan /")
    ls_run_systemd_generator = simple_command("/bin/ls -lan /run/systemd/generator")
    ls_R_var_lib_nova_instances = simple_command("/bin/ls -laR /var/lib/nova/instances")
    ls_sys_firmware = simple_command("/bin/ls -lanR /sys/firmware")
    ls_tmp = simple_command("/bin/ls -la /tmp")
    ls_usr_lib64 = simple_command("/bin/ls -lan /usr/lib64")
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
    lsmod = simple_command("/sbin/lsmod")
    lsof = simple_command("/usr/sbin/lsof")
    lspci = simple_command("/sbin/lspci -k")
    lssap = simple_command("/usr/sap/hostctrl/exe/lssap")
    lsscsi = simple_command("/usr/bin/lsscsi")
    lsvmbus = simple_command("/usr/sbin/lsvmbus -vv")
    lvm_conf = simple_file("/etc/lvm/lvm.conf")
    lvs_noheadings = simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor --config=\"global{locking_type=0}\"")
    mac_addresses = glob_file("/sys/class/net/*/address")
    machine_id = first_file(["etc/insights-client/machine-id", "etc/redhat-access-insights/machine-id", "etc/redhat_access_proactive/machine-id"])
    mariadb_log = simple_file("/var/log/mariadb/mariadb.log")
    max_uid = simple_command("/bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd")
    md5chk_files = foreach_execute(
        ["/etc/pki/product/69.pem", "/etc/pki/product-default/69.pem", "/usr/lib/libsoftokn3.so", "/usr/lib64/libsoftokn3.so", "/usr/lib/libfreeblpriv3.so", "/usr/lib64/libfreeblpriv3.so"],
        "/usr/bin/md5sum %s")
    mdstat = simple_file("/proc/mdstat")
    meminfo = first_file(["/proc/meminfo", "/meminfo"])
    messages = simple_file("/var/log/messages")
    modinfo_i40e = simple_command("/sbin/modinfo i40e")
    modinfo_igb = simple_command("/sbin/modinfo igb")
    modinfo_ixgbe = simple_command("/sbin/modinfo ixgbe")
    modinfo_veth = simple_command("/sbin/modinfo veth")
    modinfo_vmxnet3 = simple_command("/sbin/modinfo vmxnet3")
    modprobe = glob_file(["/etc/modprobe.conf", "/etc/modprobe.d/*.conf"])
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
    mysqladmin_vars = simple_command("/bin/mysqladmin variables")
    mysql_log = glob_file([
                          "/var/log/mysql/mysqld.log",
                          "/var/log/mysql.log",
                          "/var/opt/rh/rh-mysql*/log/mysql/mysqld.log"
                          ])
    named_checkconf_p = simple_command("/usr/sbin/named-checkconf -p")
    named_conf = simple_file("/etc/named.conf")
    namespace = simple_command("/bin/ls /var/run/netns")
    ndctl_list_Ni = simple_command("/usr/bin/ndctl list -Ni")
    netconsole = simple_file("/etc/sysconfig/netconsole")
    netstat = simple_command("/bin/netstat -neopa")
    netstat_agn = simple_command("/bin/netstat -agn")
    netstat_i = simple_command("/bin/netstat -i")
    netstat_s = simple_command("/bin/netstat -s")
    networkmanager_dispatcher_d = glob_file("/etc/NetworkManager/dispatcher.d/*-dhclient")
    neutron_conf = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf", "/etc/neutron/neutron.conf"])
    neutron_sriov_agent = first_file([
        "/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/sriov_agent.ini",
        "/etc/neutron/plugins/ml2/sriov_agent.ini"])
    neutron_dhcp_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/dhcp_agent.ini", "/etc/neutron/dhcp_agent.ini"])
    neutron_l3_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini", "/etc/neutron/l3_agent.ini"])
    neutron_l3_agent_log = simple_file("/var/log/neutron/l3-agent.log")
    neutron_metadata_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/metadata_agent.ini", "/etc/neutron/metadata_agent.ini"])
    neutron_metadata_agent_log = first_file(["/var/log/containers/neutron/metadata-agent.log", "/var/log/neutron/metadata-agent.log"])
    neutron_ovs_agent_log = first_file(["/var/log/containers/neutron/openvswitch-agent.log", "/var/log/neutron/openvswitch-agent.log"])
    neutron_plugin_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugin.ini", "/etc/neutron/plugin.ini"])
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
    nova_uid = simple_command("/usr/bin/id -u nova")
    nscd_conf = simple_file("/etc/nscd.conf")
    nsswitch_conf = simple_file("/etc/nsswitch.conf")
    ntp_conf = simple_file("/etc/ntp.conf")
    ntpq_leap = simple_command("/usr/sbin/ntpq -c 'rv 0 leap'")
    ntptime = simple_command("/usr/sbin/ntptime")
    numa_cpus = glob_file("/sys/devices/system/node/node[0-9]*/cpulist")
    numeric_user_group_name = simple_command("/bin/grep -c '^[[:digit:]]' /etc/passwd /etc/group")
    nvme_core_io_timeout = simple_file("/sys/module/nvme_core/parameters/io_timeout")
    oc_get_clusterrole_with_config = simple_command("/usr/bin/oc get clusterrole --config /etc/origin/master/admin.kubeconfig")
    oc_get_clusterrolebinding_with_config = simple_command("/usr/bin/oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig")
    odbc_ini = simple_file("/etc/odbc.ini")
    odbcinst_ini = simple_file("/etc/odbcinst.ini")
    openshift_hosts = simple_file("/root/.config/openshift/hosts")
    openshift_router_pid = simple_command("/usr/bin/pgrep -n openshift-route")
    openshift_router_environ = foreach_collect(openshift_router_pid, "/proc/%s/environ")
    openvswitch_other_config = simple_command("/usr/bin/ovs-vsctl -t 5 get Open_vSwitch . other_config")
    os_release = simple_file("etc/os-release")
    ose_master_config = simple_file("/etc/origin/master/master-config.yaml")
    ose_node_config = simple_file("/etc/origin/node/node-config.yaml")
    ovirt_engine_server_log = simple_file("/var/log/ovirt-engine/server.log")
    ovirt_engine_ui_log = simple_file("/var/log/ovirt-engine/ui.log")
    ovs_vsctl_list_bridge = simple_command("/usr/bin/ovs-vsctl list bridge")
    ovs_vsctl_show = simple_command("/usr/bin/ovs-vsctl show")
    pacemaker_log = first_file(["/var/log/pacemaker.log", "/var/log/pacemaker/pacemaker.log"])
    pci_rport_target_disk_paths = simple_command("/usr/bin/find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f")

    @datasource(Services, context=HostContext)
    def pcp_enabled(broker):
        """ bool: Returns True if pmproxy service is on in services """
        if not broker[Services].is_on("pmproxy"):
            raise SkipComponent("pmproxy not enabled")

    pcp_metrics = simple_command("/usr/bin/curl -s http://127.0.0.1:44322/metrics --connect-timeout 5", deps=[pcp_enabled])
    passenger_status = simple_command("/usr/bin/passenger-status")
    password_auth = simple_file("/etc/pam.d/password-auth")
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
    proc_netstat = simple_file("proc/net/netstat")
    proc_slabinfo = simple_file("proc/slabinfo")
    proc_snmp_ipv4 = simple_file("proc/net/snmp")
    proc_snmp_ipv6 = simple_file("proc/net/snmp6")
    proc_stat = simple_file("proc/stat")
    pulp_worker_defaults = simple_file("etc/default/pulp_workers")
    pvs_noheadings = simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config=\"global{locking_type=0}\"")
    qemu_conf = simple_file("/etc/libvirt/qemu.conf")
    qemu_xml = glob_file(r"/etc/libvirt/qemu/*.xml")
    qpid_stat_g = simple_command("/usr/bin/qpid-stat -g --ssl-certificate=/etc/pki/katello/qpid_client_striped.crt -b amqps://localhost:5671")
    qpidd_conf = simple_file("/etc/qpid/qpidd.conf")
    rabbitmq_env = simple_file("/etc/rabbitmq/rabbitmq-env.conf")
    rabbitmq_report = simple_command("/usr/sbin/rabbitmqctl report")
    rabbitmq_startup_log = simple_file("/var/log/rabbitmq/startup_log")
    rabbitmq_users = simple_command("/usr/sbin/rabbitmqctl list_users")
    rc_local = simple_file("/etc/rc.d/rc.local")
    rdma_conf = simple_file("/etc/rdma/rdma.conf")
    readlink_e_etc_mtab = simple_command("/usr/bin/readlink -e /etc/mtab")
    readlink_e_shift_cert_client = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-client-current.pem")
    readlink_e_shift_cert_server = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-server-current.pem")
    redhat_release = simple_file("/etc/redhat-release")
    resolv_conf = simple_file("/etc/resolv.conf")
    rhn_conf = first_file(["/etc/rhn/rhn.conf", "/conf/rhn/rhn/rhn.conf"])
    rhn_entitlement_cert_xml = first_of([glob_file("/etc/sysconfig/rhn/rhn-entitlement-cert.xml*"),
                                   glob_file("/conf/rhn/sysconfig/rhn/rhn-entitlement-cert.xml*")])
    rhn_schema_version = simple_command("/usr/bin/rhn-schema-version")
    rhn_taskomatic_daemon_log = first_file(["/var/log/rhn/rhn_taskomatic_daemon.log",
                                               "rhn-logs/rhn/rhn_taskomatic_daemon.log"])
    rhsm_conf = simple_file("/etc/rhsm/rhsm.conf")
    rhsm_log = simple_file("/var/log/rhsm/rhsm.log")
    rhsm_releasever = simple_file('/var/lib/rhsm/cache/releasever.json')
    rndc_status = simple_command("/usr/sbin/rndc status")
    rpm_V_packages = simple_command("/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo chrony", keep_rc=True)
    rsyslog_conf = simple_file("/etc/rsyslog.conf")
    samba = simple_file("/etc/samba/smb.conf")

    @datasource(Sap)
    def sap_sid_name(broker):
        """(list): Returns the list of (SAP SID, SAP InstanceName) """
        sap = broker[Sap]
        return [(sap.sid(i), i) for i in sap.local_instances]

    sap_dev_disp = foreach_collect(sap_sid_name, "/usr/sap/%s/%s/work/dev_disp")
    sap_dev_rd = foreach_collect(sap_sid_name, "/usr/sap/%s/%s/work/dev_rd")
    saphostctl_getcimobject_sapinstance = simple_command("/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance")
    sat5_insights_properties = simple_file("/etc/redhat-access/redhat-access-insights.properties")
    satellite_mongodb_storage_engine = simple_command("/usr/bin/mongo pulp_database --eval 'db.serverStatus().storageEngine'")
    satellite_version_rb = simple_file("/usr/share/foreman/lib/satellite/version.rb")
    satellite_custom_hiera = simple_file("/etc/foreman-installer/custom-hiera.yaml")
    scsi = simple_file("/proc/scsi/scsi")
    scsi_eh_deadline = glob_file('/sys/class/scsi_host/host[0-9]*/eh_deadline')
    scsi_fwver = glob_file('/sys/class/scsi_host/host[0-9]*/fwrev')
    sctp_asc = simple_file('/proc/net/sctp/assocs')
    sctp_eps = simple_file('/proc/net/sctp/eps')
    sctp_snmp = simple_file('/proc/net/sctp/snmp')
    sealert = simple_command('/usr/bin/sealert -l "*"')
    selinux_config = simple_file("/etc/selinux/config")
    sestatus = simple_command("/usr/sbin/sestatus -b")
    setup_named_chroot = simple_file("/usr/libexec/setup-named-chroot.sh")
    smbstatus_p = simple_command("/usr/bin/smbstatus -p")
    smartpdc_settings = simple_file("/etc/smart_proxy_dynflow_core/settings.yml")
    sockstat = simple_file("/proc/net/sockstat")
    softnet_stat = simple_file("proc/net/softnet_stat")
    software_collections_list = simple_command('/usr/bin/scl --list')
    ss = simple_command("/usr/sbin/ss -tupna")
    ssh_config = simple_file("/etc/ssh/ssh_config")
    ssh_config_d = glob_file(r"/etc/ssh/ssh_config.d/*.conf")
    ssh_foreman_proxy_config = simple_file("/usr/share/foreman-proxy/.ssh/ssh_config")
    sshd_config = simple_file("/etc/ssh/sshd_config")
    sshd_config_perms = simple_command("/bin/ls -l /etc/ssh/sshd_config")
    sssd_config = simple_file("/etc/sssd/sssd.conf")
    subscription_manager_id = simple_command("/usr/sbin/subscription-manager identity")  # use "/usr/sbin" here, BZ#1690529
    swift_object_expirer_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/object-expirer.conf", "/etc/swift/object-expirer.conf"])
    swift_proxy_server_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/proxy-server.conf", "/etc/swift/proxy-server.conf"])
    sysconfig_kdump = simple_file("etc/sysconfig/kdump")
    sysconfig_libvirt_guests = simple_file("etc/sysconfig/libvirt-guests")
    sysconfig_network = simple_file("etc/sysconfig/network")
    sysconfig_ntpd = simple_file("/etc/sysconfig/ntpd")
    sysconfig_prelink = simple_file("/etc/sysconfig/prelink")
    sysconfig_sshd = simple_file("/etc/sysconfig/sshd")
    sysconfig_virt_who = simple_file("/etc/sysconfig/virt-who")
    sysctl = simple_command("/sbin/sysctl -a")
    sysctl_conf = simple_file("/etc/sysctl.conf")
    systemctl_cat_rpcbind_socket = simple_command("/bin/systemctl cat rpcbind.socket")
    systemctl_cinder_volume = simple_command("/bin/systemctl show openstack-cinder-volume")
    systemctl_httpd = simple_command("/bin/systemctl show httpd")
    systemctl_nginx = simple_command("/bin/systemctl show nginx")
    systemctl_list_unit_files = simple_command("/bin/systemctl list-unit-files")
    systemctl_list_units = simple_command("/bin/systemctl list-units")
    systemctl_mariadb = simple_command("/bin/systemctl show mariadb")
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
    systemid = first_of([
        simple_file("/etc/sysconfig/rhn/systemid"),
        simple_file("/conf/rhn/sysconfig/rhn/systemid")
    ])
    systool_b_scsi_v = simple_command("/bin/systool -b scsi -v")
    tags = simple_file("/tags.json", kind=RawFileProvider)
    thp_use_zero_page = simple_file("/sys/kernel/mm/transparent_hugepage/use_zero_page")
    thp_enabled = simple_file("/sys/kernel/mm/transparent_hugepage/enabled")
    tmpfilesd = glob_file(["/etc/tmpfiles.d/*.conf", "/usr/lib/tmpfiles.d/*.conf", "/run/tmpfiles.d/*.conf"])
    tomcat_vdc_fallback = simple_command("/usr/bin/find /usr/share -maxdepth 1 -name 'tomcat*' -exec /bin/grep -R -s 'VirtualDirContext' --include '*.xml' '{}' +")
    tuned_adm = simple_command("/usr/sbin/tuned-adm list")
    udev_fc_wwpn_id_rules = simple_file("/usr/lib/udev/rules.d/59-fc-wwpn-id.rules")
    uname = simple_command("/usr/bin/uname -a")
    up2date = simple_file("/etc/sysconfig/rhn/up2date")
    up2date_log = simple_file("/var/log/up2date")
    uptime = simple_command("/usr/bin/uptime")
    usr_journald_conf_d = glob_file(r"usr/lib/systemd/journald.conf.d/*.conf")  # note that etc_journald.conf.d also exists
    vdo_status = simple_command("/usr/bin/vdo status")
    vgdisplay = simple_command("/sbin/vgdisplay")
    vdsm_log = simple_file("var/log/vdsm/vdsm.log")
    vdsm_logger_conf = simple_file("etc/vdsm/logger.conf")
    vma_ra_enabled = simple_file("/sys/kernel/mm/swap/vma_ra_enabled")
    vgs_noheadings = simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config=\"global{locking_type=0}\"")
    virsh_list_all = simple_command("/usr/bin/virsh --readonly list --all")
    virt_what = simple_command("/usr/sbin/virt-what")
    virt_who_conf = glob_file([r"etc/virt-who.conf", r"etc/virt-who.d/*.conf"])
    virtlogd_conf = simple_file("/etc/libvirt/virtlogd.conf")
    vsftpd = simple_file("/etc/pam.d/vsftpd")
    vsftpd_conf = simple_file("/etc/vsftpd/vsftpd.conf")
    woopsie = simple_command(r"/usr/bin/find /var/crash /var/tmp -path '*.reports-*/whoopsie-report' -print -quit")
    x86_pti_enabled = simple_file("sys/kernel/debug/x86/pti_enabled")
    x86_ibpb_enabled = simple_file("sys/kernel/debug/x86/ibpb_enabled")
    x86_ibrs_enabled = simple_file("sys/kernel/debug/x86/ibrs_enabled")
    x86_retp_enabled = simple_file("sys/kernel/debug/x86/retp_enabled")
    xinetd_conf = glob_file(["/etc/xinetd.conf", "/etc/xinetd.d/*"])
    yum_conf = simple_file("/etc/yum.conf")
    yum_list_available = simple_command("yum -C --noplugins list available")
    yum_log = simple_file("/var/log/yum.log")
    yum_repolist = simple_command("/usr/bin/yum -C --noplugins repolist")
    yum_repos_d = glob_file("/etc/yum.repos.d/*.repo")
    zipl_conf = simple_file("/etc/zipl.conf")
    rpm_format = format_rpm()
    installed_rpms = simple_command("/bin/rpm -qa --qf '%s'" % rpm_format, context=HostContext)
