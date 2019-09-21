%if 0%{?fedora}
%global with_python3 0
%endif

Name:           python-testtools
Version:        1.1.0
Release:        1%{?dist}
Summary:        Extensions to the Python unit testing framework

%if 0%{?rhel}
Group:          Development/Tools
%endif
License:        MIT
URL:            https://launchpad.net/testtools
Source0:        http://pypi.python.org/packages/source/t/testtools/testtools-%{version}.tar.gz
Patch0:         testtools-0.9.30-py3.patch

BuildArch:      noarch
BuildRequires:  python2-devel
BuildRequires:  python-extras
BuildRequires:  python-mimeparse >= 0.1.4
BuildRequires:  python-setuptools
%if 0%{?with_python3}
BuildRequires:  python3-devel
BuildRequires:  python3-extras
BuildRequires:  python3-mimeparse
BuildRequires:  python3-setuptools
%endif
BuildRequires:  python-sphinx

Requires:       python-extras
Requires:       python-mimeparse

%description
testtools is a set of extensions to the Python standard library's unit testing
framework.


%if 0%{?with_python3}
%package -n python3-testtools
Summary:        Extensions to the Python unit testing framework

Requires:       python3-extras
Requires:       python3-mimeparse

%description -n python3-testtools
testtools is a set of extensions to the Python standard library's unit testing
framework.

%endif # with_python3


%package        doc
Summary:        Documentation for %{name}
Group:          Documentation

Requires:       %{name} = %{version}-%{release}

# https://fedoraproject.org/wiki/Packaging:No_Bundled_Libraries#Packages_granted_temporary_exceptions
Provides:       bundled(jquery)

%description doc
This package contains HTML documentation for %{name}.


%prep
%setup -q -n testtools-%{version}

%if 0%{?with_python3}
rm -rf %{py3dir}
cp -a . %{py3dir}

# make the Python 3 build load the Python 3.x compatibility library directly
pushd %{py3dir}
%patch0 -p1 -b.py3
popd

find %{py3dir} -name '*.py' | xargs sed -i '1s|^#!python|#!%{__python3}|'
rm %{py3dir}/testtools/_compat2x.py
rm testtools/_compat3x.py
%endif # with_python3


%build
%{__python} setup.py build

%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py build
popd
%endif # with_python3

PYTHONPATH=$PWD make -C doc html


%install
# do python3 install first in case python-testtools ever install scripts in
# _bindir -- the one installed last should be Python 2.x's as that's the
# current default
%if 0%{?with_python3}
pushd %{py3dir}
%{__python3} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
popd
%endif # with_python3

%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT



%check
make PYTHON=%{__python} check

%if 0%{?with_python3}
pushd %{py3dir}
make PYTHON=%{__python3} check
popd
%endif # with_python3


%files
%defattr(-,root,root,-)
%doc NEWS README.rst
%license LICENSE
%{python_sitelib}/*

%if 0%{?with_python3}
%files -n python3-testtools
%doc NEWS README.rst
%license LICENSE
%{python3_sitelib}/*
%endif

%files doc
%defattr(-,root,root,-)
%doc doc/_build/html/*


%changelog
* Fri Sep 19 2014 Jerry James <loganjerry@gmail.com> - 1.1.0-1
- Update to 1.1.0 (bz 1132881)
- Fix license handling
- Note bundling exception for jquery in -doc

* Mon Feb  3 2014 Michel Salim <salimma@fedoraproject.org> - 0.9.35-1
- Update to 0.9.35

* Thu Jul  4 2013 Michel Salim <salimma@fedoraproject.org> - 0.9.32-2
- Add new runtime dep on -extras to Python3 variant as well

* Thu Jul  4 2013 Michel Salim <salimma@fedoraproject.org> - 0.9.32-1
- Update to 0.9.32
- Switch to using split-off extras package

* Sat May 18 2013 Pádraig Brady <pbrady@redhat.com> - 0.9.30-1
- Update to 0.9.30

* Thu Feb 07 2013 Pádraig Brady <pbrady@redhat.com> - 0.9.29-1
- Update to 0.9.29

* Sat Oct 27 2012 Michel Alexandre Salim <michel@sojourner> - 0.9.21-1
- Update to 0.9.21

* Sat Oct 20 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.19-1
- Update to 0.9.19
- On Fedora, also build for Python 3.x

* Wed Sep  5 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.16-1
- Update to 0.9.16
- Remove deprecated sections

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri May 11 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.15-1
- Update to 0.9.15

* Thu Apr  5 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.14-1
- Update to 0.9.14
- Enable unit tests

* Tue Feb  7 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.13-1
- Update to 0.9.13

* Tue Jan 31 2012 Michel Salim <salimma@fedoraproject.org> - 0.9.12-1
- Update to 0.9.12

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jul 15 2011 Michel Salim <salimma@fedoraproject.org> - 0.9.11-1
- Update to 0.9.11
- Enable documentation generation

* Thu Apr  7 2011 Michel Salim <salimma@fedoraproject.org> - 0.9.8-2
- Add definitions needed by older RPM versions

* Thu Apr  7 2011 Michel Salim <salimma@fedoraproject.org> - 0.9.8-1
- Initial package
