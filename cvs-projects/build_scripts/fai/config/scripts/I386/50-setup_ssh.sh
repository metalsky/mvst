#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

echo "chroot /chroot/node /etc/init.d/sshd start" > $target/etc/init.d/nodessh
chroot $target chmod 755 /etc/init.d/nodessh
chroot $target ln -s /etc/init.d/nodessh /etc/rc2.d/S20nodessh
exit $error
