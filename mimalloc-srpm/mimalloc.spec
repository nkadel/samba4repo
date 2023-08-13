%undefine __cmake_in_source_build

Name:           mimalloc
Version:        2.0.9
#Release:        2$%{?dist}
Release:        0.2%{?dist}
Summary:        A general purpose allocator with excellent performance

License:        MIT
URL:            https://github.com/microsoft/mimalloc
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++

%description
mimalloc (pronounced "me-malloc")
is a general purpose allocator with excellent performance characteristics.
Initially developed by Daan Leijen for the run-time systems.

%package devel
Summary:        Development environment for %name
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development package for mimalloc.

%prep
%autosetup -p1
# Remove unneded binary from sources
rm -rf bin


%build
%cmake \
    -DMI_BUILD_OBJECT=OFF \
    -DMI_OVERRIDE=OFF \
    -DMI_INSTALL_TOPLEVEL=ON \
    -DMI_BUILD_STATIC=OFF \
    -DMI_BUILD_TESTS=OFF \
    -DCMAKE_BUILD_TYPE=Release
%cmake_build


%install
%cmake_install


%files
%license LICENSE
%doc readme.md
%{_libdir}/lib%{name}.so.*

%files devel
%{_libdir}/lib%{name}.so
%{_libdir}/cmake/%{name}/
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/*


%changelog
* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Wed Dec 28 2022 Vasiliy Glazov <vascom2@gmail.com> - 2.0.9-1
- Update to 2.0.9

* Mon Nov 14 2022 Vasiliy Glazov <vascom2@gmail.com> - 2.0.7-1
- Update to 2.0.7

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Fri Apr 15 2022 Vasiliy Glazov <vascom2@gmail.com> - 2.0.6-1
- Update to 2.0.6

* Tue Feb 15 2022 Vasiliy Glazov <vascom2@gmail.com> - 2.0.5-1
- Update to 2.0.5

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Nov 15 2021 Vasiliy Glazov <vascom2@gmail.com> - 2.0.3-1
- Update to 2.0.3

* Wed Sep 29 2021 Vasiliy Glazov <vascom2@gmail.com> - 2.0.2-2
- Clean spec to follow packaging guidelines

* Wed Sep 29 2021 Vasiliy Glazov <vascom2@gmail.com> - 2.0.2-1
- Initial packaging for Fedora
