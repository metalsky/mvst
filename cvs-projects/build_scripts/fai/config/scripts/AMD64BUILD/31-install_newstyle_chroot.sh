#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR
mkdir $target/chroot
cd $target/home/setup/chroots
for i in centos3 centos3_64 centos4 centos4_64 redhat90; do
	CHROOT=$target/chroot/$i
	echo -n "untarring $i environment ...\n"
	tar -C $target/chroot -xjf $i.tar.bz2
	echo -e "127.0.0.1\tlocalhost" > $CHROOT/etc/hosts
	echo -e "10.23.5.10\tglue.borg.mvista.com\tglue" >> $CHROOT/etc/hosts
	echo -e "10.23.5.3\toverlord.borg.mvista.com\toverlord" >> $CHROOT/etc/hosts
	echo -e "/proc\t\t/chroot/$i/proc\tproc\tdefaults\t0 0" >> $target/etc/fstab
done
exit $error



