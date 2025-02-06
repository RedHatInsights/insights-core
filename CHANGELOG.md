# Change Log

## [Unreleased](https://github.com/RedHatInsights/insights-core/tree/HEAD)

# [insights-core-3.5.3](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.5.3) (2025-02-06)

- fix: remove /dev, /boot and /sys/firmware from ls_lanR ([PR 4347](https://github.com/RedHatInsights/insights-core/pull/4347))
- fix: remove the MustGatherContext and InsightsOperatorContext ([PR 4330](https://github.com/RedHatInsights/insights-core/pull/4330))
- fix(client): Status code should indicate registration status ([PR 4344](https://github.com/RedHatInsights/insights-core/pull/4344))
- fix(client): Support playbooks with unicode for Python 3.12+ ([PR 4342](https://github.com/RedHatInsights/insights-core/pull/4342))
- fix: default return value type of ls.listing_of() ([PR 4343](https://github.com/RedHatInsights/insights-core/pull/4343))
- fix: 'tail' filterable text files before filtering with 'grep' ([PR 4341](https://github.com/RedHatInsights/insights-core/pull/4341))
- Fix/cct-375: Change location of /tmp/insights-client.ppid ([PR 4269](https://github.com/RedHatInsights/insights-core/pull/4269))
- remove support of python 2.6 ([PR 4325](https://github.com/RedHatInsights/insights-core/pull/4325))

# [insights-core-3.5.2](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.5.2) (2025-01-16)

- spec: collect output of 'flatpak list' ([PR 4337](https://github.com/RedHatInsights/insights-core/pull/4337))
- fix(client): Serialize properly playbooks with empty maps ([PR 4340](https://github.com/RedHatInsights/insights-core/pull/4340))
- fix(client): Serialize properly playbooks with empty values ([PR 4338](https://github.com/RedHatInsights/insights-core/pull/4338))
- fix(client): Serialize properly escape characters ([PR 4335](https://github.com/RedHatInsights/insights-core/pull/4335))
- feat: Enhanced CephVersion parser to support more versions ([PR 4334](https://github.com/RedHatInsights/insights-core/pull/4334))
- fix: reverse the filters order when grep ([PR 4332](https://github.com/RedHatInsights/insights-core/pull/4332))
- feat: add spec parser and combiner for grubby_info ([PR 4329](https://github.com/RedHatInsights/insights-core/pull/4329))
- fix: set should be supported by add_filter ([PR 4333](https://github.com/RedHatInsights/insights-core/pull/4333))

# [insights-core-3.5.1](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.5.1) (2025-01-09)

- fix: error msg for compliance apiv2 assign/unassign ([PR 4328](https://github.com/RedHatInsights/insights-core/pull/4328))
- chore: sort out exceptions ([PR 4327](https://github.com/RedHatInsights/insights-core/pull/4327))
- chore: do not collect chkconfig on RHEL 7+ ([PR 4326](https://github.com/RedHatInsights/insights-core/pull/4326))
- fix(client): Display correct Insights URL ([PR 4297](https://github.com/RedHatInsights/insights-core/pull/4297))
- feat: enhance add_filter to support the max matched lines  ([PR 4303](https://github.com/RedHatInsights/insights-core/pull/4303))

# [insights-core-3.5.0](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.5.0) (2025-01-02)

- fix: typo options to the ls_lanRL spec ([PR 4323](https://github.com/RedHatInsights/insights-core/pull/4323))
- chore: remove planned deprecations for bumping 3.5.0 ([PR 4308](https://github.com/RedHatInsights/insights-core/pull/4308))
- feat: Enhance od_cpu_dma_latency miss strip ([PR 4321](https://github.com/RedHatInsights/insights-core/pull/4321))
- fix: do not print collection messages for compliance apiv2 options ([PR 4319](https://github.com/RedHatInsights/insights-core/pull/4319))
- feat: support line filter in spec Cleaner ([PR 4299](https://github.com/RedHatInsights/insights-core/pull/4299))
- feat: add new command fwupdmgr to spec.fw_security ([PR 4320](https://github.com/RedHatInsights/insights-core/pull/4320))
- fix: handler extra header lines in JSONParser ([PR 4317](https://github.com/RedHatInsights/insights-core/pull/4317))
- feat: remove collection of unused spec fw_devices ([PR 4318](https://github.com/RedHatInsights/insights-core/pull/4318))
- feat: Add is_rhel_ai to parser of os_release ([PR 4313](https://github.com/RedHatInsights/insights-core/pull/4313))
- feat: Add spec and parser for ilab_model_list ([PR 4311](https://github.com/RedHatInsights/insights-core/pull/4311))
- chore: Use caplog to verify log calls ([PR 4315](https://github.com/RedHatInsights/insights-core/pull/4315))
- test(client): Fix unusual race condition in tests ([PR 4316](https://github.com/RedHatInsights/insights-core/pull/4316))
- feat: add a base parser LazyLogFileOutput ([PR 4309](https://github.com/RedHatInsights/insights-core/pull/4309))
- fix(ci): Use dynamic repo URL for python26-test ([PR 4314](https://github.com/RedHatInsights/insights-core/pull/4314))
- fix(test): failures of test_eap_reports in some test env ([PR 4310](https://github.com/RedHatInsights/insights-core/pull/4310))
- No longer test the uploader JSON files ([PR 4304](https://github.com/RedHatInsights/insights-core/pull/4304))
- feat: download egg as per the RHEL major version ([PR 4266](https://github.com/RedHatInsights/insights-core/pull/4266))
- feat: Remove nmcli_conn_show_uuids datasource and parser ([PR 4307](https://github.com/RedHatInsights/insights-core/pull/4307))
- fix: invalid content of datasource aws_imdsv2_token ([PR 4305](https://github.com/RedHatInsights/insights-core/pull/4305))

# [insights-core-3.4.27](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.27) (2024-12-12)

- fix: ansi color code in parser TimeDateCtlStatus ([PR 4300](https://github.com/RedHatInsights/insights-core/pull/4300))
- fix(license): add NOTICE file specifying Red Had as the owner ([PR 4298](https://github.com/RedHatInsights/insights-core/pull/4298))
- chore: Improve and simplify logging ([PR 4194](https://github.com/RedHatInsights/insights-core/pull/4194))
- fix: change sysconfig specs as filterable=True ([PR 4295](https://github.com/RedHatInsights/insights-core/pull/4295))

# [insights-core-3.4.26](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.26) (2024-12-11)

- fix: add the missed compliance entry in compliance manifest ([PR 4302](https://github.com/RedHatInsights/insights-core/pull/4302))

# [insights-core-3.4.25](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.25) (2024-12-05)

- Add spec sysconfig_irqbalance ([PR 4294](https://github.com/RedHatInsights/insights-core/pull/4294))
- tools: refine the apply_spec_filters script ([PR 4292](https://github.com/RedHatInsights/insights-core/pull/4292))
- chore: remove 'check-docstring-first' from pre-commit-hooks ([PR 4293](https://github.com/RedHatInsights/insights-core/pull/4293))
- fix(client): checkin for unregistered hosts should fail ([PR 4274](https://github.com/RedHatInsights/insights-core/pull/4274))
- feat(compliance): RHINENG-8964 allow listing/assigning policies ([PR 4209](https://github.com/RedHatInsights/insights-core/pull/4209))
- feat: support more RHEL product key in subscription_manage_status ([PR 4291](https://github.com/RedHatInsights/insights-core/pull/4291))

# [insights-core-3.4.24](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.24) (2024-11-28)

- fix: handle empty value in krb5 config ([PR 4289](https://github.com/RedHatInsights/insights-core/pull/4289))
- fix: add six.text_type to the check of command_with_args ([PR 4290](https://github.com/RedHatInsights/insights-core/pull/4290))
- fix: proper error handling of AzurePublicIpv4Addresses ([PR 4288](https://github.com/RedHatInsights/insights-core/pull/4288))
- fix: remove the 'fstab_mounted.dirs' from the final ls args ([PR 4287](https://github.com/RedHatInsights/insights-core/pull/4287))
- ci: fix action errors of py26 test ([PR 4286](https://github.com/RedHatInsights/insights-core/pull/4286))
- chore: uname supports RHEL 9.5 ([PR 4284](https://github.com/RedHatInsights/insights-core/pull/4284))
- feat: Add datasource and parser for nmcli_conn_show_uuid ([PR 4273](https://github.com/RedHatInsights/insights-core/pull/4273))
- fix: Update combiner httpd_conf include ([PR 4275](https://github.com/RedHatInsights/insights-core/pull/4275))

# [insights-core-3.4.23](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.23) (2024-11-21)

- chore: add initial .pre-commit hooks ([PR 4271](https://github.com/RedHatInsights/insights-core/pull/4271))
- new spec and parser for cloud-init query ([PR 4272](https://github.com/RedHatInsights/insights-core/pull/4272))
- add ipa_default_conf spec back to collection ([PR 4270](https://github.com/RedHatInsights/insights-core/pull/4270))

# [insights-core-3.4.22](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.22) (2024-11-14)

- fix: do not import 'insights.client.constants' in spec_cleaner ([PR 4267](https://github.com/RedHatInsights/insights-core/pull/4267))
- feat(client): Improve test coverage of crypto.py ([PR 4268](https://github.com/RedHatInsights/insights-core/pull/4268))
- Speed up `keyword_search` by storing pre-processed data ([PR 3604](https://github.com/RedHatInsights/insights-core/pull/3604))
- feat(client): write .last-upload.results also after non-legacy uploads ([PR 4229](https://github.com/RedHatInsights/insights-core/pull/4229))

# [insights-core-3.4.21](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.21) (2024-11-07)

- FEAT: new custom filter 'fstab_mounted.dirs' to ls_lan spec ([PR 4255](https://github.com/RedHatInsights/insights-core/pull/4255))
- test: refine the tests used add_filter() ([PR 4265](https://github.com/RedHatInsights/insights-core/pull/4265))
- Fix: Enhance datasource httpd include upcase ([PR 4264](https://github.com/RedHatInsights/insights-core/pull/4264))
- Make test_urls test names consistent ([PR 4263](https://github.com/RedHatInsights/insights-core/pull/4263))
- Simplify re-raise for non-legacy ([PR 4254](https://github.com/RedHatInsights/insights-core/pull/4254))

# [insights-core-3.4.20](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.20) (2024-10-31)

- parsers: add parser for image builder facts (RHINENG-13943) ([PR 4261](https://github.com/RedHatInsights/insights-core/pull/4261))
- Catch Timeout on test connection ([PR 4211](https://github.com/RedHatInsights/insights-core/pull/4211))
- Remove double exception print ([PR 4246](https://github.com/RedHatInsights/insights-core/pull/4246))
- Add subscription_manager_status spec file path for sos_archive ([PR 4260](https://github.com/RedHatInsights/insights-core/pull/4260))

# [insights-core-3.4.19](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.19) (2024-10-24)

- test(ci/cd:py26): download pkgs instead of using personal repo ([PR 4251](https://github.com/RedHatInsights/insights-core/pull/4251))
- Catch Timeout on test urls ([PR 4248](https://github.com/RedHatInsights/insights-core/pull/4248))
- fix: do not obfuscate in runtime but in archive only ([PR 4249](https://github.com/RedHatInsights/insights-core/pull/4249))
- test: test_httpd_conf_files_main_miss failed httpd.conf exists ([PR 4257](https://github.com/RedHatInsights/insights-core/pull/4257))
- chore: refine the format of default_manifest in collect.py ([PR 4258](https://github.com/RedHatInsights/insights-core/pull/4258))
- test(ci/cd) update the config-path for gitleaks-action ([PR 4256](https://github.com/RedHatInsights/insights-core/pull/4256))

# [insights-core-3.4.18](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.18) (2024-10-17)

- fix: encoding issue in python2 env ([PR 4242](https://github.com/RedHatInsights/insights-core/pull/4242))
- test(ci/cd): add relevant commits to gitleaks allowlist ([PR 4245](https://github.com/RedHatInsights/insights-core/pull/4245))
- feat: New spec and the parser to collect nftables ruleset ([PR 4240](https://github.com/RedHatInsights/insights-core/pull/4240))
- FEAT: Add new parser LocaleCtlStatus ([PR 4247](https://github.com/RedHatInsights/insights-core/pull/4247))
- fix: nginx_ssl_certificate_files no longer depends on NginxConfTree ([PR 4241](https://github.com/RedHatInsights/insights-core/pull/4241))
- feat: New datasource "ld_library_path_of_global" and its parser ([PR 4236](https://github.com/RedHatInsights/insights-core/pull/4236))
- chore: remove useless lines and hostnames from tests and doc ([PR 4244](https://github.com/RedHatInsights/insights-core/pull/4244))

# [insights-core-3.4.17](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.17) (2024-10-10)

- fix: set no_redact for spec sshd_test_mode ([PR 4243](https://github.com/RedHatInsights/insights-core/pull/4243))
- New spec "/etc/rhc/config.toml" and parser ([PR 4239](https://github.com/RedHatInsights/insights-core/pull/4239))
- fix: update ls specs, parser definition & test files to support new options ([PR 4234](https://github.com/RedHatInsights/insights-core/pull/4234))
- feat: add ceph specs 'ceph_v' and 'ceph_insights' to sos_archive ([PR 4233](https://github.com/RedHatInsights/insights-core/pull/4233))
- fix: Update malware-detection tests ([PR 4235](https://github.com/RedHatInsights/insights-core/pull/4235))
- doc(conf): remove definiation of html_theme_path ([PR 4238](https://github.com/RedHatInsights/insights-core/pull/4238))
- refactor: remove legacy collection ([PR 4009](https://github.com/RedHatInsights/insights-core/pull/4009))
- test(ci/cd): add first-interaction action ([PR 4226](https://github.com/RedHatInsights/insights-core/pull/4226))
- doc: Update the contributing guidance ([PR 4222](https://github.com/RedHatInsights/insights-core/pull/4222))
- fix: datasource passed unicode to foreach_execute in py26 ([PR 4232](https://github.com/RedHatInsights/insights-core/pull/4232))
- fix: collect uname on RHEL 6 ([PR 4231](https://github.com/RedHatInsights/insights-core/pull/4231))
- test(ci/cd): add gitleaks pipeline ([PR 4225](https://github.com/RedHatInsights/insights-core/pull/4225))
- test: use Codecov instead of self script ([PR 4224](https://github.com/RedHatInsights/insights-core/pull/4224))
- test: fix the py26 flake8 error in ssl_certificate test ([PR 4223](https://github.com/RedHatInsights/insights-core/pull/4223))

# [insights-core-3.4.16](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.16) (2024-09-28)

- fix: Update value format of CupsBrowsedConf ([PR 4230](https://github.com/RedHatInsights/insights-core/pull/4230))

# [insights-core-3.4.15](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.15) (2024-09-27)

- feat: Add spec cups_browsed_conf ([PR 4227](https://github.com/RedHatInsights/insights-core/pull/4227))
- Revert "feat(client): write .last-upload.results also after non-legacy upload…" ([PR 4228](https://github.com/RedHatInsights/insights-core/pull/4228))

# [insights-core-3.4.14](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.14) (2024-09-26)

- fix: ssl_certificate no longer depends on HttpdConfTree ([PR 4220](https://github.com/RedHatInsights/insights-core/pull/4220))
- feat: add spec and parser for etc_sysconfig_kernel ([PR 4221](https://github.com/RedHatInsights/insights-core/pull/4221))
- feat(client): write .last-upload.results also after non-legacy uploads ([PR 4217](https://github.com/RedHatInsights/insights-core/pull/4217))
- fix: Fix issue 4218 in lspci combiner ([PR 4219](https://github.com/RedHatInsights/insights-core/pull/4219))

# [insights-core-3.4.13](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.13) (2024-09-19)

- test: refine the messages for coverage check in CI/CD ([PR 4213](https://github.com/RedHatInsights/insights-core/pull/4213))
- Enhance datasource httpd ignore include expanded inner ([PR 4214](https://github.com/RedHatInsights/insights-core/pull/4214))

# [insights-core-3.4.12](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.12) (2024-09-12)

- Fix skipped assertions for itests ([PR 4207](https://github.com/RedHatInsights/insights-core/pull/4207))
- feat(ci): add coverage check for changed python file ([PR 4200](https://github.com/RedHatInsights/insights-core/pull/4200))
- spec: stop collecting cloud_init_cfg_run ([PR 4212](https://github.com/RedHatInsights/insights-core/pull/4212))
- chore: add sensitive data checkpoint to PR template ([PR 4210](https://github.com/RedHatInsights/insights-core/pull/4210))

# [insights-core-3.4.11](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.11) (2024-09-05)

- feat: New spec and parser for host facts count of Satellite ([PR 4206](https://github.com/RedHatInsights/insights-core/pull/4206))
- test: fix test_copy_dir for coverage test ([PR 4204](https://github.com/RedHatInsights/insights-core/pull/4204))

# [insights-core-3.4.10](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.10) (2024-08-22)

- doc(README): remove the Py26 unsupported announcement ([PR 4199](https://github.com/RedHatInsights/insights-core/pull/4199))
- fix: correct NoFilterException in all datasource functions ([PR 4197](https://github.com/RedHatInsights/insights-core/pull/4197))
- FEAT: Add new parser RearLocalConf ([PR 4198](https://github.com/RedHatInsights/insights-core/pull/4198))
- fix: pass stdin=DEVNULL to Popen to avoid eating stdin from pipes ([PR 4189](https://github.com/RedHatInsights/insights-core/pull/4189))
- feat: New spec "lsattr <paths>" and its parser ([PR 4193](https://github.com/RedHatInsights/insights-core/pull/4193))
- feat(ci): add workflow to build egg for PRs and pushes ([PR 4190](https://github.com/RedHatInsights/insights-core/pull/4190))
- fix: handle non-existing configuration in SSSDConfAll ([PR 4192](https://github.com/RedHatInsights/insights-core/pull/4192))

# [insights-core-3.4.9](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.9) (2024-08-15)

- fix: Snyk CWE-295 issue in remote_resource module ([PR 4188](https://github.com/RedHatInsights/insights-core/pull/4188))
- fix: ausearch spec takes audit.log as input instead of stdin ([PR 4186](https://github.com/RedHatInsights/insights-core/pull/4186))
- chore: Skip empty spec only when collecting ([PR 4183](https://github.com/RedHatInsights/insights-core/pull/4183))

# [insights-core-3.4.8](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.8) (2024-08-08)

- Fix and test IdM related parsers and combiners ([PR 4178](https://github.com/RedHatInsights/insights-core/pull/4178))
- fix: insights-client failed, when --group was used ([PR 4070](https://github.com/RedHatInsights/insights-core/pull/4070))
- fix: single quoted string parse of os_release ([PR 4184](https://github.com/RedHatInsights/insights-core/pull/4184))
- fix: Run subshells with LC_ALL=C.UTF-8 ([PR 4182](https://github.com/RedHatInsights/insights-core/pull/4182))

# [insights-core-3.4.7](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.7) (2024-08-01)

- test: Add more playbooks to verifier's test suite ([PR 4170](https://github.com/RedHatInsights/insights-core/pull/4170))
- feat: Iterate over all plays in a playbook ([PR 4169](https://github.com/RedHatInsights/insights-core/pull/4169))
- fix: 'filterable' specs were skipped incorrectly when running plugins ([PR 4176](https://github.com/RedHatInsights/insights-core/pull/4176))
- fix: Properly serialize playbook strings containing quote marks ([PR 4175](https://github.com/RedHatInsights/insights-core/pull/4175))
- fix: do not encode(utf-8) when writing spec content to disk in py2 ([PR 4179](https://github.com/RedHatInsights/insights-core/pull/4179))
- feat: introduce a new TextFileOutput base parser ([PR 4148](https://github.com/RedHatInsights/insights-core/pull/4148))
- fix: Prevent test teardown issues of fast_fetch ([PR 4172](https://github.com/RedHatInsights/insights-core/pull/4172))
- feat: drop URLCache and associated code ([PR 4173](https://github.com/RedHatInsights/insights-core/pull/4173))

# [insights-core-3.4.6](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.6) (2024-07-25)

- fix: Remove --force-reregister command ([PR 4162](https://github.com/RedHatInsights/insights-core/pull/4162))
- feat: update specs for parser crictl_logs ([PR 4171](https://github.com/RedHatInsights/insights-core/pull/4171))
- feat: add parser for spec nvidia_smi_l ([PR 4174](https://github.com/RedHatInsights/insights-core/pull/4174))

# [insights-core-3.4.5](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.5) (2024-07-18)

- feat(pgp): Use crypto.py during Egg and Collection verification ([PR 4131](https://github.com/RedHatInsights/insights-core/pull/4131))

# [insights-core-3.4.4](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.4) (2024-07-18)

- feat: Add spec etc_sysconfig_pcs and parser ([PR 4167](https://github.com/RedHatInsights/insights-core/pull/4167))
- feat: New spec "/sys/class/tty/console/active" and parser ([PR 4165](https://github.com/RedHatInsights/insights-core/pull/4165))
- feat: New spec "/etc/securetty" and parser ([PR 4166](https://github.com/RedHatInsights/insights-core/pull/4166))
- feat: New spec "/etc/pam.d/login" and parser ([PR 4164](https://github.com/RedHatInsights/insights-core/pull/4164))
- chore: remove collection of cups_pdd ([PR 4168](https://github.com/RedHatInsights/insights-core/pull/4168))
- chore: re-write the OsRelease parser ([PR 4163](https://github.com/RedHatInsights/insights-core/pull/4163))
- doc(README): Python 2.6 unsupported announcement ([PR 4161](https://github.com/RedHatInsights/insights-core/pull/4161))
- fix: all SyntaxWarning and some of the DeprecationWarning ([PR 4154](https://github.com/RedHatInsights/insights-core/pull/4154))
- feat: collect the file /run/cloud-init/cloud.cfg for analytics ([PR 4155](https://github.com/RedHatInsights/insights-core/pull/4155))
- fix: Serialize playbooks manually on Python 3.12+ ([PR 4120](https://github.com/RedHatInsights/insights-core/pull/4120))

# [insights-core-3.4.3](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.3) (2024-07-11)

- feat: New spec and parser to get rsyslog CA cert expiration date ([PR 4139](https://github.com/RedHatInsights/insights-core/pull/4139))
- fix: handle another input format in parser NmapSsh ([PR 4158](https://github.com/RedHatInsights/insights-core/pull/4158))
- feat: replace deprecated datetime.utcnow() usage ([PR 4156](https://github.com/RedHatInsights/insights-core/pull/4156))
- feat: New spec "/usr/bin/pidstat" and parser ([PR 4153](https://github.com/RedHatInsights/insights-core/pull/4153))
- fix: collect sealert only when SELinux is not disabled ([PR 4150](https://github.com/RedHatInsights/insights-core/pull/4150))
- chore(ci): Add Python 3.12 to test matrix ([PR 4151](https://github.com/RedHatInsights/insights-core/pull/4151))
- chore: collect image builder's osbuild.facts ([PR 4119](https://github.com/RedHatInsights/insights-core/pull/4119))

# [insights-core-3.4.2](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.2) (2024-07-08)

- fix: show compliance errors only when compliance is specified ([PR 4152](https://github.com/RedHatInsights/insights-core/pull/4152))

# [insights-core-3.4.1](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.1) (2024-07-08)

- test: fix py26 test in CI/CD ([PR 4144](https://github.com/RedHatInsights/insights-core/pull/4144))
- feat: New spec and parser for /etc/kubernetes/kubelet.conf ([PR 4145](https://github.com/RedHatInsights/insights-core/pull/4145))
- FIX: remove reference for a deprecated module ([PR 4149](https://github.com/RedHatInsights/insights-core/pull/4149))
- fix: use ubi8 image instead of centos7 in the Dockerfile ([PR 4146](https://github.com/RedHatInsights/insights-core/pull/4146))

# [insights-core-3.4.0](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.4.0) (2024-07-04)

- feat: New spec "/proc/fs/cifs/DebugData" and parser ([PR 4138](https://github.com/RedHatInsights/insights-core/pull/4138))
- fix: lvm_system_devices contains hostname and should be obfuscated ([PR 4135](https://github.com/RedHatInsights/insights-core/pull/4135))
- chore: refine the msg for empty exception ([PR 4136](https://github.com/RedHatInsights/insights-core/pull/4136))
- doc: remove the doc-entries of unused parser ([PR 4137](https://github.com/RedHatInsights/insights-core/pull/4137))
- chore: remove planned deprecations for bumping 3.4.0 ([PR 4134](https://github.com/RedHatInsights/insights-core/pull/4134))
- fix: add dependencies to manifest for ausearch_insights_client ([PR 4133](https://github.com/RedHatInsights/insights-core/pull/4133))
- refactor: move compliance to specs.datasources ([PR 4124](https://github.com/RedHatInsights/insights-core/pull/4124))

# [insights-core-3.3.29](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.29) (2024-06-27)

- fix: change the validate order when collecting specs ([PR 4132](https://github.com/RedHatInsights/insights-core/pull/4132))
- fix: password regex skip lines end with 'password' ([PR 4130](https://github.com/RedHatInsights/insights-core/pull/4130))
- feat: new spec to collect SELinux issues via ausearch ([PR 4129](https://github.com/RedHatInsights/insights-core/pull/4129))

# [insights-core-3.3.28](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.28) (2024-06-20)

- chore: use datasoruce spec to collect blacklist_report ([PR 4127](https://github.com/RedHatInsights/insights-core/pull/4127))
- FEAT: Add new parser SubscriptionManagerStatus ([PR 4126](https://github.com/RedHatInsights/insights-core/pull/4126))
- feat: New spec and parser to get the expire date of ssl certificate in rsyslog ([PR 4125](https://github.com/RedHatInsights/insights-core/pull/4125))
- fix: strip lines before parsing for InstalledProductIDs ([PR 4128](https://github.com/RedHatInsights/insights-core/pull/4128))
- feat: include JSON format in malware detection results ([PR 4123](https://github.com/RedHatInsights/insights-core/pull/4123))
- feat: Enhance InstalledProductIDs to support more lines/filters ([PR 4122](https://github.com/RedHatInsights/insights-core/pull/4122))
- fix: debug print of egg versions doesn't handle corrupted eggs ([PR 4101](https://github.com/RedHatInsights/insights-core/pull/4101))

# [insights-core-3.3.27](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.27) (2024-06-13)

- refactor: move malware_detection to specs.datasources ([PR 4117](https://github.com/RedHatInsights/insights-core/pull/4117))
- fix(test): Catch errors caused by GPG ([PR 4121](https://github.com/RedHatInsights/insights-core/pull/4121))
- chore(test): Add unit tests for playbook verification ([PR 4115](https://github.com/RedHatInsights/insights-core/pull/4115))
- chore(test): Move existing playbook verifier tests into a class ([PR 4115](https://github.com/RedHatInsights/insights-core/pull/4115))
- chore: playbook verifier: Simplify the logic and structure ([PR 4115](https://github.com/RedHatInsights/insights-core/pull/4115))
- chore: playbook verifier: Update function/variable names ([PR 4115](https://github.com/RedHatInsights/insights-core/pull/4115))
- chore: Drop vendorized oyaml from playbook verifier ([PR 4115](https://github.com/RedHatInsights/insights-core/pull/4115))

# [insights-core-3.3.26](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.26) (2024-06-06)

- Add spec falconctl version ([PR 4114](https://github.com/RedHatInsights/insights-core/pull/4114))
- feat: exclude empty files during core collection ([PR 4113](https://github.com/RedHatInsights/insights-core/pull/4113))

# [insights-core-3.3.25](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.25) (2024-05-30)

- feat: enhance falconctl_aid exception parsing ([PR 4112](https://github.com/RedHatInsights/insights-core/pull/4112))
- chore: uname supports RHEL 8.10 ([PR 4110](https://github.com/RedHatInsights/insights-core/pull/4110))

# [insights-core-3.3.24](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.24) (2024-05-23)

- fix: TypeError in ethtool.Ring ([PR 4098](https://github.com/RedHatInsights/insights-core/pull/4098))
- fix: correct the root of SerializedArchiveContext ([PR 4109](https://github.com/RedHatInsights/insights-core/pull/4109))
- feat: new spec and parser for falconctl_aid ([PR 4107](https://github.com/RedHatInsights/insights-core/pull/4107))
- fix: 'NoneType' AttributeError in insights-info ([PR 4105](https://github.com/RedHatInsights/insights-core/pull/4105))
- fix: add manifest option back to insights.collect() ([PR 4106](https://github.com/RedHatInsights/insights-core/pull/4106))

# [insights-core-3.3.23](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.23) (2024-05-16)

- feat: Improve debugging experience ([PR 4094](https://github.com/RedHatInsights/insights-core/pull/4094))
- fix: env INSIGHTS_FILTERS_ENABLED no longer works ([PR 4104](https://github.com/RedHatInsights/insights-core/pull/4104))
- feat: Add parser sshd_config_d back ([PR 4102](https://github.com/RedHatInsights/insights-core/pull/4102))
- fix: Make utilities.write_to_disk use current time by default ([PR 4022](https://github.com/RedHatInsights/insights-core/pull/4022))

# [insights-core-3.3.22](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.22) (2024-05-10)

- fix: only non-filter exception can terminate the first_file spec ([PR 4100](https://github.com/RedHatInsights/insights-core/pull/4100))

# [insights-core-3.3.21](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.21) (2024-05-09)

- feat: clean (obfuscate/redact) specs in memory ([PR 4055](https://github.com/RedHatInsights/insights-core/pull/4055))
- feat: Add parser nmap ([PR 4092](https://github.com/RedHatInsights/insights-core/pull/4092))
- fix: no context and datasource when running against insights-archive ([PR 4082](https://github.com/RedHatInsights/insights-core/pull/4082))
- feat: Add parser db2 commands ([PR 4089](https://github.com/RedHatInsights/insights-core/pull/4089))
- fix: special chars in nginx directive name ([PR 4095](https://github.com/RedHatInsights/insights-core/pull/4095))
- fix: canonical facts was not obfuscated when '--checkin' ([PR 4090](https://github.com/RedHatInsights/insights-core/pull/4090))
- Add spec cups_ppd ([PR 4096](https://github.com/RedHatInsights/insights-core/pull/4096))
- fix: ParseException raising in parsers.scsi ([PR 4097](https://github.com/RedHatInsights/insights-core/pull/4097))
- chore: uname supports RHEL 9.4 ([PR 4093](https://github.com/RedHatInsights/insights-core/pull/4093))

# [insights-core-3.3.20](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.20) (2024-04-25)

- Feat: enhance combiners sudoers ([PR 4088](https://github.com/RedHatInsights/insights-core/pull/4088))
- bug: Fix nginx conf parser for empty quoted params ([PR 4087](https://github.com/RedHatInsights/insights-core/pull/4087))
- fix: obfuscate/redact the facts for legacy_upload=False ([PR 4085](https://github.com/RedHatInsights/insights-core/pull/4085))

# [insights-core-3.3.19](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.19) (2024-04-18)

- chore: print warning when 'machine_id' is skipped for redaction ([PR 4073](https://github.com/RedHatInsights/insights-core/pull/4073))
- feat: extend Specs.ps_eo_cmd to deprecate Specs.ps_eo ([PR 4066](https://github.com/RedHatInsights/insights-core/pull/4066))
- feat: add "nvidia-smi -L" command to collect gpu data ([PR 4083](https://github.com/RedHatInsights/insights-core/pull/4083))
- fix: deprecated parser usage in combiner.rhsm_release ([PR 4078](https://github.com/RedHatInsights/insights-core/pull/4078))
- feat: add filter to Specs.subscription_manager_facts ([PR 4080](https://github.com/RedHatInsights/insights-core/pull/4080))

# [insights-core-3.3.18](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.18) (2024-04-11)

- feat: add spec to collect pmlogsummary of PCP Raw data ([PR 4064](https://github.com/RedHatInsights/insights-core/pull/4064))
- feat: imporve Cleaner.clean_content to process filters ([PR 4076](https://github.com/RedHatInsights/insights-core/pull/4076))
- fix: workaround/skip password redaction for special case ([PR 4074](https://github.com/RedHatInsights/insights-core/pull/4074))
- fix: save_as of command_with_args cannot be a directory ([PR 4069](https://github.com/RedHatInsights/insights-core/pull/4069))
- feat: Enhance luksmeta parser ([PR 4072](https://github.com/RedHatInsights/insights-core/pull/4072))
- chore: use the uploader.json in '/testing' for unit test ([PR 4071](https://github.com/RedHatInsights/insights-core/pull/4071))

# [insights-core-3.3.17](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.17) (2024-04-04)

- fix: Update falconctl name ([PR 4068](https://github.com/RedHatInsights/insights-core/pull/4068))
- fix: support commands/files in file-redaction.yaml per manual ([PR 4059](https://github.com/RedHatInsights/insights-core/pull/4059))
- Fix: Fix LogRotateConfPEG cannot handle '=' ([PR 3967](https://github.com/RedHatInsights/insights-core/pull/3967))
- feat: collect specs in order based on given priority ([PR 4062](https://github.com/RedHatInsights/insights-core/pull/4062))

# [insights-core-3.3.16](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.16) (2024-03-26)

- feat: Reuse subscription-manager identity for machine-id ([PR 4057](https://github.com/RedHatInsights/insights-core/pull/4057))

# [insights-core-3.3.15](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.15) (2024-03-26)

- Re-do "fix: check status created a machine-id file (3965)" ([PR 4032](https://github.com/RedHatInsights/insights-core/pull/4032))
- fix(setup): Allow running setup.py from non-current directory ([PR 4065](https://github.com/RedHatInsights/insights-core/pull/4065))

# [insights-core-3.3.14](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.14) (2024-03-21)

- refactor: avoid passing duplicated mainfest to insights.collect() ([PR 4058](https://github.com/RedHatInsights/insights-core/pull/4058))
- fix: incorrect deps in default_manifest for HttpdConfTree combiner ([PR 4063](https://github.com/RedHatInsights/insights-core/pull/4063))
- fix: Correct the dep parser to collect "nginx_ssl_certificate_files" ([PR 4060](https://github.com/RedHatInsights/insights-core/pull/4060))
- fix: when all content are redacted, empty the file ([PR 4051](https://github.com/RedHatInsights/insights-core/pull/4051))

# [insights-core-3.3.13](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.13) (2024-03-14)

- fix: ContainerMssqlApiAssessment ParseException ([PR 4050](https://github.com/RedHatInsights/insights-core/pull/4050))
- fix: get bios_uuid (system_uuid) from dmidecode correctly ([PR 4052](https://github.com/RedHatInsights/insights-core/pull/4052))
- feat: collect LEAPP_* and CONVERT2RHEL_ env vars in migration-results ([PR 4037](https://github.com/RedHatInsights/insights-core/pull/4037))
- FEAT: Add new parser SystemctlGetDefault ([PR 4048](https://github.com/RedHatInsights/insights-core/pull/4048))
- refactor: generate 'canonical_facts' from Parsers instead of Specs ([PR 4047](https://github.com/RedHatInsights/insights-core/pull/4047))
- fix: subscription-manager identity should be obfuscated with hostname ([PR 4046](https://github.com/RedHatInsights/insights-core/pull/4046))
- fix: missed passing 'cleaner' to super of ContainerProvider" ([PR 4044](https://github.com/RedHatInsights/insights-core/pull/4044))
- fix: unexpect kwargs save_as ([PR 4043](https://github.com/RedHatInsights/insights-core/pull/4043))

# [insights-core-3.3.12](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.12) (2024-03-07)

- feat: make spec_cleaner support clean file content ([PR 4033](https://github.com/RedHatInsights/insights-core/pull/4033))
- Add parser falcontcl_backend_rfm ([PR 4039](https://github.com/RedHatInsights/insights-core/pull/4039))
- Fix: AllKrb5Conf cannot handle 'includedir' configured under /etc/krb5.conf.d/ ([PR 4041](https://github.com/RedHatInsights/insights-core/pull/4041))
- fix: Enhance "RHUIReleaseVer" to support "7Server" format ([PR 4038](https://github.com/RedHatInsights/insights-core/pull/4038))

# [insights-core-3.3.11](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.11) (2024-02-29)

- Deprecate pvs lvs vgs ([PR 4025](https://github.com/RedHatInsights/insights-core/pull/4025))
- Add httpd spec insights_archive ([PR 4036](https://github.com/RedHatInsights/insights-core/pull/4036))
- Add miss dependency specs ([PR 4020](https://github.com/RedHatInsights/insights-core/pull/4020))
- feat: New spec "rhui_releasever" and parser ([PR 4029](https://github.com/RedHatInsights/insights-core/pull/4029))
- fix: save_as in meta_data should reflect the actual config ([PR 4035](https://github.com/RedHatInsights/insights-core/pull/4035))
- fix: datasource should not be deserialized by RawProvider ([PR 4034](https://github.com/RedHatInsights/insights-core/pull/4034))
- Deprecate the spec "rhui_set_release" and parser ([PR 4030](https://github.com/RedHatInsights/insights-core/pull/4030))

# [insights-core-3.3.10](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.10) (2024-02-22)

- fixes: Update combiner "RhsmRelease" ([PR 4027](https://github.com/RedHatInsights/insights-core/pull/4027))
- feat: New spec /var/log/cron and parser ([PR 4026](https://github.com/RedHatInsights/insights-core/pull/4026))
- fix(client): Update typo in a log statement ([PR 4023](https://github.com/RedHatInsights/insights-core/pull/4023))

# [insights-core-3.3.9](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.9) (2024-02-14)

- Revert "RHEL-2480: Do not create /root/.gnupg/ directory by accident" ([PR 4021](https://github.com/RedHatInsights/insights-core/pull/4021))

# [insights-core-3.3.8](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.8) (2024-02-13)

- fix: hostname is not obfuscated when specify display_name ([PR 4019](https://github.com/RedHatInsights/insights-core/pull/4019))

# [insights-core-3.3.7](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.7) (2024-02-09)

- fix: resolve missing insights-client.ppid error ([PR 4002](https://github.com/RedHatInsights/insights-core/pull/4002))
- Revert "fix: check status created a machine-id file (3965)" ([PR 4018](https://github.com/RedHatInsights/insights-core/pull/4018))

# [insights-core-3.3.6](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.6) (2024-02-08)

- fix: no such attribute error ([PR 4015](https://github.com/RedHatInsights/insights-core/pull/4015))
- fix: spec mdadm_D to render arg /dev/md* properly ([PR 4011](https://github.com/RedHatInsights/insights-core/pull/4011))
- feat: Add permanent hardware addr to bond parser ([PR 4016](https://github.com/RedHatInsights/insights-core/pull/4016))
- feat: collect PCP RAW data per 'ros_collect' set in insights-client.conf ([PR 3979](https://github.com/RedHatInsights/insights-core/pull/3979))
- fix: RHINENG-8044 create facts file with right permission and respecting umask ([PR 4014](https://github.com/RedHatInsights/insights-core/pull/4014))
- fix: check status created a machine-id file ([PR 3965](https://github.com/RedHatInsights/insights-core/pull/3965))
- fix(test): Make the malware detection detect Podman containers ([PR 4012](https://github.com/RedHatInsights/insights-core/pull/4012))
- fix(test): spec cleaner tests are using 'is' for comparing strings ([PR 4013](https://github.com/RedHatInsights/insights-core/pull/4013))
- RHEL-2480: Do not create /root/.gnupg/ directory by accident ([PR 3930](https://github.com/RedHatInsights/insights-core/pull/3930))

# [insights-core-3.3.5](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.5) (2024-02-01)

- feat: New spec "rhui-set-release" and parser ([PR 3998](https://github.com/RedHatInsights/insights-core/pull/3998))
- fix(yum_udpates): load dnf plugins ([PR 4007](https://github.com/RedHatInsights/insights-core/pull/4007))
- feat: deprecate parser SubscriptionManagerReleaseShow ([PR 4006](https://github.com/RedHatInsights/insights-core/pull/4006))
- feat: move obfuscation and redaction to core (with specs) ([PR 3679](https://github.com/RedHatInsights/insights-core/pull/3679))
- fix: rmtree error in playbook verification tests of py27 ([PR 4008](https://github.com/RedHatInsights/insights-core/pull/4008))
- fix: change log level to debug for ValueError in serde.py ([PR 4001](https://github.com/RedHatInsights/insights-core/pull/4001))
- fix(compliance): RHINENG-1935 handle non-list responses from inventory ([PR 4004](https://github.com/RedHatInsights/insights-core/pull/4004))
- feat: add warning message when BASIC auth is used ([PR 3997](https://github.com/RedHatInsights/insights-core/pull/3997))
- fix: resolve missing 'insights-client/lib' error in playbook verification tests ([PR 4005](https://github.com/RedHatInsights/insights-core/pull/4005))

# [insights-core-3.3.4](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.4) (2024-01-26)

- fix: 'Save As' as a limited workaround ([PR 4000](https://github.com/RedHatInsights/insights-core/pull/4000))

# [insights-core-3.3.3](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.3) (2024-01-25)

- feat: new 'Save As' feature to core collection ([PR 3992](https://github.com/RedHatInsights/insights-core/pull/3992))
- Add parser sshd_test_mode ([PR 3996](https://github.com/RedHatInsights/insights-core/pull/3996))
- fix: wrong spec file path of UdevRules66MD ([PR 3995](https://github.com/RedHatInsights/insights-core/pull/3995))

# [insights-core-3.3.2](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.2) (2024-01-18)

- Enhance crypto_policies_opensshserver for rhel9 ([PR 3994](https://github.com/RedHatInsights/insights-core/pull/3994))

# [insights-core-3.3.1](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.1) (2024-01-11)

- Chore: Update data structure of xfs_quota to fix taking too long to run ([PR 3989](https://github.com/RedHatInsights/insights-core/pull/3989))
- feat: Add "systemd" to the spec "rpm -V" ([PR 3990](https://github.com/RedHatInsights/insights-core/pull/3990))
- feat: New spec to get the count of revoked certificates on satellite ([PR 3988](https://github.com/RedHatInsights/insights-core/pull/3988))
- Add spec "/var/log/candlepin/candlepin.log" back ([PR 3987](https://github.com/RedHatInsights/insights-core/pull/3987))
- fix: Fix problem parsing mnt opt quotes ([PR 3985](https://github.com/RedHatInsights/insights-core/pull/3985))
- Update readthedocs to version 2 ([PR 3986](https://github.com/RedHatInsights/insights-core/pull/3986))

# [insights-core-3.3.0](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.3.0) (2024-01-04)

- fix: Fix issue with mount parsers mount option parsing ([PR 3984](https://github.com/RedHatInsights/insights-core/pull/3984))
- INSPEC-443: new spec and parser for bootc status ([PR 3982](https://github.com/RedHatInsights/insights-core/pull/3982))
- fixes: Fix a bug about spec "modinfo_filtered_modules" ([PR 3981](https://github.com/RedHatInsights/insights-core/pull/3981))
- fix: enhance "include" of httpd_conf spec ([PR 3977](https://github.com/RedHatInsights/insights-core/pull/3977))
- chore: remove planned deprecations - 3.3.0 ([PR 3978](https://github.com/RedHatInsights/insights-core/pull/3978))

# [insights-core-3.2.27](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.27) (2023-12-14)

- INSPEC-432: collect convert2rhel.facts ([PR 3972](https://github.com/RedHatInsights/insights-core/pull/3972))
- fix: Remove pruning client code from rpm ([PR 3976](https://github.com/RedHatInsights/insights-core/pull/3976))
- Removed unnecessary parameter from `str` method ([PR 3975](https://github.com/RedHatInsights/insights-core/pull/3975))
- feat: update eap json report spec ([PR 3964](https://github.com/RedHatInsights/insights-core/pull/3964))
- chore: Remove the specs and parsers related to xfs_db command ([PR 3973](https://github.com/RedHatInsights/insights-core/pull/3973))

# [insights-core-3.2.26](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.26) (2023-12-07)

- fix: unify parser for dse_ldif.py files ([PR 3970](https://github.com/RedHatInsights/insights-core/pull/3970))
- feat: New spec "/etc/sysconfig/sbd" and parser ([PR 3969](https://github.com/RedHatInsights/insights-core/pull/3969))
- fix: avoid AttributeError raised by filterable check when run rules ([PR 3968](https://github.com/RedHatInsights/insights-core/pull/3968))
- fix: do not collect filterable specs when no filters ([PR 3959](https://github.com/RedHatInsights/insights-core/pull/3959))

# [insights-core-3.2.25](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.25) (2023-11-30)

- fix: change Specs.yum_conf to filterable=True ([PR 3963](https://github.com/RedHatInsights/insights-core/pull/3963))
- feat: Add spec "httpd_limits" back ([PR 3962](https://github.com/RedHatInsights/insights-core/pull/3962))
- fix: Enhance datasource "satellite_missed_pulp_agent_queues" ([PR 3960](https://github.com/RedHatInsights/insights-core/pull/3960))
- test: remove the temporarily generated dir in test_client ([PR 3961](https://github.com/RedHatInsights/insights-core/pull/3961))

# [insights-core-3.2.24](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.24) (2023-11-16)

- fix: Enhance spec "satellite_settings" and parser to support satellite 6.14 ([PR 3952](https://github.com/RedHatInsights/insights-core/pull/3952))
- chore: uname supports RHEL 8.9 ([PR 3957](https://github.com/RedHatInsights/insights-core/pull/3957))
- fix: ethtool.Ring parsing be blocked by TypeError ([PR 3954](https://github.com/RedHatInsights/insights-core/pull/3954))
- fix: ls_laZ handling "?" as rhel8 selinux context ([PR 3956](https://github.com/RedHatInsights/insights-core/pull/3956))
- chore: remove specs not used by rules ([PR 3821](https://github.com/RedHatInsights/insights-core/pull/3821))
- fix: add filter to dependency datasource ([PR 3949](https://github.com/RedHatInsights/insights-core/pull/3949))

# [insights-core-3.2.23](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.23) (2023-11-09)

- feat: uname supports RHEL 9.3 ([PR 3950](https://github.com/RedHatInsights/insights-core/pull/3950))

# [insights-core-3.2.22](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.22) (2023-11-02)

- feat: Add one more arg to the command "ps -eo" ([PR 3945](https://github.com/RedHatInsights/insights-core/pull/3945))
- feat: New spec "/var/log/squid/cache.log" and parser ([PR 3947](https://github.com/RedHatInsights/insights-core/pull/3947))
- fix: make Specs.rhsm_conf as filterable=True ([PR 3919](https://github.com/RedHatInsights/insights-core/pull/3919))

# [insights-core-3.2.21](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.21) (2023-10-26)

- feat: Add spec basic_insights_client ([PR 3943](https://github.com/RedHatInsights/insights-core/pull/3943))

# [insights-core-3.2.20](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.20) (2023-10-19)

- fix: compatible support built-in files for old archives ([PR 3937](https://github.com/RedHatInsights/insights-core/pull/3937))
- Add warning to yum_log exclusion ([PR 3941](https://github.com/RedHatInsights/insights-core/pull/3941))
- fix: unexpected Exception of YumRepoList caused by localization ([PR 3855](https://github.com/RedHatInsights/insights-core/pull/3855))
- fix: Fix bug of ls_parser when handling "major" and "minor" in e.g. "ls -lZ /dev" ([PR 3940](https://github.com/RedHatInsights/insights-core/pull/3940))
- fix: Replace "ls_lanRZ" and "ls_lanZ" with "ls_laRZ" and "ls_laZ" ([PR 3938](https://github.com/RedHatInsights/insights-core/pull/3938))
- test: not raise Exception when Component is filtered in parent Component ([PR 3933](https://github.com/RedHatInsights/insights-core/pull/3933))
- Exclude yum_log from IP obfuscation ([PR 3893](https://github.com/RedHatInsights/insights-core/pull/3893))

# [insights-core-3.2.19](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.19) (2023-10-12)

- Enhance chkconfig spec deps_isrhel6 ([PR 3935](https://github.com/RedHatInsights/insights-core/pull/3935))
- fix: Suspend the data collection for xfs_db command ([PR 3932](https://github.com/RedHatInsights/insights-core/pull/3932))
- feat: add do_filter option to run_test for rule test ([PR 3923](https://github.com/RedHatInsights/insights-core/pull/3923))
- fix: use get_dependencies in get_registry_points ([PR 3920](https://github.com/RedHatInsights/insights-core/pull/3920))
- fix: identify SAP instances per short type when InstanceType is missing ([PR 3931](https://github.com/RedHatInsights/insights-core/pull/3931))
- Enhance SAP combiner with update attributes name ([PR 3925](https://github.com/RedHatInsights/insights-core/pull/3925))

# [insights-core-3.2.18](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.18) (2023-09-28)

- feat: New spec and parser for xfs_db -r -c freesp command ([PR 3927](https://github.com/RedHatInsights/insights-core/pull/3927))
- Improve logging for disabled rule matches ([PR 3922](https://github.com/RedHatInsights/insights-core/pull/3922))
- fix: store_skips argument of run_input_data has no effect (3928) ([PR 3929](https://github.com/RedHatInsights/insights-core/pull/3929))
- Deprecate pyparsing usage in parsers ([PR 3911](https://github.com/RedHatInsights/insights-core/pull/3911))
- feat: New spec and parser for xfs_db -r -c frag command ([PR 3926](https://github.com/RedHatInsights/insights-core/pull/3926))
- fix: show internal DeprecationWarnings only when pytest ([PR 3924](https://github.com/RedHatInsights/insights-core/pull/3924))

# [insights-core-3.2.17](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.17) (2023-09-21)

- Download malware rules into /var/lib/insights ([PR 3921](https://github.com/RedHatInsights/insights-core/pull/3921))
- fix: raise Exception when adding filters to non-filterable datasource ([PR 3917](https://github.com/RedHatInsights/insights-core/pull/3917))

# [insights-core-3.2.16](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.16) (2023-09-14)

- FEAT: New rpm_v_package using foreach_execute ([PR 3915](https://github.com/RedHatInsights/insights-core/pull/3915))
- fix: Refactor iris relevant parsers and datasources ([PR 3914](https://github.com/RedHatInsights/insights-core/pull/3914))
- feat: New spec and parser for migration-results ([PR 3913](https://github.com/RedHatInsights/insights-core/pull/3913))
- chore: stop collecting .exp.sed from Specs (core collection) ([PR 3908](https://github.com/RedHatInsights/insights-core/pull/3908))

# [insights-core-3.2.15](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.15) (2023-09-08)

- feat: New spec "/etc/mail/sendmail.mc" ([PR 3910](https://github.com/RedHatInsights/insights-core/pull/3910))
- feat: collect built-in metadata in 'data' via datasource ([PR 3755](https://github.com/RedHatInsights/insights-core/pull/3755))
- RHINENG-1764: start processing every errata for available package ([PR 3909](https://github.com/RedHatInsights/insights-core/pull/3909))
- fix: do not download uploader.json when core_collect=True ([PR 3896](https://github.com/RedHatInsights/insights-core/pull/3896))
- FEAT: Add new parser LpstatQueuedJobs ([PR 3906](https://github.com/RedHatInsights/insights-core/pull/3906))
- fix: improve temporary directory ([PR 3905](https://github.com/RedHatInsights/insights-core/pull/3905))
- feat: Add glibc to rpm_V_packages Spec ([PR 3907](https://github.com/RedHatInsights/insights-core/pull/3907))
- Feat: Add new parser PostfixMaster ([PR 3898](https://github.com/RedHatInsights/insights-core/pull/3898))
- fix: flake8 error in py26 test of lvm ([PR 3904](https://github.com/RedHatInsights/insights-core/pull/3904))
- feat: Add new spec and parser for lvm fullreport cmd ([PR 3792](https://github.com/RedHatInsights/insights-core/pull/3792))
- feat: add spec and parser for udev 66-md-auto-re-add.rules ([PR 3902](https://github.com/RedHatInsights/insights-core/pull/3902))
- fix: skip new known invalid content for AWS parsers ([PR 3903](https://github.com/RedHatInsights/insights-core/pull/3903))
- fix: another attempt to fix the py26 CI/CD ([PR 3901](https://github.com/RedHatInsights/insights-core/pull/3901))

# [insights-core-3.2.14](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.14) (2023-08-31)

- refactor(client): remove hacky proxy code ([PR 3730](https://github.com/RedHatInsights/insights-core/pull/3730))
- feat: new test for symbolic_name in uploader.json ([PR 3899](https://github.com/RedHatInsights/insights-core/pull/3899))
- fix: remove Lssap from Sap combiner ([PR 3895](https://github.com/RedHatInsights/insights-core/pull/3895))
- fix: change tar command ([PR 3897](https://github.com/RedHatInsights/insights-core/pull/3897))

# [insights-core-3.2.13](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.13) (2023-08-25)

- fix: tar command ([PR 3894](https://github.com/RedHatInsights/insights-core/pull/3894))

# [insights-core-3.2.12](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.12) (2023-08-24)

- fix: revert change in path directory ([PR 3891](https://github.com/RedHatInsights/insights-core/pull/3891))
- fix: don't initial InsighsConfig in dup_machine_id_info ([PR 3888](https://github.com/RedHatInsights/insights-core/pull/3888))
- feat: improve temp directories ([PR 3878](https://github.com/RedHatInsights/insights-core/pull/3878))
- SPM-2113: allow re-generating dnf/yum cache on demand ([PR 3874](https://github.com/RedHatInsights/insights-core/pull/3874))
- feat: Apply malware disabled rules ([PR 3884](https://github.com/RedHatInsights/insights-core/pull/3884))

# [insights-core-3.2.11](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.11) (2023-08-17)

- feat: Add rendered content to json output ([PR 3881](https://github.com/RedHatInsights/insights-core/pull/3881))
- chore: add required dirs to LSlanR spec in parser ([PR 3875](https://github.com/RedHatInsights/insights-core/pull/3875))
- chore: collect '/etc/.exp.sed' ([PR 3880](https://github.com/RedHatInsights/insights-core/pull/3880))
- fixes: Add one more warning for LVM output ([PR 3882](https://github.com/RedHatInsights/insights-core/pull/3882))
- fix: Do not redact mssql_api_assessment ([PR 3886](https://github.com/RedHatInsights/insights-core/pull/3886))

# [insights-core-3.2.10](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.10) (2023-08-10)

- feat: add spec and parser of mdadm_d ([PR 3868](https://github.com/RedHatInsights/insights-core/pull/3868))
- fix: let OSRelease.release returns the prepared OS Name ([PR 3879](https://github.com/RedHatInsights/insights-core/pull/3879))
- feat: add spec and parser for /proc/buddyinfo ([PR 3877](https://github.com/RedHatInsights/insights-core/pull/3877))
- feat: add try/except in jinja2 content rendering ([PR 3876](https://github.com/RedHatInsights/insights-core/pull/3876))
- fix: update Uname parser to fix LooseVersion comparision error ([PR 3814](https://github.com/RedHatInsights/insights-core/pull/3814))
- fix: simplify OSRelease: stop when identified NON-RHEL ([PR 3873](https://github.com/RedHatInsights/insights-core/pull/3873))
- Handle exception when updating rules ([PR 3570](https://github.com/RedHatInsights/insights-core/pull/3570))
- fix: OSRelease when both os_release and redhat_release available ([PR 3872](https://github.com/RedHatInsights/insights-core/pull/3872))
- ESSNTL-5101: disable libdnf info logging ([PR 3871](https://github.com/RedHatInsights/insights-core/pull/3871))

# [insights-core-3.2.9](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.9) (2023-08-03)

- fix: don't redact ls_systemd_units to avoid issue#3858 ([PR 3870](https://github.com/RedHatInsights/insights-core/pull/3870))
- [INSPEC-414] collect .exp.sed for analysis ([PR 3869](https://github.com/RedHatInsights/insights-core/pull/3869))
- feat: Add parser intersystems_configuration_log ([PR 3861](https://github.com/RedHatInsights/insights-core/pull/3861))
- fix: datasource specs cannot be loaded during collection ([PR 3867](https://github.com/RedHatInsights/insights-core/pull/3867))
- feat: 2 new properties to OSRelease combiner ([PR 3863](https://github.com/RedHatInsights/insights-core/pull/3863))
- fix: use pre-build python26 instead of compiling it ([PR 3865](https://github.com/RedHatInsights/insights-core/pull/3865))
- fix: flake8 rule E721 ([PR 3864](https://github.com/RedHatInsights/insights-core/pull/3864))

# [insights-core-3.2.8](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.8) (2023-07-27)

- feat: New spec "/proc/sys/kernel/random/entropy_avail" ([PR 3860](https://github.com/RedHatInsights/insights-core/pull/3860)

# [insights-core-3.2.7](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.7) (2023-07-21)

- feat: modifying umask before creating log files ([PR 3820](https://github.com/RedHatInsights/insights-core/pull/3820))
- Fix: Enhance LogrotateConfAll Combiner ([PR 3853](https://github.com/RedHatInsights/insights-core/pull/3853))
- feat: revert the xfs_info spec ([PR 3857](https://github.com/RedHatInsights/insights-core/pull/3857))
- fix: Malware fix to handle cert_verify set in conf file ([PR 3856](https://github.com/RedHatInsights/insights-core/pull/3856))
- chore: discard the deprecation of LsBoot, LsDev and LsSysFirmware ([PR 3849](https://github.com/RedHatInsights/insights-core/pull/3849))
- Fix Compliance possible json decoding issue ([PR 3851](https://github.com/RedHatInsights/insights-core/pull/3851))

# [insights-core-3.2.6](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.6) (2023-07-13)

- FEAT: Add new parser XFSQuotaState ([PR 3850](https://github.com/RedHatInsights/insights-core/pull/3850))
- Handle module router request response format ([PR 3838](https://github.com/RedHatInsights/insights-core/pull/3838))
- RHINENG-761: Handle Compliance tailoring file request ([PR 3846](https://github.com/RedHatInsights/insights-core/pull/3846))
- feat: pass the client_config to the core collection ([PR 3839](https://github.com/RedHatInsights/insights-core/pull/3839))
- Add new fact to sub mgr facts filters ([PR 3848](https://github.com/RedHatInsights/insights-core/pull/3848))
- fix: Fix wrong filter reference ([PR 3842](https://github.com/RedHatInsights/insights-core/pull/3842))
- Update CI/CD to include python3.11 ([PR 3847](https://github.com/RedHatInsights/insights-core/pull/3847))

# [insights-core-3.2.5](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.5) (2023-07-06)

- feat: add safety check to methods of 'LS' Parsers ([PR 3841](https://github.com/RedHatInsights/insights-core/pull/3841))
- Revert "chore: remove unused spec lsinitrd_kdump_image (3644)" ([PR 3840](https://github.com/RedHatInsights/insights-core/pull/3840))
- feat: new Ls Parsers for 'ls' commands ([PR 3833](https://github.com/RedHatInsights/insights-core/pull/3833))
- Use SIGTERM for dnf command ([PR 3837](https://github.com/RedHatInsights/insights-core/pull/3837))
- fix(yum_updates): releasever and basearch ([PR 3835](https://github.com/RedHatInsights/insights-core/pull/3835))

# [insights-core-3.2.4](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.4) (2023-07-03)

- Revert "RHICOMPL-3862 Adjust insights-client to upload reports in the ARF format (#3829)" ([PR 3836](https://github.com/RedHatInsights/insights-core/pull/3836))
- fix: refactor the SubscriptionManageID parser ([PR 3834](https://github.com/RedHatInsights/insights-core/pull/3834))

# [insights-core-3.2.3](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.3) (2023-06-29)

- Feat: new spec "/usr/bin/iris list" and its parser  ([PR 3828](https://github.com/RedHatInsights/insights-core/pull/3828))
- fix: Add /host prefix to a few specs ([PR 3831](https://github.com/RedHatInsights/insights-core/pull/3831))
- RHICOMPL-3862 Adjust insights-client to upload reports in the ARF format ([PR 3829](https://github.com/RedHatInsights/insights-core/pull/3829))
- chore: uniform the deprecation warnings and docstring ([PR 3830](https://github.com/RedHatInsights/insights-core/pull/3830))
- fix: new spec and parser for eap runtime json reports ([PR 3825](https://github.com/RedHatInsights/insights-core/pull/3825))
- Use the existing cert_verify value, if set ([PR 3826](https://github.com/RedHatInsights/insights-core/pull/3826))
- fix: Using pip for python2.7 instead of python3x ([PR 3827](https://github.com/RedHatInsights/insights-core/pull/3827))
- Add malware-detection tests that use real yara ([PR 3822](https://github.com/RedHatInsights/insights-core/pull/3822))
- fix: CI test for python27 ([PR 3824](https://github.com/RedHatInsights/insights-core/pull/3824))
- feat: update Specs.yumlog to filterable=True ([PR 3810](https://github.com/RedHatInsights/insights-core/pull/3810))
- fix: Build python26 instead of install ([PR 3823](https://github.com/RedHatInsights/insights-core/pull/3823))

# [insights-core-3.2.2](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.2) (2023-06-15)

- Feat: new spec "/var/log/watchdog/*" and the parser ([PR 3819](https://github.com/RedHatInsights/insights-core/pull/3819))
- Feat: new spec "/etc/sysconfig/stonith" and its parser ([PR 3817](https://github.com/RedHatInsights/insights-core/pull/3817))
- feat: New spec to get repos which ingores source rpms on Satellite ([PR 3812](https://github.com/RedHatInsights/insights-core/pull/3812))
- feat: update logging file handler for logrotate ([PR 3765](https://github.com/RedHatInsights/insights-core/pull/3765))

# [insights-core-3.2.1](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.1) (2023-06-09)

- Enhance datasource kernel_module_list ([PR 3816](https://github.com/RedHatInsights/insights-core/pull/3816))

# [insights-core-3.2.0](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.2.0) (2023-06-08)

- Feat: new spec "ls -lan /etc/watchdog.d/" ([PR 3813](https://github.com/RedHatInsights/insights-core/pull/3813))
- fix: support inhibitor entries with missing remediations ([PR 3809](https://github.com/RedHatInsights/insights-core/pull/3809))
- chore: remove the planned deprecated modules from 3.2.0 ([PR 3811](https://github.com/RedHatInsights/insights-core/pull/3811))
- feat: beautify testcase deep_compare diff details ([PR 3804](https://github.com/RedHatInsights/insights-core/pull/3804))

# [insights-core-3.1.26](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.26) (2023-06-01)

- feat: add spec and parser for proc_keyusers ([PR 3802](https://github.com/RedHatInsights/insights-core/pull/3802))
- FEAT: Add new parser EtcMachineId ([PR 3805](https://github.com/RedHatInsights/insights-core/pull/3805))
- Feat: remove spec ls_rsyslog_errorfile ([PR 3803](https://github.com/RedHatInsights/insights-core/pull/3803))
- Feat: Add identity domain combiner ([PR 3790](https://github.com/RedHatInsights/insights-core/pull/3790))
- fix: correctly identify final segment of kernel version in uname ([PR 3801](https://github.com/RedHatInsights/insights-core/pull/3801))
- feat: enhance test to check the missing components ([PR 3798](https://github.com/RedHatInsights/insights-core/pull/3798))
- fix: uname pad release without el segment ([PR 3800](https://github.com/RedHatInsights/insights-core/pull/3800))
- feat: update SystemctlStatusAll and add its spec back ([PR 3797](https://github.com/RedHatInsights/insights-core/pull/3797))

# [insights-core-3.1.25](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.25) (2023-05-18)

- feat: New spec to get RHV hosts count on satellite and its parser ([PR 3794](https://github.com/RedHatInsights/insights-core/pull/3794))
- fix: add the lvm_conf back to sos_archive ([PR 3796](https://github.com/RedHatInsights/insights-core/pull/3796))
- Remove useless postgresql queries ([PR 3793](https://github.com/RedHatInsights/insights-core/pull/3793))
- feat: uname supports RHEL 8.8 ([PR 3795](https://github.com/RedHatInsights/insights-core/pull/3795))
- fix: Add missing multi_output=True for dnf_modules spec ([PR 3791](https://github.com/RedHatInsights/insights-core/pull/3791))

# [insights-core-3.1.24](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.24) (2023-05-11)

- Feat: Add new parser CupsFilesConf ([PR 3782](https://github.com/RedHatInsights/insights-core/pull/3782))
- Feat: Add new parser CupsdConf ([PR 3781](https://github.com/RedHatInsights/insights-core/pull/3781))
- feat: uname supports RHEL 9.2 ([PR 3789](https://github.com/RedHatInsights/insights-core/pull/3789))
- fix: Replace SkipException with SkipComponent ([PR 3786](https://github.com/RedHatInsights/insights-core/pull/3786))
- fix: fix IndexError in PartedL ([PR 3784](https://github.com/RedHatInsights/insights-core/pull/3784))
- Remove spec lsinitrd_lvm_conf ([PR 3785](https://github.com/RedHatInsights/insights-core/pull/3785))
- RHICOMPL-3512: Select correct datastream file for Compliance scan ([PR 3776](https://github.com/RedHatInsights/insights-core/pull/3776))
- fix: sort the filters in the filters.yaml ([PR 3779](https://github.com/RedHatInsights/insights-core/pull/3779))
- fix: py3.9 test error: 'HTTPResponse' object has no attribute 'strict' ([PR 3780](https://github.com/RedHatInsights/insights-core/pull/3780))
- fix: Unhandled 'Connection failed' in 'gluster_peer_status' parser ([PR 3768](https://github.com/RedHatInsights/insights-core/pull/3768))

# [insights-core-3.1.23](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.23) (2023-05-04)

- feat: new client_metadata module to hold parsers for all client generated files ([PR 3775](https://github.com/RedHatInsights/insights-core/pull/3775))
- chore: add the missed deprecate warnings ([PR 3774](https://github.com/RedHatInsights/insights-core/pull/3774))
- feat: new option to show hit result only for insights-run ([PR 3771](https://github.com/RedHatInsights/insights-core/pull/3771))
- feat: add parser and combiner for IPA ([PR 3767](https://github.com/RedHatInsights/insights-core/pull/3767))
- Travis is dead. Travis is dead, Baby. ([PR 3777](https://github.com/RedHatInsights/insights-core/pull/3777))
- fix: default and disabled module cannot be active ([PR 3773](https://github.com/RedHatInsights/insights-core/pull/3773))
- fix: fix test playbook by using no named tuples ([PR 3772](https://github.com/RedHatInsights/insights-core/pull/3772))

# [insights-core-3.1.22](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.22) (2023-04-27)

- fix: handle the first line is warning in InstalledRpms ([PR 3770](https://github.com/RedHatInsights/insights-core/pull/3770))
- fix(playbook_verifier): clarify logic when normalizing snippets ([PR 3752](https://github.com/RedHatInsights/insights-core/pull/3752))
- Feat: Add new parser ls_var_lib_rpm ([PR 3763](https://github.com/RedHatInsights/insights-core/pull/3763))
- fix: DnfModuleList parser and collect dnf_module_list ([PR 3756](https://github.com/RedHatInsights/insights-core/pull/3756))
- feat: enhance GrubbyDefaultKernel to skip warn msgs ([PR 3761](https://github.com/RedHatInsights/insights-core/pull/3761))
- fix: update ubuntu image for 2.6 test ([PR 3766](https://github.com/RedHatInsights/insights-core/pull/3766))
- feat: Google Cloud public IP spec ([PR 3762](https://github.com/RedHatInsights/insights-core/pull/3762))

# [insights-core-3.1.21](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.21) (2023-04-25)

- Revert "feat: update logging file handler for logrotate (3702)" ([PR 3760](https://github.com/RedHatInsights/insights-core/pull/3760))
- fix: fix processing of SerializedArchiveContext ([PR 3183](https://github.com/RedHatInsights/insights-core/pull/3183))

# [insights-core-3.1.20](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.20) (2023-04-20)

- feat: update logging file handler for logrotate ([PR 3702](https://github.com/RedHatInsights/insights-core/pull/3702))
- fix: use log instead of print in test.run_input_data([PR 3750](https://github.com/RedHatInsights/insights-core/pull/3750))
- feat: Azure public IP spec ([PR 3751](https://github.com/RedHatInsights/insights-core/pull/3751))
- fix: soscleaner get relative_path safely - 2 ([PR 3754](https://github.com/RedHatInsights/insights-core/pull/3754))
- Make malware more flexible when detecting its running against stage ([PR 3725](https://github.com/RedHatInsights/insights-core/pull/3725))

# [insights-core-3.1.19](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.19) (2023-04-14)

- fix: Wrong raw line bound in parser "FSTab" ([PR 3749](https://github.com/RedHatInsights/insights-core/pull/3749))
- feat: add spec and parser for /etc/audisp/audispd.conf ([PR 3743](https://github.com/RedHatInsights/insights-core/pull/3743))
- feat: AWS public IPv4 spec ([PR 3741](https://github.com/RedHatInsights/insights-core/pull/3741))
- fix: check machine id as some archives are with empty machine-id file ([PR 3747](https://github.com/RedHatInsights/insights-core/pull/3747))
- fix: soscleaner get relative_path safely ([PR 3744](https://github.com/RedHatInsights/insights-core/pull/3744))
- feat: Add parser LsinitrdLvmConf ([PR 3740](https://github.com/RedHatInsights/insights-core/pull/3740))
- fix: correct the initialization of ParserException in PHPConf ([PR 3738](https://github.com/RedHatInsights/insights-core/pull/3738))
- fix: datasource rpm_pkgs returns list of string but not tuple ([PR 3736](https://github.com/RedHatInsights/insights-core/pull/3736))
- fix: Add new package findutils into spec rpm_V_packages ([PR 3733](https://github.com/RedHatInsights/insights-core/pull/3733))

# [insights-core-3.1.18](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.18) (2023-04-06)

- feat: add "vf_enabled" parse for spec ip_s_link ([PR 3729](https://github.com/RedHatInsights/insights-core/pull/3729))
- Fix check registration status to be robust against network failures ([PR 3713](https://github.com/RedHatInsights/insights-core/pull/3713))

# [insights-core-3.1.17](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.17) (2023-04-06)

- Feat: New parser for repquota command ([PR 3717](https://github.com/RedHatInsights/insights-core/pull/3717))
- chore: update the spec name of BlacklistedSpecs ([PR 3728](https://github.com/RedHatInsights/insights-core/pull/3728))
- fix: check content before use it ([PR 3727](https://github.com/RedHatInsights/insights-core/pull/3727))
- fix: support built-in metadata files in core-collection ([PR 3723](https://github.com/RedHatInsights/insights-core/pull/3723))
- feat: RHICOMPL-3706 add link to KB article about OOM issues ([PR 3724](https://github.com/RedHatInsights/insights-core/pull/3724))
- chore: tiny simplify and remove unused code in spec_factory.py ([PR 3726](https://github.com/RedHatInsights/insights-core/pull/3726))

# [insights-core-3.1.16](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.16) (2023-03-30)

- feat(compliance): RHICOMPL-3629 log OOM error when scan fails ([PR 3721](https://github.com/RedHatInsights/insights-core/pull/3721))
- New spec "ls -lan /etc/selinux/targeted/policy" ([PR 3722](https://github.com/RedHatInsights/insights-core/pull/3722))

# [insights-core-3.1.15](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.15) (2023-03-23)

- FEAT: Add new parser ls_rsyslog_errorfile ([PR 3719](https://github.com/RedHatInsights/insights-core/pull/3719))

# [insights-core-3.1.14](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.14) (2023-03-17)

- chore: use RHEL for os_release.release ([PR 3716](https://github.com/RedHatInsights/insights-core/pull/3716))
- fix: should not lose the exceptions from components ([PR 3715](https://github.com/RedHatInsights/insights-core/pull/3715))

# [insights-core-3.1.13](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.13) (2023-03-16)

- feat: New datasource and parser for leapp-report.json ([PR 3708](https://github.com/RedHatInsights/insights-core/pull/3708))
- feat: Add store_skips argument to run_input_data ([PR 3706](https://github.com/RedHatInsights/insights-core/pull/3706))
- feat: Split listdir to listdir and listglob spec factories ([PR 3694](https://github.com/RedHatInsights/insights-core/pull/3694))
- fix: enhance the error message to reminder customers re-register ([PR 3691](https://github.com/RedHatInsights/insights-core/pull/3691))
- feat: New spec to get the duplicate machine id  ([PR 3709](https://github.com/RedHatInsights/insights-core/pull/3709))
- Fix logs of check registration status for legacy upload ([PR 3710](https://github.com/RedHatInsights/insights-core/pull/3710))
- fix: print short info for all Exceptions ([PR 3707](https://github.com/RedHatInsights/insights-core/pull/3707))
- Log malware tracebacks to the log file, not the console ([PR 3701](https://github.com/RedHatInsights/insights-core/pull/3701))
- fix: let 'get_filters' work for filterable=True specs only ([PR 3705](https://github.com/RedHatInsights/insights-core/pull/3705))
- fix: update OSRelease.is_rhel more accurate ([PR 3700](https://github.com/RedHatInsights/insights-core/pull/3700))

# [insights-core-3.1.12](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.12) (2023-03-11)

- Revert "feat: New spec to get the duplicate machine id (3697)" ([PR 3703](https://github.com/RedHatInsights/insights-core/pull/3703))

# [insights-core-3.1.11](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.11) (2023-03-09)

- Fix malware SSL error fix - make it more flexible ([PR 3695](https://github.com/RedHatInsights/insights-core/pull/3695))
- feat: New spec to get the duplicate machine id ([PR 3697](https://github.com/RedHatInsights/insights-core/pull/3697))
- chore: update the latest package signing keys ([PR 3696](https://github.com/RedHatInsights/insights-core/pull/3696))

# [insights-core-3.1.10](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.10) (2023-03-02)

- feat: New spec and parser for sys_block_queue_stable_writes ([PR 3688](https://github.com/RedHatInsights/insights-core/pull/3688))
- feat: Add container spec mssql_api_assessment ([PR 3690](https://github.com/RedHatInsights/insights-core/pull/3690))
- feat: add OSRelease.issued_packages to return the issued packages ([PR 3686](https://github.com/RedHatInsights/insights-core/pull/3686))
- Better handle SSL cert verify errors when downloading malware rules ([PR 3685](https://github.com/RedHatInsights/insights-core/pull/3685))

# [insights-core-3.1.9](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.9) (2023-02-23)

- Update rpm_pkgs datasource and create new parser RpmPkgsWritable. ([PR 3684](https://github.com/RedHatInsights/insights-core/pull/3684))

## [insights-core-3.1.8](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.8) (2023-02-23)

- feat: New spec "/etc/sos.conf" and its parser ([PR 3680](https://github.com/RedHatInsights/insights-core/pull/3680))
- fix: correct parse_content in JSONParser ([PR 3682](https://github.com/RedHatInsights/insights-core/pull/3682))

## [insights-core-3.1.7](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.7) (2023-02-16)

- fix: The provider of GCP should be 'gcp' but not 'google' ([PR 3678](https://github.com/RedHatInsights/insights-core/pull/3678))
- feat: Add spec "parted__l" and enhance its parser ([PR 3676](https://github.com/RedHatInsights/insights-core/pull/3676))
- feat: Add container spec for vsftpd and ps ([PR 3674](https://github.com/RedHatInsights/insights-core/pull/3674))
- fix: Correct parser examples and tests ([PR 3677](https://github.com/RedHatInsights/insights-core/pull/3677))

## [insights-core-3.1.6](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.6) (2023-02-09)

- chore: remove unused spec lsinitrd_kdump_image ([PR 3644](https://github.com/RedHatInsights/insights-core/pull/3644))
- fix: py26 test: install libssl1.0-dev manually ([PR 3675](https://github.com/RedHatInsights/insights-core/pull/3675))
- chore: use the unique mangle_command for specs ([PR 3673](https://github.com/RedHatInsights/insights-core/pull/3673))
- feat: Capture blacklisted specs inside archive ([PR 3664](https://github.com/RedHatInsights/insights-core/pull/3664))
- Change sos archive lvm spec names ([PR 3672](https://github.com/RedHatInsights/insights-core/pull/3672))

## [insights-core-3.1.5](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.5) (2023-02-02)

- fix: Enhance datasource kernel_module_filters to check the loaded modules ([PR 3670](https://github.com/RedHatInsights/insights-core/pull/3670))
- fix: use LC_ALL=C.UTF-8 for subscription-manager ([PR 3669](https://github.com/RedHatInsights/insights-core/pull/3669))
- feat: add CloudInstance to canonical_facts ([PR 3654](https://github.com/RedHatInsights/insights-core/pull/3654))
- Deprecate SkipException to help avoid confusion ([PR 3662](https://github.com/RedHatInsights/insights-core/pull/3662))
- feat: Add arg to capture skips in the broker ([PR 3663](https://github.com/RedHatInsights/insights-core/pull/3663))
- fix: Resolve VDOStatus excessive ParseException ([PR 3668](https://github.com/RedHatInsights/insights-core/pull/3668))
- Disable datasource timeout alarm for the malware-detection app ([PR 3666](https://github.com/RedHatInsights/insights-core/pull/3666))
- Make malware-detection app more resilient to unexpected errors ([PR 3661](https://github.com/RedHatInsights/insights-core/pull/3661))
- Exclude malware-detection rules files in /var/tmp (and other locations) ([PR 3665](https://github.com/RedHatInsights/insights-core/pull/3665))

## [insights-core-3.1.4](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.4) (2023-01-19)

- fix: add '-d 2' to yum_repolist spec ([PR 3660](https://github.com/RedHatInsights/insights-core/pull/3660))
- feat: add JbossRuntimeVersions parser ([PR 3639](https://github.com/RedHatInsights/insights-core/pull/3639))
- Move remaining exceptions to the new exceptions module ([PR 3656](https://github.com/RedHatInsights/insights-core/pull/3656))
- Fix: Add condition to check the output of "rpm-ostree status" firstly into combiner rhel_for_edge ([PR 3657](https://github.com/RedHatInsights/insights-core/pull/3657))
- fix: check the content first in class InstalledRpms ([PR 3651](https://github.com/RedHatInsights/insights-core/pull/3651))
- Fix: write all getting data to sys_fs_cgroup_uniq_memory_swappiness ([PR 3658](https://github.com/RedHatInsights/insights-core/pull/3658))
- add specs (datasource via insights-cat) required by CloudInstance ([PR 3655](https://github.com/RedHatInsights/insights-core/pull/3655)

## [insights-core-3.1.3](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.3) (2023-01-12)

- Revert "Fix: Add condition to check the output of "rpm-ostree status" firstly (3634)" ([PR 3652](https://github.com/RedHatInsights/insights-core/pull/3652))
- feat: new combiner OSRelease to identify RHEL ([PR 3640](https://github.com/RedHatInsights/insights-core/pull/3640))
- feat: New datasource "sys_fs_cgroup_uniq_memory_swappiness" and its parser ([PR 3645](https://github.com/RedHatInsights/insights-core/pull/3645))
- fix: Do not log Parsers' Traceback during collection ([PR 3633](https://github.com/RedHatInsights/insights-core/pull/3633))
- Fix: Add condition to check the output of "rpm-ostree status" firstly ([PR 3634](https://github.com/RedHatInsights/insights-core/pull/3634))
- Move exceptions to their own module file ([PR 3622](https://github.com/RedHatInsights/insights-core/pull/3622))
- Allow callers to order components for execution. ([PR 3649](https://github.com/RedHatInsights/insights-core/pull/3649))
- Create timeout signal for hostcontext only ([PR 3647](https://github.com/RedHatInsights/insights-core/pull/3647))
- feat: Add env override to CommandOutputProvider ([PR 3636](https://github.com/RedHatInsights/insights-core/pull/3636))
- fix: Convert aws_token to string since sometimes it's unicode ([PR 3643](https://github.com/RedHatInsights/insights-core/pull/3643))
- fix: py26 CI not found 'Python.h' ([PR 3642](https://github.com/RedHatInsights/insights-core/pull/3642))

## [insights-core-3.1.2](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.2) (2022-12-15)

- Fix: fix GrubbyDefaultKernel cannot handle specific invalid content ([PR 3632](https://github.com/RedHatInsights/insights-core/pull/3632))
- Improve old Python compatibility by not requiring ipython 8.6.0. ([PR 3630](https://github.com/RedHatInsights/insights-core/pull/3630))
- fix: Log brief msg instead of Traceback when cmd not found ([PR 3628](https://github.com/RedHatInsights/insights-core/pull/3628))
- Delete old malware rules files from /var/tmp as well ([PR 3625](https://github.com/RedHatInsights/insights-core/pull/3625))

## [insights-core-3.1.1](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.1) (2022-12-08)

- fix: fix CI issue when preparing py26 env ([PR 3624](https://github.com/RedHatInsights/insights-core/pull/3624))
- Feat: Add Parser LsinitrdKdumpImage  ([PR 3567](https://github.com/RedHatInsights/insights-core/pull/3567))
- Remove usage of reregistration and deprecate cli-option ([PR 3522](https://github.com/RedHatInsights/insights-core/pull/3522))
- feat: Add spec sys_cpuset_cpus ([PR 3611](https://github.com/RedHatInsights/insights-core/pull/3611))
- fix: fix errors in ethtool ([PR 3605](https://github.com/RedHatInsights/insights-core/pull/3605))
- feat: Add spec container_nginx_error_log ([PR 3607](https://github.com/RedHatInsights/insights-core/pull/3607))
- feat: Add container spec sys_cpu_online ([PR 3612](https://github.com/RedHatInsights/insights-core/pull/3612))
- feat: New spec "ls -lZ /var/lib/rsyslog" and the parser ([PR 3618](https://github.com/RedHatInsights/insights-core/pull/3618))
- Feat register no machine-id ([PR 3554](https://github.com/RedHatInsights/insights-core/pull/3554))

## [insights-core-3.1.0](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.1.0) (2022-12-01)

- Keep the code to delete previously-named malware rules file ([PR 3619](https://github.com/RedHatInsights/insights-core/pull/3619))
- fix: add deprecated warning message in insights.combiners.mounts ([PR 3613](https://github.com/RedHatInsights/insights-core/pull/3613))
- feat: Add timeout to datasources ([PR 3598](https://github.com/RedHatInsights/insights-core/pull/3598))
- Display message when malware scan_timeout aborts scan ([PR 3617](https://github.com/RedHatInsights/insights-core/pull/3617))
- Add nginx error log which is installed from RHSCL ([PR 3616](https://github.com/RedHatInsights/insights-core/pull/3616))
- fix: Update the pinned doc modules ([PR 3615](https://github.com/RedHatInsights/insights-core/pull/3615))
- Add datasource to get jboss versions ([PR 3600](https://github.com/RedHatInsights/insights-core/pull/3600))
- [insights-core-3.0.300] Remove deprecated features ([PR 3595](https://github.com/RedHatInsights/insights-core/pull/3595))
- Don't look for yara installed in /usr/local/bin ([PR 3614](https://github.com/RedHatInsights/insights-core/pull/3614))
- test: use ubuntu 20.04 instead of latest as the issue in latest ([PR 3608](https://github.com/RedHatInsights/insights-core/pull/3608))
- Rename downloaded temp malware rules file ([PR 3602](https://github.com/RedHatInsights/insights-core/pull/3602))
- New specs var_log_pcp_openmetrics_log ([PR 3596](https://github.com/RedHatInsights/insights-core/pull/3596))
- feat: RHEL 9.1 is GA ([PR 3599](https://github.com/RedHatInsights/insights-core/pull/3599))
- feat: New spec "timedatectl" and the parser ([PR 3592](https://github.com/RedHatInsights/insights-core/pull/3592))

## [insights-core-3.0.305](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.305) (2022-11-17)

- Rename system_user_dirs to rpm_pkgs ([PR 3597](https://github.com/RedHatInsights/insights-core/pull/3597))

## [insights-core-3.0.304](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.304) (2022-11-17)

- [New Specs] ls_var_lib_pcp ([PR 3590](https://github.com/RedHatInsights/insights-core/pull/3590))
- Fix: Update container_installed_rpms spec ([PR 3589](https://github.com/RedHatInsights/insights-core/pull/3589))
- Revert "feat: Add timeout to datasources (#3573)" ([PR 3594](https://github.com/RedHatInsights/insights-core/pull/3594))
- feat: Add timeout to datasources ([PR 3573](https://github.com/RedHatInsights/insights-core/pull/3573))
- Add rhel 8.7 into uname.py ([PR 3591](https://github.com/RedHatInsights/insights-core/pull/3591))

## [insights-core-3.0.303](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.303) (2022-11-10)

- Registration check unregisters when it is not connected ([PR 3540](https://github.com/RedHatInsights/insights-core/pull/3540))
- Update system_user_dirs datasource ([PR 3586](https://github.com/RedHatInsights/insights-core/pull/3586))
- Handle network exceptions when accessing egg URL ([PR 3588](https://github.com/RedHatInsights/insights-core/pull/3588))
- Feat: New Parser for 'dotnet --version' Command for Containers ([PR 3581](https://github.com/RedHatInsights/insights-core/pull/3581))
- feat: New Combiner CloudInstance ([PR 3585](https://github.com/RedHatInsights/insights-core/pull/3585))
- feat: New spec "/etc/fapolicyd/rules.d/*.rules" and parser ([PR 3587](https://github.com/RedHatInsights/insights-core/pull/3587))
- fix: values of broker.tracebacks should be string ([PR 3579](https://github.com/RedHatInsights/insights-core/pull/3579))
- Update github actions to use latest version ([PR 3583](https://github.com/RedHatInsights/insights-core/pull/3583))
- fix(parsers): add support for missing logs ([PR 3582](https://github.com/RedHatInsights/insights-core/pull/3582))
- feat(client): add --manifest argument ([PR 3547](https://github.com/RedHatInsights/insights-core/pull/3547))

## [insights-core-3.0.302](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.302) (2022-11-03)

- feat: new spec and parser for 'azure_instance_id' ([PR 3568](https://github.com/RedHatInsights/insights-core/pull/3568))
- feat: Add parser container_inspect ([PR 3562](https://github.com/RedHatInsights/insights-core/pull/3562))
- fix: remove the inner functions of the _make_rpm_formatter ([PR 3574](https://github.com/RedHatInsights/insights-core/pull/3574))
- chore: remove the unused 'ethernet_interfaces' spec ([PR 3577](https://github.com/RedHatInsights/insights-core/pull/3577))
- fix: check list range to avoid exception ([PR 3576](https://github.com/RedHatInsights/insights-core/pull/3576))
- fix: LuksDump not parsing multiple data segments ([PR 3569](https://github.com/RedHatInsights/insights-core/pull/3569))
- feat: new spec and parser for 'subscription-manage facts' ([PR 3555](https://github.com/RedHatInsights/insights-core/pull/3555))
- enhance: add base class 'OVSvsctlList' ([PR 3575](https://github.com/RedHatInsights/insights-core/pull/3575))

## [insights-core-3.0.301](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.301) (2022-10-31)

- fix: missing call to a RPM format generation function ([PR 3572](https://github.com/RedHatInsights/insights-core/pull/3572))
- fix: remove duplicated containers from running_rhel_containers ([PR 35](https://github.com/RedHatInsights/insights-core/pull/3571))

## [insights-core-3.0.300](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.300) (2022-10-27)

- Avoid test to write in disk if machine-id is not found ([PR 3543](https://github.com/RedHatInsights/insights-core/pull/3543))
- enhance and fix for softnet_data parser ([PR 3561](https://github.com/RedHatInsights/insights-core/pull/3561))
- test: add test for existing container specs ([PR 3563](https://github.com/RedHatInsights/insights-core/pull/3563))
- Order specs by alphabetical order ([PR 3564](https://github.com/RedHatInsights/insights-core/pull/3564))
- feat: New Parser for container_installed_rpms ([PR 3560](https://github.com/RedHatInsights/insights-core/pull/3560))
- Handle upload exceptions allowing --retries to work properly ([PR 3558](https://github.com/RedHatInsights/insights-core/pull/3558))
- fix: let container_execute to support rpm_format of installed_rpms ([PR 3559](https://github.com/RedHatInsights/insights-core/pull/3559))

## [insights-core-3.0.299](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.299) (2022-10-20)

- feat: New spec "semanage login -l" and parser ([PR 3548](https://github.com/RedHatInsights/insights-core/pull/3548))
- [New-parser] parser_mpirun_version ([PR 3542](https://github.com/RedHatInsights/insights-core/pull/3542))
- Removed assert of virt-who, it is not in uploader.json ([PR 3556](https://github.com/RedHatInsights/insights-core/pull/3556))

## [insights-core-3.0.298](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.298) (2022-10-13)

- fix: Add ability to return exceptions during insights collect ([PR 3539](https://github.com/RedHatInsights/insights-core/pull/3539))
- refactor: remove duplicated specs from get_dependency_specs ([PR 3549](https://github.com/RedHatInsights/insights-core/pull/3549))
- Remove authselect_current from core collection ([PR 3552](https://github.com/RedHatInsights/insights-core/pull/3552))
- Feat: New parser for the "ls -lan /var/lib/sss/pubconf/krb5.include.d" command ([PR 3545](https://github.com/RedHatInsights/insights-core/pull/3545))
- Deprecate insights.core.scannable & engine_log parser ([PR 3541](https://github.com/RedHatInsights/insights-core/pull/3541))
- chore: remove the unused specs ([PR 3537](https://github.com/RedHatInsights/insights-core/pull/3537))
- fix: Restore the spec ovs_appctl_fdb_show_bridge ([PR 3538](https://github.com/RedHatInsights/insights-core/pull/3538))
- Add spec and parser for luksmeta command ([PR 3525](https://github.com/RedHatInsights/insights-core/pull/3525))

## [insights-core-3.0.297](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.297) (2022-10-06)

- feat: add helper function: get_dependency_specs and test ([PR 3534](https://github.com/RedHatInsights/insights-core/pull/3534))
- Fix registration tests ([PR 3519](https://github.com/RedHatInsights/insights-core/pull/3519))

## [insights-core-3.0.296](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.296) (2022-09-29)

- fix: make SAPHostCtrlInstances compatible with old archives ([PR 3528](https://github.com/RedHatInsights/insights-core/pull/3528))
- refactor: Keep the raw line for rule use ([PR 3533](https://github.com/RedHatInsights/insights-core/pull/3533))
- feat: [PoC] Support Container Specs ([PR 3477](https://github.com/RedHatInsights/insights-core/pull/3477))
- fix: bz-2130242, remove the print statement ([PR 3535](https://github.com/RedHatInsights/insights-core/pull/3535))
- Update docstring to make it more readable ([PR 3531](https://github.com/RedHatInsights/insights-core/pull/3531))

## [insights-core-3.0.295](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.295) (2022-09-22)

- feat: New spec "/etc/cron.d/foreman" and parser ([PR 3514](https://github.com/RedHatInsights/insights-core/pull/3514))
- feat: Add combiner rhel for edge ([PR 3526](https://github.com/RedHatInsights/insights-core/pull/3526))
- fix: bz-2126966: use SIGTERM for rpm instead of SIGKILL ([PR 3524](https://github.com/RedHatInsights/insights-core/pull/3524))
- fix: Soscleaner fix ([PR 3502](https://github.com/RedHatInsights/insights-core/pull/3502))
- fix: Removing extraneous space inserted in commit 894484a ([PR 3516](https://github.com/RedHatInsights/insights-core/pull/3523))

## [insights-core-3.0.294](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.294) (2022-09-15)

- feat: New spec to get satellite logs table size and its parser ([PR 3516](https://github.com/RedHatInsights/insights-core/pull/3516))
- New parser for CpuSMTControl and tests update ([PR 3521](https://github.com/RedHatInsights/insights-core/pull/3521))
- Feat: Add spec and parser for cryptsetup luksDump ([PR 3504](https://github.com/RedHatInsights/insights-core/pull/3504))
- feat: Add spec "satellite_enabled_features" back ([PR 3517](https://github.com/RedHatInsights/insights-core/pull/3517))
- Refractor cleanup local files for unregistration processes ([PR 3520](https://github.com/RedHatInsights/insights-core/pull/3520))
- feat: Update ls_systemd_units parser ([PR 3518](https://github.com/RedHatInsights/insights-core/pull/3518))

## [insights-core-3.0.293](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.293) (2022-09-08)

- fix: support InstanceType in saphostctrl ([PR 3512](https://github.com/RedHatInsights/insights-core/pull/3512))
- Feat: add secure spec to default.py ([PR 3513](https://github.com/RedHatInsights/insights-core/pull/3513))
- Ensure full path when using timeout command ([PR 3508](https://github.com/RedHatInsights/insights-core/pull/3508))

## [insights-core-3.0.292](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.292) (2022-09-01)

- Added no_proxy autoconfiguration from rhsm conf and tests ([PR 3507](https://github.com/RedHatInsights/insights-core/pull/3507))
- Fix: grubenv cannot be collected when error shown in output ([PR 3511](https://github.com/RedHatInsights/insights-core/pull/3511))
- fix: change cloud_cfg to Yaml and modify the source spec ([PR 3484](https://github.com/RedHatInsights/insights-core/pull/3484))
- fix: Revert the httpd_on_nfs datasource spec ([PR 3509](https://github.com/RedHatInsights/insights-core/pull/3509))
- fix: Issue calling collect from cli ([PR 3506](https://github.com/RedHatInsights/insights-core/pull/3506))

## [insights-core-3.0.291](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.291) (2022-08-25)

- Feat: New journal_header ([PR 3498](https://github.com/RedHatInsights/insights-core/pull/3498))
- feat: New spec and parser to get the satellite provision params ([PR 3501](https://github.com/RedHatInsights/insights-core/pull/3501))
- Feat: New parser for 'ls -lanL /etc/ssh' command ([PR 3499](https://github.com/RedHatInsights/insights-core/pull/3499))
- feat: New spec and parser for `authselect current` ([PR 3490](https://github.com/RedHatInsights/insights-core/pull/3490))
- Add release timeline ([PR 3500](https://github.com/RedHatInsights/insights-core/pull/3500))

## [insights-core-3.0.290](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.290) (2022-08-18)

- New location for temp directory and tests ([PR 3489](https://github.com/RedHatInsights/insights-core/pull/3489))

## [insights-core-3.0.289](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.289) (2022-08-18)

- feat: New spec and parser for "auditctl -l" ([PR 3496](https://github.com/RedHatInsights/insights-core/pull/3496))
- Feat: New grub2_editenv_list parser ([PR 3481](https://github.com/RedHatInsights/insights-core/pull/3481))
- Automatically retry malware-detection downloads & uploads ([PR 3493](https://github.com/RedHatInsights/insights-core/pull/3493))

## [insights-core-3.0.288](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.288) (2022-08-11)

- feat: Add version to deprecated function ([PR 3491](https://github.com/RedHatInsights/insights-core/pull/3491))

## [insights-core-3.0.287](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.287) (2022-08-04)

- Feat: Add new parser sys_fs_cgroup_memory_tasks_number ([PR 3467](https://github.com/RedHatInsights/insights-core/pull/3467))
- fix: Update aws specs to use IMDSv2 ([PR 3486](https://github.com/RedHatInsights/insights-core/pull/3486))
- New version of flake8 found some errors ([PR 3488](https://github.com/RedHatInsights/insights-core/pull/3488))
- Add missing datasource docs to build ([PR 3487](https://github.com/RedHatInsights/insights-core/pull/3487))
- Update the marker for MustGatherContext ([PR 3479](https://github.com/RedHatInsights/insights-core/pull/3479))
- Add new system_user_dirs datasource and parser ([PR 3381](https://github.com/RedHatInsights/insights-core/pull/3381))

## [insights-core-3.0.286](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.286) (2022-07-28)

- fix: the parser "LvmConfig" raises exception ([PR 3476](https://github.com/RedHatInsights/insights-core/pull/3476))
- feat: Add spec for teamdctl_config_dump parser ([PR 3472](https://github.com/RedHatInsights/insights-core/pull/3472))
- Fix error with umask not being restored when dir exists ([PR 3480](https://github.com/RedHatInsights/insights-core/pull/3480))
- fix: Restrict Sphinx's version since it breaks docs build ([PR 3483](https://github.com/RedHatInsights/insights-core/pull/3483))

## [insights-core-3.0.285](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.285) (2022-07-21)

- fix: Add spec "lvmconfig" back ([PR 3474](https://github.com/RedHatInsights/insights-core/pull/3474))
- Fix: Add pre-check for teamdctl_state_dump ([PR 3470](https://github.com/RedHatInsights/insights-core/pull/3470))
- Fix: Restore the spec cni_podman_bridge_conf ([PR 3471](https://github.com/RedHatInsights/insights-core/pull/3471))

## [insights-core-3.0.284](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.284) (2022-07-14)

- Unregister option removes machine-id ([PR 3449](https://github.com/RedHatInsights/insights-core/pull/3449))
- Add spec and parser for 'wc_-l_.proc.1.mountinfo' ([PR 3459](https://github.com/RedHatInsights/insights-core/pull/3459))
- feat: revert and refine the padman list specs and parsers ([PR 3466](https://github.com/RedHatInsights/insights-core/pull/3466))
- Fix: test error of nmcli in the datasource ethernet ([PR 3468](https://github.com/RedHatInsights/insights-core/pull/3468))
- fix: Enhance nmcli ([PR 3465](https://github.com/RedHatInsights/insights-core/pull/3465))
- Feat: Add teamdctl_state_dump spec to insights_archive ([PR 3455](https://github.com/RedHatInsights/insights-core/pull/3455))
- fix: Catch any exceptions when scanning for files ([PR 3463](https://github.com/RedHatInsights/insights-core/pull/3463))
- fix: Replace non ascii characters with question marks ([PR 3464](https://github.com/RedHatInsights/insights-core/pull/3464))
- feat: Add combiner "ModulesInfo" ([PR 3458](https://github.com/RedHatInsights/insights-core/pull/3458))

## [insights-core-3.0.283](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.283) (2022-07-07)

- feat: New spec "/etc/lvm/devices/system.devices" and parser ([PR 3457](https://github.com/RedHatInsights/insights-core/pull/3457))

## [insights-core-3.0.282](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.282) (2022-07-01)

- fixes: Recover "modinfo_xxx" specs ([PR 3456](https://github.com/RedHatInsights/insights-core/pull/3456))

## [insights-core-3.0.281](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.281) (2022-06-30)

- feat: add "modinfo_filtered_modules" to collect the filtered modules information ([PR 3447](https://github.com/RedHatInsights/insights-core/pull/3447))
- feat: Parser for "ls systemd units" ([PR 3451](https://github.com/RedHatInsights/insights-core/pull/3451))
- Handle downloading malware-detection rules from stage environment ([PR 3452](https://github.com/RedHatInsights/insights-core/pull/3452))

## [insights-core-3.0.280](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.280) (2022-06-23)

- Update canonical_facts to load needed components ([PR 3448](https://github.com/RedHatInsights/insights-core/pull/3448))
- Remove RPM_OUTPUT_SHADOW_UTILS ([PR 3442](https://github.com/RedHatInsights/insights-core/pull/3442))
- Replace xfail with positive test ([PR 3443](https://github.com/RedHatInsights/insights-core/pull/3443))

## [insights-core-3.0.279](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.279) (2022-06-17)

- Update canonical_facts to load needed components ([PR 3444](https://github.com/RedHatInsights/insights-core/pull/3444))
- Fix tests that removing temp archives ([PR 3445](https://github.com/RedHatInsights/insights-core/pull/3445))

## [insights-core-3.0.278](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.278) (2022-06-16)

- Add new parser for /etc/nfs.conf ([PR 3438](https://github.com/RedHatInsights/insights-core/pull/3438))
- Mock test creating files in protected directories ([PR 3440](https://github.com/RedHatInsights/insights-core/pull/3440))
- Append compression type to content-type of MIME. Compare file compression with content_type. ([PR 3435](https://github.com/RedHatInsights/insights-core/pull/3435))
- malware-detection: implement yara version handling differently ([PR 3437](https://github.com/RedHatInsights/insights-core/pull/3437))
- When insights client is killed the directories in /var/tmp are not removed rhbz#2009773 ([PR 3396](https://github.com/RedHatInsights/insights-core/pull/3396))

## [insights-core-3.0.277](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.277) (2022-06-09)

- feat: Add --no-load-default arg to the insights-run command ([PR 3434](https://github.com/RedHatInsights/insights-core/pull/3434))
- feat: Support parallelly running for insights-engine ([PR 3436](https://github.com/RedHatInsights/insights-core/pull/3436))

## [insights-core-3.0.276](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.276) (2022-06-02)

- feat: New specs for systemd ls output and modification of existing parser ([PR 3424](https://github.com/RedHatInsights/insights-core/pull/3424))
- Updating sos_archive to parse file for GSS rule ([PR 3432](https://github.com/RedHatInsights/insights-core/pull/3432))
- feat: Add --parallel arg for insights-run ([PR 3418](https://github.com/RedHatInsights/insights-core/pull/3418))
- feat: new spec and parser for /etc/sudoers ([PR 3425](https://github.com/RedHatInsights/insights-core/pull/3425))
- feat: New spec and parser for group_info ([PR 3423](https://github.com/RedHatInsights/insights-core/pull/3423))
- malware-detection feature: handle different yara versions ([PR 3428](https://github.com/RedHatInsights/insights-core/pull/3428))
- refactor: move the rest of datasource to the datasources dir ([PR 3430](https://github.com/RedHatInsights/insights-core/pull/3430))
- chore: remove the unused get_owner from specs.default ([PR 3429](https://github.com/RedHatInsights/insights-core/pull/3429))
- Add Alpha to redhat release detection ([PR 3431](https://github.com/RedHatInsights/insights-core/pull/3431))
- feat: Updated the parser to also return  allow-recursion content ([PR 3427](https://github.com/RedHatInsights/insights-core/pull/3427))
- fix(Compliance): Find policy correctly when there is one datasteam file ([PR 3420](https://github.com/RedHatInsights/insights-core/pull/3420))

## [insights-core-3.0.275](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.275) (2022-05-26)

- feat: New parser ProcKeys for '/proc/keys' file ([PR 3417](https://github.com/RedHatInsights/insights-core/pull/3417))
- feat: New ceph version and enhance ([PR 3422](https://github.com/RedHatInsights/insights-core/pull/3422))
- feat: Add spec and parser for file '/etc/sysconfig/nfs' ([PR 3419](https://github.com/RedHatInsights/insights-core/pull/3419))

## [insights-core-3.0.274](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.274) (2022-05-19)

- Handle the value in kernel-alt pkg ([PR 3415](https://github.com/RedHatInsights/insights-core/pull/3415))
- feat: RHEL 9.0 is GA ([PR 3416](https://github.com/RedHatInsights/insights-core/pull/3416))
- fixes: exception with "Reading VG shared_vg1 without a lock" ([PR 3412](https://github.com/RedHatInsights/insights-core/pull/3412))
- Add os major version 9 for Compliance ([PR 3413](https://github.com/RedHatInsights/insights-core/pull/3413))
- Update CI/CD to include Python 3.9 ([PR 3410](https://github.com/RedHatInsights/insights-core/pull/3410))
- Move tests in code directories to tests dir ([PR 3261](https://github.com/RedHatInsights/insights-core/pull/3261))

## [insights-core-3.0.273](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.273) (2022-05-12)

- feat: RHEL 8.6 is GA ([PR 3409](https://github.com/RedHatInsights/insights-core/pull/3409))
- Add parser for /proc/self/mountinfo and new combiner mounts ([PR 3398](https://github.com/RedHatInsights/insights-core/pull/3398))
- fix: Deprecation warnings and removal of collections ([PR 3407](https://github.com/RedHatInsights/insights-core/pull/3407))
- fixes: the last login time is considered as DB query result ([PR 3404](https://github.com/RedHatInsights/insights-core/pull/3404))
- feat: RHICOMPL-2450 implemented OpenSCAP result obfuscation ([PR 3349](https://github.com/RedHatInsights/insights-core/pull/3349))
- Feat: Add spec and parser for 'nginx_log' ([PR 3402](https://github.com/RedHatInsights/insights-core/pull/3402))
- Add parser bdi_read_ahead_kb for '/sys/class/bdi/*/read_ahead_kb' files ([PR 3391](https://github.com/RedHatInsights/insights-core/pull/3391))
- Fix failing malware-detection tests ([PR 3400](https://github.com/RedHatInsights/insights-core/pull/3400))

## [insights-core-3.0.272](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.272) (2022-04-28)

- Feat: Add spec and parser for 'containers_policy' ([PR 3394](https://github.com/RedHatInsights/insights-core/pull/3394))
- Skip malware-detection tests on RHEL6/python2.6 (not supported) ([PR 3382](https://github.com/RedHatInsights/insights-core/pull/3382))

## [insights-core-3.0.271](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.271) (2022-04-21)

- fix: Multiline quote parsing of httpd conf files ([PR 3392](https://github.com/RedHatInsights/insights-core/pull/3392))
- feat: Add new crash_kexec_post_notifiers parser ([PR 3387](https://github.com/RedHatInsights/insights-core/pull/3387))
- fix: make sure JSONParser is compatible with RawFileProvider ([PR 3390](https://github.com/RedHatInsights/insights-core/pull/3390))
- fix: Move _LogRotateConf parser out of combiner ([PR 3389](https://github.com/RedHatInsights/insights-core/pull/3389))
- fix: Move the _NginxConf parser out of the combiner ([PR 3386](https://github.com/RedHatInsights/insights-core/pull/3386))
- fix: Httpd tracebacks displaying when the client is ran ([PR 3379](https://github.com/RedHatInsights/insights-core/pull/3379))
- fix: strip the '\x00' from the ibm_fw_vernum_encoded before parsing ([PR 3378](https://github.com/RedHatInsights/insights-core/pull/3378))
- Fix spec for YumUpdates parser ([PR 3388](https://github.com/RedHatInsights/insights-core/pull/3388))
- Only collect "*.conf" for nginx ([PR 3380](https://github.com/RedHatInsights/insights-core/pull/3380))
- fix: Update the spec "du_dirs" to filterable ([PR 3384](https://github.com/RedHatInsights/insights-core/pull/3384))
- fix(client): Return valid machine-id UUID4 object ([PR 3385](https://github.com/RedHatInsights/insights-core/pull/3385))
- Exclude some Specs from IP address obfuscation ([PR 3331](https://github.com/RedHatInsights/insights-core/pull/3331))

## [insights-core-3.0.270](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.270) (2022-04-07)

- Replace <E2><80><9C>cloud.redhat.com<E2><80><9D> with <E2><80><9C>console.redhat.com<E2><80><9D> ([PR 3365](https://github.com/RedHatInsights/insights-core/pull/3365))
- New parser Ql2xmqSupport ([PR 3374](https://github.com/RedHatInsights/insights-core/pull/3374))
- Fix BZ#2071058 ([PR 3375](https://github.com/RedHatInsights/insights-core/pull/3375))
- fix: correctly obfuscate IP addresses at EOL ([PR 3376](https://github.com/RedHatInsights/insights-core/pull/3376))
- feat: Add new sos ps spec and fix ValueError caused by it ([PR 3377](https://github.com/RedHatInsights/insights-core/pull/3377))
- Enhance combiner grub_conf_blscfg ([PR 3370](https://github.com/RedHatInsights/insights-core/pull/3370))
- fix: Update bond and bond_dynamic_lb spec ([PR 3372](https://github.com/RedHatInsights/insights-core/pull/3372))

## [insights-core-3.0.269](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.269) (2022-03-31)

- fix: Enhance "PCSStatus" to make it compatible with new output format ([PR 3373](https://github.com/RedHatInsights/insights-core/pull/3373))
- Revert "fix: Enhance parser Grub2Config (#3360)" ([PR 3367](https://github.com/RedHatInsights/insights-core/pull/3367))
- fix: Fix deprecation warning for using ET.getiterator ([PR 3371](https://github.com/RedHatInsights/insights-core/pull/3371))

## [insights-core-3.0.268](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.268) (2022-03-24)

- fix: Enhance parser Grub2Config ([PR 3360](https://github.com/RedHatInsights/insights-core/pull/3360))
- fix: Switch to reading crontab file rather than run the command ([PR 3359](https://github.com/RedHatInsights/insights-core/pull/3359))
- status terminated with ok signal when wheter it is registered or not ([PR 3364](https://github.com/RedHatInsights/insights-core/pull/3364))
- fix: Keep the results once one of them is good ([PR 3357](https://github.com/RedHatInsights/insights-core/pull/3357))

## [insights-core-3.0.267](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.267) (2022-03-17)

- feat: New parser for /usr/bin/od -An -t d /dev/cpu_dma_latency ([PR 3353](https://github.com/RedHatInsights/insights-core/pull/3353))
- feat: New parsers for IBM proc files ([PR 3361](https://github.com/RedHatInsights/insights-core/pull/3361))
- feat: New spec to get satellite repos with multiple reference ([PR 3362](https://github.com/RedHatInsights/insights-core/pull/3362))
- feat: Add systctl.d spec, parser, and combiner ([PR 3358](https://github.com/RedHatInsights/insights-core/pull/3358))
- New parser ktimer_lockless ([PR 3355](https://github.com/RedHatInsights/insights-core/pull/3355))

## [insights-core-3.0.266](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.266) (2022-03-10)

- Fix slowness on RHEL 8 by simplifying looping over pkgs ([PR 3354](https://github.com/RedHatInsights/insights-core/pull/3354))
- feat: New spec and parser to get capsules and repos with conditions ([PR 3352](https://github.com/RedHatInsights/insights-core/pull/3352))
- feat: New parser for systemd_perms ([PR 3339](https://github.com/RedHatInsights/insights-core/pull/3339))

## [insights-core-3.0.265](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.265) (2022-03-03)

- fix: Fix the regression bug of soscleaner IP obsfuscating ([PR 3347](https://github.com/RedHatInsights/insights-core/pull/3347))
- Don't log the insights-core egg in verbose mode (BZ 2045995) ([PR 3348](https://github.com/RedHatInsights/insights-core/pull/3348))
- Feat: Add spec and parser for 'crictl_logs' ([PR 3345](https://github.com/RedHatInsights/insights-core/pull/3345))

## [insights-core-3.0.264](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.264) (2022-02-24)

- New parameters checked when offline is active ([PR 3338](https://github.com/RedHatInsights/insights-core/pull/3338))
- Fix issue with Markupsafe and Jinja2 versions ([PR 3344](https://github.com/RedHatInsights/insights-core/pull/3344))
- SPM-1379: skip code on RHEL8.4 because of caching bug ([PR 3341](https://github.com/RedHatInsights/insights-core/pull/3341))
- Support downloading malware-detection rules via Satellite ([PR 3337](https://github.com/RedHatInsights/insights-core/pull/3337))
- Revert satellite version enhancement and Enhance "CapsuleVersion" only ([PR 3342](https://github.com/RedHatInsights/insights-core/pull/3342))

## [insights-core-3.0.263](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.263) (2022-02-17)

- fix: Enhance combiner "SatelliteVersion" ([PR 3340](https://github.com/RedHatInsights/insights-core/pull/3340))

## [insights-core-3.0.262](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.262) (2022-02-17)

- fix: Enhance combiner "SatelliteVersion" and "CapsuleVersion" ([PR 3336](https://github.com/RedHatInsights/insights-core/pull/3336))
- feat: Add thread counts to ps's pid_info dict ([PR 3334](https://github.com/RedHatInsights/insights-core/pull/3334))
- New parser for Db2ls ([PR 3332](https://github.com/RedHatInsights/insights-core/pull/3332))
- new message for --group in client ([PR 3333](https://github.com/RedHatInsights/insights-core/pull/3333))

## [insights-core-3.0.261](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.261) (2022-02-10)

- fix: Enhance hammer_ping parser ([PR 3330](https://github.com/RedHatInsights/insights-core/pull/3330))
- feat: New spec and parser for losetup -l ([PR 3328](https://github.com/RedHatInsights/insights-core/pull/3328))
- Extended yum updates datasource to work on dnf based systems ([PR 3329](https://github.com/RedHatInsights/insights-core/pull/3329))
- feat: tell the user the largest file in the archive if the upload is too big ([PR 3059](https://github.com/RedHatInsights/insights-core/pull/3059))

## [insights-core-3.0.260](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.260) (2022-01-27)

- Feat: Add spec and parser for 'crio.conf' ([PR 3309](https://github.com/RedHatInsights/insights-core/pull/3309))
- feat: New spec to get all services which enabled CPUAccounting ([PR 3321](https://github.com/RedHatInsights/insights-core/pull/3321))

## [insights-core-3.0.259](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.259) (2022-01-20)

- Update spec ls_l first_file ([PR 3326](https://github.com/RedHatInsights/insights-core/pull/3326))
- Update the ChangeLog to include insights-core-3.0.258 ([PR 3325](https://github.com/RedHatInsights/insights-core/pull/3325))

## [insights-core-3.0.258](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.258) (2022-01-20)

- Enhance spec ls_l ([PR 3324](https://github.com/RedHatInsights/insights-core/pull/3324))
- Separate scan_only and scan_exclude options for filesystem and processes ([PR 3312](https://github.com/RedHatInsights/insights-core/pull/3312))
- Fix: Update lscpu parser to support RHEL9 output ([PR 3320](https://github.com/RedHatInsights/insights-core/pull/3320))

## [insights-core-3.0.257](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.257) (2022-01-13)

- Fix parsing problem in cloud_cfg datasource ([PR 3318](https://github.com/RedHatInsights/insights-core/pull/3318))
- Fix: Update the unitfiles parser for RHEL9 output ([PR 3319](https://github.com/RedHatInsights/insights-core/pull/3319))
- feat: Add spec and parser for systemctl_status_-all ([PR 3317](https://github.com/RedHatInsights/insights-core/pull/3317))
- feat: Switch IniConfigFile from RawConfigParser to parsr's iniparser ([PR 3310](https://github.com/RedHatInsights/insights-core/pull/3310))
- Playbook revocation list ([PR 3311](https://github.com/RedHatInsights/insights-core/pull/3311))

## [insights-core-3.0.256](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.256) (2022-01-06)

- Fix: Enhance parser "SatellitePostgreSQLQuery" ([PR 3314](https://github.com/RedHatInsights/insights-core/pull/3314))
- feat: enhance calc_offset to support check all target in line ([PR 3316](https://github.com/RedHatInsights/insights-core/pull/3316))
- Test IP obfuscation ([PR 3315](https://github.com/RedHatInsights/insights-core/pull/3315))

## [insights-core-3.0.255](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.255) (2021-12-16)

- Add spec "foreman_production_log" back. ([PR 3308](https://github.com/RedHatInsights/insights-core/pull/3308))
- Enh: Improved excluding of the insights-client log files ([PR 3306](https://github.com/RedHatInsights/insights-core/pull/3306))
- Feat: New spec to get the httpd certificate expire info stored in NSS... ([PR 3303](https://github.com/RedHatInsights/insights-core/pull/3303))

## [insights-core-3.0.254](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.254) (2021-12-09)

- Fix: Only get "SSLCertificateFile" when "SSLEngine on" is configured ([PR 3305](https://github.com/RedHatInsights/insights-core/pull/3305))
- feat: Add spec and parser for sos_commands/logs/journalctl_--no-pager file ([PR 3297](https://github.com/RedHatInsights/insights-core/pull/3297))
- feat: New spec to get satelltie empty url repositories ([PR 3299](https://github.com/RedHatInsights/insights-core/pull/3299))
- feat: New spec to get the count of satellite tasks with reserved resource ([PR 3300](https://github.com/RedHatInsights/insights-core/pull/3300))
- Remove old rules files before starting a new scan ([PR 3302](https://github.com/RedHatInsights/insights-core/pull/3302))
- Fix test system ([PR 3294](https://github.com/RedHatInsights/insights-core/pull/3294))
- Enhance parser LpstatProtocol ([PR 3301](https://github.com/RedHatInsights/insights-core/pull/3301))
- Add log_response_text flag to log downloads or not in verbose mode ([PR 3298](https://github.com/RedHatInsights/insights-core/pull/3298))
- Remove yara_binary as a config option ([PR 3296](https://github.com/RedHatInsights/insights-core/pull/3296))

## [insights-core-3.0.253](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.253) (2021-12-02)

- DOC: Added new section for client development ([PR 3287](https://github.com/RedHatInsights/insights-core/pull/3287))
- Update setup.py ([PR 3289](https://github.com/RedHatInsights/insights-core/pull/3289))
- Fix: Enhance some spec path ([PR 3293](https://github.com/RedHatInsights/insights-core/pull/3293))
- Update ethtool's parsing logic ([PR 3291](https://github.com/RedHatInsights/insights-core/pull/3291))
- Refactor: read metrics from config.ros for pmlog_summary ([PR 3278](https://github.com/RedHatInsights/insights-core/pull/3278))
- Add in IsRhel9 component ([PR 3288](https://github.com/RedHatInsights/insights-core/pull/3288))
- fix: update the pmlog_summary to support new metrics ([PR 3290](https://github.com/RedHatInsights/insights-core/pull/3290))

## [insights-core-3.0.252](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.252) (2021-11-18)

- Feat: Add Malware app as a manifest spec ([PR 3236](https://github.com/RedHatInsights/insights-core/pull/3236))
- adding the missed CHANGELOG ([PR 3286](https://github.com/RedHatInsights/insights-core/pull/3286))
- Remove unused collect variables ([PR 3284](https://github.com/RedHatInsights/insights-core/pull/3284))

## [insights-core-3.0.251](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.251) (2021-11-11)

- Add parser mssql_tls_file ([PR 3283](https://github.com/RedHatInsights/insights-core/pull/3283))
- Add spec "/etc/foreman-installer/scenarios.d/satellite.yaml" ([PR 3280](https://github.com/RedHatInsights/insights-core/pull/3280))
- New parser ldap config ([PR 3257](https://github.com/RedHatInsights/insights-core/pull/3257))
- Added spec for the getcert_list parser ([PR 3274](https://github.com/RedHatInsights/insights-core/pull/3274))
- fix: Correct the order of satellite_custom_hiera in the list of specs ([PR 3282](https://github.com/RedHatInsights/insights-core/pull/3282))
- chore: RHEL 8.5 is GA ([PR 3285](https://github.com/RedHatInsights/insights-core/pull/3285))
- Fix: Strip progress messages from testparm output ([PR 3273](https://github.com/RedHatInsights/insights-core/pull/3273))
- Get all SSL certificates for httpd incase different expired date used ([PR 3270](https://github.com/RedHatInsights/insights-core/pull/3270))

## [insights-core-3.0.250](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.250) (2021-11-04)

- Fix: RHICOMPL-1980 Adding the 'relationships' API attribute to the client profiles API call. ([PR 3241](https://github.com/RedHatInsights/insights-core/pull/3241))
- Feat: Spec & parser for 389-ds TLS-related settings. ([PR 3264](https://github.com/RedHatInsights/insights-core/pull/3264))
- fix: check 'tab' in lines of ntp.conf ([PR 3272](https://github.com/RedHatInsights/insights-core/pull/3272))
- Feat: Spec & parser for nss-rhel7.config ([PR 3269](https://github.com/RedHatInsights/insights-core/pull/3269))
- Fix: Add raise SkipException to ConfigCombiner for missing main_file ([PR 3277](https://github.com/RedHatInsights/insights-core/pull/3277))
- Fix: Fix issue in client test due to spec change ([PR 3275](https://github.com/RedHatInsights/insights-core/pull/3275))

## [insights-core-3.0.249](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.249) (2021-10-28)

- Feat: Add spec filtering to context_wrap for unit tests ([PR 3265](https://github.com/RedHatInsights/insights-core/pull/3265))
- Fix: Update verification code with an additional fix ([PR 3266](https://github.com/RedHatInsights/insights-core/pull/3266))
- New nginx spec to get ssl certificate expire data ([PR 3259](https://github.com/RedHatInsights/insights-core/pull/3259))
- Enhanced the certificates_enddate spec to support tower cert ([PR 3258](https://github.com/RedHatInsights/insights-core/pull/3258))
- fix: Remove old grub specs from client tests ([PR 3263](https://github.com/RedHatInsights/insights-core/pull/3263))

## [insights-core-3.0.248](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.248) (2021-10-21)

- Update the default exclude in load_components ([PR 3262](https://github.com/RedHatInsights/insights-core/pull/3262))
- [CloudCfg] Include full context in the output ([PR 3249](https://github.com/RedHatInsights/insights-core/pull/3249))

## [insights-core-3.0.247](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.247) (2021-10-20)

- Add new GrubEnv spec and parser ([PR 3244](https://github.com/RedHatInsights/insights-core/pull/3244))
- Update \_load_component's default exclude ([PR 3252](https://github.com/RedHatInsights/insights-core/pull/3252))
- New spec and parser to check httpd ssl certificate expire date ([PR 3212](https://github.com/RedHatInsights/insights-core/pull/3212))
- RHCLOUD-16475: Investigate error handling issue found by sat team ([PR 3255](https://github.com/RedHatInsights/insights-core/pull/3255))

## [insights-core-3.0.246](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.246) (2021-10-13)

- Add parsers and combiners for data from fwupdagent ([PR 3253](https://github.com/RedHatInsights/insights-core/pull/3253))
- Add links to recent changes  ([PR 3256](https://github.com/RedHatInsights/insights-core/pull/3256))

## [insights-core-3.0.245](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.245) (2021-10-06)

- Add doctest to messages parser ([PR 3248](https://github.com/RedHatInsights/insights-core/pull/3248), [Issue 3029](https://github.com/RedHatInsights/insights-core/issues/3029))
- Update changelog with recent changes ([PR 3247](https://github.com/RedHatInsights/insights-core/pull/3247))
- Add Spec path of chronyc_sources for sos_archive ([PR 3246](https://github.com/RedHatInsights/insights-core/pull/3246))
- Update mdstat parser to remove asserts ([PR 3240](https://github.com/RedHatInsights/insights-core/pull/3240))
- Update the nfnetlink parser ([PR 3239](https://github.com/RedHatInsights/insights-core/pull/3239))
- Replace assert with parse exception in netstat parser ([PR 3238](https://github.com/RedHatInsights/insights-core/pull/3238))
- Enhance awx_manage parser ([PR 3242](https://github.com/RedHatInsights/insights-core/pull/3242))
- Fixing broken sosreport link ([PR 3243](https://github.com/RedHatInsights/insights-core/pull/3243))

## [insights-core-3.0.244](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.244) (2021-09-29)

- [PR 3225](https://github.com/RedHatInsights/insights-core/pull/3225) - Add documentation for `yum_updates` datasource ([Issue 3223](https://github.com/RedHatInsights/insights-core/issues/3223), [Bugzilla 2006300](https://bugzilla.redhat.com/show_bug.cgi?id=2006300))
- [PR 3232](https://github.com/RedHatInsights/insights-core/pull/3232) - Add new combiner AnsibleInfo for ansible information

## [insights-core-3.0.243](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.243) (2021-09-23)

- [PR 3197](https://github.com/RedHatInsights/insights-core/pull/3197) - Add new parser *RosConfig* for file `/var/lib/pcp/config/pmlogger/config.ros`
- [PR 3218](https://github.com/RedHatInsights/insights-core/pull/3218) - Fix issue in HTTPD conf parsers/combiner where directives could have empty strings ([Issue 3211](https://github.com/RedHatInsights/insights-core/issues/3211))
- [PR 3231](https://github.com/RedHatInsights/insights-core/pull/3231) - Preserve alignment in `netstat -neopa` output in client obfuscation

## [insights-core-3.0.242](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.242) (2021-09-22)

- [PR 3219](https://github.com/RedHatInsights/insights-core/pull/3219) - Fix an issue parsing devices in the `lpstat` datasource
- [PR 3221](https://github.com/RedHatInsights/insights-core/pull/3221) - New parsers *LpfcMaxLUNs* for file `/sys/module/lpfc/parameters/lpfc_max_luns`, *Ql2xMaxLUN* for file `/sys/module/qla2xxx/parameters/ql2xmaxlun`, and *SCSIModMaxReportLUNs* for file `/sys/module/scsi_mod/parameters/max_report_luns`
- [PR 3222](https://github.com/RedHatInsights/insights-core/pull/3222) - Fix linting errors and modify setup to use latest version of `flake8`
- [PR 3224](https://github.com/RedHatInsights/insights-core/pull/3224) - Remove parser *Facter* and associated spec and dependencies ([Bugzilla 1989655](https://bugzilla.redhat.com/show_bug.cgi?id=1989655))
- [PR 3226](https://github.com/RedHatInsights/insights-core/pull/3226) - Fix linting errors in client for latest version of `flake8`
- [PR 3227](https://github.com/RedHatInsights/insights-core/pull/3227) - Update verifier in client to remove long suffix for python2
- [PR 3229](https://github.com/RedHatInsights/insights-core/pull/3229) - Update requires for RPM build for RHEL7

## [insights-core-3.0.241](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.241) (2021-09-16)

- [PR 2993](https://github.com/RedHatInsights/insights-core/pull/2993) - Add datasource and parser *YumUpdates* to provide a list of available YUM/DNF updates
- [PR 3144](https://github.com/RedHatInsights/insights-core/pull/3144) - Support insights shell running in ipykernel mode
- [PR 3207](https://github.com/RedHatInsights/insights-core/pull/3207) - Remove unused datasource specs from host collection ([Issue 3087](https://github.com/RedHatInsights/insights-core/issues/3087))
- [PR 3208](https://github.com/RedHatInsights/insights-core/pull/3208) - Add new spec `mssql_api_assessment` to collect file `/var/opt/mssql/log/assessments/assessment-latest`
- [PR 3209](https://github.com/RedHatInsights/insights-core/pull/3209) - Fix an issue where tests were being loaded in insights shell and throwing exceptions about missing modules
- [PR 3214](https://github.com/RedHatInsights/insights-core/pull/3214) - Update client validation code to fix python 2.7 issue
- [PR 3216](https://github.com/RedHatInsights/insights-core/pull/3216) - Remove unused spec `ansible_tower_settings` which was replaced by `awx_manage_print_settings`
- [PR 3217](https://github.com/RedHatInsights/insights-core/pull/3217) - Add missing file for tito RPM build
- [PR 3220](https://github.com/RedHatInsights/insights-core/pull/3220) - Enhance parser *CupsPpd* to handle comments in input

## [insights-core-3.0.240](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.240) (2021-09-01)

- [PR 3112](https://github.com/RedHatInsights/insights-core/pull/3112) - Consolidate network logging and timeouts in client
- [PR 3201](https://github.com/RedHatInsights/insights-core/pull/3201) - Add new parser *CupsPpd* for file glob `/etc/cups/ppd/*`
- [PR 3202](https://github.com/RedHatInsights/insights-core/pull/3202) - Add new parser *LpstatProtocol* for the command `lpstat -v`
- [PR 3203](https://github.com/RedHatInsights/insights-core/pull/3203) - Fix `iter/next` deprecated code in *Lsof* parser ([PR 3185](https://github.com/RedHatInsights/insights-core/pull/3185))
- [PR 3204](https://github.com/RedHatInsights/insights-core/pull/3204) - Add new attribute to *SatelliteSCAStatus* parser to indicate whether SCA is enabled
- [PR 3205](https://github.com/RedHatInsights/insights-core/pull/3205) - Fix regex in *LSBlock* parser to capture all RAID devices
- [PR 3206](https://github.com/RedHatInsights/insights-core/pull/3206) - Add new attribute to *Bond* parser for MII polling interval

## [insights-core-3.0.239](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.239) (2021-08-26)

- [PR 3128](https://github.com/RedHatInsights/insights-core/pull/3128) - Repair malformed SSG version in results for Compliance
- [PR 3195](https://github.com/RedHatInsights/insights-core/pull/3195) - Add the ability to build insights-core as an RPM
- [PR 3196](https://github.com/RedHatInsights/insights-core/pull/3196) - Restore command spec `ss -tupna` to be collected on all systems ([Issue 2909](https://github.com/RedHatInsights/insights-core/issues/2909))
- [PR 3200](https://github.com/RedHatInsights/insights-core/pull/3200) - Revert [PR 3185](https://github.com/RedHatInsights/insights-core/pull/3185)] due to collection issues

## [insights-core-3.0.238](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.238) (2021-08-19)

- [PR 3181](https://github.com/RedHatInsights/insights-core/pull/3181) - Add new parser *AwxManagerPrintSettings* for command `/usr/bin/awx-manage print_settings INSIGHTS_TRACKING_STATE SYSTEM_UUID INSTALL_UUID TOWER_URL_BASE AWX_CLEANUP_PATHS AWX_PROOT_BASE_PATH --format json`
- [PR 3184](https://github.com/RedHatInsights/insights-core/pull/3184) - In support tool `insights run` merge `-N` (show make_none rules) switch with `-S` (show rules by type) switch
- [PR 3185](https://github.com/RedHatInsights/insights-core/pull/3185) - Change code to fix Python functionality deprecated by [PEP 479](https://www.python.org/dev/peps/pep-0479) in Python 3.5
- [PR 3186](https://github.com/RedHatInsights/insights-core/pull/3186) - Update `candlepin_broker` tests to work with newer versions of Python and Pytest ([Issue 3188](https://github.com/RedHatInsights/insights-core/issues/3188))
- [PR 3187](https://github.com/RedHatInsights/insights-core/pull/3187) - Update `setup.py` to work with newer versions of Python and Pytest
- [PR 3189](https://github.com/RedHatInsights/insights-core/pull/3189) - Add new parser *MssqlApiAssessment* for file spec `/var/opt/mssql/log/assessments/assessment-latest`
- [PR 3190](https://github.com/RedHatInsights/insights-core/pull/3190) - Fix *LsPci* combiner to account for unexpected-but-valid data format in in `lspci -k` ([Issue 3176](https://github.com/RedHatInsights/insights-core/issues/3176))
- [PR 3191](https://github.com/RedHatInsights/insights-core/pull/3191) - Remove spec `mssql_api_assessment` merged in [PR 3189](https://github.com/RedHatInsights/insights-core/pull/3189) prior to spec approval
- [PR 3193](https://github.com/RedHatInsights/insights-core/pull/3193) - Fix `ntp_sources` parsers to gracefully account for no NTP sources ([Issue 3192](https://github.com/RedHatInsights/insights-core/issues/3192))
- [PR 3194](https://github.com/RedHatInsights/insights-core/pull/3194) - Fix issues in the collection and validation of canonical facts

## [insights-core-3.0.236](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.236) (2021-08-11)

- [PR 3066](https://github.com/RedHatInsights/insights-core/pull/3066) - In client, add additional messaging for `401` response
- [PR 3141](https://github.com/RedHatInsights/insights-core/pull/3141) - In client, don't add messages that say "to view logs..." to the log file
- [PR 3142](https://github.com/RedHatInsights/insights-core/pull/3142) - In client, allow collections without registration with the `--no-upload` switch
- [PR 3151](https://github.com/RedHatInsights/insights-core/pull/3151) - Compatibility layer legacy upload fix in the client
- [PR 3168](https://github.com/RedHatInsights/insights-core/pull/3168) - In client apply `chmod 644` to lastupload files
- [PR 3171](https://github.com/RedHatInsights/insights-core/pull/3171) - Remove `uploader.json` map file from repo.
- [PR 3174](https://github.com/RedHatInsights/insights-core/pull/3174) - Fix error in *Lsof* parser ([Issue 3172](https://github.com/RedHatInsights/insights-core/issues/3172))
- [PR 3178](https://github.com/RedHatInsights/insights-core/pull/3178) - Add command spec `/usr/sbin/ntpq -pn` for existing parser
- [PR 3180](https://github.com/RedHatInsights/insights-core/pull/3180) - Add new parser *ForemanSSLErrorLog* for file `/var/log/httpd/foreman-ssl_error_ssl.log`
- [PR 3182](https://github.com/RedHatInsights/insights-core/pull/3182) - Fix error in pytest fixture for `test_empty_skip`

## [insights-core-3.0.235](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.235) (2021-08-05)

- [PR 2611](https://github.com/RedHatInsights/insights-core/pull/2611) - In client use a hash function to obfuscate hostname instead of setting it to "host0"
- [PR 3137](https://github.com/RedHatInsights/insights-core/pull/3137) - Add new parser *UdevRulesOracleASM* for file glob `"/etc/udev/rules.d/\*asm*.rules"`
- [PR 3149](https://github.com/RedHatInsights/insights-core/pull/3149) - Add `slot` information to results of parser *LsPci*.
- [PR 3156](https://github.com/RedHatInsights/insights-core/pull/3156) - Add `make_none` response type to enable reporting of rules that return `none` for support/debug.
- [PR 3167](https://github.com/RedHatInsights/insights-core/pull/3167) - Turn on playbook validation in client
- [PR 3169](https://github.com/RedHatInsights/insights-core/pull/3169) - Add new parser *OracleasmSysconfig* for file spec `"/etc/sysconfig/oracleasm"`
- [PR 3170](https://github.com/RedHatInsights/insights-core/pull/3170) - In client, to facilitate removal of the `uploader_json_map.json` file from the egg, resume update of the `/etc/insights-client/.cache.json` file.
- [PR 3173](https://github.com/RedHatInsights/insights-core/pull/3173) - Add additional spec paths for `lsof` data in sosreport
- [PR 3175](https://github.com/RedHatInsights/insights-core/pull/3175) - Add `--show-rules` option to `insights run` command line support tool ([Issue 3161](https://github.com/RedHatInsights/insights-core/issues/3161))
- [PR 3177](https://github.com/RedHatInsights/insights-core/pull/3177) - Fix typo in documentation

## [insights-core-3.0.234](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.234) (2021-07-29)

- [PR 3157](https://github.com/RedHatInsights/insights-core/pull/3157) - Fix issue in base *JSONParser* class causing exceptions when content was empty
- [PR 3162](https://github.com/RedHatInsights/insights-core/pull/3162) - Revert [PR 3154](https://github.com/RedHatInsights/insights-core/pull/3154) due to issues with rules CI tests ([Issue 3161](https://github.com/RedHatInsights/insights-core/issues/3161))
- [PR 3164](https://github.com/RedHatInsights/insights-core/pull/3164) - Add new specs for existing *DnsmasqConf* parser for file glob `glob_file(["/etc/dnsmasq.conf", "/etc/dnsmasq.d/*.conf"])`
- [PR 3166](https://github.com/RedHatInsights/insights-core/pull/3166) - Add insights archive spec for `systemctl_cat_dnsmasq_service` ([Issue 3165](https://github.com/RedHatInsights/insights-core/issues/3165))

## [insights-core-3.0.233](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.233) (2021-07-22)

- [PR 3133](https://github.com/RedHatInsights/insights-core/pull/3133) - Add new parser *AnsibleTowerLicense* for command `/usr/bin/awx-manage check_license --data`
- [PR 3139](https://github.com/RedHatInsights/insights-core/pull/3139) - Fix issue in client in connection logic
- [PR 3148](https://github.com/RedHatInsights/insights-core/pull/3148) - Fix issue in *LsPci* combiner to prevent modification of parser data ([Issue 3147](https://github.com/RedHatInsights/insights-core/issues/3147))
- [PR 3153](https://github.com/RedHatInsights/insights-core/pull/3153) - Fix issue in *LogRotateConf* parser ([Issue 3152](https://github.com/RedHatInsights/insights-core/issues/3152))
- [PR 3154](https://github.com/RedHatInsights/insights-core/pull/3154) - Add new `-S` option to the `insights run` command
- [PR 3155](https://github.com/RedHatInsights/insights-core/pull/3155) - Add new parser *SystemdDnsmasqServiceConf* for command `/bin/systemctl cat dnsmasq.service` ([Issue 3165](https://github.com/RedHatInsights/insights-core/issues/3165))
- [PR 3160](https://github.com/RedHatInsights/insights-core/pull/3160) - Fix issue in tests for `candlepin_broker` datasource

## [insights-core-3.0.232](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.232) (2021-07-15)

Insights-core-3.0.231 was not released into production.  Insights-core-3.0.232 includes all PRs merged in both releases.

- [PR 3135](https://github.com/RedHatInsights/insights-core/pull/3135) - Add new `make_none` response type for rules that return `None`
- [PR 3138](https://github.com/RedHatInsights/insights-core/pull/3138) - Add new parser **HaproxyCfgScl** for file `/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg`
- [PR 3146](https://github.com/RedHatInsights/insights-core/pull/3146) - Revert [PR 3135](https://github.com/RedHatInsights/insights-core/pull/3135) due to rules CI issues

## [insights-core-3.0.230](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.230-1859) (2021-07-08)

- [PR 3053](https://github.com/RedHatInsights/insights-core/pull/3053) - Add new parser **SatelliteMissedQueues** for custom datasource `satellite_missed_pulp_agent_queues`
- [PR 3119](https://github.com/RedHatInsights/insights-core/pull/3119) - Move datasource `package_provides_command` into separate module
- [PR 3122](https://github.com/RedHatInsights/insights-core/pull/3122) - Fix `ethtool` parser exceptions caused by a spec issue ([Issue 1791](https://github.com/RedHatInsights/insights-core/issues/1791))
- [PR 3124](https://github.com/RedHatInsights/insights-core/pull/3124) - Move SAP datasources into separate module
- [PR 3127](https://github.com/RedHatInsights/insights-core/pull/3127) - Add command spec `ipcs_s_i` for command `foreach_execute(ipcs.semid, "/usr/bin/ipcs -s -i %s")` and new datasource for existing parser **IpcsSI**
- [PR 3131](https://github.com/RedHatInsights/insights-core/pull/3131) - Add documentation entry for component `cloud_provider` ([Issue 3130](https://github.com/RedHatInsights/insights-core/issues/3130))
- [PR 3132](https://github.com/RedHatInsights/insights-core/pull/3132) - Convert datasource `is_ceph_monitor` to component **IsCephMonitor**
- [PR 3136](https://github.com/RedHatInsights/insights-core/pull/3136) - Remove unnecessary datasources `is_satellite_server` and `is_satellite_capsule`

## [insights-core-3.0.229-1849](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.229-1849) (2021-07-01)

- [PR 3099](https://github.com/RedHatInsights/insights-core/pull/3099) - Add new datasource and parser **CandlepinBrokerXML** for file `/etc/candlepin/broker.xml`
- [PR 3101](https://github.com/RedHatInsights/insights-core/pull/3101) - Compliance: In client improve tmp handling
- [PR 3120](https://github.com/RedHatInsights/insights-core/pull/3120) - Remove unused Openshift collector specs and related artifacts
- [PR 3121](https://github.com/RedHatInsights/insights-core/pull/3121) - Add new datasource and parser **PsEoCmd** for command `/bin/ps -eo pid,args`
- [PR 3123](https://github.com/RedHatInsights/insights-core/pull/3123) - Add new parser **AnsibleTowerSettings** for file globs `["/etc/tower/settings.py", "/etc/tower/conf.d/*.py"]`
- [PR 3125](https://github.com/RedHatInsights/insights-core/pull/3125) - Fix test for `cloud_init` datasource
- [PR 3126](https://github.com/RedHatInsights/insights-core/pull/3126) - Refactor cloud datasources to components
- [PR 3129](https://github.com/RedHatInsights/insights-core/pull/3129) - Add tests for ps datasources added by [PR 3121](https://github.com/RedHatInsights/insights-core/pull/3121)

## [insights-core-3.0.228-1839](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.228-1839) (2021-06-24)

- [PR 3102](https://github.com/RedHatInsights/insights-core/pull/3102) - Add parser **AnsibleTowerSettings** for glob spec `["/etc/tower/settings.py", "/etc/tower/conf.d/*.py"]`
- [PR 3107](https://github.com/RedHatInsights/insights-core/pull/3107) - Fix attribute error in **AllModProbe** combiner ([Issue 3107](https://github.com/RedHatInsights/insights-core/issues/3107))
- [PR 3110](https://github.com/RedHatInsights/insights-core/pull/3110) - Move `cloud_cfg` custom datasource to a separate module
- [PR 3111](https://github.com/RedHatInsights/insights-core/pull/3111) - In client make a copy of options when loading defaults into `argparse`
- [PR 3114](https://github.com/RedHatInsights/insights-core/pull/3114) - Remove requirement for `futures` python module in `[development]` setup. ([Issue 3113](https://github.com/RedHatInsights/insights-core/issues/3113))
- [PR 3116](https://github.com/RedHatInsights/insights-core/pull/3116) - Fix definition of spec for **AnsibleTowerSettings** parser ([Issue 3115](https://github.com/RedHatInsights/insights-core/issues/3115))
- [PR 3117](https://github.com/RedHatInsights/insights-core/pull/3117) - Remove **AnsibleTowerSettings** parser

## [insights-core-3.0.227-1831](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.227-1831) (2021-06-17)

- [PR 2801](https://github.com/RedHatInsights/insights-core/pull/2801) - Add new parser **GCPInstanceType** for command `/usr/bin/curl -s -H 'Metadata-Flavor: Google' http://metadata.google.internal/computeMetadata/v1/instance/machine-type --connect-timeout 5`
- [PR 3091](https://github.com/RedHatInsights/insights-core/pull/3091) - Add new spec to collect running `httpd` and corresponding RPM package
- [PR 3100](https://github.com/RedHatInsights/insights-core/pull/3100) - Fix issue with non-AWS system being identified as AWS cloud system ([Issue 2904](https://github.com/RedHatInsights/insights-core/issues/2904))
- [PR 3103](https://github.com/RedHatInsights/insights-core/pull/3103) - Add new file spec for SOS reports `/etc/audit/auditd.conf`
- [PR 3104](https://github.com/RedHatInsights/insights-core/pull/3104) - Add new file spec `/proc/partitions` for existing parser
- [PR 3105](https://github.com/RedHatInsights/insights-core/pull/3105) - In client disallow *unregister* in offline mode ([Bugzilla 1920846](https://bugzilla.redhat.com/show_bug.cgi?id=1920946))
- [PR 3106](https://github.com/RedHatInsights/insights-core/pull/3106) - Update pull request template

## [insights-core-3.0.226-1822](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.226-1822) (2021-06-10)

- [PR 3007](https://github.com/RedHatInsights/insights-core/pull/3007) - Add `ansible_host` option to client
- [PR 3092](https://github.com/RedHatInsights/insights-core/pull/3092) - Enhance core to provide binary path to **HttpdV** and **HttpdM** parsers
- [PR 3093](https://github.com/RedHatInsights/insights-core/pull/3093) - Update CONTRIBUTING documentation
- [PR 3094](https://github.com/RedHatInsights/insights-core/pull/3094) - Fix exception in **Scheduler** parser when there is no active scheduler
- [PR 3096](https://github.com/RedHatInsights/insights-core/pull/3096) - Fix restructuredtext formatting in documentation
- [PR 3097](https://github.com/RedHatInsights/insights-core/pull/3097) - Fix incorrect collection spec for Google cloud `gcp_license_codes` ([Issue 3095](https://github.com/RedHatInsights/insights-core/issues/3095))
- [PR 3098](https://github.com/RedHatInsights/insights-core/pull/3098) - Add parser **ForemanSSLAccessLog** for SOS spec `first_file(["var/log/httpd/foreman-ssl_access_ssl.log", r"sos_commands/foreman/foreman-debug/var/log/httpd/foreman-ssl_access_ssl.log"])`

## [insights-core-3.0.225-1814](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.225-1814) (2021-06-03)

- [PR 3055](https://github.com/RedHatInsights/insights-core/pull/3055) - Update client Verifier code to allow for signature validation
- [PR 3089](https://github.com/RedHatInsights/insights-core/pull/3089) - Add a pull request template to the Github project
- [PR 3090](https://github.com/RedHatInsights/insights-core/pull/3090) - Remove duplicate core-collection spec **package_provides_java**

## [insights-core-3.0.224-1809](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.224-1809) (2021-05-26)

- [PR 3014](https://github.com/RedHatInsights/insights-core/pull/3014) - Make handling of err release in `/tmp/insights-client` more secure in client ([Bugzilla 1920344](https://bugzilla.redhat.com/show_bug.cgi?id=1920344))
- [PR 3016](https://github.com/RedHatInsights/insights-core/pull/3016) - Switch to use `/var/tmp/insights-client` instead of `/tmp/insights-client` for client egg release
- [PR 3067](https://github.com/RedHatInsights/insights-core/pull/3067) - Fix parsing for IBM s390 systems in **CpuInfo** parser ([Issue 2629](https://github.com/RedHatInsights/insights-core/issues/2629))
- [PR 3072](https://github.com/RedHatInsights/insights-core/pull/3072) - Add new parser **GrubSysconfig** for the file `/etc/default/grub`
- [PR 3074](https://github.com/RedHatInsights/insights-core/pull/3074) - Fix `IndexError` exception in SMT **CpuCoreOnline** combiner ([Issue 3073](https://github.com/RedHatInsights/insights-core/issues/3073))
- [PR 3075](https://github.com/RedHatInsights/insights-core/pull/3075) - Add support for RHEL 8.4 in Uname parser
- [PR 3077](https://github.com/RedHatInsights/insights-core/pull/3077) - Fix `ValueError` exception in RHEL 6 for **DockerList** parser ([Issue 3076](https://github.com/RedHatInsights/insights-core/issues/3076))
- [PR 3078](https://github.com/RedHatInsights/insights-core/pull/3078) - Update Sosreport spec **journal_since_boot**
- [PR 3080](https://github.com/RedHatInsights/insights-core/pull/3080) - Enable spec for existing **VMwareToolsConf** parser for file `/etc/vmware-tools/tools.conf`
- [PR 3081](https://github.com/RedHatInsights/insights-core/pull/3081) - Add new collection filter to **GreenbootStatus** parser
- [PR 3083](https://github.com/RedHatInsights/insights-core/pull/3083) - Update **Scheduler** parser to add attributes, documentation and tests ([Issue 2997](https://github.com/RedHatInsights/insights-core/issues/2997))
- [PR 3084](https://github.com/RedHatInsights/insights-core/pull/3084) - Add new CLI switch `--color` to allow color in piped commands ([Issue 2980](https://github.com/RedHatInsights/insights-core/issues/2980))

## [insights-core-3.0.223-1796](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.223-1796) (2021-05-18)

- [PR 3060](https://github.com/RedHatInsights/insights-core/pull/3060) - Add kernal-alt releases to **Uname** parser. ([Issue 2770](https://github.com/RedHatInsights/insights-core/issues/2770))
- [PR 3061](https://github.com/RedHatInsights/insights-core/pull/3061) - Update **pmrep_metrics** spec to include additional information.
- [PR 3064](https://github.com/RedHatInsights/insights-core/pull/3064) - Switch to Github actions for CI/CD.
- [PR 3068](https://github.com/RedHatInsights/insights-core/pull/3068) - Fix error in **pmrep_metrics** archive spec ([Issue 3065](https://github.com/RedHatInsights/insights-core/issues/3065))
- [PR 3070](https://github.com/RedHatInsights/insights-core/pull/3070) - Minor documentation update. ([Issue 3069](https://github.com/RedHatInsights/insights-core/issues/3069))

## [insights-core-3.0.222-1790](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.222-1790) (2021-05-13)

- [PR 3038](https://github.com/RedHatInsights/insights-core/pull/3038) - Add new combiner **SysVmBusDeviceInfo** and parsers **SysVmbusDeviceID** for files `/sys/bus/vmbus/devices/*/device_id` and **SysVmbusClassID** for files `/sys/bus/vmbus/devices/*/class_id`
- [PR 3051](https://github.com/RedHatInsights/insights-core/pull/3051) - Changes to core to allow use of new RHEL6/Python26 CI/CD image.
- [PR 3054](https://github.com/RedHatInsights/insights-core/pull/3054) - Update **mongod_conf** spec to remove old files
- [PR 3056](https://github.com/RedHatInsights/insights-core/pull/3056) - Fix **Uname** parser to support debug kernels ([Issue 2709](https://github.com/RedHatInsights/insights-core/issues/2709))
- [PR 3057](https://github.com/RedHatInsights/insights-core/pull/3057) - Fix error introduced by latest version of Jinja2.

## [insights-core-3.0.221-1784](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.221-1784) (2021-05-06)

- [PR 3027](https://github.com/RedHatInsights/insights-core/pull/3027) - Add new parser **RpmOstreeStatus** to collect command `/usr/bin/rpm-ostree status --json`
- [PR 3041](https://github.com/RedHatInsights/insights-core/pull/3041) - Fix error in **SystemdAnalyzeBlame** parser caused by unexpected input ([Issue 3040](https://github.com/RedHatInsights/insights-core/issues/3040))
- [PR 3045](https://github.com/RedHatInsights/insights-core/pull/3045) - Fix error in **VirshListAll** parser caused by unexpected input ([Issue 3044](https://github.com/RedHatInsights/insights-core/issues/3044))
- [PR 3046](https://github.com/RedHatInsights/insights-core/pull/3046) - Change compliance in client to use host ID instead of hostname
- [PR 3048](https://github.com/RedHatInsights/insights-core/pull/3048) - Add contrib module `ruamel.yaml` to client
- [PR 3049](https://github.com/RedHatInsights/insights-core/pull/3049) - Refactor client to pull os-release spec usage out into util function

## [insights-core-3.0.220-1777](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.220-1777) (2021-04-29)

- [PR 3033](https://github.com/RedHatInsights/insights-core/pull/3033) - Add new parser **PMREPMetrics** for command `pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`
- [PR 3035](https://github.com/RedHatInsights/insights-core/pull/3035) - Update sosreport specs for **Pvs**, **Vgs**, **Lvs**, and **Vgdisplay** parsers
- [PR 3036](https://github.com/RedHatInsights/insights-core/pull/3036) - Remove the spec `lsinitrd`
- [PR 3037](https://github.com/RedHatInsights/insights-core/pull/3037) - Ocp and ocpshell supports yaml files with multiple docs
- [PR 3039](https://github.com/RedHatInsights/insights-core/pull/3039) - Update parser **MongodbConf** to parse additional paths
- [PR 3043](https://github.com/RedHatInsights/insights-core/pull/3043) - Fix error in parser **DmsetupStatus** caused by unexpected command output ([Issue 3042](https://github.com/RedHatInsights/insights-core/issues/3042))
- [PR 3047](https://github.com/RedHatInsights/insights-core/pull/3047) - Documentation update for **InstalledRpms** parser

## [insights-core-3.0.219-1769](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.219-1769) (2021-04-22)

- [PR 3023](https://github.com/RedHatInsights/insights-core/pull/3023) - Add new parser **HanaLandscape** for command `foreach_execute(sap_hana_sid_SID_nr, "/bin/su -l %sadm -c 'python /usr/sap/%s/HDB%s/exe/python_support/landscapeHostConfiguration.py'", keep_rc=True)`
- [PR 3024](https://github.com/RedHatInsights/insights-core/pull/3024) - Fix attribute in docs for parser **AzureInstancePlan**
- [PR 3025](https://github.com/RedHatInsights/insights-core/pull/3025) - Update Jenkinsfile to fix issues in Python 2.6 CI
- [PR 3028](https://github.com/RedHatInsights/insights-core/pull/3028) - Revert [PR 3025](https://github.com/RedHatInsights/insights-core/pull/3025) because it was only an intermittent partial fix that was not targeting the real cause
- [PR 3030](https://github.com/RedHatInsights/insights-core/pull/3030) - Add new parser **GCPLicenseCodes** for command `/usr/bin/curl -s curl -H Metadata-Flavor: Google http://metadata.google.internal/computeMetadata/v1/instance/licenses/?recursive=True --connect-timeout 5`
- [PR 3031](https://github.com/RedHatInsights/insights-core/pull/3031) - Add new parser **GreenbootStatus** for command `/usr/libexec/greenboot/greenboot-status`
- [PR 3032](https://github.com/RedHatInsights/insights-core/pull/3032) - Fix parsing errors in **Lvm** parsers ([Issue 3034](https://github.com/RedHatInsights/insights-core/issues/3034))

## [insights-core-3.0.218-1761](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.218-1761) (2021-04-15)

- [PR 2775](https://github.com/RedHatInsights/insights-core/pull/2775) - Enable spec `lsinitrd` for collection of command `/usr/bin/lsinitrd`
- [PR 2865](https://github.com/RedHatInsights/insights-core/pull/2865) - Fix client ultralight checkins: wrap thrown exception with catch
- [PR 2996](https://github.com/RedHatInsights/insights-core/pull/2996) - Add sosreport spec `scheduler` for files `/sys/block/*/queue/scheduler`
- [PR 3000](https://github.com/RedHatInsights/insights-core/pull/3000) - Fix parsing bugs in **RedhatRelease** parser ([Issue 2999](https://github.com/RedHatInsights/insights-core/issues/2999))
- [PR 3001](https://github.com/RedHatInsights/insights-core/pull/3001) - Add `lssap` spec back to insights archives ([Issue 3002](https://github.com/RedHatInsights/insights-core/issues/3002))
- [PR 3003](https://github.com/RedHatInsights/insights-core/pull/3003) - Allow scalars in `parsr.query.choose` results
- [PR 3005](https://github.com/RedHatInsights/insights-core/pull/3005) - Fix issue with documentation build caused by latest version of **Docutils** package
- [PR 3006](https://github.com/RedHatInsights/insights-core/pull/3006) - Update Jenkinsfile to use latest Python 3 CI image
- [PR 3009](https://github.com/RedHatInsights/insights-core/pull/3009) - Update **PuppetCertExpireDate** to used shared base parser
- [PR 3010](https://github.com/RedHatInsights/insights-core/pull/3010) - In client change `validation` function to manually override `skipVerify`
- [PR 3011](https://github.com/RedHatInsights/insights-core/pull/3011) - Update parser CertificatesEnddate to return data if any certificate files found
- [PR 3012](https://github.com/RedHatInsights/insights-core/pull/3012) - Keep return code for specs `ls_etc` and `md5chk_files` so that parser can evaluate results
- [PR 3013](https://github.com/RedHatInsights/insights-core/pull/3013) - Update paths for spec `mongod_conf`
- [PR 3015](https://github.com/RedHatInsights/insights-core/pull/3015) - Update paths for specs `postgresql_conf` and `postgresql_log`
- [PR 3017](https://github.com/RedHatInsights/insights-core/pull/3017) - Add new parser **AzureInstancePlan** for command `/usr/bin/curl -s -H Metadata:true http://169.254.169.254/metadata/instance/compute/plan?api-version=2018-10-01&format=json --connect-timeout 5`
- [PR 3018](https://github.com/RedHatInsights/insights-core/pull/3018) - Remove spec `qpid_stat_g` not used by any rules
- [PR 3019](https://github.com/RedHatInsights/insights-core/pull/3019) - Add new spec `ansible_host` for client collection
- [PR 3020](https://github.com/RedHatInsights/insights-core/pull/3020) - Ensure that the sap_hdb_version spec is only executed for SAP HANA hosts ([Bugzilla 1949056](https://bugzilla.redhat.com/show_bug.cgi?id=1949056))
- [PR 3021](https://github.com/RedHatInsights/insights-core/pull/3021) - Add azure_instance_plan spec to insights archives for older clients
- [PR 3022](https://github.com/RedHatInsights/insights-core/pull/3022) - Modify spec `sap_hdb_version` to use `su` instead of `sudo` ([Bugzilla 1949056](https://bugzilla.redhat.com/show_bug.cgi?id=1949056))

## [insights-core-3.0.217-1741](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.217-1741) (2021-03-31)

- [PR 2894](https://github.com/RedHatInsights/insights-core/pull/2894) - Refactor client to remove `insecure_connection` config option
- [PR 2934](https://github.com/RedHatInsights/insights-core/pull/2934) - Add new parser **SatelliteComputeResources** for command `/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c 'select name, type from compute_resources' --csv`
- [PR 2971](https://github.com/RedHatInsights/insights-core/pull/2971) - Send OS info in profile request
- [PR 2974](https://github.com/RedHatInsights/insights-core/pull/2974) - Use **SIGTERM** on timeout for `rpm` and `yum` commands ([PR 2630](https://github.com/RedHatInsights/insights-core/pull/2630), [Bugzilla 1935846](https://bugzilla.redhat.com/show_bug.cgi?id=1935846))
- [PR 2988](https://github.com/RedHatInsights/insights-core/pull/2988) - Add `loadPlaybookYaml` funtion to verifier functionality
- [PR 2991](https://github.com/RedHatInsights/insights-core/pull/2991) - Add new parser **RhsmKatelloDefaultCACert** for command `/usr/bin/openssl x509 -in /etc/rhsm/ca/katello-default-ca.pem -noout -issuer`insights-core-assets/-/merge_requests/204[MR 204])
- [PR 2992](https://github.com/RedHatInsights/insights-core/pull/2992) - Add new sosreport spec tuned_adm for file `sos_commands/tuned/tuned-adm_list`
- [PR 2994](https://github.com/RedHatInsights/insights-core/pull/2994) - Add `timestamp` attribute to **RhsmLog** parser
- [PR 2995](https://github.com/RedHatInsights/insights-core/pull/2995) - Remove duplicate spec `lspci_kernel`

## [insights-core-3.0.216-1730](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.216-1730) (2021-03-25)

- [PR 2929](https://github.com/RedHatInsights/insights-core/pull/2929) - Add new parser **SatelliteAdminSettings** for command `/usr/bin/sudo -iu postgres /usr/bin/psql -d foreman -c \"select name, value, \\\"default\\\" from settings where name in ('destroy_vm_on_host_delete', 'unregister_delete_host')\" --csv`
- [PR 2981](https://github.com/RedHatInsights/insights-core/pull/2981) - Add new parser **SatelliteCustomCaChain** for command `/usr/bin/awk \'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}\' /etc/pki/katello/certs/katello-server-ca.crt`
- [PR 2983](https://github.com/RedHatInsights/insights-core/pull/2983) - Fix exception in **YumRepolist** parser when repolist is empty ([Issue 2857](https://github.com/RedHatInsights/insights-core/issues/2857))
- [PR 2985](https://github.com/RedHatInsights/insights-core/pull/2985) - Fix issue with deserialization of datasources as raw instead of text ([Issue 2970](https://github.com/RedHatInsights/insights-core/issues/2970))
- [PR 2987](https://github.com/RedHatInsights/insights-core/pull/2987) - Updates to edge cases, documentation and tests, and fix parsing of trailing whitespace for Tuned parser ([Issue 2986](https://github.com/RedHatInsights/insights-core/issues/2986))
- [PR 2990](https://github.com/RedHatInsights/insights-core/pull/2990) - Fix issue in LogRotate parser where missing endscript caused an infinite loop ([Issue 2989](https://github.com/RedHatInsights/insights-core/issues/2989))

## [insights-core-3.0.215-1722](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.215-1722) (2021-03-18)

- [PR 2945](https://github.com/RedHatInsights/insights-core/pull/2945) - Implement playbook signature validation logic in insights-core
- [PR 2973](https://github.com/RedHatInsights/insights-core/pull/2973) - Add new parser **LsPciVmmkn** for command `/sbin/lspci -vmmkn`
- [PR 2979](https://github.com/RedHatInsights/insights-core/pull/2979) - Remove deprecated warning for parser **VirtUuidFacts**
- [PR 2982](https://github.com/RedHatInsights/insights-core/pull/2982) - Add new combiner **LsPci** for the `lspci` command parsers

## [insights-core-3.0.214-1717](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.214-1717) (2021-03-11)

- [PR 2888](https://github.com/RedHatInsights/insights-core/pull/2888) - Activate checkin timer in client
- [PR 2969](https://github.com/RedHatInsights/insights-core/pull/2969) - Update parser and test to detect lssap issue in [Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?id=1922937)
- [PR 2972](https://github.com/RedHatInsights/insights-core/pull/2972) - Change uses of deprecated **hostname** combiner to **Hostname** combiner
- [PR 2975](https://github.com/RedHatInsights/insights-core/pull/2975) - Remove **lssap** spec from collection ([Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?id=1922937), [Bugzilla 1936951](https://bugzilla.redhat.com/show_bug.cgi?id=1936951)
- [PR 2976](https://github.com/RedHatInsights/insights-core/pull/2976) - Enhance the **SAP** combiner to use both hostname and FQDN

## [insights-core-3.0.213-1710](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.213-1710) (2021-03-04)

- [PR 2926](https://github.com/RedHatInsights/insights-core/pull/2926) - Add new parser DmsetupStatus for command `/usr/sbin/dmsetup status`
- [PR 2939](https://github.com/RedHatInsights/insights-core/pull/2939) - Update non-working parser **PidLdLibraryPath** and rename to **UserLdLibraryPath** for spec **ld_library_path_of_user**
- [PR 2965](https://github.com/RedHatInsights/insights-core/pull/2965) - Update **ld_library_path_of_user** spec to only collect information for SAP application users
- [PR 2966](https://github.com/RedHatInsights/insights-core/pull/2966) - Add `microcode` keyword value in the **CpuInfo** parser
- [PR 2967](https://github.com/RedHatInsights/insights-core/pull/2967) - Add new value `kernel.all.cpu.wait.total` to **pmlog_summary** spec

## [insights-core-3.0.212-1703](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.212-1703) (2021-02-25)

- [PR 2936](https://github.com/RedHatInsights/insights-core/pull/2936) - In client add check for null PATH environment variable before using it
- [PR 2950](https://github.com/RedHatInsights/insights-core/pull/2950) - Add new parser **PmLogSummary** for command `/usr/bin/pmlogsummary`
- [PR 2960](https://github.com/RedHatInsights/insights-core/pull/2960) - Add new sosreport spec **mdadm_E** for file glob `sos_commands/md/mdadm_-E_*`
- [PR 2961](https://github.com/RedHatInsights/insights-core/pull/2961) - Add new parser **InsightsClientConf** for file `/etc/insights-client/insights-client.conf`
- [PR 2963](https://github.com/RedHatInsights/insights-core/pull/2963) - Fix problem with exception logging in core collection ([Issue 2962](https://github.com/RedHatInsights/insights-core/issues/2962))

## [insights-core-3.0.211-1696](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.211-1696) (2021-02-18)

- [PR 2953](https://github.com/RedHatInsights/insights-core/pull/2953) - Fix handling of edge cases for **Sealert** parser ([Issue 2951](https://github.com/RedHatInsights/insights-core/issues/2951))
- [PR 2955](https://github.com/RedHatInsights/insights-core/pull/2955) - Fix problem with exceptions during collection in `corosync_cmapctl_cmd_list` datasource ([Issue 2954](https://github.com/RedHatInsights/insights-core/issues/2954))

## [insights-core-3.0.210-1692](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.210-1692) (2021-02-11)

- [PR 2905](https://github.com/RedHatInsights/insights-core/pull/2905) - Add new parser **LsVarCachePulp** for command `/bin/ls -lan /var/cache/pulp`
- [PR 2923](https://github.com/RedHatInsights/insights-core/pull/2923) - Additional paths to collect for **postgresql_log**, `/var/opt/rh/rh-postgresql12/lib/pgsql/data/log/postgresql-*.log`, and for **postgresql_conf**, `/var/opt/rh/rh-postgresql12/lib/pgsql/data/postgresql.conf`
- [PR 2944](https://github.com/RedHatInsights/insights-core/pull/2944) - Fix bug in **VirshListAll** parser to correctly handle uppercase VM names
- [PR 2946](https://github.com/RedHatInsights/insights-core/pull/2946) - Prevent soscleaner in client from erasing `insights_archive.txt`
- [PR 2949](https://github.com/RedHatInsights/insights-core/pull/2949) - Catch rules that add a blank filter for a filterable spec ([Issue 2948](https://github.com/RedHatInsights/insights-core/issues/2948))

## [insights-core-3.0.209-1685](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.209-1685) (2021-02-05)

- [PR 2869](https://github.com/RedHatInsights/insights-core/pull/2869) - Remove Satellite specs for EOL versions of Satellite
- [PR 2902](https://github.com/RedHatInsights/insights-core/pull/2902) - Add new parser **PidLdLibraryPath** for spec `ld_library_path_of_pid` which captures the PID and LD_LIBRARY_PATH value for the running process
- [PR 2906](https://github.com/RedHatInsights/insights-core/pull/2906) - Add new parser **MongoDBNonYumTypeRepos** for command spec `mongo pulp_database --eval 'db.repo_importers.find({"importer_type_id": { $ne: "yum_importer"}}).count()'`
- [PR 2910](https://github.com/RedHatInsights/insights-core/pull/2910) - Add new parser **GFS2FileSystemBlockSize** for command spec `foreach_execute(gfs2_mount_points, "/usr/bin/stat -fc %%s %s")`
- [PR 2917](https://github.com/RedHatInsights/insights-core/pull/2917) - Enhance IP parsers to get `promiscuity` data
- [PR 2919](https://github.com/RedHatInsights/insights-core/pull/2919) - Enhance collection of SAP HDB version for all instances on a system
- [PR 2921](https://github.com/RedHatInsights/insights-core/pull/2921) - Fix issue in collection of file `/etc/cloud/cloud.cfg` which caused exceptions to be logged in the client log ([Issue 2920](https://github.com/RedHatInsights/insights-core/issues/2920), [Bugzilla 1922937](https://bugzilla.redhat.com/show_bug.cgi?-d=1922937), [Bugzilla 1923120](https://bugzilla.redhat.com/show_bug.cgi?id=1923120), [Bugzilla 1922269](https://bugzilla.redhat.com/show_bug.cgi?id=1922269))
- [PR 2922](https://github.com/RedHatInsights/insights-core/pull/2922) - Fix issue with collection of spec **sap_hdb_version** from Insights archives ([Issue 2812](https://github.com/RedHatInsights/insights-core/issues/2812))
- [PR 2924](https://github.com/RedHatInsights/insights-core/pull/2924) - Add new spec **virsh_list_all** to collect sosreport file `sos_commands/virsh/virsh_-r_list_--all`
- [PR 2925](https://github.com/RedHatInsights/insights-core/pull/2925) - Enhance **IsRhel[678]** components to include RHEL`minor` version
- [PR 2927](https://github.com/RedHatInsights/insights-core/pull/2927) - Fix client checkin URL with legacy upload
- [PR 2930](https://github.com/RedHatInsights/insights-core/pull/2930) - Add new parser **VersionInfo** for existing spec collecting versions of the client and insights-core

## [insights-core-3.0.208-1673](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.208-1673) (2021-01-28)

- [PR 2893](https://github.com/RedHatInsights/insights-core/pull/2893) - Add several useful features to parsr.query
- [PR 2897](https://github.com/RedHatInsights/insights-core/pull/2897) - Add new parser UdevRules40Redhat for files `/etc/udev/rules.d/40-redhat.rules`, `/run/udev/rules.d/40-redhat.rules`, `/usr/lib/udev/rules.d/40-redhat.rules`, `/usr/local/lib/udev/rules.d/40-redhat.rules`
- [PR 2907](https://github.com/RedHatInsights/insights-core/pull/2907) - Fix issue in `dr.set_enabled` to work with components and component names ([Issue 2903](https://github.com/RedHatInsights/insights-core/issues/2903))
- [PR 2911](https://github.com/RedHatInsights/insights-core/pull/2911) - Fix issue in custom datasources to only execute when collecting in *HostContext* ([Issue 2908](https://github.com/RedHatInsights/insights-core/issues/2908))
- [PR 2914](https://github.com/RedHatInsights/insights-core/pull/2914) - Fix issue with unhelpful debug messages appearing in client log ([Issue 2912](https://github.com/RedHatInsights/insights-core/issues/2912))
- [PR 2915](https://github.com/RedHatInsights/insights-core/pull/2915) - Remove debug messages generated when commands fail during serialization ([Issue 2913](https://github.com/RedHatInsights/insights-core/issues/2913))
- [PR 2918](https://github.com/RedHatInsights/insights-core/pull/2918) - Fix issue in client with collection of `version_info` when performing core collection

## [insights-core-3.0.207-1668](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.207-1668) (2021-01-26)

- [PR 2868](https://github.com/RedHatInsights/insights-core/pull/2868) - Fix issue in client with HTTP_PROXY warning condition

## [insights-core-3.0.206-1666](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.206-1666) (2021-01-21)

- [PR 2849](https://github.com/RedHatInsights/insights-core/pull/2849) - Add new parser **YumUpdateinfo** for command `/usr/bin/yum -C updateinfo list`
- [PR 2861](https://github.com/RedHatInsights/insights-core/pull/2861) - Add new parser **CloudCfg** for file `/etc/cloud/cloud.cfg`
- [PR 2901](https://github.com/RedHatInsights/insights-core/pull/2901) - Show original exceptions for mapped or lifted functions ([Issue 2900](https://github.com/RedHatInsights/insights-core/issues/2900))

## [insights-core-3.0.205-1661](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.205-1661) (2021-01-15)

- [PR 2896](https://github.com/RedHatInsights/insights-core/pull/2896) - Add new spec **lsblk_pairs** to collect the sosreport file `sos_commands/block/lsblk_-O_-P`
- [PR 2899](https://github.com/RedHatInsights/insights-core/pull/2899) - Fix issue in core for RHEL 6 version of six python module ([Issue 2989](https://github.com/RedHatInsights/insights-core/issues/2989))

## [insights-core-3.0.203-1657](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.203-1657) (2021-01-14)

- [PR 2863](https://github.com/RedHatInsights/insights-core/pull/2863) - Fix memory and performance issues in *parsr* module ([Issue 2863](https://github.com/RedHatInsights/insights-core/issues/2863))
- [PR 2879](https://github.com/RedHatInsights/insights-core/pull/2879) - Fix error in command line support tools due to conflicting python modules ([Issue 2878](https://github.com/RedHatInsights/insights-core/issues/2878))
- [PR 2881](https://github.com/RedHatInsights/insights-core/pull/2881) - Fix error in *chkconfig* and *unitfiles* specs when no useful data is collected ([Issue 2882](https://github.com/RedHatInsights/insights-core/issues/2882))
- [PR 2884](https://github.com/RedHatInsights/insights-core/pull/2884) - Documentation fixes
- [PR 2887](https://github.com/RedHatInsights/insights-core/pull/2887) - Enhance spec *satellite_content_hosts_count* to only execute during core collection and only run on Satellite hosts
- [PR 2890](https://github.com/RedHatInsights/insights-core/pull/2890) - Fix issue in *first_file* spec that prevented collection of some specs ([Issue 2889](https://github.com/RedHatInsights/insights-core/issues/2889))
- [PR 2891](https://github.com/RedHatInsights/insights-core/pull/2891) - Fix issue in core collection spec that caused client timeouts ([Bugzilla 1915219](https://bugzilla.redhat.com/show_bug.cgi?id=1915219))
- [PR 2892](https://github.com/RedHatInsights/insights-core/pull/2892) - Documentation fixes ([Issue 2862](https://github.com/RedHatInsights/insights-core/issues/2862))

## [insights-core-3.0.202-1647](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.202-1647) (2021-01-07)

- [PR 2841](https://github.com/RedHatInsights/insights-core/pull/2841) - Enhance combiners and parsers for *package_provides_java* and *package_provides_httpd*
- [PR 2846](https://github.com/RedHatInsights/insights-core/pull/2846) - Add new parser *MDAdmMetadata* for command `foreach_execute(md_device_list, "/usr/sbin/mdadm -E %s")`
- [PR 2847](https://github.com/RedHatInsights/insights-core/pull/2847) - Re-add specs *saphostexec_status* and *saphostexec_version* for core collection
- [PR 2856](https://github.com/RedHatInsights/insights-core/pull/2856) - Add new parser *LsIPAIdoverrideMemberof* for command `/bin/ls -lan /usr/share/ipa/ui/js/plugins/idoverride-memberof`
- [PR 2860](https://github.com/RedHatInsights/insights-core/pull/2860) - Add new parser *SatelliteContentHostsCount* for command `/usr/bin/sudo -iu postgres psql -d foreman -c 'select count(*) from hosts'`
- [PR 2864](https://github.com/RedHatInsights/insights-core/pull/2864) - Remove "unknown device" string from possible LVM warnings (Solutions [1535693](https://access.redhat.com/solutions/1535693), [45108](https://access.redhat.com/solutions/45108))
- [PR 2867](https://github.com/RedHatInsights/insights-core/pull/2867) - Update client Compliance error message when no policies are assigned to the system
- [PR 2870](https://github.com/RedHatInsights/insights-core/pull/2870) - Add latest Ceph version mapping for parser *CephVersion* (Solution [2045583](https://access.redhat.com/solutions/2045583))
- [PR 2873](https://github.com/RedHatInsights/insights-core/pull/2873) - Add *LsMod* parser to preloaded components for use by client ([Issue 2872](https://github.com/RedHatInsights/insights-core/issues/2872))
- [PR 2874](https://github.com/RedHatInsights/insights-core/pull/2874) - Add spec *mokutil_sbstate* to sosreport specs for `sos_commands/boot/mokutil_--sb-state`
- [PR 2875](https://github.com/RedHatInsights/insights-core/pull/2875) - Add new parser *PuppetCertExpireDate* for command `/usr/bin/openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout`
- [PR 2877](https://github.com/RedHatInsights/insights-core/pull/2877) - Add spec *ls_sys_firmware* to sosreport specs for `sos_commands/boot/ls_-lanR_.sys.firmware`

## [insights-core-3.0.201-1634](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.201-1634) (2020-12-10)

- Commit 6ad8c2 - Fix client tests for core collection only spec
- [PR 2807](https://github.com/RedHatInsights/insights-core/pull/2807) - Add support in the client for the hourly ultra-light check-ins
- [PR 2836](https://github.com/RedHatInsights/insights-core/pull/2836) - Add new parser *PythonAlternatives* for command `/usr/sbin/alternatives --display python`
- [PR 2837](https://github.com/RedHatInsights/insights-core/pull/2837) - Add new parser *LsUsrBin* for command `/bin/ls -lan /usr/bin`
- [PR 2845](https://github.com/RedHatInsights/insights-core/pull/2845) - Add `warnings` attribute to *LVM* parsers
- [PR 2848](https://github.com/RedHatInsights/insights-core/pull/2848) - Fix bug in SAPHostExecStatus and SAPHostExecVersion parsers that didn't handle empty output correctly
- [PR 2850](https://github.com/RedHatInsights/insights-core/pull/2850) - Add precheck for modules before running command `ss -tupna` ([Bugzilla 1903183](https://bugzilla.redhat.com/show_bug.cgi?id=1903183))
- [PR 2852](https://github.com/RedHatInsights/insights-core/pull/2852) - Skip `None` value when doing keyword_search ([Issue 2851](https://github.com/RedHatInsights/insights-core/issues/2851))
- [PR 2853](https://github.com/RedHatInsights/insights-core/pull/2853) - Skip the `grep -F` in ps in the first pass of parsing ([Issue 2851](https://github.com/RedHatInsights/insights-core/issues/2851))
- [PR 2854](https://github.com/RedHatInsights/insights-core/pull/2854) - Add spec `subscription_manager_installed_product_ids = simple_command("/usr/bin/find /etc/pki/product-default/ /etc/pki/product/ -name '*pem' -exec rct cat-cert --no-content '{}' \;")` for core collection for existing parser, spec was already being collected in the JSON ([Bugzilla 1905503](https://bugzilla.redhat.com/show_bug.cgi?id=1905503))
- [PR 2855](https://github.com/RedHatInsights/insights-core/pull/2855) - Enhance *InstalledRpms* parser vendor attribute
- [PR 2858](https://github.com/RedHatInsights/insights-core/pull/2858) - Add spec `corosync_cmapctl = foreach_execute(corosync_cmapctl_cmd_list, "%s")` for core collection for existing parser
- [PR 2859](https://github.com/RedHatInsights/insights-core/pull/2859) - Add spec `httpd_limits = foreach_collect(httpd_pid, "/proc/%s/limits")` for core collection for existing parser

## [insights-core-3.0.200-1621](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.200-1621) (2020-12-03)

- [PR 2833](https://github.com/RedHatInsights/insights-core/pull/2833) - Add new parser *Postconf* for command `/usr/sbin/postconf` and enable command `/usr/bin/postconf -C builtin` for parser *PostconfBuiltin* (
- [PR 2839](https://github.com/RedHatInsights/insights-core/pull/2839) - Remove unused SAP specs from core collection
- [PR 2844](https://github.com/RedHatInsights/insights-core/pull/2844) - In client fix playbook verify, remove placeholder module

## [insights-core-3.0.199-1616](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.199-1616) (2020-11-20)

- [PR 2831](https://github.com/RedHatInsights/insights-core/pull/2831) - Add spec for file `display_name` to core collection archive

## [insights-core-3.0.198-1614](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.198-1614) (2020-11-19)

- [PR 2797](https://github.com/RedHatInsights/insights-core/pull/2797) - Add new parser *Doveconf* for command `/usr/bin/doveconf`
- [PR 2814](https://github.com/RedHatInsights/insights-core/pull/2814) - Add capability to client to verify Ansible playbooks
- [PR 2825](https://github.com/RedHatInsights/insights-core/pull/2825) - Fix error with collection of `sap_hdb_version` spec in core collection
- [PR 2826](https://github.com/RedHatInsights/insights-core/pull/2826) - Fix error with collection of `is_aws`, `is_azure`, and `pcp_enabled` specs in core collection
- [PR 2827](https://github.com/RedHatInsights/insights-core/pull/2827) - Fix issue with core collection where filtering command is captured in output
- [PR 2828](https://github.com/RedHatInsights/insights-core/pull/2828) - Reenable collection of DNF modules data
- [PR 2829](https://github.com/RedHatInsights/insights-core/pull/2829) - Fix error in collecting `foreach_execute` specs ([Issue 2824](https://github.com/RedHatInsights/insights-core/issues/2824))

## [insights-core-3.0.197-1606](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.197-1606) (2020-11-12)

- [PR 2121](https://github.com/RedHatInsights/insights-core/pull/2121) - Add combiner *RsyslogAllConf* and update parser *RsyslogConf* ([PR 2818](https://github.com/RedHatInsights/insights-core/pull/2818), [PR 2819](https://github.com/RedHatInsights/insights-core/pull/2819))
- [PR 2791](https://github.com/RedHatInsights/insights-core/pull/2791) - Enable specs for _must_gather_ archives
- [PR 2792](https://github.com/RedHatInsights/insights-core/pull/2792) - Add `--module` option to client to all running modules from the CLI
- [PR 2811](https://github.com/RedHatInsights/insights-core/pull/2811) - Add new parser *UdevRules40Redhat* for file `/etc/udev/rules.d/40-redhat.rules`
- [PR 2815](https://github.com/RedHatInsights/insights-core/pull/2815) - Enhance *parsr* module to include `line` convenience method ([Issue 2798](https://github.com/RedHatInsights/insights-core/issues/2798))
- [PR 2816](https://github.com/RedHatInsights/insights-core/pull/2816) - Ensure `branch_info` is collected as a raw file
- [PR 2817](https://github.com/RedHatInsights/insights-core/pull/2817) - Add latest RHEL 8 kernels to *Uname* parser
- [PR 2820](https://github.com/RedHatInsights/insights-core/pull/2820) - Update *YumRepoList* parser to correctly recognize Satellite repos
- [PR 2822](https://github.com/RedHatInsights/insights-core/pull/2822) - Fix error in `df` command spec that triggered mounting of unmounted filesystems ([Bugzilla 1880030](https://bugzilla.redhat.com/show_bug.cgi?id=1880030))
- [PR 2823](https://github.com/RedHatInsights/insights-core/pull/2823) - Fix error in spec `rsyslog_conf` for core collection

## [insights-core-3.0.196-1593](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.196-1593) (2020-11-05)

- Commit 0c4cbb0 - Update developer notes for client directory
- [PR 2796](https://github.com/RedHatInsights/insights-core/pull/2796) - Add new parser *PostconfBuiltin* for command `/usr/sbin/postconf -C builtin`
- [PR 2804](https://github.com/RedHatInsights/insights-core/pull/2804) - In client add capability to redact glob specs by symbolic name
- [PR 2810](https://github.com/RedHatInsights/insights-core/pull/2810) - Modify *HDBVersion* parser to support collection of `sap_hdb_version` in JSON ([Issue 2812](https://github.com/RedHatInsights/insights-core/issues/2812))

## [insights-core-3.0.195-1588](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.195-1588) (2020-11-01)

- [PR 2808](https://github.com/RedHatInsights/insights-core/pull/2808) - In client fix minor typo in registration log message
- [PR 2809](https://github.com/RedHatInsights/insights-core/pull/2809) - Ensure that *Sap* combiner uses short hostname for for comparisons

## [insights-core-3.0.194-1586](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.194-1586) (2020-10-29)

- [PR 2722](https://github.com/RedHatInsights/insights-core/pull/2722) - In client cleanup temp dir created for egg download ([Issue 2721](https://github.com/RedHatInsights/insights-core/issues/2721))
- [PR 2786](https://github.com/RedHatInsights/insights-core/pull/2786) - Add new parser *SambaConfigs* for command spec `/usr/bin/testparm -s` and *SambaConfigsAll* for command spec `/usr/bin/testparm -v -s`
- [PR 2794](https://github.com/RedHatInsights/insights-core/pull/2794) - Add new parser *NetworkManagerConfig* for file spec `/etc/NetworkManager/NetworkManager.conf`
- [PR 2795](https://github.com/RedHatInsights/insights-core/pull/2795) - In client delete pid files on exit
- [PR 2799](https://github.com/RedHatInsights/insights-core/pull/2799) - Save the raised exception raised by subscription manager spec in SubscriptionManagerListConsumed and SubscriptionManagerListInstalled parsers
- [PR 2802](https://github.com/RedHatInsights/insights-core/pull/2802) - Add new parser DotNetVersion for command spec `/usr/bin/dotnet --version`
- [PR 2805](https://github.com/RedHatInsights/insights-core/pull/2805) - Re-add spec *sap_hdb_version* for command `foreach_execute(sap_sid, "/usr/bin/sudo -iu %sadm HDB version", keep_rc=True)` for existing parser *HDBVersion*

## [insights-core-3.0.193-1576](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.193-1576) (2020-10-22)

- [PR 2767](https://github.com/RedHatInsights/insights-core/pull/2767) - Add new parser *PHPConf* for file `first_file(["/etc/opt/rh/php73/php.ini", "/etc/opt/rh/php72/php.ini", "/etc/php.ini"])`
- [PR 2778](https://github.com/RedHatInsights/insights-core/pull/2778) - Add new parser *VHostNetZeroCopyTx* for file `/sys/module/vhost_net/parameters/experimental_zcopytx`
- [PR 2782](https://github.com/RedHatInsights/insights-core/pull/2782) - Fix warning in client when skipping a glob file spec
- [PR 2784](https://github.com/RedHatInsights/insights-core/pull/2784) - Add new parser *AbrtCCppConf* for file `/etc/abrt/plugins/CCpp.conf`
- [PR 2787](https://github.com/RedHatInsights/insights-core/pull/2787) - Fix bug in command line utilities (not client) for core archive collection ([Issue 2788](https://github.com/RedHatInsights/insights-core/issues/2788))
- [PR 2789](https://github.com/RedHatInsights/insights-core/pull/2789) - Add IBM cloud detection to *CloudProvider* combiner, refactor combiner
- [PR 2790](https://github.com/RedHatInsights/insights-core/pull/2790) - Include rhsm_conf module in documentation build

## [insights-core-3.0.192](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.192-1568) (2020-10-19)

- [PR 2783](https://github.com/RedHatInsights/insights-core/pull/2783) - Add new sosreport spec *firewall_cmd_list_all_zones* for file `sos_commands/firewalld/firewall-cmd_--list-all-zones`
- [PR 2785](https://github.com/RedHatInsights/insights-core/pull/2785) - Add new spec *du_dirs* for command `foreach_execute(['/var/lib/candlepin/activemq-artemis'], "/bin/du -s -k %s")`

## [insights-core-3.0.191-1564](https://github.com/RedHatInsights/insights-core/releases/tag/insights-core-3.0.191-1564) (2020-10-14)

- [PR 2764](https://github.com/RedHatInsights/insights-core/pull/2764) - Add collection stats file to client for data collection info
- [PR 2771](https://github.com/RedHatInsights/insights-core/pull/2771) - Update client to generate log and lib dirs
- [PR 2781](https://github.com/RedHatInsights/insights-core/pull/2781) - Fix client hosts file parsing for core collection and soscleaner

## [insights-core-3.0.164-1413](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.164-1413) (2020-05-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.163-1399...insights-core-3.0.164-1413)

**Closed issues:**

- "apicid" is duplicated in CpuInfo [\#2582](https://github.com/RedHatInsights/insights-core/issues/2582)

## [insights-core-3.0.163-1399](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.163-1399) (2020-05-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.162-1395...insights-core-3.0.163-1399)

**Fixed bugs:**

- Reporting the wrong number of cores\_total [\#2555](https://github.com/RedHatInsights/insights-core/issues/2555)

**Closed issues:**

- Please add parser: ovs\_vsctl\_list\_interface for sosreport [\#1977](https://github.com/RedHatInsights/insights-core/issues/1977)
- Please add parser:OVSvsctlListBridge for sosreport [\#1976](https://github.com/RedHatInsights/insights-core/issues/1976)

## [insights-core-3.0.162-1395](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.162-1395) (2020-04-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.161-1385...insights-core-3.0.162-1395)

**Implemented enhancements:**

- Include archive type and plugin repo status information in analyses [\#2560](https://github.com/RedHatInsights/insights-core/issues/2560)
- Use igzip if it's available for tar decompression with fallback to gunzip. [\#2547](https://github.com/RedHatInsights/insights-core/issues/2547)

**Fixed bugs:**

- semid datasource shouldn't have a RegistryPoint [\#2528](https://github.com/RedHatInsights/insights-core/issues/2528)

## [insights-core-3.0.161-1385](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.161-1385) (2020-04-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.160-1380...insights-core-3.0.161-1385)

**Closed issues:**

- Better print out the 'result' when 'assert' failed in test [\#2551](https://github.com/RedHatInsights/insights-core/issues/2551)

## [insights-core-3.0.160-1380](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.160-1380) (2020-04-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.159-1375...insights-core-3.0.160-1380)

**Fixed bugs:**

- The path of command "db2licm" in spec is incorrect  [\#2452](https://github.com/RedHatInsights/insights-core/issues/2452)

## [insights-core-3.0.159-1375](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.159-1375) (2020-04-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.158-1365...insights-core-3.0.159-1375)

**Fixed bugs:**

- Sphinx 3.0 breaks documentation build [\#2531](https://github.com/RedHatInsights/insights-core/issues/2531)

## [insights-core-3.0.158-1365](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.158-1365) (2020-04-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.157-1359...insights-core-3.0.158-1365)

**Fixed bugs:**

- Block-size of 'df -al' is not always default to 1K. DiskFree\_AL and DiskFree\_ALP need handle this. [\#2502](https://github.com/RedHatInsights/insights-core/issues/2502)

**Closed issues:**

- A base class for YumList\* are needed for more "yum list \[xxx\]" commands [\#2524](https://github.com/RedHatInsights/insights-core/issues/2524)
- KpatchPatches \(kpatch\_patch\_files\) can be replaced with KpatchList \(kpatch\_list\) [\#2403](https://github.com/RedHatInsights/insights-core/issues/2403)

## [insights-core-3.0.157-1359](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.157-1359) (2020-03-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.156-1352...insights-core-3.0.157-1359)

**Closed issues:**

- RhsmReleaseVer does not handle when release version is None [\#2509](https://github.com/RedHatInsights/insights-core/issues/2509)
- NeutronConf parser is broken [\#2412](https://github.com/RedHatInsights/insights-core/issues/2412)

## [insights-core-3.0.156-1352](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.156-1352) (2020-03-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.155-1346...insights-core-3.0.156-1352)

## [insights-core-3.0.155-1346](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.155-1346) (2020-03-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.154-1343...insights-core-3.0.155-1346)

## [insights-core-3.0.154-1343](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.154-1343) (2020-03-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.153-1338...insights-core-3.0.154-1343)

**Fixed bugs:**

- InsightsEvaluator ignores its stream argument during construction [\#2483](https://github.com/RedHatInsights/insights-core/issues/2483)

**Closed issues:**

- Issue with 'firewalld\_conf' spec collection [\#2485](https://github.com/RedHatInsights/insights-core/issues/2485)

## [insights-core-3.0.153-1338](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.153-1338) (2020-02-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.152-1327...insights-core-3.0.153-1338)

**Fixed bugs:**

- Spec `yum -C repolist` should not load plugins [\#2473](https://github.com/RedHatInsights/insights-core/issues/2473)

**Closed issues:**

- Imprprovement for bond parser [\#2478](https://github.com/RedHatInsights/insights-core/issues/2478)
- "timestamp" returned by Syslog doesn't comply with the raw format in log in some cases [\#2454](https://github.com/RedHatInsights/insights-core/issues/2454)
- Documentation of mount.py should be updated [\#2276](https://github.com/RedHatInsights/insights-core/issues/2276)

## [insights-core-3.0.152-1327](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.152-1327) (2020-02-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.151-1319...insights-core-3.0.152-1327)

**Implemented enhancements:**

- Bond parser is not collecting data for currently active primary\_slave [\#2466](https://github.com/RedHatInsights/insights-core/issues/2466)

**Closed issues:**

- Enhance parser "satellite\_installer\_configurations" [\#2469](https://github.com/RedHatInsights/insights-core/issues/2469)
- YAMLParser shouldn't raise ParseException when the file is empty [\#2467](https://github.com/RedHatInsights/insights-core/issues/2467)

## [insights-core-3.0.151-1319](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.151-1319) (2020-02-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.150-1...insights-core-3.0.151-1319)

**Closed issues:**

- Extend insights.core.filters.add\_filter\(\) functionality [\#2429](https://github.com/RedHatInsights/insights-core/issues/2429)
- Create a PS combiner to consolidate data from PS parsers  [\#2423](https://github.com/RedHatInsights/insights-core/issues/2423)

## [insights-core-3.0.150-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.150-1) (2020-02-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.149-1309...insights-core-3.0.150-1)

## [insights-core-3.0.149-1309](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.149-1309) (2020-02-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.148-1...insights-core-3.0.149-1309)

## [insights-core-3.0.148-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.148-1) (2020-02-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.147-1...insights-core-3.0.148-1)

**Fixed bugs:**

- Curl command is returning stats in data, command should use --silent switch [\#2441](https://github.com/RedHatInsights/insights-core/issues/2441)
- Command spec readlink\_e\_etc\_mtab is missing path for command [\#2409](https://github.com/RedHatInsights/insights-core/issues/2409)

## [insights-core-3.0.147-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.147-1) (2020-02-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.146-1...insights-core-3.0.147-1)

## [insights-core-3.0.146-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.146-1) (2020-02-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.145-1300...insights-core-3.0.146-1)

**Fixed bugs:**

- Fatal error if run client with invalid remove\_file \(BZ1550109\) [\#975](https://github.com/RedHatInsights/insights-core/issues/975)

## [insights-core-3.0.145-1300](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.145-1300) (2020-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.144-1295...insights-core-3.0.145-1300)

**Closed issues:**

- PsEo parser is raising ValueError exception [\#2435](https://github.com/RedHatInsights/insights-core/issues/2435)

## [insights-core-3.0.144-1295](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.144-1295) (2020-01-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.143-1288...insights-core-3.0.144-1295)

**Implemented enhancements:**

- Update YAMLParser to use libyaml's CSafeLoader if it's available [\#2271](https://github.com/RedHatInsights/insights-core/issues/2271)

**Closed issues:**

- Add version command/flag to the Insights CLI  [\#2408](https://github.com/RedHatInsights/insights-core/issues/2408)
- Should keep the tests for the deprecated parsers SystemctlShow\* [\#2380](https://github.com/RedHatInsights/insights-core/issues/2380)

## [insights-core-3.0.143-1288](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.143-1288) (2020-01-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.142-1286...insights-core-3.0.143-1288)

**Fixed bugs:**

- Add links section to text format [\#2284](https://github.com/RedHatInsights/insights-core/issues/2284)

**Closed issues:**

- Add specs to sos\_archive.py [\#2407](https://github.com/RedHatInsights/insights-core/issues/2407)

## [insights-core-3.0.142-1286](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.142-1286) (2020-01-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.141-1279...insights-core-3.0.142-1286)

**Implemented enhancements:**

- Enhance the cpuinfo parser to fetch 'apicid' information [\#2393](https://github.com/RedHatInsights/insights-core/issues/2393)

**Closed issues:**

- The symbolic of simple\_file for readlink\_e\_etc\_mtab is incorrect [\#2399](https://github.com/RedHatInsights/insights-core/issues/2399)
- \[Package dependency Error: PyYAML\] TypeError: can't compare offset-naive and offset-aware datetimes [\#2397](https://github.com/RedHatInsights/insights-core/issues/2397)
- Add parser for the command "findmnt -lo+PROPAGATION" [\#2368](https://github.com/RedHatInsights/insights-core/issues/2368)

## [insights-core-3.0.141-1279](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.141-1279) (2020-01-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.140-1274...insights-core-3.0.141-1279)

**Implemented enhancements:**

- Enhnace IpLinkInfo parser [\#2389](https://github.com/RedHatInsights/insights-core/issues/2389)

**Closed issues:**

- Update file paths for foreman related specs as per sosreport changes [\#2385](https://github.com/RedHatInsights/insights-core/issues/2385)
- Remove Spec ulimit\_hard [\#2383](https://github.com/RedHatInsights/insights-core/issues/2383)

## [insights-core-3.0.140-1274](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.140-1274) (2019-12-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.139-1...insights-core-3.0.140-1274)

**Fixed bugs:**

- KpatchPatches Documentation and Archive Spec [\#2378](https://github.com/RedHatInsights/insights-core/issues/2378)

## [insights-core-3.0.139-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.139-1) (2019-12-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.138-1271...insights-core-3.0.139-1)

## [insights-core-3.0.138-1271](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.138-1271) (2019-12-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.137-1...insights-core-3.0.138-1271)

**Implemented enhancements:**

- Enhance parser "HammerPing" to keep the original output [\#2375](https://github.com/RedHatInsights/insights-core/issues/2375)

**Closed issues:**

- Fix FreeIPAHealthCheckLog so that Healthcheck 0.3+ logs can be parsed [\#2369](https://github.com/RedHatInsights/insights-core/issues/2369)

## [insights-core-3.0.137-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.137-1) (2019-12-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.136-1256...insights-core-3.0.137-1)

**Fixed bugs:**

- Bug in parser to parse the output of "hammer ping" [\#2358](https://github.com/RedHatInsights/insights-core/issues/2358)

## [insights-core-3.0.136-1256](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.136-1256) (2019-12-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.135-1237...insights-core-3.0.136-1256)

**Implemented enhancements:**

- Enhance IpLinkInfo for vxlan and ovs interfaces [\#2329](https://github.com/RedHatInsights/insights-core/issues/2329)

**Fixed bugs:**

- IP Link Parser archive spec is broken by PR [\#2356](https://github.com/RedHatInsights/insights-core/issues/2356)
- SatelliteEnableFeatures parser specs need to be revised [\#2318](https://github.com/RedHatInsights/insights-core/issues/2318)

**Closed issues:**

- Need a get\_links to return the "links" passed to the "@rule" [\#2361](https://github.com/RedHatInsights/insights-core/issues/2361)
- Double Check satellite\_version.CapsuleVersion Combiner [\#2350](https://github.com/RedHatInsights/insights-core/issues/2350)
- Handle hammer\_ping from sos archive [\#2347](https://github.com/RedHatInsights/insights-core/issues/2347)
- CI/CD failed after upgrading Pygments to 2.5.1 [\#2343](https://github.com/RedHatInsights/insights-core/issues/2343)
- Enhance function parser "ksmstate" to class [\#2337](https://github.com/RedHatInsights/insights-core/issues/2337)
- "systemctl show" on all installed services [\#2078](https://github.com/RedHatInsights/insights-core/issues/2078)

## [insights-core-3.0.135-1237](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.135-1237) (2019-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.134-1...insights-core-3.0.135-1237)

**Closed issues:**

- To improve GlusterVolStatus parser. [\#2232](https://github.com/RedHatInsights/insights-core/issues/2232)

## [insights-core-3.0.134-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.134-1) (2019-11-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.133-1228...insights-core-3.0.134-1)

**Closed issues:**

- Add is\_failed method to systemd.unitfiles.UnitFiles Parser [\#2312](https://github.com/RedHatInsights/insights-core/issues/2312)
- YumRepoList parse issue: \("Incorrect line: '{0}'", 'repolist: 59009'\) [\#2309](https://github.com/RedHatInsights/insights-core/issues/2309)
- SatelliteVersion should be enhanced for Satellite Capsule [\#2305](https://github.com/RedHatInsights/insights-core/issues/2305)
- SCTPAsc raises exception on RHEL7 [\#2303](https://github.com/RedHatInsights/insights-core/issues/2303)

## [insights-core-3.0.133-1228](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.133-1228) (2019-11-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.132-1221...insights-core-3.0.133-1228)

**Closed issues:**

- SatelliteVersion should raise SkipComponent but not return [\#2302](https://github.com/RedHatInsights/insights-core/issues/2302)
- Specs.sssd\_logs is missed in sos\_archive.py [\#2296](https://github.com/RedHatInsights/insights-core/issues/2296)
- Parser Satellite6Version is for Sat 6.1 or older only [\#2295](https://github.com/RedHatInsights/insights-core/issues/2295)
- 'community\_to\_release\_map' in 'ceph\_version.py' parser needs to be updated. [\#2290](https://github.com/RedHatInsights/insights-core/issues/2290)

## [insights-core-3.0.132-1221](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.132-1221) (2019-11-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.131-1215...insights-core-3.0.132-1221)

**Fixed bugs:**

- Blacklist patterns are not being filtered correctly [\#2287](https://github.com/RedHatInsights/insights-core/issues/2287)
- config tree combiner incorrectly detects recursive includes [\#2214](https://github.com/RedHatInsights/insights-core/issues/2214)

**Closed issues:**

- Add openvswitch\_other\_config parser for sosreport [\#2286](https://github.com/RedHatInsights/insights-core/issues/2286)

## [insights-core-3.0.131-1215](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.131-1215) (2019-10-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.130-1209...insights-core-3.0.131-1215)

## [insights-core-3.0.130-1209](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.130-1209) (2019-10-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.129-1195...insights-core-3.0.130-1209)

**Fixed bugs:**

- ListUnits parser incorrectly adds the heading as the first unit [\#2243](https://github.com/RedHatInsights/insights-core/issues/2243)

**Closed issues:**

- The DockerList and DockerInspect should be enhanced [\#2252](https://github.com/RedHatInsights/insights-core/issues/2252)
- New parser for /etc/rhosp-release [\#1763](https://github.com/RedHatInsights/insights-core/issues/1763)

## [insights-core-3.0.129-1195](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.129-1195) (2019-10-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.128-1181...insights-core-3.0.129-1195)

**Implemented enhancements:**

-  exception occurs while parsing the output of `nmcli dev show` [\#2260](https://github.com/RedHatInsights/insights-core/issues/2260)

**Closed issues:**

- Documentation of PodmanList and PodmanInspect needs update [\#2255](https://github.com/RedHatInsights/insights-core/issues/2255)
- Issue with ceph\_version parser while parsing the ceph version. [\#2224](https://github.com/RedHatInsights/insights-core/issues/2224)

## [insights-core-3.0.128-1181](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.128-1181) (2019-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.127-1168...insights-core-3.0.128-1181)

**Closed issues:**

- Better keep the spec `modinfo` compatible with the one in sosreport [\#2220](https://github.com/RedHatInsights/insights-core/issues/2220)
- Need ModInfo Specs for sos\_archive [\#2213](https://github.com/RedHatInsights/insights-core/issues/2213)

## [insights-core-3.0.127-1168](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.127-1168) (2019-10-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.126-1160...insights-core-3.0.127-1168)

## [insights-core-3.0.126-1160](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.126-1160) (2019-09-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.125-1149...insights-core-3.0.126-1160)

**Implemented enhancements:**

- 'VDO statistics: not available' is not covered by vdo\_status parser [\#2209](https://github.com/RedHatInsights/insights-core/issues/2209)

**Fixed bugs:**

- There is special characters in comment in httpd conf files [\#2219](https://github.com/RedHatInsights/insights-core/issues/2219)
- Add "No files found for" to the CommandParser's blacklist [\#2217](https://github.com/RedHatInsights/insights-core/issues/2217)
- Some parsers should succeed or fail atomically [\#2208](https://github.com/RedHatInsights/insights-core/issues/2208)

**Closed issues:**

- html.py has a vulnerable package [\#2228](https://github.com/RedHatInsights/insights-core/issues/2228)
- The HammerTaskList cannot handle cells contain "commas" [\#2211](https://github.com/RedHatInsights/insights-core/issues/2211)
- When using locally defined specs with --bare option run fails [\#2193](https://github.com/RedHatInsights/insights-core/issues/2193)
- Duplicate data stored in Parser/Combiners mixed with dict [\#2122](https://github.com/RedHatInsights/insights-core/issues/2122)

## [insights-core-3.0.125-1149](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.125-1149) (2019-09-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.124-1131...insights-core-3.0.125-1149)

**Fixed bugs:**

- Bug in httpd conf parser  [\#2151](https://github.com/RedHatInsights/insights-core/issues/2151)

**Closed issues:**

- PsAuxww parser doesn't work due to add\_filter\(\) in ps.py [\#2202](https://github.com/RedHatInsights/insights-core/issues/2202)
- Add support to older sosreport of RHEL6.5 and below [\#2196](https://github.com/RedHatInsights/insights-core/issues/2196)
- MountEntry in mount.py store 2 copy of data in both obj.attribute and self.data ways, which may lead to data inconsistency once abuse write operations are applied to it.  [\#2081](https://github.com/RedHatInsights/insights-core/issues/2081)

## [insights-core-3.0.124-1131](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.124-1131) (2019-09-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.123-1125...insights-core-3.0.124-1131)

**Fixed bugs:**

- TextFileProvider fails to read files containing byte chars in Python 3 [\#2163](https://github.com/RedHatInsights/insights-core/issues/2163)

**Closed issues:**

- Can't get the original order of lines in '/etc/hosts' from the current "Hosts" [\#2177](https://github.com/RedHatInsights/insights-core/issues/2177)
- Enhance simple to get single string from datasource [\#2113](https://github.com/RedHatInsights/insights-core/issues/2113)

## [insights-core-3.0.123-1125](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.123-1125) (2019-09-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.122-1117...insights-core-3.0.123-1125)

**Fixed bugs:**

- CephLog should collect multiple files [\#2168](https://github.com/RedHatInsights/insights-core/issues/2168)

**Closed issues:**

- Specs for hostname should be `/bin/hostname` but not `/usr/bin/hostname` [\#2175](https://github.com/RedHatInsights/insights-core/issues/2175)
- No parser for "hostname -I" [\#2173](https://github.com/RedHatInsights/insights-core/issues/2173)
- Request for mpstat parser [\#2144](https://github.com/RedHatInsights/insights-core/issues/2144)

## [insights-core-3.0.122-1117](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.122-1117) (2019-08-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.121-1...insights-core-3.0.122-1117)

**Fixed bugs:**

- lscpu datasource missing for sos reports [\#2150](https://github.com/RedHatInsights/insights-core/issues/2150)

## [insights-core-3.0.121-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.121-1) (2019-08-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.120-1112...insights-core-3.0.121-1)

## [insights-core-3.0.120-1112](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.120-1112) (2019-08-22)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.119-1105...insights-core-3.0.120-1112)

**Fixed bugs:**

- Bug in "yum repolist parser [\#2149](https://github.com/RedHatInsights/insights-core/issues/2149)

**Closed issues:**

- The new `find` does not work as expected [\#2153](https://github.com/RedHatInsights/insights-core/issues/2153)
- Archive Spec is Missing Data Source [\#2147](https://github.com/RedHatInsights/insights-core/issues/2147)

## [insights-core-3.0.119-1105](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.119-1105) (2019-08-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.118-1098...insights-core-3.0.119-1105)

**Closed issues:**

- The SELinux combiner doesn't use grub blscfg for RHEL8 [\#2138](https://github.com/RedHatInsights/insights-core/issues/2138)
- RFE: add a parser for FreeIPA's HealthCheck logs [\#2071](https://github.com/RedHatInsights/insights-core/issues/2071)

## [insights-core-3.0.118-1098](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.118-1098) (2019-08-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.117-1093...insights-core-3.0.118-1098)

## [insights-core-3.0.117-1093](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.117-1093) (2019-08-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.116-1092...insights-core-3.0.117-1093)

**Closed issues:**

- Duplicate data in Partitions [\#2124](https://github.com/RedHatInsights/insights-core/issues/2124)

## [insights-core-3.0.116-1092](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.116-1092) (2019-07-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.115-1...insights-core-3.0.116-1092)

## [3.0.115-1](https://github.com/RedHatInsights/insights-core/tree/3.0.115-1) (2019-07-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.114-1078...3.0.115-1)

## [insights-core-3.0.114-1078](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.114-1078) (2019-07-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.113-1062...insights-core-3.0.114-1078)

**Implemented enhancements:**

- Update the Mount parser and specs depends on '/proc/mounts' [\#2059](https://github.com/RedHatInsights/insights-core/issues/2059)

**Fixed bugs:**

- bash\_version example doesn't work with json format [\#2100](https://github.com/RedHatInsights/insights-core/issues/2100)
- CLI dumps tracebacks instead of simple message [\#2097](https://github.com/RedHatInsights/insights-core/issues/2097)
- Core doesn't detect chkconfig in services directory of sos archives [\#2087](https://github.com/RedHatInsights/insights-core/issues/2087)
- Dmesg combiner always succeeds [\#2084](https://github.com/RedHatInsights/insights-core/issues/2084)
- Modinfo Parser is Missing Insights Archive Spec [\#2053](https://github.com/RedHatInsights/insights-core/issues/2053)
- Systemctl cat needs to retain backward compatibility for archive specs [\#2038](https://github.com/RedHatInsights/insights-core/issues/2038)

**Closed issues:**

- insights.run does not run against sosreport directory if print\_summary=False [\#2107](https://github.com/RedHatInsights/insights-core/issues/2107)
- ProcMounts doesn't handle paths contain spaces, e.g."/run/media/VMware Tools" [\#2069](https://github.com/RedHatInsights/insights-core/issues/2069)
- Issue in installed\_rpms.redhat\_signed when run against sosreport [\#2066](https://github.com/RedHatInsights/insights-core/issues/2066)
- YAMLParser does not handle list-like YAML texts [\#2060](https://github.com/RedHatInsights/insights-core/issues/2060)
- JSONParser does not handle JSON texts consisting of an array [\#2056](https://github.com/RedHatInsights/insights-core/issues/2056)

## [insights-core-3.0.113-1062](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.113-1062) (2019-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.112-1...insights-core-3.0.113-1062)

**Implemented enhancements:**

- Refine the logic of parsers and combiners in "grub\_conf.py" [\#1983](https://github.com/RedHatInsights/insights-core/issues/1983)

**Closed issues:**

- Detect rules with possible duplicate response keys [\#2082](https://github.com/RedHatInsights/insights-core/issues/2082)
- 'grubenv' does not updated as per grubby [\#2041](https://github.com/RedHatInsights/insights-core/issues/2041)
- GRUB2 on RHEL8 - add support for blscfg [\#1650](https://github.com/RedHatInsights/insights-core/issues/1650)

## [3.0.112-1](https://github.com/RedHatInsights/insights-core/tree/3.0.112-1) (2019-07-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.111-1...3.0.112-1)

**Implemented enhancements:**

- Create make\_info response type for rules [\#2073](https://github.com/RedHatInsights/insights-core/issues/2073)
- Evolution of Rules to Share Code [\#1473](https://github.com/RedHatInsights/insights-core/issues/1473)

**Fixed bugs:**

- Fix command specs containing globs [\#1413](https://github.com/RedHatInsights/insights-core/issues/1413)

**Closed issues:**

- Incorrect insights.components.rhel\_version module doc [\#2048](https://github.com/RedHatInsights/insights-core/issues/2048)

## [3.0.111-1](https://github.com/RedHatInsights/insights-core/tree/3.0.111-1) (2019-07-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.110-1...3.0.111-1)

## [3.0.110-1](https://github.com/RedHatInsights/insights-core/tree/3.0.110-1) (2019-07-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.109-1047...3.0.110-1)

**Closed issues:**

- `modinfo` on all loaded modules [\#1793](https://github.com/RedHatInsights/insights-core/issues/1793)
- `DmesgLineList` parser cannot handle wrapped dmesg output [\#1792](https://github.com/RedHatInsights/insights-core/issues/1792)

**Merged pull requests:**

- Update changelog and bump version to 3.0.110 [\#2054](https://github.com/RedHatInsights/insights-core/pull/2054) ([wcmitchell](https://github.com/wcmitchell))

## [insights-core-3.0.109-1047](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.109-1047) (2019-07-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.108-1038...insights-core-3.0.109-1047)

**Implemented enhancements:**

- NmcliConnShow parser fails when there is warning in cmd output [\#2051](https://github.com/RedHatInsights/insights-core/issues/2051)

**Fixed bugs:**

- httpd\_V combiner doesn't treat httpd\_V parser arg as a list [\#1805](https://github.com/RedHatInsights/insights-core/issues/1805)

**Closed issues:**

- Need a parser for 'rabbitmqctl\_report' of containers [\#2049](https://github.com/RedHatInsights/insights-core/issues/2049)

## [insights-core-3.0.108-1038](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.108-1038) (2019-07-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.107-1033...insights-core-3.0.108-1038)

**Fixed bugs:**

- IfCFG parser do not add raw\_device\_value [\#2037](https://github.com/RedHatInsights/insights-core/issues/2037)
- incorrect default\_component\_enabled behavior [\#2034](https://github.com/RedHatInsights/insights-core/issues/2034)
- When em/en dash is mistakenly used for an arg to insights run exception is thrown [\#1832](https://github.com/RedHatInsights/insights-core/issues/1832)

**Closed issues:**

- Add regex support to add\_filter [\#2029](https://github.com/RedHatInsights/insights-core/issues/2029)
- Remove archive creation code [\#1642](https://github.com/RedHatInsights/insights-core/issues/1642)

## [insights-core-3.0.107-1033](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.107-1033) (2019-06-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.106-1020...insights-core-3.0.107-1033)

**Implemented enhancements:**

- Enhance parser qemu\_xml to parse new RHOSP specific attributes [\#1717](https://github.com/RedHatInsights/insights-core/issues/1717)

**Fixed bugs:**

- ModInfoVeth Parser needs spec for Insights Archives [\#2026](https://github.com/RedHatInsights/insights-core/issues/2026)

**Closed issues:**

- NoOptionError using smb.conf parser \(samba.py\) [\#2018](https://github.com/RedHatInsights/insights-core/issues/2018)
- The installed\_rpms spec does work on RHEL6 [\#2015](https://github.com/RedHatInsights/insights-core/issues/2015)
- Critical security issue in dependency pyyaml [\#2013](https://github.com/RedHatInsights/insights-core/issues/2013)
- ModuleNotFoundError: No module named 'insights.config' [\#2009](https://github.com/RedHatInsights/insights-core/issues/2009)
- Missing boilerplate notice in all the files of the project. [\#2003](https://github.com/RedHatInsights/insights-core/issues/2003)
- Markdown formatter needs to show plugin module in output [\#1700](https://github.com/RedHatInsights/insights-core/issues/1700)

## [insights-core-3.0.106-1020](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.106-1020) (2019-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.105-1009...insights-core-3.0.106-1020)

**Closed issues:**

- Change sequence of simple\_file for first\_of Spec for lspci in sos\_archive.py [\#1997](https://github.com/RedHatInsights/insights-core/issues/1997)
- Combiner CloudProvider appears in every "insights-info" [\#1994](https://github.com/RedHatInsights/insights-core/issues/1994)
- Current GrubConf parser cannot handle the "grub2/grub.cfg" of RHEL8 [\#1972](https://github.com/RedHatInsights/insights-core/issues/1972)
- Update is\_hypervisor check in InstalledRpms [\#1928](https://github.com/RedHatInsights/insights-core/issues/1928)
-  Specs.software\_collections\_list: Option `-l` is changed to 'list-collections' in RHEL8 [\#1870](https://github.com/RedHatInsights/insights-core/issues/1870)

## [insights-core-3.0.105-1009](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.105-1009) (2019-06-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.104-1004...insights-core-3.0.105-1009)

## [insights-core-3.0.104-1004](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.104-1004) (2019-06-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.103-995...insights-core-3.0.104-1004)

**Implemented enhancements:**

- Krb5Configuration do not list all the sections [\#1874](https://github.com/RedHatInsights/insights-core/issues/1874)
- Add "reponame" to the rpm query string for InstalledRpms [\#1854](https://github.com/RedHatInsights/insights-core/issues/1854)
- `CpuInfo` parser cannot handle ARM and PowerPC [\#1794](https://github.com/RedHatInsights/insights-core/issues/1794)
- Investigate collecting `/etc/dnf/modules.d` and other dnf related information [\#1648](https://github.com/RedHatInsights/insights-core/issues/1648)

**Fixed bugs:**

- There is a bug in parser "PassengerStatus" [\#1978](https://github.com/RedHatInsights/insights-core/issues/1978)
- Krb5Configuration do not list all the sections [\#1874](https://github.com/RedHatInsights/insights-core/issues/1874)
- FileListing could not check dir with sticky bit shown as 'T' in ls command [\#1121](https://github.com/RedHatInsights/insights-core/issues/1121)

**Closed issues:**

- ModInfo parser should parse octeon\_drv module. [\#1991](https://github.com/RedHatInsights/insights-core/issues/1991)
- setup\_env.sh does not check for the presence of 'virtualenv' [\#1988](https://github.com/RedHatInsights/insights-core/issues/1988)
- Need to enhance the keep\_scan and token\_scan of LogFileOutput [\#1969](https://github.com/RedHatInsights/insights-core/issues/1969)
- \[RFE\] Abrt DUPHASH integration for backtraces [\#1785](https://github.com/RedHatInsights/insights-core/issues/1785)
- Failed to get CephVersion from sosreport archives [\#1684](https://github.com/RedHatInsights/insights-core/issues/1684)

## [insights-core-3.0.103-995](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.103-995) (2019-06-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.102...insights-core-3.0.103-995)

**Closed issues:**

- issue on parsing line endswith "\*" in krb5.py [\#1911](https://github.com/RedHatInsights/insights-core/issues/1911)

## [3.0.102](https://github.com/RedHatInsights/insights-core/tree/3.0.102) (2019-06-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.101-986...3.0.102)

**Implemented enhancements:**

- Filter out wanted system logs according to the process name [\#1919](https://github.com/RedHatInsights/insights-core/issues/1919)
- Enhance @parser to allow additional dependencies [\#1888](https://github.com/RedHatInsights/insights-core/issues/1888)

**Closed issues:**

- Sync specs in sos\_archive.py [\#1950](https://github.com/RedHatInsights/insights-core/issues/1950)

## [insights-core-3.0.101-986](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.101-986) (2019-05-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.100-974...insights-core-3.0.101-986)

**Fixed bugs:**

- "CommandParser does skip the "No module named insights.tools" [\#1955](https://github.com/RedHatInsights/insights-core/issues/1955)
- wrong specs for heat api log  [\#1886](https://github.com/RedHatInsights/insights-core/issues/1886)

**Closed issues:**

- Invoking "insights-inspect" command without colorama installed results in a traceback [\#1956](https://github.com/RedHatInsights/insights-core/issues/1956)
- `SysconfigOptions` base parser does not parse unpaired quoted lines [\#1946](https://github.com/RedHatInsights/insights-core/issues/1946)
- Enhance parser RabbitMQReport  [\#1906](https://github.com/RedHatInsights/insights-core/issues/1906)
- Do we need ceph\_version parser? [\#1764](https://github.com/RedHatInsights/insights-core/issues/1764)
- nginx\_conf collection incomplete? [\#1472](https://github.com/RedHatInsights/insights-core/issues/1472)

## [insights-core-3.0.100-974](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.100-974) (2019-05-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.99-969...insights-core-3.0.100-974)

**Implemented enhancements:**

- New parser for PsAlxww [\#1833](https://github.com/RedHatInsights/insights-core/issues/1833)

**Fixed bugs:**

- Ps class incorrectly parses command name and forces position of "user" and "command" columns. [\#1915](https://github.com/RedHatInsights/insights-core/issues/1915)

## [insights-core-3.0.99-969](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.99-969) (2019-05-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.98-965...insights-core-3.0.99-969)

**Fixed bugs:**

- redhat\_release.RedHatRelease Combiner - Change `ParseException` to `SkipComponent`  [\#1924](https://github.com/RedHatInsights/insights-core/issues/1924)

**Closed issues:**

- get\_max\(package\_name\) returns TypeError for some package lists [\#1839](https://github.com/RedHatInsights/insights-core/issues/1839)
- The default comparison method of InstalledRpm should only for packages from "Red Hat" [\#1836](https://github.com/RedHatInsights/insights-core/issues/1836)

## [insights-core-3.0.98-965](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.98-965) (2019-05-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.97-1...insights-core-3.0.98-965)

**Implemented enhancements:**

- Local routes are filtered in the `RouteDevices` parser [\#1803](https://github.com/RedHatInsights/insights-core/issues/1803)

**Fixed bugs:**

- Directories of exploded archives not recognized as cluster [\#1900](https://github.com/RedHatInsights/insights-core/issues/1900)
- cluster rules execute during non-cluster analysis [\#1896](https://github.com/RedHatInsights/insights-core/issues/1896)

**Closed issues:**

- Collect insights client configuration with blacklist [\#588](https://github.com/RedHatInsights/insights-core/issues/588)
- Remove direct dependency on netstat [\#83](https://github.com/RedHatInsights/insights-core/issues/83)

## [3.0.97-1](https://github.com/RedHatInsights/insights-core/tree/3.0.97-1) (2019-05-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.96-1...3.0.97-1)

**Fixed bugs:**

- Timestamp without space in square brackets doesn't get parsed by dmesg parser [\#1909](https://github.com/RedHatInsights/insights-core/issues/1909)
- Ps aexww parser does not parser all environment vars correctly [\#1857](https://github.com/RedHatInsights/insights-core/issues/1857)
- SshDConfig parser doesn't support "=" key/value separator [\#1807](https://github.com/RedHatInsights/insights-core/issues/1807)

## [3.0.96-1](https://github.com/RedHatInsights/insights-core/tree/3.0.96-1) (2019-05-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.95-1...3.0.96-1)

## [3.0.95-1](https://github.com/RedHatInsights/insights-core/tree/3.0.95-1) (2019-05-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.94-1...3.0.95-1)

## [3.0.94-1](https://github.com/RedHatInsights/insights-core/tree/3.0.94-1) (2019-05-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.93-1...3.0.94-1)

## [3.0.93-1](https://github.com/RedHatInsights/insights-core/tree/3.0.93-1) (2019-05-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.92-937...3.0.93-1)

**Implemented enhancements:**

- Add "display\_name" spec to specs [\#1891](https://github.com/RedHatInsights/insights-core/issues/1891)

## [insights-core-3.0.92-937](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.92-937) (2019-05-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.91-930...insights-core-3.0.92-937)

**Closed issues:**

- Need to enhance parser "ls\_parser" to parse the output of  command 'ls -laRZ \<dir-name\>' in RHEL-8  [\#1825](https://github.com/RedHatInsights/insights-core/issues/1825)

## [insights-core-3.0.91-930](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.91-930) (2019-04-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.90-917...insights-core-3.0.91-930)

**Implemented enhancements:**

- No parser for /sos\_commands/ceph/ceph\_osd\_tree in sosreport  [\#1776](https://github.com/RedHatInsights/insights-core/issues/1776)

**Fixed bugs:**

- Insights Archive spec is Incorrect [\#1856](https://github.com/RedHatInsights/insights-core/issues/1856)

## [insights-core-3.0.90-917](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.90-917) (2019-04-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.89-899...insights-core-3.0.90-917)

**Closed issues:**

- Check of the IGNORE\_TYPES is not correct [\#1818](https://github.com/RedHatInsights/insights-core/issues/1818)

## [insights-core-3.0.89-899](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.89-899) (2019-04-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.88-889...insights-core-3.0.89-899)

**Implemented enhancements:**

- pcs\_config parser returns list instead of dict in "Cluster Properties" [\#1734](https://github.com/RedHatInsights/insights-core/issues/1734)

**Closed issues:**

- insights-run failed in Macbook\(Option --delay-directory-restore is not supported\) [\#1802](https://github.com/RedHatInsights/insights-core/issues/1802)
- python\_-m\_insights.tools.cat reports: "/bin/python: No module named tools" [\#1697](https://github.com/RedHatInsights/insights-core/issues/1697)

## [insights-core-3.0.88-889](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.88-889) (2019-04-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.87-1...insights-core-3.0.88-889)

**Implemented enhancements:**

- Allow different CONTENT for the same key [\#1767](https://github.com/RedHatInsights/insights-core/issues/1767)

**Closed issues:**

- Change spec for netstat parser in sos\_archive.py   [\#1783](https://github.com/RedHatInsights/insights-core/issues/1783)
- insights-client: WARNING: Unknown options: trace [\#1702](https://github.com/RedHatInsights/insights-core/issues/1702)

## [3.0.87-1](https://github.com/RedHatInsights/insights-core/tree/3.0.87-1) (2019-03-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.86-877...3.0.87-1)

**Closed issues:**

- Ceilometer Collector Log specs needs to be first\_file [\#1772](https://github.com/RedHatInsights/insights-core/issues/1772)

## [insights-core-3.0.86-877](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.86-877) (2019-03-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.85-868...insights-core-3.0.86-877)

## [insights-core-3.0.85-868](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.85-868) (2019-03-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.84-864...insights-core-3.0.85-868)

**Fixed bugs:**

- FileListing parser does not correctly handle directory path with dot [\#1748](https://github.com/RedHatInsights/insights-core/issues/1748)

## [insights-core-3.0.84-864](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.84-864) (2019-03-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.83-1...insights-core-3.0.84-864)

## [3.0.83-1](https://github.com/RedHatInsights/insights-core/tree/3.0.83-1) (2019-03-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.82-858...3.0.83-1)

**Fixed bugs:**

- Enhance multipath conf parser to parse multiple entries [\#1722](https://github.com/RedHatInsights/insights-core/issues/1722)

## [insights-core-3.0.82-858](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.82-858) (2019-03-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.81-848...insights-core-3.0.82-858)

**Implemented enhancements:**

- Set LC\_ALL=C for all commands [\#1623](https://github.com/RedHatInsights/insights-core/issues/1623)

**Fixed bugs:**

- parse\_fixed\_table header prefix bug [\#1737](https://github.com/RedHatInsights/insights-core/issues/1737)

**Closed issues:**

- SMDA\* is not business SAP instances [\#1740](https://github.com/RedHatInsights/insights-core/issues/1740)

## [insights-core-3.0.81-848](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.81-848) (2019-03-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.80-833...insights-core-3.0.81-848)

**Implemented enhancements:**

- Add filterable option to IronicInspectorLog [\#1718](https://github.com/RedHatInsights/insights-core/issues/1718)

**Fixed bugs:**

- exceptions logged at warn level when calling get\_canonical\_facts [\#1726](https://github.com/RedHatInsights/insights-core/issues/1726)
- subscription manager identity datasource raises exception [\#1674](https://github.com/RedHatInsights/insights-core/issues/1674)

**Closed issues:**

- Enhance the "Examples" of LogFileOutput and Syslog [\#1724](https://github.com/RedHatInsights/insights-core/issues/1724)
- Add filtering to the result of insights-run [\#1687](https://github.com/RedHatInsights/insights-core/issues/1687)
- Output of "insights-info" is not so accurate [\#1645](https://github.com/RedHatInsights/insights-core/issues/1645)
- A utility interface to `redhat\_release` to check/get RHEL version [\#1644](https://github.com/RedHatInsights/insights-core/issues/1644)

## [insights-core-3.0.80-833](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.80-833) (2019-02-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.79-822...insights-core-3.0.80-833)

**Closed issues:**

- insights/util/subproc.py", line 100: An unexpected keyword argument 'STDOUT' [\#1712](https://github.com/RedHatInsights/insights-core/issues/1712)

## [insights-core-3.0.79-822](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.79-822) (2019-02-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.78-807...insights-core-3.0.79-822)

**Closed issues:**

- LogFileOutput.token\_scan does not support `list` [\#1688](https://github.com/RedHatInsights/insights-core/issues/1688)
- TarExtractor doesn’t work on macOS [\#1686](https://github.com/RedHatInsights/insights-core/issues/1686)

## [insights-core-3.0.78-807](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.78-807) (2019-02-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.77-804...insights-core-3.0.78-807)

## [insights-core-3.0.77-804](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.77-804) (2019-02-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.76-795...insights-core-3.0.77-804)

**Closed issues:**

- password blanking broken on RHEL8 [\#1670](https://github.com/RedHatInsights/insights-core/issues/1670)

## [insights-core-3.0.76-795](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.76-795) (2019-01-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.75-1...insights-core-3.0.76-795)

## [3.0.75-1](https://github.com/RedHatInsights/insights-core/tree/3.0.75-1) (2019-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.74-778...3.0.75-1)

**Fixed bugs:**

- streaming bug with python3.7 [\#1652](https://github.com/RedHatInsights/insights-core/issues/1652)

**Closed issues:**

- Modinfo Parser class should be in Parsers instead of the Package spec [\#1659](https://github.com/RedHatInsights/insights-core/issues/1659)

## [insights-core-3.0.74-778](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.74-778) (2019-01-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.73-767...insights-core-3.0.74-778)

**Fixed bugs:**

- RedhatRelease parser failed to parse minor release version in some scenarios [\#1590](https://github.com/RedHatInsights/insights-core/issues/1590)
- Exceptions on the command line with invalid arguments in the archive position [\#1486](https://github.com/RedHatInsights/insights-core/issues/1486)

**Closed issues:**

- Parse\_error TOP1: mysqladmin.py: Empty or wrong content in table [\#1637](https://github.com/RedHatInsights/insights-core/issues/1637)
- Typo in quickstart documentation [\#1635](https://github.com/RedHatInsights/insights-core/issues/1635)

## [insights-core-3.0.73-767](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.73-767) (2019-01-17)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.72-1...insights-core-3.0.73-767)

**Closed issues:**

- ifcfg parser to support for MASTER and TEAM\_MASTER keys slave type [\#1626](https://github.com/RedHatInsights/insights-core/issues/1626)

## [3.0.72-1](https://github.com/RedHatInsights/insights-core/tree/3.0.72-1) (2019-01-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.71-1...3.0.72-1)

## [3.0.71-1](https://github.com/RedHatInsights/insights-core/tree/3.0.71-1) (2019-01-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.70-754...3.0.71-1)

## [insights-core-3.0.70-754](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.70-754) (2018-12-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.69-744...insights-core-3.0.70-754)

## [insights-core-3.0.69-744](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.69-744) (2018-12-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.68-1...insights-core-3.0.69-744)

**Closed issues:**

- DeprecationWarning from qemu\_xml [\#1594](https://github.com/RedHatInsights/insights-core/issues/1594)

## [3.0.68-1](https://github.com/RedHatInsights/insights-core/tree/3.0.68-1) (2018-12-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.67-732...3.0.68-1)

## [insights-core-3.0.67-732](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.67-732) (2018-12-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.66-1...insights-core-3.0.67-732)

## [3.0.66-1](https://github.com/RedHatInsights/insights-core/tree/3.0.66-1) (2018-12-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.64-717...3.0.66-1)

## [insights-core-3.0.64-717](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.64-717) (2018-11-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.63-708...insights-core-3.0.64-717)

## [insights-core-3.0.63-708](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.63-708) (2018-11-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.62-686...insights-core-3.0.63-708)

**Implemented enhancements:**

- Unnecessary Exception raised [\#1564](https://github.com/RedHatInsights/insights-core/issues/1564)

**Fixed bugs:**

- Invalid datasource for ceph\_conf [\#1570](https://github.com/RedHatInsights/insights-core/issues/1570)

**Closed issues:**

- bond object do not have \_active\_slave attribute exception issue [\#1563](https://github.com/RedHatInsights/insights-core/issues/1563)
- Unsuitable parse error in `Lssap` [\#1559](https://github.com/RedHatInsights/insights-core/issues/1559)

## [insights-core-3.0.62-686](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.62-686) (2018-11-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.61-682...insights-core-3.0.62-686)

**Closed issues:**

- Mention unsupported docs building on Python 2.6 [\#1391](https://github.com/RedHatInsights/insights-core/issues/1391)

## [insights-core-3.0.61-682](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.61-682) (2018-11-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.60-680...insights-core-3.0.61-682)

## [insights-core-3.0.60-680](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.60-680) (2018-11-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.59-1...insights-core-3.0.60-680)

## [3.0.59-1](https://github.com/RedHatInsights/insights-core/tree/3.0.59-1) (2018-11-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.58-1...3.0.59-1)

**Fixed bugs:**

- Add xfs\_info datasource to default.py [\#1303](https://github.com/RedHatInsights/insights-core/issues/1303)

**Closed issues:**

- InstalledRpm.from\_package doesn't support 'epoch' correctly [\#1544](https://github.com/RedHatInsights/insights-core/issues/1544)

## [3.0.58-1](https://github.com/RedHatInsights/insights-core/tree/3.0.58-1) (2018-11-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.57-663...3.0.58-1)

**Closed issues:**

- Working without parsers [\#1518](https://github.com/RedHatInsights/insights-core/issues/1518)

## [insights-core-3.0.57-663](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.57-663) (2018-11-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.56-653...insights-core-3.0.57-663)

**Implemented enhancements:**

- Some sos reports include JBoss Diagnostic Report contents [\#1511](https://github.com/RedHatInsights/insights-core/issues/1511)

**Fixed bugs:**

- FileListing parser does not handle filenames with newlines in the name [\#1527](https://github.com/RedHatInsights/insights-core/issues/1527)
- FileListing class has selinux arg that is not used [\#1492](https://github.com/RedHatInsights/insights-core/issues/1492)
- render is called even when rule has missing requirements [\#1489](https://github.com/RedHatInsights/insights-core/issues/1489)

**Closed issues:**

- Ensure current working directory is on the python path with insights-run [\#1523](https://github.com/RedHatInsights/insights-core/issues/1523)
- \[RFE\] Results to include positive NACK - CVEs to which a system is NOT vulnerable [\#1510](https://github.com/RedHatInsights/insights-core/issues/1510)
- `list.sort\(\)` doesn't work as expected in python3 [\#1496](https://github.com/RedHatInsights/insights-core/issues/1496)

## [insights-core-3.0.56-653](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.56-653) (2018-11-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.55-1...insights-core-3.0.56-653)

**Implemented enhancements:**

- rules without CONTENT produce hard to interpret reports [\#1480](https://github.com/RedHatInsights/insights-core/issues/1480)

**Fixed bugs:**

- The human readable rule report includes rules with missing requirements [\#1479](https://github.com/RedHatInsights/insights-core/issues/1479)

## [3.0.55-1](https://github.com/RedHatInsights/insights-core/tree/3.0.55-1) (2018-10-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.54-643...3.0.55-1)

**Closed issues:**

- fix wrong passenger\_status part in insights/specs/insights\_archive.py  [\#1508](https://github.com/RedHatInsights/insights-core/issues/1508)
- \[python3\] `unordered\_compare` does support comparing list with dictionaries [\#1494](https://github.com/RedHatInsights/insights-core/issues/1494)

## [insights-core-3.0.54-643](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.54-643) (2018-10-25)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.52-1...insights-core-3.0.54-643)

**Fixed bugs:**

- configtree include directives only work from top level [\#1477](https://github.com/RedHatInsights/insights-core/issues/1477)

**Closed issues:**

- installed\_rpms missing EPOCH [\#1431](https://github.com/RedHatInsights/insights-core/issues/1431)

## [3.0.52-1](https://github.com/RedHatInsights/insights-core/tree/3.0.52-1) (2018-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.51-623...3.0.52-1)

**Fixed bugs:**

- Issue to collect insights-archive in RHEL6 [\#1461](https://github.com/RedHatInsights/insights-core/issues/1461)

**Closed issues:**

- Add 'to\_serializable\(\)' function to 'InputData' object [\#1421](https://github.com/RedHatInsights/insights-core/issues/1421)

## [insights-core-3.0.51-623](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.51-623) (2018-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.50-1...insights-core-3.0.51-623)

## [3.0.50-1](https://github.com/RedHatInsights/insights-core/tree/3.0.50-1) (2018-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.49-615...3.0.50-1)

**Fixed bugs:**

- Mistake to recognize collected files as missing requirements [\#1466](https://github.com/RedHatInsights/insights-core/issues/1466)

## [insights-core-3.0.49-615](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.49-615) (2018-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.48-1...insights-core-3.0.49-615)

**Closed issues:**

- Run Flake8 lint on RHEL6 [\#1262](https://github.com/RedHatInsights/insights-core/issues/1262)

## [3.0.48-1](https://github.com/RedHatInsights/insights-core/tree/3.0.48-1) (2018-10-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.47-1...3.0.48-1)

**Fixed bugs:**

- Tar files aren't handled [\#1457](https://github.com/RedHatInsights/insights-core/issues/1457)

**Closed issues:**

- Incorrect configuration file paths for specs related to OpenStack [\#1441](https://github.com/RedHatInsights/insights-core/issues/1441)

## [3.0.47-1](https://github.com/RedHatInsights/insights-core/tree/3.0.47-1) (2018-09-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.46-605...3.0.47-1)

## [insights-core-3.0.46-605](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.46-605) (2018-09-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.45-594...insights-core-3.0.46-605)

## [insights-core-3.0.45-594](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.45-594) (2018-09-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.44-586...insights-core-3.0.45-594)

**Closed issues:**

- utf-8 UnicodeDecodeError in 'var/log/messages' parsing [\#1432](https://github.com/RedHatInsights/insights-core/issues/1432)

## [insights-core-3.0.44-586](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.44-586) (2018-09-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.43-576...insights-core-3.0.44-586)

**Closed issues:**

- No parser for getting number of cpu cores [\#1422](https://github.com/RedHatInsights/insights-core/issues/1422)

## [insights-core-3.0.43-576](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.43-576) (2018-09-05)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.42-564...insights-core-3.0.43-576)

## [insights-core-3.0.42-564](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.42-564) (2018-08-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.41-1...insights-core-3.0.42-564)

**Fixed bugs:**

- getsebool parser "need more than 1 value to unpack" [\#1394](https://github.com/RedHatInsights/insights-core/issues/1394)
- Unicode Warning in Python 2.7 for unitfiles module [\#1366](https://github.com/RedHatInsights/insights-core/issues/1366)

**Closed issues:**

- Need to patch machine-id in the test\_set\_display\_name [\#1407](https://github.com/RedHatInsights/insights-core/issues/1407)
- Split setuptools develop extras bundle [\#1261](https://github.com/RedHatInsights/insights-core/issues/1261)

## [3.0.41-1](https://github.com/RedHatInsights/insights-core/tree/3.0.41-1) (2018-08-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.40-1...3.0.41-1)

## [3.0.40-1](https://github.com/RedHatInsights/insights-core/tree/3.0.40-1) (2018-08-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.39-545...3.0.40-1)

**Fixed bugs:**

- Initialize release in evaluators.py [\#1383](https://github.com/RedHatInsights/insights-core/issues/1383)
- The rule component type overrides invoke but should override process [\#1376](https://github.com/RedHatInsights/insights-core/issues/1376)

**Closed issues:**

- Client Test Attempts to  Removes non-user Insights App File [\#1380](https://github.com/RedHatInsights/insights-core/issues/1380)

## [insights-core-3.0.39-545](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.39-545) (2018-08-22)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.38-534...insights-core-3.0.39-545)

**Closed issues:**

- Do not install docs tools on Python 2.6 [\#1387](https://github.com/RedHatInsights/insights-core/issues/1387)
- Limit Sphinx version to 1.6.7 [\#1385](https://github.com/RedHatInsights/insights-core/issues/1385)

## [insights-core-3.0.38-534](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.38-534) (2018-08-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.37-525...insights-core-3.0.38-534)

**Closed issues:**

- Spec for docker\_ps [\#1347](https://github.com/RedHatInsights/insights-core/issues/1347)

## [insights-core-3.0.37-525](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.37-525) (2018-08-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.36-512...insights-core-3.0.37-525)

**Implemented enhancements:**

- Add threshold for grep vs in-process filtering [\#1099](https://github.com/RedHatInsights/insights-core/issues/1099)
- Insights core tests should use Insights Demo Plugins repository as a test bed [\#1009](https://github.com/RedHatInsights/insights-core/issues/1009)
- Evaluate including psutil with Insights [\#689](https://github.com/RedHatInsights/insights-core/issues/689)
- Parser tests should be able to pass files by path rather than context\_wrap [\#413](https://github.com/RedHatInsights/insights-core/issues/413)

**Fixed bugs:**

- Specs with precommands that are not at the end don't work [\#664](https://github.com/RedHatInsights/insights-core/issues/664)
- Specs may work differently when extracting from an archive vs in the Insights client. [\#594](https://github.com/RedHatInsights/insights-core/issues/594)

**Closed issues:**

- Python 3 Issue in Client  [\#1322](https://github.com/RedHatInsights/insights-core/issues/1322)
- Research options around customer notifications for updated uploader.json/egg [\#774](https://github.com/RedHatInsights/insights-core/issues/774)
- Need to document how Specs work and how to test them [\#662](https://github.com/RedHatInsights/insights-core/issues/662)
- Content for Custom Rules [\#293](https://github.com/RedHatInsights/insights-core/issues/293)
- include and run custom rules during data collection on individual hosts [\#289](https://github.com/RedHatInsights/insights-core/issues/289)
- Improve the examples in lvm.py [\#287](https://github.com/RedHatInsights/insights-core/issues/287)
- SysctlConfInitramfs should be a Scannable, not a LogFileOutput [\#210](https://github.com/RedHatInsights/insights-core/issues/210)

## [insights-core-3.0.36-512](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.36-512) (2018-08-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.36-511...insights-core-3.0.36-512)

## [insights-core-3.0.36-511](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.36-511) (2018-08-09)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.35-1...insights-core-3.0.36-511)

## [3.0.35-1](https://github.com/RedHatInsights/insights-core/tree/3.0.35-1) (2018-08-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.34-1...3.0.35-1)

**Closed issues:**

- Consistent size constraints on make\_metadata\_key cause a plugin to fail [\#1329](https://github.com/RedHatInsights/insights-core/issues/1329)
- `add\_filter` is completely undocumented [\#927](https://github.com/RedHatInsights/insights-core/issues/927)

## [3.0.34-1](https://github.com/RedHatInsights/insights-core/tree/3.0.34-1) (2018-08-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0.33-1...3.0.34-1)

**Closed issues:**

- Check if a archive is from container or host [\#1291](https://github.com/RedHatInsights/insights-core/issues/1291)

## [3.0.33-1](https://github.com/RedHatInsights/insights-core/tree/3.0.33-1) (2018-08-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.32-494...3.0.33-1)

## [insights-core-3.0.32-494](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.32-494) (2018-08-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.31-466...insights-core-3.0.32-494)

**Implemented enhancements:**

- No JSON object could be decoded [\#996](https://github.com/RedHatInsights/insights-core/issues/996)
- Filter only when collecting on host? [\#981](https://github.com/RedHatInsights/insights-core/issues/981)
- Enable filtering and copying of large files outside the python process [\#949](https://github.com/RedHatInsights/insights-core/issues/949)

**Fixed bugs:**

- FileListing Parser does not return total for a single directory listing [\#1306](https://github.com/RedHatInsights/insights-core/issues/1306)
- Quotes and doublequotes break configtree parser [\#1300](https://github.com/RedHatInsights/insights-core/issues/1300)
- Add xfs\_info spec to default and sos\_archive [\#1117](https://github.com/RedHatInsights/insights-core/issues/1117)
- Better handling of files containing failed command output [\#1076](https://github.com/RedHatInsights/insights-core/issues/1076)
- parse\_systemd\_ini relies on implementation details of ConfigParser [\#324](https://github.com/RedHatInsights/insights-core/issues/324)

**Closed issues:**

- About the parser 'pcs\_status', the spec of it does include the full correct file path [\#1315](https://github.com/RedHatInsights/insights-core/issues/1315)
- Key error in spec.httpd\_conf [\#1308](https://github.com/RedHatInsights/insights-core/issues/1308)
- InstalledRpm parser not working [\#1299](https://github.com/RedHatInsights/insights-core/issues/1299)
- httpd\_conf parser creating list of objects [\#1288](https://github.com/RedHatInsights/insights-core/issues/1288)
- dirsrv\_access and dirsrv\_errors will never collect [\#891](https://github.com/RedHatInsights/insights-core/issues/891)

## [insights-core-3.0.31-466](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.31-466) (2018-07-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.30-462...insights-core-3.0.31-466)

## [insights-core-3.0.30-462](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.30-462) (2018-07-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.29-455...insights-core-3.0.30-462)

**Fixed bugs:**

- Wrong comparison method is used in get\_localport and get\_peerport of SsTULPN parser   [\#1281](https://github.com/RedHatInsights/insights-core/issues/1281)
- insights hang when extract jdr archive [\#1272](https://github.com/RedHatInsights/insights-core/issues/1272)
- Dead loop in Mount.get\_dir\(\) when no '/' in mount output [\#1245](https://github.com/RedHatInsights/insights-core/issues/1245)
- Commands return bytes instead of unicode [\#1181](https://github.com/RedHatInsights/insights-core/issues/1181)
- Hostname parser doesn't raise exception on invalid data [\#1113](https://github.com/RedHatInsights/insights-core/issues/1113)

**Closed issues:**

- Enhance parser mysqladmin [\#1242](https://github.com/RedHatInsights/insights-core/issues/1242)
- Failing tests in master [\#1231](https://github.com/RedHatInsights/insights-core/issues/1231)
- Issue with simple\_command data source in spec\_factory [\#1228](https://github.com/RedHatInsights/insights-core/issues/1228)
- No spec for docker\_image\_inspect and docker\_container\_inspect [\#1197](https://github.com/RedHatInsights/insights-core/issues/1197)
- There are unnecessary secondary specs in DefaultSpecs [\#1186](https://github.com/RedHatInsights/insights-core/issues/1186)
- Missing dependencies in README [\#1164](https://github.com/RedHatInsights/insights-core/issues/1164)

## [insights-core-3.0.29-455](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.29-455) (2018-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.28...insights-core-3.0.29-455)

## [insights-core-3.0.28](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.28) (2018-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.27-441...insights-core-3.0.28)

## [insights-core-3.0.27-441](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.27-441) (2018-07-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.26-436...insights-core-3.0.27-441)

## [insights-core-3.0.26-436](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.26-436) (2018-07-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.25-430...insights-core-3.0.26-436)

**Closed issues:**

- insights.utils.fs.ensure\_path is not setting requested mode on dirs [\#1238](https://github.com/RedHatInsights/insights-core/issues/1238)

## [insights-core-3.0.25-430](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.25-430) (2018-06-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.24-426...insights-core-3.0.25-430)

## [insights-core-3.0.24-426](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.24-426) (2018-06-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.22-410...insights-core-3.0.24-426)

**Closed issues:**

- path of ls\_osroot need to be fix [\#1221](https://github.com/RedHatInsights/insights-core/issues/1221)

## [insights-core-3.0.22-410](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.22-410) (2018-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.21-398...insights-core-3.0.22-410)

**Implemented enhancements:**

- Performance Degradation Processing Archives [\#1098](https://github.com/RedHatInsights/insights-core/issues/1098)

**Fixed bugs:**

- HttpdV combiner with 1.x interface [\#1206](https://github.com/RedHatInsights/insights-core/issues/1206)
- Performance Degradation Processing Archives [\#1098](https://github.com/RedHatInsights/insights-core/issues/1098)

**Closed issues:**

- FileListing cannot get the `first\_path` of `ls\_osroot` [\#1203](https://github.com/RedHatInsights/insights-core/issues/1203)
- FIX wrong command in parser systemctl\_show\_qdrouterd [\#1198](https://github.com/RedHatInsights/insights-core/issues/1198)

## [insights-core-3.0.21-398](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.21-398) (2018-06-14)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.20-390...insights-core-3.0.21-398)

**Fixed bugs:**

- ps parser depends on implementation details of cpython [\#959](https://github.com/RedHatInsights/insights-core/issues/959)
- ip parser depends on implementation specific details of cpython [\#958](https://github.com/RedHatInsights/insights-core/issues/958)
- netstat combiner depends on implementation details of cpython [\#957](https://github.com/RedHatInsights/insights-core/issues/957)
- httpd\_conf combiner depends on implementation details of python2 [\#956](https://github.com/RedHatInsights/insights-core/issues/956)
- RPM Comparisons via `InstalledRPM` rely on naive `LooseVersion` comparisons [\#952](https://github.com/RedHatInsights/insights-core/issues/952)

## [insights-core-3.0.20-390](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.20-390) (2018-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.19-380...insights-core-3.0.20-390)

**Merged pull requests:**

- httpd conf combiner new test [\#1191](https://github.com/RedHatInsights/insights-core/pull/1191) ([jsvob](https://github.com/jsvob))

## [insights-core-3.0.19-380](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.19-380) (2018-05-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.18-371...insights-core-3.0.19-380)

**Closed issues:**

- Make GrubConf combiner to get the valid grub. [\#987](https://github.com/RedHatInsights/insights-core/issues/987)

## [insights-core-3.0.18-371](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.18-371) (2018-05-24)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.17-362...insights-core-3.0.18-371)

**Fixed bugs:**

- httpd\_conf parser and combiner cannot handle directives in nest and parallel sections correct [\#1175](https://github.com/RedHatInsights/insights-core/issues/1175)

## [insights-core-3.0.17-362](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.17-362) (2018-05-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.16-355...insights-core-3.0.17-362)

**Closed issues:**

- Test of prodsec rules \(NFS\) are broken [\#1104](https://github.com/RedHatInsights/insights-core/issues/1104)

## [insights-core-3.0.16-355](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.16-355) (2018-05-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.15-350...insights-core-3.0.16-355)

## [insights-core-3.0.15-350](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.15-350) (2018-05-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.14-345...insights-core-3.0.15-350)

## [insights-core-3.0.14-345](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.14-345) (2018-05-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.13-338...insights-core-3.0.14-345)

**Implemented enhancements:**

- Use consistent heading and class style for parser catalogue [\#132](https://github.com/RedHatInsights/insights-core/issues/132)
- Create log transaction-id for log messages associated with a single transaction. [\#126](https://github.com/RedHatInsights/insights-core/issues/126)

**Fixed bugs:**

- A bug caused by typo in parser meminfo [\#1151](https://github.com/RedHatInsights/insights-core/issues/1151)
- fstab parser: parsing broken with ValueError [\#1126](https://github.com/RedHatInsights/insights-core/issues/1126)

**Closed issues:**

- Remove reminder comments after fixed mount-point-space issue from fstab's test [\#1157](https://github.com/RedHatInsights/insights-core/issues/1157)
- Add sos\_commands path entry into sos\_archive.py specs file. [\#1141](https://github.com/RedHatInsights/insights-core/issues/1141)
- LsPci needs to be anything but a LogFileOutput class [\#176](https://github.com/RedHatInsights/insights-core/issues/176)
- Asserts should be try/except in Prod [\#113](https://github.com/RedHatInsights/insights-core/issues/113)

## [insights-core-3.0.13-338](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.13-338) (2018-05-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.12-335...insights-core-3.0.13-338)

## [insights-core-3.0.12-335](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.12-335) (2018-05-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.11-322...insights-core-3.0.12-335)

## [insights-core-3.0.11-322](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.11-322) (2018-04-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.10-317...insights-core-3.0.11-322)

## [insights-core-3.0.10-317](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.10-317) (2018-04-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.9-309...insights-core-3.0.10-317)

**Fixed bugs:**

- Archives are wrong, extraneous top level files \(BZ1561015\) [\#1042](https://github.com/RedHatInsights/insights-core/issues/1042)

**Closed issues:**

- `obfuscate\_hostname` should require `obfuscate` \(BZ1554999\) [\#1016](https://github.com/RedHatInsights/insights-core/issues/1016)

## [insights-core-3.0.9-309](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.9-309) (2018-04-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.8-295...insights-core-3.0.9-309)

**Fixed bugs:**

- Add pcs\_status to sos\_archive.py [\#1082](https://github.com/RedHatInsights/insights-core/issues/1082)
- foreman production log needed for sos archives [\#1060](https://github.com/RedHatInsights/insights-core/issues/1060)
- hostname parser doesn't handle sos\_commands/general/hostname [\#1055](https://github.com/RedHatInsights/insights-core/issues/1055)

## [insights-core-3.0.8-295](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.8-295) (2018-04-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.4-3...insights-core-3.0.8-295)

**Fixed bugs:**

- ssh.py: ValueError: need more than 1 value to unpack  [\#1034](https://github.com/RedHatInsights/insights-core/issues/1034)

**Closed issues:**

- \[ls\_etc\] Test can be merged into docstring [\#1079](https://github.com/RedHatInsights/insights-core/issues/1079)

## [insights-core-3.0.4-3](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.4-3) (2018-04-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.7-270...insights-core-3.0.4-3)

**Fixed bugs:**

- SubscriptionManagerListInstalled should depend on Specs.subscription\_manager\_list\_installed [\#1047](https://github.com/RedHatInsights/insights-core/issues/1047)

**Closed issues:**

- Shippable fails with nbsphinx version 0.3.2 [\#1054](https://github.com/RedHatInsights/insights-core/issues/1054)

## [insights-core-3.0.7-270](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.7-270) (2018-03-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-261...insights-core-3.0.7-270)

**Closed issues:**

- . [\#1044](https://github.com/RedHatInsights/insights-core/issues/1044)

## [insights-core-3.0.6-261](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.6-261) (2018-03-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.6-257...insights-core-3.0.6-261)

## [insights-core-3.0.6-257](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.6-257) (2018-03-16)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.75.0-245...insights-core-3.0.6-257)

**Fixed bugs:**

- WARNING:insights.tests:Replacing ps\_auxcww in --appdebug output [\#1007](https://github.com/RedHatInsights/insights-core/issues/1007)
- Parser error in lsblk.py [\#790](https://github.com/RedHatInsights/insights-core/issues/790)
- Parser error in scsi.py [\#789](https://github.com/RedHatInsights/insights-core/issues/789)
- Parser error in fstab.py [\#788](https://github.com/RedHatInsights/insights-core/issues/788)
- Parser error in lssap.py [\#787](https://github.com/RedHatInsights/insights-core/issues/787)
- Parser error in lvm.py [\#784](https://github.com/RedHatInsights/insights-core/issues/784)
- Parser error in ntp\_sources.py [\#783](https://github.com/RedHatInsights/insights-core/issues/783)
- Parser error in dockerinfo.py [\#782](https://github.com/RedHatInsights/insights-core/issues/782)
- Parser error in ssh.py [\#781](https://github.com/RedHatInsights/insights-core/issues/781)
- Parser error in LsPci in lspci.py [\#780](https://github.com/RedHatInsights/insights-core/issues/780)
- Parser error in iptables.py [\#779](https://github.com/RedHatInsights/insights-core/issues/779)
- Parser error in netstat.py [\#778](https://github.com/RedHatInsights/insights-core/issues/778)
- Error in parser `fstab.py` [\#682](https://github.com/RedHatInsights/insights-core/issues/682)
- Error in combiner `lvm.py` [\#681](https://github.com/RedHatInsights/insights-core/issues/681)
- Possible parser error in `rabbitmq.py` [\#680](https://github.com/RedHatInsights/insights-core/issues/680)
- Another parser error in `iptables.py` [\#678](https://github.com/RedHatInsights/insights-core/issues/678)
- Parser error in `ntp\_sources.py` [\#677](https://github.com/RedHatInsights/insights-core/issues/677)
- Parser error in `ssh.py` [\#676](https://github.com/RedHatInsights/insights-core/issues/676)
- Error in parser `iptables.py` [\#675](https://github.com/RedHatInsights/insights-core/issues/675)
- Parser error in `blkid.py` [\#674](https://github.com/RedHatInsights/insights-core/issues/674)
- Parser error in `netstat.py` [\#673](https://github.com/RedHatInsights/insights-core/issues/673)

**Closed issues:**

- Should Docker Commands run in HostContext? [\#997](https://github.com/RedHatInsights/insights-core/issues/997)
- Collect specs that aren't used by a rule [\#654](https://github.com/RedHatInsights/insights-core/issues/654)
- Sync new style specs with old specs [\#598](https://github.com/RedHatInsights/insights-core/issues/598)

## [insights-core-1.75.0-245](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.75.0-245) (2018-03-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.74.0-241...insights-core-1.75.0-245)

**Implemented enhancements:**

- Cache Graph Run Order [\#974](https://github.com/RedHatInsights/insights-core/issues/974)
- Ability to enable and disable arbitrary components [\#969](https://github.com/RedHatInsights/insights-core/issues/969)
- Command parsers to be based on a CommandParser class [\#898](https://github.com/RedHatInsights/insights-core/issues/898)

**Fixed bugs:**

- Engine should parse all specs associated with an All SpecGroup [\#807](https://github.com/RedHatInsights/insights-core/issues/807)

**Closed issues:**

- Design and develop client runtime API [\#9](https://github.com/RedHatInsights/insights-core/issues/9)

## [insights-core-1.74.0-241](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.74.0-241) (2018-03-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.73.0-236...insights-core-1.74.0-241)

**Fixed bugs:**

- Invalid Subscription Manager specs [\#972](https://github.com/RedHatInsights/insights-core/issues/972)

**Closed issues:**

- Add check for brctl "No such file or directory" [\#988](https://github.com/RedHatInsights/insights-core/issues/988)
- Add parsers LvsAll, PvsAll, VgsAll and combiner LvmAll for getting LVM information for all accepted and rejected devices. \#908 [\#980](https://github.com/RedHatInsights/insights-core/issues/980)
- Install instructions do not work on RHEL 7 [\#911](https://github.com/RedHatInsights/insights-core/issues/911)
- Spec for command `modinfo` : remove OR enhance ? [\#730](https://github.com/RedHatInsights/insights-core/issues/730)

## [insights-core-1.73.0-236](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.73.0-236) (2018-02-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.72.0-224...insights-core-1.73.0-236)

**Implemented enhancements:**

- Refactor insights/specs\_\*.py files into a specs package [\#948](https://github.com/RedHatInsights/insights-core/issues/948)
- `FileListing` ignores `ls` listings that don't contain the name of the directory. [\#827](https://github.com/RedHatInsights/insights-core/issues/827)
- Update 3.x specs to handle 1.x archives [\#809](https://github.com/RedHatInsights/insights-core/issues/809)
- Insights test connection cleanup [\#708](https://github.com/RedHatInsights/insights-core/issues/708)
- Stacked Decorators are Bad [\#14](https://github.com/RedHatInsights/insights-core/issues/14)

**Fixed bugs:**

- Parser error in cluster\_conf.py [\#785](https://github.com/RedHatInsights/insights-core/issues/785)
- Parser error in `cluster\_conf.py` [\#679](https://github.com/RedHatInsights/insights-core/issues/679)
- Parser error in `check\_iptableds\_pid` [\#671](https://github.com/RedHatInsights/insights-core/issues/671)

**Closed issues:**

- Parser nmcli dev show 3.x [\#973](https://github.com/RedHatInsights/insights-core/issues/973)
- Separate specs required for Insights from those required for other archives [\#815](https://github.com/RedHatInsights/insights-core/issues/815)
- Remove 1.x spec handling from 3.x [\#808](https://github.com/RedHatInsights/insights-core/issues/808)
- Documentation referring to old parser requirement syntax [\#791](https://github.com/RedHatInsights/insights-core/issues/791)
- Get rpm signature from InstalledRpms parser [\#688](https://github.com/RedHatInsights/insights-core/issues/688)
- "runnable rules" [\#292](https://github.com/RedHatInsights/insights-core/issues/292)
- For Fava, alter the doc for each Parser and Combiner [\#291](https://github.com/RedHatInsights/insights-core/issues/291)
- run parsers and combiners \(and rules\) during collection [\#290](https://github.com/RedHatInsights/insights-core/issues/290)

## [insights-core-1.72.0-224](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.72.0-224) (2018-02-08)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/3.0rc1...insights-core-1.72.0-224)

**Closed issues:**

- run\_phase: explicit handling of process.returncode values [\#931](https://github.com/RedHatInsights/insights-core/issues/931)
- Keep .registered, .unregistered in /etc/redhat-access-insights [\#915](https://github.com/RedHatInsights/insights-core/issues/915)
- PSAuxcww need to skip warning line [\#912](https://github.com/RedHatInsights/insights-core/issues/912)

## [3.0rc1](https://github.com/RedHatInsights/insights-core/tree/3.0rc1) (2018-01-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.4-2...3.0rc1)

## [insights-core-3.0.4-2](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.4-2) (2018-01-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.71.0-217...insights-core-3.0.4-2)

## [insights-core-1.71.0-217](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.71.0-217) (2018-01-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.70.0-214...insights-core-1.71.0-217)

**Fixed bugs:**

- Update --force-reregister messaging [\#703](https://github.com/RedHatInsights/insights-core/issues/703)

## [insights-core-1.70.0-214](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.70.0-214) (2018-01-23)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.69.0-211...insights-core-1.70.0-214)

## [insights-core-1.69.0-211](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.69.0-211) (2018-01-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.68.0-203...insights-core-1.69.0-211)

**Fixed bugs:**

- Client log file rotation issues [\#710](https://github.com/RedHatInsights/insights-core/issues/710)
- Client Crashes on Fedora 26 [\#706](https://github.com/RedHatInsights/insights-core/issues/706)
- Fix fallback in 1.x and 3.x version of the client [\#695](https://github.com/RedHatInsights/insights-core/issues/695)

## [insights-core-1.68.0-203](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.68.0-203) (2018-01-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.67.0-188...insights-core-1.68.0-203)

**Closed issues:**

- Parser for command output ip -s link \#859 [\#864](https://github.com/RedHatInsights/insights-core/issues/864)
- Add CPU flags to cpuinfo parser \#816 [\#837](https://github.com/RedHatInsights/insights-core/issues/837)

## [insights-core-1.67.0-188](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.67.0-188) (2018-01-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.66.0-177...insights-core-1.67.0-188)

## [insights-core-1.66.0-177](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.66.0-177) (2017-12-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.65.0-166...insights-core-1.66.0-177)

**Implemented enhancements:**

- De-duplicate `ps` parsers [\#382](https://github.com/RedHatInsights/insights-core/issues/382)

**Fixed bugs:**

- Parser error in rabbitmq.py [\#786](https://github.com/RedHatInsights/insights-core/issues/786)

**Closed issues:**

- Nova\_log parser has no tests [\#797](https://github.com/RedHatInsights/insights-core/issues/797)
- ClusterConf should be an XML parser rather than based on LogFileOutput [\#177](https://github.com/RedHatInsights/insights-core/issues/177)

## [insights-core-1.65.0-166](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.65.0-166) (2017-12-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.64.0-154...insights-core-1.65.0-166)

**Implemented enhancements:**

- Make remove.conf smarter [\#801](https://github.com/RedHatInsights/insights-core/issues/801)
- Ps parsers update for master branch \(\#744\) [\#793](https://github.com/RedHatInsights/insights-core/issues/793)
- Implement ACLs properly [\#712](https://github.com/RedHatInsights/insights-core/issues/712)

**Fixed bugs:**

- bug in Pvs parser and Lvm combiner [\#736](https://github.com/RedHatInsights/insights-core/issues/736)

**Closed issues:**

- Also parse the grub v1 config file for UEFI machine. \#794 [\#811](https://github.com/RedHatInsights/insights-core/issues/811)
- Added new parsers for two options under /sys/kernel/mm/transparent\_hugepage/. \#767 [\#769](https://github.com/RedHatInsights/insights-core/issues/769)
- Update Insights man pages [\#707](https://github.com/RedHatInsights/insights-core/issues/707)

## [insights-core-1.64.0-154](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.64.0-154) (2017-11-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.3-2...insights-core-1.64.0-154)

**Implemented enhancements:**

- SkipComponent/SkipException Handling and Extension to Combiners [\#720](https://github.com/RedHatInsights/insights-core/issues/720)

**Fixed bugs:**

- Parse Error in `ntp\_sources.py` [\#727](https://github.com/RedHatInsights/insights-core/issues/727)
- Parser error in `ntp\_sources.py` [\#672](https://github.com/RedHatInsights/insights-core/issues/672)
- SysconfigKdump parser missing from master branch [\#670](https://github.com/RedHatInsights/insights-core/issues/670)
- satellite\_version combiner should not return None [\#658](https://github.com/RedHatInsights/insights-core/issues/658)

**Closed issues:**

- Add parser audit\_log.py to 3.x [\#685](https://github.com/RedHatInsights/insights-core/issues/685)

## [insights-core-3.0.3-2](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.3-2) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.63.0-140...insights-core-3.0.3-2)

## [insights-core-1.63.0-140](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.63.0-140) (2017-11-21)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.62.0-129...insights-core-1.63.0-140)

**Fixed bugs:**

- jaylin test [\#719](https://github.com/RedHatInsights/insights-core/issues/719)
- .cache.json is not updated correctly [\#715](https://github.com/RedHatInsights/insights-core/issues/715)

**Closed issues:**

- test [\#718](https://github.com/RedHatInsights/insights-core/issues/718)

## [insights-core-1.62.0-129](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.62.0-129) (2017-11-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.61.0-127...insights-core-1.62.0-129)

## [insights-core-1.61.0-127](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.61.0-127) (2017-11-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.60.0-117...insights-core-1.61.0-127)

**Fixed bugs:**

- Incorrect use of optional dependencies in combiners [\#647](https://github.com/RedHatInsights/insights-core/issues/647)

**Closed issues:**

- Update docs and create PR for master branch for libkeyutils parser [\#643](https://github.com/RedHatInsights/insights-core/issues/643)

## [insights-core-1.60.0-117](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.60.0-117) (2017-11-01)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.59.0-113...insights-core-1.60.0-117)

**Closed issues:**

- Port Scaffold Script to Master Branch [\#254](https://github.com/RedHatInsights/insights-core/issues/254)

## [insights-core-1.59.0-113](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.59.0-113) (2017-10-27)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.58.0-107...insights-core-1.59.0-113)

## [insights-core-1.58.0-107](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.58.0-107) (2017-10-19)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.3-1...insights-core-1.58.0-107)

## [insights-core-3.0.3-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.3-1) (2017-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.57.0-102...insights-core-3.0.3-1)

## [insights-core-1.57.0-102](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.57.0-102) (2017-10-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.56.0-95...insights-core-1.57.0-102)

**Implemented enhancements:**

- De-duplicate util/parse\_table and parsers/parse\_fixed\_table [\#344](https://github.com/RedHatInsights/insights-core/issues/344)

**Closed issues:**

- Update yaml.load to yaml.safe\_load [\#316](https://github.com/RedHatInsights/insights-core/issues/316)

## [insights-core-1.56.0-95](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.56.0-95) (2017-10-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.55.0-90...insights-core-1.56.0-95)

**Fixed bugs:**

- limits\_conf "unlimitied" error [\#447](https://github.com/RedHatInsights/insights-core/issues/447)

## [insights-core-1.55.0-90](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.55.0-90) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.54.0-87...insights-core-1.55.0-90)

## [insights-core-1.54.0-87](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.54.0-87) (2017-10-11)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.53.0-81...insights-core-1.54.0-87)

## [insights-core-1.53.0-81](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.53.0-81) (2017-10-10)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.52.0-71...insights-core-1.53.0-81)

## [insights-core-1.52.0-71](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.52.0-71) (2017-10-06)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.2-6...insights-core-1.52.0-71)

## [insights-core-3.0.2-6](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.2-6) (2017-10-04)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.1-1...insights-core-3.0.2-6)

## [insights-core-3.0.1-1](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.1-1) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-3.0.0-5...insights-core-3.0.1-1)

## [insights-core-3.0.0-5](https://github.com/RedHatInsights/insights-core/tree/insights-core-3.0.0-5) (2017-10-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.51.0-65...insights-core-3.0.0-5)

## [insights-core-1.51.0-65](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.51.0-65) (2017-09-29)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.50.0-56...insights-core-1.51.0-65)

## [insights-core-1.50.0-56](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.50.0-56) (2017-09-26)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-38...insights-core-1.50.0-56)

**Implemented enhancements:**

- Rework core runtime to be like vulcan [\#11](https://github.com/RedHatInsights/insights-core/issues/11)
- Support Python Version 2.6.x [\#10](https://github.com/RedHatInsights/insights-core/issues/10)

**Closed issues:**

- Should probably rename hand\_map\_error and handle\_reduce\_error in evaluators.py [\#66](https://github.com/RedHatInsights/insights-core/issues/66)
- Drop support for local mappers [\#7](https://github.com/RedHatInsights/insights-core/issues/7)

## [insights-core-1.49.0-38](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-38) (2017-09-15)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.49.0-37...insights-core-1.49.0-38)

**Fixed bugs:**

- chkconfig.py can not parsed RHEL 7.3 'chkconfig --list' [\#112](https://github.com/RedHatInsights/insights-core/issues/112)
- Vgdisplay spec does not match sos report or rule [\#13](https://github.com/RedHatInsights/insights-core/issues/13)

**Closed issues:**

- Get 100% test coverage of insights/core/\_\_init\_\_.py [\#139](https://github.com/RedHatInsights/insights-core/issues/139)

## [insights-core-1.49.0-37](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.49.0-37) (2017-09-13)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.48.0-34...insights-core-1.49.0-37)

## [insights-core-1.48.0-34](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.48.0-34) (2017-09-12)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.47.0-17...insights-core-1.48.0-34)

**Closed issues:**

- Sync the master branch with 1.x branch [\#121](https://github.com/RedHatInsights/insights-core/issues/121)

## [insights-core-1.47.0-17](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.47.0-17) (2017-08-31)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-15...insights-core-1.47.0-17)

## [insights-core-1.46.0-15](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-15) (2017-08-30)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.46.0-12...insights-core-1.46.0-15)

## [insights-core-1.46.0-12](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.46.0-12) (2017-08-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-105...insights-core-1.46.0-12)

**Closed issues:**

- CertificatesEnddate fails to parse filenames [\#300](https://github.com/RedHatInsights/insights-core/issues/300)

## [insights-core-1.44.0-105](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-105) (2017-08-02)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.44.0-103...insights-core-1.44.0-105)

## [insights-core-1.44.0-103](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.44.0-103) (2017-07-28)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.43.0-93...insights-core-1.44.0-103)

**Fixed bugs:**

- Lvs mapper fails on lists with log and image LVs [\#288](https://github.com/RedHatInsights/insights-core/issues/288)

**Closed issues:**

- Move AlternativesOutput class and associated parsers into single file. [\#140](https://github.com/RedHatInsights/insights-core/issues/140)

## [insights-core-1.43.0-93](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.43.0-93) (2017-07-18)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.42.0-63...insights-core-1.43.0-93)

**Implemented enhancements:**

- Support python 2.6 [\#180](https://github.com/RedHatInsights/insights-core/issues/180)

**Closed issues:**

- Add new shared parser irqbalance\_conf.py \#213 [\#223](https://github.com/RedHatInsights/insights-core/issues/223)
- Should we convert this multinode parser \(metadata.json\) to class type ? [\#221](https://github.com/RedHatInsights/insights-core/issues/221)
- NTPConfParser class is missing from the documentation [\#167](https://github.com/RedHatInsights/insights-core/issues/167)
- Neutron server log documentation for 1.x branch \#146 [\#152](https://github.com/RedHatInsights/insights-core/issues/152)
- Neutron plugin documentation for 1.x branch \#145 [\#151](https://github.com/RedHatInsights/insights-core/issues/151)
- Test scannable parser class for 1.x branch \#144 [\#150](https://github.com/RedHatInsights/insights-core/issues/150)
- Remove the deprecated `.data` from LsBoot \#103 [\#104](https://github.com/RedHatInsights/insights-core/issues/104)
- Limits conf combiner \#70 [\#85](https://github.com/RedHatInsights/insights-core/issues/85)

## [insights-core-1.42.0-63](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.42.0-63) (2017-07-03)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/insights-core-1.41.0-43...insights-core-1.42.0-63)

**Closed issues:**

- Parser module test coverage at 100% \#148 [\#154](https://github.com/RedHatInsights/insights-core/issues/154)
- Kerberos KDC log parser for 2.x branch [\#153](https://github.com/RedHatInsights/insights-core/issues/153)
- Add new shared parser iscsiadm\_mode\_session.py \#136 [\#137](https://github.com/RedHatInsights/insights-core/issues/137)
- Enhance httpd\_conf to support nested sections \#84 [\#120](https://github.com/RedHatInsights/insights-core/issues/120)
- Simplify Policy booleans handling \#96 [\#97](https://github.com/RedHatInsights/insights-core/issues/97)
- Uname not properly parsed for RHEL 6.3 sosreports [\#90](https://github.com/RedHatInsights/insights-core/issues/90)
- Falafel reference in image [\#23](https://github.com/RedHatInsights/insights-core/issues/23)

## [insights-core-1.41.0-43](https://github.com/RedHatInsights/insights-core/tree/insights-core-1.41.0-43) (2017-06-20)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.40.0-23...insights-core-1.41.0-43)

**Closed issues:**

- Update ceph\_version to add version 2.2 \#105 [\#106](https://github.com/RedHatInsights/insights-core/issues/106)
- Removing previously used but abandoned test functions \#98 [\#99](https://github.com/RedHatInsights/insights-core/issues/99)
- Expose associated satellite information in system metadata \#65 [\#87](https://github.com/RedHatInsights/insights-core/issues/87)
- Added keyword\_search function \#69 [\#86](https://github.com/RedHatInsights/insights-core/issues/86)
- Rename from falafel to insights-core [\#8](https://github.com/RedHatInsights/insights-core/issues/8)

## [falafel-1.40.0-23](https://github.com/RedHatInsights/insights-core/tree/falafel-1.40.0-23) (2017-06-07)
[Full Changelog](https://github.com/RedHatInsights/insights-core/compare/falafel-1.39.0-11...falafel-1.40.0-23)

**Fixed bugs:**

- Transaction check error w/python-requests on falafel-1.38.0-25 installation [\#12](https://github.com/RedHatInsights/insights-core/issues/12)

**Closed issues:**

- uname parser fails for kernel 2.6.32-504.8.2.bgq.el6 [\#52](https://github.com/RedHatInsights/insights-core/issues/52)

## [falafel-1.39.0-11](https://github.com/RedHatInsights/insights-core/tree/falafel-1.39.0-11) (2017-05-31)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
