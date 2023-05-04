Name:           insights-core
Version:        3.1.23
Release:        1%{?dist}
Summary:        Insights Core is a data collection and analysis framework.

License:        ASL 2.0
URL:            https://github.com/RedHatInsights/insights-core
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires: python3
Requires: python3-redis

%if 0%{?rhel} == 7
Requires: python36-CacheControl
Requires: python36-colorama
Requires: python36-defusedxml
Requires: python36-jinja2
Requires: python36-lockfile
Requires: python36-PyYAML
Requires: python36-requests
Requires: python36-six
%else
Requires: python3-CacheControl
Requires: python3-colorama
Requires: python3-defusedxml
Requires: python3-jinja2
Requires: python3-lockfile
Requires: python3-pyyaml
Requires: python3-requests
Requires: python3-six
%endif

%description
Insights Core is a data collection and analysis framework.

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT
%{__python3} setup.py install -O1 --root $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT/usr/bin

%files
# For noarch packages: sitelib
%{python3_sitelib}/*

%changelog
* Thu May 04 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.23-1
- feat: new client_metadata module to hold parsers for all client generated
  files (#3775) (xiangceliu@redhat.com)
- chore: add the missed deprecate warnings (#3774) (xiangceliu@redhat.com)
- feat: new option to show hit result only for insights-run (#3771)
  (xiangceliu@redhat.com)
- feat: add parser and combiner for IPA (#3767) (cheimes@redhat.com)
- Travis is dead. Travis is dead, Baby. (#3777) (jhnidek@redhat.com)
- fix: default and disabled module cannot be active (#3773)
  (psegedy@redhat.com)
- fix: fix test playbook by using no named tuples (#3772)
  (93577878+ahitacat@users.noreply.github.com)

* Thu Apr 27 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.22-1
- fix: handle the first line is warning in InstalledRpms (#3770)
  (xiangceliu@redhat.com)
- fix(playbook_verifier): clarify logic when normalizing snippets (#3752)
  (subpop@users.noreply.github.com)
- Feat: Add new parser ls_var_lib_rpm (#3763) (986222045@qq.com)
- fix: DnfModuleList parser and collect dnf_module_list (#3756)
  (patriksegedy@gmail.com)
- feat: enhance GrubbyDefaultKernel to skip warn msgs (#3761)
  (xiaoxwan@redhat.com)
- fix: update ubuntu image for 2.6 test (#3766) (christian@python.org)
- feat: Google Cloud public IP spec (#3762) (lzap+git@redhat.com)
- fix: the typo version in CHANGELOG (xiangceliu@redhat.com)

* Tue Apr 25 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.21-1
- Revert "feat: update logging file handler for logrotate (#3702)" (#3760)
  (xiangceliu@redhat.com)
- fix: fix processing of SerializedArchiveContext (#3183)
  (20520336+bfahr@users.noreply.github.com)

* Thu Apr 20 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.20-1
- feat: update logging file handler for logrotate (#3702)
  (jasonjerome16@gmail.com)
- fix: use log instead of print in test.run_input_data(#3750)
  (lichen@redhat.com)
- feat: Azure public IP spec (#3751) (lzap+git@redhat.com)
- fix: soscleaner get relative_path safely - 2 (#3754) (xiangceliu@redhat.com)
- Make malware more flexible when detecting its running against stage (#3725)
  (mhuth@redhat.com)

* Fri Apr 14 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.19-1
- fix: Wrong raw line bound in parser "FSTab" (#3749)
  (44796653+huali027@users.noreply.github.com)
- feat: add spec and parser for /etc/audisp/audispd.conf (#3743)
  (xiaoxwan@redhat.com)
- feat: AWS public IPv4 spec (#3741) (lukas@zapletalovi.com)
- fix: check machine id as some archives are with empty machine-id file (#3747)
  (lichen@redhat.com)
- fix: soscleaner get relative_path safely (#3744) (xiangceliu@redhat.com)
- feat: Add parser LsinitrdLvmConf (#3740)
  (30404410+qinpingli@users.noreply.github.com)
- fix: correct the initialization of ParserException in PHPConf (#3738)
  (lichen@redhat.com)
- fix: datasource rpm_pkgs returns list of string but not tuple (#3736)
  (xiangceliu@redhat.com)
- fix: Add new package findutils into spec rpm_V_packages (#3733)
  (jiazhang@redhat.com)

* Thu Apr 06 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.18-1
- feat: add "vf_enabled" parse for spec ip_s_link (#3729) (xiaoxwan@redhat.com)
- Fix check registration status to be robust against network failures (#3713)
  (93577878+ahitacat@users.noreply.github.com)

* Thu Apr 06 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.17-1
- Feat: New parser for repquota command (#3717) (986222045@qq.com)
- chore: update the spec name of BlacklistedSpecs (#3728)
  (xiangceliu@redhat.com)
- fix: check content before use it (#3727) (lichen@redhat.com)
- fix: support built-in metadata files in core-collection (#3723)
  (xiangceliu@redhat.com)
- feat: RHICOMPL-3706 add link to KB article about OOM issues (#3724)
  (skateman@users.noreply.github.com)
- chore: tiny simplify and remove unused code in spec_factory.py (#3726)
  (xiangceliu@redhat.com)

* Thu Mar 30 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.16-1
- feat(compliance): RHICOMPL-3629 log OOM error when scan fails (#3721)
  (skateman@users.noreply.github.com)
- New spec "ls -lan /etc/selinux/targeted/policy" (#3722)
  (44796653+huali027@users.noreply.github.com)

* Thu Mar 23 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.15-1
- FEAT: Add new parser ls_rsyslog_errorfile (#3719) (986222045@qq.com)

* Fri Mar 17 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.14-1
- chore: use RHEL for os_release.release (#3716) (xiangceliu@redhat.com)
- fix: should not lose the exceptions from components (#3715)
  (xiangceliu@redhat.com)

* Thu Mar 16 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.13-1
- feat: New datasource and parser for leapp-report.json (#3708)
  (xiangceliu@redhat.com)
- feat: Add store_skips argument to run_input_data (#3706) (71874510+jholecek-
  rh@users.noreply.github.com)
- feat: Split listdir to listdir and listglob spec factories (#3694)
  (71874510+jholecek-rh@users.noreply.github.com)
- fix: enhance the error message to reminder customers re-register (#3691)
  (lichen@redhat.com)
- feat: New spec to get the duplicate machine id  (#3709)
  (44796653+huali027@users.noreply.github.com)
- Fix logs of check registration status for legacy upload (#3710)
  (93577878+ahitacat@users.noreply.github.com)
- fix: print short info for all Exceptions (#3707) (xiangceliu@redhat.com)
- Log malware tracebacks to the log file, not the console (#3701)
  (mhuth@redhat.com)
- fix: let 'get_filters' work for filterable=True specs only (#3705)
  (xiangceliu@redhat.com)
- fix: update OSRelease.is_rhel more accurate (#3700) (xiangceliu@redhat.com)

* Sat Mar 11 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.12-1
- Revert "feat: New spec to get the duplicate machine id (#3697)" (#3703)
  (xiangceliu@redhat.com)

* Thu Mar 09 2023 Lizhong Chen <lichen@redhat.com> 3.1.11-1
- Fix malware SSL error fix - make it more flexible (#3695) (mhuth@redhat.com)
- feat: New spec to get the duplicate machine id (#3697)
  (44796653+huali027@users.noreply.github.com)
- chore: update the latest package signing keys (#3696) (xiangceliu@redhat.com)

* Thu Mar 02 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.10-1
- feat: New spec and parser for sys_block_queue_stable_writes (#3688)
  (xiaoxwan@redhat.com)
- feat: Add container spec mssql_api_assessment (#3690) (jiazhang@redhat.com)
- feat: add OSRelease.issued_packages to return the issued packages (#3686)
  (xiangceliu@redhat.com)
- Better handle SSL cert verify errors when downloading malware rules (#3685)
  (mhuth@redhat.com)

* Thu Feb 23 2023 Lizhong Chen <lichen@redhat.com> 3.1.9-1
- Update rpm_pkgs datasource and create new parser RpmPkgsWritable. (#3684)
  (41325380+jobselko@users.noreply.github.com)

* Thu Feb 23 2023 Lizhong Chen <lichen@redhat.com> 3.1.8-1
- feat: New spec "/etc/sos.conf" and its parser (#3680)
  (44796653+huali027@users.noreply.github.com)
- fix: correct parse_content in JSONParser (#3682)
  (91992306+ann0ra@users.noreply.github.com)

* Thu Feb 16 2023 Lizhong Chen <lichen@redhat.com> 3.1.7-1
- fix: The provider of GCP should be 'gcp' but not 'google' (#3678)
  (xiangceliu@redhat.com)
- feat: Add spec "parted__l" and enhance its parser (#3676)
  (xiaoxwan@redhat.com)
- feat: Add container spec for vsftpd and ps (#3674) (jiazhang@redhat.com)
- fix: Correct parser examples and tests (#3677) (rblakley@redhat.com)

* Thu Feb 09 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.6-1
- chore: remove unused spec lsinitrd_kdump_image (#3644) (986222045@qq.com)
- fix: py26 test: install libssl1.0-dev manually (#3675)
  (xiangceliu@redhat.com)
- chore: use the unique mangle_command for specs (#3673)
  (xiangceliu@redhat.com)
- feat: Capture blacklisted specs inside archive (#3664) (rblakley@redhat.com)
- Change sos archive lvm spec names (#3672) (rblakley@redhat.com)

* Thu Feb 02 2023 Lizhong Chen <lichen@redhat.com> 3.1.5-1
- fix: Enhance datasource kernel_module_filters to check the loaded modules
  (#3670) (jiazhang@redhat.com)
- fix: use LC_ALL=C.UTF-8 for subscription-manager (#3669)
  (ptoscano@redhat.com)
- feat: add CloudInstance to canonical_facts (#3654) (xiangceliu@redhat.com)
- Deprecate SkipException to help avoid confusion (#3662) (rblakley@redhat.com)
- feat: Add arg to capture skips in the broker (#3663) (rblakley@redhat.com)
- fix: Resolve VDOStatus excessive ParseException (#3668) (xiaoxwan@redhat.com)
- Disable datasource timeout alarm for the malware-detection app (#3666)
  (mhuth@redhat.com)
- Make malware-detection app more resilient to unexpected errors (#3661)
  (mhuth@redhat.com)
- Exclude malware-detection rules files in /var/tmp (and other locations)
  (#3665) (mhuth@redhat.com)

* Thu Jan 19 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.4-1
- fix: add '-d 2' to yum_repolist spec (#3660) (xiangceliu@redhat.com)
- feat: add JbossRuntimeVersions parser (#3639) (lichen@redhat.com)
- Move remaining exceptions to the new exceptions module (#3656)
  (rblakley@redhat.com)
- Fix: Add condition to check the output of "rpm-ostree status" firstly into
  combiner rhel_for_edge (#3657) (jiazhang@redhat.com)
- fix: check the content first in class InstalledRpms (#3651)
  (lichen@redhat.com)
- Fix: write all getting data to sys_fs_cgroup_uniq_memory_swappiness (#3658)
  (30404410+qinpingli@users.noreply.github.com)
- add specs (datasource via insights-cat) required by CloudInstance (#3655)
  (xiangceliu@redhat.com)

* Thu Jan 12 2023 Xiangce Liu <xiangceliu@redhat.com> 3.1.3-1
- Revert "Fix: Add condition to check the output of "rpm-ostree status" firstly
  (#3634)" (#3652) (xiangceliu@redhat.com)
- feat: new combiner OSRelease to identify RHEL (#3640) (xiangceliu@redhat.com)
- feat: New datasource "sys_fs_cgroup_uniq_memory_swappiness" and its parser
  (#3645) (30404410+qinpingli@users.noreply.github.com)
- fix: Do not log Parsers' Traceback during collection (#3633)
  (xiangceliu@redhat.com)
- Fix: Add condition to check the output of "rpm-ostree status" firstly (#3634)
  (jiazhang@redhat.com)
- Move exceptions to their own module file (#3622) (rblakley@redhat.com)
- Allow callers to order components for execution. (#3649)
  (csams@users.noreply.github.com)
- Create timeout signal for hostcontext only (#3647)
  (lhuett@users.noreply.github.com)
- feat: Add env override to CommandOutputProvider (#3636) (rblakley@redhat.com)
- fix: Convert aws_token to string since sometimes it's unicode (#3643)
  (44796653+huali027@users.noreply.github.com)
- fix: py26 CI not found 'Python.h' (#3642) (xiangceliu@redhat.com)

* Thu Dec 15 2022 Xiangce Liu <xiangceliu@redhat.com> 3.1.2-1
- Fix: fix GrubbyDefaultKernel cannot handle specific invalid content (#3632)
  (986222045@qq.com)
- Improve old Python compatibility by not requiring ipython 8.6.0. (#3630)
  (jsvoboda@redhat.com)
- fix: Log brief msg instead of Traceback when cmd not found (#3628)
  (xiangceliu@redhat.com)
- Delete old malware rules files from /var/tmp as well (#3625)
  (mhuth@redhat.com)

* Thu Dec 08 2022 Xiangce Liu <xiangceliu@redhat.com> 3.1.1-1
- fix: fix CI issue when preparing py26 env (#3624) (xiangceliu@redhat.com)
- Feat: Add Parser LsinitrdKdumpImage  (#3567) (986222045@qq.com)
- Remove usage of reregistration and deprecate cli-option (#3522)
  (93577878+ahitacat@users.noreply.github.com)
- feat: Add spec sys_cpuset_cpus (#3611) (jiazhang@redhat.com)
- fix: fix errors in ethtool (#3605) (lichen@redhat.com)
- feat: Add spec container_nginx_error_log (#3607) (jiazhang@redhat.com)
- feat: Add container spec sys_cpu_online (#3612) (jiazhang@redhat.com)
- feat: New spec "ls -lZ /var/lib/rsyslog" and the parser (#3618)
  (44796653+huali027@users.noreply.github.com)
- Feat register no machine-id (#3554)
  (93577878+ahitacat@users.noreply.github.com)

* Thu Dec 01 2022 Xiangce Liu <xiangceliu@redhat.com> 3.1.0-1
- Keep the code to delete previously-named malware rules file (#3619)
  (mhuth@redhat.com)
- fix: add deprecated warning message in insights.combiners.mounts (#3613)
  (lichen@redhat.com)
- feat: Add timeout to datasources (#3598) (rblakley@redhat.com)
- Display message when malware scan_timeout aborts scan (#3617)
  (mhuth@redhat.com)
- Add nginx error log which is installed from RHSCL (#3616)
  (44796653+huali027@users.noreply.github.com)
- fix: Update the pinned doc modules (#3615) (rblakley@redhat.com)
- Add datasource to get jboss versions (#3600) (lichen@redhat.com)
- [insights-core-3.0.300] Remove deprecated features (#3595)
  (psachin@redhat.com)
- Don't look for yara installed in /usr/local/bin (#3614) (mhuth@redhat.com)
- test: use ubuntu 20.04 instead of latest as the issue in latest (#3608)
  (lichen@redhat.com)
- Rename downloaded temp malware rules file (#3602) (mhuth@redhat.com)
- New specs var_log_pcp_openmetrics_log (#3596)
  (87797511+mohitkumarrh@users.noreply.github.com)
- feat: RHEL 9.1 is GA (#3599) (xiangceliu@redhat.com)
- feat: New spec "timedatectl" and the parser (#3592)
  (44796653+huali027@users.noreply.github.com)

* Thu Nov 17 2022 Sachin Patil <psachin@redhat.com> 3.0.305-1
- Rename system_user_dirs to rpm_pkgs (#3597) (41325380+jobselko@users.noreply.github.com)

* Thu Nov 17 2022 Sachin Patil <psachin@redhat.com> 3.0.304-1
- [New Specs] ls_var_lib_pcp (#3590) (87797511+mohitkumarrh@users.noreply.github.com)
- Fix: Update container_installed_rpms spec (#3589) (986222045@qq.com)
- Revert "feat: Add timeout to datasources (#3573)" (#3594) (rblakley@redhat.com)
- feat: Add timeout to datasources (#3573) (rblakley@redhat.com)
- Add rhel 8.7 into uname.py (#3591) (lichen@redhat.com)

* Thu Nov 10 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.303-1
- Registration check unregisters when it is not connected (#3540)
  (93577878+ahitacat@users.noreply.github.com)
- Update system_user_dirs datasource (#3586)
  (41325380+jobselko@users.noreply.github.com)
- Handle network exceptions when accessing egg URL (#3588) (mhuth@redhat.com)
- Feat: New Parser for 'dotnet --version' Command for Containers (#3581)
  (986222045@qq.com)
- feat: New Combiner CloudInstance (#3585) (xiangceliu@redhat.com)
- feat: New spec "/etc/fapolicyd/rules.d/*.rules" and parser (#3587)
  (44796653+huali027@users.noreply.github.com)
- fix: values of broker.tracebacks should be string (#3579)
  (xiangceliu@redhat.com)
- Update github actions to use latest version (#3583)
  (20520336+bfahr@users.noreply.github.com)
- fix(parsers): add support for missing logs (#3582)
  (subpop@users.noreply.github.com)
- feat(client): add --manifest argument (#3547)
  (subpop@users.noreply.github.com)

* Thu Nov 03 2022 Sachin Patil <psachin@redhat.com> 3.0.302-1
- feat: new spec and parser for 'azure_instance_id' (#3568) (xiangceliu@redhat.com)
- feat: Add parser container_inspect (#3562) (jiazhang@redhat.com)
- fix: remove the inner functions of the _make_rpm_formatter (#3574) (xiangceliu@redhat.com)
- chore: remove the unused 'ethernet_interfaces' spec (#3577) (xiangceliu@redhat.com)
- fix: check list range to avoid exception (#3576) (10719925+takayuki-nagata@users.noreply.github.com)
- fix: LuksDump not parsing multiple data segments (#3569) (daniel.zatovic@gmail.com)
- feat: new spec and parser for 'subscription-manage facts' (#3555) (xiangceliu@redhat.com)
- enhance: add base class 'OVSvsctlList' (#3575) (39508521+shlao@users.noreply.github.com)

* Mon Oct 31 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.301-1
- fix: missing call to a RPM format generation function (#3572)
  (daniel.zatovic@gmail.com)
- fix: remove duplicated containers from running_rhel_containers (#3571)
  (xiangceliu@redhat.com)

* Thu Oct 27 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.300-1
- Avoid test to write in disk if machine-id is not found (#3543)
  (93577878+ahitacat@users.noreply.github.com)
- enhance and fix for softnet_data parser (#3561) (remijouannet@gmail.com)
- test: add test for existing container specs (#3563) (xiangceliu@redhat.com)
- Order specs by alphabetical order (#3564) (rblakley@redhat.com)
- feat: New Parser for container_installed_rpms (#3560) (986222045@qq.com)
- Handle upload exceptions allowing --retries to work properly (#3558)
  (mhuth@redhat.com)
- fix: let container_execute to support rpm_format of installed_rpms (#3559)
  (xiangceliu@redhat.com)

* Thu Oct 20 2022 Sachin Patil <psachin@redhat.com> 3.0.299-1
- feat: New spec "semanage login -l" and parser (#3548) (44796653+huali027@users.noreply.github.com)
- [New-parser] parser_mpirun_version (#3542) (87797511+mohitkumarrh@users.noreply.github.com)
- Removed assert of virt-who, it is not in uploader.json (#3556) (93577878+ahitacat@users.noreply.github.com)

* Thu Oct 13 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.298-1
- fix: Add ability to return exceptions during insights collect (#3539)
  (vdymna@redhat.com)
- refactor: remove duplicated specs from get_dependency_specs (#3549)
  (xiangceliu@redhat.com)
- Remove authselect_current from core collection (#3552)
  (xiangceliu@redhat.com)
- Feat: New parser for the "ls -lan /var/lib/sss/pubconf/krb5.include.d"
  command (#3545) (44598880+rasrivas-redhat@users.noreply.github.com)
- Deprecate insights.core.scannable & engine_log parser (#3541)
  (psachin@redhat.com)
- chore: remove the unused specs (#3537) (xiangceliu@redhat.com)
- fix: Restore the spec ovs_appctl_fdb_show_bridge (#3538) (psachin@redhat.com)
- Add spec and parser for luksmeta command (#3525) (daniel.zatovic@gmail.com)

* Thu Oct 06 2022 Sachin Patil <psachin@redhat.com> 3.0.297-1
- feat: add helper function: get_dependency_specs and test  (#3534) (xiangceliu@redhat.com)
- Fix registration tests (#3519) (93577878+ahitacat@users.noreply.github.com)

* Thu Sep 29 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.296-1
- fix: make SAPHostCtrlInstances compatible with old archives (#3528)
  (xiangceliu@redhat.com)
- refactor: Keep the raw line for rule use (#3533)
  (44796653+huali027@users.noreply.github.com)
- feat: [PoC] Support Container Specs (#3477) (xiangceliu@redhat.com)
- fix: bz-2130242, remove the print statement (#3535) (xiangceliu@redhat.com)
- Update docstring to make it more readable (#3531) (psachin@redhat.com)

* Thu Sep 22 2022 Sachin Patil <psachin@redhat.com> 3.0.295-1
- feat: New spec "/etc/cron.d/foreman" and parser (#3514) (44796653+huali027@users.noreply.github.com)
- feat: Add combiner rhel for edge (#3526) (jiazhang@redhat.com)
- fix: bz-2126966: use SIGTERM for rpm instead of SIGKILL (#3524) (xiangceliu@redhat.com)
- fix: Soscleaner fix (#3502) (stomsa@redhat.com)
- fix: Removing extraneous space inserted in commit 894484a (#3523) (80352581+mike-kingsbury@users.noreply.github.com)

* Thu Sep 15 2022 Sachin Patil <psachin@redhat.com> 3.0.294-1
- feat: New spec to get satellite logs table size and its parser (#3516) (44796653+huali027@users.noreply.github.com)
- New parser for CpuSMTControl and tests update (#3521) (41325380+jobselko@users.noreply.github.com)
- Feat: Add spec and parser for cryptsetup luksDump (#3504) (daniel.zatovic@gmail.com)
- feat: Add spec "satellite_enabled_features" back (#3517) (44796653+huali027@users.noreply.github.com)
- Refractor cleanup local files for unregistration processes (#3520) (93577878+ahitacat@users.noreply.github.com)
- feat: Update ls_systemd_units parser (#3518) (41325380+jobselko@users.noreply.github.com)

* Thu Sep 08 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.293-1
- fix: support InstanceType in saphostctrl (#3512) (xiangceliu@redhat.com)
- Feat: add secure spec to default.py (#3513) (986222045@qq.com)
- Ensure full path when using timeout command (#3508)
  (20520336+bfahr@users.noreply.github.com)

* Thu Sep 01 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.292-1
- Added no_proxy autoconfiguration from rhsm conf and tests (#3507)
  (93577878+ahitacat@users.noreply.github.com)
- Fix: grubenv cannot be collected when error shown in output (#3511)
  (986222045@qq.com)
- fix: change cloud_cfg to Yaml and modify the source spec (#3484)
  (xiangceliu@redhat.com)
- fix: Revert the httpd_on_nfs datasource spec (#3509) (xiangceliu@redhat.com)
- fix: Issue calling collect from cli (#3506)
  (20520336+bfahr@users.noreply.github.com)

* Thu Aug 25 2022 Sachin Patil <psachin@redhat.com> 3.0.291-1
- Feat: New journal_header (#3498) (986222045@qq.com)
- feat: New spec and parser to get the satellite provision params (#3501) (44796653+huali027@users.noreply.github.com)
- Feat: New parser for 'ls -lanL /etc/ssh' command (#3499) (986222045@qq.com)
- feat: New spec and parser for `authselect current` (#3490) (xiangceliu@redhat.com)
- Add release timeline (#3500) (psachin@redhat.com)

* Thu Aug 18 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.290-1
- New location for temp directory and tests (#3489)
  (93577878+ahitacat@users.noreply.github.com)

* Thu Aug 18 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.289-1
- feat: New spec and parser for "auditctl -l" (#3496)
  (44796653+huali027@users.noreply.github.com)
- Feat: New grub2_editenv_list parser (#3481) (986222045@qq.com)
- Automatically retry malware-detection downloads & uploads (#3493)
  (mhuth@redhat.com)

* Thu Aug 11 2022 Sachin Patil <psachin@redhat.com> 3.0.288-1
- feat: Add version to deprecated function (#3491) (rblakley@redhat.com)

* Thu Aug 04 2022 Sachin Patil <psachin@redhat.com> 3.0.287-1
- Feat: Add new parser sys_fs_cgroup_memory_tasks_number (#3467) (jiazhang@redhat.com)
- fix: Update aws specs to use IMDSv2 (#3486) (20520336+bfahr@users.noreply.github.com)
- New version of flake8 found some errors (#3488) (20520336+bfahr@users.noreply.github.com)
- Add missing datasource docs to build (#3487) (20520336+bfahr@users.noreply.github.com)
- Update the marker for MustGatherContext (#3479) (shzhou@redhat.com)
- Add new system_user_dirs datasource and parser (#3381) (41325380+jobselko@users.noreply.github.com)

* Thu Jul 28 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.286-1
- fix: the parser "LvmConfig" raises exception (#3476)
  (44796653+huali027@users.noreply.github.com)
- feat: Add spec for teamdctl_config_dump parser (#3472) (986222045@qq.com)
- Fix error with umask not being restored when dir exists (#3480)
  (20520336+bfahr@users.noreply.github.com)
- fix: Restrict Sphinx's version since it breaks docs build (#3483)
  (rblakley@redhat.com)

* Thu Jul 21 2022 Sachin Patil <psachin@redhat.com> 3.0.285-1
- fix: Add spec "lvmconfig" back (#3474) (44796653+huali027@users.noreply.github.com)
- Fix: Add pre-check for teamdctl_state_dump (#3470) (986222045@qq.com)
- Fix: Restore the spec cni_podman_bridge_conf (#3471) (39508521+shlao@users.noreply.github.com)



* Thu Jul 14 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.284-1
- Unregister option removes machine-id (#3449)
  (93577878+ahitacat@users.noreply.github.com)
- Add spec and parser for 'wc_-l_.proc.1.mountinfo' (#3459)
  (xiaoxwan@redhat.com)
- feat: revert and refine the padman list specs and parsers (#3466)
  (xiangceliu@redhat.com)
- Fix: test error of nmcli in the datasource ethernet (#3468)
  (986222045@qq.com)
- fix: Enhance nmcli (#3465) (986222045@qq.com)
- Feat: Add teamdctl_state_dump spec to insights_archive (#3455)
  (986222045@qq.com)
- fix: Catch any exceptions when scanning for files (#3463)
  (rblakley@redhat.com)
- fix: Replace non ascii characters with question marks (#3464)
  (rblakley@redhat.com)
- feat: Add combiner "ModulesInfo" (#3458)
  (44796653+huali027@users.noreply.github.com)

* Thu Jul 07 2022 Sachin Patil <psachin@redhat.com> 3.0.283-1
- feat: New spec "/etc/lvm/devices/system.devices" and parser (#3457)
  (44796653+huali027@users.noreply.github.com)

* Fri Jul 01 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.282-1
- fixes: Recover "modinfo_xxx" specs (#3456)
  (44796653+huali027@users.noreply.github.com)

* Thu Jun 30 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.281-1
- feat: add "modinfo_filtered_modules" to collect the filtered modules
  information (#3447) (44796653+huali027@users.noreply.github.com)
- feat: Parser for "ls systemd units" (#3451)
  (41325380+jobselko@users.noreply.github.com)
- Handle downloading malware-detection rules from stage environment (#3452)
  (mhuth@redhat.com)

* Thu Jun 23 2022 Sachin Patil <psachin@redhat.com> 3.0.280-1
- Update canonical_facts to load needed components (#3448) (20520336+bfahr@users.noreply.github.com)
- Remove RPM_OUTPUT_SHADOW_UTILS (#3442) (stomsa@redhat.com)
- Replace xfail with positive test (#3443) (stomsa@redhat.com)

* Fri Jun 17 2022 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.279-1
- Update canonical_facts to load needed components (#3444)
  (20520336+bfahr@users.noreply.github.com)
- Fix tests that removing temp archives (#3445)
  (93577878+ahitacat@users.noreply.github.com)
- Remove the excess bracket from CHANGELOG (xiangceliu@redhat.com)
- Fix the url typo in CHANGELOG (xiangceliu@redhat.com)

* Thu Jun 16 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.278-1
- Add new parser for /etc/nfs.conf (#3438) (xiaoxwan@redhat.com)
- Mock test creating files in protected directories (#3440)
  (93577878+ahitacat@users.noreply.github.com)
- Append compression type to content-type of MIME. Compare file compression
  with content_type. (#3435) (93577878+ahitacat@users.noreply.github.com)
- malware-detection: implement yara version handling differently (#3437)
  (mhuth@redhat.com)
- When insights client is killed the directories in /var/tmp are not removed
  rhbz#2009773 (#3396) (93577878+ahitacat@users.noreply.github.com)

* Thu Jun 09 2022 Sachin Patil <psachin@redhat.com> 3.0.277-1
- feat: Add --no-load-default arg to the insights-run command (#3434)
  (rblakley@redhat.com)
- feat: Support parallelly running for insights-engine (#3436)
  (xiangceliu@redhat.com)

* Thu Jun 02 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.276-1
- feat: New specs for systemd ls output and modification of existing parser
  (#3424) (41325380+jobselko@users.noreply.github.com)
- Updating sos_archive to parse file for GSS rule (#3432)
  (87797511+mohitkumarrh@users.noreply.github.com)
- feat: Add --parallel arg for insights-run (#3418) (rblakley@redhat.com)
- feat: new spec and parser for /etc/sudoers (#3425) (xiangceliu@redhat.com)
- feat: New spec and parser for group_info (#3423) (xiangceliu@redhat.com)
- malware-detection feature: handle different yara versions (#3428)
  (mhuth@redhat.com)
- refactor: move the rest of datasource to the datasources dir (#3430)
  (xiangceliu@redhat.com)
- chore: remove the unused get_owner from specs.default (#3429)
  (xiangceliu@redhat.com)
- Add Alpha to redhat release detection (#3431)
  (20520336+bfahr@users.noreply.github.com)
- feat: Updated the parser to also return  allow-recursion content (#3427)
  (44598880+rasrivas-redhat@users.noreply.github.com)
- fix(Compliance): Find policy correctly when there is one datasteam file
  (#3420) (87209745+marleystipich2@users.noreply.github.com)

* Thu May 26 2022 Sachin Patil <psachin@redhat.com> 3.0.275-1
- feat: New parser ProcKeys for '/proc/keys' file (#3417) (986222045@qq.com)
- feat: New ceph version and enhance (#3422) (xiangceliu@redhat.com)
- feat: Add spec and parser for file '/etc/sysconfig/nfs' (#3419) (xiaoxwan@redhat.com)

* Thu May 19 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.274-1
- Handle the value in kernel-alt pkg (#3415) (psachin@redhat.com)
- feat: RHEL 9.0 is GA (#3416) (xiangceliu@redhat.com)
- fixes: exception with "Reading VG shared_vg1 without a lock" (#3412)
  (44796653+huali027@users.noreply.github.com)
- Add os major version 9 for Compliance (#3413)
  (87209745+marleystipich2@users.noreply.github.com)
- Update CI/CD to include Python 3.9 (#3410)
  (20520336+bfahr@users.noreply.github.com)
- Move tests in code directories to tests dir (#3261)
  (20520336+bfahr@users.noreply.github.com)

* Thu May 12 2022 Sachin Patil <psachin@redhat.com> 3.0.273-1
- feat: RHEL 8.6 is GA (#3409) (xiangceliu@redhat.com)
- Add parser for /proc/self/mountinfo and new combiner mounts (#3398)
  (xiaoxwan@redhat.com)
- fix: Deprecation warnings and removal of collections (#3407)
  (rblakley@redhat.com)
- fixes: the last login time is considered as DB query result (#3404)
  (44796653+huali027@users.noreply.github.com)
- feat: RHICOMPL-2450 implemented OpenSCAP result obfuscation (#3349)
  (skateman@users.noreply.github.com)
- Feat: Add spec and parser for 'nginx_log' (#3402) (rahulxsh@gmail.com)
- Add parser bdi_read_ahead_kb for '/sys/class/bdi/*/read_ahead_kb' files
  (#3391) (xiaoxwan@redhat.com)
- Fix failing malware-detection tests (#3400) (mhuth@redhat.com)

* Thu Apr 28 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.272-1
- Feat: Add spec and parser for 'containers_policy' (#3394)
  (39508521+shlao@users.noreply.github.com)
- Skip malware-detection tests on RHEL6/python2.6 (not supported) (#3382)
  (mhuth@redhat.com)

* Thu Apr 21 2022 Sachin Patil <psachin@redhat.com> 3.0.271-1
- fix: Multiline quote parsing of httpd conf files (#3392) (rblakley@redhat.com)
- feat: Add new crash_kexec_post_notifiers parser (#3387) (986222045@qq.com)
- fix: make sure JSONParser is compatible with RawFileProvider (#3390) (xiangceliu@redhat.com)
- fix: Move _LogRotateConf parser out of combiner (#3389) (rblakley@redhat.com)
- fix: Move the _NginxConf parser out of the combiner (#3386) (rblakley@redhat.com)
- fix: Httpd tracebacks displaying when the client is ran (#3379) (rblakley@redhat.com)
- fix: strip the '\x00' from the ibm_fw_vernum_encoded before parsing (#3378) (xiangceliu@redhat.com)
- Fix spec for YumUpdates parser (#3388) (20520336+bfahr@users.noreply.github.com)
- Only collect "*.conf" for nginx (#3380) (44796653+huali027@users.noreply.github.com)
- fix: Update the spec "du_dirs" to filterable (#3384) (44796653+huali027@users.noreply.github.com)
- fix(client): Return valid machine-id UUID4 object (#3385) (strider@users.noreply.github.com)
- Exclude some Specs from IP address obfuscation (#3331) (stomsa@redhat.com)
* Thu Apr 07 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.270-1
- Replace "cloud.redhat.com" with "console.redhat.com" (#3365)
  (strider@users.noreply.github.com)
- New parser Ql2xmqSupport (#3374) (986222045@qq.com)
- Fix BZ#2071058 (#3375) (psachin@redhat.com)
- fix: correctly obfuscate IP addresses at EOL (#3376)
  (subpop@users.noreply.github.com)
- feat: Add new sos ps spec and fix ValueError caused by it (#3377)
  (rblakley@redhat.com)
- Enhance combiner grub_conf_blscfg (#3370) (jiazhang@redhat.com)
- fix: Update bond and bond_dynamic_lb spec (#3372) (rblakley@redhat.com)

* Thu Mar 31 2022 Sachin Patil <psachin@redhat.com> 3.0.269-1
- fix: Enhance "PCSStatus" to make it compatible with new output format (#3373) (44796653+huali027@users.noreply.github.com)
- Revert "fix: Enhance parser Grub2Config (#3360)" (#3367) (rblakley@redhat.com)
- fix: Fix deprecation warning for using ET.getiterator (#3371) (rblakley@redhat.com)
- Add the line starter for the last release in the CHANGELOG.md file (xiangceliu@redhat.com)
* Thu Mar 24 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.268-1
- fix: Enhance parser Grub2Config (#3360) (jiazhang@redhat.com)
- fix: Switch to reading crontab file rather than run the command (#3359)
  (rblakley@redhat.com)
- status terminated with ok signal when wheter it is registered or not (#3364)
  (93577878+ahitacat@users.noreply.github.com)
- fix: Keep the results once one of them is good (#3357)
  (44796653+huali027@users.noreply.github.com)

* Thu Mar 17 2022 Sachin Patil <psachin@redhat.com> 3.0.267-1
- feat: New parser for /usr/bin/od -An -t d /dev/cpu_dma_latency (#3353) (aghodake@redhat.com)
- feat: New parsers for IBM proc files (#3361) (xiangceliu@redhat.com)
- feat: New spec to get satellite repos with multiple reference (#3362) (44796653+huali027@users.noreply.github.com)
- feat: Add systctl.d spec, parser, and combiner (#3358) (rblakley@redhat.com)
- New parser ktimer_lockless (#3355) (44598880+rasrivas-redhat@users.noreply.github.com)
* Thu Mar 10 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.266-1
- Fix slowness on RHEL 8 by simplifying looping over pkgs (#3354)
  (rblakley@redhat.com)
- feat: New spec and parser to get capsules and repos with contidions (#3352)
  (44796653+huali027@users.noreply.github.com)
- feat: New parser for systemd_perms (#3339) (986222045@qq.com)

* Thu Mar 03 2022 Sachin Patil <psachin@redhat.com> 3.0.265-1
- fix: Fix the regression bug of soscleaner IP obsfuscating (#3347) (xiangceliu@redhat.com)
- Don't log the insights-core egg in verbose mode (BZ 2045995) (#3348) (mhuth@redhat.com)
- Feat: Add spec and parser for 'crictl_logs' (#3345) (39508521+shlao@users.noreply.github.com)
* Thu Feb 24 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.264-1
- New parameters checked when offline is active (#3338)
  (93577878+ahitacat@users.noreply.github.com)
- Fix issue with Markupsafe and Jinja2 versions (#3344)
  (20520336+bfahr@users.noreply.github.com)
- SPM-1379: skip code on RHEL8.4 because of caching bug (#3341)
  (michael.mraka@redhat.com)
- Support downloading malware-detection rules via Satellite (#3337)
  (mhuth@redhat.com)
- Revert satellite version enhancement and Enhance "CapsuleVersion" only
  (#3342) (44796653+huali027@users.noreply.github.com)

* Thu Feb 17 2022 Sachin Patil <psachin@redhat.com> 3.0.263-1
- fix: Enhance combiner "SatelliteVersion" (#3340) (44796653+huali027@users.noreply.github.com)
* Thu Feb 17 2022 Sachin Patil <psachin@redhat.com> 3.0.262-1
- fix: Enhance combiner "SatelliteVersion" and "CapsuleVersion" (#3336) (44796653+huali027@users.noreply.github.com)
- feat: Add thread counts to ps's pid_info dict (#3334) (rblakley@redhat.com)
- New parser for Db2ls (#3332) (xiangceliu@redhat.com)
- 🐛 new message for --group in client (#3333) (93577878+ahitacat@users.noreply.github.com)

* Thu Feb 10 2022 Sachin Patil <psachin@redhat.com> 3.0.261-1
- fix: Enhance hammer_ping parser (#3330) (986222045@qq.com)
- feat: New spec and parser for losetup -l (#3328) (takayuki-nagata@users.noreply.github.com)
- Extended yum updates datasource to work on dnf based systems (#3329) (michael.mraka@redhat.com)
- feat: tell the user the largest file in the archive if the upload is too big (#3059) (gravitypriest@users.noreply.github.com)
* Thu Jan 27 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.260-1
- Feat: Add spec and parser for 'crio.conf' (#3309)
  (39508521+shlao@users.noreply.github.com)
- feat: New spec to get all services which enabled CPUAccounting (#3321)
  (44796653+huali027@users.noreply.github.com)

* Thu Jan 20 2022 Sachin Patil <psachin@redhat.com> 3.0.259-1
- Update spec ls_l first_file (#3326) (jiazhang@redhat.com)
- Update the ChangeLog to include insights-core-3.0.258 (#3325) (psachin@redhat.com)
* Thu Jan 20 2022 Sachin Patil <psachin@redhat.com> 3.0.258-1
- Enhance spec ls_l (#3324) (jiazhang@redhat.com)
- Separate scan_only and scan_exclude options for filesystem and processes (#3312) (mhuth@redhat.com)
- Fix: Update lscpu parser to support RHEL9 output (#3320) (rblakley@redhat.com)
* Thu Jan 13 2022 Xiangce Liu <xiangceliu@redhat.com> 3.0.257-1
- Fix parsing problem in cloud_cfg datasource (#3318)
  (41325380+jobselko@users.noreply.github.com)
- Fix: Update the unitfiles parser for RHEL9 output (#3319)
  (rblakley@redhat.com)
- feat: Add spec and parser for systemctl_status_-all (#3317)
  (39508521+shlao@users.noreply.github.com)
- feat: Switch IniConfigFile from RawConfigParser to parsr's iniparser (#3310)
  (rblakley@redhat.com)
- Playbook revocation list (#3311) (rex.white@gmail.com)

* Thu Jan 06 2022 Sachin Patil <psachin@redhat.com> 3.0.256-1
- Fix: Enhance parser "SatellitePostgreSQLQuery" (#3314) (44796653+huali027@users.noreply.github.com)
- feat: enhance calc_offset to support check all target in line (#3316) (xiangceliu@redhat.com)
- Test IP obfuscation (#3315) (stomsa@redhat.com)
* Thu Dec 16 2021 Xiangce Liu <xiangceliu@redhat.com> 3.0.255-1
- Add spec "foreman_production_log" back. (#3308)
  (44796653+huali027@users.noreply.github.com)
- Enh: Improved excluding of the insights-client log files (#3306)
  (mhuth@redhat.com)
- Feat: New spec to get the httpd certificate expire info stored in NSS…
  (#3303) (44796653+huali027@users.noreply.github.com)

* Thu Dec 09 2021 Sachin Patil <psachin@redhat.com> 3.0.254-1

- Fix: Only get "SSLCertificateFile" when "SSLEngine on" is configured (#3305)
  (44796653+huali027@users.noreply.github.com)
- feat: Add spec and parser for sos_commands/logs/journalctl_--no-pager…
  (#3297) (30404410+qinpingli@users.noreply.github.com)
- feat: New spec to get satelltie empty url repositories (#3299)
  (44796653+huali027@users.noreply.github.com)
- feat: New spec to get the count of satellite tasks with reserved resource
  (#3300) (44796653+huali027@users.noreply.github.com)
- Remove old rules files before starting a new scan (#3302) (mhuth@redhat.com)
- Fix test system (#3294) (93577878+ahitacat@users.noreply.github.com)
- Enhance parser LpstatProtocol (#3301) (jiazhang@redhat.com)
- Add log_response_text flag to log downloads or not in verbose mode (#3298)
  (mhuth@redhat.com)
- Remove yara_binary as a config option (#3296) (mhuth@redhat.com)
* Thu Dec 02 2021 Xiangce Liu <xiangceliu@redhat.com> 3.0.253-1
- DOC: Added new section for client development (#3287)
  (93577878+ahitacat@users.noreply.github.com)
- Update setup.py (#3289) (rblakley@redhat.com)
- Fix: Enhance some spec path (#3293) (jiazhang@redhat.com)
- Update ethtool's parsing logic (#3291) (rblakley@redhat.com)
- Refactor: read metrics from config.ros for pmlog_summary (#3278)
  (xiangceliu@redhat.com)
- Add in IsRhel9 component (#3288) (rblakley@redhat.com)
- fix: update the pmlog_summary to support new metrics (#3290)
  (xiangceliu@redhat.com)

* Thu Nov 18 2021 Sachin Patil <psachin@redhat.com> 3.0.252-1
- Feat: Add Malware app as a manifest spec (#3236) (gravitypriest@users.noreply.github.com)
- adding the missed CHANGELOG (#3286) (xiangceliu@redhat.com)
- Remove unused collect variables (#3284) (stomsa@redhat.com)
* Thu Nov 11 2021 Xiangce Liu <xiangceliu@redhat.com> 3.0.251-1
- Add parser mssql_tls_file (#3283) (jiazhang@redhat.com)
- Add spec "/etc/foreman-installer/scenarios.d/satellite.yaml" (#3280)
  (44796653+huali027@users.noreply.github.com)
- New parser ldap config (#3257) (44598880+rasrivas-
  redhat@users.noreply.github.com)
- Added spec for the getcert_list parser (#3274) (44598880+rasrivas-
  redhat@users.noreply.github.com)
- fix: Correct the order of satellite_custom_hiera in the list of specs (#3282)
  (44796653+huali027@users.noreply.github.com)
- chore: RHEL 8.5 is GA (#3285) (xiangceliu@redhat.com)
- Fix: Strip progress messages from testparm output (#3273) (kgrant@redhat.com)
- Get all SSL certificates for httpd incase different expired date used (#3270)
  (44796653+huali027@users.noreply.github.com)

* Thu Nov 04 2021 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.250-1
- Fix: RHICOMPL-1980 Adding the 'relationships' API attribute to the client
  profiles API call. (#3241) (87209745+marleystipich2@users.noreply.github.com)
- Feat: Spec & parser for 389-ds TLS-related settings. (#3264)
  (jsvoboda@redhat.com)
- fix: check 'tab' in lines of ntp.conf (#3272) (xiangceliu@redhat.com)
- Feat: Spec & parser for nss-rhel7.config (#3269) (jsvoboda@redhat.com)
- Fix: Add raise SkipException to ConfigCombiner for missing main_file (#3277)
  (rblakley@redhat.com)
- Fix: Fix issue in client test due to spec change (#3275)
  (20520336+bfahr@users.noreply.github.com)

* Thu Oct 28 2021 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.249-1
- Feat: Add spec filtering to context_wrap for unit tests (#3265)
  (20520336+bfahr@users.noreply.github.com)
- Fix: Update verification code with an additional fix (#3266)
  (44471274+aleccohan@users.noreply.github.com)
- New nginx spec to get ssl certificate expire data (#3259)
  (44796653+huali027@users.noreply.github.com)
- Enhanced the certificates_enddate spec to support tower cert (#3258)
  (44598880+rasrivas-redhat@users.noreply.github.com)
- fix: Remove old grub specs from client tests (#3263)
  (20520336+bfahr@users.noreply.github.com)

* Thu Oct 21 2021 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.248-1
- Update the default exclude in load_components (#3262) (rblakley@redhat.com)
- [CloudCfg] Include full context in the output (#3249) (psachin@redhat.com)

* Wed Oct 20 2021 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.247-1
- Add new GrubEnv spec and parser (#3244) (rblakley@redhat.com)
- Update _load_component's default exclude (#3252) (rblakley@redhat.com)
- New spec and parser to check httpd ssl certificate expire date (#3212)
  (44796653+huali027@users.noreply.github.com)
- RHCLOUD-16475: Investigate error handling issue found by sat team (#3255)
  (alcohan@redhat.com)

* Wed Oct 13 2021 Vitaliy Dymna <vdymna@redhat.com> 3.0.246-1
- Add parsers and combiners for data from fwupdagent (#3253)
- Add links to recent changes (#3256)
- Automatic commit of package [insights-core] release [3.0.245-1].

* Wed Oct 06 2021 Lloyd Huett <lhuett@redhat.com> 3.0.245-1
- Add doctest to messages parser (#3248) (rblakley@redhat.com)
- Update changelog with recent changes (#3247)
  (20520336+bfahr@users.noreply.github.com)
- Add Spec path of chronyc_sources for sos_archive (roarora@redhat.com)
- Update mdstat parser to remove asserts (#3240) (rblakley@redhat.com)
- Update the nfnetlink parser (#3239) (rblakley@redhat.com)
- Replace assert with parse exception in netstat parser (#3238)
  (rblakley@redhat.com)
- Enhance awx_manage parser (#3242) (44598880+rasrivas-
  redhat@users.noreply.github.com)
- Fixing broken sosreport link (#3243)
  (73747618+gkamathe@users.noreply.github.com)

* Wed Sep 29 2021 Ryan Blakley <rblakley@redhat.com> 3.0.244-1
- Add yum_updates to documentation (#3225) (mhornick@redhat.com)
- Add combiner for ansible information (#3232)
  (20520336+bfahr@users.noreply.github.com)

* Thu Sep 23 2021 Vitaliy Dymna <vdymna@redhat.com> 3.0.243-1
- Add config.ros parser (#3197) (apuntamb@redhat.com)
- Fix bug about some httpd directives may have empty string as attribute
  (#3218) (44796653+huali027@users.noreply.github.com)
- preserve alignment in netstat -neopa output in obfuscation (#3231)
  (gravitypriest@users.noreply.github.com)

* Wed Sep 22 2021 Vitaliy Dymna <vdymna@redhat.com> 3.0.242-1
- [3.0] Update requires in core rpm spec for el7 (#3229) (rblakley@redhat.com)
- Fixed flake8 errors for the newest version of flake8 (#3222)
  (rblakley@redhat.com)
- Update verifier code to remove long suffix python2 (#3227)
  (44471274+aleccohan@users.noreply.github.com)
- Fixed flake8 errors for the newest version of flake8 for the client (#3226)
  (rblakley@redhat.com)
- Stop collection of facter and remove dependencies (#3224)
  (20520336+bfahr@users.noreply.github.com)
- New specs and parsers for scsi_mod, lpfc driver and qla2xxx driver ma…
  (#3221) (30404410+qinpingli@users.noreply.github.com)
- Enhance datasource lpstat (#3219) (jiazhang@redhat.com)

* Wed Sep 15 2021 Bob Fahr <20520336+bfahr@users.noreply.github.com> 3.0.241-1
- Add in missing tito file (#3217) (rblakley@redhat.com)
- Remove old spec ansible_tower_settings (#3216) (jiazhang@redhat.com)
- Enhance parser cups_ppd (#3220) (jiazhang@redhat.com)
- Add custom datasource for collecting yum/dnf updates (#2993)
  (mhornick@redhat.com)
- shell: support running shell in kernel mode (#3144)
  (52785490+amorenoz@users.noreply.github.com)
- Update validation code to fix python2.7 issue (#3214)
  (44471274+aleccohan@users.noreply.github.com)
- Remove the unused datasource specs from default.py (#3207)
  (xiangceliu@redhat.com)
- Add default spec mssql_api_assessment (#3208) (jiazhang@redhat.com)
- Fix excludes not working in _load_components (#3209) (3789184+ryan-
  blakley@users.noreply.github.com)
- Bumping Insights Core version to 3.0.241 (lhuett@redhat.com)

* Wed Sep 01 2021 Ryan Blakley <rblakley@redhat.com> 3.0.240-1
- new package built with tito
