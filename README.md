samba4repo
==========

Wrapper for SRPM building tools for Samba 4 on Fedora 37, CentOS 8 and 9

The samba here is built with the domain controller fully enabled, in
the "samba-dc" packagtes. The RPMs from RHEL upstream included only
stubs, they did not actually include the domain controller components,
partly because those are incompatible with the default Kerberos built
into Fedora and RHEL. The experiemental Samba support for that default
Kerberos is tentative and not yet suitable for production.

Git Checkout
===========

This repository relies on extensive git submodules. When cloning it locally, use:

* git clone --recurse-submodules https://github.com/nkadel/samba4repo

*** NOTE: The git repos at github.com do not include the tarballs ***

This is for basic security reasons: you'll need to get the tarballs
separaately.  These can normally be pulled from the Source:
references, and pulled with this command.

* make getsrc
    
If necessary for manual download, look at:

* https://www.samba.org/ftp/samba/

Building Samba
==============

These are rebuilt from Fedora rawhide releases, and need to be built
and installed in the following order.

* make cfgs # Create local .cfg configs for "mock".
* * centos-stream+epel-8-x86_64.cfg # Used for some Makefiles
* * centos-stream+epel-9-x86_64.cfg # Used for some Makefiles
* * fedora-37-x86_64.cfg # Used for some Makefiles
* * samba4repo-8-x86_64.cfg # Activates local RPM dependency repository
* * samba4repo-9-x86_64.cfg # Activates local RPM dependency repository
* * samba4repo-f34-x86_64.cfg # Activates local RPM dependency repository

* make repos # Creates local local yum repositories in $PWD/samba4repo
* * samba4repo/el/8
* * samba4repo/el/9
* * samba4repo/fedora/37

* make # Make all distinct versions using "mock"

Building a compoenent, without "mock" and in the local working system,
can also be done for testing.

* make build

Samba 4.10 nad later has strong dependencies on additional components
that may or not be built into the current Fedora releases. These are
in the following submodules:

* liburing-xxx-srpm
* lmdb-xxxx-srpm
* python-iso86001-xxx-srpm
* python-pyasn1-xxx-srpm
* python-setproctitle-xxx-srpm

Th following libraries are all now compiled internally with the Samba
tarball. Building them separately conflicts with the versions used by sssd.

* libtalloc-xxx-srpm
* libtdb-xxx-srpm
* libldb-xxx-srpm
* libtevent-xxx-srpm

Then build the final package.

* samba-xxx-srpm

Installing Samba
==============--

The relevant yum repository is built locally in samba4reepo. To enable the repository, use this:

* make repo

Then install the .repo file in /etc/yum.repos.d/ as directed. This
requires root privileges, which is why it's not automated.

Samba RPM Build Security
====================

There is a significant security risk with enabling yum repositories
for locally built components. Generating GPG signed packages and
ensuring that the compneents are in this build location are securely
and safely built is not addressed in this test setup.

CentOS Overlap
========================

CentOS 8 has published libraries such as libtalloc and libldb of
sufficiently recent release for Samba 4.16. Unfortunately, they
elected to discard "python3-talloc-devel" and similar components,
simply to diverge from Fedora and "mark their territory". So
unfortunately, those have to be built and updated from here.

Amazon Linux Compilation
========================

Mock on CentOS and RHEL cannot compile Amazon Linux RPMS with
mock. The necessary yum repositories are accessible on Amazon Linux
hosts, not publicly available the way CentOS and RHEL repos are.  A
tentative command to build on an amazon Linux 2 host is:

* grep -l '^MOCK.*-7-x86_64' *srpm/Makefile | while read name; do  pushd `dirname $name`; make MOCKS=amazonlinux-2-x86_64; popd; done


Nico Kadel-Garcia <nkadel@gmail.com>
