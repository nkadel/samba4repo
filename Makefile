#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

# Critical for Samba, not built into RHEL 6
SAMBAPKGS+=iniparser-srpm

# krb5-1.10 or later required for Samba 4 on RHEL 6
SAMBAPKGS+=krb5-srpm

# libtalloc-2.0.8 rquired for Samba 4 on RHELL 6
SAMBAPKGS+=libtalloc-srpm

# libtdb-1.23.11 required for Samba 4 on RHEL 6
SAMBAPKGS+=libtdb-srpm

# libldb-1.1.15 required for Samba 4 on RHEL 6
SAMBAPKGS+=libldb-srpm
# libldb-0.9.17 required for Samba 4 on RHEL 6
SAMBAPKGS+=libtevent-srpm

SAMBAPKGS+=samba-srpm

all clean distclean build::
	@for name in $(SAMBAPKGS); do \
		(cd $$name; $(MAKE) $(MLAGS) $@); \
	done

# Dependencies of libraries on other libraries for compilation
libtevent:: libtalloc-srpm

libldb-srpm:: libtalloc-srpm
libldb-srpm:: libtdb-srpm
libldb-srpm:: libtevent-srpm

# Samba rellies on all the othe components
samba-srpm:: krb5-srpm
samba-srpm:: libtalloc-srpm
samba-srpm:: libldb-srpm
samba-srpm:: libtevent-srpm
samba-srpm:: libtdb-srpm
samba-srpm:: iniparser-srpm


all:: $(SAMBAPKGS)

$(SAMBAPKGS):: FORCE
	(cd $@; $(MAKE) $(MLAGS))

install:: $(SAMBAPKGS)
	@for name in $?; do \
	     (cd $$name; $(MAKE) $(MFLAGS)); \
	done  

clean::
	find . -name \*~ -exec rm -f {} \;


FORCE::

