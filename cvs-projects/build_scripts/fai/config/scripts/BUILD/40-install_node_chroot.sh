#!/bin/sh
error=0 ; trap "error=$((error|1))" ERR

echo -n "untarring node chroot... "
cd $target/home/setup/chroots
CHROOT=$target/chroot/node
mkdir -p $target/chroot
tar -C $target/chroot -xjf node.tar.bz2
echo "done"
cp $target/etc/fstab $target/etc/fstab.new
cat >> $target/etc/fstab.new <<FSTAB
san:/vol/dev_area  /chroot/node/mvista/dev_area    nfs     rw,tcp,rsize=32768,wsize=32768,noatime,hard 0 0
san:/vol/release   /chroot/node/mvista/release_area     nfs     ro,tcp,rsize=32768,wsize=32768,noatime,hard 0 0
overlord.borg.mvista.com:/home               /chroot/node/home                       nfs     rw,tcp,rsize=4096,wsize=4096,noatime,hard 0 0
proc      /chroot/node/proc proc    defaults 0 0
FSTAB
mv $target/etc/fstab.new $target/etc/fstab
cp -a $target/chroot/node/etc/ssh/*key* $target/etc/ssh/
exit $error
