%global srcname zebconf

Name:		python-%{srcname}
Version:	0.1.5
Release:	1%{?dist}
Summary:	Zebra printer configuration
License:	GPLv2+
URL:		https://github.com/unipartdigital/zebconf
Source0:	%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python3-devel
BuildRequires:	python3dist(setuptools)

%description
Zebra printer configuration library and command-line tool.

%package -n	python3-%{srcname}
Summary:	%{summary}
Requires:	python3dist(future)
Requires:	python3dist(passlib)
Requires:	python3dist(pyusb)
Requires:	python3dist(setuptools)
Recommends:	python3dist(colorlog)

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
Zebra printer configuration library and command-line tool.

%prep
%autosetup

%build
%py3_build

%install
%py3_install

%files -n python3-%{srcname}
%doc README.md
%license COPYING
%{_bindir}/zebconf
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/%{srcname}-%{version}-*.egg-info/

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