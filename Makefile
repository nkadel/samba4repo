#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

# RHEL 8 beta needs doxygen
#SAMBAPKGS+=doxygen-1.8.x-srpm
# RHEL 8 beta needs cmocka
#SAMBAPKGS+=cmocka-1.1.x-srpm

# RHEL 7 needs compat-nettle32-3.x, which uses epel-7-x86_64
SAMBAPKGS+=compat-nettle32-3.x-srpm

# Current libtalloc-1.x required
SAMBAPKGS+=libtalloc-2.1.x-srpm

# Current libtdb-1.3.x required
SAMBAPKGS+=libtdb-1.3.x-srpm

# RHEL 7 needs compat-gnutls3.4.x-sprm, which uses compat-nettle32
SAMBAPKGS+=compat-gnutls34-3.x-srpm

# Current libtevent-0.9.x required for Samba 4.10
SAMBAPKGS+=libtevent-0.9.x-srpm

# Also requires libtevent, 1.5.4 required for Samba 4.10
SAMBAPKGS+=libldb-1.5.x-srpm

# Current samba release, requires all curent libraries
SAMBAPKGS+=samba-4.10.x-srpm

REPOS+=samba4repo/el/7
REPOS+=samba4repo/el/8
REPOS+=samba4repo/fedora/29
REPOS+=samba4repo/fedora/30
REPOS+=samba4repo/fedora/rawhide

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-rawhide-x86_64.cfg
CFGS+=samba4repo-f29-x86_64.cfg
CFGS+=samba4repo-7-x86_64.cfg
CFGS+=samba4repo-8-x86_64.cfg

# Link from /etc/mock
MOCKCFGS+=epel-7-x86_64.cfg
MOCKCFGS+=rhelbeta-8-x86_64.cfg
MOCKCFGS+=fedora-29-x86_64.cfg
MOCKCFGS+=fedora-rawhide-x86_64.cfg

all:: $(CFGS)
all:: $(MOCKCFGS)
all:: $(REPODIRS)
all:: $(SAMBAPKGS)

all install clean:: FORCE
	@for name in $(SAMBAPKGS); do \
	     (cd $$name; $(MAKE) $(MFLAGS) $@); \
	done  

# Build for locacl OS
build:: FORCE
	@for name in $(SAMBAPKGS); do \
	     (cd $$name; $(MAKE) $(MFLAGS) $@); \
	done

# Git submodule checkout operation
# For more recent versions of git, use "git checkout --recurse-submodules"
*-srpm::
	@[ -d $@/.git ] || \
		git submodule update --init $@

# Dependencies of libraries on other libraries for compilation

# doxygen needed for RHEL 8 beta
#cmocka-1.1.x-srpm:: doxygen-1.8.x-srpm
#libtalloc-2.1.x-srpm:: doxygen-1.8.x-srpm
#libtevent-0.10.x-srpm:: doxygen-1.8.x-srpm
#libtdb-1.3.x-srpm:: doxygen-1.8.x-srpm
#libldb-1.5.x-srpm:: doxygen-1.8.x-srpm

compat-gnutls34-3.x-srpm:: compat-nettle32-3.x-srpm

libtevent-0.9.x-srpm:: libtalloc-2.1.x-srpm

libldb-1.5.x-srpm:: libtalloc-2.1.x-srpm
libldb-1.5.x-srpm:: libtdb-1.3.x-srpm
libldb-1.5.x-srpm:: libtevent-0.9.x-srpm

# Samba rellies on all the othe components
samba-4.10.x-srpm:: libtalloc-2.1.x-srpm
samba-4.10.x-srpm:: libldb-1.5.x-srpm
samba-4.10.x-srpm:: libtevent-0.9.x-srpm
samba-4.10.x-srpm:: libtdb-1.3.x-srpm

# Actually build in directories
$(SAMBAPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS) install)

repos: $(REPOS) $(REPODIRS)
$(REPOS):
	install -d -m 755 $@

.PHONY: $(REPODIRS)
$(REPODIRS): $(REPOS)
	@install -d -m 755 `dirname $@`
	/usr/bin/createrepo -q `dirname $@`


.PHONY: cfg
cfg:: cfgs

.PHONY: cfgs
cfgs: $(CFGS) $(MOCKCFGS)

samba4repo-7-x86_64.cfg: epel-7-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/epel-7-x86_64/samba4repo-7-x86_64/g' $@
	@echo '"""' >> $@
	@echo >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=file://$(PWD)/samba4repo/el/7/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo '#cost=2000' >> $@
	@echo '"""' >> $@
	@uniq -u $@ > $@.out
	@mv $@.out $@

samba4repo-8-x86_64.cfg: rhelbeta-8-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/rhelbeta-8-x86_64/samba4repo-8-x86_64/g' $@
	@echo '"""' >> $@
	@echo >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=file://$(PWD)/samba4repo/el/8/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo '#cost=2000' >> $@
	@echo '"""' >> $@
	@uniq -u $@ > $@.out
	@mv $@.out $@

samba4repo-f29-x86_64.cfg: fedora-29-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/fedora-29-x86_64/samba4repo-f29-x86_64/g' $@
	@echo '"""' >> $@
	@echo >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=file://$(PWD)/samba4repo/fedora/29/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo '#cost=2000' >> $@
	@echo '"""' >> $@
	@uniq -u $@ > $@.out
	@mv $@.out $@

samba4repo-rawhide-x86_64.cfg: fedora-rawhide-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/fedora-rawhide-x86_64/samba4repo-rawhide-x86_64/g' $@
	@echo '"""' >> $@
	@echo >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=file://$(PWD)/samba4repo/fedora/rawhide/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo '#cost=2000' >> $@
	@echo '"""' >> $@
	@uniq -u $@ > $@.out
	@mv $@.out $@

$(MOCKCFGS)::
	ln -sf /etc/mock/$@ $@

repo: samba4repo.repo
samba4repo.repo:: Makefile samba4repo.repo.in
	if [ -s /etc/fedora-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/fedora/|g" > $@; \
	elif [ -s /etc/redhat-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/el/|g" > $@; \
	else \
		echo Error: unknown release, check /etc/*-release; \
		exit 1; \
	fi

samba4repo.repo::
	@cmp -s $@ /etc/yum.repos.d/$@ || \
	    diff -u $@ /etc/yum.repos.d/$@

clean::
	find . -name \*~ -exec rm -f {} \;
	rm -f *.cfg
	rm -f *.out
	@for name in $(SAMBAPKGS); do \
	    $(MAKE) -C $$name clean; \
	done

distclean:
	rm -rf $(REPOS)

maintainer-clean:
	rm -rf $(SAMBAPKGS)

FORCE::

