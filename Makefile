#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

REPOBASE=file://$(PWD)

# Buildable without samba4repo, many needed only for amaozn Linux 2023
SAMBAPKGS+=firebird-srpm
SAMBAPKGS+=freetds-sprm
SAMBAPKGS+=fmt-srpm
SAMBAPKGS+=gflags-srpm
SAMBAPKGS+=libmng-srpm
SAMBAPKGS+=mimalloc-srpm
SAMBAPKGS+=qt5-srpm

# Requires locally build components
SAMBAPKGS+=mold-srpm
SAMBAPKGS+=glusterfs-srpm
SAMBAPKGS+=qt5-qtbase-srpm
# Requires qt5 and libmng and qt5-qtbase
SAMBAPKGS+=thrift-srpm

# Requires gflags-sprm
SAMBAPKGS+=glog-srpm
# Requires gflags
SAMBAPKGS+=libarrow-srpm
# Requires mold
SAMBAPKGS+=ceph-srpm

SAMBAPKGS+=python-iso86001-0.1.x-srpm
SAMBAPKGS+=python-pyasn1-0.4.x-srpm
#SAMBAPKGS+=python-coverage-srpm
# Requires coverage
SAMBAPKGS+=python-nose-srpm
# Needs nose
#SAMBAPKGS+=python-setproctitle-1.2.x-srpm

# Requires nose
SAMBAPKGS+=python-etcd-srpm

#SAMBAPKGS+=libtalloc-2.4.x-srpm
#SAMBAPKGS+=libtdb-1.4.x-srpm
## Requires libtalloc
#SAMBAPKGS+=libtevent-0.14.x-srpm
## Requires libtalloc,libtdb,libtevent
#SAMBAPKGS+=libldb-2.7.x-srpm

## Current samba release
# Now builds internal libraries rather than:
# libtalloc, libtdb, libtevent, libldb
# Internal libraries avoids conflict with sssd dependencies
SAMBAPKGS+=samba-srpm

REPOS+=samba4repo/el/8
REPOS+=samba4repo/el/9
REPOS+=samba4repo/fedora/39
REPOS+=samba4repo/amazon/2023

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-8-x86_64.cfg
CFGS+=samba4repo-9-x86_64.cfg
CFGS+=samba4repo-f39-x86_64.cfg
# Amazon 2 config
CFGS+=samba4repo-amz2023-x86_64.cfg

# /et/cmock version lacks EPEL

# Link from /etc/mock
MOCKCFGS+=centos-stream+epel-8-x86_64.cfg
MOCKCFGS+=centos-stream+epel-9-x86_64.cfg
MOCKCFGS+=fedora-39-x86_64.cfg
MOCKCFGS+=amazonlinux-2023-x86_64.cfg

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

$(MOCKCFGS)::
	@echo Generating $@ from /etc/mock/$@
	@echo "include('/etc/mock/$@')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@

samba4repo-8-x86_64.cfg: /etc/mock/centos-stream+epel-8-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@
	@echo | tee -a $@
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" | tee -a $@
	@echo "config_opts['dnf.conf'] += \"\"\"" | tee -a $@
	@echo '[samba4repo]' | tee -a $@
	@echo 'name=samba4repo' | tee -a $@
	@echo 'enabled=1' | tee -a $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/el/8/x86_64/' | tee -a $@
	@echo 'skip_if_unavailable=False' | tee -a $@
	@echo 'metadata_expire=0' | tee -a $@
	@echo 'gpgcheck=0' | tee -a $@
	@echo 'priority=20' | tee -a $@
	@echo '"""' | tee -a $@

samba4repo-9-x86_64.cfg: /etc/mock/centos-stream+epel-9-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" | tee -a $@
	@echo "config_opts['dnf.conf'] += \"\"\"" | tee -a $@
	@echo '[samba4repo]' | tee -a $@
	@echo 'name=samba4repo' | tee -a $@
	@echo 'enabled=1' | tee -a $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/el/9/x86_64/' | tee -a $@
	@echo 'skip_if_unavailable=False' | tee -a $@
	@echo 'metadata_expire=0' | tee -a $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-f39-x86_64.cfg: /etc/mock/fedora-39-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@
	@echo >> $@
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/fedora/39/x86_64/' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-rawhide-x86_64.cfg: /etc/mock/fedora-rawhide-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@
	@sed -i "s/^config_opts\['root'\] =/#config_opts\['root'\] =/g" $@
	@echo >> $@
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" >> $@
	@echo "config_opts['yum.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/fedora/rawhide/x86_64/' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-amz2023-x86_64.cfg: /etc/mock/amazonlinux-2023-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo "config_opts['dnf_vars'] = { 'best': 'False' }" | tee -a $@
	@echo >> $@
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/amazon/2023/x86_64/' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

repo: samba4repo.repo
samba4repo.repo:: Makefile samba4repo.repo.in
	if [ -s /etc/fedora-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/fedora/|g" | tee $@; \
	elif [ -s /etc/redhat-release ]; then \
		cat $@.in | \
			sed "s|@REPOBASEDIR@/|$(PWD)/|g" | \
			sed "s|/@RELEASEDIR@/|/el/|g" | tee $@; \
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
