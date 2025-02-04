%bcond_without python3

%global modname nose

# Enable building without docs to avoid a circular dependency between this and python-sphinx
#
# Docs disabled permanently because the docs build config is not ported to
# Python 3 and thus cannot be built with Python 3 version of Sphinx.
%bcond_with docs

%global desc nose extends the test loading and running features of unit test, making\
it easier to write, find and run tests.\
\
By default, nose will run tests in files or directories under the\
current working directory whose names include "test" or "Test" at a\
word boundary (like "test_this" or "functional_test" or "TestClass"\
but not "libtest"). Test output is similar to that of unit test, but\
also includes captured stdout output from failing tests, for easy\
print-style debugging.\
\
These features, and many more, are customizable through the use of\
plugins. Plugins included with nose provide support for doctest, code\
coverage and profiling, flexible attribute-based test selection,\
output capture and more.\


Name:           python-%{modname}
Version:        1.3.7
#Release:        31%%{?dist}
Release:        0.31%{?dist}
BuildArch:      noarch

License:        LGPLv2+ and Public Domain
Summary:        Discovery-based unit test extension for Python
URL:            https://nose.readthedocs.org/en/latest/
Source0:        https://pypi.python.org/packages/source/n/nose/nose-%{version}.tar.gz
# Make compatible with coverage 4.1
# https://github.com/nose-devs/nose/pull/1004
##Patch0:         python-nose-coverage4.patch
# Fix python 3.5 compat
# https://github.com/nose-devs/nose/pull/983
##Patch1:         python-nose-py35.patch
# Fix UnicodeDecodeError with captured output
# https://github.com/nose-devs/nose/pull/988
##Patch2:         python-nose-unicode.patch
# Allow docutils to read utf-8 source
##Patch3:         python-nose-readunicode.patch
# Fix Python 3.6 compatibility
# Python now returns ModuleNotFoundError instead of the previous ImportError
# https://github.com/nose-devs/nose/pull/1029
##Patch4:         python-nose-py36.patch

BuildRequires:  dos2unix

%description
%{desc}

%package docs
Summary:        Nose Documentation
%if %{with docs}
BuildRequires:  %{_bindir}/sphinx-build-%{?python3_pkgverson}
%endif

%description docs
Documentation for Nose.

%package -n python%{python3_pkgversion}-%{modname}
Summary:        %{summary}
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-coverage >= 3.4-1

# Require alternatives version that implements the --keep-foreign flag
Requires(postun): alternatives >= 1.19.1-1
# For alternatives
Requires:       python%{python3_pkgversion}
Requires:       python%{python3_pkgversion}-setuptools

%description -n python%{python3_pkgversion}-%{modname}
%{desc}

This package installs the nose module and nosetests3 program that can discover
python3 unit tests.

%prep
%setup -qc
pushd %{modname}-%{version}
%autopatch -p1
dos2unix examples/attrib_plugin.py
cp -pr lgpl.txt AUTHORS CHANGELOG examples NEWS README.txt ..
popd

mv %{modname}-%{version} python3

%build
pushd python3
%py3_build
popd

%install
mkdir -p %{buildroot}%{_mandir}/man1

pushd python3
%py3_install
mv %{buildroot}%{_bindir}/nosetests{,-%{python3_version}}
touch %{buildroot}%{_bindir}/nosetests-3 # for alternatives
mv %{buildroot}%{_prefix}/man/man1/nosetests.1 %{buildroot}%{_mandir}/man1/nosetests-%{python3_version}.1
touch %{buildroot}%{_mandir}/man1/nosetests-3.1 # for alternatives
popd

%if %{with docs}
pushd python3/doc
  sphinx-build-${python3_pkgversion} -b html -d .build/doctrees . .build/html
  rm -vrf .build/html/.buildinfo .build/html/_sources
  mv .build/html ../..
  rm -vrf .build
popd
%endif
cp -a python3/doc reST
rm -vrf reST/{.static,.templates}

# Disable checks until further notice <nkadel@gmail.com>
#%check
#pushd python3
#%{__python3} setup.py build_tests
#%{__python3} selftest.py
#popd

%post -n python%{python3_pkgversion}-%{modname}
alternatives --add-slave python3 %{_bindir}/python%{python3_version} \
    %{_bindir}/nosetests-3 \
    nosetests-3 \
    %{_bindir}/nosetests-%{python3_version}

alternatives --add-slave python3 %{_bindir}/python%{python3_version} \
    %{_mandir}/man1/nosetests-3.1.gz \
    nosetests-3-man \
    %{_mandir}/man1/nosetests-%{python3_version}.1.gz

%postun -n python%{python3_pkgversion}-%{modname}
if [ $1 -eq 0 ]; then
  alternatives --keep-foreign --remove-slave python3 \
      %{_bindir}/python%{python3_version} nosetests-3

  alternatives --keep-foreign --remove-slave python3 \
      %{_bindir}/python%{python3_version} nosetests-3-man
fi

%files -n python%{python3_pkgversion}-%{modname}
%license lgpl.txt
%ghost %{_bindir}/nosetests-3
%{_bindir}/nosetests-%{python3_version}
%ghost %{_mandir}/man1/nosetests-3.1*
%{_mandir}/man1/nosetests-%{python3_version}.1*
%{python3_sitelib}/nose-*.egg-info/
%{python3_sitelib}/nose/

%files docs
%license lgpl.txt
%doc AUTHORS CHANGELOG examples NEWS README.txt
%if %{with docs}
%doc html reST
%endif  # with docs

%changelog
* Fri Jul 30 2021 Tomas Orsava <torsava@redhat.com> - 1.3.7-31
- Adjusted the postun scriptlets to enable upgrading to RHEL 9
- Resolves: rhbz#1933055

* Thu Apr 25 2019 Tomas Orsava <torsava@redhat.com> - 1.3.7-30
- Bumping due to problems with modular RPM upgrade path
- Resolves: rhbz#1695587

* Thu Oct 04 2018 Lumír Balhar <lbalhar@redhat.com> - 1.3.7-29
- Fix alternatives - post and postun sections only with python3
- Resolves: rhbz#1633534

* Tue Oct 02 2018 Lumír Balhar <lbalhar@redhat.com> - 1.3.7-28
- Add alternatives for the executable and manpage
- Resolves: rhbz#1633534

* Wed Aug 15 2018 Lumír Balhar <lbalhar@redhat.com> - 1.3.7-27
- Remove nosetest-3 executable/manpage. This will be provided by python3 module.
- Resolves: rhbz#1615727

* Wed Aug 08 2018 Lumír Balhar <lbalhar@redhat.com> - 1.3.7-26
- Remove unversioned binaries from python2 subpackage
- Resolves: rhbz#1613343

* Tue Jul 31 2018 Lumír Balhar <lbalhar@redhat.com> - 1.3.7-25
- Make possible to disable python3 subpackage

* Wed Jul 18 2018 Tomas Orsava <torsava@redhat.com> - 1.3.7-24
- BuildRequire also python36-rpm-macros as part of the python36 module build

* Wed Jul 04 2018 Miro Hrončok <mhroncok@redhat.com> - 1.3.7-23
- Add a bcond for python2
- Build docs with python3 explicitly

* Tue Jun 26 2018 Tomas Orsava <torsava@redhat.com> - 1.3.7-22
- Use python2 macros instead of unversioned python macros

* Mon Jun 18 2018 Tomas Orsava <torsava@redhat.com> - 1.3.7-21
- Disabled docs because the docs build config is not ported to Python 3 and
  thus cannot be built with Python 3 version of Sphinx

* Mon Apr 30 2018 Tomas Orsava <torsava@redhat.com> - 1.3.7-20
- Require the python36-devel package when building for the python36 module

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.7-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Nov 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.3.7-18
- Use better Obsoletes for platform-python

* Sat Nov 04 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.3.7-17
- Remove platform-python subpackage
- Cleanup spec

* Fri Sep 29 2017 Troy Dawson <tdawson@redhat.com> - 1.3.7-16
- Cleanup spec file conditionals

* Thu Aug 10 2017 Miro Hrončok <mhroncok@redhat.com> - 1.3.7-15
- Add platform-python subpackage

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.7-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.7-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Dec 12 2016 Tomas Orsava <torsava@redhat.com> - 1.3.7-12
- Patched to fix compatibility with Python 3.6

* Mon Dec 05 2016 Randy Barlow <bowlofeggs@fedoraproject.org> - 1.3.7-11
- Provide nosetests-3 (#1289820).
- Rename python-nose to python2-nose and use Python provides macro.
- Include the license with the -docs subpackage.
- Use symlinks to provide man pages for all the Python version variants of /usr/bin/nosetests.
- The -docs subpackage no longer requires python-nose since that doesn't make sense.

* Tue Nov 15 2016 Orion Poplawski <orion@cora.nwra.com> 1.3.7-10
- Add upstream patch to fix python 3.5 compat
- Add patch to allow docutils to read unicode source
- Update spec

* Wed Nov 9 2016 Orion Poplawski <orion@cora.nwra.com> 1.3.7-9
- Add patch to fix build with coverage 4.1

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.7-8
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Feb 2 2016 Orion Poplawski <orion@cora.nwra.com> 1.3.7-7
- Fix URL

* Thu Sep 24 2015 Robert Kuska <rkuska@redhat.com> 1.3.7-6
- Rebuilt for Python3.5 rebuild with disabled tests under python3

* Sun Aug 09 2015 Kevin Fenzi <kevin@scrye.com> 1.3.7-5
- Add conditional for python-sphinx buildrequires when with_docs is not set. 
- Fixes bug #1251700

* Fri Jul 24 2015 Kevin Fenzi <kevin@scrye.com> 1.3.7-4
- Version provides correctly for python2-nose.

* Fri Jul 17 2015 Kevin Fenzi <kevin@scrye.com> 1.3.7-3
- Add provides for python2-nose. Fixes bug #1241670

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 03 2015 Kevin Fenzi <kevin@scrye.com> 1.3.7-1
- Update to 1.3.7 (#1227345)

* Sat Apr 04 2015 Ralph Bean <rbean@redhat.com> - 1.3.6-1
- new version

* Wed Aug 27 2014 Luke Macken <lmacken@redhat.com> - 1.3.4-1
- Update to 1.3.4 (#1094718)

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon May 19 2014 Bohuslav Kabrda <bkabrda@redhat.com> - 1.3.2-2
- Add patch for issue https://github.com/nose-devs/nose/pull/811,
which makes tests of python-billiard and python-falcon fail with Python 3.4

* Sat May 03 2014 Orion Poplawski <orion@cora.nwra.com> - 1.3.2-1
- Update to 1.3.2 for Python 3.4 suport

* Fri May 02 2014 Orion Poplawski <orion@cora.nwra.com> - 1.3.1-2
- Rebuild for Python 3.4

* Fri Mar 14 2014 Luke Macken <lmacken@redhat.com> - 1.3.1-1
- Update to 1.3.1 (#1074971)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Apr  9 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.3.0-1
- Update to 1.3.0 upstream with python-3.3 fixes

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Sep 12 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 1.2.1-1
- New upsream 1.2.1 that just bumps the version properly

* Mon Sep 10 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 1.2.0-1
- Update to nose-1.2.0.
- Two less python3 test failures than 1.1.2

* Sat Aug  4 2012 David Malcolm <dmalcolm@redhat.com> - 1.1.2-5
- rebuild for https://fedoraproject.org/wiki/Features/Python_3.3
- disable selftests that fail under 3.3

* Fri Aug  3 2012 David Malcolm <dmalcolm@redhat.com> - 1.1.2-4
- remove rhel logic from with_python3 conditional

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Mon Aug 1 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.1.2-1
- Upstream bugfix release

* Wed Jul 27 2011 Toshio Kuratomi <toshio@fedoraproject.org> - 1.1.1-1
- Upstream bugfix release

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Dec 26 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0
- Create the docs subpackage for text docs even if we don't create the html docs.
- Make python3 subpackage

* Tue Dec 7 2010 Toshio Kuratomi <toshio@fedoraproject.org> - 0.11.4-2
- Fix FTBFS with newer coverage

* Thu Oct 21 2010 Luke Macken <lmacken@redhat.com> - 0.11.4-1
- Update to 0.11.4 (#3630722)

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.11.3-5
- add support for building without docs, to avoid a circular build-time
dependency between this and python-sphinx; disable docs subpackage for now
- add (apparently) missing BR on python-coverage (appears to be needed
for %%check)
- cherrypick upstream compatibility fixes for 2.7

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.11.3-4
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Thu May 20 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-3
- Update URL to http://code.google.com/p/python-nose/
- Align description to reflect that in setup.py
- Create a docs subpackage containing HTML & reST documentation
- Thanks to Gareth Armstrong at HP for the patch

* Thu May 06 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-2
- Don't hardcode the python version

* Thu May 06 2010 Luke Macken <lmacken@redhat.com> - 0.11.3-1
- Update to 0.11.3
- Enable the self tests

* Mon Oct 05 2009 Luke Macken <lmacken@redhat.com> - 0.11.1-2
- Include the new nosetests-2.6 script as well

* Mon Oct 05 2009 Luke Macken <lmacken@redhat.com> - 0.11.1-1
- Update to 0.11.1

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.4-1
- Update to 0.10.4 to fix 2.6 issues

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.10.3-2
- Rebuild for Python 2.6

* Sat Aug 02 2008 Luke Macken <lmacken@redhat.com> 0.10.3-1
- Update to 0.10.3

* Thu Feb 28 2008 Luke Macken <lmacken@redhat.com> 0.10.1-1
- Update to 0.10.1

* Mon Dec  3 2007 Luke Macken <lmacken@redhat.com> 0.10.0-2
- Add python-setuptools to Requires (Bug #408491)

* Tue Nov 27 2007 Luke Macken <lmacken@redhat.com> 0.10.0-1
- 0.10.0

* Sun Sep  2 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.3.b1
- Update for python-setuptools changes in rawhide

* Tue Aug 21 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.2.b1
- 0.10.0b1
- Update license tag to LGPLv2

* Wed Jun 20 2007 Luke Macken <lmacken@redhat.com> 0.10.0-0.1.a2
- 0.10.0a2

* Sat Jun  2 2007 Luke Macken <lmacken@redhat.com> 0.9.3-1
- Latest upstream release
- Remove python-nose-0.9.2-mandir.patch

* Sat Mar  3 2007 Luke Macken <lmacken@redhat.com> 0.9.2-1
- Add nosetests(1) manpage, and python-nose-0.9.2-mandir.patch to put it in
  the correct location.
- 0.9.2

* Sat Dec  9 2006 Luke Macken <lmacken@redhat.com> 0.9.1-2
- Rebuild for python 2.5

* Fri Nov 24 2006 Luke Macken <lmacken@redhat.com> 0.9.1-1
- 0.9.1

* Fri Sep  8 2006 Luke Macken <lmacken@redhat.com> 0.9.0-1
- 0.9.0

* Wed Apr 19 2006 Ignacio Vazquez-Abrams <ivazquez@ivazquez.net> 0.8.7.2-1
- Initial RPM release
