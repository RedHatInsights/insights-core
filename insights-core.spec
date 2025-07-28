%define distro redhat
%global debug_package %{nil}
%global modulename insights_core
%global selinux_policy_version 42.1.1
%global selinuxtype targeted

Name:           insights-core
Version:        3.0.8
Release:        1%{?dist}
Summary:        Insights Core is a data collection and analysis framework.

License:        Apache-2.0
URL:            https://github.com/RedHatInsights/insights-core
Source0:        https://github.com/RedHatInsights/insights-core/archive/refs/tags/%{name}-%{version}.tar.gz
%if 0%{?with_selinux}
Source1:        https://github.com/xiangce/insights-core-selinux/archive/refs/tags/%{name}-selinux-%{version}.tar.gz
%endif

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools

Requires: python3
%if 0%{?rhel} == 7
Requires:       python36-CacheControl
Requires:       python36-colorama
Requires:       python36-defusedxml
Requires:       python36-jinja2
Requires:       python36-lockfile
Requires:       python36-PyYAML
Requires:       python36-requests
Requires:       python36-six
%else
%if 0%{?for_internal}
Requires:       python3-CacheControl
Requires:       python3-colorama
Requires:       python3-defusedxml
Requires:       python3-jinja2
Requires:       python3-lockfile
Requires:       python3-redis
%endif
Requires:       python3-pyyaml
Requires:       python3-requests
Requires:       python3-rpm
Requires:       python3-six
%endif

%if 0%{?with_selinux}
Requires:       ((%{name}-selinux == %{version}) if selinux-policy-%{selinuxtype})
%endif

%description
Insights Core is a data collection and analysis framework.

%prep
%if 0%{?with_selinux}
%setup -q -n %{name}-%{version} -a 1
%else
%setup -q -n %{name}-%{version}
%endif

%if 0%{?with_selinux}
%package -n %{name}-selinux
Summary:            Insights Core SELinux policy
License:            Apache-2.0

BuildArch:          noarch
BuildRequires:      selinux-policy-devel

Requires:           selinux-policy >= %{selinux_policy_version}
Requires:           selinux-policy-%{selinuxtype} >= %{selinux_policy_version}
Requires(post):     libselinux-utils
Requires(post):     policycoreutils
Requires(post):     selinux-policy-%{selinuxtype}
Requires(post):     selinux-policy-base >= %{selinux_policy_version}
Requires(postun):   libselinux-utils
Requires(postun):   policycoreutils

%description -n %{name}-selinux
Insights Core Custom SELinux policy module

%pre -n %{name}-selinux
%selinux_relabel_pre -s %{selinuxtype}

%post -n %{name}-selinux
%selinux_modules_install -s %{selinuxtype} %{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.bz2
%selinux_relabel_post -s %{selinuxtype}

%postun -n %{name}-selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s %{selinuxtype} %{modulename}
    %selinux_relabel_post -s %{selinuxtype}
fi

%build -n %{name}-selinux
make -f %{_datadir}/selinux/devel/Makefile %{modulename}.pp
bzip2 -9 %{modulename}.pp
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__python3} setup.py install -O1 --root $RPM_BUILD_ROOT
rm -rf $RPM_BUILD_ROOT/usr/bin

%if 0%{?with_selinux}
install -D -p -m 0644 %{modulename}.pp.bz2 %{buildroot}%{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.bz2
install -D -p -m 0644 %{name}-selinux-%{version}/%{modulename}.if %{buildroot}%{_datadir}/selinux/devel/include/distributed/%{modulename}.if
%endif

%files
# For noarch packages: sitelib
%{python3_sitelib}/*
%license LICENSE

%if 0%{?with_selinux}
%files -n %{name}-selinux
%license LICENSE
%{_datadir}/selinux/packages/%{selinuxtype}/%{modulename}.pp.*
%{_datadir}/selinux/devel/include/distributed/%{modulename}.if
%ghost %verify(not md5 size mode mtime) %{_sharedstatedir}/selinux/%{selinuxtype}/active/modules/200/%{modulename}
%endif

%changelog

