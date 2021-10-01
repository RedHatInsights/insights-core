# Change Log

## [Unreleased](https://github.com/RedHatInsights/insights-core/tree/HEAD)

## [insights-core-3.0.244](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.244) (2021-09-29)

- PR \#3225 - Add documentation for `yum_updates` datasource (Issue \#3223)
- PR \#3232 - Add new combiner AnsibleInfo for ansible information

## [insights-core-3.0.243](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.243) (2021-09-23)

- PR \#3197 - Add new parser *RosConfig* for file `/var/lib/pcp/config/pmlogger/config.ros`
- PR \#3218 - Fix issue in HTTPD conf parsers/combiner where directives could have empty strings (Issue \#3211)
- PR \#3231 - Preserve alignment in `netstat -neopa` output in client obfuscation

## [insights-core-3.0.242](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.242) (2021-09-22)

- PR \#3219 - Fix an issue parsing devices in the `lpstat` datasource
- PR \#3221 - New parsers *LpfcMaxLUNs* for file `/sys/module/lpfc/parameters/lpfc_max_luns`, *Ql2xMaxLUN* for file `/sys/module/qla2xxx/parameters/ql2xmaxlun`, and *SCSIModMaxReportLUNs* for file `/sys/module/scsi_mod/parameters/max_report_luns`
- PR \#3222 - Fix linting errors and modify setup to use latest version of `flake8`
- PR \#3224 - Remove parser *Facter* and associated spec and dependencies ([Bugzilla 1989655](https://bugzilla.redhat.com/show_bug.cgi?id=1989655))
- PR \#3226 - Fix linting errors in client for latest version of `flake8`
- PR \#3227 - Update verifier in client to remove long suffix for python2
- PR \#3229 - Update requires for RPM build for RHEL7

## [insights-core-3.0.241](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.241) (2021-09-16)

- PR \#2993 - Add datasource and parser *YumUpdates* to provide a list of available YUM/DNF updates
- PR \#3144 - Support insights shell running in ipykernel mode
- PR \#3207 - Remove unused datasource specs from host collection (Issue \#3087)
- PR \#3208 - Add new spec `mssql_api_assessment` to collect file `/var/opt/mssql/log/assessments/assessment-latest`
- PR \#3209 - Fix an issue where tests were being loaded in insights shell and throwing exceptions about missing modules
- PR \#3214 - Update client validation code to fix python 2.7 issue
- PR \#3216 - Remove unused spec `ansible_tower_settings` which was replaced by `awx_manage_print_settings`
- PR \#3217 - Add missing file for tito RPM build
- PR \#3220 - Enhance parser *CupsPpd* to handle comments in input

## [insights-core-3.0.240](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.240) (2021-09-01)

- PR \#3112 - Consolidate network logging and timeouts in client
- PR \#3201 - Add new parser *CupsPpd* for file glob `/etc/cups/ppd/*`
- PR \#3202 - Add new parser *LpstatProtocol* for the command `lpstat -v`
- PR \#3203 - Fix `iter/next` deprecated code in *Lsof* parser (PR \#3185)
- PR \#3204 - Add new attribute to *SatelliteSCAStatus* parser to indicate whether SCA is enabled
- PR \#3205 - Fix regex in *LSBlock* parser to capture all RAID devices
- PR \#3206 - Add new attribute to *Bond* parser for MII polling interval

## [insights-core-3.0.239](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.239) (2021-08-26)

- PR \#3128 - Repair malformed SSG version in results for Compliance
- PR \#3195 - Add the ability to build insights-core as an RPM
- PR \#3196 - Restore command spec `ss -tupna` to be collected on all systems (Issue \#2909)
- PR \#3200 - Revert PR \#3185] due to collection issues

## [insights-core-3.0.238](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.238) (2021-08-19)

- PR \#3181 - Add new parser *AwxManagerPrintSettings* for command `/usr/bin/awx-manage print_settings INSIGHTS_TRACKING_STATE SYSTEM_UUID INSTALL_UUID TOWER_URL_BASE AWX_CLEANUP_PATHS AWX_PROOT_BASE_PATH --format json`
- PR \#3184 - In support tool `insights run` merge `-N` (show make_none rules) switch with `-S` (show rules by type) switch
- PR \#3185 - Change code to fix Python functionality deprecated by [PEP 479](https://www.python.org/dev/peps/pep-0479) in Python 3.5
- PR \#3186 - Update `candlepin_broker` tests to work with newer versions of Python and Pytest (Issue \#3188)
- PR \#3187 - Update `setup.py` to work with newer versions of Python and Pytest
- PR \#3189 - Add new parser *MssqlApiAssessment* for file spec `/var/opt/mssql/log/assessments/assessment-latest`
- PR \#3190 - Fix *LsPci* combiner to account for unexpected-but-valid data format in in `lspci -k` (Issue \#3176)
- PR \#3191 - Remove spec `mssql_api_assessment` merged in PR \#3189 prior to spec approval
- PR \#3193 - Fix `ntp_sources` parsers to gracefully account for no NTP sources (Issue \#3192)
- PR \#3194 - Fix issues in the collection and validation of canonical facts

## [insights-core-3.0.236](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.236) (2021-08-11)

- PR \#3066 - In client, add additional messaging for `401` response
- PR \#3141 - In client, don't add messages that say "to view logs..." to the log file
- PR \#3142 - In client, allow collections without registration with the `--no-upload` switch
- PR \#3151 - Compatibility layer legacy upload fix in the client
- PR \#3168 - In client apply `chmod 644` to lastupload files
- PR \#3171 - Remove `uploader.json` map file from repo.
- PR \#3174 - Fix error in *Lsof* parser (Issue \#3172)
- PR \#3178 - Add command spec `/usr/sbin/ntpq -pn` for existing parser
- PR \#3180 - Add new parser *ForemanSSLErrorLog* for file `/var/log/httpd/foreman-ssl_error_ssl.log`
- PR \#3182 - Fix error in pytest fixture for `test_empty_skip`

## [insights-core-3.0.235](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.235) (2021-08-05)

- PR \#2611 - In client use a hash function to obfuscate hostname instead of setting it to "host0"
- PR \#3137 - Add new parser *UdevRulesOracleASM* for file glob `"/etc/udev/rules.d/\*asm*.rules"`
- PR \#3149 - Add `slot` information to results of parser *LsPci*.
- PR \#3156 - Add `make_none` response type to enable reporting of rules that return `none` for support/debug.
- PR \#3167 - Turn on playbook validation in client
- PR \#3169 - Add new parser *OracleasmSysconfig* for file spec `"/etc/sysconfig/oracleasm"`
- PR \#3170 - In client, to facilitate removal of the `uploader_json_map.json` file from the egg, resume update of the `/etc/insights-client/.cache.json` file.
- PR \#3173 - Add additional spec paths for `lsof` data in sosreport
- PR \#3175 - Add `--show-rules` option to `insights run` command line support tool (Issue \#3161)
- PR \#3177 - Fix typo in documentation

## [insights-core-3.0.234](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.234) (2021-07-29)

- PR \#3157 - Fix issue in base *JSONParser* class causing exceptions when content was empty
- PR \#3162 - Revert PR \#3154 due to issues with rules CI tests (Issue \#3161)
- PR \#3164 - Add new specs for existing *DnsmasqConf* parser for file glob `glob_file(["/etc/dnsmasq.conf", "/etc/dnsmasq.d/*.conf"])`
- PR \#3166 - Add insights archive spec for `systemctl_cat_dnsmasq_service` (Issue \#3165)

## [insights-core-3.0.233](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.233) (2021-07-22)

- PR \#3133 - Add new parser *AnsibleTowerLicense* for command `/usr/bin/awx-manage check_license --data`
- PR \#3139 - Fix issue in client in connection logic
- PR \#3148 - Fix issue in *LsPci* combiner to prevent modification of parser data (Issue \#3147)
- PR \#3153 - Fix issue in *LogRotateConf* parser (Issue \#3152)
- PR \#3154 - Add new `-S` option to the `insights run` command
- PR \#3155 - Add new parser *SystemdDnsmasqServiceConf* for command `/bin/systemctl cat dnsmasq.service` (Issue \#3165)
- PR \#3160 - Fix issue in tests for `candlepin_broker` datasource

## [insights-core-3.0.232](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.232) (2021-07-15)

Insights-core-3.0.231 was not released into production.  Insights-core-3.0.232 includes all PRs merged in both releases.

- PR \#3135 - Add new `make_none` response type for rules that return `None`
- PR \#3138 - Add new parser **HaproxyCfgScl** for file `/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg`
- PR \#3146 - Revert PR \#3135 due to rules CI issues

## [insights-core-3.0.230](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.230-1859) (2021-07-08)

- PR \#3053 - Add new parser **SatelliteMissedQueues** for custom datasource `satellite_missed_pulp_agent_queues`
- PR \#3119 - Move datasource `package_provides_command` into separate module
- PR \#3122 - Fix `ethtool` parser exceptions caused by a spec issue (Issue \#1791)
- PR \#3124 - Move SAP datasources into separate module
- PR \#3127 - Add command spec `ipcs_s_i` for command `foreach_execute(ipcs.semid, "/usr/bin/ipcs -s -i %s")` and new datasource for existing parser **IpcsSI**
- PR \#3131 - Add documentation entry for component `cloud_provider` (Issue \#3130)
- PR \#3132 - Convert datasource `is_ceph_monitor` to component **IsCephMonitor**
- PR \#3136 - Remove unnecessary datasources `is_satellite_server` and `is_satellite_capsule`

## [insights-core-3.0.229-1849](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.229-1849) (2021-07-01)

- PR \#3099 - Add new datasource and parser **CandlepinBrokerXML** for file `/etc/candlepin/broker.xml`
- PR \#3101 - Compliance: In client improve tmp handling
- PR \#3120 - Remove unused Openshift collector specs and related artifacts
- PR \#3121 - Add new datasource and parser **PsEoCmd** for command `/bin/ps -eo pid,args`
- PR \#3123 - Add new parser **AnsibleTowerSettings** for file globs `["/etc/tower/settings.py", "/etc/tower/conf.d/*.py"]`
- PR \#3125 - Fix test for `cloud_init` datasource
- PR \#3126 - Refactor cloud datasources to components
- PR \#3129 - Add tests for ps datasources added by PR \#3121

## [insights-core-3.0.228-1839](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.228-1839) (2021-06-24)

- PR \#3102 - Add parser **AnsibleTowerSettings** for glob spec `["/etc/tower/settings.py", "/etc/tower/conf.d/*.py"]`
- PR \#3107 - Fix attribute error in **AllModProbe** combiner (Issue \#3107)
- PR \#3110 - Move `cloud_cfg` custom datasource to a separate module
- PR \#3111 - In client make a copy of options when loading defaults into `argparse`
- PR \#3114 - Remove requirement for `futures` python module in `[development]` setup. (Issue \#3113)
- PR \#3116 - Fix definition of spec for **AnsibleTowerSettings** parser (Issue \#3115)
- PR \#3117 - Remove **AnsibleTowerSettings** parser

## [insights-core-3.0.227-1831](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.227-1831) (2021-06-17)

- PR \#2801 - Add new parser **GCPInstanceType** for command `/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/machine-type --connect-timeout 5`
- PR \#3091 - Add new spec to collect running `httpd` and corresponding RPM package
- PR \#3100 - Fix issue with non-AWS system being identified as AWS cloud system (Issue \#2904)
- PR \#3103 - Add new file spec for SOS reports `/etc/audit/auditd.conf`
- PR \#3104 - Add new file spec `/proc/partitions` for existing parser
- PR \#3105 - In client disallow *unregister* in offline mode ([Bugzilla 1920846](https://bugzilla.redhat.com/show_bug.cgi?id=1920946))
- PR \#3106 - Update pull request template

## [insights-core-3.0.226-1822](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.226-1822) (2021-06-10)

- PR \#3007 - Add `ansible_host` option to client
- PR \#3092 - Enhance core to provide binary path to **HttpdV** and **HttpdM** parsers
- PR \#3093 - Update CONTRIBUTING documentation
- PR \#3094 - Fix exception in **Scheduler** parser when there is no active scheduler
- PR \#3096 - Fix restructuredtext formatting in documentation
- PR \#3097 - Fix incorrect collection spec for Google cloud `gcp_license_codes` (Issue \#3095)
- PR \#3098 - Add parser **ForemanSSLAccessLog** for SOS spec `first_file(["var/log/httpd/foreman-ssl_access_ssl.log", r"sos_commands/foreman/foreman-debug/var/log/httpd/foreman-ssl_access_ssl.log"])`

## [insights-core-3.0.225-1814](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.225-1814) (2021-06-03)

- PR \#3055 - Update client Verifier code to allow for signature validation
- PR \#3089 - Add a pull request template to the Github project
- PR \#3090 - Remove duplicate core-collection spec **package_provides_java**

## [insights-core-3.0.224-1809](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.224-1809) (2021-05-26)

- PR \#3014 - Make handling of err release in `/tmp/insights-client` more secure in client ([Bugzilla 1920344](https://bugzilla.redhat.com/show_bug.cgi?id=1920344))
- PR \#3016 - Switch to use `/var/tmp/insights-client` instead of `/tmp/insights-client` for client egg release
- PR \#3067 - Fix parsing for IBM s390 systems in **CpuInfo** parser (Issue \#2629)
- PR \#3072 - Add new parser **GrubSysconfig** for the file `/etc/default/grub`
- PR \#3074 - Fix `IndexError` exception in SMT **CpuCoreOnline** combiner (Issue \#3073)
- PR \#3075 - Add support for RHEL 8.4 in Uname parser
- PR \#3077 - Fix `ValueError` exception in RHEL 6 for **DockerList** parser (Issue \#3076)
- PR \#3078 - Update Sosreport spec **journal_since_boot**
- PR \#3080 - Enable spec for existing **VMwareToolsConf** parser for file `/etc/vmware-tools/tools.conf`
- PR \#3081 - Add new collection filter to **GreenbootStatus** parser
- PR \#3083 - Update **Scheduler** parser to add attributes, documentation and tests (Issue \#2997)
- PR \#3084 - Add new CLI switch `--color` to allow color in piped commands (Issue \#2980)

## [insights-core-3.0.223-1796](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.223-1796) (2021-05-18)

- PR \#3060 - Add kernal-alt releases to **Uname** parser. (Issue \#2770)
- PR \#3061 - Update **pmrep_metrics** spec to include additional information.
- PR \#3064 - Switch to Github actions for CI/CD.
- PR \#3068 - Fix error in **pmrep_metrics** archive spec (Issue \#3065)
- PR \#3070 - Minor documentation update. (Issue \#3069)

## [insights-core-3.0.222-1790](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.222-1790) (2021-05-13)

- PR \#3038 - Add new combiner **SysVmBusDeviceInfo** and parsers **SysVmbusDeviceID** for files `/sys/bus/vmbus/devices/*/device_id` and **SysVmbusClassID** for files `/sys/bus/vmbus/devices/*/class_id`
- PR \#3051 - Changes to core to allow use of new RHEL6/Python26 CI/CD image.
- PR \#3054 - Update **mongod_conf** spec to remove old files
- PR \#3056 - Fix **Uname** parser to support debug kernels (Issue \#2709)
- PR \#3057 - Fix error introduced by latest version of Jinja2.

## [insights-core-3.0.221-1784](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.221-1784) (2021-05-06)

- PR \#3027 - Add new parser **RpmOstreeStatus** to collect command `/usr/bin/rpm-ostree status --json`
- PR \#3041 - Fix error in **SystemdAnalyzeBlame** parser caused by unexpected input (Issue \#3040)
- PR \#3045 - Fix error in **VirshListAll** parser caused by unexpected input (Issue \#3044)
- PR \#3046 - Change compliance in client to use host ID instead of hostname
- PR \#3048 - Add contrib module `ruamel.yaml` to client
- PR \#3049 - Refactor client to pull os-release spec usage out into util function

## [insights-core-3.0.220-1777](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.220-1777) (2021-04-29)

- PR \#3033 - Add new parser **PMREPMetrics** for command `pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`
- PR \#3035 - Update sosreport specs for **Pvs**, **Vgs**, **Lvs**, and **Vgdisplay** parsers
- PR \#3036 - Remove the spec `lsinitrd`
- PR \#3037 - Ocp and ocpshell supports yaml files with multiple docs
- PR \#3039 - Update parser **MongodbConf** to parse additional paths
- PR \#3043 - Fix error in parser **DmsetupStatus** caused by unexpected command output (Issue \#3042)
- PR \#3047 - Documentation update for **InstalledRpms** parser

## [insights-core-3.0.219-1769](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.219-1769) (2021-04-22)

- PR \#3023 - Add new parser **HanaLandscape** for command `foreach_execute(sap_hana_sid_SID_nr, "/bin/su -l %sadm -c 'python /usr/sap/%s/HDB%s/exe/python_support/landscapeHostConfiguration.py'", keep_rc=True)`
- PR \#3024 - Fix attribute in docs for parser **AzureInstancePlan**
- PR \#3025 - Update Jenkinsfile to fix issues in Python 2.6 CI
- PR \#3028 - Revert PR \#3025 because it was only an intermittent partial fix that was not targeting the real cause
- PR \#3030 - Add new parser **GCPLicenseCodes** for command `/usr/bin/curl -s curl -H Metadata-Flavor: Google http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True --connect-timeout 5`
- PR \#3031 - Add new parser **GreenbootStatus** for command `/usr/libexec/greenboot/greenboot-status`
- PR \#3032 - Fix parsing errors in **Lvm** parsers (Issue \#3034)

## [insights-core-3.0.218-1761](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.218-1761) (2021-04-15)

- PR \#2775 - Enable spec `lsinitrd` for collection of command `/usr/bin/lsinitrd`
- PR \#2865 - Fix client ultralight checkins: wrap thrown exception with catch
- PR \#2996 - Add sosreport spec `scheduler` for files `/sys/block/*/queue/scheduler`
- PR \#3000 - Fix parsing bugs in **RedhatRelease** parser (Issue \#2999)
- PR \#3001 - Add `lssap` spec back to insights archives (Issue \#3002)
- PR \#3003 - Allow scalars in `parsr.query.choose` results
- PR \#3005 - Fix issue with documentation build caused by latest version of **Docutils** package
- PR \#3006 - Update Jenkinsfile to use latest Python 3 CI image
- PR \#3009 - Update **PuppetCertExpireDate** to used shared base parser
- PR \#3010 - In client change `validation` function to manually override `skipVerify`
- PR \#3011 - Update parser CertificatesEnddate to return data if any certificate files found
- PR \#3012 - Keep return code for specs `ls_etc` and `md5chk_files` so that parser can evaluate results
- PR \#3013 - Update paths for spec `mongod_conf`
- PR \#3015 - Update paths for specs `postgresql_conf` and `postgresql_log`
- PR \#3017 - Add new parser **AzureInstancePlan** for command `/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json --connect-timeout 5`
- PR \#3018 - Remove spec `qpid_stat_g` not used by any rules
- PR \#3019 - Add new spec `ansible_host` for client collection
- PR \#3020 - Ensure that the sap_hdb_version spec is only executed for SAP HANA hosts ([Bugzilla 1949056](https://bugzilla.redhat.com/show_bug.cgi?id=1949056))
- PR \#3021 - Add azure_instance_plan spec to insights archives for older clients
- PR \#3022 - Modify spec `sap_hdb_version` to use `su` instead of `sudo` ([Bugzilla 1949056](https://bugzilla.redhat.com/show_bug.cgi?id=1949056))

## [insights-core-3.0.217-1741](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.217-1741) (2021-03-31)

- PR \#2894 - Refactor client to remove `insecure_connection` config option
- PR \#2934 - Add new parser **SatelliteComputeResources** for command `/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select name, type from compute_resources' --csv`
- PR \#2971 - Send OS info in profile request
- PR \#2974 - Use **SIGTERM** on timeout for `rpm` and `yum` commands (PR \#2630, [Bugzilla 1935846](https://bugzilla.redhat.com/show_bug.cgi?id=1935846))
- PR \#2988 - Add `loadPlaybookYaml` funtion to verifier functionality
- PR \#2991 - Add new parser **RhsmKatelloDefaultCACert** for command `/usr/bin/openssl x509 -in /etc/rhsm/ca/katello-default-ca.pem -noout -issuer`insights-core-assets/-/merge_requests/204[MR 204])
- PR \#2992 - Add new sosreport spec tuned_adm for file `sos_commands/tuned/tuned-adm_list`
- PR \#2994 - Add `timestamp` attribute to **RhsmLog** parser
- PR \#2995 - Remove duplicate spec `lspci_kernel`

## [insights-core-3.0.216-1730](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.216-1730) (2021-03-25)

- PR \#2929 - Add new parser **SatelliteAdminSettings** for command `/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name, value, \\\"default\\\" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')\" --csv`
- PR \#2981 - Add new parser **SatelliteCustomCaChain** for command `/usr/bin/awk \'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}\' /etc/pki/katello/certs/katello-server-ca.crt`
- PR \#2983 - Fix exception in **YumRepolist** parser when repolist is empty (Issue \#2857)
- PR \#2985 - Fix issue with deserialization of datasources as raw instead of text (Issue \#2970)
- PR \#2987 - Updates to edge cases, documentation and tests, and fix parsing of trailing whitespace for Tuned parser (Issue \#2986)
- PR \#2990 - Fix issue in LogRotate parser where missing endscript caused an infinite loop (Issue \#2989)

## [insights-core-3.0.215-1722](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.215-1722) (2021-03-18)

- PR \#2945 - Implement playbook signature validation logic in insights-core
- PR \#2973 - Add new parser **LsPciVmmkn** for command `/sbin/lspci -vmmkn`
- PR \#2979 - Remove deprecated warning for parser **VirtUuidFacts**
- PR \#2982 - Add new combiner **LsPci** for the `lspci` command parsers

## [insights-core-3.0.214-1717](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.214-1717) (2021-03-11)

- PR \#2888 - Activate checkin timer in client
- PR \#2969 - Update parser and test to detect lssap issue in [Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?id=1922937)
- PR \#2972 - Change uses of deprecated **hostname** combiner to **Hostname** combiner
- PR \#2975 - Remove **lssap** spec from collection ([Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?id=1922937), [Bugzilla 1936951](https://bugzilla.redhat.com/show_bug.cgi?id=1936951)
- PR \#2976 - Enhance the **SAP** combiner to use both hostname and FQDN

## [insights-core-3.0.213-1710](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.213-1710) (2021-03-04)

- PR \#2926 - Add new parser DmsetupStatus for command `/usr/sbin/dmsetup status`
- PR \#2939 - Update non-working parser **PidLdLibraryPath** and rename to **UserLdLibraryPath** for spec **ld_library_path_of_user**
- PR \#2965 - Update **ld_library_path_of_user** spec to only collect information for SAP application users
- PR \#2966 - Add `microcode` keyword value in the **CpuInfo** parser
- PR \#2967 - Add new value `kernel.all.cpu.wait.total` to **pmlog_summary** spec

## [insights-core-3.0.212-1703](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.212-1703) (2021-02-25)

- PR \#2936 - In client add check for null PATH environment variable before using it
- PR \#2950 - Add new parser **PmLogSummary** for command `/usr/bin/pmlogsummary`
- PR \#2960 - Add new sosreport spec **mdadm_E** for file glob `sos_commands/md/mdadm_-E_*`
- PR \#2961 - Add new parser **InsightsClientConf** for file `/etc/insights-client/insights-client.conf`
- PR \#2963 - Fix problem with exception logging in core collection (Issue \#2962)

## [insights-core-3.0.211-1696](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.211-1696) (2021-02-18)

- PR \#2953 - Fix handling of edge cases for **Sealert** parser (Issue \#2951)
- PR \#2955 - Fix problem with exceptions during collection in `corosync_cmapctl_cmd_list` datasource (Issue \#2954)

## [insights-core-3.0.210-1692](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.210-1692) (2021-02-11)

- PR \#2905 - Add new parser **LsVarCachePulp** for command `/bin/ls -lan /var/cache/pulp`
- PR \#2923 - Additional paths to collect for **postgresql_log**, `/var/opt/rh/rh-postgresql12/lib/pgsql/data/log/postgresql-*.log`, and for **postgresql_conf**, `/var/opt/rh/rh-postgresql12/lib/pgsql/data/postgresql.conf`
- PR \#2944 - Fix bug in **VirshListAll** parser to correctly handle uppercase VM names
- PR \#2946 - Prevent soscleaner in client from erasing `insights_archive.txt`
- PR \#2949 - Catch rules that add a blank filter for a filterable spec (Issue \#2948)

## [insights-core-3.0.209-1685](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.209-1685) (2021-02-05)

- PR \#2869 - Remove Satellite specs for EOL versions of Satellite
- PR \#2902 - Add new parser **PidLdLibraryPath** for spec `ld_library_path_of_pid` which captures the PID and LD_LIBRARY_PATH value for the running process
- PR \#2906 - Add new parser **MongoDBNonYumTypeRepos** for command spec `mongo pulp_database --eval 'db.repo_importers.find({"importer_type_id": { $ne: "yum_importer"}}).count()'`
- PR \#2910 - Add new parser **GFS2FileSystemBlockSize** for command spec `foreach_execute(gfs2_mount_points, "/usr/bin/stat -fc %%s %s")`
- PR \#2917 - Enhance IP parsers to get `promiscuity` data
- PR \#2919 - Enhance collection of SAP HDB version for all instances on a system
- PR \#2921 - Fix issue in collection of file `/etc/cloud/cloud.cfg` which caused exceptions to be logged in the client log (Issue \#2920, [Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?-d=1922937), [Bugzilla 1923120](https://bugzilla.redhat.com/show_bug.cgi?id=1923120), [Bugzilla 1922269](https://bugzilla.redhat.com/show_bug.cgi?id=1922269))
- PR \#2922 - Fix issue with collection of spec **sap_hdb_version** from Insights archives (Issue \#2812)
- PR \#2924 - Add new spec **virsh_list_all** to collect sosreport file `sos_commands/virsh/virsh_-r_list_--all`
- PR \#2925 - Enhance **IsRhel[678]** components to include RHEL`minor` version
- PR \#2927 - Fix client checkin URL with legacy upload
- PR \#2930 - Add new parser **VersionInfo** for existing spec collecting versions of the client and insights-core

## [insights-core-3.0.208-1673](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.208-1673) (2021-01-28)

- PR \#2893 - Add several useful features to parsr.query
- PR \#2897 - Add new parser UdevRules40Redhat for files `/etc/udev/rules.d/40-redhat.rules`, `/run/udev/rules.d/40-redhat.rules`, `/usr/lib/udev/rules.d/40-redhat.rules`, `/usr/local/lib/udev/rules.d/40-redhat.rules`
- PR \#2907 - Fix issue in `dr.set_enabled` to work with components and component names (Issue \#2903)
- PR \#2911 - Fix issue in custom datasources to only execute when collecting in *HostContext* (Issue \#2908)
- PR \#2914 - Fix issue with unhelpful debug messages appearing in client log (Issue \#2912)
- PR \#2915 - Remove debug messages generated when commands fail during serialization (Issue \#2913)
- PR \#2918 - Fix issue in client with collection of `version_info` when performing core collection

## [insights-core-3.0.207-1668](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.207-1668) (2021-01-26)

- PR \#2868 - Fix issue in client with HTTP_PROXY warning condition

## [insights-core-3.0.206-1666](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.206-1666) (2021-01-21)

- PR \#2849 - Add new parser **YumUpdateinfo** for command `/usr/bin/yum -C updateinfo list`
- PR \#2861 - Add new parser **CloudCfg** for file `/etc/cloud/cloud.cfg`
- PR \#2901 - Show original exceptions for mapped or lifted functions (Issue \#2900)

## [insights-core-3.0.205-1661](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.205-1661) (2021-01-15)

- PR \#2896 - Add new spec **lsblk_pairs** to collect the sosreport file `sos_commands/block/lsblk_-O_-P`
- PR \#2899 - Fix issue in core for RHEL 6 version of six python module (Issue \#2989)

## [insights-core-3.0.203-1657](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.203-1657) (2021-01-14)

- PR \#2863 - Fix memory and performance issues in *parsr* module (Issue \#2863)
- PR \#2879 - Fix error in command line support tools due to conflicting python modules (Issue \#2878)
- PR \#2881 - Fix error in *chkconfig* and *unitfiles* specs when no useful data is collected (Issue \#2882)
- PR \#2884 - Documentation fixes
- PR \#2887 - Enhance spec *satellite_content_hosts_count* to only execute during core collection and only run on Satellite hosts
- PR \#2890 - Fix issue in *first_file* spec that prevented collection of some specs (Issue \#2889)
- PR \#2891 - Fix issue in core collection spec that caused client timeouts ([Bugzilla 1915219](https://bugzilla.redhat.com/show_bug.cgi?id=1915219))
- PR \#2892 - Documentation fixes (Issue \#2862)

## [insights-core-3.0.202-1647](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.202-1647) (2021-01-07)

- PR \#2841 - Enhance combiners and parsers for *package_provides_java* and *package_provides_httpd*
- PR \#2846 - Add new parser *MDAdmMetadata* for command `foreach_execute(md_device_list, "/usr/sbin/mdadm -E %s")`
- PR \#2847 - Re-add specs *saphostexec_status* and *saphostexec_version* for core collection
- PR \#2856 - Add new parser *LsIPAIdoverrideMemberof* for command `/bin/ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof`
- PR \#2860 - Add new parser *SatelliteContentHostsCount* for command `/usr/bin/sudo -iu postgres psql -d foreman -c 'select count(*) from hosts'`
- PR \#2864 - Remove "unknown device" string from possible LVM warnings (Solutions [1535693](https://access.redhat.com/solutions/1535693), [45108](https://access.redhat.com/solutions/45108))
- PR \#2867 - Update client Compliance error message when no policies are assigned to the system
- PR \#2870 - Add latest Ceph version mapping for parser *CephVersion* (Solution [2045583](https://access.redhat.com/solutions/2045583))
- PR \#2873 - Add *LsMod* parser to preloaded components for use by client (Issue \#2872)
- PR \#2874 - Add spec *mokutil_sbstate* to sosreport specs for `sos_commands/boot/mokutil_--sb-state`
- PR \#2875 - Add new parser *PuppetCertExpireDate* for command `/usr/bin/openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout`
- PR \#2877 - Add spec *ls_sys_firmware* to sosreport specs for `sos_commands/boot/ls_-lanR_.sys.firmware`

## [insights-core-3.0.201-1634](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.201-1634) (2020-12-10)

- Commit 6ad8c2 - Fix client tests for core collection only spec
- PR \#2807 - Add support in the client for the hourly ultra-light check-ins
- PR \#2836 - Add new parser *PythonAlternatives* for command `/usr/sbin/alternatives --display python`
- PR \#2837 - Add new parser *LsUsrBin* for command `/bin/ls -lan /usr/bin`
- PR \#2845 - Add `warnings` attribute to *LVM* parsers
- PR \#2848 - Fix bug in SAPHostExecStatus and SAPHostExecVersion parsers that didn't handle empty output correctly
- PR \#2850 - Add precheck for modules before running command `ss -tupna` ([Bugzilla 1903183](https://bugzilla.redhat.com/show_bug.cgi?id=1903183))
- PR \#2852 - Skip `None` value when doing keyword_search (Issue \#2851)
- PR \#2853 - Skip the `grep -F` in ps in the first pass of parsing (Issue \#2851)
- PR \#2854 - Add spec `subscription_manager_installed_product_ids = simple_command("/usr/bin/find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;")` for core collection for existing parser, spec was already being collected in the JSON ([Bugzilla 1905503](https://bugzilla.redhat.com/show_bug.cgi?id=1905503))
- PR \#2855 - Enhance *InstalledRpms* parser vendor attribute
- PR \#2858 - Add spec `corosync_cmapctl = foreach_execute(corosync_cmapctl_cmd_list, "%s")` for core collection for existing parser
- PR \#2859 - Add spec `httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")` for core collection for existing parser

## [insights-core-3.0.200-1621](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.200-1621) (2020-12-03)

- PR \#2833 - Add new parser *Postconf* for command `/usr/sbin/postconf` and enable command `/usr/bin/postconf -C builtin` for parser *PostconfBuiltin* (
- PR \#2839 - Remove unused SAP specs from core collection
- PR \#2844 - In client fix playbook verify, remove placeholder module

## [insights-core-3.0.199-1616](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.199-1616) (2020-11-20)

- PR \#2831 - Add spec for file `display_name` to core collection archive

## [insights-core-3.0.198-1614](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.198-1614) (2020-11-19)

- PR \#2797 - Add new parser *Doveconf* for command `/usr/bin/doveconf`
- PR \#2814 - Add capability to client to verify Ansible playbooks
- PR \#2825 - Fix error with collection of `sap_hdb_version` spec in core collection
- PR \#2826 - Fix error with collection of `is_aws`, `is_azure`, and `pcp_enabled` specs in core collection
- PR \#2827 - Fix issue with core collection where filtering command is captured in output
- PR \#2828 - Reenable collection of DNF modules data
- PR \#2829 - Fix error in collecting `foreach_execute` specs (Issue \#2824)

## [insights-core-3.0.197-1606](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.197-1606) (2020-11-12)

- PR \#2121 - Add combiner *RsyslogAllConf* and update parser *RsyslogConf* (PR \#2818, PR \#2819)
- PR \#2791 - Enable specs for _must_gather_ archives
- PR \#2792 - Add `--module` option to client to all running modules from the CLI
- PR \#2811 - Add new parser *UdevRules40Redhat* for file `/etc/udev/rules.d/40-redhat.rules`
- PR \#2815 - Enhance *parsr* module to include `line` convenience method (Issue \#2798)
- PR \#2816 - Ensure `branch_info` is collected as a raw file
- PR \#2817 - Add latest RHEL 8 kernels to *Uname* parser
- PR \#2820 - Update *YumRepoList* parser to correctly recognize Satellite repos
- PR \#2822 - Fix error in `df` command spec that triggered mounting of unmounted filesystems ([Bugzilla 1880030](https://bugzilla.redhat.com/show_bug.cgi?id=1880030))
- PR \#2823 - Fix error in spec `rsyslog_conf` for core collection

## [insights-core-3.0.196-1593](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.196-1593) (2020-11-05)

- Commit 0c4cbb0 - Update developer notes for client directory
- PR \#2796 - Add new parser *PostconfBuiltin* for command `/usr/sbin/postconf -C builtin`
- PR \#2804 - In client add capability to redact glob specs by symbolic name
- PR \#2810 - Modify *HDBVersion* parser to support collection of `sap_hdb_version` in JSON (Issue \#2812)

## [insights-core-3.0.195-1588](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.195-1588) (2020-11-01)

- PR \#2808 - In client fix minor typo in registration log message
- PR \#2809 - Ensure that *Sap* combiner uses short hostname for for comparisons

## [insights-core-3.0.194-1586](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.194-1586) (2020-10-29)

- PR \#2722 - In client cleanup temp dir created for egg download (Issue \#2721)
- PR \#2786 - Add new parser *SambaConfigs* for command spec `/usr/bin/testparm -s` and *SambaConfigsAll* for command spec `/usr/bin/testparm -v -s`
- PR \#2794 - Add new parser *NetworkManagerConfig* for file spec `/etc/NetworkManager/NetworkManager.conf`
- PR \#2795 - In client delete pid files on exit
- PR \#2799 - Save the raised exception raised by subscription manager spec in SubscriptionManagerListConsumed and SubscriptionManagerListInstalled parsers
- PR \#2802 - Add new parser DotNetVersion for command spec `/usr/bin/dotnet --version`
- PR \#2805 - Re-add spec *sap_hdb_version* for command `foreach_execute(sap_sid, "/usr/bin/sudo -iu %sadm HDB version", keep_rc=True)` for existing parser *HDBVersion*

## [insights-core-3.0.193-1576](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.193-1576) (2020-10-22)

- PR \#2767 - Add new parser *PHPConf* for file `first_file(["/etc/opt/rh/php73/php.ini", "/etc/opt/rh/php72/php.ini", "/etc/php.ini"])`
- PR \#2778 - Add new parser *VHostNetZeroCopyTx* for file `/sys/module/vhost_net/parameters/experimental_zcopytx`
- PR \#2782 - Fix warning in client when skipping a glob file spec
- PR \#2784 - Add new parser *AbrtCCppConf* for file `/etc/abrt/plugins/CCpp.conf`
- PR \#2787 - Fix bug in command line utilities (not client) for core archive collection (Issue \#2788)
- PR \#2789 - Add IBM cloud detection to *CloudProvider* combiner, refactor combiner
- PR \#2790 - Include rhsm_conf module in documentation build

## [insights-core-3.0.192](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.192-1568) (2020-10-19)

- PR \#2783 - Add new sosreport spec *firewall_cmd_list_all_zones* for file `sos_commands/firewalld/firewall-cmd_--list-all-zones`
- PR \#2785 - Add new spec *du_dirs* for command `foreach_execute(['/var/lib/candlepin/activemq-artemis'], "/bin/du -s -k %s")`

## [insights-core-3.0.191-1564](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.191-1564) (2020-10-14)

- PR \#2764 - Add collection stats file to client for data collection info
- PR \#2771 - Update client to generate log and lib dirs
- PR \#2781 - Fix client hosts file parsing for core collection and soscleaner

## [insights-core-3.0.7-270](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.7-270) (2018-03-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-261...insights-core-3.0.7-270)

**Closed issues:**

- . [\#1044](https://github.com/RedHatInsights/insights-core/issues/1044)

## [insights-core-3.0.6-261](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.6-261) (2018-03-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-257...insights-core-3.0.6-261)

**Closed issues:**

- Simplify Policy booleans handling \#96 [\#97](https://github.com/RedHatInsights/insights-core/issues/97)
- Falafel reference in image [\#23](https://github.com/RedHatInsights/insights-core/issues/23)

**Merged pull requests:**

- add new shared parser [\#129](https://github.com/RedHatInsights/insights-core/pull/129) ([xiaoyu74](https://github.com/xiaoyu74))
- Unitfiles parser enhanced to deal with all unit states and enhanced w… [\#114](https://github.com/RedHatInsights/insights-core/pull/114) ([jsvob](https://github.com/jsvob))
- Simplify 'Policy booleans' handling [\#96](https://github.com/RedHatInsights/insights-core/pull/96) ([PaulWay](https://github.com/PaulWay))

## [insights-core-1.41.0-43](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.41.0-43) (2017-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.40.0-23...insights-core-1.41.0-43)

**Closed issues:**

- Update ceph\_version to add version 2.2 \#105 [\#106](https://github.com/RedHatInsights/insights-core/issues/106)
- Removing previously used but abandoned test functions \#98 [\#99](https://github.com/RedHatInsights/insights-core/issues/99)
- Expose associated satellite information in system metadata \#65 [\#87](https://github.com/RedHatInsights/insights-core/issues/87)
- Added keyword\_search function \#69 [\#86](https://github.com/RedHatInsights/insights-core/issues/86)
- Rename from falafel to insights-core [\#8](https://github.com/RedHatInsights/insights-core/issues/8)

**Merged pull requests:**

- Update ceph\_version to add version 2.2 [\#107](https://github.com/RedHatInsights/insights-core/pull/107) ([shzhou12](https://github.com/shzhou12))
- Enhance parser openshift\_get in master [\#102](https://github.com/RedHatInsights/insights-core/pull/102) ([wushiqinlou](https://github.com/wushiqinlou))
- Removing previously used but abandoned test functions [\#98](https://github.com/RedHatInsights/insights-core/pull/98) ([PaulWay](https://github.com/PaulWay))
- Expose satellite information in the system metadata [\#89](https://github.com/RedHatInsights/insights-core/pull/89) ([jeudy100](https://github.com/jeudy100))
- Update docs and consolidate tests for parsers module [\#78](https://github.com/RedHatInsights/insights-core/pull/78) ([bfahr](https://github.com/bfahr))
- Added ``keyword\_search`` function [\#69](https://github.com/RedHatInsights/insights-core/pull/69) ([PaulWay](https://github.com/PaulWay))
- Rename parser module tests [\#68](https://github.com/RedHatInsights/insights-core/pull/68) ([PaulWay](https://github.com/PaulWay))
- Fix exception 'unexpected keyword argument' when calling a rule. [\#64](https://github.com/RedHatInsights/insights-core/pull/64) ([matysek](https://github.com/matysek))
- Fix netstat rows\_by\(\) method to implement AND rather than OR search [\#62](https://github.com/RedHatInsights/insights-core/pull/62) ([PaulWay](https://github.com/PaulWay))
- Bond module tests at 100% code coverage [\#58](https://github.com/RedHatInsights/insights-core/pull/58) ([PaulWay](https://github.com/PaulWay))
- AlternativesOutput mapper class definition [\#47](https://github.com/RedHatInsights/insights-core/pull/47) ([PaulWay](https://github.com/PaulWay))

## [falafel-1.40.0-23](https://github.com/RedHatInsights/insights-core/tree/falafel-1.40.0-23) (2017-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.39.0-11...falafel-1.40.0-23)

**Fixed bugs:**

- Transaction check error w/python-requests on falafel-1.38.0-25 installation [\#12](https://github.com/RedHatInsights/insights-core/issues/12)

**Closed issues:**

- uname parser fails for kernel 2.6.32-504.8.2.bgq.el6 [\#52](https://github.com/RedHatInsights/insights-core/issues/52)

**Merged pull requests:**

- Enhance grub\_conf coverage test to 100% [\#60](https://github.com/RedHatInsights/insights-core/pull/60) ([xiangce](https://github.com/xiangce))
- Remove the deprecated method: get\_expiration\_date\(\). \(master\) [\#59](https://github.com/RedHatInsights/insights-core/pull/59) ([JoySnow](https://github.com/JoySnow))
- df parser at 100% code coverage in tests [\#56](https://github.com/RedHatInsights/insights-core/pull/56) ([PaulWay](https://github.com/PaulWay))
- Skip newline 4 rhel6.3 [\#55](https://github.com/RedHatInsights/insights-core/pull/55) ([chenlizhong](https://github.com/chenlizhong))
- Fix uname to accept 5 sections in release string. \(master\) [\#54](https://github.com/RedHatInsights/insights-core/pull/54) ([jsvob](https://github.com/jsvob))
- SMARTctl parser at 100% code coverage in tests [\#51](https://github.com/RedHatInsights/insights-core/pull/51) ([PaulWay](https://github.com/PaulWay))
- tomcat\_web\_xml at 100% code coverage in tests [\#50](https://github.com/RedHatInsights/insights-core/pull/50) ([PaulWay](https://github.com/PaulWay))
- Enhance grub\_conf.py [\#49](https://github.com/RedHatInsights/insights-core/pull/49) ([xiangce](https://github.com/xiangce))
- Uptime improved processing and test coverage [\#48](https://github.com/RedHatInsights/insights-core/pull/48) ([PaulWay](https://github.com/PaulWay))
- Don't process blank lines from blkid [\#44](https://github.com/RedHatInsights/insights-core/pull/44) ([kylape](https://github.com/kylape))
- Revert deletion of test for systemctl\_show\_mariadb [\#41](https://github.com/RedHatInsights/insights-core/pull/41) ([bfahr](https://github.com/bfahr))
- Use correct base archive version [\#39](https://github.com/RedHatInsights/insights-core/pull/39) ([kylape](https://github.com/kylape))
- Moved test\_systemctl\_show\_mariadb.py to ./insights/parsers/tests [\#38](https://github.com/RedHatInsights/insights-core/pull/38) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Enhance httpd\_conf mapper and shared reducer [\#36](https://github.com/RedHatInsights/insights-core/pull/36) ([skontar](https://github.com/skontar))
- cpuinfo\_max\_freq mapper is no longer in use - removing mapper files entirely [\#34](https://github.com/RedHatInsights/insights-core/pull/34) ([PaulWay](https://github.com/PaulWay))
- Prepare for release on pypi [\#30](https://github.com/RedHatInsights/insights-core/pull/30) ([kylape](https://github.com/kylape))
- Updated multipath config to use mapper class [\#22](https://github.com/RedHatInsights/insights-core/pull/22) ([PaulWay](https://github.com/PaulWay))
- Enhance grub\_conf.py [\#21](https://github.com/RedHatInsights/insights-core/pull/21) ([xiangce](https://github.com/xiangce))
- Netstat mapper improvements [\#20](https://github.com/RedHatInsights/insights-core/pull/20) ([PaulWay](https://github.com/PaulWay))
- XFS info improvements [\#19](https://github.com/RedHatInsights/insights-core/pull/19) ([PaulWay](https://github.com/PaulWay))
- fd\_total\_limit mapper is unused - remove it and improve tests  [\#18](https://github.com/RedHatInsights/insights-core/pull/18) ([PaulWay](https://github.com/PaulWay))
- Added Shared Mapper for mariadb service parameters check [\#4](https://github.com/RedHatInsights/insights-core/pull/4) ([vishwanathjadhav](https://github.com/vishwanathjadhav))
- Enhance mapper certificates\_enddate.py [\#2](https://github.com/RedHatInsights/insights-core/pull/2) ([JoySnow](https://github.com/JoySnow))

## [falafel-1.39.0-11](https://github.com/RedHatInsights/insights-core/tree/falafel-1.39.0-11) (2017-05-31)
**Merged pull requests:**

- Adding missing files from rhel7 base archive [\#29](https://github.com/RedHatInsights/insights-core/pull/29) ([kylape](https://github.com/kylape))
- Use new naming conventions. [\#27](https://github.com/RedHatInsights/insights-core/pull/27) ([csams](https://github.com/csams))
- cpuinfo\_max\_freq mapper is no longer in use - removing mapper files entirely [\#17](https://github.com/RedHatInsights/insights-core/pull/17) ([PaulWay](https://github.com/PaulWay))
- Package archive tool data files [\#16](https://github.com/RedHatInsights/insights-core/pull/16) ([kylape](https://github.com/kylape))
- Update ansible repo references to RedHatInsights. [\#15](https://github.com/RedHatInsights/insights-core/pull/15) ([csams](https://github.com/csams))
- Add back the archive tool [\#6](https://github.com/RedHatInsights/insights-core/pull/6) ([kylape](https://github.com/kylape))



\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
