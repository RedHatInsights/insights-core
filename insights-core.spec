Name:           insights-core
Version:        3.0.252
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
