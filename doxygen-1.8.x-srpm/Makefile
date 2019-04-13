#
# Build mock and local RPM versions of tools for Samba
#

# Assure that sorting is case sensitive
LANG=C

#
MOCKS+=fedora-29-x86_64

# repositories to touch after installation
MOCKCFGS+=samba4repo-f29-x86_64

#REPOBASEDIR=/var/www/linux/samba4repo
REPOBASEDIR:=`/bin/pwd`/../samba4repo

SPEC := libtalloc.spec

all:: $(MOCKS)

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
		echo "Building $@.src.rpm in $@"; \
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
		*-6-x86_64) yumrelease=el/6; yumarch=x86_64; ;; \
		*-7-x86_64) yumrelease=el/7; yumarch=x86_64; ;; \
		*-29-x86_64) yumrelease=fedora/29; yumarch=x86_64; ;; \
		*-f29-x86_64) yumrelease=fedora/29; yumarch=x86_64; ;; \
		*) echo "Unrecognized release for $$repo, exiting" >&2; exit 1; ;; \
	    esac; \
	    rpmdir=$(REPOBASEDIR)/$$yumrelease/$$yumarch; \
	    srpmdir=$(REPOBASEDIR)/$$yumrelease/SRPMS; \
	    echo "Pushing SRPMS to $$srpmdir"; \
	    rsync -av $$repo/*.src.rpm --no-owner --no-group $$repo/*.src.rpm $$srpmdir/. || exit 1; \
	    createrepo -q --update $$srpmdir/.; \
	    echo "Pushing RPMS to $$rpmdir"; \
	    rsync -av $$repo/*.rpm --exclude=*.src.rpm --exclude=*debuginfo*.rpm --no-owner --no-group $$repo/*.rpm $$rpmdir/. || exit 1; \
	    createrepo -q --update $$rpmdir/.; \
	    echo "Touching $(PWD)/../$$repo.cfg to clear cache"; \
	    /bin/touch --no-dereference $(PWD)/../$$repo.cfg; \
	done
	@for repo in $(MOCKCFGS); do \
	    echo "Touching $(PWD)/../$$repo.cfg to clear cache"; \
	    /bin/touch --no-dereference $(PWD)/../$$repo.cfg; \
	done

clean::
	rm -rf */
	rm -rf rpmbuild
	rm -f *.out

realclean distclean:: clean
	rm -f *.rpm

FORCE:
