#!/bin/bash


# simple script to automate the process of assembling engineering drops of MSD's.
# this script assumes that /mvista/dev_area is mounted locally.


REQ_ARGS=4
MVL6DIR="/mvista/dev_area/bosch"
MVL6IP="/mvista/dev_area/integration_platform"


function usage {
	# Display script usage:
	echo ""
	echo "Usage: $0 -b BUILDTAG -t TOOLCHAIN [ -h displays usage ]"
	echo ""
}


# Check the command line:
if [ $# -lt $REQ_ARGS ];
	then
		usage
		exit 1
fi


# Ensure that $HOME/engr_drop exists, if not... create it:
echo ""
echo ""
echo -n "1. Checking for drop dir: "
if [ ! -d "$HOME/engr_drop" ];
	then
		echo "$HOME/engr_drop not found, creating."
		mkdir $HOME/engr_drop
	else
		echo "found $HOME/engr_drop."
fi


# Check to see if /mvista/dev_area is mounted locally, if not exit:
echo -n "2. Checking /mvista/dev_area mount: "
if [ ! -d /mvista/dev_area ];
	then
		echo "/mvista/dev_area doesn't appear to be mounted locally, exiting."
		exit 1
	else
		echo "found."
fi

# evaluate args:
while getopts "b:ht:" ARGS;
do
	case $ARGS in
		b)	BUILDTAG=$OPTARG;;

		h)	usage
			exit 0;;

		t)	TOOLCHAIN=$OPTARG;;

		*)	usage
			exit 1;;
	esac
done

# checking for build and content dir:
echo -n "3. Checking for content dir: "
if [ ! -d "$MVL6DIR/$BUILDTAG/content" ];
	then
		echo "$MVL6DIR/$BUILDTAG/content not found: 
		This engr drop will not work, exiting"
		exit 1;
	else
		echo "found, continuing"
fi


# check for installer directory, if its there, remove it remake it; if not there, create it:
echo -n "4. Checking for installer dir: "
if [ ! -d "$MVL6DIR/$BUILDTAG/content/installer" ];
	then
		echo "$MVL6DIR/$BUILDTAG/content/installer does not exists, creating"  
		mkdir $MVL6DIR/$BUILDTAG/content/installer
	else
		echo "$MVL6DIR/$BUILDTAG/content/installer directory maybe dirty. 
		Removing and recreating" 
		rm -rf  $MVL6DIR/$BUILDTAG/content/installer
		echo "  Making $MVL6DIR/$BUILDTAG/content/installer directory" 
		mkdir $MVL6DIR/$BUILDTAG/content/installer
fi
# copy over the appropriate IP:
IPDIR="$MVL6IP/`/bin/cat $MVL6DIR/$BUILDTAG/$BUILDTAG.ip`/build/installers"
echo -n "5. Copying IP from $IPDIR to $MVL6DIR/$BUILDTAG/content/installer... "
sudo /bin/cp $IPDIR/MVL-Integration-Platform*-Install $MVL6DIR/$BUILDTAG/content/installer
echo "done."
# copy over the appropriate toolchain:
TCDIR="$MVL6IP/`/bin/cat $MVL6DIR/$BUILDTAG/$BUILDTAG.toolchain`/build/installers"
echo -n "6. Copying Toolchains from $TCDIR to $MVL6DIR/$BUILDTAG/content/installer... "
sudo /bin/cp $TCDIR/*$TOOLCHAIN* $MVL6DIR/$BUILDTAG/content/installer
sudo /bin/cp $TCDIR/*i686-gnu* $MVL6DIR/$BUILDTAG/content/installer
echo "done."

# piece together the tarball:
echo -n "7. Creating engineering drop for $MVL6DIR/$BUILDTAG... "
cd $MVL6DIR
tar --owner=bin --group=bin -czf $HOME/engr_drop/$BUILDTAG.tar.gz --exclude=.git --exclude=svn $BUILDTAG/content/collections \
$BUILDTAG/content/msds $BUILDTAG/content/installer $BUILDTAG/content.html
echo "done."

#Make the md5sum file
echo ""
echo -n "8. Making the README.md5sum file... "

cd $HOME/engr_drop

echo "The following information is the MD5 checksums of each file
contained in this directory.  This information is used to
verify that the files downloaded from this directory were not
corrupted during the transfer.

           md5sum                          file
--------------------------------  ---------------------------" > README.md5sum

md5sum $BUILDTAG.tar.gz >> README.md5sum

if [ -e README ];
  then
	md5sum README >> README.md5sum
  else
        echo "No README Doc file available for md5sum"
fi

if [ -e  install.sh ];
  then
  	md5sum install.sh >> README.md5sum
  else
      	echo "No install.sh available for md5sum"
fi
echo -n " All Done."
echo ""
