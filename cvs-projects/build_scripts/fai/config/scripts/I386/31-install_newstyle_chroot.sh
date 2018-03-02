#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

mkdir $target/chroot
cd $target/home/setup/chroots
for i in redhat90 centos3 centos4 ; do
	CHROOT=$target/chroot/$i
	echo -n "untarring $i environment ..."
	tar -C $target/chroot -xjf $i.tar.bz2
	echo -e "127.0.0.1\tlocalhost" > $CHROOT/etc/hosts
	echo -e "10.23.5.10\tglue.borg.mvista.com\tglue" >> $CHROOT/etc/hosts
	echo -e "10.23.5.3\toverlord.brog.mvista.com\toverlord" >> $CHROOT/etc/hosts
	echo "proc\t\t/chroot/$i/proc\tproc\tdefaults\t0 0" >> $target/etc/fstab
done
exit $error



