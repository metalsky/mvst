#!/bin/bash


# simple script to automate the process of assembling engineering drops of MSD's.
# this script assumes that /mvista/dev_area is mounted locally.


REQ_ARGS=4
MVL6DIR="/mvista/dev_area/mvl6"


function usage {
	# Display script usage:
	echo ""
	echo "Usage: $0 -b BUILDTAG -t TOOLCHAIN [ -h displays usage ]"
	echo ""
}


# Check the command line:
if [ $# -lt $REQ_ARGS ]; then
	usage
	exit 1
fi


# Ensure that $HOME/engr_drop exists, if not... create it:
if [ ! -d "$HOME/engr_drop" ]; then
	echo ""
	echo "$HOME/engr_drop not found, creating... "
	mkdir $HOME/engr_drop
fi


# Check to see if /mvista/dev_area is mounted locally, if not exit:
if [ ! -d /mvista/dev_area ]; then
	echo ""
	echo "/mvista/dev_area doesn't appear to be mounted locally, exiting."
	echo ""
	exit 1
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


# piece together the tarball:
cd $MVL6DIR
tar --owner=bin --group=bin -czf $HOME/engr_drop/$BUILDTAG.tar.gz $BUILDTAG/content/collections \
$BUILDTAG/content/msds $BUILDTAG/content/installer/MVL-Integration-Platform-* \
$BUILDTAG/content/installer/$TOOLCHAIN* $BUILDTAG/content.html

echo ""
echo "Done."
echo ""
