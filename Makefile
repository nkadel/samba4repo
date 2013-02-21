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

all:: $(SAMBAPKGS)

all clean install:: FORCE
	@for name in $(SAMBAPKGS); do \
	     (cd $$name; $(MAKE) $(MFLAGS) $@); \
	done  

# Git clone operations, not normally required
# Targets may change

krb5-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/krb5-1.10.3-srpm.git krb5-srpm

iniparser-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/iniparser-3.1-srpm.git iniparser-srpm

libtalloc-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtalloc-2.0.8-srpm.git libtalloc-srpm

libtdb-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtdb-1.2.11-srpm.git libtdb-srpm

libldb-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libldb-1.1.15-srpm.git libldb-srpm

libtevent-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtevent-0.9.17-srpm.git libtevent-srpm

samba-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/samba-4.0.3-srpm.git samba-srpm


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


# Actually build in directories
#$(SAMBAPKGS):: FORCE
#	(cd $@; $(MAKE) $(MLAGS))

clean::
	find . -name \*~ -exec rm -f {} \;

FORCE::

