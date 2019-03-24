#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

# Current libtalloc-2.1.x required
SAMBAPKGS+=libtalloc-srpm

# Current libtdb-1.3.x required
SAMBAPKGS+=libtdb-srpm

# Current libtevent-0.9.x required
SAMBAPKGS+=libtevent-srpm

# Current libldb-1.4.x required for samba-4.9
# Also requires libtevent
SAMBAPKGS+=libldb-1.4.x-srpm
SAMBAPKGS+=libldb-1.5.x-srpm

# Current samba release, requires all curent libraries
SAMBAPKGS+=samba-srpm
SAMBAPKGS+=samba-4.10.x-srpm

REPOS+=samba4repo/el/6
REPOS+=samba4repo/el/7
REPOS+=samba4repo/fedora/29
REPOS+=samba4repo/fedora/rawhide

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-rawhide-x86_64.cfg
CFGS+=samba4repo-f29-x86_64.cfg
CFGS+=samba4repo-7-x86_64.cfg
CFGS+=samba4repo-6-x86_64.cfg

# Link from /etc/mock
MOCKCFGS+=epel-6-x86_64.cfg
MOCKCFGS+=epel-7-x86_64.cfg
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
libtevent:: libtalloc-srpm

libldb-1.4.x-srpm:: libtalloc-srpm
libldb-1.4.x-srpm:: libtdb-srpm
libldb-1.4.x-srpm:: libtevent-srpm

libldb-1.5.x-srpm:: libtalloc-srpm
libldb-1.5.x-srpm:: libtdb-srpm
libldb-1.5.x-srpm:: libtevent-srpm

# Samba rellies on all the othe components
samba-srpm:: libtalloc-srpm
samba-srpm:: libldb-1.4.x-srpm
samba-srpm:: libtevent-srpm
samba-srpm:: libtdb-srpm

samba-4.10.x-srpm:: libtalloc-srpm
samba-4.10.x-srpm:: libldb-1.5.x-srpm
samba-4.10.x-srpm:: libtevent-srpm
samba-4.10.x-srpm:: libtdb-srpm


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

samba4repo-6-x86_64.cfg: epel-6-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/epel-6-x86_64/samba4repo-6-x86_64/g' $@
	@echo '"""' >> $@
	@echo >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=file://$(PWD)/samba4repo/el/6/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo '#cost=2000' >> $@
	@echo '"""' >> $@
	@uniq -u $@ > $@~
	@mv $@~ $@

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
	@uniq -u $@ > $@~
	@mv $@~ $@

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
	@uniq -u $@ > $@~
	@mv $@~ $@

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
	@uniq -u $@ > $@~
	@mv $@~ $@

$(MOCKCFGS)::
	ln -sf /etc/mock/$@ $@

repo: samba4repo.repo
samba4repo.repo:: samba4repo.repo.in
	sed 's|@REPOBASEDIR@|$(PWD)|g' $@.in > $@
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

