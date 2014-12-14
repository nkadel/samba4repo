#
# Makefile - build wrapper for Samba 4 on RHEL 6
#
#	git clone RHEL 6 SRPM building tools from
#	https://github.com/nkadel/[package] into designated
#	SAMBAPKGS below
#
#	Set up local 

# libntdb new in Samba 4.1.x
# Build in samba-srpm by default
#SAMBAPKGS+=libntdb-srpm

# Critical for samba-srpm, not built into RHEL 6
SAMBAPKGS+=iniparser-srpm

# libtalloc-2.1.1 required for Samba 4 on RHELL 6
SAMBAPKGS+=libtalloc-srpm

# libtdb-1.3.3 required for Samba 4 on RHEL 6
SAMBAPKGS+=libtdb-srpm

# libldb-1.1.18 required for Samba 4 on RHEL 6
SAMBAPKGS+=libldb-srpm

# libtevent-0.9.22 required for Samba 4 on RHEL 6
SAMBAPKGS+=libtevent-srpm

# Current release 4.1.14
SAMBAPKGS+=samba-srpm

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

maintainer-clean::
	rm -rf $(SAMBAPKGS)

# Git clone operations, not normally required
# Targets may change

iniparser-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/iniparser-3.1-srpm.git iniparser-srpm

libtalloc-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtalloc-2.0.8-srpm.git libtalloc-srpm

libntdb-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libntdb-1.0-srpm.git libntdb-srpm

libtdb-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtdb-1.2.12-srpm.git libtdb-srpm

libldb-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libldb-1.1.16-srpm.git libldb-srpm

libtevent-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/libtevent-0.9.18-srpm.git libtevent-srpm

samba-srpm::
	@[ -d $@/.git ] || \
	git clone git://github.com/nkadel/samba-4.1.x-srpm.git samba-srpm


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
#samba-srpm:: iniparser-srpm


# Actually build in directories
#$(SAMBAPKGS):: FORCE
#	(cd $@; $(MAKE) $(MLAGS))

clean::
	find . -name \*~ -exec rm -f {} \;

FORCE::

