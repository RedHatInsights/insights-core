from functools import partial
from insights.specs import Specs
from insights.core.context import SosArchiveContext
from insights.core.spec_factory import simple_file, first_of, first_file, glob_file

first_file = partial(first_file, context=SosArchiveContext)
glob_file = partial(glob_file, context=SosArchiveContext)
simple_file = partial(simple_file, context=SosArchiveContext)


class SosSpecs(Specs):
    blkid = simple_file("sos_commands/block/blkid_-c_.dev.null")
    candlepin_error_log = first_of([
        simple_file("var/log/candlepin/error.log"),
        simple_file(r"sos_commands/foreman/foreman-debug/var/log/candlepin/error.log")
    ])
    catalina_out = glob_file("tomcat-logs/tomcat*/catalina.out")
    catalina_server_log = glob_file("tomcat-logs/tomcat*/catalina*.log")
    chkconfig = simple_file("sos_commands/startup/chkconfig_--list")
    date = simple_file("sos_commands/general/date")
    df__al = simple_file("sos_commands/filesys/df_-al")
    df__alP = simple_file("sos_commands/filesys/df_-alP")
    df__li = simple_file("sos_commands/filesys/df_-li")
    display_java = simple_file("sos_commands/java/alternatives_--display_java")
    dmesg = simple_file("sos_commands/kernel/dmesg")
    dmidecode = simple_file("dmidecode")
    dumpe2fs_h = glob_file("sos_commands/filesys/dumpe2fs_-h_*")
    ethtool = glob_file("sos_commands/networking/ethtool_*", ignore="ethtool_-.*")
    ethtool_S = glob_file("sos_commands/networking/ethtool_-S_*")
    ethtool_a = glob_file("sos_commands/networking/ethtool_-a_*")
    ethtool_c = glob_file("sos_commands/networking/ethtool_-c_*")
    ethtool_g = glob_file("sos_commands/networking/ethtool_-g_*")
    ethtool_i = glob_file("sos_commands/networking/ethtool_-i_*")
    ethtool_k = glob_file("sos_commands/networking/ethtool_-k_*")
    fdisk_l_sos = glob_file(r"sos_commands/filesys/fdisk_-l_*")
    foreman_ssl_access_ssl_log = first_file(["var/log/httpd/foreman-ssl_access_ssl.log", r"sos_commands/foreman/foreman-debug/var/log/httpd/foreman-ssl_access_ssl.log"])
    getcert_list = simple_file("sos_commands/ipa/ipa-getcert_list")
    hostname = first_of([simple_file("sos_commands/general/hostname_-f"), simple_file("sos_commands/general/hostname")])
    httpd_conf_sos = glob_file(["/conf/httpd/conf/httpd.conf", "/conf/httpd/conf.d/*.conf"])
    installed_rpms = simple_file("installed-rpms")
    journal_since_boot = simple_file("sos_commands/logs/journalctl_--no-pager_--boot")
    locale = simple_file("sos_commands/i18n/locale")
    lsblk = simple_file("sos_commands/block/lsblk")
    lsof = simple_file("lsof")
    lsmod = simple_file("lsmod")
    lspci = simple_file("lspci")
    lvs = simple_file("sos_commands/lvm2/lvs_-a_-o_lv_tags_devices_--config_global_locking_type_0")
    mount = simple_file("mount")
    multipath__v4__ll = simple_file("sos_commands/multipath/multipath_-v4_-ll")
    netstat = simple_file("netstat")
    netstat_agn = simple_file("sos_commands/networking/netstat_-agn")
    netstat_i = simple_file("sos_commands/networking/netstat_-i")
    netstat_s = simple_file("sos_commands/networking/netstat_-s")
    nmcli_dev_show = simple_file("sos_commands/networking/nmcli_dev_show")
    ntptime = simple_file("sos_commands/ntp/ntptime")
    ps_auxww = first_file(["sos_commands/process/ps_auxwww", "sos_commands/process/ps_aux", "sos_commands/process/ps_auxcww"])
    puppet_ssl_cert_ca_pem = simple_file("sos_commands/foreman/foreman-debug/var/lib/puppet/ssl/certs/ca.pem")
    pvs = simple_file("sos_commands/lvm2/pvs_-a_-v_-o_pv_mda_free_pv_mda_size_pv_mda_count_pv_mda_used_count_pe_start_--config_global_locking_type_0")
    qpid_stat_q = simple_file("sos_commands/foreman/foreman-debug/qpid-stat-q")
    qpid_stat_u = simple_file("sos_commands/foreman/foreman-debug/qpid-stat-u")
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
    uname = simple_file("sos_commands/kernel/uname_-a")
    uptime = simple_file("sos_commands/general/uptime")
    vgdisplay = simple_file("vgdisplay")
    vgs = simple_file("sos_commands/lvm2/vgs_-v_-o_vg_mda_count_vg_mda_free_vg_mda_size_vg_mda_used_count_vg_tags_--config_global_locking_type_0")
    yum_repolist = simple_file("sos_commands/yum/yum_-C_repolist")
