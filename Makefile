#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

#REOBASEE=http://localhost
REPOBASE=file://$(PWD)

# RHEL 7 needs compat-nettle34-3.x, which uses epel-7-x86_64
SAMBAPKGS+=compat-nettle34-3.x-srpm

# RHEL 7 needs gmp-6.1.x-srpm, which uses epel-7-x86_64
SAMBAPKGS+=gmp-6.1.x-srpm

# CentOS 8 needs quota-devel, whcih RHEL 8 and CentOS 8 put in a different
# channel from quota and quota debuginfo for no sane reason
#SAMBAPKGS+=quota-4.x-srpm

# Current libtalloc-2.x required
SAMBAPKGS+=libtalloc-2.3.x-srpm

# Current libtdb-1.4.x required
SAMBAPKGS+=libtdb-1.4.x-srpm

# Current libtevent-0.11.x required for Samba 4.10
SAMBAPKGS+=libtevent-0.11.x-srpm

# RHEL 7 needs compat-gnutls36.3.x-sprm, which uses compat-nettle34
SAMBAPKGS+=compat-gnutls36-3.x-srpm

# Also requires libtevent
SAMBAPKGS+=libldb-2.4.x-srpm

# Current samba release, requires all curent libraries
SAMBAPKGS+=samba-4.15.x-srpm

REPOS+=samba4repo/el/7
REPOS+=samba4repo/el/8
REPOS+=samba4repo/fedora/34
REPOS+=samba4repo/amz/2

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-7-x86_64.cfg
CFGS+=samba4repo-8-x86_64.cfg
CFGS+=samba4repo-f34-x86_64.cfg
# Amazon 2 config
CFGS+=samba4repo-amz2-x86_64.cfg

# /et/cmock version lacks EPEL
CFGS+=epel-8-x86_64.cfg

# Link from /etc/mock
MOCKCFGS+=epel-7-x86_64.cfg
MOCKCFGS+=epel-8-x86_64.cfg
MOCKCFGS+=fedora-34-x86_64.cfg
#MOCKCFGS+=amazonlinux-2-x86_64.cfg

all:: install

install:: $(CFGS)
install:: $(MOCKCFGS)
install:: $(REPODIRS)
install:: $(SAMBAPKGS)

# Actually put all the modules in the local repo
.PHONY: install clean getsrc build srpm src.rpm
install clean getsrc build srpm src.rpm::
	@for name in $(SAMBAPKGS); do \
	     (cd $$name && $(MAKE) $(MFLAGS) $@); \
	done  

# Git submodule checkout operation
# For more recent versions of git, use "git checkout --recurse-submodules"
#*-srpm::
#	@[ -d $@/.git ] || \
#	     git submodule update --init $@

# Dependencies of libraries on other libraries for compilation

libtevent-0.11.x-srpm:: libtalloc-2.3.x-srpm

libldb-2.4.x-srpm:: libtalloc-2.3.x-srpm
libldb-2.4.x-srpm:: libtdb-1.4.x-srpm
libldb-2.4.x-srpm:: libtevent-0.11.x-srpm

compat-gnutls36-3.x-srpm:: compat-nettle34-3.x-srpm
compat-gnutls36-3.x-srpm:: gmp-6.1.x-srpm
compat-gnutls36-3.x-srpm:: libldb-2.4.x-srpm

# Samba rellies on all the othe components
samba-4.15.x-srpm:: compat-gnutls36-3.x-srpm
samba-4.15.x-srpm:: libtalloc-2.3.x-srpm
samba-4.15.x-srpm:: libtdb-1.4.x-srpm
samba-4.15.x-srpm:: libtevent-0.11.x-srpm
samba-4.15.x-srpm:: libldb-2.4.x-srpm

# Actually build in directories
.PHONY: $(SAMBAPKGS)
$(SAMBAPKGS)::
	(cd $@ && $(MAKE) $(MLAGS) install)

repodirs: $(REPOS) $(REPODIRS)
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

epel-8-x86_64.cfg:: /etc/mock/epel-8-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@echo >> $@
	@echo '# epel-8 configs lack EPEL, added here' >> $@
	@echo "include('templates/epel-8.tpl')" >> $@

samba4repo-7-x86_64.cfg: /etc/mock/epel-7-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/epel-7-x86_64/samba4repo-7-x86_64/g' $@
	@echo >> $@
	@echo "Disabling 'best=' for $@"
	@sed -i '/^best=/d' $@
	@echo "best=0" >> $@
	@echo "config_opts['yum.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/el/7/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-8-x86_64.cfg: epel-8-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/epel-8-x86_64/samba4repo-8-x86_64/g' $@
	@echo >> $@
	@echo "Disabling 'best=' for $@"
	@sed -i '/^best=/d' $@
	@echo "best=0" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/el/8/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-f34-x86_64.cfg: /etc/mock/fedora-34-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/fedora-34-x86_64/samba4repo-f34-x86_64/g' $@
	@echo >> $@
	@echo "Disabling 'best=' for $@"
	@sed -i '/^best=/d' $@
	@echo "best=0" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/fedora/34/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-rawhide-x86_64.cfg: /etc/mock/fedora-rawhide-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/fedora-rawhide-x86_64/samba4repo-rawhide-x86_64/g' $@
	@echo >> $@
	@echo "Disabling 'best=' for $@"
	@sed -i '/^best=/d' $@
	@echo "best=0" >> $@
	@echo "config_opts['yum.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/fedora/rawhide/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-amz2-x86_64.cfg: /etc/mock/amazonlinux-2-x86_64.cfg
	@echo Generating $@ from $?
	@cat $? > $@
	@sed -i 's/amz-2-x86_64/samba4repo-amz2-x86_64/g' $@
	@echo >> $@
	@echo "Disabling 'best=' for $@"
	@sed -i '/^best=/d' $@
	@echo "best=0" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/amz/2/x86_64/' >> $@
	@echo 'failovermethod=priority' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

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

distclean: clean
	rm -rf $(REPOS)
	rm -rf samba4repo
	@for name in $(SAMBAPKGS); do \
	    (cd $$name; git clean -x -d -f); \
	done

maintainer-clean: distclean
	rm -rf $(SAMBAPKGS)
	@for name in $(SAMBAPKGS); do \
	    (cd $$name; git clean -x -d -f); \
	done


