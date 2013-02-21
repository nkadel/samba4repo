samba4repo
==========

Wrapper for SRPM building tools for Samba 4 on RHEL 6.

These are rebuilt from Fedora rawhide releases, and need to be built
and installed in the following order.

	samba4repo-6-x86_64.cfg - install in /etc/mock/
	samba4repo.repo - install in /etc/yum.repos.d/.

Then install and enable a yum repository on the local server, or a
designated host, with this kind of layout:

	mkdir /var/www/linux	  
	mkdir /var/www/linux/samba4repo
	mkdir /var/www/linux/samba4repo/6
	mkdir /var/www/linux/samba4repo/6/x86_64
	createrepo /var/www/linux/samba4repo/6/x86_64
	mkdir /var/www/linux/samba4repo/6/SRPMS
	createrepo /var/www/linux/samba4repo/6/SRPMS

Set up symlinks for "$releasever" names in yum setups.

	ln -s -f -n 6 /var/www/linux/samba4repo/6.3
	ln -s -f -n 6 /var/www/linux/samba4repo/6Server

The "make" command will build all components. If they don't exist yet,
they will be git cloned from https://github.com/nkadel/. The
components there are somewhat interwoven with this "samba4repo"
structure, so review it before building or deploying with it.

*** NOTE: The git repos at github.com do not include the tarballs ***

This is for basic security reasons: I do *not* want to become
responsible for publishing the source code software for other people's
compnents, and possibly getting hacked and corrupting your
software. You'll need to get the tarballs manually, usually from the
"Source:" locations designated in the .spec file.

"make install" will attempt to deploy them in a designated directory
for "yum" repository access, run "createrepo", to get the packages
listeed, and and clear away old "mock" configurations. "createrepo
--update" and "mock clean" are somewhat unreliable in their behavior,
so actually re-running and createrepo and using "rm -rf" on the mock
cache works better.

Samba 4.0.3 has strong dependencies on additional components that are
not part of RHEL 6, or are not recent enough in RHEL 6, and need to be
built and deployed for local compilation or for "mock"
compilation. These dependencies are detailed in the Makefile, but
include:

    iniparser
    krb5
    libtalloc
    libtdb
    libldb
    libtevent

		Nico Kadel-Garcia <nkadel@gmail.com>
