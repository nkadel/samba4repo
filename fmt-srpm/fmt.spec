%undefine __cmake_in_source_build

Name:           fmt
Version:        8.1.1
#Release:        5%{?dist}
Release:        0.5%{?dist}

License:        BSD
Summary:        Small, safe and fast formatting library for C++
URL:            https://github.com/fmtlib/%{name}
Source0:        %{url}/archive/%{version}.tar.gz

# fix for https://github.com/fmtlib/fmt/issues/2717
Patch100:       %{name}-fix_implicit_ptr_conv.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  ninja-build

# This package replaces the old name of cppformat
Provides:       cppformat = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      cppformat < %{?epoch:%{epoch}:}%{version}-%{release}

%description
C++ Format is an open-source formatting library for C++. It can be used as a
safe alternative to printf or as a fast alternative to IOStreams.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{?epoch:%{epoch}:}%{version}-%{release}

# This package replaces the old name of cppformat
Provides:       cppformat-devel = %{?epoch:%{epoch}:}%{version}-%{release}
Obsoletes:      cppformat-devel < %{?epoch:%{epoch}:}%{version}-%{release}

%description    devel
This package contains the header file for using %{name}.

%prep
%autosetup -p1

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DCMAKE_POSITION_INDEPENDENT_CODE:BOOL=ON \
    -DFMT_CMAKE_DIR:STRING=%{_libdir}/cmake/%{name} \
    -DFMT_LIB_DIR:STRING=%{_libdir}
%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE.rst
%doc ChangeLog.rst README.rst
%{_libdir}/lib%{name}.so.8*

%files devel
%{_includedir}/%{name}
%{_libdir}/lib%{name}.so
%{_libdir}/cmake/%{name}
%{_libdir}/pkgconfig/%{name}.pc

%changelog
* Wed Mar 02 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 8.1.1-5
- Removed obsolete macros.

* Tue Mar 01 2022 Michel Alexandre Salim <salimma@fedoraproject.org> - 8.1.1-4
- Backport fix handling of formattable types implicitly convertible to pointers (fixes: rhbz#2059736)

* Thu Jan 27 2022 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 8.1.1-3
- Rebuild with new annobin (rhbz#2046232)

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 8.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Jan 07 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 8.1.1-1
- Updated to version 8.1.1.

* Wed Jan 05 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 8.1.0-2
- Updated Big Endian patch.
- Added ABI fix patch.

* Tue Jan 04 2022 Vitaly Zaitsev <vitaly@easycoding.org> - 8.1.0-1
- Updated to version 8.1.0.

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 8.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Sun Jul 04 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 8.0.1-1
- Updated to version 8.0.1.

* Mon May 03 2021 Vitaly Zaitsev <vitaly@easycoding.org> - 7.1.3-3
- Fixed RHBZ#1956521.

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 7.1.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sun Nov 29 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 7.1.3-1
- Updated to version 7.1.3.

* Tue Nov 10 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 7.1.2-1
- Updated to version 7.1.2.

* Sat Aug 08 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 7.0.3-1
- Updated to version 7.0.3.

* Wed Jul 29 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 7.0.2-1
- Updated to version 7.0.2.

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 7.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 08 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 7.0.1-1
- Updated to version 7.0.1.

* Sat May 09 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 6.2.1-1
- Updated to version 6.2.1.

* Thu Apr 30 2020 Kefu Chai <tchaikov@gmail.com> - 6.2.0-2
- Incorporate patch from upstream to address https://github.com/fmtlib/fmt/issues/1631

* Mon Apr 06 2020 Vitaly Zaitsev <vitaly@easycoding.org> - 6.2.0-1
- Updated to version 6.2.0.

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 6.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Dec 18 2019 Vitaly Zaitsev <vitaly@easycoding.org> - 6.1.2-1
- Updated to version 6.1.2.
- Recreated all documentation patches.
- SPEC file cleanup.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jun 10 2019 Jan Staněk <jstanek@redhat.com> - 5.3.0-1
- Update to 5.3.0
- Recreate documentation build patches
- Package new pkg-config files

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Oct 11 2018 Kefu Chai <tchaikov@gmail.com> - 5.2.1-1
- Update to 5.2.1
- Build using python3 packages on fedora
- Remove links in document accessing network
- Package ChangeLog.rst and README.rst
- Drop fmt-static package

* Fri Aug 31 2018 Leigh Scott <leigh123linux@googlemail.com> - 3.0.2-7
- Fix python2 issue for doc

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 09 2017 Dave Johansen <davejohansen@gmail.com> - 3.0.2-4
- Patch for Test 8 segfault

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jun 24 2017 Dave Johansen <davejohansen@gmail.com> - 3.0.2-1
- Upstream release

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Tue Dec 27 2016 Dave Johansen <davejohansen@gmail.com> - 3.0.1-2
- Build documentation

* Fri Nov 25 2016 Dave Johansen <davejohansen@gmail.com> - 3.0.1-1
- Upstream release

* Tue Nov 15 2016 Dave Johansen <davejohansen@gmail.com> - 3.0.0-2
- Fix expected unqualified-id before numeric constant error

* Wed Aug 24 2016 Dave Johansen <davejohansen@gmail.com> - 3.0.0-1
- Initial RPM release
