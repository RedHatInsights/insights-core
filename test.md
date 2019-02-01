# Insights Core Run (01/31/19 18:28:22)

## Command Line
`/home/remote/bfahr/dev/venv3/bin/insights-run -f _markdown -p telemetry.rules.plugins,diag_insights_rules sosreport-20181220-081944/scicloudrhevm.n1grid.lan`


## Rules Executed
### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_1117613.report
```
1117613:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.5', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02208150',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02208150'},
                      'classification': 'Regular',
                      'cwe': {'id': '1117613',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=1117613'},
                      'relations': {'child': ['2086313', '2086323', '2111951'], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_1117633.report
```
1117633:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.1 U2', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02208147',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02208147'},
                      'classification': 'Regular',
                      'cwe': {'id': '1117633',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=1117633'},
                      'relations': {'child': ['1562723'], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_1383283.report
```
1383283:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.0', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02211208',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02211208'},
                      'classification': 'Regular',
                      'cwe': {'id': '1383283',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=1383283'},
                      'relations': {'child': ['2086303', '2599711', '2951451'], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_1562723.report
```
1562723:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.1 U3', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02213544',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02213544'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '1562723',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=1562723'},
                      'relations': {'child': [], 'parent': ['1117633']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2086303.report
```
2086303:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.0 U1', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02214731',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02214731'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2086303',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2086303'},
                      'relations': {'child': [], 'parent': ['1383283']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2086313.report
```
2086313:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.5 U1', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02214734',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02214734'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2086313',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2086313'},
                      'relations': {'child': [], 'parent': ['1117613']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2086323.report
```
2086323:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.5 U2', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02214737',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02214737'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2086323',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2086323'},
                      'relations': {'child': [], 'parent': ['1117613']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2111951.report
```
2111951:
    additional_info: {'make': 'ESXi', 'model': 'Server 5.5 U3', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02214740',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02214740'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2111951',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2111951'},
                      'relations': {'child': [], 'parent': ['1117613']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2599711.report
```
2599711:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.0 U2', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02219826',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02219826'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2599711',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2599711'},
                      'relations': {'child': [], 'parent': ['1383283']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2769061.report
```
2769061:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.5', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02220301',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02220301'},
                      'classification': 'Regular',
                      'cwe': {'id': '2769061',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2769061'},
                      'relations': {'child': ['3432261', '3160291'], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_2951451.report
```
2951451:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.0 U3', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02221969',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02221969'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '2951451',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=2951451'},
                      'relations': {'child': [], 'parent': ['1383283']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_3108501.report
```
3108501:
    additional_info: {'make': 'ESXi', 'model': 'Server for VMware Cloud', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02223050',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02223050'},
                      'classification': 'Regular',
                      'cwe': {'id': '3108501',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=3108501'},
                      'relations': {'child': [], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_3160291.report
```
3160291:
    additional_info: {'make': 'ESXi', 'model': '6.5 U1', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02223846',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02223846'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '3160291',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=3160291'},
                      'relations': {'child': [], 'parent': ['2769061']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_3386611.report
```
3386611:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.7', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02226400',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02226400'},
                      'classification': 'Regular',
                      'cwe': {'id': '3386611',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=3386611'},
                      'relations': {'child': [], 'parent': []},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [FINGERPRINT] diag_insights_rules.plugins.fingerprint.vmware.vmware_3432261.report
```
3432261:
    additional_info: {'make': 'ESXi', 'model': 'Server 6.5 U2', 'vendor': 'VMware'}
    cert_details   : {'case': {'id': '02226577',
                               'url': 'https://access.redhat.com/certops/internal/#/certification/02226577'},
                      'classification': 'Pass-Through',
                      'cwe': {'id': '3432261',
                              'url': 'https://hardware.redhat.com/show.cgi?cert_nid=3432261'},
                      'relations': {'child': [], 'parent': ['2769061']},
                      'rhel_version': '7.0',
                      'status': 'Certified',
                      'type': 'Hardware'}
    fingerprint    : {'redhat_release': {'major': '7'},
                      'system_information': {'manufacturer': 'VMware, Inc.',
                                             'product_name': 'VMware Virtual Platform'}}

```

### [META] diag_insights_rules.plugins.general.identify_product_and_version_installed.report
```
None:
    version: {'RHEL': '7.5'}

```

### [META] diag_insights_rules.plugins.general.rhel_lifecycle_display.report
```
None:
    NOTE: 'Kernel of this system is not released by RedHat'

```

### [META] diag_insights_rules.plugins.kernel.official_release_kernel_version.report
```
None:
    Is GA                   : False
    Kernel Version Installed: '3.10.0-862.3.2.el7'
    Official Release Kernel : 'Yes'
    RHEL Release            : '7.5'

```

### [META] diag_insights_rules.plugins.rhev.rhv_lifecycle_info.report
```
None:
    Product Lifecycle Dates            : {'End Full Support': 'August 23rd, 2019',
                                          'End Maintenance Support': 'August 23rd, 2021',
                                          'Extended Life Support': 'August 23rd, 2023',
                                          'GA': 'August 23rd, 2016'}
    Product Name                       : 'Red Hat Virtualization'
    Product Version                    : 4.2
    RHVH Supported Compatibility Levels: [4.2, 4.1, 4.0, 3.6]
    Release Date                       : 'May 15th, 2018'

```

### [META] diag_insights_rules.plugins.stack.osp_error_counts.report
```
None:
    Cinder Errors Found         : 0
    Mariadb Errors              : 0
    Neutron API Errors          : 0
    RabbitMQ StartErr Log Errors: 0
    RabbitMQ Startup Log Errors : 0

```

### [META] telemetry.rules.plugins.container.docker_container_metadata.report
```
None

```

### [META] telemetry.rules.plugins.container.docker_host_metadata.report
```
None

```

### [META] telemetry.rules.plugins.kernel.dmidecode_virtwhat_metadata.report
```
None:
    bios_information  : {'bios_revision': '4.6',
                         'release_date': '04/05/2016',
                         'vendor': 'Phoenix Technologies LTD',
                         'version': '6.00'}
    system_information: {'family': 'Not Specified',
                         'manufacturer': 'VMware, Inc.',
                         'product_name': 'VMware Virtual Platform',
                         'virtual_machine': True}

```

### [FAIL] telemetry.rules.plugins.networking.ip_local_port_range_parity.report
```
IP_LOCAL_PORT_RANGE_INFO:
    port_range: ['15000', '61000']

```

### [META] telemetry.rules.plugins.networking.listening_processes_on_ports_metadata.report
```
None:
    listening_processes: [{'ip_addr': '0.0.0.0', 'port': '80', 'process_name': 'httpd'},
                          {'ip_addr': '0.0.0.0', 'port': '9696', 'process_name': 'python'},
                          {'ip_addr': '127.0.0.1', 'port': '8707', 'process_name': 'ovirt-engine'},
                          {'ip_addr': '0.0.0.0', 'port': '10050', 'process_name': 'zabbix_agentd'},
                          {'ip_addr': '0.0.0.0', 'port': '51821', 'process_name': 'rpc.statd'},
                          {'ip_addr': '0.0.0.0', 'port': '2222', 'process_name': 'sshd'},
                          {'ip_addr': '0.0.0.0', 'port': '111', 'process_name': 'rpcbind'},
                          {'ip_addr': '0.0.0.0', 'port': '8080', 'process_name': '(squid-1)'},
                          {'ip_addr': '0.0.0.0', 'port': '6641', 'process_name': 'ovsdb-server'},
                          {'ip_addr': '0.0.0.0', 'port': '6642', 'process_name': 'ovsdb-server'},
                         <...5 more lines...>

```

### [FAIL] telemetry.rules.plugins.networking.systemd_non_persistent_ifname.report
```
NON_PERSISTENT_IFNAME

```

### [META] telemetry.rules.plugins.non_kernel.rpm_listing.report
```
Number of packages installed: 1186
```

### [META] telemetry.rules.plugins.release_metadata.report
```
None:
    rhel_version: '7.5'

```

### [FAIL] telemetry.rules.plugins.storage.storage_netfs_without_netdev.report
```
NETWORK_FILESYSTEM_NOT_MOUNT_ON_STARTUP:
    fstab_entries        : ['192.168.115.2:/sre_scicloud_iso',
                            '192.168.115.2:/sre_scicloud_data01',
                            '192.168.115.2:/sre_scicloud_data02',
                            '192.168.115.2:/sre_scicloud_export',
                            '192.168.115.2:/sre_smalls/scicloudrhevm_pg_backup']
    fstab_return_clauses : ['192.168.115.2:/sre_scicloud_iso /sre_scicloud_iso nfs nfsvers=3,ro,_netdev 0 '
                            '0',
                            '192.168.115.2:/sre_scicloud_data01 /sre_scicloud_data01 nfs '
                            'nfsvers=3,rw,_netdev 0 0',
                            '192.168.115.2:/sre_scicloud_data02 /sre_scicloud_data02 nfs '
                            'nfsvers=3,ro,_netdev 0 0',
                            '192.168.115.2:/sre_scicloud_export /sre_scicloud_export nfs '
                            'nfsvers=3,rw,_netdev 0 0',
                            '192.168.115.2:/sre_smalls/scicloudrhevm_pg_backup '
                            '/var/lib/ovirt-engine-dwh/backups nfs rw,noatime,nfsvers=3,_netdev 0 0']
    netfs_service_enabled: 'True'
    version              : 7

```


## Rule Execution Summary
```
 Missing Deps: 462
 Passed      : 0
 Failed      : 3
 Metadata    : 10
 Metadata Key: 1
 Fingerprint : 15
 Exceptions  : 5
```
