.. _custom-datasources:

Custom Datasources Catalog
==========================

insights.specs.datasources
--------------------------

.. automodule:: insights.specs.datasources
    :members:
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.aws
------------------------------

.. automodule:: insights.specs.datasources.aws
    :members: aws_imdsv2_token, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.awx_manage
-------------------------------------

.. automodule:: insights.specs.datasources.awx_manage
    :members: check_license_data, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.candlepin
------------------------------------

.. automodule:: insights.specs.datasources.candlepin
    :members: candlepin_broker, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.client_metadata
------------------------------------------

.. automodule:: insights.specs.datasources.client_metadata
    :members: ansible_host, basic_auth_insights_client, blacklist_report, blacklisted_specs, branch_info, display_name, egg_release, tags, version_info,
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.cloud_init
-------------------------------------

.. automodule:: insights.specs.datasources.cloud_init
    :members: cloud_cfg, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.compliance.compliance_ds
---------------------------------------------------

.. automodule:: insights.specs.datasources.compliance.compliance_ds
    :members: compliance_enabled, compliance_policies_enabled, compliance_assign_enabled, compliance_unassign_enabled, os_version, package_check, compliance, compliance_policies, compliance_assign, compliance_unassign, compliance_advisor_rule_enabled
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.container
------------------------------------

.. automodule:: insights.specs.datasources.container
    :members: running_rhel_containers
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.container.containers_inspect
-------------------------------------------------------

.. automodule:: insights.specs.datasources.container.containers_inspect
    :members: running_rhel_containers_id, containers_inspect_data_datasource
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.container.nginx_conf
-----------------------------------------------

.. automodule:: insights.specs.datasources.container.nginx_conf
    :members: nginx_conf, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.corosync
-----------------------------------

.. automodule:: insights.specs.datasources.corosync
    :members:  corosync_cmapctl_cmds
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.du
-----------------------------

.. automodule:: insights.specs.datasources.du
    :members: du_dir_list
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.env
------------------------------

.. automodule:: insights.specs.datasources.env
    :members: ld_library_path_global_conf
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.ethernet
-----------------------------------

.. automodule:: insights.specs.datasources.ethernet
    :members: interfaces, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.httpd
--------------------------------

.. automodule:: insights.specs.datasources.httpd
    :members: httpd_cmds, httpd_on_nfs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.intersystems
---------------------------------------

.. automodule:: insights.specs.datasources.intersystems
    :members: iris_working_configuration, iris_working_messages_log
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.ipcs
-------------------------------

.. automodule:: insights.specs.datasources.ipcs
    :members: semid
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.kernel
---------------------------------

.. automodule:: insights.specs.datasources.kernel
    :members:  current_version, default_version, kernel_module_filters
    :show-inheritance:
    :undoc-members:

    :show-inheritance:
    :undoc-members:

insights.specs.datasources.leapp
--------------------------------

.. automodule:: insights.specs.datasources.leapp
    :members: leapp_report
    :show-inheritance:
    :undoc-members:


insights.specs.datasources.ls
-----------------------------

.. automodule:: insights.specs.datasources.ls
    :members: list_with_la, list_with_la_filtered, list_with_lan, list_with_lan_filtered, list_with_lanL, list_with_lanR, list_with_lanRL, list_with_laRZ, list_with_laZ, files_dirs_number
    :show-inheritance:
    :undoc-members:


insights.specs.datasources.lsattr
---------------------------------

.. automodule:: insights.specs.datasources.lsattr
    :members: paths_to_lsattr
    :show-inheritance:
    :undoc-members:


insights.specs.datasources.lpstat
---------------------------------

.. automodule:: insights.specs.datasources.lpstat
    :members: lpstat_protocol_printers_info, LocalSpecs
    :show-inheritance:
    :undoc-members:


insights.specs.datasources.luks
-------------------------------

.. automodule:: insights.specs.datasources.luks
    :members: luks_block_devices, luks_data_sources, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.machine_id
-------------------------------------

.. automodule:: insights.specs.datasources.machine_id
    :members: dup_machine_id_info
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.malware_detection
--------------------------------------------

.. automodule:: insights.specs.datasources.malware_detection.malware_detection_ds
    :members: malware_detection
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.mount
--------------------------------

.. automodule:: insights.specs.datasources.mount
    :members: xfs_mounts
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.md5chk
---------------------------------

.. automodule:: insights.specs.datasources.md5chk
    :members: files
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.package_provides
-------------------------------------------

.. automodule:: insights.specs.datasources.package_provides
    :members: cmd_and_pkg, get_package
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.pcp
------------------------------

.. automodule:: insights.specs.datasources.pcp
    :members: ros_collect, pcp_enabled, pmlog_summary_args, pmlog_summary_args_pcp_zeroconf
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.ps
-----------------------------

.. automodule:: insights.specs.datasources.ps
    :members: jboss_runtime_versions, ps_eo_cmd, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.rpm
------------------------------

.. automodule:: insights.specs.datasources.rpm
    :members: pkgs_with_writable_dirs, rpm_v_pkg_list
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.rsyslog
----------------------------------

.. automodule:: insights.specs.datasources.rsyslog
    :members: rsyslog_errorfile
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.sap
------------------------------

.. automodule:: insights.specs.datasources.sap
    :members: sap_sid, sap_hana_sid, sap_hana_sid_SID_nr, ld_library_path_of_user, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.satellite
------------------------------------

.. automodule:: insights.specs.datasources.satellite
    :members: satellite_missed_pulp_agent_queues, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.semanage
-----------------------------------

.. automodule:: insights.specs.datasources.semanage
    :members: users_count_map_selinux_user, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.ssl_certificate
------------------------------------------

.. automodule:: insights.specs.datasources.ssl_certificate
    :members: httpd_certificate_info_in_nss, httpd_ssl_certificate_files, nginx_ssl_certificate_files, mssql_tls_cert_file, rsyslog_tls_ca_cert_file, rsyslog_tls_cert_file
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.sys_fs_cgroup_memory
-----------------------------------------------

.. automodule:: insights.specs.datasources.sys_fs_cgroup_memory
    :members: uniq_memory_swappiness, tasks_number, LocalSpecs
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.user_group
-------------------------------------

.. automodule:: insights.specs.datasources.user_group
    :members: group_filters
    :show-inheritance:
    :undoc-members:

insights.specs.datasources.yum_updates
--------------------------------------

.. automodule:: insights.specs.datasources.yum_updates
    :members: yum_updates
    :show-inheritance:
    :undoc-members:
