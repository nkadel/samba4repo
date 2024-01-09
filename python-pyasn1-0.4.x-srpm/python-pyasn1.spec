%global module pyasn1
%global modules_version 0.2.8

Name:           python-pyasn1
Version:        0.4.8
#Release:        1%%{?dist}
Release:        0.1%{?dist}
Summary:        ASN.1 tools for Python
License:        BSD
Source0:        https://github.com/etingof/pyasn1/archive/v%{version}.tar.gz
Source1:        https://github.com/etingof/pyasn1-modules/archive/v%{modules_version}.tar.gz
URL:            https://github.com/etingof/pyasn1
BuildArch:      noarch

%description
This is an implementation of ASN.1 types and codecs in the Python programming
language.

%package -n python%{python3_pkgversion}-pyasn1
Summary:    ASN.1 tools for Python 3
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools

%description -n python%{python3_pkgversion}-pyasn1
This is an implementation of ASN.1 types and codecs in the Python 3 programming
language.

%package -n python%{python3_pkgversion}-pyasn1-modules
Summary:    Modules for pyasn1
Requires:   python%{python3_pkgversion}-pyasn1 >= 0.4.7, python%{python3_pkgversion}-pyasn1 < 0.6.0

%description -n python%{python3_pkgversion}-pyasn1-modules
ASN.1 types modules for python%{python3_pkgversion}-pyasn1.

%package doc
Summary:        Documentation for pyasn1
BuildRequires:  make
BuildRequires:  python3-sphinx

%description doc
%{summary}.


%prep
%setup -n %{module}-%{version} -q -b1


%build
%py3_build

pushd ../pyasn1-modules-%{modules_version}
%py3_build
popd

pushd docs
PYTHONPATH=%{buildroot}%{python3_sitelib} make SPHINXBUILD=sphinx-build-3 html
popd


%install
%py3_install

pushd ../pyasn1-modules-%{modules_version}
%py3_install
popd


%check
PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} setup.py test


%files -n python%{python3_pkgversion}-pyasn1
%doc README.md
%license LICENSE.rst
%{python3_sitelib}/%{module}
%{python3_sitelib}/%{module}-%{version}-*.egg-info/

%files -n python%{python3_pkgversion}-pyasn1-modules
%{python3_sitelib}/%{module}_modules/
%{python3_sitelib}/%{module}_modules-%{modules_version}-*.egg-info/

%files doc
%license LICENSE.rst
%doc docs/build/html/*

%changelog
* Mon Oct 24 2022 Orion Poplawski <orion@nwra.com> - 0.4.8-1
- Python 3.8 package for EPEL
