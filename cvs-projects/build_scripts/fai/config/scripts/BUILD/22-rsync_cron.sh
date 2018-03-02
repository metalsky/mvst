#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR
cp $target/home/setup/rsync_ssh $target/etc/cron.hourly/
chroot $target chmod 755 /etc/cron.hourly/rsync_ssh
exit $error
