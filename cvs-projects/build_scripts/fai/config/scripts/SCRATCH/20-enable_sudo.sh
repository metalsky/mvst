#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

cd $target/etc
echo "ALL  ALL=NOPASSWD: /usr/sbin/chroot" >> $target/etc/sudoers
echo "ALL  ALL=NOPASSWD: /bin/tar" >> $target/etc/sudoers
exit $error
