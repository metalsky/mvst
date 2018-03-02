#!/bin/sh

#env_setup.py and env_setup_d.py are so that engineers can setup chroots without having permission to destroy the system

error=0 ; trap "error=$((error|1))" ERR


cp $target/home/setup/env_setup.py $target/usr/bin/
chroot $target chmod 755 /usr/bin/env_setup.py
chroot $target ln -s /usr/bin/env_setup.py /usr/bin/env_setup

cp $target/home/setup/env_setup_d.py $target/usr/sbin/
cp $target/home/setup/envLaunch $target/etc/init.d/
chroot $target chmod 700 /usr/sbin/env_setup_d.py
chroot $target update-rc.d envLaunch defaults

exit $error
