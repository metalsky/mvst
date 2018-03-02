#!/bin/bash


# location where the drop archive has been downloaded to
# modify as necessary
ARCHIVE="$HOME/x86-target-64-2.6.28_091030_0903699.tar.gz"


# the name of the drop archive (minus extension)
DROP="${ARCHIVE##*/}"
DROP="${DROP%.tar.gz}"

# the name of the MSD
MSD=${DROP%%_*}

# the directory where the archive should be installed
INSTALLDIR="$PWD/$DROP"


# these commands will unpack the archive, create the content.xml
# file, and install the Integration Platform and toolchain.
mkdir -p $INSTALLDIR
cd $INSTALLDIR
echo "Untarring MSD... "
echo ""
tar zxvf $ARCHIVE
echo "done."
echo ""
echo ""
sed -e "s|http://collective\.sh\.mvista\.com/dev_area/mvl6|file://$PWD|g" < $DROP/content.html > content.xml
echo "Installing Integration Platform... "
echo ""
./$DROP/content/installer/MVL-Integration-Platform-*-Install --mode console --prefix $PWD/tools
echo "done."
echo ""
echo ""
echo "Installing the toolchain... "
echo ""
./$DROP/content/installer/*/MVL-Toolchain-*-Install --mode console --prefix $PWD/tools
echo "done."
echo ""
echo ""


# the following commands show how to create a project that uses
# the installed engineering drop archive to create and build
# a project called "newproject".  They can be executed anywhere
# on the host regardless of where the INSTALLDIR is.
PATH=$INSTALLDIR/tools/bin:$PATH
echo "Running mvl-project... "
echo ""
mvl-project -m $MSD --content-xml-dir=$INSTALLDIR newproject
echo " done."
echo ""
echo ""
echo "MVLCONTENT_OPTS = \" --content-xml-dir=$INSTALLDIR\"" >> newproject/conf/local.conf
cd newproject
echo "Sourcing setup.sh... "
source setup.sh
echo "done."
echo ""
echo ""
echo "Running bitbake... "
echo ""
bitbake default-image
echo "done."
echo ""
echo ""
