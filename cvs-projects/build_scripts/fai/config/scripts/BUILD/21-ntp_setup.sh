#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

chroot $target ntpdate ntp.borg.mvista.com 
fcopy -iM /etc/ntp.conf
exit $error
