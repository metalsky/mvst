#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

# add user build:
echo 'Adding group "engr"'
chroot $target groupadd -g 510 engr
exit $error
