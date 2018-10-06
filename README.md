samba4repo
==========

Wrapper for SRPM building tools for Samba 4 on CentOS 7 and Fedora 28.

The samba hers is built with the domain controller fully enabled, in
the "samba-dc" packagtes. The RPMs from RHEL upstream include only
stubs, they do not actually include the domain controller components,
partly because those are incompatible with the default Kerberos built
into Fedora and RHEL.

Git Checkout
===========

This repository relies on extensive git submodules. When cloneing it locally, use:

* git clone --recurse-submodules https://github.com/nkadel/samba4repo

*** NOTE: The git repos at github.com do not include the tarballs ***

This is for basic security reasons: you'll need to get the tarballs
manually, usually from the "Source:" locations designated in the .spec
file. These are typically available at:

* https://ftp.samba.org/pub/samba/

Building Samba
==============

These are rebuilt from Fedora rawhide releases, and need to be built
and installed in the following order.

* make cfgs # Create local .cfg configs for "mock".
* * epel-7-x86_64.cfg # Used for some Makefiles
* * fedora-28-x86_64.cfg # Used for some Makefiles
* * samba4repo-7-x86_64.cfg # Activates local RPM dependency repository
* * samba4repo-428-x86_64.cfg # Activates local RPM dependency repository

* make repos # Creates local local yum repositories in $PWD/samba4repo
* * samba4repo/el/7
* * samba4repo/fedora/28

* make # Make all distinct versions using "mock"

Building a compoenent, without "mock" and in the local working system,
can also be done for testing.

* make build

Samba 4.9 as strong dependencies on additional components that are not
recent enough in RHEL 7, and may not be up-to-date enough even in
Fedora. They typically need to be built and deployed for local compilation or for
"mock" compilation. These dependencies are detailed in the Makefile,
but include:

* libtalloc
* libtdb
* libldb
* libtevent

Installing Samba
==============--

The relevant yum repository is built locally in samba4reepo. To enable the repository, use this:

* make repo

Then install the .repo file in /etc/yum.repos.d/ as directed. This
requires root privileges, which is why it's not automated.

Samba RPM Build Security
====================

There is a significant security risk with enabling yum repositories
for locally built components. Generating GPF signed packages and
ensuring that the compneents are in this build location are securely
and safely built is not addressed in this test setup.

		Nico Kadel-Garcia <nkadel@gmail.com>
