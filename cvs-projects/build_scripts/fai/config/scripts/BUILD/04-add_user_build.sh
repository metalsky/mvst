#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

# add user build:
echo 'Adding user "build" in group "engr"'
chroot $target groupadd -g 510 engr
chroot $target useradd -m -d /home/build -u 5003 -g 510 -s /bin/bash -p moEDzkhhyFOnQ   -c "Build Monkey" build
exit $error
