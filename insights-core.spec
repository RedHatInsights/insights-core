Name:           insights-core
Version:        3.0.241
Release:        1%{?dist}
Summary:        Insights Core is a data collection and analysis framework.

License:        ASL 2.0
URL:            https://github.com/RedHatInsights/insights-core
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires: python3
Requires: python3-colorama
Requires: python3-defusedxml
Requires: python3-lockfile
Requires: python3-jinja2
Requires: python3-redis
Requires: python3-requests
Requires: python3-six

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
