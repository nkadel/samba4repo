%if 0%{?el8}
# Disable annobin plugin on el8 (unusable with gcc-toolset-12)
%undefine _annotated_build
%endif

Name:		mold
Version:	1.11.0
Release:	1%{?dist}
Summary:	A Modern Linker

License:	AGPL-3.0-or-later AND (Apache-2.0 OR MIT)
URL:		https://github.com/rui314/mold
Source0:	%{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# The bundled build system for tbb tries to strip all Werror from the
# CFLAGS/CXXFLAGS when not building in strict mode (mold doesn't use strict
# mode). We don't want that because it causes the "Werror=format-security"
# option to become "=format-security" and break the build. (similar to a patch
# in the Fedora tbb package)
Patch0:		tbb-strip-werror.patch

# Allow building against the system-provided `xxhash.h`
Patch1:		0001-Use-system-compatible-include-path-for-xxhash.h.patch

# mold currently cannot produce native binaries for MIPS
ExcludeArch:	%{mips}

BuildRequires:	cmake
%if 0%{?el8}
BuildRequires:	gcc-toolset-12
%else
BuildRequires:	gcc
BuildRequires:	gcc-c++ >= 10
%endif
BuildRequires:	libzstd-devel
BuildRequires:	mimalloc-devel
BuildRequires:	openssl-devel
BuildRequires:	xxhash-devel
BuildRequires:	zlib-devel

# Required by bundled oneTBB
BuildRequires:	hwloc-devel

# The following packages are only required for executing the tests
BuildRequires:	clang
BuildRequires:	gdb
BuildRequires:	glibc-static
%if ! 0%{?el8}
%ifarch x86_64
BuildRequires:	glibc-devel
%endif
BuildRequires:	libdwarf-tools
%endif
BuildRequires:	libstdc++-static
BuildRequires:	llvm

Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives

# API-incompatible with older tbb 2020.3 currently shipped by Fedora:
# https://bugzilla.redhat.com/show_bug.cgi?id=2036372
Provides:	bundled(tbb) = 2021.7

%description
mold is a faster drop-in replacement for existing Unix linkers.
It is several times faster than the LLVM lld linker.
mold is designed to increase developer productivity by reducing
build time, especially in rapid debug-edit-rebuild cycles.

%prep
%autosetup -p1
rm -r third-party/{mimalloc,xxhash,zlib,zstd}

%build
%if 0%{?el8}
. /opt/rh/gcc-toolset-12/enable
%endif
%cmake -DMOLD_USE_SYSTEM_MIMALLOC=ON
%cmake_build

%install
%cmake_install

%post
if [ "$1" = 1 ]; then
  %{_sbindir}/alternatives --install %{_bindir}/ld ld %{_bindir}/ld.mold 1
fi

%postun
if [ "$1" = 0 ]; then
  %{_sbindir}/alternatives --remove ld %{_bindir}/ld.mold
fi

%check
%if 0%{?el8}
. /opt/rh/gcc-toolset-12/enable
%endif
%ctest

%files
%license %{_docdir}/mold/LICENSE
%ghost %{_bindir}/ld
%{_bindir}/mold
%{_bindir}/ld.mold
%{_libdir}/mold/mold-wrapper.so
%{_libexecdir}/mold/ld
%{_mandir}/man1/ld.mold.1*
%{_mandir}/man1/mold.1*

%changelog
* Thu Mar 16 2023 Christoph Erhardt <fedora@sicherha.de> - 1.11.0-1
- Bump version to 1.11.0
- Update version number of bundled tbb package to 2021.7

* Sat Jan 21 2023 Christoph Erhardt <fedora@sicherha.de> - 1.10.0-1
- Bump version to 1.10.0
- Refresh patch

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Fri Jan 06 2023 Christoph Erhardt <fedora@sicherha.de> - 1.9.0-1
- Bump version to 1.9.0
- Don't enforce out-of-source build since the `inttypes.h` collision is resolved

* Mon Dec 26 2022 Christoph Erhardt <fedora@sicherha.de> - 1.8.0-1
- Bump version to 1.8.0
- Drop upstreamed patch
- Refresh patch

* Sat Nov 19 2022 Christoph Erhardt <fedora@sicherha.de> - 1.7.1-1
- Bump version to 1.7.1

* Fri Nov 18 2022 Christoph Erhardt <fedora@sicherha.de> - 1.7.0-1
- Bump version to 1.7.0
- Drop upstreamed patches
- Move from `ExclusiveArch` to `ExcludeArch` as only MIPS remains unsupported
- Build with GCC 12 on el8

* Sat Oct 22 2022 Christoph Erhardt <fedora@sicherha.de> - 1.6.0-1
- Bump version to 1.6.0
- Add new supported architectures
- Drop upstreamed patch

* Thu Sep 29 2022 Christoph Erhardt <fedora@sicherha.de> - 1.5.1-1
- Bump version to 1.5.1 (#2130132)
- Switch to CMake build
- Remove obsolete dependencies
- Add new supported architectures
- Refresh patch

* Sun Sep 04 2022 Christoph Erhardt <fedora@sicherha.de> - 1.4.2-1
- Bump version to 1.4.2
- Refresh patch

* Thu Aug 18 2022 Christoph Erhardt <fedora@sicherha.de> - 1.4.1-1
- Bump version to 1.4.1 (#2119324)
- Refresh patch
- Remove superfluous directory entries from `%%files`

* Sun Aug 07 2022 Christoph Erhardt <fedora@sicherha.de> - 1.4.0-1
- Bump version to 1.4.0 (#2116004)
- Refresh patch
- Use SPDX notation for `License:` field

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.3.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Sun Jul 03 2022 Christoph Erhardt <fedora@sicherha.de> - 1.3.1-1
- Bump version to 1.3.1 (#2103365)

* Sat Jun 18 2022 Christoph Erhardt <fedora@sicherha.de> - 1.3.0-1
- Bump version to 1.3.0 (#2098316)
- Drop upstreamed patches

* Sat Apr 30 2022 Christoph Erhardt <fedora@sicherha.de> - 1.2.1-1
- Bump version to 1.2.1
- Drop upstreamed patch
- Add support for 32-bit x86 and Arm

* Sat Apr 16 2022 Christoph Erhardt <fedora@sicherha.de> - 1.2-1
- Bump version to 1.2
- Drop upstreamed patches
- Set correct version of bundled tbb
- Suppress 'comparison between signed and unsigned' warnings

* Tue Mar 08 2022 Christoph Erhardt <fedora@sicherha.de> - 1.1.1-1
- Bump version to 1.1.1

* Mon Feb 21 2022 Christoph Erhardt <fedora@sicherha.de> - 1.1-1
- Bump version to 1.1
- Drop upstreamed patches
- Update description

* Thu Feb 17 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.2-2
- Rebuild due to mimalloc soname change

* Sun Jan 23 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.2-1
- Bump version to 1.0.2.

* Sat Jan 01 2022 Christoph Erhardt <fedora@sicherha.de> - 1.0.1-1
- Initial package for version 1.0.1.
