from functools import partial
from insights.specs import Specs
from insights.core.context import SosArchiveContext
from insights.core.spec_factory import simple_file, first_of, first_file, glob_file

first_file = partial(first_file, context=SosArchiveContext)
glob_file = partial(glob_file, context=SosArchiveContext)
simple_file = partial(simple_file, context=SosArchiveContext)


class SosSpecs(Specs):
    auditctl_status = simple_file("sos_commands/auditd/auditctl_-s")
    blkid = simple_file("sos_commands/block/blkid_-c_.dev.null")
    candlepin_log = first_of([
        simple_file("/var/log/candlepin/candlepin.log"),
        simple_file("sos_commands/foreman/foreman-debug/var/log/candlepin/candlepin.log")
    ])
    candlepin_error_log = first_of([
        simple_file("var/log/candlepin/error.log"),
        simple_file(r"sos_commands/foreman/foreman-debug/var/log/candlepin/error.log")
    ])
    catalina_out = glob_file("tomcat-logs/tomcat*/catalina.out")
    catalina_server_log = glob_file("tomcat-logs/tomcat*/catalina*.log")
    ceph_osd_tree_text = simple_file("sos_commands/ceph/ceph_osd_tree")
    chkconfig = simple_file("sos_commands/startup/chkconfig_--list")
    date = first_of([simple_file("sos_commands/general/date"), simple_file("sos_commands/date/date")])
    df__al = first_file(["sos_commands/filesys/df_-al", "sos_commands/filesys/df_-al_-x_autofs"])
    df__alP = simple_file("sos_commands/filesys/df_-alP")
    df__li = first_file(["sos_commands/filesys/df_-li", "sos_commands/filesys/df_-ali_-x_autofs"])
    display_java = simple_file("sos_commands/java/alternatives_--display_java")
    docker_info = simple_file("sos_commands/docker/docker_info")
    docker_list_containers = first_file(["sos_commands/docker/docker_ps", "sos_commands/docker/docker_ps_-a"])
    dmesg = simple_file("sos_commands/kernel/dmesg")
    dmidecode = simple_file("dmidecode")
    dmsetup_info = simple_file("sos_commands/devicemapper/dmsetup_info_-c")
    dumpe2fs_h = glob_file("sos_commands/filesys/dumpe2fs_-h_*")
    ethtool = glob_file("sos_commands/networking/ethtool_*", ignore="ethtool_-.*")
    ethtool_S = glob_file("sos_commands/networking/ethtool_-S_*")
    ethtool_a = glob_file("sos_commands/networking/ethtool_-a_*")
    ethtool_c = glob_file("sos_commands/networking/ethtool_-c_*")
    ethtool_g = glob_file("sos_commands/networking/ethtool_-g_*")
    ethtool_i = glob_file("sos_commands/networking/ethtool_-i_*")
    ethtool_k = glob_file("sos_commands/networking/ethtool_-k_*")
    fdisk_l_sos = first_of([glob_file(r"sos_commands/filesys/fdisk_-l_*"), glob_file(r"sos_commands/block/fdisk_-l_*")])
    foreman_production_log = first_of([simple_file("/var/log/foreman/production.log"), simple_file("sos_commands/foreman/foreman-debug/var/log/foreman/production.log")])
    foreman_proxy_conf = first_of([simple_file("/etc/foreman-proxy/settings.yml"), simple_file("sos_commands/foreman/foreman-debug/etc/foreman-proxy/settings.yml")])
    foreman_proxy_log = first_of([simple_file("/var/log/foreman-proxy/proxy.log"), simple_file("sos_commands/foreman/foreman-debug/var/log/foreman-proxy/proxy.log")])
    foreman_satellite_log = first_of([simple_file("/var/log/foreman-installer/satellite.log"), simple_file("sos_commands/foreman/foreman-debug/var/log/foreman-installer/satellite.log")])
    foreman_ssl_access_ssl_log = first_file(["var/log/httpd/foreman-ssl_access_ssl.log", r"sos_commands/foreman/foreman-debug/var/log/httpd/foreman-ssl_access_ssl.log"])
    getcert_list = simple_file("sos_commands/ipa/ipa-getcert_list")
    gluster_v_info = simple_file("sos_commands/gluster/gluster_volume_info")
    gluster_v_status = simple_file("sos_commands/gluster/gluster_volume_status")
    hostname = first_file(["sos_commands/general/hostname_-f", "sos_commands/general/hostname", "sos_commands/host/hostname_-f", "sos_commands/host/hostname", "/etc/hostname", "hostname"])
    httpd_conf_sos = glob_file(["/conf/httpd/conf/httpd.conf", "/conf/httpd/conf.d/*.conf"])
    installed_rpms = simple_file("installed-rpms")
    ip_addr = first_of([simple_file("sos_commands/networking/ip_-d_address"), simple_file("sos_commands/networking/ip_address")])
    ip_route_show_table_all = simple_file("sos_commands/networking/ip_route_show_table_all")
    iptables = first_file(["/etc/sysconfig/iptables", "/etc/sysconfig/iptables.save"])
    journal_since_boot = first_of([simple_file("sos_commands/logs/journalctl_--no-pager_--boot"), simple_file("sos_commands/logs/journalctl_--no-pager_--catalog_--boot")])
    locale = simple_file("sos_commands/i18n/locale")
    lsblk = simple_file("sos_commands/block/lsblk")
    lsof = simple_file("lsof")
    lsmod = simple_file("lsmod")
    lspci = first_of([
        simple_file("sos_commands/pci/lspci_-nnvv"),
        simple_file("sos_commands/pci/lspci_-nvv"),
        simple_file("sos_commands/pci/lspci")
    ])
    lsscsi = simple_file("sos_commands/scsi/lsscsi")
    ls_dev = simple_file("sos_commands/block/ls_-lanR_.dev")
    lvs = simple_file("sos_commands/lvm2/lvs_-a_-o_lv_tags_devices_--config_global_locking_type_0")
    mount = simple_file("mount")
    multipath__v4__ll = simple_file("sos_commands/multipath/multipath_-v4_-ll")
    netstat = simple_file("sos_commands/networking/netstat_-neopa")
    netstat_agn = first_of([simple_file("sos_commands/networking/netstat_-agn"), simple_file("sos_commands/networking/netstat_-W_-agn"), simple_file("sos_commands/networking/netstat_-T_-agn")])
    netstat_i = simple_file("sos_commands/networking/netstat_-i")
    netstat_s = simple_file("sos_commands/networking/netstat_-s")
    nmcli_dev_show = simple_file("sos_commands/networking/nmcli_dev_show")
    ntptime = simple_file("sos_commands/ntp/ntptime")
    pcs_config = first_file(["sos_commands/pacemaker/pcs_config", "sos_commands/cluster/pcs_config"])
    pcs_status = first_file(["sos_commands/pacemaker/pcs_status", "sos_commands/cluster/pcs_status"])
    ps_aux = first_file(["sos_commands/process/ps_aux", "sos_commands/process/ps_auxwww", "sos_commands/process/ps_auxcww"])
    ps_auxcww = first_file(["sos_commands/process/ps_auxcww", "sos_commands/process/ps_auxwww", "sos_commands/process/ps_aux"])
    ps_auxww = first_file(["sos_commands/process/ps_auxww", "sos_commands/process/ps_auxwww", "sos_commands/process/ps_aux", "sos_commands/process/ps_auxcww"])
    puppet_ssl_cert_ca_pem = simple_file("sos_commands/foreman/foreman-debug/var/lib/puppet/ssl/certs/ca.pem")
    pvs = simple_file("sos_commands/lvm2/pvs_-a_-v_-o_pv_mda_free_pv_mda_size_pv_mda_count_pv_mda_used_count_pe_start_--config_global_locking_type_0")
    qpid_stat_q = first_of([
        simple_file("qpid_stat_queues"),
        simple_file("qpid-stat-q"),
        simple_file("sos_commands/foreman/foreman-debug/qpid_stat_queues"),
        simple_file("sos_commands/foreman/foreman-debug/qpid-stat-q")
    ])
    qpid_stat_u = first_of([
        simple_file("qpid_stat_subscriptions"),
        simple_file("qpid-stat-u"),
        simple_file("sos_commands/foreman/foreman-debug/qpid_stat_subscriptions"),
        simple_file("sos_commands/foreman/foreman-debug/qpid-stat-u")
    ])
    rhn_charsets = simple_file("database-character-sets")
    root_crontab = simple_file("sos_commands/cron/root_crontab")
    route = simple_file("sos_commands/networking/route_-n")
    sestatus = simple_file("sos_commands/selinux/sestatus_-b")
    subscription_manager_list_consumed = first_file([
        'sos_commands/yum/subscription-manager_list_--consumed',
        'sos_commands/subscription_manager/subscription-manager_list_--consumed',
        'sos_commands/general/subscription-manager_list_--consumed']
    )
    subscription_manager_list_installed = first_file([
        'sos_commands/yum/subscription-manager_list_--installed',
        'sos_commands/subscription_manager/subscription-manager_list_--installed',
        'sos_commands/general/subscription-manager_list_--installed']
    )
    sysctl = simple_file("sos_commands/kernel/sysctl_-a")
    systemctl_list_unit_files = simple_file("sos_commands/systemd/systemctl_list-unit-files")
    systemctl_list_units = simple_file("sos_commands/systemd/systemctl_list-units")
    uname = simple_file("sos_commands/kernel/uname_-a")
    uptime = first_of([simple_file("sos_commands/general/uptime"), simple_file("sos_commands/host/uptime")])
    var_qemu_xml = glob_file(r"var/run/libvirt/qemu/*.xml")
    vdsm_import_log = glob_file("var/log/vdsm/import/import-*.log")
    vgdisplay = simple_file("vgdisplay")
    vgs = simple_file("sos_commands/lvm2/vgs_-v_-o_vg_mda_count_vg_mda_free_vg_mda_size_vg_mda_used_count_vg_tags_--config_global_locking_type_0")
    xfs_info = glob_file("sos_commands/xfs/xfs_info*")
    yum_repolist = simple_file("sos_commands/yum/yum_-C_repolist")
