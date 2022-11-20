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

# Samba required
SAMBAPKGS+=liburing-2.x-srpm
# Only needed for Amazon Linux
#SAMBAPKGS+=lmdb-0.9.x-srpm
SAMBAPKGS+=python-iso86001-0.1.x-srpm
SAMBAPKGS+=python-pyasn1-0.4.x-srpm
SAMBAPKGS+=python-nose-1.3.x-srpm
SAMBAPKGS+=python-setproctitle-1.2.x-srpm

# Current samba release, requires all curent libraries
SAMBAPKGS+=samba-4.17.x-srpm

REPOS+=samba4repo/el/8
REPOS+=samba4repo/el/9
REPOS+=samba4repo/fedora/36
REPOS+=samba4repo/amz/2

REPODIRS := $(patsubst %,%/x86_64/repodata,$(REPOS)) $(patsubst %,%/SRPMS/repodata,$(REPOS))

CFGS+=samba4repo-8-x86_64.cfg
CFGS+=samba4repo-9-x86_64.cfg
CFGS+=samba4repo-f36-x86_64.cfg
# Amazon 2 config
#CFGS+=samba4repo-amz2-x86_64.cfg

# /et/cmock version lacks EPEL

# Link from /etc/mock
MOCKCFGS+=centos-stream+epel-8-x86_64.cfg
MOCKCFGS+=centos-stream+epel-9-x86_64.cfg
MOCKCFGS+=fedora-36-x86_64.cfg
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
python-setproctitle-1.2.x-srpm:: python-nose-1.3.x-srpm

# Samba rellies on all the othe components
samba-4.17.x-srpm:: lmdb-0.9.x-srpm
samba-4.17.x-srpm:: liburing-2.x-srpm
samba-4.17.x-srpm:: python-setproctitle-1.2.x-srpm

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

samba4repo-8-x86_64.cfg: /etc/mock/centos-stream+epel-8-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo | tee -a $@
	@echo Resetting root directory
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
	@echo Resetting root directory
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

samba4repo-f36-x86_64.cfg: /etc/mock/fedora-36-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo >> $@
	@echo Resetting root directory
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/fedora/36/x86_64/' >> $@
	@echo 'skip_if_unavailable=False' >> $@
	@echo 'metadata_expire=0' >> $@
	@echo 'gpgcheck=0' >> $@
	@echo 'priority=20' >> $@
	@echo '"""' >> $@

samba4repo-rawhide-x86_64.cfg: /etc/mock/fedora-rawhide-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@sed -i "s/^config_opts\['root'\] =/#config_opts\['root'\] =/g" $@
	@echo >> $@
	@echo Resetting root directory
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

samba4repo-amz2-x86_64.cfg: /etc/mock/amazonlinux-2-x86_64.cfg
	@echo Generating $@ from $?
	@echo "include('$?')" | tee $@
	@echo >> $@
	@echo Resetting root directory
	@echo "config_opts['root'] = 'samba4repo-{{ releasever }}-{{ target_arch }}'" >> $@
	@echo "config_opts['dnf.conf'] += \"\"\"" >> $@
	@echo '[samba4repo]' >> $@
	@echo 'name=samba4repo' >> $@
	@echo 'enabled=1' >> $@
	@echo 'baseurl=$(REPOBASE)/samba4repo/amz/2/x86_64/' >> $@
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
