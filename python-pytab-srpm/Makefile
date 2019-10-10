#
# Build mock and local RPM versions of tools for Samba
#

# Assure that sorting is case sensitive
LANG=C

MOCKS+=samba4repo-f30-x86_64
MOCKS+=samba4repo-8-x86_64
MOCKS+=samba4repo-7-x86_64

MOCKCFGS+=$(MOCKS)

#REPOBASEDIR=/var/www/linux/samba4repo
REPOBASEDIR:=`/bin/pwd`/../samba4repo

SPEC := `ls *.spec`

all:: $(MOCKS)

getsrc:: FORCE
	spectool -g $(SPEC)

srpm:: FORCE
	@echo "Building SRPM with $(SPEC)"
	rm -rf rpmbuild
	rpmbuild --define '_topdir $(PWD)/rpmbuild' \
		--define '_sourcedir $(PWD)' \
		-bs $(SPEC) --nodeps

build:: srpm FORCE
	rpmbuild --define '_topdir $(PWD)/rpmbuild' \
		--rebuild rpmbuild/SRPMS/*.src.rpm

$(MOCKS):: srpm FORCE
	@if [ -e $@ -a -n "`find $@ -name \*.rpm`" ]; then \
		echo "	Skipping RPM populated $@"; \
	else \
		echo "Storing " rpmbuild/SRPMS/*.src.rpm "as $@.src.rpm"; \
		install rpmbuild/SRPMS/*.src.rpm $@.src.rpm; \
		echo "Actally building RPMS in $@"; \
		rm -rf $@; \
		mock -q -r $(PWD)/../$@.cfg \
		     --resultdir=$(PWD)/$@ \
		     $@.src.rpm; \
	fi

mock:: $(MOCKS)

install:: $(MOCKS)
	@for repo in $(MOCKS); do \
	    echo Installing $$repo; \
	    case $$repo in \
		*-7-x86_64) yumrelease=el/7; yumarch=x86_64; ;; \
		*-8-x86_64) yumrelease=el/8; yumarch=x86_64; ;; \
		*-30-x86_64) yumrelease=fedora/30; yumarch=x86_64; ;; \
		*-f30-x86_64) yumrelease=fedora/30; yumarch=x86_64; ;; \
		*-rawhide-x86_64) yumrelease=fedora/rawhide; yumarch=x86_64; ;; \
		*) echo "Unrecognized release for $$repo, exiting" >&2; exit 1; ;; \
	    esac; \
	    rpmdir=$(REPOBASEDIR)/$$yumrelease/$$yumarch; \
	    srpmdir=$(REPOBASEDIR)/$$yumrelease/SRPMS; \
	    echo "Pushing SRPMS to $$srpmdir"; \
	    rsync -av $$repo/*.src.rpm --no-owner --no-group $$repo/*.src.rpm $$srpmdir/. || exit 1; \
	    createrepo -q $$srpmdir/.; \
	    echo "Pushing RPMS to $$rpmdir"; \
	    rsync -av $$repo/*.rpm --exclude=*.src.rpm --exclude=*debuginfo*.rpm --no-owner --no-group $$repo/*.rpm $$rpmdir/. || exit 1; \
	    createrepo -q $$rpmdir/.; \
	done
	@for repo in $(MOCKCFGS); do \
	    echo "Touching $(PWD)/../$$repo.cfg"; \
	    /bin/touch --no-dereference $(PWD)/../$$repo.cfg; \
	done

clean::
	rm -rf */
	rm -rf rpmbuild
	rm -f *.out

realclean distclean:: clean
	rm -f *.rpm

FORCE:
