#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR
rm -f $target/etc/rc2.d/S20ssh
echo "linux32 /etc/init.d/ssh start" > $target/etc/init.d/ssh32
chroot $target chmod 755 /etc/init.d/ssh32
chroot $target ln -s /etc/init.d/ssh32 /etc/rc2.d/S20ssh

echo "linux32 chroot /chroot/node /etc/init.d/sshd start" > $target/etc/init.d/nodessh
chroot $target chmod 755 /etc/init.d/nodessh
chroot $target ln -s /etc/init.d/nodessh /etc/rc2.d/S20nodessh
rsync -avz root@overlord:.ssh $target/root/
exit $error
