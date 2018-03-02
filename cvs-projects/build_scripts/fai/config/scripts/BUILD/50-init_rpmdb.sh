#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

mkdir $target/var/lib/rpm
chroot $target rpm --initdb --dbpath /var/lib/rpm
exit $error
