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
from insights.core.spec_factory import MetadataProvider
from insights.core.spec_factory import simple_file, simple_command, glob_file, head
from insights.core.spec_factory import first_of, command_with_args
from insights.core.spec_factory import foreach_collect, foreach_execute
from insights.core.spec_factory import container_collect, container_execute
from insights.core.spec_factory import first_file, listdir
from insights.components.cloud_provider import IsAzure, IsGCP
from insights.components.ceph import IsCephMonitor
from insights.components.virtualization import IsBareMetal
from insights.components.satellite import IsCapsule, IsSatellite611, IsSatellite
from insights.specs import Specs
from insights.specs.datasources import (
    aws, awx_manage, cloud_init, candlepin_broker, corosync as corosync_ds,
    dir_list, ethernet, httpd, ipcs, kernel, kernel_module_list, leapp, lpstat,
    machine_ids, md5chk, package_provides, ps as ps_datasource, rsyslog_confs, sap,
    satellite_missed_queues, semanage, ssl_certificate, sys_fs_cgroup_memory,
    sys_fs_cgroup_memory_tasks_number, rpm_pkgs, user_group, yum_updates,
    luks_devices)
from insights.specs.datasources.sap import sap_hana_sid, sap_hana_sid_SID_nr
from insights.specs.datasources.pcp import pcp_enabled, pmlog_summary_args
from insights.specs.datasources.container import running_rhel_containers, containers_inspect
from insights.specs.datasources.container.nginx_conf import nginx_conf as container_nginx_conf_ds


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
    return "\{" + ",".join(fmt) + "\}\n"


_etc_and_sub_dirs = sorted(["/etc", "/etc/pki/tls/private", "/etc/pki/tls/certs",
                           "/etc/pki/ovirt-vmconsole", "/etc/nova/migration", "/etc/sysconfig",
                           "/etc/cloud/cloud.cfg.d", "/etc/rc.d/init.d", "/etc/selinux/targeted/policy"])
""" List of directories for spec `ls_etc` """
_rpm_format = _make_rpm_formatter()
""" Query format for specs `installed_rpms` and `container_installed_rpms` """


class DefaultSpecs(Specs):
    # Dep specs that aren't in the registry
    block_devices_by_uuid = listdir("/dev/disk/by-uuid/", context=HostContext)
    httpd_pid = simple_command("/usr/bin/pgrep -o httpd")
    openshift_router_pid = simple_command("/usr/bin/pgrep -n openshift-route")
    ovs_vsctl_list_br = simple_command("/usr/bin/ovs-vsctl list-br")

    # Archive metadata specs/files
    ansible_host = simple_file("/ansible_host", kind=MetadataProvider)
    blacklisted_specs = first_file(["/blacklisted_specs", "/blacklisted_specs.txt"], kind=MetadataProvider)
    branch_info = simple_file("/branch_info", kind=MetadataProvider)
    display_name = simple_file("/display_name", kind=MetadataProvider)
    tags = simple_file("/tags.json", kind=MetadataProvider)
    version_info = simple_file("/version_info", kind=MetadataProvider)

    # Regular collection specs
    abrt_ccpp_conf = simple_file("/etc/abrt/plugins/CCpp.conf")
    abrt_status_bare = simple_command("/usr/bin/abrt status --bare=True")
    alternatives_display_python = simple_command("/usr/sbin/alternatives --display python")
    amq_broker = glob_file("/var/opt/amq-broker/*/etc/broker.xml")
    audit_log = simple_file("/var/log/audit/audit.log")
    auditctl_rules = simple_command("/sbin/auditctl -l")
    auditctl_status = simple_command("/sbin/auditctl -s")
    auditd_conf = simple_file("/etc/audit/auditd.conf")
    audispd_conf = simple_file("/etc/audisp/audispd.conf")
    aws_instance_id_doc = command_with_args('/usr/bin/curl -s -H "X-aws-ec2-metadata-token: %s" http://169.254.169.254/latest/dynamic/instance-identity/document --connect-timeout 5', aws.aws_imdsv2_token, deps=[aws.aws_imdsv2_token])
    aws_instance_id_pkcs7 = command_with_args('/usr/bin/curl -s -H "X-aws-ec2-metadata-token: %s" http://169.254.169.254/latest/dynamic/instance-identity/pkcs7 --connect-timeout 5', aws.aws_imdsv2_token, deps=[aws.aws_imdsv2_token])
    aws_public_ipv4_addresses = command_with_args('/usr/bin/curl -s -H "X-aws-ec2-metadata-token: %s" http://169.254.169.254/latest/meta-data/public-ipv4 --connect-timeout 5', aws.aws_imdsv2_token, deps=[aws.aws_imdsv2_token])
    aws_public_hostnames = command_with_args('/usr/bin/curl -s -H "X-aws-ec2-metadata-token: %s" http://169.254.169.254/latest/meta-data/public-hostname --connect-timeout 5', aws.aws_imdsv2_token, deps=[aws.aws_imdsv2_token])
    awx_manage_check_license = simple_command("/usr/bin/awx-manage check_license")
    awx_manage_check_license_data = awx_manage.awx_manage_check_license_data_datasource
    awx_manage_print_settings = simple_command("/usr/bin/awx-manage print_settings INSIGHTS_TRACKING_STATE SYSTEM_UUID INSTALL_UUID TOWER_URL_BASE AWX_CLEANUP_PATHS AWX_PROOT_BASE_PATH LOG_AGGREGATOR_ENABLED LOG_AGGREGATOR_LEVEL --format json")
    azure_instance_id = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmId?api-version=2021-12-13&format=text --connect-timeout 5", deps=[IsAzure])
    azure_instance_plan = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2021-12-13&format=json --connect-timeout 5", deps=[IsAzure])
    azure_instance_type = simple_command("/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/vmSize?api-version=2021-12-13&format=text --connect-timeout 5", deps=[IsAzure])
    bdi_read_ahead_kb = glob_file("/sys/class/bdi/*/read_ahead_kb")
    bios_uuid = simple_command("/usr/sbin/dmidecode -s system-uuid")
    blkid = simple_command("/sbin/blkid -c /dev/null")
    bond = glob_file("/proc/net/bonding/*")
    bond_dynamic_lb = glob_file("/sys/class/net/*/bonding/tlb_dynamic_lb")
    boot_loader_entries = glob_file("/boot/loader/entries/*.conf")
    brctl_show = simple_command("/usr/sbin/brctl show")
    candlepin_broker = candlepin_broker.candlepin_broker
    cciss = glob_file("/proc/driver/cciss/cciss*")
    cdc_wdm = simple_file("/sys/bus/usb/drivers/cdc_wdm/module/refcnt")
    ceilometer_compute_log = first_file(["/var/log/containers/ceilometer/compute.log", "/var/log/ceilometer/compute.log"])
    ceph_conf = first_file(["/var/lib/config-data/puppet-generated/ceph/etc/ceph/ceph.conf", "/etc/ceph/ceph.conf"])
    ceph_df_detail = simple_command("/usr/bin/ceph df detail -f json")
    ceph_health_detail = simple_command("/usr/bin/ceph health detail -f json")
    ceph_insights = simple_command("/usr/bin/ceph insights", deps=[IsCephMonitor])
    ceph_log = glob_file(r"var/log/ceph/ceph.log*")
    ceph_osd_dump = simple_command("/usr/bin/ceph osd dump -f json")
    ceph_osd_ec_profile_ls = simple_command("/usr/bin/ceph osd erasure-code-profile ls")
    ceph_osd_tree = simple_command("/usr/bin/ceph osd tree -f json")
    ceph_v = simple_command("/usr/bin/ceph -v")
    certificates_enddate = simple_command("/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki /etc/ipa /etc/tower/tower.cert -type f -exec /usr/bin/openssl x509 -noout -enddate -in '{}' \; -exec echo 'FileName= {}' \;", keep_rc=True)
    cgroups = simple_file("/proc/cgroups")
    chkconfig = simple_command("/sbin/chkconfig --list")
    chrony_conf = simple_file("/etc/chrony.conf")
    chronyc_sources = simple_command("/usr/bin/chronyc sources")
    cib_xml = simple_file("/var/lib/pacemaker/cib/cib.xml")
    cinder_api_log = first_file(["/var/log/containers/cinder/cinder-api.log", "/var/log/cinder/cinder-api.log"])
    cinder_conf = first_file(["/var/lib/config-data/puppet-generated/cinder/etc/cinder/cinder.conf", "/etc/cinder/cinder.conf"])
    cinder_volume_log = first_file(["/var/log/containers/cinder/volume.log", "/var/log/containers/cinder/cinder-volume.log", "/var/log/cinder/volume.log"])
    cloud_cfg_filtered = cloud_init.cloud_cfg
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
    cpu_smt_control = simple_file("sys/devices/system/cpu/smt/control")
    cpu_vulns = glob_file("sys/devices/system/cpu/vulnerabilities/*")
    cpuinfo = simple_file("/proc/cpuinfo")
    cpupower_frequency_info = simple_command("/usr/bin/cpupower -c all frequency-info")
    cpuset_cpus = simple_file("/sys/fs/cgroup/cpuset/cpuset.cpus")
    cron_daily_rhsmd = simple_file("/etc/cron.daily/rhsmd")
    cron_foreman = simple_file("/etc/cron.d/foreman")
    crypto_policies_bind = simple_file("/etc/crypto-policies/back-ends/bind.config")
    crypto_policies_config = simple_file("/etc/crypto-policies/config")
    crypto_policies_opensshserver = simple_file("/etc/crypto-policies/back-ends/opensshserver.config")
    crypto_policies_state_current = simple_file("/etc/crypto-policies/state/current")
    cryptsetup_luksDump = luks_devices.luks_data_sources
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
    docker_info = simple_command("/usr/bin/docker info")
    docker_list_containers = simple_command("/usr/bin/docker ps --all --no-trunc")
    docker_list_images = simple_command("/usr/bin/docker images --all --no-trunc --digests")
    docker_storage_setup = simple_file("/etc/sysconfig/docker-storage-setup")
    docker_sysconfig = simple_file("/etc/sysconfig/docker")
    dotnet_version = simple_command("/usr/bin/dotnet --version")
    doveconf = simple_command("/usr/bin/doveconf")
    dracut_kdump_capture_service = simple_file("/usr/lib/dracut/modules.d/99kdumpbase/kdump-capture.service")
    dse_ldif = glob_file("/etc/dirsrv/*/dse.ldif")
    du_dirs = foreach_execute(dir_list.du_dir_list, "/bin/du -s -k %s")
    duplicate_machine_id = machine_ids.dup_machine_id_info
    engine_log = simple_file("/var/log/ovirt-engine/engine.log")
    etc_journald_conf = simple_file(r"etc/systemd/journald.conf")
    etc_journald_conf_d = glob_file(r"etc/systemd/journald.conf.d/*.conf")
    etc_machine_id = simple_file("/etc/machine-id")
    etc_udev_40_redhat_rules = first_file(["/etc/udev/rules.d/40-redhat.rules", "/run/udev/rules.d/40-redhat.rules",
                                       "/usr/lib/udev/rules.d/40-redhat.rules", "/usr/local/lib/udev/rules.d/40-redhat.rules"])
    etc_udev_oracle_asm_rules = glob_file(r"/etc/udev/rules.d/*asm*.rules")
    etcd_conf = simple_file("/etc/etcd/etcd.conf")
    ethtool = foreach_execute(ethernet.interfaces, "/sbin/ethtool %s")
    ethtool_S = foreach_execute(ethernet.interfaces, "/sbin/ethtool -S %s")
    ethtool_T = foreach_execute(ethernet.interfaces, "/sbin/ethtool -T %s")
    ethtool_c = foreach_execute(ethernet.interfaces, "/sbin/ethtool -c %s")
    ethtool_g = foreach_execute(ethernet.interfaces, "/sbin/ethtool -g %s")
    ethtool_i = foreach_execute(ethernet.interfaces, "/sbin/ethtool -i %s")
    ethtool_k = foreach_execute(ethernet.interfaces, "/sbin/ethtool -k %s")
    fapolicyd_rules = glob_file(r"/etc/fapolicyd/rules.d/*.rules")
    fcoeadm_i = simple_command("/usr/sbin/fcoeadm -i")
    findmnt_lo_propagation = simple_command("/bin/findmnt -lo+PROPAGATION")
    firewall_cmd_list_all_zones = simple_command("/usr/bin/firewall-cmd --list-all-zones")
    firewalld_conf = simple_file("/etc/firewalld/firewalld.conf")
    foreman_production_log = simple_file("/var/log/foreman/production.log")
    fstab = simple_file("/etc/fstab")
    fw_devices = simple_command("/bin/fwupdagent get-devices", deps=[IsBareMetal])
    fw_security = simple_command("/bin/fwupdagent security --force", deps=[IsBareMetal])
    galera_cnf = first_file(["/var/lib/config-data/puppet-generated/mysql/etc/my.cnf.d/galera.cnf", "/etc/my.cnf.d/galera.cnf"])
    gcp_instance_type = simple_command("/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/machine-type --connect-timeout 5", deps=[IsGCP])
    gcp_license_codes = simple_command("/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True --connect-timeout 5", deps=[IsGCP])
    getcert_list = simple_command("/usr/bin/getcert list")
    getconf_page_size = simple_command("/usr/bin/getconf PAGE_SIZE")
    getenforce = simple_command("/usr/sbin/getenforce")
    getsebool = simple_command("/usr/sbin/getsebool -a")
    gluster_v_info = simple_command("/usr/sbin/gluster volume info")
    gnocchi_conf = first_file(["/var/lib/config-data/puppet-generated/gnocchi/etc/gnocchi/gnocchi.conf", "/etc/gnocchi/gnocchi.conf"])
    gnocchi_metricd_log = first_file(["/var/log/containers/gnocchi/gnocchi-metricd.log", "/var/log/gnocchi/metricd.log"])
    greenboot_status = simple_command("/usr/libexec/greenboot/greenboot-status")
    group_info = command_with_args("/usr/bin/getent group %s", user_group.group_filters)
    grub1_config_perms = simple_command("/bin/ls -lH /boot/grub/grub.conf")  # RHEL6
    grub2_cfg = simple_file("/boot/grub2/grub.cfg")
    grub2_efi_cfg = simple_file("boot/efi/EFI/redhat/grub.cfg")
    grubby_default_index = simple_command("/usr/sbin/grubby --default-index")  # only RHEL7 and updwards
    grubby_default_kernel = simple_command("/sbin/grubby --default-kernel")
    grub_conf = simple_file("/boot/grub/grub.conf")
    grub_config_perms = simple_command("/bin/ls -lH /boot/grub2/grub.cfg")  # only RHEL7 and updwards
    grub_efi_conf = simple_file("/boot/efi/EFI/redhat/grub.conf")
    grubenv = simple_command("/usr/bin/grub2-editenv list", keep_rc=True)
    haproxy_cfg = first_file(["/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg", "/etc/haproxy/haproxy.cfg"])
    haproxy_cfg_scl = simple_file("/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg")
    heat_conf = first_file(["/var/lib/config-data/puppet-generated/heat/etc/heat/heat.conf", "/etc/heat/heat.conf"])
    hostname = simple_command("/bin/hostname -f")
    hostname_default = simple_command("/bin/hostname")
    hostname_short = simple_command("/bin/hostname -s")
    hosts = simple_file("/etc/hosts")
    httpd24_httpd_error_log = simple_file("/opt/rh/httpd24/root/etc/httpd/logs/error_log")
    httpd_M = foreach_execute(httpd.httpd_cmds, "%s -M")
    httpd_V = foreach_execute(httpd.httpd_cmds, "%s -V")
    httpd_cert_info_in_nss = foreach_execute(ssl_certificate.httpd_certificate_info_in_nss, '/usr/bin/certutil -d %s -L -n %s')
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
    httpd_on_nfs = httpd.httpd_on_nfs
    httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")
    httpd_ssl_cert_enddate = foreach_execute(ssl_certificate.httpd_ssl_certificate_files, "/usr/bin/openssl x509 -in %s -enddate -noout")
    ibm_fw_vernum_encoded = simple_file("/proc/device-tree/openprom/ibm,fw-vernum_encoded")
    ibm_lparcfg = simple_file("/proc/powerpc/lparcfg")
    ifcfg = glob_file("/etc/sysconfig/network-scripts/ifcfg-*")
    ifcfg_static_route = glob_file("/etc/sysconfig/network-scripts/route-*")
    imagemagick_policy = glob_file(["/etc/ImageMagick/policy.xml", "/usr/lib*/ImageMagick-6.5.4/config/policy.xml"])
    init_process_cgroup = simple_file("/proc/1/cgroup")
    initctl_lst = simple_command("/sbin/initctl --system list")
    insights_client_conf = simple_file('/etc/insights-client/insights-client.conf')
    installed_rpms = simple_command("/bin/rpm -qa --qf '%s'" % _rpm_format, context=HostContext, signum=signal.SIGTERM)
    interrupts = simple_file("/proc/interrupts")
    ip6tables = simple_command("/sbin/ip6tables-save")
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
    ipv4_neigh = simple_command("/sbin/ip -4 neighbor show nud all")
    ipv6_neigh = simple_command("/sbin/ip -6 neighbor show nud all")
    ironic_inspector_log = first_file(["/var/log/containers/ironic-inspector/ironic-inspector.log", "/var/log/ironic-inspector/ironic-inspector.log"])
    iscsiadm_m_session = simple_command("/usr/sbin/iscsiadm -m session")
    jbcs_httpd24_httpd_error_log = simple_file("/opt/rh/jbcs-httpd24/root/etc/httpd/logs/error_log")
    jboss_runtime_versions = ps_datasource.jboss_runtime_versions
    journal_header = simple_command("/usr/bin/journalctl --no-pager --header")
    kdump_conf = simple_file("/etc/kdump.conf")
    kernel_config = glob_file("/boot/config-*")
    kernel_crash_kexec_post_notifiers = simple_file("/sys/module/kernel/parameters/crash_kexec_post_notifiers")
    kexec_crash_size = simple_file("/sys/kernel/kexec_crash_size")
    keystone_crontab = simple_file("/var/spool/cron/keystone")
    kpatch_list = simple_command("/usr/sbin/kpatch list")
    krb5 = glob_file([r"etc/krb5.conf", r"etc/krb5.conf.d/*"])
    ksmstate = simple_file("/sys/kernel/mm/ksm/run")
    lastupload = glob_file(["/etc/redhat-access-insights/.lastupload", "/etc/insights-client/.lastupload"])
    leapp_report = leapp.leapp_report
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
    lsinitrd_lvm_conf = command_with_args("/bin/lsinitrd -f /etc/lvm/lvm.conf --kver %s", kernel.default_version)
    ls_R_var_lib_nova_instances = simple_command("/bin/ls -laR /var/lib/nova/instances")
    ls_boot = simple_command("/bin/ls -lanR /boot")
    ls_dev = simple_command("/bin/ls -lanR /dev")
    ls_disk = simple_command("/bin/ls -lanR /dev/disk")
    ls_edac_mc = simple_command("/bin/ls -lan /sys/devices/system/edac/mc")
    ls_etc = simple_command("/bin/ls -lan {0}".format(' '.join(_etc_and_sub_dirs)), keep_rc=True)
    ls_etc_ssh = simple_command("/bin/ls -lanL /etc/ssh")
    ls_ipa_idoverride_memberof = simple_command("/bin/ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof")
    ls_krb5_sssd = simple_command("/bin/ls -lan /var/lib/sss/pubconf/krb5.include.d")
    ls_lib_firmware = simple_command("/bin/ls -lanR /lib/firmware")
    ls_osroot = simple_command("/bin/ls -lan /")
    ls_rsyslog_errorfile = command_with_args("/bin/ls -ln %s", rsyslog_confs.rsyslog_errorfile, keep_rc=True)
    ls_sys_firmware = simple_command("/bin/ls -lanR /sys/firmware")
    ls_systemd_units = simple_command(
        "/bin/ls -lanRL /etc/systemd /run/systemd /usr/lib/systemd /usr/local/lib/systemd /usr/local/share/systemd /usr/share/systemd",
        keep_rc=True
    )
    ls_tmp = simple_command("/bin/ls -la /tmp")
    ls_usr_bin = simple_command("/bin/ls -lan /usr/bin")
    ls_usr_lib64 = simple_command("/bin/ls -lan /usr/lib64")
    ls_var_cache_pulp = simple_command("/bin/ls -lan /var/cache/pulp")
    ls_var_lib_mongodb = simple_command("/bin/ls -la /var/lib/mongodb")
    ls_var_lib_nova_instances = simple_command("/bin/ls -laRZ /var/lib/nova/instances")
    ls_var_lib_pcp = simple_command("/bin/ls -la /var/lib/pcp")
    ls_var_lib_rsyslog = simple_command("/bin/ls -lZ /var/lib/rsyslog")
    ls_var_log = simple_command("/bin/ls -la /var/log /var/log/audit")
    ls_var_opt_mssql = simple_command("/bin/ls -ld /var/opt/mssql")
    ls_var_opt_mssql_log = simple_command("/bin/ls -la /var/opt/mssql/log")
    ls_var_run = simple_command("/bin/ls -lnL /var/run")
    ls_var_spool_clientmq = simple_command("/bin/ls -ln /var/spool/clientmqueue")
    ls_var_spool_postfix_maildrop = simple_command("/bin/ls -ln /var/spool/postfix/maildrop")
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
    luksmeta = foreach_execute(block_devices_by_uuid, "/usr/bin/luksmeta show -d /dev/disk/by-uuid/%s", keep_rc=True)
    lvm_system_devices = simple_file("/etc/lvm/devices/system.devices")
    lvmconfig = first_of([
        simple_command("/usr/sbin/lvmconfig --type full"),
        simple_command("/usr/sbin/lvm dumpconfig --type full"),
    ])
    lvs_noheadings = simple_command("/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor,lv_kernel_major,lv_kernel_minor --config=\"global{locking_type=0}\"")
    mac_addresses = glob_file("/sys/class/net/*/address")
    machine_id = first_file(["etc/insights-client/machine-id", "etc/redhat-access-insights/machine-id", "etc/redhat_access_proactive/machine-id"])
    mariadb_log = simple_file("/var/log/mariadb/mariadb.log")
    max_uid = simple_command("/bin/awk -F':' '{ if($3 > max) max = $3 } END { print max }' /etc/passwd")
    md5chk_files = foreach_execute(md5chk.files, "/usr/bin/md5sum %s", keep_rc=True)
    mdstat = simple_file("/proc/mdstat")
    meminfo = first_file(["/proc/meminfo", "/meminfo"])
    messages = simple_file("/var/log/messages")
    modinfo_filtered_modules = command_with_args('modinfo %s', kernel_module_list.kernel_module_filters)
    modprobe = glob_file(["/etc/modprobe.conf", "/etc/modprobe.d/*.conf"])
    mokutil_sbstate = simple_command("/bin/mokutil --sb-state")
    mongod_conf = glob_file([
        "/etc/mongod.conf",
        "/etc/opt/rh/rh-mongodb34/mongod.conf"
    ])
    mount = simple_command("/bin/mount")
    mountinfo = simple_file("/proc/self/mountinfo")
    mounts = simple_file("/proc/mounts")
    mpirun_version = simple_command("/usr/local/bin/mpirun --version")
    mssql_api_assessment = simple_file("/var/opt/mssql/log/assessments/assessment-latest")
    mssql_conf = simple_file("/var/opt/mssql/mssql.conf")
    mssql_tls_cert_enddate = command_with_args("/usr/bin/openssl x509 -in %s -enddate -noout", ssl_certificate.mssql_tls_cert_file)
    multicast_querier = simple_command("/usr/bin/find /sys/devices/virtual/net/ -name multicast_querier -print -exec cat {} \;")
    multipath__v4__ll = simple_command("/sbin/multipath -v4 -ll")
    multipath_conf = simple_file("/etc/multipath.conf")
    multipath_conf_initramfs = simple_command("/bin/lsinitrd -f /etc/multipath.conf")
    mysql_log = glob_file([
                          "/var/log/mysql/mysqld.log",
                          "/var/log/mysql.log",
                          "/var/opt/rh/rh-mysql*/log/mysql/mysqld.log"
                          ])
    mysqladmin_vars = simple_command("/bin/mysqladmin variables")
    named_checkconf_p = simple_command("/usr/sbin/named-checkconf -p")
    named_conf = simple_file("/etc/named.conf")
    ndctl_list_Ni = simple_command("/usr/bin/ndctl list -Ni")
    netconsole = simple_file("/etc/sysconfig/netconsole")
    netstat = simple_command("/bin/netstat -neopa")
    netstat_i = simple_command("/bin/netstat -i")
    netstat_s = simple_command("/bin/netstat -s")
    networkmanager_conf = simple_file("/etc/NetworkManager/NetworkManager.conf")
    networkmanager_dispatcher_d = glob_file("/etc/NetworkManager/dispatcher.d/*-dhclient")
    neutron_conf = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf", "/etc/neutron/neutron.conf"])
    neutron_dhcp_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/dhcp_agent.ini", "/etc/neutron/dhcp_agent.ini"])
    neutron_l3_agent_ini = first_file(["/var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini", "/etc/neutron/l3_agent.ini"])
    neutron_l3_agent_log = first_file(["/var/log/containers/neutron/l3-agent.log", "/var/log/neutron/l3-agent.log"])
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

    nginx_error_log = first_of(
        [
            simple_file("/var/log/nginx/error.log"),
            head(glob_file("/var/opt/rh/rh-nginx*/log/nginx/error.log")),
        ]
    )
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
    nova_uid = simple_command("/usr/bin/id -u nova")
    nscd_conf = simple_file("/etc/nscd.conf")
    nss_rhel7 = simple_file("/etc/pki/nss-legacy/nss-rhel7.config")
    nsswitch_conf = simple_file("/etc/nsswitch.conf")
    ntp_conf = simple_file("/etc/ntp.conf")
    ntpq_pn = simple_command("/usr/sbin/ntpq -pn")
    numa_cpus = glob_file("/sys/devices/system/node/node[0-9]*/cpulist")
    numeric_user_group_name = simple_command("/bin/grep -c '^[[:digit:]]' /etc/passwd /etc/group")
    nvme_core_io_timeout = simple_file("/sys/module/nvme_core/parameters/io_timeout")
    od_cpu_dma_latency = simple_command("/usr/bin/od -An -t d /dev/cpu_dma_latency")
    odbc_ini = simple_file("/etc/odbc.ini")
    odbcinst_ini = simple_file("/etc/odbcinst.ini")
    openshift_router_environ = foreach_collect(openshift_router_pid, "/proc/%s/environ")
    openvswitch_other_config = simple_command("/usr/bin/ovs-vsctl -t 5 get Open_vSwitch . other_config")
    os_release = simple_file("etc/os-release")
    ose_master_config = simple_file("/etc/origin/master/master-config.yaml")
    ose_node_config = simple_file("/etc/origin/node/node-config.yaml")
    ovirt_engine_server_log = simple_file("/var/log/ovirt-engine/server.log")
    ovirt_engine_ui_log = simple_file("/var/log/ovirt-engine/ui.log")
    ovs_appctl_fdb_show_bridge = foreach_execute(ovs_vsctl_list_br, "/usr/bin/ovs-appctl fdb/show %s")
    ovs_vsctl_list_bridge = simple_command("/usr/bin/ovs-vsctl list bridge")
    ovs_vsctl_show = simple_command("/usr/bin/ovs-vsctl show")
    pacemaker_log = first_file(["/var/log/pacemaker.log", "/var/log/pacemaker/pacemaker.log"])
    package_provides_command = package_provides.cmd_and_pkg
    parted__l = simple_command("/sbin/parted -l -s")
    password_auth = simple_file("/etc/pam.d/password-auth")
    pci_rport_target_disk_paths = simple_command("/usr/bin/find /sys/devices/ -maxdepth 10 -mindepth 9 -name stat -type f")
    pcp_metrics = simple_command("/usr/bin/curl -s http://127.0.0.1:44322/metrics --connect-timeout 5", deps=[pcp_enabled])
    pcp_openmetrics_log = simple_file("/var/log/pcp/pmcd/openmetrics.log")
    pcs_quorum_status = simple_command("/usr/sbin/pcs quorum status")
    pcs_status = simple_command("/usr/sbin/pcs status")
    php_ini = first_file(["/etc/opt/rh/php73/php.ini", "/etc/opt/rh/php72/php.ini", "/etc/php.ini"])
    pluginconf_d = glob_file("/etc/yum/pluginconf.d/*.conf")
    pmlog_summary = command_with_args("/usr/bin/pmlogsummary %s", pmlog_summary_args)
    pmrep_metrics = simple_command("/usr/bin/pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout mssql.memory_manager.stolen_server_memory mssql.memory_manager.total_server_memory -o csv")
    podman_list_containers = simple_command("/usr/bin/podman ps --all --no-trunc")
    podman_list_images = simple_command("/usr/bin/podman images --all --no-trunc --digests")
    postconf = simple_command("/usr/sbin/postconf")
    postconf_builtin = simple_command("/usr/sbin/postconf -C builtin")
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
    proc_keys = simple_file("/proc/keys")
    proc_netstat = simple_file("proc/net/netstat")
    proc_slabinfo = simple_file("proc/slabinfo")
    proc_snmp_ipv4 = simple_file("proc/net/snmp")
    proc_snmp_ipv6 = simple_file("proc/net/snmp6")
    proc_stat = simple_file("proc/stat")
    ps_alxwww = simple_command("/bin/ps alxwww")
    ps_aux = simple_command("/bin/ps aux")
    ps_auxcww = simple_command("/bin/ps auxcww")
    ps_auxww = simple_command("/bin/ps auxww")
    ps_ef = simple_command("/bin/ps -ef")
    ps_eo = simple_command("/usr/bin/ps -eo pid,ppid,comm")
    ps_eo_cmd = ps_datasource.ps_eo_cmd
    pulp_worker_defaults = simple_file("etc/default/pulp_workers")
    puppet_ca_cert_expire_date = simple_command("/usr/bin/openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout")
    pvs_noheadings = simple_command("/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config=\"global{locking_type=0}\"")
    rhsm_katello_default_ca_cert = simple_command("/usr/bin/openssl x509 -in /etc/rhsm/ca/katello-default-ca.pem -noout -issuer")
    qemu_xml = glob_file(r"/etc/libvirt/qemu/*.xml")
    ql2xmaxlun = simple_file("/sys/module/qla2xxx/parameters/ql2xmaxlun")
    ql2xmqsupport = simple_file("/sys/module/qla2xxx/parameters/ql2xmqsupport")
    rabbitmq_env = simple_file("/etc/rabbitmq/rabbitmq-env.conf")
    rabbitmq_report = simple_command("/usr/sbin/rabbitmqctl report")
    rc_local = simple_file("/etc/rc.d/rc.local")
    readlink_e_etc_mtab = simple_command("/usr/bin/readlink -e /etc/mtab")
    readlink_e_shift_cert_client = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-client-current.pem")
    readlink_e_shift_cert_server = simple_command("/usr/bin/readlink -e /etc/origin/node/certificates/kubelet-server-current.pem")
    redhat_release = simple_file("/etc/redhat-release")
    repquota_agnpuv = simple_command("/usr/sbin/repquota -agnpuv")
    resolv_conf = simple_file("/etc/resolv.conf")
    rhsm_conf = simple_file("/etc/rhsm/rhsm.conf")
    rhsm_releasever = simple_file('/var/lib/rhsm/cache/releasever.json')
    rndc_status = simple_command("/usr/sbin/rndc status")
    ros_config = simple_file("/var/lib/pcp/config/pmlogger/config.ros")
    rpm_V_packages = simple_command("/bin/rpm -V coreutils procps procps-ng shadow-utils passwd sudo chrony findutils", keep_rc=True, signum=signal.SIGTERM)
    rpm_ostree_status = simple_command("/usr/bin/rpm-ostree status --json", signum=signal.SIGTERM)
    rpm_pkgs = rpm_pkgs.pkgs_with_writable_dirs
    rsyslog_conf = glob_file(["/etc/rsyslog.conf", "/etc/rsyslog.d/*.conf"])
    samba = simple_file("/etc/samba/smb.conf")
    sap_hana_landscape = foreach_execute(sap_hana_sid_SID_nr, "/bin/su -l %sadm -c 'python /usr/sap/%s/HDB%s/exe/python_support/landscapeHostConfiguration.py'", keep_rc=True)
    sap_hdb_version = foreach_execute(sap_hana_sid, "/bin/su -l %sadm -c 'HDB version'", keep_rc=True)
    saphostctl_getcimobject_sapinstance = simple_command("/usr/sap/hostctrl/exe/saphostctrl -function GetCIMObject -enuminstances SAPInstance")
    saphostexec_status = simple_command("/usr/sap/hostctrl/exe/saphostexec -status")
    saphostexec_version = simple_command("/usr/sap/hostctrl/exe/saphostexec -version")
    satellite_compute_resources = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select name, type from compute_resources' --csv",
        deps=[IsSatellite]
    )
    satellite_content_hosts_count = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select count(*) from hosts'",
        deps=[IsSatellite]
    )
    satellite_core_taskreservedresource_count = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d pulpcore -c 'select count(*) from core_taskreservedresource' --csv",
        deps=[IsSatellite]
    )
    satellite_custom_ca_chain = simple_command(
        '/usr/bin/awk \'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}\' /etc/pki/katello/certs/katello-server-ca.crt',
    )
    satellite_custom_hiera = simple_file("/etc/foreman-installer/custom-hiera.yaml")
    satellite_enabled_features = simple_command("/usr/bin/curl -sk https://localhost:9090/features --connect-timeout 5", deps=[IsSatellite])
    satellite_katello_repos_with_muliple_ref = simple_command(
        '/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c "select repository_href, count(*) from katello_repository_references group by repository_href having count(*) > 1;" --csv',
        deps=[IsSatellite]
    )
    satellite_logs_table_size = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select pg_total_relation_size('logs') as logs_size\" --csv",
        deps=[IsSatellite]
    )
    satellite_missed_pulp_agent_queues = satellite_missed_queues.satellite_missed_pulp_agent_queues
    satellite_mongodb_storage_engine = simple_command("/usr/bin/mongo pulp_database --eval 'db.serverStatus().storageEngine'")
    satellite_non_yum_type_repos = simple_command(
        "/usr/bin/mongo pulp_database --eval 'db.repo_importers.find({\"importer_type_id\": { $ne: \"yum_importer\"}}).count()'",
        deps=[[IsSatellite, IsCapsule]]
    )
    satellite_provision_param_settings = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name, value from parameters where name='package_upgrade' and reference_id in (select id from operatingsystems where name='RedHat' and major='9')\" --csv",
        deps=[IsSatellite611]
    )
    satellite_qualified_capsules = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name from smart_proxies where download_policy = 'background'\" --csv",
        deps=[IsSatellite]
    )
    satellite_qualified_katello_repos = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select id, name, url, download_policy from katello_root_repositories where download_policy = 'background' or url is NULL\" --csv",
        deps=[IsSatellite]
    )
    satellite_sca_status = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d candlepin -c \"select displayname,content_access_mode from cp_owner\" --csv",
        deps=[IsSatellite]
    )
    satellite_settings = simple_command(
        "/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name, value, \\\"default\\\" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')\" --csv",
        deps=[IsSatellite]
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
    secure = simple_file("/var/log/secure")
    selinux_config = simple_file("/etc/selinux/config")
    sestatus = simple_command("/usr/sbin/sestatus -b")
    setup_named_chroot = simple_file("/usr/libexec/setup-named-chroot.sh")
    smbstatus_p = simple_command("/usr/bin/smbstatus -p")
    sockstat = simple_file("/proc/net/sockstat")
    softnet_stat = simple_file("proc/net/softnet_stat")
    software_collections_list = simple_command('/usr/bin/scl --list')
    sos_conf = first_file(["/etc/sos/sos.conf", "/etc/sos.conf"])
    spamassassin_channels = simple_command("/bin/grep -r '^\\s*CHANNELURL=' /etc/mail/spamassassin/channel.d")
    ss = simple_command("/usr/sbin/ss -tupna")
    ssh_config = simple_file("/etc/ssh/ssh_config")
    ssh_config_d = glob_file(r"/etc/ssh/ssh_config.d/*.conf")
    sshd_config = simple_file("/etc/ssh/sshd_config")
    sshd_config_perms = simple_command("/bin/ls -lH /etc/ssh/sshd_config")
    sssd_config = simple_file("/etc/sssd/sssd.conf")
    subscription_manager_facts = simple_command("/usr/sbin/subscription-manager facts",
                                                override_env={"LC_ALL": "C.UTF-8"})
    subscription_manager_id = simple_command("/usr/sbin/subscription-manager identity",  # use "/usr/sbin" here, BZ#1690529
                                             override_env={"LC_ALL": "C.UTF-8"})
    subscription_manager_installed_product_ids = simple_command("/usr/bin/find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;")
    sudoers = glob_file(["/etc/sudoers", "/etc/sudoers.d/*"])
    swift_object_expirer_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/object-expirer.conf", "/etc/swift/object-expirer.conf"])
    swift_proxy_server_conf = first_file(["/var/lib/config-data/puppet-generated/swift/etc/swift/proxy-server.conf", "/etc/swift/proxy-server.conf"])
    sys_block_queue_stable_writes = glob_file("/sys/block/*/queue/stable_writes")
    sys_fs_cgroup_memory_tasks_number = sys_fs_cgroup_memory_tasks_number.sys_fs_cgroup_memory_tasks_number_data_datasource
    sys_fs_cgroup_uniq_memory_swappiness = sys_fs_cgroup_memory.sys_fs_cgroup_uniq_memory_swappiness
    sys_vmbus_class_id = glob_file('/sys/bus/vmbus/devices/*/class_id')
    sys_vmbus_device_id = glob_file('/sys/bus/vmbus/devices/*/device_id')
    sysconfig_grub = simple_file("/etc/default/grub")  # This is the file where the "/etc/sysconfig/grub" point to
    sysconfig_kdump = simple_file("etc/sysconfig/kdump")
    sysconfig_libvirt_guests = simple_file("etc/sysconfig/libvirt-guests")
    sysconfig_network = simple_file("etc/sysconfig/network")
    sysconfig_nfs = simple_file("/etc/sysconfig/nfs")
    sysconfig_ntpd = simple_file("/etc/sysconfig/ntpd")
    sysconfig_oracleasm = simple_file("/etc/sysconfig/oracleasm")
    sysconfig_prelink = simple_file("/etc/sysconfig/prelink")
    sysconfig_sshd = simple_file("/etc/sysconfig/sshd")
    sysctl = simple_command("/sbin/sysctl -a")
    sysctl_conf = simple_file("/etc/sysctl.conf")
    sysctl_d_conf_etc = glob_file("/etc/sysctl.d/*.conf")
    sysctl_d_conf_usr = glob_file("/usr/lib/sysctl.d/*.conf")
    systemctl_cat_rpcbind_socket = simple_command("/bin/systemctl cat rpcbind.socket")
    systemctl_list_unit_files = simple_command("/bin/systemctl list-unit-files")
    systemctl_list_units = simple_command("/bin/systemctl list-units")
    systemctl_show_all_services = simple_command("/bin/systemctl show *.service")
    systemctl_show_target = simple_command("/bin/systemctl show *.target")
    systemd_analyze_blame = simple_command("/bin/systemd-analyze blame")
    systemd_docker = simple_command("/usr/bin/systemctl cat docker.service")
    systemd_logind_conf = simple_file("/etc/systemd/logind.conf")
    systemd_openshift_node = simple_command("/usr/bin/systemctl cat atomic-openshift-node.service")
    systemd_system_conf = simple_file("/etc/systemd/system.conf")
    systemid = first_of([
        simple_file("/etc/sysconfig/rhn/systemid"),
        simple_file("/conf/rhn/sysconfig/rhn/systemid")
    ])
    teamdctl_config_dump = foreach_execute(ethernet.team_interfaces, "/usr/bin/teamdctl %s config dump")
    teamdctl_state_dump = foreach_execute(ethernet.team_interfaces, "/usr/bin/teamdctl %s state dump")
    testparm_s = simple_command("/usr/bin/testparm -s")
    testparm_v_s = simple_command("/usr/bin/testparm -v -s")
    thp_enabled = simple_file("/sys/kernel/mm/transparent_hugepage/enabled")
    thp_use_zero_page = simple_file("/sys/kernel/mm/transparent_hugepage/use_zero_page")
    timedatectl_status = simple_command('/usr/bin/timedatectl status')
    tmpfilesd = glob_file(["/etc/tmpfiles.d/*.conf", "/usr/lib/tmpfiles.d/*.conf", "/run/tmpfiles.d/*.conf"])
    tomcat_vdc_fallback = simple_command("/usr/bin/find /usr/share -maxdepth 1 -name 'tomcat*' -exec /bin/grep -R -s 'VirtualDirContext' --include '*.xml' '{}' +")
    tuned_adm = simple_command("/usr/sbin/tuned-adm list")
    udev_fc_wwpn_id_rules = simple_file("/usr/lib/udev/rules.d/59-fc-wwpn-id.rules")
    uname = simple_command("/usr/bin/uname -a")
    up2date = simple_file("/etc/sysconfig/rhn/up2date")
    up2date_log = simple_file("/var/log/up2date")
    uptime = simple_command("/usr/bin/uptime")
    users_count_map_selinux_user = semanage.users_count_map_selinux_user
    usr_journald_conf_d = glob_file(r"usr/lib/systemd/journald.conf.d/*.conf")  # note that etc_journald.conf.d also exists
    vdo_status = simple_command("/usr/bin/vdo status")
    vdsm_log = simple_file("var/log/vdsm/vdsm.log")
    vgdisplay = simple_command("/sbin/vgdisplay")
    vgs_noheadings = simple_command("/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config=\"global{locking_type=0}\"")
    virsh_list_all = simple_command("/usr/bin/virsh --readonly list --all")
    virt_what = simple_command("/usr/sbin/virt-what")
    virtlogd_conf = simple_file("/etc/libvirt/virtlogd.conf")
    vma_ra_enabled = simple_file("/sys/kernel/mm/swap/vma_ra_enabled")
    vsftpd = simple_file("/etc/pam.d/vsftpd")
    vsftpd_conf = simple_file("/etc/vsftpd/vsftpd.conf")
    wc_proc_1_mountinfo = simple_command("/usr/bin/wc -l /proc/1/mountinfo")
    x86_ibpb_enabled = simple_file("sys/kernel/debug/x86/ibpb_enabled")
    x86_ibrs_enabled = simple_file("sys/kernel/debug/x86/ibrs_enabled")
    x86_pti_enabled = simple_file("sys/kernel/debug/x86/pti_enabled")
    x86_retp_enabled = simple_file("sys/kernel/debug/x86/retp_enabled")
    xinetd_conf = glob_file(["/etc/xinetd.conf", "/etc/xinetd.d/*"])
    yum_conf = simple_file("/etc/yum.conf")
    yum_list_available = simple_command("yum -C --noplugins list available", signum=signal.SIGTERM)
    yum_log = simple_file("/var/log/yum.log")
    yum_repolist = simple_command("/usr/bin/yum -d 2 -C --noplugins repolist", override_env={"LC_ALL": ""},
                                  signum=signal.SIGTERM)
    yum_repos_d = glob_file("/etc/yum.repos.d/*.repo")
    yum_updates = yum_updates.yum_updates
    zipl_conf = simple_file("/etc/zipl.conf")

    # Container collection specs
    container_cpu_online = container_collect(running_rhel_containers, "/sys/devices/system/cpu/online")
    container_cpuset_cpus = container_collect(running_rhel_containers, "/sys/fs/cgroup/cpuset/cpuset.cpus")
    container_dotnet_version = container_execute(running_rhel_containers, "/usr/bin/dotnet --version")
    container_installed_rpms = container_execute(running_rhel_containers, "/usr/bin/rpm -qa --qf '%s'" % _rpm_format, context=HostContext, signum=signal.SIGTERM)
    container_mssql_api_assessment = container_collect(running_rhel_containers, "/var/opt/mssql/log/assessments/assessment-latest")
    container_nginx_conf = container_collect(container_nginx_conf_ds)
    container_nginx_error_log = container_collect(running_rhel_containers, "/var/log/nginx/error.log")
    container_ps_aux = container_execute(running_rhel_containers, "/bin/ps aux")
    container_redhat_release = container_collect(running_rhel_containers, "/etc/redhat-release")
    container_vsftpd_conf = container_collect(running_rhel_containers, "/etc/vsftpd/vsftpd.conf")
    containers_inspect = containers_inspect.containers_inspect_data_datasource
