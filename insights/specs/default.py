"""
This module defines all datasources used by standard Red Hat Insight components.

To define data sources that override the components in this file, create a
`insights.core.spec_factory.SpecFactory` with "insights.specs" as the constructor
argument. Data sources created with that factory will override components in
this file with the same `name` keyword argument. This allows overriding the
data sources that standard Insights `Parsers` resolve against.
"""

import logging
import signal

from insights.core.context import HostContext
from insights.core.spec_factory import RawFileProvider
from insights.core.spec_factory import simple_file, simple_command, glob_file
from insights.core.spec_factory import first_of, command_with_args
from insights.core.spec_factory import foreach_collect, foreach_execute
from insights.core.spec_factory import first_file, listdir
from insights.components.cloud_provider import IsAWS, IsAzure, IsGCP
from insights.components.ceph import IsCephMonitor
from insights.components.virtualization import IsBareMetal
from insights.combiners.satellite_version import SatelliteVersion, CapsuleVersion
from insights.specs import Specs
from insights.specs.datasources import (
    awx_manage, cloud_init, candlepin_broker, corosync as corosync_ds,
    dir_list, ethernet, httpd, ipcs, kernel_module_list, lpstat, md5chk,
    package_provides, ps as ps_datasource, sap, satellite_missed_queues,
    ssl_certificate, user_group, yum_updates)
from insights.specs.datasources.sap import sap_hana_sid, sap_hana_sid_SID_nr
from insights.specs.datasources.pcp import pcp_enabled, pmlog_summary_args


logger = logging.getLogger(__name__)


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
    abrt_ccpp_conf = simple_file("/etc/abrt/plugins/CCpp.conf")
    abrt_status_bare = simple_command("/usr/bin/abrt status --bare=True")
    alternatives_display_python = simple_command("/usr/sbin/alternatives --display python")
    amq_broker = glob_file("/var/opt/amq-broker/*/etc/broker.xml")
    dse_ldif = glob_file("/etc/dirsrv/*/dse.ldif")
    auditctl_status = simple_command("/sbin/auditctl -s")
    auditd_conf = simple_file("/etc/audit/auditd.conf")
    audit_log = simple_file("/var/log/audit/audit.log")
    avc_hash_stats = simple_file("/sys/fs/selinux/avc/hash_stats")
    avc_cache_threshold = simple_file("/sys/fs/selinux/avc/cache_threshold")
    aws_instance_id_doc = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/document --connect-timeout 5", deps=[IsAWS])
    aws_instance_id_pkcs7 = simple_command("/usr/bin/curl -s http://169.254.169.254/latest/dynamic/instance-identity/pkcs7 --connect-timeout 5", deps=[IsAWS])
    awx_manage_check_license = simple_command("/usr/bin/awx-manage check_license")
    awx_manage_check_license_data = awx_manage.awx_manage_check_license_data_datasource
    awx_manage_print_settings = simple_command("/usr/bin/awx-manage print_settings INSIGHTS_TRACKING_STATE SYSTEM_UUID INSTALL_UUID TOWER_URL_BASE AWX_CLEANUP_PATHS AWX_PROOT_BASE_PATH LOG_AGGREGATOR_ENABLED LOG_AGGREGATOR_LEVEL --format json")
    azure_instance_type = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2018-10-01&format=text --connect-timeout 5", deps=[IsAzure])
    azure_instance_plan = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json --connect-timeout 5", deps=[IsAzure])
    bdi_read_ahead_kb = glob_file("/sys/class/bdi/*/read_ahead_kb")
    bios_uuid = simple_command("/usr/sbin/dmidecode -s system-uuid")
    blkid = simple_command("/sbin/blkid -c /dev/null")
    bond = glob_file("/proc/net/bonding/*")
    bond_dynamic_lb = glob_file("/sys/class/net/*/bonding/tlb_dynamic_lb")
    boot_loader_entries = glob_file("/boot/loader/entries/*.conf")
    branch_info = simple_file("/branch_info", kind=RawFileProvider)
    brctl_show = simple_command("/usr/sbin/brctl show")
    candlepin_broker = candlepin_broker.candlepin_broker
    candlepin_log = simple_file("/var/log/candlepin/candlepin.log")
    cgroups = simple_file("/proc/cgroups")
    proc_keys = simple_file("/proc/keys")
    ps_alxwww = simple_command("/bin/ps alxwww")
    ps_aux = simple_command("/bin/ps aux")
    ps_auxcww = simple_command("/bin/ps auxcww")
    ps_auxww = simple_command("/bin/ps auxww")
    ps_ef = simple_command("/bin/ps -ef")
    ps_eo = simple_command("/usr/bin/ps -eo pid,ppid,comm")
    ps_eo_cmd = ps_datasource.ps_eo_cmd
    cciss = glob_file("/proc/driver/cciss/cciss*")
    cdc_wdm = simple_file("/sys/bus/usb/drivers/cdc_wdm/module/refcnt")
    ceilometer_collector_log = first_file(["/var/log/containers/ceilometer/collector.log", "/var/log/ceilometer/collector.log"])
    ceilometer_compute_log = first_file(["/var/log/containers/ceilometer/compute.log", "/var/log/ceilometer/compute.log"])
    ceilometer_conf = first_file(["/var/lib/config-data/puppet-generated/ceilometer/etc/ceilometer/ceilometer.conf", "/etc/ceilometer/ceilometer.conf"])
    ceph_conf = first_file(["/var/lib/config-data/puppet-generated/ceph/etc/ceph/ceph.conf", "/etc/ceph/ceph.conf"])
    ceph_df_detail = simple_command("/usr/bin/ceph df detail -f json")
    ceph_health_detail = simple_command("/usr/bin/ceph health detail -f json")
    ceph_insights = simple_command("/usr/bin/ceph insights", deps=[IsCephMonitor])
    ceph_log = glob_file(r"var/log/ceph/ceph.log*")
    ceph_osd_dump = simple_command("/usr/bin/ceph osd dump -f json")
    ceph_osd_ec_profile_ls = simple_command("/usr/bin/ceph osd erasure-code-profile ls")
    ceph_osd_log = glob_file(r"var/log/ceph/ceph-osd*.log")
    ceph_osd_tree = simple_command("/usr/bin/ceph osd tree -f json")
    ceph_s = simple_command("/usr/bin/ceph -s -f json")
    ceph_v = simple_command("/usr/bin/ceph -v")
    certificates_enddate = simple_command("/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa /etc/tower/tower.cert -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \; -exec echo 'FileName= {}' \;", keep_rc=True)
    chkconfig = simple_command("/sbin/chkconfig --list")
    chrony_conf = simple_file("/etc/chrony.conf")
    chronyc_sources = simple_command("/usr/bin/chronyc sources")
    cib_xml = simple_file("/var/lib/pacemaker/cib/cib.xml")
    cinder_api_log = first_file(["/var/log/containers/cinder/cinder-api.log", "/var/log/cinder/cinder-api.log"])
    cinder_conf = first_file(["/var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf", "/etc/cinder/cinder.conf"])
    cinder_volume_log = first_file(["/var/log/containers/cinder/volume.log", "/var/log/containers/cinder/cinder-volume.log", "/var/log/cinder/volume.log"])
    cloud_cfg = cloud_init.cloud_cfg
    cloud_init_custom_network = simple_file("/etc/cloud/cloud.cfg.d/99-custom-networking.cfg")
    cloud_init_log = simple_file("/var/log/cloud-init.log")
    cluster_conf = simple_file("/etc/cluster/cluster.conf")
    cmdline = simple_file("/proc/cmdline")
    cni_podman_bridge_conf = simple_file("/etc/cni/net.d/87-podman-bridge.conflist")
    corosync = simple_file("/etc/sysconfig/corosync")
    corosync_cmapctl = foreach_execute(corosync_ds.corosync_cmapctl_cmds, "%s")
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
    cups_ppd = glob_file("etc/cups/ppd/*")
    current_clocksource = simple_file("/sys/devices/system/clocksource/clocksource0/current_clocksource")
    date = simple_command("/bin/date")
    date_utc = simple_command("/bin/date --utc")
    db2ls_a_c = simple_command("/usr/local/bin/db2ls -a -c")
    designate_conf = first_file(["/var/lib/config-data/puppet-generated/designate/etc/designate/designate.conf",
                                 "/etc/designate/designate.conf"])
    df__al = simple_command("/bin/df -al -x autofs")
    df__alP = simple_command("/bin/df -alP -x autofs")
    df__li = simple_command("/bin/df -li -x autofs")
    dig_dnssec = simple_command("/usr/bin/dig +dnssec . SOA")
    dig_edns = simple_command("/usr/bin/dig +edns=0 . SOA")
    dig_noedns = simple_command("/usr/bin/dig +noedns . SOA")
    dirsrv_errors = glob_file("var/log/dirsrv/*/errors*")
    dm_mod_use_blk_mq = simple_file("/sys/module/dm_mod/parameters/use_blk_mq")
    dmesg = simple_command("/bin/dmesg")
    dmesg_log = simple_file("/var/log/dmesg")
    dmidecode = simple_command("/usr/sbin/dmidecode")
    dmsetup_info = simple_command("/usr/sbin/dmsetup info -C")
    dmsetup_status = simple_command("/usr/sbin/dmsetup status")
    dnf_conf = simple_file("/etc/dnf/dnf.conf")
    dnf_modules = glob_file("/etc/dnf/modules.d/*.module")
    dnsmasq_config = glob_file(["/etc/dnsmasq.conf", "/etc/dnsmasq.d/*.conf"])
    docker_info = simple_command("/usr/bin/docker info")
    docker_list_containers = simple_command("/usr/bin/docker ps --all --no-trunc")
    docker_list_images = simple_command("/usr/bin/docker images --all --no-trunc --digests")
    doveconf = simple_command("/usr/bin/doveconf")
    docker_storage_setup = simple_file("/etc/sysconfig/docker-storage-setup")
    docker_sysconfig = simple_file("/etc/sysconfig/docker")
    dotnet_version = simple_command("/usr/bin/dotnet --version")
    dracut_kdump_capture_service = simple_file("/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service")
    du_dirs = foreach_execute(dir_list.du_dir_list, "/bin/du -s -k %s")
    engine_db_query_vdsm_version = simple_command('engine-db-query --statement "SELECT vs.vds_name, rpm_version FROM vds_dynamic vd, vds_static vs WHERE vd.vds_id = vs.vds_id" --json')
    engine_log = simple_file("/var/log/ovirt-engine/engine.log")
    etc_journald_conf = simple_file(r"etc/systemd/journald.conf")
    etc_journald_conf_d = glob_file(r"etc/systemd/journald.conf.d/*.conf")
    etc_machine_id = simple_file("/etc/machine-id")
    etc_udev_40_redhat_rules = first_file(["/etc/udev/rules.d/40-redhat.rules", "/run/udev/rules.d/40-redhat.rules",
                                       "/usr/lib/udev/rules.d/40-redhat.rules", "/usr/local/lib/udev/rules.d/40-redhat.rules"])
    etc_udev_oracle_asm_rules = glob_file(r"/etc/udev/rules.d/*asm*.rules")
    etcd_conf = simple_file("/etc/etcd/etcd.conf")
    ethernet_interfaces = listdir("/sys/class/net", context=HostContext)
    ethtool = foreach_execute(ethernet.interfaces, "/sbin/ethtool %s")
    ethtool_S = foreach_execute(ethernet.interfaces, "/sbin/ethtool -S %s")
    ethtool_T = foreach_execute(ethernet.interfaces, "/sbin/ethtool -T %s")
    ethtool_c = foreach_execute(ethernet.interfaces, "/sbin/ethtool -c %s")
    ethtool_g = foreach_execute(ethernet.interfaces, "/sbin/ethtool -g %s")
    ethtool_i = foreach_execute(ethernet.interfaces, "/sbin/ethtool -i %s")
    ethtool_k = foreach_execute(ethernet.interfaces, "/sbin/ethtool -k %s")
    fc_match = simple_command("/bin/fc-match -sv 'sans:regular:roman' family fontformat")
    fcoeadm_i = simple_command("/usr/sbin/fcoeadm -i")
    findmnt_lo_propagation = simple_command("/bin/findmnt -lo+PROPAGATION")
    firewall_cmd_list_all_zones = simple_command("/usr/bin/firewall-cmd --list-all-zones")
    firewalld_conf = simple_file("/etc/firewalld/firewalld.conf")
    foreman_production_log = simple_file("/var/log/foreman/production.log")
    foreman_ssl_error_ssl_log = simple_file("/var/log/httpd/foreman-ssl_error_ssl.log")
    fstab = simple_file("/etc/fstab")
    fw_devices = simple_command("/bin/fwupdagent get-devices", deps=[IsBareMetal])
    fw_security = simple_command("/bin/fwupdagent security --force", deps=[IsBareMetal])
    galera_cnf = first_file(["/var/lib/config-data/puppet-generated/mysql/etc/my.cnf.d/galera.cnf", "/etc/my.cnf.d/galera.cnf"])
    getcert_list = simple_command("/usr/bin/getcert list")
    getconf_page_size = simple_command("/usr/bin/getconf PAGE_SIZE")
    getenforce = simple_command("/usr/sbin/getenforce")
    getsebool = simple_command("/usr/sbin/getsebool -a")
    gluster_v_info = simple_command("/usr/sbin/gluster volume info")
    gnocchi_conf = first_file(["/var/lib/config-data/puppet-generated/gnocchi/etc/gnocchi/gnocchi.conf", "/etc/gnocchi/gnocchi.conf"])
    gnocchi_metricd_log = first_file(["/var/log/containers/gnocchi/gnocchi-metricd.log", "/var/log/gnocchi/metricd.log"])
    gcp_instance_type = simple_command("/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/machine-type --connect-timeout 5", deps=[IsGCP])
    gcp_license_codes = simple_command("/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True --connect-timeout 5", deps=[IsGCP])
    greenboot_status = simple_command("/usr/libexec/greenboot/greenboot-status")
    group_info = command_with_args("/usr/bin/getent group %s", user_group.group_filters)
    grubenv = first_file(["/boot/grub2/grubenv", "/boot/efi/EFI/redhat/grubenv"])
    grub_conf = simple_file("/boot/grub/grub.conf")
    grub_config_perms = simple_command("/bin/ls -lH /boot/grub2/grub.cfg")  # only RHEL7 and updwards
    grub_efi_conf = simple_file("/boot/efi/EFI/redhat/grub.conf")
    grub1_config_perms = simple_command("/bin/ls -lH /boot/grub/grub.conf")  # RHEL6
    grub2_cfg = simple_file("/boot/grub2/grub.cfg")
    grub2_efi_cfg = simple_file("boot/efi/EFI/redhat/grub.cfg")
    grubby_default_index = simple_command("/usr/sbin/grubby --default-index")  # only RHEL7 and updwards
    grubby_default_kernel = simple_command("/sbin/grubby --default-kernel")
    hammer_task_list = simple_command("/usr/bin/hammer --config /root/.hammer/cli.modules.d/foreman.yml --output csv task list --search 'state=running AND ( label=Actions::Candlepin::ListenOnCandlepinEvents OR label=Actions::Katello::EventQueue::Monitor )'")
    haproxy_cfg = first_file(["/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.cfg"])
    haproxy_cfg_scl = simple_file("/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg")
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
    httpd_cert_info_in_nss = foreach_execute(ssl_certificate.httpd_certificate_info_in_nss, '/usr/bin/certutil -d %s -L -n %s')
    httpd_error_log = simple_file("var/log/httpd/error_log")
    httpd24_httpd_error_log = simple_file("/opt/rh/httpd24/root/etc/httpd/logs/error_log")
    jbcs_httpd24_httpd_error_log = simple_file("/opt/rh/jbcs-httpd24/root/etc/httpd/logs/error_log")
    virt_uuid_facts = simple_file("/etc/rhsm/facts/virt_uuid.facts")
    httpd_pid = simple_command("/usr/bin/pgrep -o httpd")
    httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")
    httpd_M = foreach_execute(httpd.httpd_cmds, "%s -M")
    httpd_ssl_cert_enddate = foreach_execute(ssl_certificate.httpd_ssl_certificate_files, "/usr/bin/openssl x509 -in %s -enddate -noout")
    httpd_V = foreach_execute(httpd.httpd_cmds, "%s -V")
    ibm_fw_vernum_encoded = simple_file("/proc/device-tree/openprom/ibm,fw-vernum_encoded")
    ibm_lparcfg = simple_file("/proc/powerpc/lparcfg")
    ifcfg = glob_file("/etc/sysconfig/network-scripts/ifcfg-*")
    ifcfg_static_route = glob_file("/etc/sysconfig/network-scripts/route-*")
    imagemagick_policy = glob_file(["/etc/ImageMagick/policy.xml", "/usr/lib*/ImageMagick-6.5.4/config/policy.xml"])
    initctl_lst = simple_command("/sbin/initctl --system list")
    init_process_cgroup = simple_file("/proc/1/cgroup")
    insights_client_conf = simple_file('/etc/insights-client/insights-client.conf')
    interrupts = simple_file("/proc/interrupts")
    ip_addr = simple_command("/sbin/ip addr")
    ip_addresses = simple_command("/bin/hostname -I")
    ip_route_show_table_all = simple_command("/sbin/ip route show table all")
    ip_s_link = simple_command("/sbin/ip -s -d link")
    ipaupgrade_log = simple_file("/var/log/ipaupgrade.log")
    ipcs_m = simple_command("/usr/bin/ipcs -m")
    ipcs_m_p = simple_command("/usr/bin/ipcs -m -p")
    ipcs_s = simple_command("/usr/bin/ipcs -s")
    ipcs_s_i = foreach_execute(ipcs.semid, "/usr/bin/ipcs -s -i %s")
    ipsec_conf = simple_file("/etc/ipsec.conf")
    iptables = simple_command("/sbin/iptables-save")
    iptables_permanent = simple_file("etc/sysconfig/iptables")
    ip6tables = simple_command("/sbin/ip6tables-save")
    ipv4_neigh = simple_command("/sbin/ip -4 neighbor show nud all")
    ipv6_neigh = simple_command("/sbin/ip -6 neighbor show nud all")
    ironic_inspector_log = first_file(["/var/log/containers/ironic-inspector/ironic-inspector.log", "/var/log/ironic-inspector/ironic-inspector.log"])
    iscsiadm_m_session = simple_command("/usr/sbin/iscsiadm -m session")
    kdump_conf = simple_file("/etc/kdump.conf")
    kernel_config = glob_file("/boot/config-*")
    kernel_crash_kexec_post_notifiers = simple_file("/sys/module/kernel/parameters/crash_kexec_post_notifiers")
    kexec_crash_size = simple_file("/sys/kernel/kexec_crash_size")
    keystone_crontab = simple_file("/var/spool/cron/keystone")
    kpatch_list = simple_command("/usr/sbin/kpatch list")
    krb5 = glob_file([r"etc/krb5.conf", r"etc/krb5.conf.d/*"])
    ksmstate = simple_file("/sys/kernel/mm/ksm/run")
    ktimer_lockless = simple_file("/sys/kernel/ktimer_lockless_check")
    kubepods_cpu_quota = glob_file("/sys/fs/cgroup/cpu/kubepods.slice/kubepods-burstable.slice/kubepods-burstable-pod[a-f0-9_]*.slice/cpu.cfs_quota_us")
    last_upload_globs = ["/etc/redhat-access-insights/.lastupload", "/etc/insights-client/.lastupload"]
    lastupload = glob_file(last_upload_globs)
    ld_library_path_of_user = sap.ld_library_path_of_user
    ldif_config = glob_file("/etc/dirsrv/slapd-*/dse.ldif")
    libssh_client_config = simple_file("/etc/libssh/libssh_client.config")
    libssh_server_config = simple_file("/etc/libssh/libssh_server.config")
    libvirtd_log = simple_file("/var/log/libvirt/libvirtd.log")
    limits_conf = glob_file(["/etc/security/limits.conf", "/etc/security/limits.d/*.conf"])
    localtime = simple_command("/usr/bin/file -L /etc/localtime")
    logrotate_conf = glob_file(["/etc/logrotate.conf", "/etc/logrotate.d/*"])
    losetup = simple_command("/usr/sbin/losetup -l")
    lpfc_max_luns = simple_file("/sys/module/lpfc/parameters/lpfc_max_luns")
    lpstat_p = simple_command("/usr/bin/lpstat -p")
    lpstat_protocol_printers = lpstat.lpstat_protocol_printers_info
    ls_boot = simple_command("/bin/ls -lanR /boot")
    ls_dev = simple_command("/bin/ls -lanR /dev")
    ls_disk = simple_command("/bin/ls -lanR /dev/disk")
    ls_edac_mc = simple_command("/bin/ls -lan /sys/devices/system/edac/mc")
    etc_and_sub_dirs = sorted(["/etc", "/etc/pki/tls/private", "/etc/pki/tls/certs",
        "/etc/pki/ovirt-vmconsole", "/etc/nova/migration", "/etc/sysconfig",
        "/etc/cloud/cloud.cfg.d", "/etc/rc.d/init.d"])
    ls_etc = simple_command("/bin/ls -lan {0}".format(' '.join(etc_and_sub_dirs)), keep_rc=True)
    ls_ipa_idoverride_memberof = simple_command("/bin/ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof")
    ls_lib_firmware = simple_command("/bin/ls -lanR /lib/firmware")
    ls_ocp_cni_openshift_sdn = simple_command("/bin/ls -l /var/lib/cni/networks/openshift-sdn")
    ls_origin_local_volumes_pods = simple_command("/bin/ls -l /var/lib/origin/openshift.local.volumes/pods")
    ls_osroot = simple_command("/bin/ls -lan /")
    ls_R_var_lib_nova_instances = simple_command("/bin/ls -laR /var/lib/nova/instances")
    ls_sys_firmware = simple_command("/bin/ls -lanR /sys/firmware")
    ls_systemd_units = simple_command(
        "/bin/ls -lanRL /etc/systemd /run/systemd /usr/lib/systemd /usr/local/lib/systemd", keep_rc=True
    )
    ls_tmp = simple_command("/bin/ls -la /tmp")
    ls_usr_bin = simple_command("/bin/ls -lan /usr/bin")
    ls_usr_lib64 = simple_command("/bin/ls -lan /usr/lib64")
    ls_var_cache_pulp = simple_command("/bin/ls -lan /var/cache/pulp")
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
    lsof = first_of([
        simple_command("/usr/bin/lsof"),
        simple_command("/usr/sbin/lsof")
    ])
    lspci = simple_command("/sbin/lspci -k")
    lspci_vmmkn = simple_command("/sbin/lspci -vmmkn")
    lsscsi = simple_command("/usr/bin/lsscsi")
    lsvmbus = simple_command("/usr/sbin/lsvmbus -vv")
    lvm_conf = simple_file("/etc/lvm/lvm.conf")
    lvmconfig = first_of([
        simple_command("/usr/sbin/lvmconfig --type full"),
        simple_command("/usr/sbin/lvm dumpconfig --type full"),
    ])
    lvm_system_devices = simple_file("/etc/lvm/devices/system.devices")
    lvs_noheadings = simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor,lv_kernel_major,lv_kernel_minor --config=\"global{locking_type=0}\"")
    mac_addresses = glob_file("/sys/class/net/*/address")
    machine_id = first_file(["etc/insights-client/machine-id", "etc/redhat-access-insights/machine-id", "etc/redhat_access_proactive/machine-id"])
    mariadb_log = simple_file("/var/log/mariadb/mariadb.log")
    max_uid = simple_command("/bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd")
    md5chk_files = foreach_execute(md5chk.files, "/usr/bin/md5sum %s", keep_rc=True)
    mdstat = simple_file("/proc/mdstat")
    meminfo = first_file(["/proc/meminfo", "/meminfo"])
    messages = simple_file("/var/log/messages")
    modinfo_i40e = simple_command("/sbin/modinfo i40e")
    modinfo_igb = simple_command("/sbin/modinfo igb")
    modinfo_ixgbe = simple_command("/sbin/modinfo ixgbe")
    modinfo_filtered_modules = command_with_args('modinfo %s', kernel_module_list.kernel_module_filters)
    modinfo_veth = simple_command("/sbin/modinfo veth")
    modinfo_vmxnet3 = simple_command("/sbin/modinfo vmxnet3")
    modprobe = glob_file(["/etc/modprobe.conf", "/etc/modprobe.d/*.conf"])
    mokutil_sbstate = simple_command("/bin/mokutil --sb-state")
    mongod_conf = glob_file([
        "/etc/mongod.conf",
        "/etc/opt/rh/rh-mongodb34/mongod.conf"
    ])
    mount = simple_command("/bin/mount")
    mountinfo = simple_file("/proc/self/mountinfo")
    mounts = simple_file("/proc/mounts")
    mssql_api_assessment = simple_file("/var/opt/mssql/log/assessments/assessment-latest")
    mssql_conf = simple_file("/var/opt/mssql/mssql.conf")
    mssql_tls_cert_enddate = command_with_args("/usr/bin/openssl x509 -in %s -enddate -noout", ssl_certificate.mssql_tls_cert_file)
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
    networkmanager_conf = simple_file("/etc/NetworkManager/NetworkManager.conf")
    networkmanager_dispatcher_d = glob_file("/etc/NetworkManager/dispatcher.d/*-dhclient")
    neutron_conf = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf", "/etc/neutron/neutron.conf"])
    neutron_sriov_agent = first_file([
        "/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/sriov_agent.ini",
        "/etc/neutron/plugins/ml2/sriov_agent.ini"])
    neutron_dhcp_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/dhcp_agent.ini", "/etc/neutron/dhcp_agent.ini"])
    neutron_l3_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini", "/etc/neutron/l3_agent.ini"])
    neutron_l3_agent_log = first_file(["/var/log/containers/neutron/l3-agent.log", "/var/log/neutron/l3-agent.log"])
    neutron_metadata_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/metadata_agent.ini", "/etc/neutron/metadata_agent.ini"])
    neutron_metadata_agent_log = first_file(["/var/log/containers/neutron/metadata-agent.log", "/var/log/neutron/metadata-agent.log"])
    neutron_ovs_agent_log = first_file(["/var/log/containers/neutron/openvswitch-agent.log", "/var/log/neutron/openvswitch-agent.log"])
    neutron_plugin_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/plugin.ini", "/etc/neutron/plugin.ini"])
    nfnetlink_queue = simple_file("/proc/net/netfilter/nfnetlink_queue")
    nfs_conf = simple_file("/etc/nfs.conf")
    nfs_exports = simple_file("/etc/exports")
    nfs_exports_d = glob_file("/etc/exports.d/*.exports")
    nginx_conf = glob_file([
                           "/etc/nginx/*.conf", "/etc/nginx/conf.d/*.conf", "/etc/nginx/default.d/*.conf",
                           "/opt/rh/nginx*/root/etc/nginx/*.conf", "/opt/rh/nginx*/root/etc/nginx/conf.d/*.conf", "/opt/rh/nginx*/root/etc/nginx/default.d/*.conf",
                           "/etc/opt/rh/rh-nginx*/nginx/*.conf", "/etc/opt/rh/rh-nginx*/nginx/conf.d/*.conf", "/etc/opt/rh/rh-nginx*/nginx/default.d/*.conf"
                           ])
    nginx_ssl_cert_enddate = foreach_execute(ssl_certificate.nginx_ssl_certificate_files, "/usr/bin/openssl x509 -in %s -enddate -noout")
    nmcli_conn_show = simple_command("/usr/bin/nmcli conn show")
    nmcli_dev_show = simple_command("/usr/bin/nmcli dev show")
    nova_api_log = first_file(["/var/log/containers/nova/nova-api.log", "/var/log/nova/nova-api.log"])
    nova_compute_log = first_file(["/var/log/containers/nova/nova-compute.log", "/var/log/nova/nova-compute.log"])
    nova_conf = first_file([
                           "/var/lib/config-data/puppet-generated/nova/etc/nova/nova.conf",
                           "/var/lib/config-data/puppet-generated/nova_libvirt/etc/nova/nova.conf",
                           "/etc/nova/nova.conf"
                           ])
    nginx_error_log = simple_file("/var/log/nginx/error.log")
    nova_crontab = simple_file("/var/spool/cron/nova")
    nova_uid = simple_command("/usr/bin/id -u nova")
    nscd_conf = simple_file("/etc/nscd.conf")
    nss_rhel7 = simple_file("/etc/pki/nss-legacy/nss-rhel7.config")
    nsswitch_conf = simple_file("/etc/nsswitch.conf")
    ntp_conf = simple_file("/etc/ntp.conf")
    ntpq_leap = simple_command("/usr/sbin/ntpq -c 'rv 0 leap'")
    ntpq_pn = simple_command("/usr/sbin/ntpq -pn")
    ntptime = simple_command("/usr/sbin/ntptime")
    numa_cpus = glob_file("/sys/devices/system/node/node[0-9]*/cpulist")
    numeric_user_group_name = simple_command("/bin/grep -c '^[[:digit:]]' /etc/passwd /etc/group")
    nvme_core_io_timeout = simple_file("/sys/module/nvme_core/parameters/io_timeout")
    oc_get_clusterrole_with_config = simple_command("/usr/bin/oc get clusterrole --config /etc/origin/master/admin.kubeconfig")
    oc_get_clusterrolebinding_with_config = simple_command("/usr/bin/oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig")
    od_cpu_dma_latency = simple_command("/usr/bin/od -An -t d /dev/cpu_dma_latency")
    odbc_ini = simple_file("/etc/odbc.ini")
    odbcinst_ini = simple_file("/etc/odbcinst.ini")
    open_vm_tools_stat_raw_text_session = simple_command("/usr/bin/vmware-toolbox-cmd stat raw text session")
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
    package_provides_command = package_provides.cmd_and_pkg
    pacemaker_log = first_file(["/var/log/pacemaker.log", "/var/log/pacemaker/pacemaker.log"])
    partitions = simple_file("/proc/partitions")
    pci_rport_target_disk_paths = simple_command("/usr/bin/find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f")
    pcp_metrics = simple_command("/usr/bin/curl -s http://127.0.0.1:44322/metrics --connect-timeout 5", deps=[pcp_enabled])
    passenger_status = simple_command("/usr/bin/passenger-status")
    password_auth = simple_file("/etc/pam.d/password-auth")
    pcs_quorum_status = simple_command("/usr/sbin/pcs quorum status")
    pcs_status = simple_command("/usr/sbin/pcs status")
    php_ini = first_file(["/etc/opt/rh/php73/php.ini", "/etc/opt/rh/php72/php.ini", "/etc/php.ini"])
    pluginconf_d = glob_file("/etc/yum/pluginconf.d/*.conf")
    pmlog_summary = command_with_args("/usr/bin/pmlogsummary %s", pmlog_summary_args)
    pmrep_metrics = simple_command("/usr/bin/pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout mssql.memory_manager.stolen_server_memory mssql.memory_manager.total_server_memory -o csv")
    podman_list_containers = simple_command("/usr/bin/podman ps --all --no-trunc")
    podman_list_images = simple_command("/usr/bin/podman images --all --no-trunc --digests")
    postconf_builtin = simple_command("/usr/sbin/postconf -C builtin")
    postconf = simple_command("/usr/sbin/postconf")
    postgresql_conf = first_file([
        "/var/opt/rh/rh-postgresql12/lib/pgsql/data/postgresql.conf",
        "/var/lib/pgsql/data/postgresql.conf",
    ])
    postgresql_log = first_of(
        [
            glob_file("/var/opt/rh/rh-postgresql12/lib/pgsql/data/log/postgresql-*.log"),
            glob_file("/var/lib/pgsql/data/pg_log/postgresql-*.log"),
        ]
    )
    puppetserver_config = simple_file("/etc/sysconfig/puppetserver")
    proc_netstat = simple_file("proc/net/netstat")
    proc_slabinfo = simple_file("proc/slabinfo")
    proc_snmp_ipv4 = simple_file("proc/net/snmp")
    proc_snmp_ipv6 = simple_file("proc/net/snmp6")
    proc_stat = simple_file("proc/stat")
    pulp_worker_defaults = simple_file("etc/default/pulp_workers")
    puppet_ca_cert_expire_date = simple_command("/usr/bin/openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout")
    pvs_noheadings = simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config=\"global{locking_type=0}\"")
    rhsm_katello_default_ca_cert = simple_command("/usr/bin/openssl x509 -in /etc/rhsm/ca/katello-default-ca.pem -noout -issuer")
    qemu_conf = simple_file("/etc/libvirt/qemu.conf")
    qemu_xml = glob_file(r"/etc/libvirt/qemu/*.xml")
    ql2xmaxlun = simple_file("/sys/module/qla2xxx/parameters/ql2xmaxlun")
    ql2xmqsupport = simple_file("/sys/module/qla2xxx/parameters/ql2xmqsupport")
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
    rhsm_conf = simple_file("/etc/rhsm/rhsm.conf")
    rhsm_log = simple_file("/var/log/rhsm/rhsm.log")
    rhsm_releasever = simple_file('/var/lib/rhsm/cache/releasever.json')
    rndc_status = simple_command("/usr/sbin/rndc status")
    ros_config = simple_file("/var/lib/pcp/config/pmlogger/config.ros")
    rpm_ostree_status = simple_command("/usr/bin/rpm-ostree status --json")
    rpm_V_packages = simple_command("/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo chrony", keep_rc=True, signum=signal.SIGTERM)
    rsyslog_conf = glob_file(["/etc/rsyslog.conf", "/etc/rsyslog.d/*.conf"])
    samba = simple_file("/etc/samba/smb.conf")
    sap_hana_landscape = foreach_execute(sap_hana_sid_SID_nr, "/bin/su -l %sadm -c 'python /usr/sap/%s/HDB%s/exe/python_support/landscapeHostConfiguration.py'", keep_rc=True)
    sap_hdb_version = foreach_execute(sap_hana_sid, "/bin/su -l %sadm -c 'HDB version'", keep_rc=True)
    saphostctl_getcimobject_sapinstance = simple_command("/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance")
    saphostexec_status = simple_command("/usr/sap/hostctrl/exe/saphostexec -status")
    saphostexec_version = simple_command("/usr/sap/hostctrl/exe/saphostexec -version")
    sat5_insights_properties = simple_file("/etc/redhat-access/redhat-access-insights.properties")
    satellite_compute_resources = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select name, type from compute_resources' --csv",
        deps=[SatelliteVersion]
    )
    satellite_content_hosts_count = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select count(*) from hosts'",
        deps=[SatelliteVersion]
    )
    satellite_core_taskreservedresource_count = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d pulpcore -c 'select count(*) from core_taskreservedresource' --csv",
        deps=[SatelliteVersion]
    )
    satellite_custom_ca_chain = simple_command(
        '/usr/bin/awk \'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}\' /etc/pki/katello/certs/katello-server-ca.crt',
    )
    satellite_custom_hiera = simple_file("/etc/foreman-installer/custom-hiera.yaml")
    satellite_katello_repos_with_muliple_ref = simple_command(
        '/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c "select repository_href, count(*) from katello_repository_references group by repository_href having count(*) > 1;" --csv',
        deps=[SatelliteVersion]
    )
    satellite_missed_pulp_agent_queues = satellite_missed_queues.satellite_missed_pulp_agent_queues
    satellite_mongodb_storage_engine = simple_command("/usr/bin/mongo pulp_database --eval 'db.serverStatus().storageEngine'")
    satellite_non_yum_type_repos = simple_command(
        "/usr/bin/mongo pulp_database --eval 'db.repo_importers.find({\"importer_type_id\": { $ne: \"yum_importer\"}}).count()'",
        deps=[[SatelliteVersion, CapsuleVersion]]
    )
    satellite_qualified_capsules = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name from smart_proxies where download_policy = 'background'\" --csv",
        deps=[SatelliteVersion]
    )
    satellite_qualified_katello_repos = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select id, name, url, download_policy from katello_root_repositories where download_policy = 'background' or url is NULL\" --csv",
        deps=[SatelliteVersion]
    )
    satellite_sca_status = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d candlepin -c \"select displayname,content_access_mode from cp_owner\" --csv",
        deps=[SatelliteVersion]
    )
    satellite_settings = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name, value, \\\"default\\\" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')\" --csv",
        deps=[SatelliteVersion]
    )
    satellite_version_rb = simple_file("/usr/share/foreman/lib/satellite/version.rb")
    satellite_yaml = simple_file("/etc/foreman-installer/scenarios.d/satellite.yaml")
    scheduler = glob_file("/sys/block/*/queue/scheduler")
    scsi = simple_file("/proc/scsi/scsi")
    scsi_eh_deadline = glob_file('/sys/class/scsi_host/host[0-9]*/eh_deadline')
    scsi_fwver = glob_file('/sys/class/scsi_host/host[0-9]*/fwrev')
    scsi_mod_max_report_luns = simple_file("/sys/module/scsi_mod/parameters/max_report_luns")
    scsi_mod_use_blk_mq = simple_file("/sys/module/scsi_mod/parameters/use_blk_mq")
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
    spamassassin_channels = simple_command("/bin/grep -r '^\\s*CHANNELURL=' /etc/mail/spamassassin/channel.d")
    ss = simple_command("/usr/sbin/ss -tupna")
    ssh_config = simple_file("/etc/ssh/ssh_config")
    ssh_config_d = glob_file(r"/etc/ssh/ssh_config.d/*.conf")
    ssh_foreman_proxy_config = simple_file("/usr/share/foreman-proxy/.ssh/ssh_config")
    sshd_config = simple_file("/etc/ssh/sshd_config")
    sshd_config_perms = simple_command("/bin/ls -lH /etc/ssh/sshd_config")
    sssd_config = simple_file("/etc/sssd/sssd.conf")
    subscription_manager_id = simple_command("/usr/sbin/subscription-manager identity")  # use "/usr/sbin" here, BZ#1690529
    subscription_manager_installed_product_ids = simple_command("/usr/bin/find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;")
    sudoers = glob_file(["/etc/sudoers", "/etc/sudoers.d/*"])
    swift_object_expirer_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/object-expirer.conf", "/etc/swift/object-expirer.conf"])
    swift_proxy_server_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/proxy-server.conf", "/etc/swift/proxy-server.conf"])
    sysconfig_grub = simple_file("/etc/default/grub")  # This is the file where the "/etc/sysconfig/grub" point to
    sysconfig_kdump = simple_file("etc/sysconfig/kdump")
    sysconfig_libvirt_guests = simple_file("etc/sysconfig/libvirt-guests")
    sysconfig_network = simple_file("etc/sysconfig/network")
    sysconfig_nfs = simple_file("/etc/sysconfig/nfs")
    sysconfig_ntpd = simple_file("/etc/sysconfig/ntpd")
    sysconfig_oracleasm = simple_file("/etc/sysconfig/oracleasm")
    sysconfig_prelink = simple_file("/etc/sysconfig/prelink")
    sysconfig_sshd = simple_file("/etc/sysconfig/sshd")
    sysconfig_virt_who = simple_file("/etc/sysconfig/virt-who")
    sysctl = simple_command("/sbin/sysctl -a")
    sysctl_conf = simple_file("/etc/sysctl.conf")
    sysctl_d_conf_etc = glob_file("/etc/sysctl.d/*.conf")
    sysctl_d_conf_usr = glob_file("/usr/lib/sysctl.d/*.conf")
    systemctl_cat_dnsmasq_service = simple_command("/bin/systemctl cat dnsmasq.service")
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
    systemctl_show_all_services_with_limited_properties = simple_command("systemctl show *.service --all --property=Names,CPUAccounting,CPUQuotaPerSecUSec,CPUShares,StartupCPUShares,UnitFileState,SubState")
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
    systool_b_scsi_v = first_of([
        simple_command("/usr/bin/systool -b scsi -v"),
        simple_command("/bin/systool -b scsi -v")
    ])
    sys_vmbus_device_id = glob_file('/sys/bus/vmbus/devices/*/device_id')
    sys_vmbus_class_id = glob_file('/sys/bus/vmbus/devices/*/class_id')
    teamdctl_state_dump = foreach_execute(ethernet.team_interfaces, "/usr/bin/teamdctl %s state dump")
    testparm_s = simple_command("/usr/bin/testparm -s")
    testparm_v_s = simple_command("/usr/bin/testparm -v -s")
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
    version_info = simple_file("/version_info")
    vgdisplay = simple_command("/sbin/vgdisplay")
    vhost_net_zero_copy_tx = simple_file("/sys/module/vhost_net/parameters/experimental_zcopytx")
    vdsm_log = simple_file("var/log/vdsm/vdsm.log")
    vdsm_logger_conf = simple_file("etc/vdsm/logger.conf")
    vma_ra_enabled = simple_file("/sys/kernel/mm/swap/vma_ra_enabled")
    vgs_noheadings = simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config=\"global{locking_type=0}\"")
    virsh_list_all = simple_command("/usr/bin/virsh --readonly list --all")
    virt_what = simple_command("/usr/sbin/virt-what")
    virt_who_conf = glob_file([r"etc/virt-who.conf", r"etc/virt-who.d/*.conf"])
    virtlogd_conf = simple_file("/etc/libvirt/virtlogd.conf")
    vmware_tools_conf = simple_file("/etc/vmware-tools/tools.conf")
    vsftpd = simple_file("/etc/pam.d/vsftpd")
    vsftpd_conf = simple_file("/etc/vsftpd/vsftpd.conf")
    wc_proc_1_mountinfo = simple_command("/usr/bin/wc -l /proc/1/mountinfo")
    x86_pti_enabled = simple_file("sys/kernel/debug/x86/pti_enabled")
    x86_ibpb_enabled = simple_file("sys/kernel/debug/x86/ibpb_enabled")
    x86_ibrs_enabled = simple_file("sys/kernel/debug/x86/ibrs_enabled")
    x86_retp_enabled = simple_file("sys/kernel/debug/x86/retp_enabled")
    xinetd_conf = glob_file(["/etc/xinetd.conf", "/etc/xinetd.d/*"])
    yum_conf = simple_file("/etc/yum.conf")
    yum_list_available = simple_command("yum -C --noplugins list available", signum=signal.SIGTERM)
    yum_log = simple_file("/var/log/yum.log")
    yum_repolist = simple_command("/usr/bin/yum -C --noplugins repolist", signum=signal.SIGTERM)
    yum_repos_d = glob_file("/etc/yum.repos.d/*.repo")
    yum_updateinfo = simple_command("/usr/bin/yum -C updateinfo list", signum=signal.SIGTERM)
    yum_updates = yum_updates.yum_updates

    zipl_conf = simple_file("/etc/zipl.conf")
    rpm_format = format_rpm()
    installed_rpms = simple_command("/bin/rpm -qa --qf '%s'" % rpm_format, context=HostContext, signum=signal.SIGTERM)
