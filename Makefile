
YUMSRCDIR=/var/www/mirrors/scientific/6x/x86_64/os
YUMTARGETDIR=/var/www/mirrors/smbrepo/6/x86_64

# krb5 update required, independent of Samba published packagees
SAMBAPKGS+=krb5-srpm

# Critical for Samba
SAMBAPKGS+=iniparser-srpm

# libtalloc does not require others
SAMBAPKGS+=libtalloc-srpm

# Pre-req for others
SAMBAPKGS+=libtdb-srpm

SAMBAPKGS+=libldb-srpm
SAMBAPKGS+=libtevent-srpm

SAMBAPKGS+=samba4-srpm

all clean distclean build::
	@for name in $(SAMBAPKGS); do \
		(cd $$name; $(MAKE) $(MLAGS) $@); \
	done

# Dependencies
libtevent:: libtalloc-srpm

libldb-srpm:: libtalloc-srpm
libldb-srpm:: libtdb-srpm
libldb-srpm:: libtevent-srpm

# Samba rellies on all the others
samba-srpm:: krb5-srpm
samba-srpm:: libtalloc-srpm
samba-srpm:: libldb-srpm
samba-srpm:: libtevent-srpm
samba-srpm:: libtdb-srpm
samba-srpm:: iniparser-srpm


$(SAMBAPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS)); \

install:: FORCE

clean::
	find . -name \*~ -exec rm -f {} \;


# Set up symlinks
update:: $(YUMSRCDIR)
	ln -s -f -n $(YUMSRCDIR)/Packages  $(YUMTARGETDIR)/Packages
	createrepo -v --update $(YUMTARGETDIR)/

FORCE::

