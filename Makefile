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

# Current libldb-1.4.x required
# Also reuqires libtevent
SAMBAPKGS+=libldb-srpm

# Current samba release, requires all curent libraries
SAMBAPKGS+=samba-srpm

REPOS+=samba4repo/el/7
REPOS+=samba4repo/fedora/29

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-f29-x86_64.cfg
CFGS+=samba4repo-7-x86_64.cfg

# Link from /etc/mock
MOCKCFGS+=epel-7-x86_64.cfg
#MOCKCFGS+=fedora-29-x86_64.cfg

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

libldb-srpm:: libtalloc-srpm
libldb-srpm:: libtdb-srpm
libldb-srpm:: libtevent-srpm

# Samba rellies on all the othe components
samba-srpm:: libtalloc-srpm
samba-srpm:: libldb-srpm
samba-srpm:: libtevent-srpm
samba-srpm:: libtdb-srpm

# Actually build in directories
$(SAMBAPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS) install)

repos: $(REPOS) $(REPODIRS)
$(REPOS):
	install -d -m 755 $@

.PHONY: $(REPODIRS)
$(REPODIRS): $(REPOS)
	@install -d -m 755 `dirname $@`
	/usr/bin/createrepo `dirname $@`


.PHONY: cfg
cfg:: cfgs

.PHONY: cfgs
cfgs: $(CFGS) $(MOCKCFGS)

$(CFGS)::
	sed 's|@REPOBASEDIR@|$(PWD)|g' $@.in > $@

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

