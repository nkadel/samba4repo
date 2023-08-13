#
# spec file for package ceph
#
# Copyright (C) 2004-2019 The Ceph Project Developers. See COPYING file
# at the top-level directory of this distribution and at
# https://github.com/ceph/ceph/blob/master/COPYING
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon.
#
# This file is under the GNU Lesser General Public License, version 2.1
#
# Please submit bugfixes or comments via http://tracker.ceph.com/
#

#################################################################################
# conditional build section
#
# please read this for explanation of bcond syntax:
# https://rpm-software-management.github.io/rpm/manual/conditionalbuilds.html
#################################################################################
%global _hardened_build 1

%bcond_with make_check
%bcond_with zbd
%bcond_with cmake_verbose_logging
%bcond_without ceph_test_package
%ifarch s390
%bcond_with tcmalloc
%else
%bcond_without tcmalloc
%endif
%bcond_without rbd_ssd_cache
%ifarch x86_64
%bcond_without rbd_rwl_cache
%else
%bcond_with rbd_rwl_cache
%endif
%if 0%{?fedora} || 0%{?rhel}
%ifarch s390x %{arm64}
%bcond_with system_pmdk
%else
%bcond_without system_pmdk
%endif
%bcond_without selinux
%if 0%{?rhel} >= 8
%bcond_with cephfs_java
%else
%bcond_without cephfs_java
%endif
%bcond_without amqp_endpoint
%bcond_without kafka_endpoint
%bcond_without lttng
%bcond_without libradosstriper
%bcond_without ocf
%global luarocks_package_name luarocks
%bcond_without lua_packages
%global _remote_tarball_prefix https://download.ceph.com/tarballs/
%endif
%if 0%{?suse_version}
%bcond_without system_pmdk
%bcond_with amqp_endpoint
%bcond_with cephfs_java
%bcond_with kafka_endpoint
%bcond_with libradosstriper
%ifarch x86_64 aarch64 ppc64le
%bcond_without lttng
%else
%bcond_with lttng
%endif
%bcond_with ocf
%bcond_with selinux
#Compat macro for _fillupdir macro introduced in Nov 2017
%if ! %{defined _fillupdir}
%global _fillupdir /var/adm/fillup-templates
%endif
#luarocks
%if 0%{?is_opensuse}
# openSUSE
%bcond_without lua_packages
%if 0%{?sle_version}
# openSUSE Leap
%global luarocks_package_name lua53-luarocks
%else
# openSUSE Tumbleweed
%global luarocks_package_name lua54-luarocks
%endif
%else
# SLE
%bcond_with lua_packages
%endif
%endif
%bcond_with seastar
%bcond_with jaeger
%if 0%{?fedora} || 0%{?suse_version} >= 1500 || 0%{?rhel} >= 10
# distros that ship cmd2 and/or colorama
%bcond_without cephfs_shell
%else
# distros that do _not_ ship cmd2/colorama
%bcond_with cephfs_shell
%endif
%bcond_without system_arrow
%bcond_without system_utf8proc
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} >= 8
%global weak_deps 1
%endif
%if %{with selinux}
# get selinux policy version
# Force 0.0.0 policy version for centos builds to avoid repository sync issues between rhel and centos
%if 0%{?centos}
%global _selinux_policy_version 0.0.0
%else
%{!?_selinux_policy_version: %global _selinux_policy_version 0.0.0}
%endif
%endif

%{!?_udevrulesdir: %global _udevrulesdir /lib/udev/rules.d}
%{!?tmpfiles_create: %global tmpfiles_create systemd-tmpfiles --create}
%{!?python3_pkgversion: %global python3_pkgversion 3}
%{!?python3_version_nodots: %global python3_version_nodots 3}
%{!?python3_version: %global python3_version 3}
%{!?gts_prefix: %global gts_prefix gcc-toolset-11}


%if ! 0%{?suse_version}
# use multi-threaded xz compression: xz level 7 using ncpus threads
%global _source_payload w7T%{_smp_build_ncpus}.xzdio
%global _binary_payload w7T%{_smp_build_ncpus}.xzdio
%endif

%define smp_limit_mem_per_job() %( \
  kb_per_job=%1 \
  kb_total=$(head -3 /proc/meminfo | sed -n 's/MemAvailable:\\s*\\(.*\\) kB.*/\\1/p') \
  jobs=$(( $kb_total / $kb_per_job )) \
  [ $jobs -lt 1 ] && jobs=1 \
  echo $jobs )

%if 0%{?_smp_ncpus_max} == 0
%if 0%{?__isa_bits} == 32
# 32-bit builds can use 3G memory max, which is not enough even for -j2
%global _smp_ncpus_max 1
%else
# 3.0 GiB mem per job
# SUSE distros use limit_build in the place of smp_limit_mem_per_job, please
# be sure to update it (in the build section, below) as well when changing this
# number.
%global _smp_ncpus_max %{smp_limit_mem_per_job 3000000}
%endif
%endif

# disable -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1, as gcc-toolset-{10,11}-annobin
# do not provide gcc-annobin.so anymore, despite that they provide annobin.so. but
# redhat-rpm-config still passes -fplugin=gcc-annobin to the compiler.
%undefine _annotated_build
%if 0%{?rhel} == 8 && 0%{?enable_devtoolset11:1}
%enable_devtoolset11
%endif

#################################################################################
# main package definition
#################################################################################
Name:		ceph
Version:	17.2.5
#Release:	11%%{?dist}
Release:	0.11%{?dist}
%if 0%{?fedora} || 0%{?rhel}
Epoch:		2
%endif

# define _epoch_prefix macro which will expand to the empty string if epoch is
# undefined
%global _epoch_prefix %{?epoch:%{epoch}:}

Summary:	User space components of the Ceph file system
#License:	LGPL-2.1 and LGPL-3.0 and CC-BY-SA-3.0 and GPL-2.0 and BSL-1.0 and BSD-3-Clause and MIT
#License:	(LGPLv2+ or LGPLv3) and CC-BY-SA-3.0 and GPLv2 and Boost and BSD and MIT
License:	(LGPL-2.1-or-later OR LGPL-3.0-only) and CC-BY-SA-3.0 and GPL-2.0-only and BSL-1.0 and BSD-3-Clause and MIT
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
URL:		http://ceph.com/
Source0:	https://download.ceph.com/tarballs/ceph-%{version}.tar.gz
Patch0001:	0001-src-common-crc32c_intel_fast.patch
Patch0003:	0003-src-common-bitstr.h.patch
Patch0008:	0008-cmake-modules-Finduring.cmake.patch
Patch0010:	0010-CET-Add-CET-marker-to-crc32c_intel_fast_zero_asm.s.patch
Patch0011:	0011-isa-l-CET-Add-CET-marker-to-x86-64-crc32-assembly-co.patch
Patch0012:	0012-spdk-isa-l-CET-Add-CET-marker-to-x86-64-crc32-assemb.patch
Patch0016:	0016-src-tracing-patch
Patch0017:	0017-gcc-12-omnibus.patch
Patch0018:	0018-src-rgw-store-dbstore-CMakeLists.txt.patch
Patch0019:	0019-cmake-modules-CheckCxxAtomic.cmake.patch
Patch0020:	0020-src-arrow-cpp-cmake_modules-ThirdpartyToolchain.cmake.patch
Patch0023:	0023-src-s3select-include-s3select_parquet_intrf.h.patch
Patch0024:	0024-gcc-13.patch
Patch0025:	0025-selinux-prepare-for-anon-inode-controls-enablement.patch
# ceph 14.0.1 does not support 32-bit architectures, bugs #1727788, #1727787
ExcludeArch:	i686 armv7hl
%if 0%{?suse_version}
# _insert_obs_source_lines_here
ExclusiveArch:	x86_64 aarch64 ppc64le s390x
%endif
#################################################################################
# dependencies that apply across all distro families
#################################################################################
Requires:	ceph-osd = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mds = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mon = %{_epoch_prefix}%{version}-%{release}
Requires(post):	binutils
%if 0%{with cephfs_java}
BuildRequires:	java-devel
BuildRequires:	sharutils
%endif
%if 0%{with selinux}
BuildRequires:	checkpolicy
BuildRequires:	selinux-policy-devel
%endif
BuildRequires:	gperf
BuildRequires:	cmake > 3.5
BuildRequires:	fuse3-devel
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} == 9
BuildRequires: gcc-c++ >= 11
%endif
%if 0%{?rhel} == 8
BuildRequires: %{gts_prefix}-gcc-c++
BuildRequires: %{gts_prefix}-build
%ifarch aarch64
BuildRequires: %{gts_prefix}-libatomic-devel
%endif
%endif
%if 0%{?fedora} || 0%{?rhel} == 9
BuildRequires: libatomic
BuildRequires:	gcc-c++
%endif
BuildRequires:	libatomic
%ifarch x86_64 aarch64
BuildRequires:	mold
%endif
%if 0%{with tcmalloc}
# libprofiler did not build on ppc64le until 2.7.90
%if 0%{?fedora} || 0%{?rhel} >= 8
BuildRequires:	gperftools-devel >= 2.7.90
BuildRequires:	libunwind-devel
%endif
%if 0%{?rhel} && 0%{?rhel} < 8
BuildRequires:	gperftools-devel >= 2.6.1
%endif
%if 0%{?suse_version}
BuildRequires:	gperftools-devel >= 2.4
%endif
%endif
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel >= 2.17
BuildRequires:	cryptsetup-devel
BuildRequires:	libcurl-devel
BuildRequires:	libcap-ng-devel
BuildRequires:	fmt-devel >= 6.2.1
%if 0%{?fedora} || 0%{?rhel} >= 10
BuildRequires:	rocksdb-devel
Requires:	rocksdb
%endif
BuildRequires:	liburing-devel
BuildRequires:	pkgconfig(libudev)
BuildRequires:	libnl3-devel
BuildRequires:	liboath-devel
BuildRequires:	libtool
BuildRequires:	libxml2-devel
BuildRequires:	libzstd-devel
BuildRequires:	ninja-build
BuildRequires:	ncurses-devel
BuildRequires:	libicu-devel
BuildRequires:	patch
BuildRequires:	perl
BuildRequires:	pkgconfig
BuildRequires:	procps
BuildRequires:	python%{python3_pkgversion}
BuildRequires:	python%{python3_pkgversion}-devel
BuildRequires:	python%{python3_pkgversion}-setuptools
BuildRequires:	python%{python3_pkgversion}-Cython
BuildRequires:	snappy-devel
BuildRequires:	sqlite-devel
BuildRequires:	sudo
BuildRequires:	pkgconfig(udev)
BuildRequires:	valgrind-devel
BuildRequires:	which
BuildRequires:	xfsprogs-devel
BuildRequires:	xmlstarlet
BuildRequires:	nasm
BuildRequires:	lua-devel
%if 0%{with seastar} || 0%{with jaeger}
BuildRequires:	yaml-cpp-devel >= 0.6
%endif
%if 0%{with amqp_endpoint}
BuildRequires:	librabbitmq-devel
%endif
%if 0%{with kafka_endpoint}
BuildRequires:	librdkafka-devel
%endif
%if 0%{with lua_packages}
BuildRequires:	%{luarocks_package_name}
%endif
%if 0%{with make_check}
BuildRequires:	hostname
BuildRequires:	jq
BuildRequires:	libuuid-devel
BuildRequires:	python%{python3_pkgversion}-bcrypt
BuildRequires:	python%{python3_pkgversion}-pecan
BuildRequires:	python%{python3_pkgversion}-requests
BuildRequires:	python%{python3_pkgversion}-dateutil
BuildRequires:	python%{python3_pkgversion}-coverage
BuildRequires:	python%{python3_pkgversion}-pyOpenSSL
BuildRequires:	socat
BuildRequires:	python%{python3_pkgversion}-asyncssh
BuildRequires:	python%{python3_pkgversion}-natsort
%endif
%if 0%{with zbd}
BuildRequires:	libzbd-devel
%endif
%if 0%{?suse_version}
BuildRequires:	libthrift-devel >= 0.13.0
%else
BuildRequires:	thrift-devel >= 0.13.0
%endif
BuildRequires:	re2-devel
%if 0%{with jaeger}
BuildRequires:	bison
BuildRequires:	flex
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	json-devel
%endif
%if 0%{?suse_version}
BuildRequires:	nlohmann_json-devel
%endif
BuildRequires:	libevent-devel
%endif
%if 0%{with system_pmdk}
BuildRequires:	libpmem-devel
BuildRequires:	libpmemobj-devel
%endif
%if 0%{with system_arrow}
BuildRequires:	libarrow-devel
BuildRequires:	parquet-libs-devel
%else
BuildRequires:	xsimd-devel
%endif
%if 0%{with system_utf8proc}
BuildRequires:	utf8proc-devel
%endif
%if 0%{with seastar}
BuildRequires:	c-ares-devel
BuildRequires:	gnutls-devel
BuildRequires:	hwloc-devel
BuildRequires:	libpciaccess-devel
BuildRequires:	lksctp-tools-devel
BuildRequires:	ragel
BuildRequires:	systemtap-sdt-devel
%if 0%{?fedora} || 0%{?rhel} >= 10
BuildRequires:	libubsan
BuildRequires:	libasan
%endif
%if 0%{?rhel} == 8
BuildRequires: %{gts_prefix}-annobin
BuildRequires: %{gts_prefix}-annobin-plugin-gcc
BuildRequires: %{gts_prefix}-libubsan-devel
BuildRequires: %{gts_prefix}-libasan-devel
%endif
%endif
#################################################################################
# distro-conditional dependencies
#################################################################################
%if 0%{?suse_version}
BuildRequires:	pkgconfig(systemd)
BuildRequires:	systemd-rpm-macros
%{?systemd_requires}
PreReq:		%fillup_prereq
BuildRequires:	fdupes
BuildRequires:	memory-constraints
BuildRequires:	net-tools
BuildRequires:	libbz2-devel
BuildRequires:	mozilla-nss-devel
BuildRequires:	keyutils-devel
BuildRequires:	libopenssl-devel
BuildRequires:	ninja
BuildRequires:	lsb-release
BuildRequires:	openldap2-devel
#BuildRequires:	krb5
#BuildRequires:	krb5-devel
BuildRequires:	cunit-devel
BuildRequires:	python%{python3_pkgversion}-PrettyTable
BuildRequires:	python%{python3_pkgversion}-PyYAML
BuildRequires:	python%{python3_pkgversion}-Sphinx
BuildRequires:	rdma-core-devel
BuildRequires:	liblz4-devel >= 1.7
# for prometheus-alerts
BuildRequires:	golang-github-prometheus-prometheus
BuildRequires:	jsonnet
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:	systemd
BuildRequires:	boost-devel
BuildRequires:	boost-random
BuildRequires:	nss-devel
BuildRequires:	keyutils-libs-devel
BuildRequires:	libibverbs-devel
BuildRequires:	librdmacm-devel
BuildRequires:	ninja-build
BuildRequires:	openldap-devel
#BuildRequires:	krb5-devel
BuildRequires:	openssl-devel
BuildRequires:	CUnit-devel
BuildRequires:	python%{python3_pkgversion}-devel
BuildRequires:	python%{python3_pkgversion}-prettytable
BuildRequires:	python%{python3_pkgversion}-pyyaml
BuildRequires:	python%{python3_pkgversion}-sphinx
BuildRequires:	lz4-devel >= 1.7
%endif
# distro-conditional make check dependencies
BuildRequires:	golang
%if 0%{with make_check}
BuildRequires:	golang
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	golang-github-prometheus
BuildRequires:	libtool-ltdl-devel
BuildRequires:	xmlsec1
BuildRequires:	xmlsec1-devel
%ifarch x86_64
BuildRequires:	xmlsec1-nss
%endif
BuildRequires:	xmlsec1-openssl
BuildRequires:	xmlsec1-openssl-devel
BuildRequires:	python%{python3_pkgversion}-cherrypy
BuildRequires:	python%{python3_pkgversion}-jwt
BuildRequires:	python%{python3_pkgversion}-routes
BuildRequires:	python%{python3_pkgversion}-scipy
BuildRequires:	python%{python3_pkgversion}-werkzeug
BuildRequires:	python%{python3_pkgversion}-pyOpenSSL
%endif
%if 0%{?suse_version}
BuildRequires:	golang-github-prometheus-prometheus
BuildRequires:	jsonnet
BuildRequires:	libxmlsec1-1
BuildRequires:	libxmlsec1-nss1
BuildRequires:	libxmlsec1-openssl1
BuildRequires:	python%{python3_pkgversion}-CherryPy
BuildRequires:	python%{python3_pkgversion}-PyJWT
BuildRequires:	python%{python3_pkgversion}-Routes
BuildRequires:	python%{python3_pkgversion}-Werkzeug
BuildRequires:	python%{python3_pkgversion}-numpy-devel
BuildRequires:	xmlsec1-devel
BuildRequires:	xmlsec1-openssl-devel
%endif
%endif
# lttng and babeltrace for rbd-replay-prep
%if %{with lttng}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	lttng-ust-devel
BuildRequires:	libbabeltrace-devel
%endif
%if 0%{?suse_version}
BuildRequires:	lttng-ust-devel
BuildRequires:	babeltrace-devel
%endif
%endif
%if 0%{?suse_version}
BuildRequires:	libexpat-devel
%endif
%if 0%{?rhel} || 0%{?fedora}
BuildRequires:	expat-devel
%endif
#hardened-cc1
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	redhat-rpm-config
%endif
%if 0%{with seastar}
%if 0%{?fedora} || 0%{?rhel}
BuildRequires:	cryptopp-devel
BuildRequires:	numactl-devel
BuildRequires:	protobuf-compiler
%endif
%if 0%{?suse_version}
BuildRequires:	libcryptopp-devel
BuildRequires:	libnuma-devel
%endif
%endif
%if 0%{?rhel} >= 8
BuildRequires:	/usr/bin/pathfix.py
%endif

%description
Ceph is a massively scalable, open-source, distributed storage system that runs
on commodity hardware and delivers object, block and file system storage.


#################################################################################
# subpackages
#################################################################################
%package base
Summary:	Ceph Base Package
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Provides:	ceph-test:/usr/bin/ceph-kvstore-tool = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-common = %{_epoch_prefix}%{version}-%{release}
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librgw2 = %{_epoch_prefix}%{version}-%{release}
%if 0%{with selinux}
Requires:	ceph-selinux = %{_epoch_prefix}%{version}-%{release}
%endif
Requires:	findutils
Requires:	grep
Requires:	logrotate
Requires:	parted
Requires:	psmisc
Requires:	util-linux
Requires:	which
%if 0%{?rhel} && 0%{?rhel} < 8
# The following is necessary due to tracker 36508 and can be removed once the
# associated upstream bugs are resolved.
%if 0%{with tcmalloc}
Requires:	gperftools-libs >= 2.6.1
%endif
%endif
%if 0%{?weak_deps}
Recommends:	chrony
Recommends:	nvme-cli
%if 0%{?suse_version}
Requires:	smartmontools
%else
Recommends:	smartmontools
%endif
%endif
%description base
Base is the package that includes all the files shared amongst ceph servers

%package -n cephadm
Summary:	Utility to bootstrap Ceph clusters
BuildArch:	noarch
Requires:	lvm2
Requires:	python%{python3_pkgversion}
Requires:	openssh-server
Requires:	which
%if 0%{?weak_deps}
Recommends:	podman >= 2.0.2
%endif
%description -n cephadm
Utility to bootstrap a Ceph cluster and manage Ceph daemons deployed
with systemd and podman.

%package -n ceph-common
Summary:	Ceph Common
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rbd = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-cephfs = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rgw = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-argparse = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-common = %{_epoch_prefix}%{version}-%{release}
%if 0%{with jaeger}
Requires:	libjaeger = %{_epoch_prefix}%{version}-%{release}
%endif
%if 0%{?fedora} || 0%{?rhel}
Requires:	python%{python3_pkgversion}-prettytable
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-PrettyTable
%endif
%if 0%{with libradosstriper}
Requires:	libradosstriper1 = %{_epoch_prefix}%{version}-%{release}
%endif
%{?systemd_requires}
%if 0%{?suse_version}
Requires(pre):	pwdutils
%endif
Requires:	systemd-udev
%description -n ceph-common
Common utilities to mount and interact with a ceph storage cluster.
Comprised of files that are common to Ceph clients and servers.

%package mds
Summary:	Ceph Metadata Server Daemon
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
%description mds
ceph-mds is the metadata server daemon for the Ceph distributed file system.
One or more instances of ceph-mds collectively manage the file system
namespace, coordinating access to the shared OSD cluster.

%package mon
Summary:	Ceph Monitor Daemon
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Provides:	ceph-test:/usr/bin/ceph-monstore-tool = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
%description mon
ceph-mon is the cluster monitor daemon for the Ceph distributed file
system. One or more instances of ceph-mon form a Paxos part-time
parliament cluster that provides extremely reliable and durable storage
of cluster membership, configuration, and state.

%package mgr
Summary:	Ceph Manager Daemon
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-mgr-modules-core = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephsqlite = %{_epoch_prefix}%{version}-%{release}
%if 0%{?weak_deps}
Recommends:	ceph-mgr-dashboard = %{_epoch_prefix}%{version}-%{release}
Recommends:	ceph-mgr-diskprediction-local = %{_epoch_prefix}%{version}-%{release}
Recommends:	ceph-mgr-k8sevents = %{_epoch_prefix}%{version}-%{release}
Recommends:	ceph-mgr-cephadm = %{_epoch_prefix}%{version}-%{release}
Recommends:	python%{python3_pkgversion}-influxdb
%endif
%description mgr
ceph-mgr enables python modules that provide services (such as the REST
module derived from Calamari) and expose CLI hooks.  ceph-mgr gathers
the cluster maps, the daemon metadata, and performance counters, and
exposes all these to the python modules.

%package mgr-dashboard
Summary:	Ceph Dashboard
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-grafana-dashboards = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-prometheus-alerts = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-setuptools
%if 0%{?fedora} || 0%{?rhel}
Requires:	python%{python3_pkgversion}-cherrypy
Requires:	python%{python3_pkgversion}-jwt
Requires:	python%{python3_pkgversion}-routes
Requires:	python%{python3_pkgversion}-werkzeug
%if 0%{?weak_deps}
Recommends:	python%{python3_pkgversion}-saml
%endif
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-CherryPy
Requires:	python%{python3_pkgversion}-PyJWT
Requires:	python%{python3_pkgversion}-Routes
Requires:	python%{python3_pkgversion}-Werkzeug
Recommends:	python%{python3_pkgversion}-python3-saml
%endif
%description mgr-dashboard
ceph-mgr-dashboard is a manager module, providing a web-based application
to monitor and manage many aspects of a Ceph cluster and related components.
See the Dashboard documentation at http://docs.ceph.com/ for details and a
detailed feature overview.

%package mgr-diskprediction-local
Summary:	Ceph Manager module for predicting disk failures
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-numpy
%if 0%{?fedora} || 0%{?suse_version} || 0%{?rhel} >= 10
Requires:	python%{python3_pkgversion}-scikit-learn
%endif
Requires:	python3-scipy
%description mgr-diskprediction-local
ceph-mgr-diskprediction-local is a ceph-mgr module that tries to predict
disk failures using local algorithms and machine-learning databases.

%package mgr-modules-core
Summary:	Ceph Manager modules which are always enabled
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	python%{python3_pkgversion}-bcrypt
Requires:	python%{python3_pkgversion}-pecan
Requires:	python%{python3_pkgversion}-pyOpenSSL
Requires:	python%{python3_pkgversion}-requests
Requires:	python%{python3_pkgversion}-dateutil
%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:	python%{python3_pkgversion}-cherrypy
Requires:	python%{python3_pkgversion}-pyyaml
Requires:	python%{python3_pkgversion}-werkzeug
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-CherryPy
Requires:	python%{python3_pkgversion}-PyYAML
Requires:	python%{python3_pkgversion}-Werkzeug
%endif
%if 0%{?weak_deps}
Recommends:	ceph-mgr-rook = %{_epoch_prefix}%{version}-%{release}
%endif
%description mgr-modules-core
ceph-mgr-modules-core provides a set of modules which are always
enabled by ceph-mgr.

%package mgr-rook
BuildArch:	noarch
Summary:	Ceph Manager module for Rook-based orchestration
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-kubernetes
Requires:	python%{python3_pkgversion}-jsonpatch
%description mgr-rook
ceph-mgr-rook is a ceph-mgr module for orchestration functions using
a Rook backend.

%package mgr-k8sevents
BuildArch:	noarch
Summary:	Ceph Manager module to orchestrate ceph-events to kubernetes' events API
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-kubernetes
%description mgr-k8sevents
ceph-mgr-k8sevents is a ceph-mgr module that sends every ceph-events
to kubernetes' events API

%package mgr-cephadm
Summary:	Ceph Manager module for cephadm-based orchestration
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-mgr = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-asyncssh
Requires:	python%{python3_pkgversion}-natsort
Requires:	cephadm = %{_epoch_prefix}%{version}-%{release}
%if 0%{?suse_version}
Requires:	openssh
Requires:	python%{python3_pkgversion}-CherryPy
Requires:	python%{python3_pkgversion}-Jinja2
%endif
%if 0%{?rhel} || 0%{?fedora}
Requires:	openssh-clients
Requires:	python%{python3_pkgversion}-cherrypy
Requires:	python%{python3_pkgversion}-jinja2
%endif
%description mgr-cephadm
ceph-mgr-cephadm is a ceph-mgr module for orchestration functions using
the integrated cephadm deployment tool management operations.

%package fuse
Summary:	Ceph fuse-based client
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	fuse
Requires:	python%{python3_pkgversion}
%description fuse
FUSE based client for Ceph distributed network file system

%package -n cephfs-mirror
Summary:	Ceph daemon for mirroring CephFS snapshots
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
%description -n cephfs-mirror
Daemon for mirroring CephFS snapshots between Ceph clusters.

%package -n ceph-exporter
Summary:	Daemon for exposing perf counters as Prometheus metrics
%if 0%{?suse_version}
Group:	System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
%description -n ceph-exporter
Daemon for exposing perf counters as Prometheus metrics

%package -n rbd-fuse
Summary:	Ceph fuse-based client
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
%description -n rbd-fuse
FUSE based client to map Ceph rbd images to files

%package -n rbd-mirror
Summary:	Ceph daemon for mirroring RBD images
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
%description -n rbd-mirror
Daemon for mirroring RBD images between Ceph clusters, streaming
changes asynchronously.

%package immutable-object-cache
Summary:	Ceph daemon for immutable object cache
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description immutable-object-cache
Daemon for immutable object cache.

%package -n rbd-nbd
Summary:	Ceph RBD client base on NBD
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
%description -n rbd-nbd
NBD based client to map Ceph rbd images to local device

%package radosgw
Summary:	Rados REST gateway
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
%if 0%{with selinux}
Requires:	ceph-selinux = %{_epoch_prefix}%{version}-%{release}
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librgw2 = %{_epoch_prefix}%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Requires:	mailcap
%endif
%if 0%{?weak_deps}
Recommends:	gawk
%endif
%description radosgw
RADOS is a distributed object store used by the Ceph distributed
storage system.  This package provides a REST gateway to the
object store that aims to implement a superset of Amazon's S3
service as well as the OpenStack Object Storage ("Swift") API.

%package -n cephfs-top
Summary:	top(1) like utility for Ceph Filesystem
BuildArch:	noarch
Requires:	python%{python3_pkgversion}-rados
%description -n cephfs-top
This package provides a top(1) like utility to display Ceph Filesystem metrics
in realtime.

%if %{with ocf}
%package resource-agents
Summary:	OCF-compliant resource agents for Ceph daemons
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}
Requires:	resource-agents
%description resource-agents
Resource agents for monitoring and managing Ceph daemons
under Open Cluster Framework (OCF) compliant resource
managers such as Pacemaker.
%endif

%package osd
Summary:	Ceph Object Storage Daemon
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Provides:	ceph-test:/usr/bin/ceph-osdomap-tool = %{_epoch_prefix}%{version}-%{release}
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	sudo
Requires:	libstoragemgmt
%if 0%{?weak_deps}
Recommends:	ceph-volume = %{_epoch_prefix}%{version}-%{release}
%endif
%description osd
ceph-osd is the object storage daemon for the Ceph distributed file
system.  It is responsible for storing objects on a local file system
and providing access to them over the network.

%if 0%{with seastar}
%package crimson-osd
Summary:	Ceph Object Storage Daemon (crimson)
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-osd = %{_epoch_prefix}%{version}-%{release}
Requires:	binutils
%description crimson-osd
crimson-osd is the object storage daemon for the Ceph distributed file
system.  It is responsible for storing objects on a local file system
and providing access to them over the network.
%endif

%package volume
Summary: Ceph OSD deployment and inspection tool
BuildArch: noarch
%if 0%{?suse_version}
Group: System/Filesystems
%endif
Requires:	ceph-osd = %{_epoch_prefix}%{version}-%{release}
Requires:	cryptsetup
Requires:	e2fsprogs
Requires:	lvm2
Requires:	parted
Requires:	util-linux
Requires:	xfsprogs
Requires:	python%{python3_pkgversion}-setuptools
Requires:	python%{python3_pkgversion}-ceph-common = %{_epoch_prefix}%{version}-%{release}
%description volume
This package contains a tool to deploy OSD with different devices like
lvm or physical disks, and trying to follow a predictable, and robust
way of preparing, activating, and starting the deployed OSD.

%package -n librados2
Summary:	RADOS distributed object store client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librados2
RADOS is a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to access the distributed object
store using a simple file-like interface.

%package -n librados-devel
Summary:	RADOS headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librados2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librados2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librados-devel
This package contains C libraries and headers needed to develop programs
that use RADOS object store.

%package -n libradospp-devel
Summary:	RADOS headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
%description -n libradospp-devel
This package contains C++ libraries and headers needed to develop programs
that use RADOS object store.

%package -n librgw2
Summary:	RADOS gateway client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n librgw2
This package provides a library implementation of the RADOS gateway
(distributed object store with S3 and Swift personalities).

%package -n librgw-devel
Summary:	RADOS gateway client library
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	librgw2 = %{_epoch_prefix}%{version}-%{release}
Provides:	librgw2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librgw2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librgw-devel
This package contains libraries and headers needed to develop programs
that use RADOS gateway client library.

%package -n python%{python3_pkgversion}-rgw
Summary:	Python 3 libraries for the RADOS gateway
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	librgw2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-rgw}
Provides:	python-rgw = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-rgw < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rgw
This package contains Python 3 libraries for interacting with Ceph RADOS
gateway.

%package -n python%{python3_pkgversion}-rados
Summary:	Python 3 libraries for the RADOS object store
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	python%{python3_pkgversion}
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-rados}
Provides:	python-rados = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-rados < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rados
This package contains Python 3 libraries for interacting with Ceph RADOS
object store.

%package -n libcephsqlite
Summary:	SQLite3 VFS for Ceph
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n libcephsqlite
A SQLite3 VFS for storing and manipulating databases stored on Ceph's RADOS
distributed object store.

%package -n libcephsqlite-devel
Summary:	SQLite3 VFS for Ceph headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	sqlite-devel
Requires:	libcephsqlite = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephsqlite-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephsqlite-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephsqlite-devel
A SQLite3 VFS for storing and manipulating databases stored on Ceph's RADOS
distributed object store.

%if 0%{with libradosstriper}
%package -n libradosstriper1
Summary:	RADOS striping interface
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper1
Striping interface built on top of the rados library, allowing
to stripe bigger objects onto several standard rados objects using
an interface very similar to the rados one.

%package -n libradosstriper-devel
Summary:	RADOS striping interface headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libradosstriper1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libradosstriper1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libradosstriper1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libradosstriper-devel
This package contains libraries and headers needed to develop programs
that use RADOS striping interface.
%endif

%package -n librbd1
Summary:	RADOS block device client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	librados2 = %{_epoch_prefix}%{version}-%{release}
%if 0%{?suse_version}
Requires(post): coreutils
%endif
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n librbd1
RBD is a block device striped across multiple distributed objects in
RADOS, a reliable, autonomic distributed object storage cluster
developed as part of the Ceph distributed storage system. This is a
shared library allowing applications to manage these block devices.

%package -n librbd-devel
Summary:	RADOS block device headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	librbd1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	librbd1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n librbd-devel
This package contains libraries and headers needed to develop programs
that use RADOS block device.

%package -n python%{python3_pkgversion}-rbd
Summary:	Python 3 libraries for the RADOS block device
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	librbd1 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-rbd}
Provides:	python-rbd = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-rbd < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-rbd
This package contains Python 3 libraries for interacting with Ceph RADOS
block device.

%package -n libcephfs2
Summary:	Ceph distributed file system client library
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Obsoletes:	libcephfs1 < %{_epoch_prefix}%{version}-%{release}
%if 0%{?rhel} || 0%{?fedora}
Obsoletes:	ceph-libs < %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-libcephfs < %{_epoch_prefix}%{version}-%{release}
%endif
%description -n libcephfs2
Ceph is a distributed network file system designed to provide excellent
performance, reliability, and scalability. This is a shared library
allowing applications to access a Ceph distributed file system via a
POSIX-like interface.

%package -n libcephfs-devel
Summary:	Ceph distributed file system headers
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	librados-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephfs2-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephfs2-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephfs-devel
This package contains libraries and headers needed to develop programs
that use Ceph distributed file system.

%package -n python%{python3_pkgversion}-cephfs
Summary:	Python 3 libraries for Ceph distributed file system
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-rados = %{_epoch_prefix}%{version}-%{release}
Requires:	python%{python3_pkgversion}-ceph-argparse = %{_epoch_prefix}%{version}-%{release}
%{?python_provide:%python_provide python%{python3_pkgversion}-cephfs}
Provides:	python-cephfs = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	python-cephfs < %{_epoch_prefix}%{version}-%{release}
%description -n python%{python3_pkgversion}-cephfs
This package contains Python 3 libraries for interacting with Ceph distributed
file system.

%package -n python%{python3_pkgversion}-ceph-argparse
Summary:	Python 3 utility libraries for Ceph CLI
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
%{?python_provide:%python_provide python%{python3_pkgversion}-ceph-argparse}
%description -n python%{python3_pkgversion}-ceph-argparse
This package contains types and routines for Python 3 used by the Ceph CLI as
well as the RESTful interface. These have to do with querying the daemons for
command-description information, validating user command input against those
descriptions, and submitting the command to the appropriate daemon.

%package -n python%{python3_pkgversion}-ceph-common
Summary:	Python 3 utility libraries for Ceph
%if 0%{?fedora} || 0%{?rhel} >= 8
Requires:	python%{python3_pkgversion}-pyyaml
%endif
%if 0%{?suse_version}
Requires:	python%{python3_pkgversion}-PyYAML
%endif
%if 0%{?suse_version}
Group:		Development/Libraries/Python
%endif
%{?python_provide:%python_provide python%{python3_pkgversion}-ceph-common}
%description -n python%{python3_pkgversion}-ceph-common
This package contains data structures, classes and functions used by Ceph.
It also contains utilities used for the cephadm orchestrator.

%if 0%{with cephfs_shell}
%package -n cephfs-shell
Summary:	Interactive shell for Ceph file system
Requires:	python%{python3_pkgversion}-cmd2
Requires:	python%{python3_pkgversion}-colorama
Requires:	python%{python3_pkgversion}-cephfs
%description -n cephfs-shell
This package contains an interactive tool that allows accessing a Ceph
file system without mounting it by providing a nice pseudo-shell which
works like an FTP client.
%endif

%if 0%{with ceph_test_package}
%package -n ceph-test
Summary:	Ceph benchmarks and test tools
%if 0%{?suse_version}
Group:		System/Benchmark
%endif
Requires:	ceph-common = %{_epoch_prefix}%{version}-%{release}
Requires:	xmlstarlet
Requires:	jq
Requires:	socat
BuildRequires:	gtest-devel
BuildRequires:	gmock-devel
%description -n ceph-test
This package contains Ceph benchmarks and test tools.
%endif

%if 0%{with cephfs_java}

%package -n libcephfs_jni1
Summary:	Java Native Interface library for CephFS Java bindings
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	java
Requires:	libcephfs2 = %{_epoch_prefix}%{version}-%{release}
%description -n libcephfs_jni1
This package contains the Java Native Interface library for CephFS Java
bindings.

%package -n libcephfs_jni-devel
Summary:	Development files for CephFS Java Native Interface library
%if 0%{?suse_version}
Group:		Development/Libraries/Java
%endif
Requires:	java
Requires:	libcephfs_jni1 = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	ceph-devel < %{_epoch_prefix}%{version}-%{release}
Provides:	libcephfs_jni1-devel = %{_epoch_prefix}%{version}-%{release}
Obsoletes:	libcephfs_jni1-devel < %{_epoch_prefix}%{version}-%{release}
%description -n libcephfs_jni-devel
This package contains the development files for CephFS Java Native Interface
library.

%package -n cephfs-java
Summary:	Java libraries for the Ceph File System
%if 0%{?suse_version}
Group:		System/Libraries
%endif
Requires:	java
Requires:	libcephfs_jni1 = %{_epoch_prefix}%{version}-%{release}
Requires:	junit
BuildRequires:	junit
%description -n cephfs-java
This package contains the Java libraries for the Ceph File System.

%endif

%package -n rados-objclass-devel
Summary:	RADOS object class development kit
%if 0%{?suse_version}
Group:		Development/Libraries/C and C++
%endif
Requires:	libradospp-devel = %{_epoch_prefix}%{version}-%{release}
%description -n rados-objclass-devel
This package contains libraries and headers needed to develop RADOS object
class plugins.

%if 0%{with selinux}

%package selinux
Summary:	SELinux support for Ceph MON, OSD and MDS
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
Requires:	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires:	policycoreutils, libselinux-utils
Requires(post):	ceph-base = %{_epoch_prefix}%{version}-%{release}
Requires(post): selinux-policy-base >= %{_selinux_policy_version}, policycoreutils, gawk
Requires(postun): policycoreutils
%description selinux
This package contains SELinux support for Ceph MON, OSD and MDS. The package
also performs file-system relabelling which can take a long time on heavily
populated file-systems.

%endif

%package grafana-dashboards
Summary:	The set of Grafana dashboards for monitoring purposes
BuildArch:	noarch
%if 0%{?suse_version}
Group:		System/Filesystems
%endif
%description grafana-dashboards
This package provides a set of Grafana dashboards for monitoring of
Ceph clusters. The dashboards require a Prometheus server setup
collecting data from Ceph Manager "prometheus" module and Prometheus
project "node_exporter" module. The dashboards are designed to be
integrated with the Ceph Manager Dashboard web UI.

%package prometheus-alerts
Summary:	Prometheus alerts for a Ceph deplyoment
BuildArch:	noarch
Group:		System/Monitoring
%description prometheus-alerts
This package provides Ceph default alerts for Prometheus.

#################################################################################
# common
#################################################################################
%prep
%autosetup -p1

%build
# Disable lto on systems that do not support symver attribute
# See https://gcc.gnu.org/bugzilla/show_bug.cgi?id=48200 for details
%if ( 0%{?rhel} && 0%{?rhel} < 9 ) || ( 0%{?suse_version} && 0%{?suse_version} <= 1500 )
 %define _lto_cflags %{nil}
%endif


%if 0%{with cephfs_java}
# Find jni.h
for i in /usr/{lib64,lib}/jvm/java/include{,/linux}; do
    [ -d $i ] && java_inc="$java_inc -I$i"
done
%endif

%if 0%{?suse_version}
%limit_build -m 3000
%endif

export CPPFLAGS="$java_inc"
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
export LDFLAGS="$RPM_LD_FLAGS"

# Workaround to https://tracker.ceph.com/issues/56610
%if 0%{?fedora} >= 37 || 0%{?rhel} >= 10
export CFLAGS="$RPM_OPT_FLAGS -DFMT_DEPRECATED_OSTREAM"
export CXXFLAGS="$RPM_OPT_FLAGS -DFMT_DEPRECATED_OSTREAM"
%endif

%if 0%{with seastar}
# seastar uses longjmp() to implement coroutine. and this annoys longjmp_chk()
%undefine _fortify_level
%endif

env | sort

%{?!_vpath_builddir:%global _vpath_builddir %{_target_platform}}

# TODO: drop this step once we can use `cmake -B`
%{cmake} \
    -GNinja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DBUILD_CONFIG=rpmbuild \
    -DSYSTEMD_SYSTEM_UNIT_DIR:PATH=%{_unitdir} \
    -DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
    -DWITH_MANPAGE:BOOL=ON \
    -DWITH_PYTHON3:STRING=%{python3_version} \
    -DWITH_MGR_DASHBOARD_FRONTEND:BOOL=OFF \
%if 0%{?suse_version}
    -DWITH_RADOSGW_SELECT_PARQUET:BOOL=OFF \
%endif
%if 0%{without ceph_test_package}
    -DWITH_TESTS:BOOL=OFF \
%endif
%if 0%{with cephfs_java}
    -DWITH_CEPHFS_JAVA:BOOL=ON \
%endif
%if 0%{with selinux}
    -DWITH_SELINUX:BOOL=ON \
%endif
%if %{with lttng}
    -DWITH_LTTNG:BOOL=ON \
    -DWITH_BABELTRACE:BOOL=ON \
%else
    -DWITH_LTTNG:BOOL=OFF \
    -DWITH_BABELTRACE:BOOL=OFF \
%endif
    $CEPH_EXTRA_CMAKE_ARGS \
%if 0%{with ocf}
    -DWITH_OCF:BOOL=ON \
%endif
%if 0%{?fedora} || 0%{?rhel} >= 10
    -DWITH_SYSTEM_ROCKSDB:BOOL=ON \
%endif
    -DWITH_SYSTEM_LIBURING:BOOL=ON \
    -DWITH_SYSTEM_BOOST:BOOL=ON \
%if 0%{with cephfs_shell}
    -DWITH_CEPHFS_SHELL:BOOL=ON \
%endif
%if 0%{with libradosstriper}
    -DWITH_LIBRADOSSTRIPER:BOOL=ON \
%else
    -DWITH_LIBRADOSSTRIPER:BOOL=OFF \
%endif
%if 0%{with amqp_endpoint}
    -DWITH_RADOSGW_AMQP_ENDPOINT:BOOL=ON \
%else
    -DWITH_RADOSGW_AMQP_ENDPOINT:BOOL=OFF \
%endif
%if 0%{with kafka_endpoint}
    -DWITH_RADOSGW_KAFKA_ENDPOINT:BOOL=ON \
%else
    -DWITH_RADOSGW_KAFKA_ENDPOINT:BOOL=OFF \
%endif
%if 0%{without lua_packages}
    -DWITH_RADOSGW_LUA_PACKAGES:BOOL=OFF \
%endif
%if 0%{with zbd}
    -DWITH_ZBD:BOOL=ON \
%endif
%if 0%{with cmake_verbose_logging}
    -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
%endif
%if 0%{with rbd_rwl_cache}
    -DWITH_RBD_RWL:BOOL=ON \
%endif
%if 0%{with rbd_ssd_cache}
    -DWITH_RBD_SSD_CACHE:BOOL=ON \
%endif
%if 0%{with system_pmdk}
    -DWITH_SYSTEM_PMDK:BOOL=ON \
%endif
%if 0%{with jaeger}
    -DWITH_JAEGER:BOOL=ON \
%endif
%if 0%{?suse_version}
    -DBOOST_J:STRING=%{jobs} \
%else
    -DBOOST_J:STRING=%{_smp_build_ncpus} \
%endif
%if 0%{with ceph_test_package}
    -DWITH_SYSTEM_GTEST:BOOL=ON \
%endif
    -DWITH_SYSTEM_ZSTD:BOOL=ON \
%if 0%{?rhel}
    -DWITH_FMT_HEADER_ONLY:BOOL=ON \
%endif
%if 0%{with system_arrow}
    -DWITH_SYSTEM_ARROW:BOOL=ON \
%endif
%if 0%{with system_utf8proc}
    -DWITH_SYSTEM_UTF8PROC:BOOL=ON \
%endif
%ifarch x86_64 aarch64
    -DCMAKE_LINKER=%{_bindir}/ld.mold \
%endif
%if 0%{with seastar}
    -DWITH_SEASTAR:BOOL=ON \
    -DWITH_JAEGER:BOOL=OFF \
%endif
    -DWITH_GRAFANA:BOOL=ON

%if %{with cmake_verbose_logging}
cat ./%{__cmake_builddir}/CMakeFiles/CMakeOutput.log
cat ./%{__cmake_builddir}/CMakeFiles/CMakeError.log
%endif

export VERBOSE=1
export V=1
export GCC_COLORS=
%cmake_build

%if 0%{with make_check}
%check
# run in-tree unittests
# cd %{_vpath_builddir}
# ctest "$CEPH_MFLAGS_JOBS"
%endif

%install
%cmake_install
# we have dropped sysvinit bits
rm -f %{buildroot}/%{_sysconfdir}/init.d/ceph
%if 0%{with seastar}
# package crimson-osd with the name of ceph-osd
install -m 0755 %{buildroot}%{_bindir}/crimson-osd %{buildroot}%{_bindir}/ceph-osd
%endif

install -m 0644 -D src/etc-rbdmap %{buildroot}%{_sysconfdir}/ceph/rbdmap
%if 0%{?fedora} || 0%{?rhel}
install -m 0644 -D etc/sysconfig/ceph %{buildroot}%{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
install -m 0644 -D etc/sysconfig/ceph %{buildroot}%{_fillupdir}/sysconfig.%{name}
%endif
install -m 0644 -D systemd/ceph.tmpfiles.d %{buildroot}%{_tmpfilesdir}/ceph-common.conf
install -m 0644 -D systemd/50-ceph.preset %{buildroot}%{_presetdir}/50-ceph.preset
mkdir -p %{buildroot}%{_sbindir}
install -m 0644 -D src/logrotate.conf %{buildroot}%{_sysconfdir}/logrotate.d/ceph
chmod 0644 %{buildroot}%{_docdir}/ceph/sample.ceph.conf
install -m 0644 -D COPYING %{buildroot}%{_docdir}/ceph/COPYING
install -m 0644 -D etc/sysctl/90-ceph-osd.conf %{buildroot}%{_sysctldir}/90-ceph-osd.conf
install -m 0755 -D src/tools/rbd_nbd/rbd-nbd_quiesce %{buildroot}%{_libexecdir}/rbd-nbd/rbd-nbd_quiesce

install -m 0755 src/cephadm/cephadm %{buildroot}%{_sbindir}/cephadm
mkdir -p %{buildroot}%{_sharedstatedir}/cephadm
chmod 0700 %{buildroot}%{_sharedstatedir}/cephadm
mkdir -p %{buildroot}%{_sharedstatedir}/cephadm/.ssh
chmod 0700 %{buildroot}%{_sharedstatedir}/cephadm/.ssh
touch %{buildroot}%{_sharedstatedir}/cephadm/.ssh/authorized_keys
chmod 0600 %{buildroot}%{_sharedstatedir}/cephadm/.ssh/authorized_keys

# firewall templates and /sbin/mount.ceph symlink
%if 0%{?suse_version} && !0%{?usrmerged}
mkdir -p %{buildroot}/sbin
ln -sf %{_sbindir}/mount.ceph %{buildroot}/sbin/mount.ceph
%endif

# udev rules
install -m 0644 -D udev/50-rbd.rules %{buildroot}%{_udevrulesdir}/50-rbd.rules

# sudoers.d
install -m 0440 -D sudoers.d/ceph-smartctl %{buildroot}%{_sysconfdir}/sudoers.d/ceph-smartctl

%if 0%{?rhel} >= 8
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{_bindir}/*
pathfix.py -pni "%{__python3} %{py3_shbang_opts}" %{buildroot}%{_sbindir}/*
%endif

#set up placeholder directories
mkdir -p %{buildroot}%{_sysconfdir}/ceph
mkdir -p %{buildroot}%{_localstatedir}/run/ceph
mkdir -p %{buildroot}%{_localstatedir}/log/ceph
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/tmp
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/mon
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/osd
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/mds
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/mgr
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/crash
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/crash/posted
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/radosgw
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-osd
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-mds
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-rgw
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-mgr
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-rbd
mkdir -p %{buildroot}%{_localstatedir}/lib/ceph/bootstrap-rbd-mirror

# prometheus alerts
install -m 644 -D monitoring/ceph-mixin/prometheus_alerts.yml %{buildroot}/etc/prometheus/ceph/ceph_default_alerts.yml

%if 0%{?suse_version}
# create __pycache__ directories and their contents
%py3_compile %{buildroot}%{python3_sitelib}
# hardlink duplicate files under /usr to save space
%fdupes %{buildroot}%{_prefix}
%endif

%if 0%{?rhel} == 8 || 0%{?fedora} >= 33
%py_byte_compile %{__python3} %{buildroot}%{python3_sitelib}
%endif

#################################################################################
# files and systemd scriptlets
#################################################################################
%files

%files base
%{_bindir}/ceph-crash
%{_bindir}/crushtool
%{_bindir}/monmaptool
%{_bindir}/osdmaptool
%{_bindir}/ceph-kvstore-tool
%{_bindir}/ceph-run
%{_presetdir}/50-ceph.preset
%{_sbindir}/ceph-create-keys
%dir %{_libexecdir}/ceph
%{_libexecdir}/ceph/ceph_common.sh
%dir %{_libdir}/rados-classes
%{_libdir}/rados-classes/*
%dir %{_libdir}/ceph
%dir %{_libdir}/ceph/erasure-code
%{_libdir}/ceph/erasure-code/libec_*.so*
%dir %{_libdir}/ceph/compressor
%{_libdir}/ceph/compressor/libceph_*.so*
%{_unitdir}/ceph-crash.service
%dir %{_libdir}/ceph/crypto
%{_libdir}/ceph/crypto/libceph_*.so*
%if %{with lttng}
%{_libdir}/libos_tp.so*
%{_libdir}/libosd_tp.so*
%endif
%config(noreplace) %{_sysconfdir}/logrotate.d/ceph
%if 0%{?fedora} || 0%{?rhel}
%config(noreplace) %{_sysconfdir}/sysconfig/ceph
%endif
%if 0%{?suse_version}
%{_fillupdir}/sysconfig.*
%endif
%{_unitdir}/ceph.target
%{_mandir}/man8/ceph-create-keys.8*
%{_mandir}/man8/ceph-run.8*
%{_mandir}/man8/crushtool.8*
%{_mandir}/man8/osdmaptool.8*
%{_mandir}/man8/monmaptool.8*
%{_mandir}/man8/ceph-kvstore-tool.8*
#set up placeholder directories
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/crash
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/crash/posted
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/tmp
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-osd
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-mds
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-rgw
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-mgr
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-rbd
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/bootstrap-rbd-mirror
%{_sysconfdir}/sudoers.d/ceph-smartctl

%post base
/sbin/ldconfig
%if 0%{?suse_version}
%fillup_only
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl preset ceph.target ceph-crash.service >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph.target ceph-crash.service
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph.target ceph-crash.service >/dev/null 2>&1 || :
fi

%preun base
%if 0%{?suse_version}
%service_del_preun ceph.target ceph-crash.service
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph.target ceph-crash.service
%endif

%postun base
/sbin/ldconfig
%systemd_postun ceph.target

%pre -n cephadm
getent group cephadm >/dev/null || groupadd -r cephadm
getent passwd cephadm >/dev/null || useradd -r -g cephadm -s /bin/bash -c "cephadm user for mgr/cephadm" -d %{_sharedstatedir}/cephadm cephadm
exit 0

%if ! 0%{?suse_version}
%postun -n cephadm
[ $1 -ne 0 ] || userdel cephadm || :
%endif

%files -n cephadm
%{_sbindir}/cephadm
%{_mandir}/man8/cephadm.8*
%attr(0700,cephadm,cephadm) %dir %{_sharedstatedir}/cephadm
%attr(0700,cephadm,cephadm) %dir %{_sharedstatedir}/cephadm/.ssh
%config(noreplace) %attr(0600,cephadm,cephadm) %{_sharedstatedir}/cephadm/.ssh/authorized_keys

%files common
%dir %{_docdir}/ceph
%doc %{_docdir}/ceph/sample.ceph.conf
%license %{_docdir}/ceph/COPYING
%{_bindir}/ceph
%{_bindir}/ceph-authtool
%{_bindir}/ceph-conf
%{_bindir}/ceph-dencoder
%{_bindir}/ceph-rbdnamer
%{_bindir}/ceph-syn
%{_bindir}/cephfs-data-scan
%{_bindir}/cephfs-journal-tool
%{_bindir}/cephfs-table-tool
%{_bindir}/crushdiff
%{_bindir}/rados
%{_bindir}/radosgw-admin
%{_bindir}/rbd
%{_bindir}/rbd-replay
%{_bindir}/rbd-replay-many
%{_bindir}/rbdmap
%{_sbindir}/mount.ceph
%if 0%{?suse_version} && !0%{?usrmerged}
/sbin/mount.ceph
%endif
%if %{with lttng}
%{_bindir}/rbd-replay-prep
%endif
%{_bindir}/ceph-post-file
%dir %{_libdir}/ceph/denc
%{_libdir}/ceph/denc/denc-mod-*.so
%{_tmpfilesdir}/ceph-common.conf
%{_mandir}/man8/ceph-authtool.8*
%{_mandir}/man8/ceph-conf.8*
%{_mandir}/man8/ceph-dencoder.8*
%{_mandir}/man8/ceph-diff-sorted.8*
%{_mandir}/man8/ceph-rbdnamer.8*
%{_mandir}/man8/ceph-syn.8*
%{_mandir}/man8/ceph-post-file.8*
%{_mandir}/man8/ceph.8*
%{_mandir}/man8/crushdiff.8*
%{_mandir}/man8/mount.ceph.8*
%{_mandir}/man8/rados.8*
%{_mandir}/man8/radosgw-admin.8*
%{_mandir}/man8/rbd.8*
%{_mandir}/man8/rbdmap.8*
%{_mandir}/man8/rbd-replay.8*
%{_mandir}/man8/rbd-replay-many.8*
%{_mandir}/man8/rbd-replay-prep.8*
%{_mandir}/man8/rgw-orphan-list.8*
%dir %{_datadir}/ceph/
%{_datadir}/ceph/known_hosts_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com
%{_datadir}/ceph/id_rsa_drop.ceph.com.pub
%dir %{_sysconfdir}/ceph/
%config %{_sysconfdir}/bash_completion.d/ceph
%config %{_sysconfdir}/bash_completion.d/rados
%config %{_sysconfdir}/bash_completion.d/rbd
%config %{_sysconfdir}/bash_completion.d/radosgw-admin
%config(noreplace) %{_sysconfdir}/ceph/rbdmap
%{_unitdir}/rbdmap.service
%{_udevrulesdir}/50-rbd.rules
%attr(3770,ceph,ceph) %dir %{_localstatedir}/log/ceph/
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/

%pre common
CEPH_GROUP_ID=167
CEPH_USER_ID=167
%if 0%{?rhel} || 0%{?fedora}
/usr/sbin/groupadd ceph -g $CEPH_GROUP_ID -o -r 2>/dev/null || :
/usr/sbin/useradd ceph -u $CEPH_USER_ID -o -r -g ceph -s /sbin/nologin -c "Ceph daemons" -d %{_localstatedir}/lib/ceph 2>/dev/null || :
%endif
%if 0%{?suse_version}
if ! getent group ceph >/dev/null ; then
    CEPH_GROUP_ID_OPTION=""
    getent group $CEPH_GROUP_ID >/dev/null || CEPH_GROUP_ID_OPTION="-g $CEPH_GROUP_ID"
    groupadd ceph $CEPH_GROUP_ID_OPTION -r 2>/dev/null || :
fi
if ! getent passwd ceph >/dev/null ; then
    CEPH_USER_ID_OPTION=""
    getent passwd $CEPH_USER_ID >/dev/null || CEPH_USER_ID_OPTION="-u $CEPH_USER_ID"
    useradd ceph $CEPH_USER_ID_OPTION -r -g ceph -s /sbin/nologin 2>/dev/null || :
fi
usermod -c "Ceph storage service" \
        -d %{_localstatedir}/lib/ceph \
        -g ceph \
        -s /sbin/nologin \
        ceph
%endif
exit 0

%post common
%tmpfiles_create %{_tmpfilesdir}/ceph-common.conf

%postun common
# Package removal cleanup
if [ "$1" -eq "0" ] ; then
    rm -rf %{_localstatedir}/log/ceph
    rm -rf %{_sysconfdir}/ceph
fi

%files mds
%{_bindir}/ceph-mds
%{_mandir}/man8/ceph-mds.8*
%{_unitdir}/ceph-mds@.service
%{_unitdir}/ceph-mds.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mds

%post mds
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-mds@\*.service ceph-mds.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-mds@\*.service ceph-mds.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-mds.target >/dev/null 2>&1 || :
fi

%preun mds
%if 0%{?suse_version}
%service_del_preun ceph-mds@\*.service ceph-mds.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-mds@\*.service ceph-mds.target
%endif

%postun mds
%systemd_postun ceph-mds@\*.service ceph-mds.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-mds@\*.service > /dev/null 2>&1 || :
  fi
fi

%files mgr
%{_bindir}/ceph-mgr
%dir %{_datadir}/ceph/mgr
%{_datadir}/ceph/mgr/mgr_module.*
%{_datadir}/ceph/mgr/mgr_util.*
%{_datadir}/ceph/mgr/object_format.*
%{_unitdir}/ceph-mgr@.service
%{_unitdir}/ceph-mgr.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mgr

%post mgr
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-mgr@\*.service ceph-mgr.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-mgr@\*.service ceph-mgr.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-mgr.target >/dev/null 2>&1 || :
fi

%preun mgr
%if 0%{?suse_version}
%service_del_preun ceph-mgr@\*.service ceph-mgr.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-mgr@\*.service ceph-mgr.target
%endif

%postun mgr
%systemd_postun ceph-mgr@\*.service ceph-mgr.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-mgr@\*.service > /dev/null 2>&1 || :
  fi
fi

%files mgr-dashboard
%{_datadir}/ceph/mgr/dashboard

%post mgr-dashboard
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%postun mgr-dashboard
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%files mgr-diskprediction-local
%{_datadir}/ceph/mgr/diskprediction_local

%post mgr-diskprediction-local
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%postun mgr-diskprediction-local
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%files mgr-modules-core
%dir %{_datadir}/ceph/mgr
%{_datadir}/ceph/mgr/alerts
%{_datadir}/ceph/mgr/balancer
%{_datadir}/ceph/mgr/crash
%{_datadir}/ceph/mgr/devicehealth
%{_datadir}/ceph/mgr/influx
%{_datadir}/ceph/mgr/insights
%{_datadir}/ceph/mgr/iostat
%{_datadir}/ceph/mgr/localpool
%{_datadir}/ceph/mgr/mds_autoscaler
%{_datadir}/ceph/mgr/mirroring
%{_datadir}/ceph/mgr/nfs
%{_datadir}/ceph/mgr/orchestrator
%{_datadir}/ceph/mgr/osd_perf_query
%{_datadir}/ceph/mgr/osd_support
%{_datadir}/ceph/mgr/pg_autoscaler
%{_datadir}/ceph/mgr/progress
%{_datadir}/ceph/mgr/prometheus
%{_datadir}/ceph/mgr/rbd_support
%{_datadir}/ceph/mgr/restful
%{_datadir}/ceph/mgr/selftest
%{_datadir}/ceph/mgr/snap_schedule
%{_datadir}/ceph/mgr/stats
%{_datadir}/ceph/mgr/status
%{_datadir}/ceph/mgr/telegraf
%{_datadir}/ceph/mgr/telemetry
%{_datadir}/ceph/mgr/test_orchestrator
%{_datadir}/ceph/mgr/volumes
%{_datadir}/ceph/mgr/zabbix

%files mgr-rook
%{_datadir}/ceph/mgr/rook

%post mgr-rook
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%postun mgr-rook
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%files mgr-k8sevents
%{_datadir}/ceph/mgr/k8sevents

%post mgr-k8sevents
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%postun mgr-k8sevents
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%files mgr-cephadm
%{_datadir}/ceph/mgr/cephadm

%post mgr-cephadm
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%postun mgr-cephadm
if [ $1 -eq 1 ] ; then
    /usr/bin/systemctl try-restart ceph-mgr.target >/dev/null 2>&1 || :
fi

%files mon
%{_bindir}/ceph-mon
%{_bindir}/ceph-monstore-tool
%{_mandir}/man8/ceph-mon.8*
%{_unitdir}/ceph-mon@.service
%{_unitdir}/ceph-mon.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/mon

%post mon
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-mon@\*.service ceph-mon.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-mon@\*.service ceph-mon.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-mon.target >/dev/null 2>&1 || :
fi

%preun mon
%if 0%{?suse_version}
%service_del_preun ceph-mon@\*.service ceph-mon.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-mon@\*.service ceph-mon.target
%endif

%postun mon
%systemd_postun ceph-mon@\*.service ceph-mon.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-mon@\*.service > /dev/null 2>&1 || :
  fi
fi

%files fuse
%{_bindir}/ceph-fuse
%{_mandir}/man8/ceph-fuse.8*
%{_sbindir}/mount.fuse.ceph
%{_mandir}/man8/mount.fuse.ceph.8*
%{_unitdir}/ceph-fuse@.service
%{_unitdir}/ceph-fuse.target

%files -n cephfs-mirror
%{_bindir}/cephfs-mirror
%{_mandir}/man8/cephfs-mirror.8*
%{_unitdir}/cephfs-mirror@.service
%{_unitdir}/cephfs-mirror.target

%post -n cephfs-mirror
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset cephfs-mirror@\*.service cephfs-mirror.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post cephfs-mirror@\*.service cephfs-mirror.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start cephfs-mirror.target >/dev/null 2>&1 || :
fi

%preun -n cephfs-mirror
%if 0%{?suse_version}
%service_del_preun cephfs-mirror@\*.service cephfs-mirror.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun cephfs-mirror@\*.service cephfs-mirror.target
%endif

%postun -n cephfs-mirror
%systemd_postun cephfs-mirror@\*.service cephfs-mirror.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart cephfs-mirror@\*.service > /dev/null 2>&1 || :
  fi
fi

%files -n ceph-exporter
%{_bindir}/ceph-exporter

%files -n rbd-fuse
%{_bindir}/rbd-fuse
%{_mandir}/man8/rbd-fuse.8*

%files -n rbd-mirror
%{_bindir}/rbd-mirror
%{_mandir}/man8/rbd-mirror.8*
%{_unitdir}/ceph-rbd-mirror@.service
%{_unitdir}/ceph-rbd-mirror.target

%post -n rbd-mirror
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-rbd-mirror@\*.service ceph-rbd-mirror.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-rbd-mirror.target >/dev/null 2>&1 || :
fi

%preun -n rbd-mirror
%if 0%{?suse_version}
%service_del_preun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
%endif

%postun -n rbd-mirror
%systemd_postun ceph-rbd-mirror@\*.service ceph-rbd-mirror.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-rbd-mirror@\*.service > /dev/null 2>&1 || :
  fi
fi

%files immutable-object-cache
%{_bindir}/ceph-immutable-object-cache
%{_mandir}/man8/ceph-immutable-object-cache.8*
%{_unitdir}/ceph-immutable-object-cache@.service
%{_unitdir}/ceph-immutable-object-cache.target

%post immutable-object-cache
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-immutable-object-cache@\*.service ceph-immutable-object-cache.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-immutable-object-cache@\*.service ceph-immutable-object-cache.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-immutable-object-cache.target >/dev/null 2>&1 || :
fi

%preun immutable-object-cache
%if 0%{?suse_version}
%service_del_preun ceph-immutable-object-cache@\*.service ceph-immutable-object-cache.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-immutable-object-cache@\*.service ceph-immutable-object-cache.target
%endif

%postun immutable-object-cache
%systemd_postun ceph-immutable-object-cache@\*.service ceph-immutable-object-cache.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-immutable-object-cache@\*.service > /dev/null 2>&1 || :
  fi
fi

%files -n rbd-nbd
%{_bindir}/rbd-nbd
%{_mandir}/man8/rbd-nbd.8*
%dir %{_libexecdir}/rbd-nbd
%{_libexecdir}/rbd-nbd/rbd-nbd_quiesce

%files radosgw
%{_bindir}/ceph-diff-sorted
%{_bindir}/radosgw
%{_bindir}/radosgw-token
%{_bindir}/radosgw-es
%{_bindir}/radosgw-object-expirer
%{_bindir}/rgw-gap-list
%{_bindir}/rgw-gap-list-comparator
%{_bindir}/rgw-orphan-list
%{_libdir}/libradosgw.so*
%{_mandir}/man8/radosgw.8*
%dir %{_localstatedir}/lib/ceph/radosgw
%{_unitdir}/ceph-radosgw@.service
%{_unitdir}/ceph-radosgw.target

%post radosgw
/sbin/ldconfig
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-radosgw@\*.service ceph-radosgw.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-radosgw@\*.service ceph-radosgw.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-radosgw.target >/dev/null 2>&1 || :
fi

%preun radosgw
%if 0%{?suse_version}
%service_del_preun ceph-radosgw@\*.service ceph-radosgw.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-radosgw@\*.service ceph-radosgw.target
%endif

%postun radosgw
/sbin/ldconfig
%systemd_postun ceph-radosgw@\*.service ceph-radosgw.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-radosgw@\*.service > /dev/null 2>&1 || :
  fi
fi

%files osd
%{_bindir}/ceph-clsinfo
%{_bindir}/ceph-bluestore-tool
%{_bindir}/ceph-erasure-code-tool
%{_bindir}/ceph-objectstore-tool
%{_bindir}/ceph-osdomap-tool
%{_bindir}/ceph-osd
%{_libexecdir}/ceph/ceph-osd-prestart.sh
%{_mandir}/man8/ceph-clsinfo.8*
%{_mandir}/man8/ceph-osd.8*
%{_mandir}/man8/ceph-bluestore-tool.8*
%{_unitdir}/ceph-osd@.service
%{_unitdir}/ceph-osd.target
%attr(750,ceph,ceph) %dir %{_localstatedir}/lib/ceph/osd
%config(noreplace) %{_sysctldir}/90-ceph-osd.conf

%post osd
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-osd@\*.service ceph-osd.target >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-osd@\*.service ceph-volume@\*.service ceph-osd.target
%endif
if [ $1 -eq 1 ] ; then
/usr/bin/systemctl start ceph-osd.target >/dev/null 2>&1 || :
fi
%if 0%{?sysctl_apply}
    %sysctl_apply 90-ceph-osd.conf
%else
    /usr/lib/systemd/systemd-sysctl %{_sysctldir}/90-ceph-osd.conf > /dev/null 2>&1 || :
%endif

%preun osd
%if 0%{?suse_version}
%service_del_preun ceph-osd@\*.service ceph-osd.target
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-osd@\*.service ceph-osd.target
%endif

%postun osd
%systemd_postun ceph-osd@\*.service ceph-volume@\*.service ceph-osd.target
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-osd@\*.service ceph-volume@\*.service > /dev/null 2>&1 || :
  fi
fi

%if 0%{with seastar}
%files crimson-osd
%{_bindir}/crimson-osd
%endif

%files volume
%{_sbindir}/ceph-volume
%{_sbindir}/ceph-volume-systemd
%dir %{python3_sitelib}/ceph_volume
%{python3_sitelib}/ceph_volume/*
%{python3_sitelib}/ceph_volume-*
%{_mandir}/man8/ceph-volume.8*
%{_mandir}/man8/ceph-volume-systemd.8*
%{_unitdir}/ceph-volume@.service

%post volume
%if 0%{?suse_version}
if [ $1 -eq 1 ] ; then
  /usr/bin/systemctl preset ceph-volume@\*.service >/dev/null 2>&1 || :
fi
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_post ceph-volume@\*.service
%endif

%preun volume
%if 0%{?suse_version}
%service_del_preun ceph-volume@\*.service
%endif
%if 0%{?fedora} || 0%{?rhel}
%systemd_preun ceph-volume@\*.service
%endif

%postun volume
%systemd_postun ceph-volume@\*.service
if [ $1 -ge 1 ] ; then
  # Restart on upgrade, but only if "CEPH_AUTO_RESTART_ON_UPGRADE" is set to
  # "yes". In any case: if units are not running, do not touch them.
  SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
  if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
  fi
  if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
    /usr/bin/systemctl try-restart ceph-volume@\*.service > /dev/null 2>&1 || :
  fi
fi

%if %{with ocf}

%files resource-agents
%dir %{_prefix}/lib/ocf
%dir %{_prefix}/lib/ocf/resource.d
%dir %{_prefix}/lib/ocf/resource.d/ceph
%attr(0755,-,-) %{_prefix}/lib/ocf/resource.d/ceph/rbd

%endif

%files -n librados2
%{_libdir}/librados.so.*
%dir %{_libdir}/ceph
%{_libdir}/ceph/libceph-common.so.*
%if %{with lttng}
%{_libdir}/librados_tp.so.*
%endif
%dir %{_sysconfdir}/ceph

%post -n librados2 -p /sbin/ldconfig

%postun -n librados2 -p /sbin/ldconfig

%files -n librados-devel
%dir %{_includedir}/rados
%{_includedir}/rados/librados.h
%{_includedir}/rados/rados_types.h
%{_libdir}/librados.so
%if %{with lttng}
%{_libdir}/librados_tp.so
%endif
%{_bindir}/librados-config
%{_mandir}/man8/librados-config.8*

%files -n libradospp-devel
%dir %{_includedir}/rados
%{_includedir}/rados/buffer.h
%{_includedir}/rados/buffer_fwd.h
%{_includedir}/rados/crc32c.h
%{_includedir}/rados/inline_memory.h
%{_includedir}/rados/librados.hpp
%{_includedir}/rados/librados_fwd.hpp
%{_includedir}/rados/page.h
%{_includedir}/rados/rados_types.hpp

%files -n python%{python3_pkgversion}-rados
%{python3_sitearch}/rados.cpython*.so
%{python3_sitearch}/rados-*.egg-info

%files -n libcephsqlite
%{_libdir}/libcephsqlite.so

%post -n libcephsqlite -p /sbin/ldconfig

%postun -n libcephsqlite -p /sbin/ldconfig

%files -n libcephsqlite-devel
%{_includedir}/libcephsqlite.h

%if 0%{with libradosstriper}
%files -n libradosstriper1
%{_libdir}/libradosstriper.so.*

%post -n libradosstriper1 -p /sbin/ldconfig

%postun -n libradosstriper1 -p /sbin/ldconfig

%files -n libradosstriper-devel
%dir %{_includedir}/radosstriper
%{_includedir}/radosstriper/libradosstriper.h
%{_includedir}/radosstriper/libradosstriper.hpp
%{_libdir}/libradosstriper.so
%endif

%files -n librbd1
%{_libdir}/librbd.so.*
%if %{with lttng}
%{_libdir}/librbd_tp.so.*
%endif
%dir %{_libdir}/ceph/librbd
%{_libdir}/ceph/librbd/libceph_*.so*

%post -n librbd1 -p /sbin/ldconfig

%postun -n librbd1 -p /sbin/ldconfig

%files -n librbd-devel
%dir %{_includedir}/rbd
%{_includedir}/rbd/librbd.h
%{_includedir}/rbd/librbd.hpp
%{_includedir}/rbd/features.h
%{_libdir}/librbd.so
%if %{with lttng}
%{_libdir}/librbd_tp.so
%endif

%files -n librgw2
%{_libdir}/librgw.so.*
%if %{with lttng}
%{_libdir}/librgw_op_tp.so.*
%{_libdir}/librgw_rados_tp.so.*
%endif

%post -n librgw2 -p /sbin/ldconfig

%postun -n librgw2 -p /sbin/ldconfig

%files -n librgw-devel
%dir %{_includedir}/rados
%{_includedir}/rados/librgw.h
%{_includedir}/rados/rgw_file.h
%{_libdir}/librgw.so
%if %{with lttng}
%{_libdir}/librgw_op_tp.so
%{_libdir}/librgw_rados_tp.so
%endif

%files -n python%{python3_pkgversion}-rgw
%{python3_sitearch}/rgw.cpython*.so
%{python3_sitearch}/rgw-*.egg-info

%files -n python%{python3_pkgversion}-rbd
%{python3_sitearch}/rbd.cpython*.so
%{python3_sitearch}/rbd-*.egg-info

%files -n libcephfs2
%{_libdir}/libcephfs.so.*
%dir %{_sysconfdir}/ceph

%post -n libcephfs2 -p /sbin/ldconfig

%postun -n libcephfs2 -p /sbin/ldconfig

%files -n libcephfs-devel
%dir %{_includedir}/cephfs
%{_includedir}/cephfs/libcephfs.h
%{_includedir}/cephfs/ceph_ll_client.h
%dir %{_includedir}/cephfs/metrics
%{_includedir}/cephfs/metrics/Types.h
%{_libdir}/libcephfs.so

%files -n python%{python3_pkgversion}-cephfs
%{python3_sitearch}/cephfs.cpython*.so
%{python3_sitearch}/cephfs-*.egg-info

%files -n python%{python3_pkgversion}-ceph-argparse
%{python3_sitelib}/ceph_argparse.py
%{python3_sitelib}/__pycache__/ceph_argparse.cpython*.py*
%{python3_sitelib}/ceph_daemon.py
%{python3_sitelib}/__pycache__/ceph_daemon.cpython*.py*

%files -n python%{python3_pkgversion}-ceph-common
%{python3_sitelib}/ceph
%{python3_sitelib}/ceph-*.egg-info

%if 0%{with cephfs_shell}
%files -n cephfs-shell
%{python3_sitelib}/cephfs_shell-*.egg-info
%{_bindir}/cephfs-shell
%{_mandir}/man8/cephfs-shell.8*
%endif

%files -n cephfs-top
%{python3_sitelib}/cephfs_top-*.egg-info
%{_bindir}/cephfs-top
%{_mandir}/man8/cephfs-top.8*

%if 0%{with ceph_test_package}
%files -n ceph-test
%{_bindir}/ceph-client-debug
%{_bindir}/ceph_bench_log
%{_bindir}/ceph_multi_stress_watch
%{_bindir}/ceph_erasure_code_benchmark
%{_bindir}/ceph_omapbench
%{_bindir}/ceph_objectstore_bench
%{_bindir}/ceph_perf_objectstore
%{_bindir}/ceph_perf_local
%{_bindir}/ceph_perf_msgr_client
%{_bindir}/ceph_perf_msgr_server
%{_bindir}/ceph_psim
%{_bindir}/ceph_radosacl
%{_bindir}/ceph_rgw_jsonparser
%{_bindir}/ceph_rgw_multiparser
%{_bindir}/ceph_scratchtool
%{_bindir}/ceph_scratchtoolpp
%{_bindir}/ceph_test_*
%{_bindir}/ceph-coverage
%{_bindir}/ceph-debugpack
%{_bindir}/ceph-dedup-tool
%if 0%{with seastar}
%{_bindir}/crimson-store-nbd
%endif
%{_mandir}/man8/ceph-debugpack.8*
%dir %{_libdir}/ceph
%{_libdir}/ceph/ceph-monstore-update-crush.sh
%endif

%if 0%{with cephfs_java}
%files -n libcephfs_jni1
%{_libdir}/libcephfs_jni.so.*

%post -n libcephfs_jni1 -p /sbin/ldconfig

%postun -n libcephfs_jni1 -p /sbin/ldconfig

%files -n libcephfs_jni-devel
%{_libdir}/libcephfs_jni.so

%files -n cephfs-java
%{_javadir}/libcephfs.jar
%{_javadir}/libcephfs-test.jar
%endif

%files -n rados-objclass-devel
%dir %{_includedir}/rados
%{_includedir}/rados/objclass.h

%if 0%{with selinux}
%files selinux
%attr(0600,root,root) %{_datadir}/selinux/packages/ceph.pp
%{_datadir}/selinux/devel/include/contrib/ceph.if
%{_mandir}/man8/ceph_selinux.8*

%post selinux
# backup file_contexts before update
. /etc/selinux/config
FILE_CONTEXT=/etc/selinux/${SELINUXTYPE}/contexts/files/file_contexts
cp ${FILE_CONTEXT} ${FILE_CONTEXT}.pre

# Install the policy
/usr/sbin/semodule -i %{_datadir}/selinux/packages/ceph.pp

# Load the policy if SELinux is enabled
if ! /usr/sbin/selinuxenabled; then
    # Do not relabel if selinux is not enabled
    exit 0
fi

if diff ${FILE_CONTEXT} ${FILE_CONTEXT}.pre > /dev/null 2>&1; then
   # Do not relabel if file contexts did not change
   exit 0
fi

# Stop ceph.target while relabeling if CEPH_AUTO_RESTART_ON_UPGRADE=yes
SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
    source $SYSCONF_CEPH
fi

# Check whether the daemons are running
/usr/bin/systemctl status ceph.target > /dev/null 2>&1
STATUS=$?

# Stop the daemons if they were running
if test $STATUS -eq 0; then
    if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
        /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
    fi
fi

# Relabel the files fix for first package install
/usr/sbin/fixfiles -C ${FILE_CONTEXT}.pre restore 2> /dev/null

rm -f ${FILE_CONTEXT}.pre
# The fixfiles command won't fix label for /var/run/ceph
/usr/sbin/restorecon -R /var/run/ceph > /dev/null 2>&1

# Start the daemons iff they were running before
if test $STATUS -eq 0; then
    if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
        /usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
    fi
fi
exit 0

%postun selinux
if [ $1 -eq 0 ]; then
    # backup file_contexts before update
    . /etc/selinux/config
    FILE_CONTEXT=/etc/selinux/${SELINUXTYPE}/contexts/files/file_contexts
    cp ${FILE_CONTEXT} ${FILE_CONTEXT}.pre

    # Remove the module
    /usr/sbin/semodule -n -r ceph > /dev/null 2>&1

    # Reload the policy if SELinux is enabled
    if ! /usr/sbin/selinuxenabled ; then
        # Do not relabel if SELinux is not enabled
        exit 0
    fi

    # Stop ceph.target while relabeling if CEPH_AUTO_RESTART_ON_UPGRADE=yes
    SYSCONF_CEPH=%{_sysconfdir}/sysconfig/ceph
    if [ -f $SYSCONF_CEPH -a -r $SYSCONF_CEPH ] ; then
        source $SYSCONF_CEPH
    fi

    # Check whether the daemons are running
    /usr/bin/systemctl status ceph.target > /dev/null 2>&1
    STATUS=$?

    # Stop the daemons if they were running
    if test $STATUS -eq 0; then
        if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
            /usr/bin/systemctl stop ceph.target > /dev/null 2>&1
        fi
    fi

    /usr/sbin/fixfiles -C ${FILE_CONTEXT}.pre restore 2> /dev/null
    rm -f ${FILE_CONTEXT}.pre
    # The fixfiles command won't fix label for /var/run/ceph
    /usr/sbin/restorecon -R /var/run/ceph > /dev/null 2>&1

    # Start the daemons if they were running before
    if test $STATUS -eq 0; then
        if [ "X$CEPH_AUTO_RESTART_ON_UPGRADE" = "Xyes" ] ; then
           /usr/bin/systemctl start ceph.target > /dev/null 2>&1 || :
        fi
    fi
fi
exit 0
%endif

%files grafana-dashboards
%if 0%{?suse_version}
%attr(0755,root,root) %dir %{_sysconfdir}/grafana
%attr(0755,root,root) %dir %{_sysconfdir}/grafana/dashboards
%endif
%attr(0755,root,root) %dir %{_sysconfdir}/grafana/dashboards/ceph-dashboard
%config %{_sysconfdir}/grafana/dashboards/ceph-dashboard/*

%files prometheus-alerts
%if 0%{?suse_version}
%attr(0755,root,root) %dir %{_sysconfdir}/prometheus
%endif
%attr(0755,root,root) %dir %{_sysconfdir}/prometheus/ceph
%config %{_sysconfdir}/prometheus/ceph/ceph_default_alerts.yml

%changelog
* Fri Feb 17 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-11
- ceph-17.2.5, rebuild with libarrow-11, this time for real

* Wed Feb 15 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-10
- ceph-17.2.5, rebuild with libarrow-11

* Fri Jan 27 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-9
- ceph-17.2.5, more ELN (rhel 10)

* Thu Jan 26 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-8
- ceph-17.2.5, rocksdb on ELN (rhel 10)

* Tue Jan 24 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-7
- ceph-17.2.5, rebuild with gtest-13 rhbz#2163823

* Fri Jan 20 2023 Siddhesh Poyarekar <siddhesh@redhat.com> - 2:17.2.5-6
- Use _fortify_level to disable fortification.

* Thu Jan 19 2023 Ondrej Mosnacek <omosnace@redhat.com>
- Prepare for anon inode SELinux controls enablement

* Wed Jan 18 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2:17.2.5-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Tue Jan 17 2023 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-4
- ceph-17.2.5, rebuild with gcc-13

* Sat Dec 31 2022 Pete Walter <pwalter@fedoraproject.org> - 2:17.2.5-3
- Rebuild for ICU 72

* Thu Dec 1 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-2
- ceph-17.2.5, rebuild with libarrow-10

* Fri Nov 11 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- SPDX migration

* Tue Oct 18 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.5-1
- ceph-17.2.5 GA

* Fri Sep 30 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.4-1
- ceph-17.2.4 GA

* Mon Aug 22 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.3-5
- ceph-17.2.3 revised patch for libarrow-9.0.0

* Wed Aug 3 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.3-4
- ceph-17.2.3 rebuild with libarrow-9.0.0

* Wed Aug 3 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.3-3
- ceph-17.2.3 fmt for ELN

* Mon Aug 01 2022 Frantisek Zatloukal <fzatlouk@redhat.com> - 2:17.2.3-2
- Rebuilt for ICU 71.1

* Fri Jul 29 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.3-1
- ceph-17.2.3 GA

* Fri Jul 22 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.2-1
- ceph-17.2.2 GA

* Wed Jul 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2:17.2.1-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jul 18 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.1-6
- Rebuild for fmt-9, src/mon/LogMonitor.cc fix

* Sun Jul 17 2022 Robert-André Mauchin <zebob.m@gmail.com> - 2:17.2.1-5
- Rebuild for new fmt

* Sun Jul 10 2022 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2:17.2.1-4
- Rebuild for new gtest

* Wed Jul 6 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.1-3
- enable cephfs-shell

* Tue Jun 28 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.1-2
- ceph-17.2.1, rhbz#2101744, rebuild with gtest, gmock 1.12.0
- fix inconsistent tabs, spaces
- temporarily disable cephfs-shell until install issues (python3-11?) are resolved

* Thu Jun 23 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.1-1
- ceph-17.2.1 GA

* Fri Jun 17 2022 Robert-André Mauchin <zebob.m@gmail.com> - 2:17.2.0-7
- Rebuilt for CVE-2022-1996, CVE-2022-24675, CVE-2022-28327, CVE-2022-27191,
  CVE-2022-29526, CVE-2022-30629

* Wed Jun 15 2022 Python Maint <python-maint@redhat.com> - 2:17.2.0-6
- Rebuilt for Python 3.11

* Thu May 19 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.0-5
- Rebuild for rocksdb 7.2.2

* Wed May 11 2022 Thomas Rodgers <trodgers@redhat.com> - 2:17.2.0-4
- Rebuilt for Boost 1.78

* Wed May 4 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.0-3
- 17.2.0 w/ -DWITH_SYSTEM_ARROW

* Wed May 04 2022 Thomas Rodgers <trodgers@redhat.com> - 2:17.2.0-2
- Rebuilt for Boost 1.78

* Wed Apr 20 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.2.0-1
- 17.2.0 GA

* Thu Apr 14 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.10.201.gcc420538
- 17.1.0 snapshot 201

* Fri Apr 8 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.9.175.g086c8f84
- 17.1.0 snapshot 175

* Mon Mar 28 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.7.123.g14f44feb
- 17.1.0 snapshot 123

* Thu Mar 24 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.6.70-g06806b4d
- 17.1.0 snapshot 70

* Mon Mar 21 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.5.56-g60fdd357
- 17.1.0 snapshot 56

* Thu Mar 17 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.4.31-g1ccf6db7
- 17.1.0 snapshot 31 plus rhbz#2064219 (ceph #53266, #54561)

* Wed Mar 16 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.3.28-g77b78287
- 17.1.0 snapshot 28

* Sat Mar 12 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.2.rc1
- 17.1.0 RC1

* Mon Feb 28 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:17.1.0-0.1.rc1
- 17.1.0 RC1

* Sat Feb 05 2022 Jiri Vanek <jvanek@redhat.com> - 2:16.2.7-10
- Rebuilt for java-17-openjdk as system jdk

* Wed Feb 2 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-9
- 16.2.7, python3.10 w/ __CHAR_UNSIGNED__ fix

* Thu Jan 27 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-8
- 16.2.7, w/ modern linker (mold), x86_64 and aarch64, this time for real

* Wed Jan 26 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-7
- 16.2.7, build with modern linker (mold), x86_64 and aarch64
- reenable ppc64le

* Tue Jan 25 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-6
- 16.2.7, more CET enablement, rhbz#2040091

* Thu Jan 20 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-5
- 16.2.7, rebuild with gcc-12, exclude ppc64le until fmt on ppc64le is fixed

* Wed Jan 19 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2:16.2.7-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Mon Jan 10 2022 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-3
- 16.2.7, rebuild with fmt-8.1.1

* Wed Dec 29 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-2
- 16.2.7, LGPLv2.1 -> LGPLv2+, rhbz#2036035

* Tue Dec 7 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.7-1
- 16.2.7 GA

* Tue Nov 02 2021 Mamoru TASAKA <mtasaka@fedoraproject.org> - 2:16.2.6-3
- rebuild against new liblttng-ust

* Tue Oct 19 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.6-2
- 16.2.6, rebuild with rocksdb 6.25

* Fri Sep 17 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.6-1
- 16.2.6 GA

* Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 2:16.2.5-11
- Rebuilt with OpenSSL 3.0.0

* Mon Sep 6 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-10
- Rebuilt for gtest 1.11.0

* Thu Aug 26 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-9
- Rebuilt for rocksdb 6.22

* Tue Aug 17 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-8
- build with ninja, -DWITH_SYSTEM_ZSTD, without gdbm

* Sun Aug 8 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-7
- Rebuild for Boost 1.76 again

* Fri Aug 06 2021 Jonathan Wakely <jwakely@redhat.com> - 2:16.2.5-6
- Rebuilt for Boost 1.76

* Thu Aug 5 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-5
- Rebuild for leveldb-1.23-3 w/ reverted -fno-rtti

* Tue Aug 3 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-4
- Rebuild for leveldb-1.23

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2:16.2.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Thu Jul 8 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-2
- Rebuild for new fmt version.

* Thu Jul 8 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.5-1
- 16.2.5 GA

* Mon Jul 05 2021 Richard Shaw <hobbes1069@gmail.com> - 2:16.2.4-6
- Rebuild for new fmt version.

* Fri Jun 11 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.4-5
- https://src.fedoraproject.org/rpms/ceph/pull-request/3#

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 2:16.2.4-4
- Rebuilt for Python 3.10

* Wed May 26 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.4-3
- 16.2.4, bz 1964858, snappy::uint32

* Wed May 19 2021 Pete Walter <pwalter@fedoraproject.org> - 2:16.2.4-2
- Rebuild for ICU 69

* Thu May 13 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.4-1
- 16.2.4 GA

* Thu May 6 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.3-1
- 16.2.3 GA

* Wed May 5 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.2-1
- 16.2.2 GA

* Tue Apr 20 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.1-1
- 16.2.1 GA

* Wed Apr 14 2021 Richard W.M. Jones <rjones@redhat.com> - 2:16.2.0-3
- Rebuild for updated liburing.

* Sat Apr 10 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.0-2
- 16.2.0, libamqp_mock fix (FTBFS, #1947281), rgw fix

* Wed Mar 31 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.2.0-1
- 16.2.0 GA

* Tue Mar 30 2021 Jonathan Wakely <jwakely@redhat.com> - 2:16.1.0-2
- Rebuilt for removed libstdc++ symbol (#1937698)

* Thu Mar 25 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-1
- 16.1.0 RC

* Tue Mar 23 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.8.snapshot
- 16.1.0 RC (ceph-16.1.0-944-ge53ee8bd plus fix trailing slash bluestore)

* Sat Mar 20 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.7.snapshot
- 16.1.0 RC (ceph-16.1.0-944-ge53ee8bd)

* Fri Mar 19 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.6.snapshot
- 16.1.0 RC (ceph-16.1.0-308-gabe639eb)

* Fri Mar 5 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.5.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-308-gabe639eb)
-  rpmbuild apparently unable to automatically derive 'Requires: rocksdb' from 'BuildRequires: rocksdb-devel' for librocksdb.so.6.13

* Sat Feb 20 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.4.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-308-gabe639eb)

* Thu Feb 4 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.3.snapshot
- rocksdb not available in el8+, use bundled rocksdb

* Mon Feb 1 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.2.snapshot
- libblk.so -> libblk.a
- libneoradostest-support.so -> libneoradostest-support.a
- w/ liburing-devel, -DWITH_SYSTEM_LIBURING=ON
- w/ rocksdb-devel, -DWITH_SYSTEM_ROCKSDB=ON

* Fri Jan 29 2021 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:16.1.0-0.1.snapshot
- ceph 16.1.0 RC (ceph-16.1.0-43-g6b74fb5c)

* Wed Sep 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.5-1
- ceph 15.2.5 GA

* Wed Jul 29 2020 Richard W.M. Jones <rjones@redhat.com> - 2:15.2.4-11
- Rebuild against fmt 7.

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2:15.2.4-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jul 21 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-9
- %%cmake_build and %%cmake_install

* Mon Jul 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-8
- see 15.2.4-4 (f33-java11) for real this time
- and use %%make_install macro

* Mon Jul 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-7
- see 15.2.4-3, hopefully for real this time
- and use %%make_install macro

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-6
- see 15.2.4-4

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-5
- see 15.2.4-3

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-4
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Fri Jul 17 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-3
- use `ld -r -z ibt -z shstk...` instead of magic hackery to get CET ibt
  and shstk. N.B. updated yasm in f33/rawhide now has support for
  .note.gnu.properties so even this will go away in the next build
- signal_handler.cc, use HAVE_REENTRANT_STRSIGNAL, strsignal(3)

* Fri Jul 10 2020 Jiri Vanek <jvanek@redhat.com> - 2:15.2.4-2
- Rebuilt for JDK-11, see https://fedoraproject.org/wiki/Changes/Java11

* Wed Jul 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.4-1
- ceph 15.2.4 GA

* Tue Jun 23 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- explicit BuildRequires python3-setuptools

* Mon Jun 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.3-1
- ceph 15.2.3 GA

* Tue May 26 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.2-3
- ceph 15.2.2, CET enable src/common/crc32c_intel_*_asm.s; shstk, ibt
- and other fixes
- see https://github.com/intel/isa-l/blob/master/crc/crc32_iscsi_00.asm

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 2:15.2.2-2
- Rebuilt for Python 3.9

* Mon May 18 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.2-1
- ceph 15.2.2 GA

* Mon May 18 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.1-2
- ceph 15.2.1, gmock and gtest. (although gmock last built for f27)

* Fri Apr 10 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.1-1
- ceph 15.2.1 GA

* Mon Mar 23 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.2.0-1
- ceph 15.2.0 GA

* Mon Mar 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.1-2
- ceph 15.1.1 fmt, rhbz#1805422 again

* Mon Mar 16 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.1-1
- ceph 15.1.1 RC

* Thu Mar 5 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-3
- ceph 15.1.0, rhbz#1809799

* Thu Feb 20 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-2
- ceph 15.1.0, fmt, rhbz#1805422

* Tue Feb 11 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:15.1.0-1
- ceph 15.1.0 RC

* Mon Feb 3 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.7-2
- ceph 14.2.7 python3-remoto #1784216

* Sat Feb 1 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.7-1
- ceph 14.2.7 GA

* Wed Jan 29 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-4
- ceph 14.2.6, https://tracker.ceph.com/issues/43649

* Mon Jan 27 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-3
- ceph 14.2.6, (temporarily) disable unit tests

* Fri Jan 24 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- ceph 14.2.6, gcc-10, missing includes

* Thu Jan 9 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-2
- ceph 14.2.6

* Thu Jan 9 2020 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.6-1
- ceph 14.2.6 GA

* Tue Dec 10 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.5-1
- ceph 14.2.5 GA

* Mon Nov 11 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-3
- ceph 14.2.4, fix typo

* Tue Nov 5 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-2
- ceph 14.2.4, partial fix for bz#1768017

* Tue Sep 17 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.4-1
- ceph 14.2.4 GA

* Wed Sep 4 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.3-1
- ceph 14.2.3 GA

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 2:14.2.2-3
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:14.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri Jul 19 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.2-1
- ceph 14.2.2 GA

* Tue May 28 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.0-2
- numpy -> python3-numpy, bz#1712203 (and why I like to keep upstream
  and fedora .spec files in sync)

* Wed May 8 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- sync w/ upstream to minimize diffs/drift

* Mon Apr 29 2019 Boris Ranto <branto@redhat.com> - 2:14.2.1-1
- Rebase to latest upstream version (14.2.1)

* Tue Mar 19 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.2.0-1
- ceph 14.2.0 GA

* Wed Mar 13 2019 Boris Ranto <branto@redhat.com> - 2:14.1.1-1
- Rebase to latest upstream version

* Thu Mar 07 2019 Adam Williamson <awilliam@redhat.com> - 2:14.1.0-3
- Return epoch to 2, epochs cannot ever go backwards

* Wed Mar 6 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.1.0-2
- ceph 14.1.0 w/ static libcrc32

* Wed Feb 27 2019 Boris Ranto <branto@redhat.com> - 1:14.1.0-1
- Rebase to v14.1.0 (updated for fixes in upstream nautilus branch)

* Thu Feb 21 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.0.1-2
- Eliminate redundant CMAKE_* macros when using %%cmake global
- Add CMAKE_BUILD_TYPE=RelWithDeb(ug)Info and BUILD_CONFIG=rpmbuild

* Wed Feb 20 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:14.0.1-1
- rebuild for f31/rawhide, including:
- use the %%{cmake} %%global to get all the extra Fedora cmake options.
  (This is Fedora, so don't care so much about rhel/rhel7 cmake3.)
- reset epoch to 1. Note we use (have been using) epoch=1 in Fedora since
  forever. I presume this is so that people can install Ceph RPMs from
  ceph.com if they prefer those, which use epoch=2, and not run into issues
  when updating.

* Thu Feb 7 2019 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 2:14.0.1-4
- w/ fixes for gcc9

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:14.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Dec 08 2018 Boris Ranto <branto@redhat.com> - 2:14.0.1-2
- fix pyOpenSSL depemdency

* Tue Dec 04 2018 Boris Ranto <branto@redhat.com> - 2:14.0.1-1
- New release (2:14.0.1-1)
- Sync with upstream
- Drop 32-bit support

* Wed Nov 21 2018 Boris Ranto <branto@redhat.com> - 2:13.2.2-1
- New release (2:13.2.2-1)
- Sync with upstream

* Mon Oct 29 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.9-1
- New release (1:12.2.9-1)

* Wed Sep 12 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.8-2
- Fedora 30 python3. Note ceph-mgr subpackage, ceph-detect-init, ceph-disk,
  ceph-volume, and ceph-volume-systemd are missing in this build

* Fri Aug 31 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.8-1
- New release (1:12.2.8-1)

* Wed Jul 18 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.7-1
- New release (1:12.2.7-1)

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.2.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Jul 11 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.6-1
- New release (1:12.2.6-1)

* Mon Jul 2 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-3
- New release (1:12.2.5-3) w/ python-3.7

* Fri Jun 29 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-2
- New release (1:12.2.5-2)

* Fri Apr 27 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.5-1
- New release (1:12.2.5-1)

* Fri Apr 13 2018 Rafael dos Santos <rdossant@redhat.com> - 1:12.2.4-2
- Use standard Fedora linker flags (bug #1547552)

* Fri Mar 2 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.4-1
- New release (1:12.2.4-1)
- rhbz#1446610, rhbz#1546611, cephbz#23039

* Wed Feb 21 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.3-1
- New release (1:12.2.3-1)

* Thu Feb 15 2018 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.2-3
- no ldconfig in F28

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.2.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Dec 5 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.2-1
- New release (1:12.2.2-1)
- Fix build error on arm

* Thu Oct 05 2017 Boris Ranto <branto@redhat.com> - 1:12.2.1-2
- Obsolete ceph-libs-compat package

* Wed Sep 27 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.1-1
- New release (1:12.2.1-1)

* Tue Aug 29 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.2.0-1
- New release (1:12.2.0-1)

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-5
- libibverbs(-devel) is superceded by rdma-core(-devel), again

* Thu Aug 24 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-4
- libibverbs(-devel) is superceded by rdma-core(-devel)

* Tue Aug 22 2017 Adam Williamson <awilliam@redhat.com> - 1:12.1.4-3
- Disable RDMA support on 32-bit ARM (#1484155)

* Thu Aug 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-2
- fix %%epoch in comment, ppc64le lowmem_builder

* Wed Aug 16 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.4-1
- New release (1:12.1.4-1)

* Sat Aug 12 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.3-1
- New release (1:12.1.3-1)

* Fri Aug 11 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-3
- rebuild with librpm.so.7

* Thu Aug 10 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-2
- Fix 32-bit alignment

* Thu Aug 3 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.2-1
- New release (1:12.1.2-1)

* Tue Aug 1 2017 Boris Ranto <branto@redhat.com> - 1:12.1.1-8
- Fix ppc64 build

* Tue Aug 1 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-7
- python34 and other nits
- still no fix for ppc64

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 1:12.1.1-6
- Reenable ppc64le, with binutils fix for ppc64le (#1475636)

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-5
- ppc64le disabled until bz #1475636 resolution

* Fri Jul 28 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-4
- 12.1.1 w/ hacks for armv7hl: low mem, no java jni
- WTIH_BABELTRACE -> WITH_BABELTRACE for all archs
- still no fix for ppc64

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1:12.1.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-2
- 12.1.1 w/ rocksdb patch (i686)

* Sat Jul 22 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-1
- New release (1:12.1.1-1)

* Fri Jul 21 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:12.1.1-0
- New release (1:12.1.1-0)

* Fri Jul 21 2017 Kalev Lember <klember@redhat.com> - 1:10.2.7-3
- Rebuilt for Boost 1.64

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Mon Apr 17 2017 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 1:10.2.7-1
- New release (1:10.2.7-1)

* Wed Feb 08 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-2
- New release (1:10.2.5-2)

* Fri Jan 13 2017 Boris Ranto <branto@redhat.com> - 1:10.2.5-1
- New release (1:10.2.5-1)
- hack: do not test for libxfs, assume it is present

* Wed Dec 14 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-2
- New version (1:10.2.4-2)
- This syncs up with the upstream 10.2.5
- Doing it this way because of broken lookaside cache
- Fix the -devel obsoletes

* Thu Dec 08 2016 Boris Ranto <branto@redhat.com> - 1:10.2.4-1
- New version (1:10.2.4-1)
- Disable erasure_codelib neon build
- Use newer -devel package format
- Sync up the spec file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:10.2.3-4
- librgw: add API version defines for librgw and rgw_file

* Wed Oct 26 2016 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:10.2.3-3
- update patches style for rdopkg

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-2
- New release (1:10.2.3-2)
- common: instantiate strict_si_cast<long> not

* Thu Sep 29 2016 Boris Ranto <branto@redhat.com> - 1:10.2.3-1
- New version (1:10.2.3-1)
- Disable erasure_codelib neon build

* Sun Aug 07 2016 Igor Gnatenko <ignatenko@redhat.com> - 1:10.2.2-4
- Rebuild for LevelDB 1.18

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:10.2.2-3
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Jun 21 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-2
- New release (1:10.2.2-2)
- fix tcmalloc handling in spec file

* Mon Jun 20 2016 Boris Ranto <branto@redhat.com> - 1:10.2.2-1
- New version (1:10.2.2-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Mon May 16 2016 Boris Ranto <branto@redhat.com> - 1:10.2.1-1
- New version (1:10.2.1-1)
- Disable erasure_codelib neon build
- Do not use -momit-leaf-frame-pointer flag

* Fri May 06 2016 Dan Horák <dan[at]danny.cz> - 10.2.0-3
- fix build on s390(x) - gperftools/tcmalloc not available there

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - 10.2.0-2
- Do not use -momit-leaf-frame-pointer flag

* Fri Apr 22 2016 Boris Ranto <branto@redhat.com> - -
- Rebase to version 10.2.0
- Disable erasure_codelib neon build

* Mon Apr 11 2016 Richard W.M. Jones <rjones@redhat.com> - 1:9.2.0-5
- Fix large startup times of processes linking to -lrbd.
  Backport upstream commit 1c2831a2, fixes RHBZ#1319483.
- Add workaround for XFS header brokenness.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1:9.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jan 14 2016 Jonathan Wakely <jwakely@redhat.com> - 1:9.2.0-3
- Rebuilt for Boost 1.60

* Mon Dec 14 2015 Dan Horák <dan[at]danny.cz> - 1:9.2.0-2
- fix build on s390(x) - gperftools/tcmalloc not available there

* Tue Nov 10 2015 Boris Ranto <branto@redhat.com> - 1:9.2.0-1
- Rebase to latest stable upstream version (9.2.0 - infernalis)
- Use upstream spec file

* Tue Oct 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.5-1
- Rebase to latest upstream version

* Tue Oct 20 2015 Boris Ranto <branto@redhat.com> - 1:0.94.4-1
- Rebase to latest upstream version
- The rtdsc patch got merged upstream and is already present in the release

* Thu Aug 27 2015 Jonathan Wakely <jwakely@redhat.com> - 1:0.94.3-2
- Rebuilt for Boost 1.59

* Thu Aug 27 2015 Boris Ranto <branto@redhat.com> - 1:0.94.3-1
- Rebase to latest upstream version
- The boost patch got merged upstream and is already present in the release

* Fri Jul 31 2015 Richard W.M. Jones <rjones@redhat.com> - 1:0.94.2-4
- Fix build against boost 1.58 (http://tracker.ceph.com/issues/11576).

* Wed Jul 29 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.2-3
- Rebuilt for https://fedoraproject.org/wiki/Changes/F23Boost159

* Wed Jul 22 2015 David Tardon <dtardon@redhat.com> - 1:0.94.2-2
- rebuild for Boost 1.58

* Thu Jul 16 2015 Boris Ranto <branto@redhat.com> - 1:0.94.2-1
- Rebase to latest upstream version

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.94.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 Dan Horák <dan[at]danny.cz> - 1:0.94.1-4
- fix build on s390(x) - no gperftools there

* Thu May 21 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-3
- Disable lttng support (rhbz#1223319)

* Mon May 18 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-2
- Fix arm linking issue (rhbz#1222286)

* Tue Apr 14 2015 Boris Ranto <branto@redhat.com> - 1:0.94.1-1
- Rebase to latest upstream version and sync-up the spec file
- Add arm compilation patches

* Wed Apr 01 2015 Ken Dreyer <ktdreyer@ktdreyer.com> - 1:0.87.1-3
- add version numbers to Obsoletes (RHBZ #1193182)

* Wed Mar 4 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-2
- Perform a hardened build
- Use git-formatted patches
- Add patch for pthreads rwlock unlock problem
- Do not remove conf files on uninstall
- Remove the cleanup function, it is only necessary for f20 and f21

* Wed Feb 25 2015 Boris Ranto <branto@redhat.com> - 1:0.87.1-1
- Rebase to latest upstream
- Remove boost patch, it is in upstream tarball
- Build with yasm, tarball contains fix for the SELinux issue

* Thu Jan 29 2015 Petr Machata <pmachata@redhat.com> - 1:0.87-2
- Rebuild for boost 1.57.0
- Include <boost/optional/optional_io.hpp> instead of
  <boost/optional.hpp>.  Keep the old dumping behavior in
  osd/ECBackend.cc (ceph-0.87-boost157.patch)

* Mon Nov 3 2014 Boris Ranto <branto@redhat.com> - 1:0.87-1
- Rebase to latest major version (firefly -> giant)

* Thu Oct 16 2014 Boris Ranto <branto@redhat.com - 1:0.80.7-1
- Rebase to latest upstream version

* Sat Oct 11 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-3
- Fix a typo in librados-devel vs librados2-devel dependency

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-2
- Provide empty file list for python-ceph-compat and ceph-devel-compat

* Fri Oct 10 2014 Boris Ranto <branto@redhat.com> - 1:0.80.6-1
- Rebase to 0.80.6
- Split ceph-devel and python-ceph packages

* Tue Sep 9 2014 Dan Horák <dan[at]danny.cz> - 1:0.80.5-10
- update Requires for s390(x)

* Wed Sep 3 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-9
- Symlink librd.so.1 to /usr/lib64/qemu only on rhel6+ x86_64 (1136811)

* Thu Aug 21 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-8
- Revert the previous change
- Fix bz 1118504, second attempt (yasm appears to be the package that caused this
- Fix bogus dates

* Wed Aug 20 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-7
- Several more merges from file to try to fix the selinux issue (1118504)

* Sun Aug 17 2014 Kalev Lember <kalevlember@gmail.com> - 1:0.80.5-6
- Obsolete ceph-libcephfs

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-5
- Do not require xfsprogs/xfsprogs-devel for el6
- Require gperftools-devel for non-ppc*/s390* architectures only
- Do not require junit -- no need to build libcephfs-test.jar
- Build without libxfs for el6
- Build without tcmalloc for ppc*/s390* architectures
- Location of mkcephfs must depend on a rhel release
- Use epoch in the Requires fields [1130700]

* Sat Aug 16 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-4
- Use the proper version name in Obsoletes

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:0.80.5-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-2
- Add the arm pthread hack

* Fri Aug 15 2014 Boris Ranto <branto@redhat.com> - 1:0.80.5-1
- Bump the Epoch, we need to keep the latest stable, not development, ceph version in fedora
- Use the upstream spec file with the ceph-libs split
- Add libs-compat subpackage [1116546]
- use fedora in rhel 7 checks
- obsolete libcephfs [1116614]
- depend on redhat-lsb-core for the initscript [1108696]

* Wed Aug 13 2014 Kalev Lember <kalevlember@gmail.com> - 0.81.0-6
- Add obsoletes to keep the upgrade path working (#1118510)

* Mon Jul 7 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-5
- revert to old spec until after f21 branch

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- temporary exclude f21/armv7hl. N.B. it builds fine on f20/armv7hl.

* Fri Jul 4 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-4
- upstream ceph.spec file

* Tue Jul 1 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-3
- upstream ceph.spec file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.81.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 likewise for tcmalloc, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com>
- el6 ppc64 does not have gperftools, merge from origin/el6

* Thu Jun 5 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.81.0-1
- ceph-0.81.0

* Wed Jun  4 2014 Peter Robinson <pbrobinson@fedoraproject.org> 0.80.1-5
- gperftools now available on aarch64/ppc64

* Fri May 23 2014 Petr Machata <pmachata@redhat.com> - 0.80.1-4
- Rebuild for boost 1.55.0

* Fri May 23 2014 David Tardon <dtardon@redhat.com> - 0.80.1-3
- rebuild for boost 1.55.0

* Wed May 14 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-2
- build epel-6
- exclude %%{_libdir}/ceph/erasure-code in base package

* Tue May 13 2014 Kaleb S. KEITHLEY <kkeithle[at]redhat.com> - 0.80.1-1
- Update to latest stable upstream release, BZ 1095201
- PIE, _hardened_build, BZ 955174

* Thu Feb 06 2014 Ken Dreyer <ken.dreyer@inktank.com> - 0.72.2-2
- Move plugins from -devel into -libs package (#891993). Thanks Michael
  Schwendt.

* Mon Jan 06 2014 Ken Dreyer <ken.dreyer@inktank.com> 0.72.2-1
- Update to latest stable upstream release
- Use HTTPS for URLs
- Submit Automake 1.12 patch upstream
- Move unversioned shared libs from ceph-libs into ceph-devel

* Wed Dec 18 2013 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> 0.67.3-4
- build without tcmalloc on aarch64 (no gperftools)

* Sat Nov 30 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.67.3-3
- gperftools not currently available on aarch64

* Mon Oct 07 2013 Dan Horák <dan[at]danny.cz> - 0.67.3-2
- fix build on non-x86_64 64-bit arches

* Wed Sep 11 2013 Josef Bacik <josef@toxicpanda.com> - 0.67.3-1
- update to 0.67.3

* Wed Sep 11 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.61.7-3
- let base package include all its documentation files via %%doc magic,
  so for Fedora 20 Unversioned Docdirs no files are included accidentally
- include the sample config files again (instead of just an empty docdir
  that has been added for #846735)
- don't include librbd.so.1 also in -devel package (#1003202)
- move one misplaced rados plugin from -devel into -libs package (#891993)
- include missing directories in -devel and -libs packages
- move librados-config into the -devel pkg where its manual page is, too
- add %%_isa to subpackage dependencies
- don't use %%defattr anymore
- add V=1 to make invocation for verbose build output

* Wed Jul 31 2013 Peter Robinson <pbrobinson@fedoraproject.org> 0.61.7-2
- re-enable tmalloc on arm now gperftools is fixed

* Mon Jul 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.61.7-1
- Update to 0.61.7

* Sat Jul 27 2013 pmachata@redhat.com - 0.56.4-2
- Rebuild for boost 1.54.0

* Fri Mar 29 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.4-1
- Update to 0.56.4
- Add upstream d02340d90c9d30d44c962bea7171db3fe3bfba8e to fix logrotate

* Wed Feb 20 2013 Josef Bacik <josef@toxicpanda.com> - 0.56.3-1
- Update to 0.56.3

* Mon Feb 11 2013 Richard W.M. Jones <rjones@redhat.com> - 0.53-2
- Rebuilt to try to fix boost dependency problem in Rawhide.

* Thu Nov  1 2012 Josef Bacik <josef@toxicpanda.com> - 0.53-1
- Update to 0.53

* Mon Sep 24 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-3
- Fix automake 1.12 error
- Rebuild after buildroot was messed up

* Tue Sep 18 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.51-2
- Use system leveldb

* Fri Sep 07 2012 David Nalley <david@gnsa.us> - 0.51-1
- Updating to 0.51
- Updated url and source url.

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.46-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed May  9 2012 Josef Bacik <josef@toxicpanda.com> - 0.46-1
- updated to upstream 0.46
- broke out libcephfs (rhbz# 812975)

* Mon Apr 23 2012 Dan Horák <dan[at]danny.cz> - 0.45-2
- fix detection of C++11 atomic header

* Thu Apr 12 2012 Josef Bacik <josef@toxicpanda.com> - 0.45-1
- updating to upstream 0.45

* Wed Apr  4 2012 Niels de Vos <devos@fedoraproject.org> - 0.44-5
- Add LDFLAGS=-lpthread on any ARM architecture
- Add CFLAGS=-DAO_USE_PTHREAD_DEFS on ARMv5tel

* Mon Mar 26 2012 Dan Horák <dan[at]danny.cz> 0.44-4
- gperftools not available also on ppc

* Mon Mar 26 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-3
- Remove unneeded patch

* Sun Mar 25 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.44-2
- Update to 0.44
- Fix build problems

* Mon Mar  5 2012 Jonathan Dieter <jdieter@lesbg.com> - 0.43-1
- Update to 0.43
- Remove upstreamed compile fixes patch
- Remove obsoleted dump_pop patch

* Tue Feb 28 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.41-2
- Rebuilt for c++ ABI breakage

* Thu Feb 16 2012 Tom Callaway <spot@fedoraproject.org> 0.41-1
- update to 0.41
- fix issues preventing build
- rebuild against gperftools

* Sat Dec 03 2011 David Nalley <david@gnsa.us> 0.38-1
- updating to upstream 0.39

* Sat Nov 05 2011 David Nalley <david@gnsa.us> 0.37-1
- create /etc/ceph - bug 745462
- upgrading to 0.37, fixing 745460, 691033
- fixing various logrotate bugs 748930, 747101

* Fri Aug 19 2011 Dan Horák <dan[at]danny.cz> 0.31-4
- google-perftools not available also on s390(x)

* Mon Jul 25 2011 Karsten Hopp <karsten@redhat.com> 0.31-3
- build without tcmalloc on ppc64, BR google-perftools is not available there

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-2
- Remove curl/types.h include since we don't use it anymore

* Tue Jul 12 2011 Josef Bacik <josef@toxicpanda.com> 0.31-1
- Update to 0.31

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26-2
- Add the compile fix patch

* Tue Apr  5 2011 Josef Bacik <josef@toxicpanda.com> 0.26
- Update to 0.26

* Tue Mar 22 2011 Josef Bacik <josef@toxicpanda.com> 0.25.1-1
- Update to 0.25.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Sep 29 2010 Steven Pritchard <steve@kspei.com> 0.21.3-1
- Update to 0.21.3.

* Mon Aug 30 2010 Steven Pritchard <steve@kspei.com> 0.21.2-1
- Update to 0.21.2.

* Thu Aug 26 2010 Steven Pritchard <steve@kspei.com> 0.21.1-1
- Update to 0.21.1.
- Sample configs moved to /usr/share/doc/ceph/.
- Added cclass, rbd, and cclsinfo.
- Dropped mkmonfs and rbdtool.
- mkcephfs moved to /sbin.
- Add libcls_rbd.so.

* Tue Jul  6 2010 Josef Bacik <josef@toxicpanda.com> 0.20.2-1
- update to 0.20.2

* Wed May  5 2010 Josef Bacik <josef@toxicpanda.com> 0.20-1
- update to 0.20
- disable hadoop building
- remove all the test binaries properly

* Fri Apr 30 2010 Sage Weil <sage@newdream.net> 0.19.1-5
- Remove java deps (no need to build hadoop by default)
- Include all required librados helpers
- Include fetch_config sample
- Include rbdtool
- Remove misc debugging, test binaries

* Fri Apr 30 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-4
- Add java-devel and java tricks to get hadoop to build

* Mon Apr 26 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-3
- Move the rados and cauthtool man pages into the base package

* Sun Apr 25 2010 Jonathan Dieter <jdieter@lesbg.com> 0.19.1-2
- Add missing libhadoopcephfs.so* to file list
- Add COPYING to all subpackages
- Fix ownership of /usr/lib[64]/ceph
- Enhance description of fuse client

* Tue Apr 20 2010 Josef Bacik <josef@toxicpanda.com> 0.19.1-1
- Update to 0.19.1

* Mon Feb  8 2010 Josef Bacik <josef@toxicpanda.com> 0.18-1
- Initial spec file creation, based on the template provided in the ceph src
