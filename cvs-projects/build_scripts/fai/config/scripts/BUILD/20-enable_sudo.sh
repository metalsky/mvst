#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

fcopy -iM /etc/sudoers
chmod 440 $target/etc/sudoers

exit $error
