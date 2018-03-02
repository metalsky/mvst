#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

chroot $target ntpdate time.sh.mvista.com 
fcopy -iM /etc/ntp.conf 
exit $error
