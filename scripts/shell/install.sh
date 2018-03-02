#!/bin/bash


# location where the drop archive has been downloaded to
# modify $TARBALL as necessary
INSTALLDIR="$PWD/$1"


# drop archive minus extension:
DROP="${INSTALLDIR##*/}"
DROP="${DROP%.tar.gz}"


# MSD name:
MSD=${DROP%%_*}


BP_TARBALL="$INSTALLDIR-bp.tar.gz"
CM_TARBALL="$INSTALLDIR-cm.tar.gz"
TOOLS_TARBALL="$INSTALLDIR-tools.tar.gz"


if [ ! -f "${TOOLS_TARBALL}" -o ! -f "${CM_TARBALL}" -o ! "${BP_TARBALL}"  ] ; then
	echo "Installation tarball\(s\) not found for buildtag $1!"
	exit 1
fi


echo ""
echo ""
echo "INSTALLDIR is $INSTALLDIR"
echo "DROP is $DROP"
echo "MSD is $MSD"
echo ""
echo ""


# these commands will unpack the archive, create the content.xml
# file, and install the Integration Platform and toolchain.
mkdir -p $INSTALLDIR
cd $INSTALLDIR


for TARBALL in $TOOLS_TARBALL $BP_TARBALL $CM_TARBALL
do
	echo "Extracting $TARBALL"
	tar zxf $TARBALL
done


sed -e "s|http://collective\.sh\.mvista\.com/dev_area/bosch|file://$PWD|g" < content.html > content.xml
echo ""
echo ""
echo "Installing Integration Platform... "


echo ""
echo ""
echo "INSTALLDIR is $INSTALLDIR"
echo "CURRENT DIR IS $PWD"
# determine which version of the IP we're working with so we can use mvl-project accordingly:
IP_INSTALLER="$INSTALLDIR/content/installer/MVL-I*-P*-Linux*Install"
if [[ `basename $IP_INSTALLER` = MVL-I*-P*-6.0.*-Install ]]; then
	IP=6.0
else
	IP=6.1
fi

./content/installer/MVL-Integration-Platform-*-Install --mode silent --prefix $PWD/tools
echo "done."
echo ""
echo ""

echo -ne "Installing the toolchain... "
for TC in ./content/installer/MVL-Toolchain-*-Install; do
	$TC --mode silent --prefix $PWD/tools;
done
echo " done."
echo ""
echo ""


# the following commands show how to create a project that uses
# the installed engineering drop archive to create and build
# a project called "newproject".  They can be executed anywhere
# on the host regardless of where the INSTALLDIR is.
PATH=$INSTALLDIR/tools/bin:$PATH

# based on the IP we found in the drop, we'll run mvl-project accordingly:
if [ $IP = 6.0 ]; then
	echo "IP 6.0 detected, running mvl-project accordingly... "
	mvl-project -m $MSD --content-xml-dir=$INSTALLDIR newproject
	echo "MVLCONTENT_OPTS = \" --content-xml-dir=$INSTALLDIR\"" >> newproject/conf/local.conf
else
	echo "IP 6.1 detected, running mvl-project accordingly... "
	mvl-project --create --dir=newproject
	mvl-project --dir=newproject --add --uri=file://$INSTALLDIR/symphony-ivi-2.6.34/solutions/mvista.com/symphony-ivi-2.6.34/symphony-ivi-2.6.34.xml
	mvl-project --dir=newproject --add --uri=file://$INSTALLDIR/symphony-ivi-cm/solutions/mvista.com/symphony-ivi-cm/symphony-ivi-cm.xml
fi


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
bitbake default-image
echo "done."
echo ""
echo ""
