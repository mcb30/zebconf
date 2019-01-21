%global srcname zebconf

Name:		python-%{srcname}
Version:	0.1.3
Release:	1%{?dist}
Summary:	Zebra printer configuration
License:	GPLv2+
URL:		https://github.com/unipartdigital/zebconf
Source0:	%{srcname}-%{version}.tar.gz
BuildArch:	noarch
BuildRequires:	python3-devel
BuildRequires:	python3dist(setuptools)

%description
Zebra printer configuration library and command-line tool.

%package -n	python3-%{srcname}
Summary:	%{summary}
Requires:	python3dist(colorlog)
Requires:	python3dist(passlib)
Requires:	python3dist(pyusb)
Requires:	python3dist(setuptools)

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
Zebra printer configuration library and command-line tool.

%prep
%autosetup -n %{srcname}-%{version}

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
* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.3-1
- Create new release tag using tito

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.2-1
- Initial package.
