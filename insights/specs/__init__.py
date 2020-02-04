from insights.core.spec_factory import SpecSet, RegistryPoint


class Openshift(SpecSet):
    cluster_operators = RegistryPoint(raw=True)
    crds = RegistryPoint(raw=True)
    crs = RegistryPoint(raw=True, multi_output=True)
    machine_configs = RegistryPoint(raw=True)
    machines = RegistryPoint(raw=True)
    machine_id = RegistryPoint(raw=True)  # stand in for system id
    namespaces = RegistryPoint(raw=True)
    nodes = RegistryPoint(raw=True)
    pods = RegistryPoint(raw=True)
    pvcs = RegistryPoint(raw=True)
    storage_classes = RegistryPoint(raw=True)


class Specs(SpecSet):
    abrt_status_bare = RegistryPoint()
    amq_broker = RegistryPoint(multi_output=True)
    auditctl_status = RegistryPoint()
    auditd_conf = RegistryPoint()
    audit_log = RegistryPoint(filterable=True)
    autofs_conf = RegistryPoint()
    avc_hash_stats = RegistryPoint()
    avc_cache_threshold = RegistryPoint()
    aws_instance_id_doc = RegistryPoint()
    aws_instance_id_pkcs7 = RegistryPoint()
    aws_instance_type = RegistryPoint()
    azure_instance_type = RegistryPoint()
    bios_uuid = RegistryPoint()
    blkid = RegistryPoint()
    bond = RegistryPoint(multi_output=True)
    bond_dynamic_lb = RegistryPoint(multi_output=True)
    boot_loader_entries = RegistryPoint(multi_output=True)
    branch_info = RegistryPoint()
    brctl_show = RegistryPoint()
    candlepin_error_log = RegistryPoint(filterable=True)
    candlepin_log = RegistryPoint(filterable=True)
    cdc_wdm = RegistryPoint()
    checkin_conf = RegistryPoint()
    catalina_out = RegistryPoint(multi_output=True, filterable=True)
    catalina_server_log = RegistryPoint(multi_output=True, filterable=True)
    cciss = RegistryPoint(multi_output=True)
    ceilometer_central_log = RegistryPoint(filterable=True)
    ceilometer_collector_log = RegistryPoint(filterable=True)
    ceilometer_compute_log = RegistryPoint(filterable=True)
    ceilometer_conf = RegistryPoint()
    ceph_conf = RegistryPoint(filterable=True)
    ceph_config_show = RegistryPoint(multi_output=True)
    ceph_df_detail = RegistryPoint()
    ceph_health_detail = RegistryPoint()
    ceph_insights = RegistryPoint()
    ceph_log = RegistryPoint(multi_output=True, filterable=True)
    ceph_osd_df = RegistryPoint()
    ceph_osd_dump = RegistryPoint()
    ceph_osd_ec_profile_get = RegistryPoint(multi_output=True)
    ceph_osd_ec_profile_ls = RegistryPoint()
    ceph_osd_log = RegistryPoint(multi_output=True, filterable=True)
    ceph_osd_tree = RegistryPoint()
    ceph_osd_tree_text = RegistryPoint()
    ceph_report = RegistryPoint()
    ceph_s = RegistryPoint()
    ceph_v = RegistryPoint()
    certificates_enddate = RegistryPoint()
    cgroups = RegistryPoint()
    chkconfig = RegistryPoint()
    chrony_conf = RegistryPoint()
    chronyc_sources = RegistryPoint()
    cib_xml = RegistryPoint()
    cinder_api_log = RegistryPoint(filterable=True)
    cinder_conf = RegistryPoint()
    cinder_volume_log = RegistryPoint(filterable=True)
    cloud_init_custom_network = RegistryPoint()
    cloud_init_log = RegistryPoint(filterable=True)
    cluster_conf = RegistryPoint(filterable=True)
    cmdline = RegistryPoint()
    cobbler_modules_conf = RegistryPoint()
    cobbler_settings = RegistryPoint()
    corosync = RegistryPoint()
    corosync_conf = RegistryPoint()
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
    cpupower_frequency_info = RegistryPoint()
    cpuset_cpus = RegistryPoint()
    crypto_policies_config = RegistryPoint()
    crypto_policies_state_current = RegistryPoint()
    crypto_policies_opensshserver = RegistryPoint()
    crypto_policies_bind = RegistryPoint()
    crt = RegistryPoint()
    current_clocksource = RegistryPoint()
    date_iso = RegistryPoint()
    date = RegistryPoint()
    date_utc = RegistryPoint()
    db2licm_l = RegistryPoint()
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
    display_name = RegistryPoint()
    dmesg = RegistryPoint(filterable=True)
    dmesg_log = RegistryPoint(filterable=True)
    dmidecode = RegistryPoint()
    dmsetup_info = RegistryPoint()
    dnf_modules = RegistryPoint()
    dnf_module_list = RegistryPoint()
    dnf_module_info = RegistryPoint()
    dnsmasq_config = RegistryPoint(multi_output=True)
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
    dse_ldif = RegistryPoint(filterable=True)
    dumpe2fs_h = RegistryPoint(multi_output=True)
    engine_config_all = RegistryPoint()
    engine_log = RegistryPoint(filterable=True)
    etc_journald_conf_d = RegistryPoint(multi_output=True)
    etc_journald_conf = RegistryPoint()
    etc_machine_id = RegistryPoint()
    etcd_conf = RegistryPoint(filterable=True)
    ethernet_interfaces = RegistryPoint()
    ethtool_a = RegistryPoint(multi_output=True)
    ethtool_c = RegistryPoint(multi_output=True)
    ethtool_g = RegistryPoint(multi_output=True)
    ethtool_i = RegistryPoint(multi_output=True)
    ethtool_k = RegistryPoint(multi_output=True)
    ethtool = RegistryPoint(multi_output=True)
    ethtool_S = RegistryPoint(multi_output=True)
    ethtool_T = RegistryPoint(multi_output=True)
    exim_conf = RegistryPoint()
    facter = RegistryPoint()
    fc_match = RegistryPoint()
    fcoeadm_i = RegistryPoint()
    fdisk_l = RegistryPoint()
    fdisk_l_sos = RegistryPoint(multi_output=True)
    findmnt_lo_propagation = RegistryPoint()
    firewall_cmd_list_all_zones = RegistryPoint()
    firewalld_conf = RegistryPoint(filterable=True)
    foreman_production_log = RegistryPoint(filterable=True)
    foreman_proxy_conf = RegistryPoint()
    foreman_proxy_log = RegistryPoint(filterable=True)
    foreman_satellite_log = RegistryPoint(filterable=True)
    foreman_ssl_access_ssl_log = RegistryPoint(filterable=True)
    foreman_rake_db_migrate_status = RegistryPoint()
    foreman_tasks_config = RegistryPoint(filterable=True)
    freeipa_healthcheck_log = RegistryPoint()
    fstab = RegistryPoint()
    galera_cnf = RegistryPoint()
    getcert_list = RegistryPoint()
    getconf_page_size = RegistryPoint()
    getenforce = RegistryPoint()
    getsebool = RegistryPoint()
    glance_api_conf = RegistryPoint()
    glance_api_log = RegistryPoint(filterable=True)
    glance_cache_conf = RegistryPoint()
    glance_registry_conf = RegistryPoint()
    gluster_v_info = RegistryPoint()
    gluster_v_status = RegistryPoint()
    gluster_peer_status = RegistryPoint()
    gnocchi_conf = RegistryPoint(filterable=True)
    gnocchi_metricd_log = RegistryPoint(filterable=True)
    grub_conf = RegistryPoint()
    grub_config_perms = RegistryPoint()
    grub_efi_conf = RegistryPoint()
    grub1_config_perms = RegistryPoint()
    grub2_cfg = RegistryPoint()
    grub2_efi_cfg = RegistryPoint()
    grubby_default_index = RegistryPoint()
    grubby_default_kernel = RegistryPoint()
    hammer_ping = RegistryPoint()
    hammer_task_list = RegistryPoint()
    satellite_enabled_features = RegistryPoint()
    haproxy_cfg = RegistryPoint()
    heat_api_log = RegistryPoint(filterable=True)
    heat_conf = RegistryPoint()
    heat_crontab = RegistryPoint()
    heat_crontab_container = RegistryPoint()
    heat_engine_log = RegistryPoint(filterable=True)
    hostname = RegistryPoint()
    hostname_default = RegistryPoint()
    hostname_short = RegistryPoint()
    hosts = RegistryPoint()
    hponcfg_g = RegistryPoint()
    httpd_access_log = RegistryPoint(filterable=True)
    httpd_conf = RegistryPoint(multi_output=True)
    httpd_conf_sos = RegistryPoint(multi_output=True)
    httpd_conf_scl_httpd24 = RegistryPoint(multi_output=True)
    httpd_conf_scl_jbcs_httpd24 = RegistryPoint(multi_output=True)
    httpd_error_log = RegistryPoint(filterable=True)
    httpd24_httpd_error_log = RegistryPoint(filterable=True)
    jbcs_httpd24_httpd_error_log = RegistryPoint(filterable=True)
    httpd_limits = RegistryPoint(multi_output=True)
    httpd_M = RegistryPoint(multi_output=True)
    httpd_on_nfs = RegistryPoint()
    httpd_pid = RegistryPoint()
    httpd_ssl_access_log = RegistryPoint(filterable=True)
    httpd_ssl_error_log = RegistryPoint(filterable=True)
    httpd_V = RegistryPoint(multi_output=True)
    virt_uuid_facts = RegistryPoint()
    ifcfg = RegistryPoint(multi_output=True)
    ifcfg_static_route = RegistryPoint(multi_output=True)
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
    ip_addresses = RegistryPoint()
    ipaupgrade_log = RegistryPoint(filterable=True)
    ipcs_m = RegistryPoint()
    ipcs_m_p = RegistryPoint()
    ipcs_s = RegistryPoint()
    ipcs_s_i = RegistryPoint(multi_output=True)
    ip_netns_exec_namespace_lsof = RegistryPoint(multi_output=True, filterable=True)
    ip_route_show_table_all = RegistryPoint()
    ip_s_link = RegistryPoint()
    iptables_permanent = RegistryPoint()
    iptables = RegistryPoint()
    ipv4_neigh = RegistryPoint()
    ipv6_neigh = RegistryPoint()
    ip_neigh_show = RegistryPoint()
    ironic_conf = RegistryPoint(filterable=True)
    ironic_inspector_log = RegistryPoint(filterable=True)
    iscsiadm_m_session = RegistryPoint()
    jboss_domain_server_log = RegistryPoint(multi_output=True, filterable=True)
    jboss_standalone_server_log = RegistryPoint(multi_output=True, filterable=True)
    jboss_standalone_main_config = RegistryPoint(multi_output=True)
    jboss_version = RegistryPoint(multi_output=True)
    journal_since_boot = RegistryPoint(filterable=True)
    katello_service_status = RegistryPoint(filterable=True)
    kdump_conf = RegistryPoint()
    kerberos_kdc_log = RegistryPoint(filterable=True)
    kernel_config = RegistryPoint(multi_output=True, filterable=True)
    kexec_crash_loaded = RegistryPoint()
    kexec_crash_size = RegistryPoint()
    keystone_conf = RegistryPoint()
    keystone_crontab = RegistryPoint()
    keystone_crontab_container = RegistryPoint()
    keystone_log = RegistryPoint(filterable=True)
    kpatch_list = RegistryPoint()
    krb5 = RegistryPoint(multi_output=True)
    ksmstate = RegistryPoint()
    kubepods_cpu_quota = RegistryPoint(multi_output=True)
    lastupload = RegistryPoint(multi_output=True)
    libkeyutils_objdumps = RegistryPoint()
    libkeyutils = RegistryPoint()
    libvirtd_log = RegistryPoint(filterable=True)
    libvirtd_qemu_log = RegistryPoint(multi_output=True, filterable=True)
    limits_conf = RegistryPoint(multi_output=True)
    locale = RegistryPoint()
    localtime = RegistryPoint()
    logrotate_conf = RegistryPoint(multi_output=True)
    lpstat_p = RegistryPoint()
    ls_boot = RegistryPoint()
    ls_dev = RegistryPoint()
    ls_disk = RegistryPoint()
    ls_docker_volumes = RegistryPoint()
    ls_edac_mc = RegistryPoint()
    ls_etc = RegistryPoint()
    ls_lib_firmware = RegistryPoint()
    ls_ocp_cni_openshift_sdn = RegistryPoint()
    ls_origin_local_volumes_pods = RegistryPoint()
    ls_osroot = RegistryPoint()
    ls_run_systemd_generator = RegistryPoint()
    ls_R_var_lib_nova_instances = RegistryPoint()
    ls_sys_firmware = RegistryPoint()
    ls_usr_lib64 = RegistryPoint(filterable=True)
    ls_usr_sbin = RegistryPoint(filterable=True)
    ls_var_lib_mongodb = RegistryPoint()
    ls_var_lib_nova_instances = RegistryPoint()
    ls_var_log = RegistryPoint()
    ls_var_opt_mssql = RegistryPoint()
    ls_var_opt_mssql_log = RegistryPoint()
    ls_var_run = RegistryPoint()
    ls_var_spool_clientmq = RegistryPoint()
    ls_var_spool_postfix_maildrop = RegistryPoint()
    ls_var_tmp = RegistryPoint(filterable=True)
    ls_var_www = RegistryPoint()
    lsblk = RegistryPoint()
    lsblk_pairs = RegistryPoint()
    lscpu = RegistryPoint()
    lsinitrd = RegistryPoint(filterable=True)
    lsinitrd_lvm_conf = RegistryPoint()
    lsmod = RegistryPoint()
    lsof = RegistryPoint(filterable=True)
    lspci = RegistryPoint()
    lssap = RegistryPoint()
    lsscsi = RegistryPoint()
    lvdisplay = RegistryPoint()
    lvm_conf = RegistryPoint(filterable=True)
    lvs_noheadings = RegistryPoint()
    lvs_noheadings_all = RegistryPoint()
    lvs = RegistryPoint()
    mac_addresses = RegistryPoint(multi_output=True)
    machine_id = RegistryPoint()
    manila_conf = RegistryPoint()
    mariadb_log = RegistryPoint(filterable=True)
    max_uid = RegistryPoint()
    md5chk_files = RegistryPoint(multi_output=True)
    mdstat = RegistryPoint()
    meminfo = RegistryPoint()
    messages = RegistryPoint(filterable=True)
    metadata_json = RegistryPoint(raw=True)
    mistral_executor_log = RegistryPoint(filterable=True)
    mlx4_port = RegistryPoint(multi_output=True)
    modinfo_i40e = RegistryPoint()
    modinfo_igb = RegistryPoint()
    modinfo_ixgbe = RegistryPoint()
    modinfo_veth = RegistryPoint()
    modinfo_vmxnet3 = RegistryPoint()
    modinfo = RegistryPoint(multi_output=True)
    modinfo_all = RegistryPoint()
    modprobe = RegistryPoint(multi_output=True)
    module = RegistryPoint()
    mongod_conf = RegistryPoint(multi_output=True, filterable=True)
    mount = RegistryPoint()
    mounts = RegistryPoint()
    mssql_conf = RegistryPoint()
    multicast_querier = RegistryPoint()
    multipath_conf = RegistryPoint()
    multipath_conf_initramfs = RegistryPoint()
    multipath__v4__ll = RegistryPoint()
    mysqladmin_status = RegistryPoint()
    mysqladmin_vars = RegistryPoint()
    mysql_log = RegistryPoint(multi_output=True, filterable=True)
    mysqld_limits = RegistryPoint()
    named_checkconf_p = RegistryPoint(filterable=True)
    namespace = RegistryPoint()
    netconsole = RegistryPoint()
    netstat_agn = RegistryPoint()
    netstat_i = RegistryPoint()
    netstat = RegistryPoint()
    netstat_s = RegistryPoint()
    networkmanager_dispatcher_d = RegistryPoint(multi_output=True)
    neutron_conf = RegistryPoint(filterable=True)
    neutron_dhcp_agent_ini = RegistryPoint(filterable=True)
    neutron_l3_agent_ini = RegistryPoint(filterable=True)
    neutron_l3_agent_log = RegistryPoint(filterable=True)
    neutron_metadata_agent_ini = RegistryPoint(filterable=True)
    neutron_metadata_agent_log = RegistryPoint(filterable=True)
    neutron_ml2_conf = RegistryPoint(filterable=True)
    neutron_ovs_agent_log = RegistryPoint(filterable=True)
    neutron_plugin_ini = RegistryPoint()
    neutron_server_log = RegistryPoint(filterable=True)
    nfnetlink_queue = RegistryPoint()
    nfs_exports_d = RegistryPoint(multi_output=True)
    nfs_exports = RegistryPoint()
    nginx_conf = RegistryPoint(multi_output=True)
    nmcli_conn_show = RegistryPoint()
    nmcli_dev_show = RegistryPoint()
    nmcli_dev_show_sos = RegistryPoint(multi_output=True)
    nova_api_log = RegistryPoint(filterable=True)
    nova_compute_log = RegistryPoint(filterable=True)
    nova_conf = RegistryPoint()
    nova_crontab = RegistryPoint()
    nova_crontab_container = RegistryPoint()
    nova_uid = RegistryPoint()
    nova_migration_uid = RegistryPoint()
    nscd_conf = RegistryPoint(filterable=True)
    nsswitch_conf = RegistryPoint(filterable=True)
    ntp_conf = RegistryPoint()
    ntpq_leap = RegistryPoint()
    ntpq_pn = RegistryPoint()
    ntptime = RegistryPoint()
    numa_cpus = RegistryPoint(multi_output=True)
    numeric_user_group_name = RegistryPoint()
    nvme_core_io_timeout = RegistryPoint()
    oc_get_bc = RegistryPoint()
    oc_get_build = RegistryPoint()
    oc_get_clusterrole_with_config = RegistryPoint()
    oc_get_clusterrolebinding_with_config = RegistryPoint()
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
    octavia_conf = RegistryPoint(filterable=True)
    odbc_ini = RegistryPoint(filterable=True)
    odbcinst_ini = RegistryPoint()
    openvswitch_other_config = RegistryPoint()
    openvswitch_server_log = RegistryPoint(filterable=True)
    openshift_certificates = RegistryPoint(multi_output=True)
    openshift_fluentd_environ = RegistryPoint(multi_output=True)
    openshift_hosts = RegistryPoint(filterable=True)
    openshift_router_environ = RegistryPoint(multi_output=True)
    openvswitch_daemon_log = RegistryPoint(filterable=True)
    openvswitch_server_log = RegistryPoint(filterable=True)
    osa_dispatcher_log = RegistryPoint(filterable=True)
    ose_master_config = RegistryPoint()
    ose_node_config = RegistryPoint()
    os_release = RegistryPoint()
    ovirt_engine_boot_log = RegistryPoint(filterable=True)
    ovirt_engine_confd = RegistryPoint(multi_output=True)
    ovirt_engine_console_log = RegistryPoint(filterable=True)
    ovirt_engine_server_log = RegistryPoint(filterable=True)
    ovirt_engine_ui_log = RegistryPoint(filterable=True)
    ovs_appctl_fdb_show_bridge = RegistryPoint(multi_output=True)
    ovs_ofctl_dump_flows = RegistryPoint(multi_output=True)
    ovs_vsctl_list_bridge = RegistryPoint()
    ovs_vsctl_show = RegistryPoint()
    ovs_vswitchd_limits = RegistryPoint()
    pacemaker_log = RegistryPoint(filterable=True)
    package_provides_java = RegistryPoint(multi_output=True)
    package_provides_httpd = RegistryPoint(multi_output=True)
    pam_conf = RegistryPoint()
    parted__l = RegistryPoint()
    partitions = RegistryPoint()
    passenger_status = RegistryPoint()
    password_auth = RegistryPoint()
    pci_rport_target_disk_paths = RegistryPoint()
    pcs_config = RegistryPoint()
    pcs_quorum_status = RegistryPoint()
    pcs_status = RegistryPoint()
    pluginconf_d = RegistryPoint(multi_output=True)
    podman_container_inspect = RegistryPoint(multi_output=True)
    podman_image_inspect = RegistryPoint(multi_output=True)
    podman_list_containers = RegistryPoint()
    podman_list_images = RegistryPoint()
    postgresql_conf = RegistryPoint()
    postgresql_log = RegistryPoint(multi_output=True, filterable=True)
    prev_uploader_log = RegistryPoint()
    proc_netstat = RegistryPoint()
    proc_slabinfo = RegistryPoint()
    proc_snmp_ipv4 = RegistryPoint()
    proc_snmp_ipv6 = RegistryPoint()
    proc_stat = RegistryPoint()
    ps_alxwww = RegistryPoint(filterable=True)
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
    rabbitmq_env = RegistryPoint()
    rabbitmq_logs = RegistryPoint(multi_output=True, filterable=True)
    rabbitmq_policies = RegistryPoint()
    rabbitmq_queues = RegistryPoint()
    rabbitmq_report = RegistryPoint()
    rabbitmq_report_of_containers = RegistryPoint(multi_output=True)
    rabbitmq_startup_err = RegistryPoint(filterable=True)
    rabbitmq_startup_log = RegistryPoint(filterable=True)
    rabbitmq_users = RegistryPoint()
    rc_local = RegistryPoint()
    rdma_conf = RegistryPoint()
    readlink_e_etc_mtab = RegistryPoint()
    readlink_e_shift_cert_client = RegistryPoint()
    readlink_e_shift_cert_server = RegistryPoint()
    redhat_release = RegistryPoint()
    resolv_conf = RegistryPoint()
    rhev_data_center = RegistryPoint()
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
    rhosp_release = RegistryPoint()
    rhsm_conf = RegistryPoint()
    rhsm_log = RegistryPoint(filterable=True)
    rhsm_releasever = RegistryPoint()
    rndc_status = RegistryPoint()
    root_crontab = RegistryPoint()
    route = RegistryPoint()
    rpm_V_packages = RegistryPoint()
    rsyslog_conf = RegistryPoint(filterable=True)
    running_java = RegistryPoint()
    samba = RegistryPoint(filterable=True)
    sap_hdb_version = RegistryPoint(multi_output=True)
    sap_host_profile = RegistryPoint(filterable=True)
    sapcontrol_getsystemupdatelist = RegistryPoint()
    saphostctl_getcimobject_sapinstance = RegistryPoint(filterable=True)
    saphostexec_status = RegistryPoint()
    saphostexec_version = RegistryPoint()
    sat5_insights_properties = RegistryPoint()
    satellite_mongodb_storage_engine = RegistryPoint()
    satellite_version_rb = RegistryPoint()
    satellite_custom_hiera = RegistryPoint()
    scheduler = RegistryPoint(multi_output=True)
    sched_rt_runtime_us = RegistryPoint()
    scsi = RegistryPoint()
    sctp_asc = RegistryPoint()
    sctp_eps = RegistryPoint()
    sctp_snmp = RegistryPoint()
    scsi_eh_deadline = RegistryPoint(multi_output=True)
    scsi_fwver = RegistryPoint(multi_output=True)
    sealert = RegistryPoint()
    secure = RegistryPoint(filterable=True)
    selinux_config = RegistryPoint()
    semid = RegistryPoint()
    sestatus = RegistryPoint()
    setup_named_chroot = RegistryPoint(filterable=True)
    smartctl = RegistryPoint(multi_output=True)
    smartpdc_settings = RegistryPoint(filterable=True)
    smbstatus_p = RegistryPoint()
    smbstatus_S = RegistryPoint()
    sockstat = RegistryPoint()
    softnet_stat = RegistryPoint()
    software_collections_list = RegistryPoint()
    spfile_ora = RegistryPoint(multi_output=True)
    ssh_config = RegistryPoint(filterable=True)
    ssh_foreman_config = RegistryPoint(filterable=True)
    ssh_foreman_proxy_config = RegistryPoint(filterable=True)
    sshd_config_perms = RegistryPoint()
    sshd_config = RegistryPoint(filterable=True)
    ss = RegistryPoint()
    sssd_config = RegistryPoint()
    sssd_logs = RegistryPoint(multi_output=True, filterable=True)
    samba_logs = RegistryPoint(multi_output=True, filterable=True)
    subscription_manager_id = RegistryPoint()
    subscription_manager_list_consumed = RegistryPoint()
    subscription_manager_list_installed = RegistryPoint()
    subscription_manager_installed_product_ids = RegistryPoint(filterable=True)
    subscription_manager_release_show = RegistryPoint()
    swift_conf = RegistryPoint()
    swift_log = RegistryPoint(filterable=True)
    swift_object_expirer_conf = RegistryPoint()
    swift_proxy_server_conf = RegistryPoint()
    sys_kernel_sched_features = RegistryPoint()
    sysconfig_chronyd = RegistryPoint()
    sysconfig_httpd = RegistryPoint()
    sysconfig_irqbalance = RegistryPoint()
    sysconfig_kdump = RegistryPoint()
    sysconfig_libvirt_guests = RegistryPoint()
    sysconfig_memcached = RegistryPoint()
    sysconfig_mongod = RegistryPoint(multi_output=True)
    sysconfig_network = RegistryPoint()
    sysconfig_ntpd = RegistryPoint()
    sysconfig_prelink = RegistryPoint()
    sysconfig_sshd = RegistryPoint()
    sysconfig_virt_who = RegistryPoint()
    sysctl_conf_initramfs = RegistryPoint(multi_output=True)
    sysctl_conf = RegistryPoint()
    sysctl = RegistryPoint()
    systemctl_cat_rpcbind_socket = RegistryPoint()
    systemctl_cinder_volume = RegistryPoint()
    systemctl_httpd = RegistryPoint()
    systemctl_nginx = RegistryPoint()
    systemctl_list_unit_files = RegistryPoint()
    systemctl_list_units = RegistryPoint()
    systemctl_mariadb = RegistryPoint()
    systemctl_pulp_workers = RegistryPoint()
    systemctl_pulp_resmg = RegistryPoint()
    systemctl_pulp_celerybeat = RegistryPoint()
    systemctl_qpidd = RegistryPoint()
    systemctl_qdrouterd = RegistryPoint()
    systemctl_show_all_services = RegistryPoint()
    systemctl_show_target = RegistryPoint()
    systemctl_smartpdc = RegistryPoint()
    systemd_docker = RegistryPoint()
    systemd_logind_conf = RegistryPoint()
    systemd_openshift_node = RegistryPoint()
    systemd_system_conf = RegistryPoint()
    systemd_system_origin_accounting = RegistryPoint()
    systemid = RegistryPoint()
    systool_b_scsi_v = RegistryPoint()
    tags = RegistryPoint()
    teamdctl_config_dump = RegistryPoint(multi_output=True)
    teamdctl_state_dump = RegistryPoint(multi_output=True)
    thp_enabled = RegistryPoint()
    thp_use_zero_page = RegistryPoint()
    tmpfilesd = RegistryPoint(multi_output=True)
    tomcat_server_xml = RegistryPoint(multi_output=True)
    tomcat_vdc_fallback = RegistryPoint()
    tomcat_vdc_targeted = RegistryPoint(multi_output=True)
    tomcat_web_xml = RegistryPoint(multi_output=True)
    tuned_adm = RegistryPoint()
    tuned_conf = RegistryPoint()
    udev_persistent_net_rules = RegistryPoint()
    udev_fc_wwpn_id_rules = RegistryPoint(filterable=True)
    uname = RegistryPoint()
    up2date = RegistryPoint()
    up2date_log = RegistryPoint(filterable=True)
    uploader_log = RegistryPoint()
    uptime = RegistryPoint()
    usr_journald_conf_d = RegistryPoint(multi_output=True)
    var_qemu_xml = RegistryPoint(multi_output=True)
    vdsm_conf = RegistryPoint()
    vdsm_id = RegistryPoint()
    vdsm_import_log = RegistryPoint(multi_output=True, filterable=True)
    vdsm_log = RegistryPoint(filterable=True)
    vdsm_logger_conf = RegistryPoint()
    version_info = RegistryPoint()
    vdo_status = RegistryPoint()
    vgdisplay = RegistryPoint()
    vgs_noheadings = RegistryPoint()
    vgs_noheadings_all = RegistryPoint()
    vgs = RegistryPoint()
    virsh_list_all = RegistryPoint()
    virt_what = RegistryPoint()
    virt_who_conf = RegistryPoint(multi_output=True, filterable=True)
    virtlogd_conf = RegistryPoint(filterable=True)
    vma_ra_enabled = RegistryPoint()
    vmcore_dmesg = RegistryPoint(multi_output=True, filterable=True)
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
    yum_list_installed = RegistryPoint()
    yum_log = RegistryPoint()
    yum_repolist = RegistryPoint()
    yum_repos_d = RegistryPoint(multi_output=True)
    zdump_v = RegistryPoint()
    zipl_conf = RegistryPoint()
