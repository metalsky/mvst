#!/bin/sh

#env_setup.py and env_setup_d.py are so that engineers can setup chroots without having permission to destroy the system

error=0 ; trap "error=$((error|1))" ERR


cp $target/home/setup/mychroot.py $target/usr/bin/
chroot $target chmod 755 /usr/bin/mychroot.py
chroot $target ln -s /usr/bin/mychroot.py /usr/bin/mychroot

exit $error
