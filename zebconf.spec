%if %{_vendor} == "debbuild"
%global _buildshell /bin/bash
%endif

%if %{_vendor} == "debbuild"
%global pyinstflags --no-compile -O0
%global pytargetflags --install-layout=deb
%endif

# For systems (mostly debian) that don't define these things -------------------
%{!?__python2:%global __python2 /usr/bin/python2}
%{!?__python3:%global __python3 /usr/bin/python3}

%if %{undefined python2_sitearch}
%global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")
%endif

%if %{undefined python3_sitearch}
%global python3_sitearch %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")
%endif

%{!?py3dir: %global py3dir %{_builddir}/python3-%{name}-%{version}-%{release}}


%global srcname zebconf

%define with_py2 1
%define with_py3 1
%define with_recommends 1

%if 0%{?rhel}
%define with_py3 0
%define with_recommends 0
%endif

Name:		python-%{srcname}
Version:	0.1.8
Release:	1%{?dist}
Summary:	Zebra printer configuration
URL:		https://github.com/unipartdigital/zebconf
Source0:	%{name}-%{version}.tar.gz
BuildArch:	noarch
%if %{_vendor} == "debbuild"
Packager: Mike Perlov <mike.perlov@unipart.io>
License: GPL-2.0
Group: python
%else
License:        GPLv2+
%endif
%if 0%{?with_py2}
%if %{_vendor} == "debbuild"
BuildRequires: python-dev
BuildRequires: python-setuptools
%else
BuildRequires:	python2-devel
BuildRequires:	python2-setuptools
%endif
%endif
%if 0%{?with_py3}
%if %{_vendor} == "debbuild"
BuildRequires: python3-dev
BuildRequires: python3-setuptools
%else
BuildRequires:	python3-devel
BuildRequires:	python3-setuptools
%endif
%endif

%description
Zebra printer configuration library and command-line tool.

%if 0%{?with_py2}
%package -n	python2-%{srcname}
Summary:	%{summary}
%if %{_vendor} == "debbuild"
Requires:       python-future
Requires:       python-passlib
Requires:       python-usb
Requires:       python-setuptools
%else
Requires:	python2-future
Requires:	python2-passlib
%if 0%{?rhel}
Requires:	pyusb
%else
Requires:	python2-pyusb
Requires:	python2-setuptools
%endif
%endif
%if 0%{?with_recommends}
%if %{_vendor} == "debbuild"
Recommends:     python-colorlog
%else
Recommends:	python2-colorlog
%endif
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
Requires:	python3-setuptools
%if %{_vendor} == "debbuild"
Requires:	python3-usb
%else
Requires:	python3-pyusb
%endif
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
%if %{_vendor} == "debbuild"
%{__python2} setup.py build
%else
%py2_build
%endif
%endif
%if 0%{?with_py3}
%if %{_vendor} == "debbuild"
%{__python3} setup.py build
%else
%py3_build
%endif
%endif


%install
%if 0%{?with_py2}
%if %{_vendor} == "debbuild"
%{__python2} setup.py install --root %{buildroot} %{?pytargetflags}
%else
%py2_install
%endif
%endif
%if 0%{?with_py3}
%if %{_vendor} == "debbuild"
%{__python3} setup.py install --root %{buildroot} %{?pytargetflags}
%else
%py3_install
%endif
%endif

%if 0%{?with_py2}
%files -n python2-%{srcname}
%doc README.md
%license COPYING
%if %{_vendor} == "debbuild"
%{python2_sitearch}/%{srcname}/
%{python2_sitearch}/%{srcname}-%{version}-*.egg-info/
%else
%{python2_sitelib}/%{srcname}/
%{python2_sitelib}/%{srcname}-%{version}-*.egg-info/
%endif
%if ! 0%{?with_py3}
%{_bindir}/zebconf
%endif
%endif

%if 0%{?with_py3}
%files -n python3-%{srcname}
%doc README.md
%license COPYING
%if %{_vendor} == "debbuild"
%{python3_sitearch}/%{srcname}/
%{python3_sitearch}/%{srcname}-%{version}*.egg-info/
%else
%{python3_sitelib}/%{srcname}/
%{python3_sitelib}/%{srcname}-%{version}-*.egg-info/
%endif
%{_bindir}/zebconf
%endif

%changelog
* Wed Feb 20 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.8-1
- zebconf: Fix use of "zebconf set" for Python 2.7

* Tue Feb 19 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.7-1
- zebconf: Apply timeout when opening network connections

* Fri Jan 25 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.6-1
- rpm: Support building for EPEL as well as Fedora
- rpm: Build both Python 2 and Python 3 RPMs
- zebconf: Make colorlog an optional dependency

* Wed Jan 23 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.5-1
- zebconf: Support Python 2 alongside Python 3

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.4-1
- rpm: Omit author from RPM changelog messages
- rpm: Fix source tarball name to match tito's expectations

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.3-1
- Create new release tag using tito

* Mon Jan 21 2019 Michael Brown <mbrown@fensystems.co.uk> 0.1.2-1
- Initial package.
