%global srcname zebconf

%define with_py2 1
%define with_py3 1
%define with_recommends 1

%if 0%{?rhel}
%define with_py3 0
%define with_recommends 0
%endif

Name:		python-%{srcname}
Version:	0.1.5
Release:	1%{?dist}
Summary:	Zebra printer configuration
License:	GPLv2+
URL:		https://github.com/unipartdigital/zebconf
Source0:	%{name}-%{version}.tar.gz
BuildArch:	noarch
%if 0%{?with_py2}
BuildRequires:	python2-devel
BuildRequires:	python2-setuptools
%endif
%if 0%{?with_py3}
BuildRequires:	python3-devel
BuildRequires:	python3-setuptools
%endif

%description
Zebra printer configuration library and command-line tool.

%if 0%{?with_py2}
%package -n	python2-%{srcname}
Summary:	%{summary}
Requires:	python2-future
Requires:	python2-passlib
%if 0%{?rhel}
Requires:	pyusb
%else
Requires:	python2-pyusb
%endif
Requires:	python2-setuptools
%if 0%{?with_recommends}
Recommends:	python2-colorlog
%endif
%if ! 0%{?with_py3}
Provides:	%{srcname} = %{version}-%{release}
%endif

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
Zebra printer configuration library and command-line tool.
%endif

%if 0%{?with_py3}
%package -n	python3-%{srcname}
Summary:	%{summary}
Requires:	python3-future
Requires:	python3-passlib
Requires:	python3-pyusb
Requires:	python3-setuptools
Recommends:	python3-colorlog
Provides:	%{srcname} = %{version}-%{release}

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
Zebra printer configuration library and command-line tool.
%endif

%prep
%autosetup

%build
%if 0%{?with_py2}
%py2_build
%endif
%if 0%{?with_py3}
%py3_build
%endif

%install
%if 0%{?with_py2}
%py2_install
%endif
%if 0%{?with_py3}
%py3_install
%endif

%if 0%{?with_py2}
%files -n python2-%{srcname}
%doc README.md
%license COPYING
%{python2_sitelib}/%{srcname}/
%{python2_sitelib}/%{srcname}-%{version}-*.egg-info/
%if ! 0%{?with_py3}
%{_bindir}/zebconf
%endif
%endif

%if 0%{?with_py3}
%files -n python3-%{srcname}
%doc README.md
%license COPYING
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/%{srcname}-%{version}-*.egg-info/
%{_bindir}/zebconf
%endif

%changelog
* Wed Jan 23 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.5-1
- zebconf: Support Python 2 alongside Python 3

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.4-1
- rpm: Omit author from RPM changelog messages
- rpm: Fix source tarball name to match tito's expectations

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.3-1
- Create new release tag using tito

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.2-1
- Initial package.
