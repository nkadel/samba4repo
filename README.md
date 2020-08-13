samba4repo
==========

Wrapper for SRPM building tools for Samba 4 on Fedora 31, CentOS 7 and 8

Samba 4.10.0 and later are not compatible with Python 2.. These tools
have been updated to use the EPEL published python36-devel, and build
matching modules.

compat-nettle32 and compat-gnutlf34 are provided for the Samba DC
to work on RHEL 7. They are based on sergiomdk2's work at:

     https://github.com/sergiomb2/SambaAD

The samba here is built with the domain controller fully enabled, in
the "samba-dc" packagtes. The RPMs from RHEL upstream included only
stubs, they did not actually include the domain controller components,
partly because those are incompatible with the default Kerberos built
into Fedora and RHEL. The experiemental Samba support for that default
Kerberos is tentative and not yet suitable for production.

quota-devel
===========

Red Hat, for reasons which defy logic, did not elect to publish the
"quota-devel" package along with "quota" in RHEL 8. CentOS has worked
around this by adding a "Devel" stream to the 5 arbitrary and
inconsistently segregated channels of their primary OS channels. This
Devel channel is disabled by default.

Enable it in /etc/mock/centos-8.tpl gefore trying to compile Samba
with mock, and enablr it /etc/yum.repos.d/ before compiling Samba
lodally.

Git Checkout
===========

This repository relies on extensive git submodules. When cloning it locally, use:

* git clone --recurse-submodules https://github.com/nkadel/samba4repo

*** NOTE: The git repos at github.com do not include the tarballs ***

This is for basic security reasons: you'll need to get the tarballs separaately.
These can normally be pulled from the Source: references, and pulled with this command.

* make getsrc
    
If necessary for manual download, look at:

* https://www.samba.org/ftp/samba/

Building Samba
==============

These are rebuilt from Fedora rawhide releases, and need to be built
and installed in the following order.

* make cfgs # Create local .cfg configs for "mock".
* * epel-7-x86_64.cfg # Used for some Makefiles
* * epel-8-x86_64.cfg # Used for some Makefiles
* * fedora-32-x86_64.cfg # Used for some Makefiles
* * samba4repo-7-x86_64.cfg # Activates local RPM dependency repository
* * samba4repo-8-x86_64.cfg # Activates local RPM dependency repository
* * samba4repo-f32-x86_64.cfg # Activates local RPM dependency repository

* make repos # Creates local local yum repositories in $PWD/samba4repo
* * samba4repo/el/7
* * samba4repo/el/8
* * samba4repo/fedora/32

* make # Make all distinct versions using "mock"

Building a compoenent, without "mock" and in the local working system,
can also be done for testing.

* make build

Samba 4.10 nad later has strong dependencies on additional components that may or not be 
built into the current Fedora releases. These are in the following submodules:

* libtalloc-xxx-srpm
* libtdb-xxx-srpm
* libldb-xxx-srpm
* libtevent-xxx-srpm
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

		Nico Kadel-Garcia <nkadel@gmail.com>
