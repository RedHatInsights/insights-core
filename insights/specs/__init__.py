from insights.core.spec_factory import SpecSet, RegistryPoint


class Specs(SpecSet):
    amq_broker = RegistryPoint(multi_output=True)
    auditd_conf = RegistryPoint()
    audit_log = RegistryPoint(filterable=True)
    autofs_conf = RegistryPoint()
    blkid = RegistryPoint()
    bond = RegistryPoint(multi_output=True)
    branch_info = RegistryPoint()
    brctl_show = RegistryPoint()
    candlepin_error_log = RegistryPoint(filterable=True)
    candlepin_log = RegistryPoint(filterable=True)
    checkin_conf = RegistryPoint()
    catalina_out = RegistryPoint(multi_output=True, filterable=True)
    catalina_server_log = RegistryPoint(multi_output=True, filterable=True)
    cciss = RegistryPoint(multi_output=True)
    ceilometer_central_log = RegistryPoint(filterable=True)
    ceilometer_collector_log = RegistryPoint(filterable=True)
    ceilometer_conf = RegistryPoint()
    ceph_conf = RegistryPoint(filterable=True)
    ceph_config_show = RegistryPoint(multi_output=True)
    ceph_df_detail = RegistryPoint()
    ceph_health_detail = RegistryPoint()
    ceph_log = RegistryPoint(filterable=True)
    ceph_osd_df = RegistryPoint()
    ceph_osd_dump = RegistryPoint()
    ceph_osd_ec_profile_get = RegistryPoint(multi_output=True)
    ceph_osd_ec_profile_ls = RegistryPoint()
    ceph_osd_log = RegistryPoint(multi_output=True, filterable=True)
    ceph_osd_tree = RegistryPoint()
    ceph_s = RegistryPoint()
    ceph_v = RegistryPoint()
    certificates_enddate = RegistryPoint()
    chkconfig = RegistryPoint()
    chrony_conf = RegistryPoint()
    chronyc_sources = RegistryPoint()
    cib_xml = RegistryPoint()
    cinder_conf = RegistryPoint()
    cinder_volume_log = RegistryPoint(filterable=True)
    cluster_conf = RegistryPoint(filterable=True)
    cmdline = RegistryPoint()
    cobbler_modules_conf = RegistryPoint()
    cobbler_settings = RegistryPoint()
    corosync = RegistryPoint()
    cpe = RegistryPoint()
    cpu_cores = RegistryPoint(multi_output=True)
    cpu_siblings = RegistryPoint(multi_output=True)
    cpu_smt_active = RegistryPoint()
    cpu_smt_control = RegistryPoint()
    cpu_vulns = RegistryPoint(multi_output=True)
    cpu_vulns_meltdown = RegistryPoint()
    cpu_vulns_spectre_v1 = RegistryPoint()
    cpu_vulns_spectre_v2 = RegistryPoint()
    cpu_vulns_spec_store_bypass = RegistryPoint()
    cpuinfo_max_freq = RegistryPoint()
    cpuinfo = RegistryPoint()
    cpuset_cpus = RegistryPoint()
    crt = RegistryPoint()
    current_clocksource = RegistryPoint()
    date_iso = RegistryPoint()
    date = RegistryPoint()
    date_utc = RegistryPoint()
    dcbtool_gc_dcb = RegistryPoint(multi_output=True)
    df__alP = RegistryPoint()
    df__al = RegistryPoint()
    df__li = RegistryPoint()
    dig_dnssec = RegistryPoint()
    dig_edns = RegistryPoint()
    dig_noedns = RegistryPoint()
    dig = RegistryPoint()
    dirsrv = RegistryPoint()
    dirsrv_access = RegistryPoint(multi_output=True, filterable=True)
    dirsrv_errors = RegistryPoint(multi_output=True, filterable=True)
    display_java = RegistryPoint()
    dmesg = RegistryPoint(filterable=True)
    dmidecode = RegistryPoint()
    dmsetup_info = RegistryPoint()
    docker_container_inspect = RegistryPoint(multi_output=True)
    docker_host_machine_id = RegistryPoint()
    docker_image_inspect = RegistryPoint(multi_output=True)
    docker_info = RegistryPoint()
    docker_list_containers = RegistryPoint()
    docker_list_images = RegistryPoint()
    docker_network = RegistryPoint()
    docker_storage = RegistryPoint()
    docker_storage_setup = RegistryPoint()
    docker_sysconfig = RegistryPoint()
    dumpdev = RegistryPoint()
    dumpe2fs_h = RegistryPoint(multi_output=True)
    engine_config_all = RegistryPoint()
    engine_log = RegistryPoint(filterable=True)
    etc_journald_conf_d = RegistryPoint(multi_output=True)
    etc_journald_conf = RegistryPoint()
    ethernet_interfaces = RegistryPoint()
    ethtool_a = RegistryPoint(multi_output=True)
    ethtool_c = RegistryPoint(multi_output=True)
    ethtool_g = RegistryPoint(multi_output=True)
    ethtool_i = RegistryPoint(multi_output=True)
    ethtool_k = RegistryPoint(multi_output=True)
    ethtool = RegistryPoint(multi_output=True)
    ethtool_S = RegistryPoint(multi_output=True)
    exim_conf = RegistryPoint()
    facter = RegistryPoint()
    fc_match = RegistryPoint()
    fdisk_l = RegistryPoint()
    fdisk_l_sos = RegistryPoint(multi_output=True)
    foreman_production_log = RegistryPoint(filterable=True)
    foreman_proxy_conf = RegistryPoint()
    foreman_proxy_log = RegistryPoint(filterable=True)
    foreman_satellite_log = RegistryPoint(filterable=True)
    foreman_ssl_access_ssl_log = RegistryPoint(filterable=True)
    foreman_rake_db_migrate_status = RegistryPoint()
    foreman_tasks_config = RegistryPoint(filterable=True)
    fstab = RegistryPoint()
    galera_cnf = RegistryPoint()
    getcert_list = RegistryPoint()
    getenforce = RegistryPoint()
    getsebool = RegistryPoint()
    glance_api_conf = RegistryPoint()
    glance_api_log = RegistryPoint(filterable=True)
    glance_cache_conf = RegistryPoint()
    glance_registry_conf = RegistryPoint()
    gluster_v_info = RegistryPoint()
    gnocchi_conf = RegistryPoint(filterable=True)
    gnocchi_metricd_log = RegistryPoint(filterable=True)
    grub1_config_perms = RegistryPoint()
    grub2_cfg = RegistryPoint()
    grub2_efi_cfg = RegistryPoint()
    grub_config_perms = RegistryPoint()
    grub_conf = RegistryPoint()
    grub_efi_conf = RegistryPoint()
    grubby_default_index = RegistryPoint()
    hammer_ping = RegistryPoint()
    hammer_task_list = RegistryPoint()
    haproxy_cfg = RegistryPoint()
    heat_api_log = RegistryPoint(filterable=True)
    heat_conf = RegistryPoint()
    heat_crontab = RegistryPoint()
    heat_crontab_container = RegistryPoint()
    heat_engine_log = RegistryPoint(filterable=True)
    hostname = RegistryPoint()
    hosts = RegistryPoint()
    hponcfg_g = RegistryPoint()
    httpd_access_log = RegistryPoint(filterable=True)
    httpd_conf = RegistryPoint(multi_output=True)
    httpd_conf_sos = RegistryPoint(multi_output=True)
    httpd_conf_scl_httpd24 = RegistryPoint(multi_output=True)
    httpd_conf_scl_jbcs_httpd24 = RegistryPoint(multi_output=True)
    httpd_error_log = RegistryPoint(filterable=True)
    httpd_limits = RegistryPoint(multi_output=True)
    httpd_M = RegistryPoint(multi_output=True)
    httpd_pid = RegistryPoint()
    httpd_ssl_access_log = RegistryPoint(filterable=True)
    httpd_ssl_error_log = RegistryPoint(filterable=True)
    httpd_V = RegistryPoint(multi_output=True)
    virt_uuid_facts = RegistryPoint()
    ifcfg = RegistryPoint(multi_output=True)
    ifconfig = RegistryPoint()
    imagemagick_policy = RegistryPoint(multi_output=True, filterable=True)
    init_ora = RegistryPoint()
    initscript = RegistryPoint(multi_output=True)
    init_process_cgroup = RegistryPoint()
    installed_rpms = RegistryPoint()
    interrupts = RegistryPoint()
    ip6tables_permanent = RegistryPoint()
    ip6tables = RegistryPoint()
    ip_addr = RegistryPoint()
    ipaupgrade_log = RegistryPoint(filterable=True)
    ipcs_m = RegistryPoint()
    ipcs_m_p = RegistryPoint()
    ipcs_s = RegistryPoint()
    ipcs_s_i = RegistryPoint(multi_output=True)
    ip_route_show_table_all = RegistryPoint()
    ip_s_link = RegistryPoint()
    iptables_permanent = RegistryPoint()
    iptables = RegistryPoint()
    ipv4_neigh = RegistryPoint()
    ipv6_neigh = RegistryPoint()
    iscsiadm_m_session = RegistryPoint()
    jboss_domain_server_log = RegistryPoint(multi_output=True, filterable=True)
    jboss_standalone_server_log = RegistryPoint(multi_output=True, filterable=True)
    jboss_standalone_main_config = RegistryPoint(multi_output=True)
    jboss_version = RegistryPoint(multi_output=True)
    journal_since_boot = RegistryPoint(filterable=True)
    katello_service_status = RegistryPoint(filterable=True)
    kdump_conf = RegistryPoint()
    kdump = RegistryPoint()
    kerberos_kdc_log = RegistryPoint(filterable=True)
    kexec_crash_loaded = RegistryPoint()
    kexec_crash_size = RegistryPoint()
    keystone_conf = RegistryPoint()
    keystone_crontab = RegistryPoint()
    keystone_crontab_container = RegistryPoint()
    keystone_log = RegistryPoint(filterable=True)
    krb5 = RegistryPoint(multi_output=True)
    ksmstate = RegistryPoint()
    lastupload = RegistryPoint(multi_output=True)
    libkeyutils_objdumps = RegistryPoint()
    libkeyutils = RegistryPoint()
    libvirtd_log = RegistryPoint(filterable=True)
    limits_conf = RegistryPoint(multi_output=True)
    locale = RegistryPoint()
    localtime = RegistryPoint()
    logrotate_conf = RegistryPoint(multi_output=True)
    lpstat_p = RegistryPoint()
    lsblk_pairs = RegistryPoint()
    lsblk = RegistryPoint()
    ls_boot = RegistryPoint()
    lscpu = RegistryPoint()
    ls_dev = RegistryPoint()
    ls_disk = RegistryPoint()
    ls_docker_volumes = RegistryPoint()
    ls_etc = RegistryPoint()
    ls_ocp_cni_openshift_sdn = RegistryPoint()
    lsinitrd_lvm_conf = RegistryPoint()
    lsmod = RegistryPoint()
    lsof = RegistryPoint(filterable=True)
    lspci = RegistryPoint()
    lssap = RegistryPoint()
    lsscsi = RegistryPoint()
    ls_lib_firmware = RegistryPoint()
    ls_sys_firmware = RegistryPoint()
    ls_var_lib_mongodb = RegistryPoint()
    ls_var_lib_nova_instances = RegistryPoint()
    ls_usr_sbin = RegistryPoint(filterable=True)
    ls_var_log = RegistryPoint()
    ls_var_www = RegistryPoint()
    ls_var_spool_clientmq = RegistryPoint()
    ls_var_tmp = RegistryPoint(filterable=True)
    ls_var_run = RegistryPoint()
    ls_var_spool_postfix_maildrop = RegistryPoint()
    ls_osroot = RegistryPoint()
    lvdisplay = RegistryPoint()
    lvm_conf = RegistryPoint(filterable=True)
    lvs_noheadings = RegistryPoint()
    lvs_noheadings_all = RegistryPoint()
    lvs = RegistryPoint()
    machine_id = RegistryPoint()
    manila_conf = RegistryPoint()
    mariadb_log = RegistryPoint(filterable=True)
    md5chk_files = RegistryPoint()
    mdstat = RegistryPoint()
    meminfo = RegistryPoint()
    messages = RegistryPoint(filterable=True)
    metadata_json = RegistryPoint(raw=True)
    mlx4_port = RegistryPoint()
    modprobe = RegistryPoint(multi_output=True)
    module = RegistryPoint()
    mongod_conf = RegistryPoint(multi_output=True, filterable=True)
    mount = RegistryPoint()
    multicast_querier = RegistryPoint()
    multipath_conf = RegistryPoint()
    multipath_conf_initramfs = RegistryPoint()
    multipath__v4__ll = RegistryPoint()
    mysqladmin_vars = RegistryPoint()
    mysql_log = RegistryPoint(multi_output=True, filterable=True)
    mysqld_limits = RegistryPoint()
    named_checkconf_p = RegistryPoint(filterable=True)
    netconsole = RegistryPoint()
    netstat_agn = RegistryPoint()
    netstat_i = RegistryPoint()
    netstat = RegistryPoint()
    netstat_s = RegistryPoint()
    networkmanager_dispatcher_d = RegistryPoint(multi_output=True)
    neutron_conf = RegistryPoint(filterable=True)
    neutron_l3_agent_ini = RegistryPoint(filterable=True)
    neutron_l3_agent_log = RegistryPoint(filterable=True)
    neutron_metadata_agent_ini = RegistryPoint(filterable=True)
    neutron_metadata_agent_log = RegistryPoint(filterable=True)
    neutron_ovs_agent_log = RegistryPoint(filterable=True)
    neutron_plugin_ini = RegistryPoint()
    neutron_server_log = RegistryPoint(filterable=True)
    nfnetlink_queue = RegistryPoint()
    nfs_exports_d = RegistryPoint(multi_output=True)
    nfs_exports = RegistryPoint()
    nginx_conf = RegistryPoint(multi_output=True)
    nmcli_dev_show = RegistryPoint()
    nova_api_log = RegistryPoint(filterable=True)
    nova_compute_log = RegistryPoint(filterable=True)
    nova_conf = RegistryPoint()
    nova_crontab = RegistryPoint()
    nova_crontab_container = RegistryPoint()
    nscd_conf = RegistryPoint(filterable=True)
    nsswitch_conf = RegistryPoint(filterable=True)
    ntp_conf = RegistryPoint()
    ntpq_leap = RegistryPoint()
    ntpq_pn = RegistryPoint()
    ntptime = RegistryPoint()
    numeric_user_group_name = RegistryPoint()
    oc_get_bc = RegistryPoint()
    oc_get_build = RegistryPoint()
    oc_get_dc = RegistryPoint()
    oc_get_egressnetworkpolicy = RegistryPoint()
    oc_get_endpoints = RegistryPoint()
    oc_get_event = RegistryPoint()
    oc_get_node = RegistryPoint()
    oc_get_pod = RegistryPoint()
    oc_get_project = RegistryPoint()
    oc_get_pvc = RegistryPoint()
    oc_get_pv = RegistryPoint()
    oc_get_rc = RegistryPoint()
    oc_get_rolebinding = RegistryPoint()
    oc_get_role = RegistryPoint()
    oc_get_route = RegistryPoint()
    oc_get_service = RegistryPoint()
    oc_get_configmap = RegistryPoint()
    odbc_ini = RegistryPoint(filterable=True)
    odbcinst_ini = RegistryPoint()
    openvswitch_other_config = RegistryPoint()
    openvswitch_server_log = RegistryPoint(filterable=True)
    openshift_certificates = RegistryPoint(multi_output=True)
    openshift_hosts = RegistryPoint(filterable=True)
    openvswitch_daemon_log = RegistryPoint(filterable=True)
    openvswitch_server_log = RegistryPoint(filterable=True)
    osa_dispatcher_log = RegistryPoint(filterable=True)
    ose_master_config = RegistryPoint()
    ose_node_config = RegistryPoint()
    os_release = RegistryPoint()
    ovirt_engine_boot_log = RegistryPoint()
    ovirt_engine_confd = RegistryPoint(multi_output=True)
    ovirt_engine_console_log = RegistryPoint()
    ovirt_engine_server_log = RegistryPoint(filterable=True)
    ovirt_engine_ui_log = RegistryPoint()
    ovs_vsctl_show = RegistryPoint()
    pacemaker_log = RegistryPoint(filterable=True)
    package_provides_java = RegistryPoint(multi_output=True)
    pam_conf = RegistryPoint()
    parted__l = RegistryPoint()
    passenger_status = RegistryPoint()
    password_auth = RegistryPoint()
    pcs_config = RegistryPoint()
    pcs_status = RegistryPoint()
    pluginconf_d = RegistryPoint(multi_output=True)
    postgresql_conf = RegistryPoint()
    postgresql_log = RegistryPoint(multi_output=True, filterable=True)
    prelink_orig_md5 = RegistryPoint(multi_output=True)
    prev_uploader_log = RegistryPoint()
    proc_snmp_ipv4 = RegistryPoint()
    proc_snmp_ipv6 = RegistryPoint()
    ps_aux = RegistryPoint(filterable=True)
    ps_auxcww = RegistryPoint()
    ps_auxww = RegistryPoint(filterable=True)
    ps_ef = RegistryPoint(filterable=True)
    ps_eo = RegistryPoint()
    pulp_worker_defaults = RegistryPoint()
    puppet_ssl_cert_ca_pem = RegistryPoint()
    puppetserver_config = RegistryPoint(filterable=True)
    pvs_noheadings = RegistryPoint()
    pvs_noheadings_all = RegistryPoint()
    pvs = RegistryPoint()
    qemu_conf = RegistryPoint()
    qemu_xml = RegistryPoint(multi_output=True)
    qpid_stat_g = RegistryPoint()
    qpid_stat_q = RegistryPoint()
    qpid_stat_u = RegistryPoint()
    qpidd_conf = RegistryPoint()
    rabbitmq_logs = RegistryPoint(multi_output=True, filterable=True)
    rabbitmq_policies = RegistryPoint()
    rabbitmq_queues = RegistryPoint()
    rabbitmq_report = RegistryPoint()
    rabbitmq_startup_err = RegistryPoint(filterable=True)
    rabbitmq_startup_log = RegistryPoint(filterable=True)
    rabbitmq_users = RegistryPoint()
    rc_local = RegistryPoint()
    redhat_release = RegistryPoint()
    resolv_conf = RegistryPoint()
    rhv_log_collector_analyzer = RegistryPoint()
    rhn_charsets = RegistryPoint()
    rhn_conf = RegistryPoint()
    rhn_entitlement_cert_xml = RegistryPoint(multi_output=True)
    rhn_hibernate_conf = RegistryPoint()
    rhn_schema_stats = RegistryPoint()
    rhn_schema_version = RegistryPoint()
    rhn_search_daemon_log = RegistryPoint(filterable=True)
    rhn_server_satellite_log = RegistryPoint(filterable=True)
    rhn_server_xmlrpc_log = RegistryPoint(filterable=True)
    rhn_taskomatic_daemon_log = RegistryPoint(filterable=False)
    rhsm_conf = RegistryPoint()
    rhsm_log = RegistryPoint(filterable=True)
    root_crontab = RegistryPoint()
    route = RegistryPoint()
    rpm_V_packages = RegistryPoint()
    rsyslog_conf = RegistryPoint(filterable=True)
    running_java = RegistryPoint()
    samba = RegistryPoint(filterable=True)
    sap_hdb_version = RegistryPoint(multi_output=True)
    sap_host_profile = RegistryPoint(filterable=True)
    saphostctl_getcimobject_sapinstance = RegistryPoint(filterable=True)
    saphostexec_status = RegistryPoint()
    saphostexec_version = RegistryPoint()
    satellite_version_rb = RegistryPoint()
    scheduler = RegistryPoint(multi_output=True)
    scsi = RegistryPoint()
    scsi_eh_deadline = RegistryPoint(multi_output=True)
    scsi_fwver = RegistryPoint(multi_output=True)
    secure = RegistryPoint(filterable=True)
    selinux_config = RegistryPoint()
    semid = RegistryPoint()
    sestatus = RegistryPoint()
    smartctl = RegistryPoint(multi_output=True)
    smartpdc_settings = RegistryPoint(filterable=True)
    smbstatus_p = RegistryPoint()
    smbstatus_S = RegistryPoint()
    softnet_stat = RegistryPoint()
    software_collections_list = RegistryPoint()
    spfile_ora = RegistryPoint(multi_output=True)
    ssh_config = RegistryPoint()
    sshd_config_perms = RegistryPoint()
    sshd_config = RegistryPoint(filterable=True)
    ss = RegistryPoint()
    sssd_config = RegistryPoint()
    sssd_logs = RegistryPoint(multi_output=True, filterable=True)
    subscription_manager_list_consumed = RegistryPoint()
    subscription_manager_list_installed = RegistryPoint()
    subscription_manager_release_show = RegistryPoint()
    subscription_manager_repos_list_enabled = RegistryPoint()
    swift_object_expirer_conf = RegistryPoint()
    swift_proxy_server_conf = RegistryPoint()
    sysconfig_chronyd = RegistryPoint()
    sysconfig_httpd = RegistryPoint()
    sysconfig_irqbalance = RegistryPoint()
    sysconfig_kdump = RegistryPoint()
    sysconfig_libvirt_guests = RegistryPoint()
    sysconfig_memcached = RegistryPoint()
    sysconfig_mongod = RegistryPoint(multi_output=True)
    sysconfig_ntpd = RegistryPoint()
    sysconfig_prelink = RegistryPoint()
    sysconfig_virt_who = RegistryPoint()
    sysctl_conf_initramfs = RegistryPoint()
    sysctl_conf = RegistryPoint()
    sysctl = RegistryPoint()
    systemctl_cinder_volume = RegistryPoint()
    systemctl_httpd = RegistryPoint()
    systemctl_list_unit_files = RegistryPoint()
    systemctl_list_units = RegistryPoint()
    systemctl_mariadb = RegistryPoint()
    systemctl_pulp_workers = RegistryPoint()
    systemctl_pulp_resmg = RegistryPoint()
    systemctl_pulp_celerybeat = RegistryPoint()
    systemctl_qpidd = RegistryPoint()
    systemctl_qdrouterd = RegistryPoint()
    systemctl_smartpdc = RegistryPoint()
    systemd_docker = RegistryPoint()
    systemd_logind_conf = RegistryPoint()
    systemd_openshift_node = RegistryPoint()
    systemd_system_conf = RegistryPoint()
    systemid = RegistryPoint()
    systool_b_scsi_v = RegistryPoint()
    teamdctl_state_dump = RegistryPoint(multi_output=True)
    thp_enabled = RegistryPoint()
    thp_use_zero_page = RegistryPoint()
    tmpfilesd = RegistryPoint(multi_output=True)
    tomcat_server_xml = RegistryPoint(multi_output=True)
    tomcat_vdc_fallback = RegistryPoint()
    tomcat_vdc_targeted = RegistryPoint(multi_output=True)
    tomcat_web_xml = RegistryPoint(multi_output=True)
    tuned_adm = RegistryPoint()
    udev_persistent_net_rules = RegistryPoint()
    uname = RegistryPoint()
    up2date = RegistryPoint()
    up2date_log = RegistryPoint(filterable=True)
    uploader_log = RegistryPoint()
    uptime = RegistryPoint()
    usr_journald_conf_d = RegistryPoint(multi_output=True)
    vdsm_conf = RegistryPoint()
    vdsm_id = RegistryPoint()
    vdsm_log = RegistryPoint(filterable=True)
    vdsm_logger_conf = RegistryPoint()
    vgdisplay = RegistryPoint()
    vgs_noheadings = RegistryPoint()
    vgs_noheadings_all = RegistryPoint()
    vgs = RegistryPoint()
    virsh_list_all = RegistryPoint()
    virt_what = RegistryPoint()
    virt_who_conf = RegistryPoint(multi_output=True, filterable=True)
    virtlogd_conf = RegistryPoint(filterable=True)
    vmcore_dmesg = RegistryPoint(multi_output=True)
    vmware_tools_conf = RegistryPoint()
    vsftpd_conf = RegistryPoint(filterable=True)
    vsftpd = RegistryPoint()
    woopsie = RegistryPoint()
    x86_pti_enabled = RegistryPoint()
    x86_ibpb_enabled = RegistryPoint()
    x86_ibrs_enabled = RegistryPoint()
    x86_retp_enabled = RegistryPoint()
    xfs_info = RegistryPoint(multi_output=True)
    xinetd_conf = RegistryPoint(multi_output=True)
    yum_conf = RegistryPoint()
    yum_log = RegistryPoint()
    yum_repolist = RegistryPoint()
    yum_repos_d = RegistryPoint(multi_output=True)
    zipl_conf = RegistryPoint()
