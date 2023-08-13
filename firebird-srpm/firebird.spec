%global         upversion 4.0.0.2496
%global         pkgversion Firebird-%{upversion}-0

%global         major 4.0
%global         _hardened_build 1
# firebird is mis-compiled when LTO is enabled. A root
# cause analysis has not yet been completed. Reported upstream.
# Disable LTO for now
%global         _lto_cflags %nil

Name:           firebird
Version:        %{upversion}
#Release:        2%%{?dist}
Release:        0.2%{?dist}

Summary:        SQL relational database management system
License:        Interbase
URL:            http://www.firebirdsql.org/

Source0:        https://github.com/FirebirdSQL/firebird/releases/download/v4.0.0/%{pkgversion}.tar.xz
Source1:        firebird-logrotate
Source2:        README.Fedora
Source3:        firebird.service
Source4:        fb_config

# from OpenSuse
Patch101:       add-pkgconfig-files.patch

# from Debian to be sent upstream
Patch203:       no-copy-from-icu.patch
Patch205:       cloop-honour-build-flags.patch

# from upstream
Patch303:       fix_build_on_big_endian_platforms.patch
Patch304:       ttmath-abseil.4.0.0.patch

BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtommath-devel
BuildRequires: libtool
BuildRequires: ncurses-devel
BuildRequires: libicu-devel
BuildRequires: libedit-devel
BuildRequires: gcc-c++
BuildRequires: libstdc++-static
BuildRequires: systemd-units
BuildRequires: chrpath
BuildRequires: zlib-devel
BuildRequires: procmail
BuildRequires: make
BuildRequires: libtomcrypt-devel
BuildRequires: unzip
BuildRequires: sed

Requires(postun): /usr/sbin/userdel
Requires(postun): /usr/sbin/groupdel
Requires(pre):    /usr/sbin/groupadd
Requires(pre):    /usr/sbin/useradd
Requires(post):   systemd-units
Requires(preun):  systemd-units
Requires(postun): systemd-units
Requires:       logrotate
Requires:       libfbclient2 = %{version}-%{release}
Requires:       libib-util = %{version}-%{release}
Requires:       %{name}-utils = %{version}-%{release}

Obsoletes:      firebird-arch < 4.0
Obsoletes:      firebird-filesystem < 4.0
Obsoletes:      firebird-classic-common < 4.0
Obsoletes:      firebird-classic < 4.0
Obsoletes:      firebird-superclassic < 4.0
Obsoletes:      firebird-superserver < 4.0
Conflicts:      firebird-arch < 4.0
Conflicts:      firebird-filesystem < 4.0
Conflicts:      firebird-classic-common < 4.0
Conflicts:      firebird-classic < 4.0
Conflicts:      firebird-superclassic < 4.0
Conflicts:      firebird-superserver < 4.0


%description
Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package devel
Requires:       %{name} = %{version}-%{release}
Requires:       libfbclient2-devel = %{version}-%{release}
Summary:        UDF support library for Firebird SQL server

%description devel
This package is needed for development of client applications and user
defined functions (UDF) for Firebird SQL server.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package -n libib-util
Summary:        Firebird SQL UDF support library

%description -n libib-util
libib_util contains utility functions used by
User-Defined Functions (UDF) for memory management etc.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package -n libfbclient2
Summary:        Firebird SQL server client library
Obsoletes:      firebird-libfbclient < 4.0
Conflicts:      firebird-libfbclient < 4.0
Obsoletes:      firebird-libfbembed < 4.0

%description -n libfbclient2
Shared client library for Firebird SQL server.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package -n libfbclient2-devel
Summary:        Development libraries and headers for Firebird SQL server
Requires:       %{name}-devel = %{version}-%{release}
Requires:       libfbclient2 = %{version}-%{release}
Requires:       pkgconfig

%description -n libfbclient2-devel
Development files for Firebird SQL server client library.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package doc
Requires:       %{name} = %{version}-%{release}
Summary:        Documentation for Firebird SQL server
BuildArch:      noarch

%description doc
Documentation for Firebird SQL server.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package utils
Requires:       libfbclient2 = %{version}-%{release}
Summary:        Firebird SQL user utilities

%description utils
Firebird SQL user utilities.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%package examples
Requires:       %{name}-doc = %{version}-%{release}
Summary:        Examples for Firebird SQL server
BuildArch:      noarch

%description examples
Examples for Firebird SQL server.

Firebird is a relational database offering many ANSI SQL standard
features that runs on Linux, Windows, and a variety of Unix platforms.
Firebird offers excellent concurrency, high performance, and powerful
language support for stored procedures and triggers. It has been used
in production systems, under a variety of names, since 1981.


%prep
%setup -q -n %{pkgversion}
%patch101 -p1
%patch203 -p1
%patch205 -p1
%ifarch s390x
%patch303 -p1
%patch304 -p1
%endif


%build
%ifarch s390x
%global _lto_cflags %{nil}
%endif
export CFLAGS="%{optflags} -fno-strict-aliasing"
export CXXFLAGS="${CFLAGS} -fno-delete-null-pointer-checks"
NOCONFIGURE=1 ./autogen.sh
%configure --disable-rpath --prefix=%{_prefix} \
  --with-system-editline \
  --with-fbbin=%{_bindir} --with-fbsbin=%{_sbindir} \
  --with-fbconf=%{_sysconfdir}/%{name} \
  --with-fblib=%{_libdir} --with-fbinclude=%{_includedir} \
  --with-fbdoc=%{_defaultdocdir}/%{name} \
  --with-fbsample=%{_defaultdocdir}/%{name}/sample \
  --with-fbsample-db=%{_localstatedir}/lib/%{name}/data \
  --with-fbhelp=%{_localstatedir}/lib/%{name}/system \
  --with-fbintl=%{_libdir}/%{name}/intl \
  --with-fbmisc=%{_datadir}/%{name}/misc \
  --with-fbsecure-db=%{_localstatedir}/lib/%{name}/secdb \
  --with-fbmsg=%{_localstatedir}/lib/%{name}/system \
  --with-fblog=%{_localstatedir}/log/%{name} \
  --with-fbglock=/run/%{name} \
  --with-fbplugins=%{_libdir}/%{name}/plugins \
  --with-fbtzdata=%{_localstatedir}/lib/%{name}/tzdata 

make %{?_smp_mflags}
cd gen
sed -i '/linkFiles "/d' ./install/makeInstallImage.sh
./install/makeInstallImage.sh
chmod -R u+w buildroot%{_docdir}/%{name}

%install
chmod u+rw,a+rx gen/buildroot/%{_includedir}/firebird/impl
cp -r gen/buildroot/* ${RPM_BUILD_ROOT}/
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig
cp -v gen/install/misc/*.pc ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig/

cd ${RPM_BUILD_ROOT}
rm -vf .%{_sbindir}/*.sh
mv -v .%{_sbindir}/fb_config .%{_libdir}/
install -p -m 0755 %{SOURCE4} %{buildroot}%{_sbindir}/fb_config
rm -vf .%{_includedir}/perf.h
rm -vf .%{_libdir}/libicu*.so
chmod -R u+w .%{_docdir}/%{name}
mv -v .%{_datadir}/%{name}/misc/upgrade/udf/* .%{_docdir}/%{name}/
rm -rvf .%{_datadir}/%{name}/misc
mv -v .%{_sysconfdir}/%{name}/README.md .%{_sysconfdir}/%{name}/CHANGELOG.md \
  .%{_docdir}/%{name}/
mv -v .%{_sysconfdir}/%{name}/IDPLicense.txt .%{_docdir}/%{name}/
mv -v .%{_sysconfdir}/%{name}/IPLicense.txt .%{_docdir}/%{name}/
install -p -m 0644 -D %{SOURCE2} .%{_docdir}/%{name}/README.Fedora
mv -v .%{_bindir}/gstat .%{_bindir}/gstat-fb
mv -v .%{_bindir}/isql .%{_bindir}/isql-fb
rm -rvf .%{_defaultdocdir}/%{name}/sample/prebuilt

mkdir -p .%{_localstatedir}/log/%{name}
mkdir -p .%{_sysconfdir}/logrotate.d
echo 1 > .%{_localstatedir}/log/%{name}/%{name}.log
sed "s@%{name}.log@%{_localstatedir}/log/%{name}/%{name}.log@g" %{SOURCE1} > .%{_sysconfdir}/logrotate.d/%{name}

mkdir -p .%{_unitdir}
cp -f %{SOURCE3} .%{_unitdir}/%{name}.service


%pre 
# Create the firebird group if it doesn't exist
getent group %{name} > /dev/null || /usr/sbin/groupadd -r %{name} 
getent passwd %{name} >/dev/null || /usr/sbin/useradd -d / -g %{name} -s /sbin/nologin -r %{name} 

# Add gds_db to /etc/services if needed
FileName=/etc/services
newLine="gds_db 3050/tcp  # Firebird SQL Database Remote Protocol"
oldLine=`grep "^gds_db" $FileName`
if [ -z "$oldLine" ]; then
 echo $newLine >> $FileName
fi


%post 
%systemd_post firebird.service


%postun 
%systemd_postun_with_restart firebird.service


%preun 
%systemd_preun firebird.service


%files
%{_docdir}/%{name}/IDPLicense.txt
%{_docdir}/%{name}/IPLicense.txt
%{_docdir}/%{name}/README.Fedora
%{_bindir}/fbtracemgr
%{_sbindir}/firebird
%{_sbindir}/fbguard
%{_sbindir}/fb_lock_print
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/databases.conf
%config(noreplace) %{_sysconfdir}/%{name}/fbtrace.conf
%config(noreplace) %{_sysconfdir}/%{name}/firebird.conf
%config(noreplace) %{_sysconfdir}/%{name}/plugins.conf
%config(noreplace) %{_sysconfdir}/%{name}/replication.conf
%dir %{_libdir}/%{name}
%dir %{_datadir}/%{name}
%{_libdir}/%{name}/intl
%{_libdir}/%{name}/plugins

%dir %{_localstatedir}/lib/%{name}
%dir %attr(0700,%{name},%{name}) %{_localstatedir}/lib/%{name}/secdb
%dir %attr(0700,%{name},%{name}) %{_localstatedir}/lib/%{name}/data
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/system
%dir %attr(0755,%{name},%{name}) %{_localstatedir}/lib/%{name}/tzdata
%attr(0600,firebird,firebird) %config(noreplace) %{_localstatedir}/lib/%{name}/secdb/security4.fdb
%attr(0644,firebird,firebird) %{_localstatedir}/lib/%{name}/system/help.fdb
%attr(0644,firebird,firebird) %{_localstatedir}/lib/%{name}/system/firebird.msg
%attr(0644,firebird,firebird) %{_localstatedir}/lib/%{name}/tzdata/*.res
%ghost %dir %attr(0775,%{name},%{name}) /run/%{name}
%ghost %attr(0644,%{name},%{name}) /run/%{name}/fb_guard
%dir %{_localstatedir}/log/%{name}
%config(noreplace) %attr(0664,%{name},%{name})  %{_localstatedir}/log/%{name}/%{name}.log
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}

%attr(0644,root,root) %{_unitdir}/%{name}.service


%files devel
%{_includedir}/*.h
%{_includedir}/%{name}
%{_libdir}/fb_config
%{_sbindir}/fb_config


%files -n libfbclient2
%{_libdir}/libfbclient.so.*


%files -n libfbclient2-devel
%{_libdir}/libfbclient.so
%{_libdir}/pkgconfig/fbclient.pc


%files -n libib-util
%{_libdir}/libib_util.so


%files doc
%{_docdir}/%{name}
%exclude %{_docdir}/%{name}/sample
%exclude %{_docdir}/%{name}/IDPLicense.txt
%exclude %{_docdir}/%{name}/IPLicense.txt


%files utils
%{_bindir}/gstat-fb
%{_bindir}/fbsvcmgr
%{_bindir}/gbak
%{_bindir}/gfix
%{_bindir}/gpre
%{_bindir}/gsec
%{_bindir}/isql-fb
%{_bindir}/nbackup
%{_bindir}/qli
%{_bindir}/gsplit


%files examples
%{_docdir}/%{name}/sample
%attr(0600,firebird,firebird) %{_localstatedir}/lib/%{name}/data/employee.fdb


%changelog
* Fri Aug 20 2021 Philippe Makowski <makowski@fedoraproject.org> - 4.0.0.2496-2
- Fix build on s390x (#1969393)

* Tue Jun 08 2021 Philippe Makowski <makowski@fedoraproject.org> - 4.0.0.2496-1
- Update to 4.0.0 (#1963311)

* Fri Oct 23 2020 Philippe Makowski <makowski@fedoraproject.org> - 3.0.7.33374-1
- new upstream release fix #1887991

* Wed Jul 08 2020 Philippe Makowski <makowski@fedoraproject.org> - 3.0.6.33328-1
- new upstream release fix #1850675
 
* Mon Jan 20 2020 Philippe Makowski <makowski@fedoraproject.org> - 3.0.5.33220-1
- new upstream release fix #1786885

* Wed Sep 18 2019 Philippe Makowski <makowski@fedoraproject.org> - 3.0.4.33054-1
- new upstream release

* Thu Aug 22 2019 Philippe Makowski <makowski@fedoraproject.org> 2.5.9.27139.0-1
- update to 2.5.9 (End of Series)

* Fri Aug 31 2018 Philippe Makowski <makowski@fedoraproject.org> 2.5.8.27089.0-1
- update to 2.5.8

* Tue Feb 21 2017 Philippe Makowski <makowski@fedoraproject.org> 2.5.7.27050.0-1
- update to 2.5.7
- security fix (#1425332)

* Thu Dec 29 2016 Philippe Makowski <makowski@fedoraproject.org> 2.5.6.27020.0-1
- update to 2.5.6

* Fri Feb 05 2016 Philippe Makowski <makowski@fedoraproject.org> - 2.5.5.26952.0-2
- move fb_config (#1297506)
- fix CVE-2016-1569 (#1297447 #1297450 #1297451)

* Thu Nov 19 2015 Philippe Makowski <makowski@fedoraproject.org> 2.5.5.26952.0-1
- update to 2.5.5

* Thu Apr 2 2015 Philippe Makowski <makowski@fedoraproject.org> 2.5.4.26856.0-1
- update to 2.5.4

* Sun Dec 7 2014 Philippe Makowski <makowski@fedoraproject.org> 2.5.3.26778.0-2
- security fix firebird CORE-4630

* Sat Jul 26 2014 Philippe Makowski <makowski@fedoraproject.org>  - 2.5.3.26778.0-1
- update from upstream 2.5.3
- update arm64 patch

* Tue Jan 21 2014 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-8
- add missing BR on libstdc++-static

* Tue Jul 23 2013 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-7
- make fb_config executable  (bug #985335)

* Tue Jul 23 2013 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-6
- Provide fb_config in firebird-devel  (bug #985335)

* Mon Jun 03 2013 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-5
- Firebird fails to build for aarch64  (bug #969851)

* Thu Apr 25 2013 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-4
- set PIE compiler flags (bug #955274)

* Sun Mar 10 2013 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-3
- added patch from upstream to fix Firebird CORE-4058 CVE-2013-2492

* Sat Jan 26 2013 Rex Dieter <rdieter@fedoraproject.org> 2.5.2.26539.0-2
- rebuild (icu)

* Fri Nov 09 2012 Philippe Makowski <makowski@fedoraproject.org>  2.5.2.26539.0-1
- new upstream (bug fix release)
- added patch from upstream to fix Firebird CORE-3946

* Sat Aug 25 2012 Philippe Makowski <makowski@fedoraproject.org> 2.5.1.26351.0-4
- Modernize systemd scriptlets (bug #850109)

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.1.26351.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 23 2012 Philippe Makowski <makowski@fedoraproject.org> 2.5.1.26351.0-2
- rebuild for icu 4.8

* Thu Jan 19 2012 Philippe Makowski <makowski@fedoraproject.org> 2.5.1.26351.0-1
- Fix non-fatal POSTIN fix rh #781691
- new upstream

* Fri Jan 06 2012 Philippe Makowski <makowski@fedoraproject.org> 2.5.1.26349.0-4
- Rebuild for GCC-4.7

* Mon Nov 28 2011 Philippe Makowski <makowski@fedoraproject.org> 2.5.1.26349.O-3
- Better systemd support fix rh #757624

* Sun Oct 02 2011 Karsten Hopp <karsten@redhat.com> 2.5.1.26349.O-2
- drop ppc64 configure script hack, not required anymore

* Thu Sep 29 2011 Philippe Makowski <makowski@fedoraproject.org>  2.5.1.26349.0-1
- new upstream (bug fix release)
- added patch from upstream to fix Firebird CORE-3610

* Thu Sep 22 2011 Philippe Makowski <makowski@fedoraproject.org>  2.5.0.26074.0-10
- Add support for systemd (rh #737281)

* Fri Apr 22 2011 Philippe Makowski <makowski@fedoraproject.org>  2.5.0.26074.0-8
- added patch from upstream to fix rh #697313

* Mon Mar 07 2011 Caolรกn McNamara <caolanm@redhat.com> - 2.5.0.26074.0-7
- rebuild for icu 4.6

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.5.0.26074.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan 28 2011 Philippe Makowski <makowski[at]fedoraproject.org>  2.5.0.26074.0-5
- services must not be enabled by default

* Tue Jan 25 2011 Karsten Hopp <karsten@redhat.com> 2.5.0.26074.0-4
- firebird got miscompiled on ppc and had an empty libfbclient.so.2.5.0
  bump release and rebuild

* Wed Dec 22 2010 Philippe Makowski <makowski[at]fedoraproject.org>  2.5.0.26074.0-3
- Fix wrong assign file for classic and classic common

* Thu Dec 16 2010 Dan Horรกk <dan[at]danny.cz>  2.5.0.26074.0-2
- sync the s390(x) utilities list with other arches
- add libatomic_ops-devel as BR: on non-x86 arches

* Sat Dec 04 2010 Philippe Makowski <makowski@fedoraproject.org>  2.5.0.26074.0-1
- Fix rh #656587 /var/run mounted as tempfs

* Mon Nov 22 2010 Philippe Makowski <makowski@fedoraproject.org>  2.5.0.26074.0-0
- build with last upstream

* Tue Jun 29 2010 Dan Horรกk <dan[at]danny.cz>  2.1.3.18185.0-9
- update the s390(x) patch to match upstream

* Fri Jun 04 2010 Philippe Makowski <makowski@fedoraproject.org>  2.1.3.18185.0-8
 - conditional BuildRequires libstdc++-static

* Fri Jun 04 2010 Philippe Makowski <makowski@fedoraproject.org>  2.1.3.18185.0-7
- build with last upstream
- Fix rh #563461 with backport mainstream patch CORE-2928


* Fri Apr 02 2010 Caolรกn McNamara <caolanm@redhat.com> 2.1.3.18185.0-6
- rebuild for icu 4.4

* Sat Sep 05 2009 Karsten Hopp <karsten@redhat.com> 2.1.3.18185.0-5
- fix build on s390x for F-12 mass rebuild (Dan Horรกk)

* Tue Aug 11 2009  Philippe Makowski <makowski at fedoraproject.org> 2.1.3.18185.0-4
- build it against system edit lib
- set correct setuid for Classic lock manager
- set correct permission for /var/run/firebird

* Wed Aug 05 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.3.18185.0-2
- rename /usr/bin/gstat to /usr/bin/gstat-fb  to avoid conflict with ganglia-gmond (rh #515510)
- remove stupid rm -rf in postun

* Thu Jul 30 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.3.18185.0-1
- Update to 2.1.3.18185
- Fix rh #514463
- Remove doc patch
- Apply backport initscript patch

* Sat Jul 11 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-11
- change xinetd script (rh #506528)
- add missing library (and header files) for build php4-interbase module (rh #506728)
- update README.fedora
- automatically created user now have /bin/nologin as shell to make things a little more secure

* Tue May 12 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-8
- patch to fix gcc 4.4.0 and icu 4.2 build error

* Tue May 12 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-7
- patch to change lock files location and avoid %%{fbroot} owned by firebird user (rh #500219)
- add README.fedora
- add symlinks in /usr/bin
- change xinetd reload (rh #500219)

* Sat May 02 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-6
- add filesystem-subpackage
- remove common subpackage and use the main instead
- add logrotate config

* Thu Apr 30 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-5
- fix directories owning

* Thu Apr 23 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-4
- major cleaning install process to take care of the two architectures (Classic and Superserver) the right way

* Wed Apr 22 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-3
- fix group creation

* Sun Apr 19 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-2
- fix autogen issue for f11
- patch init script
- fix ppc64 lib destination issue

* Sun Apr 19 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.2.18118.0-1
- backport doc patch
- update to 2.1.2.18118
- cleanup macros
- specifie libdir
- change firebird user login

* Sat Mar 28 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.1.17910.0-5
- Major packaging restructuring

* Sat Mar 21 2009  Philippe Makowski <makowski at firebird-fr.eu.org> 2.1.1.17190.0-4
- Create a doc package
- major cleaning to avoid rpmlint errors
- revert to 2.1.1 (last stable build published)

* Mon Mar 09 2009  Jonathan MERCIER <bioinfornatics at gmail.com> 2.1.2.18116.0-3
- Perform %%configure with option --with-system-icu
- Add libicu-devel in BuildRequires
- Use iconv for convert files to UTF-8

* Thu Mar 05 2009  Jonathan MERCIER <bioinfornatics at gmail.com> 2.1.2.18116.0-2
- Update to 2.1.2
- Use %%global instead of %%define
- Change ${SOURCE1} to %%{SOURCE1}
- Change Group Database to Applications/Databases
- Change License IPL to Interbase
- Perform %%configure section's with some module
- Cconvert cyrillic character to UTF-8

* Thu Jul 17 2008 Arkady L. Shane <ashejn@yandex-team.ru> 2.1.1.17910.0-1
- Update to 2.1.1

* Fri Apr 18 2008 Arkady L. Shane <ashejn@yandex-team.ru> 2.1.0.17798.0-1
- Update to 2.1.0

* Thu Sep 27 2007 Arkady L. Shane <ashejn@yandex-team.ru> 2.0.3.12981.1-1
- Update to 2.0.3

* Thu Sep 13 2007 Arkady L. Shane <ashejn@yandex-team.ru> 2.0.1.12855.0-1
- Initial build for Fedora
- cleanup Mandriva spec

