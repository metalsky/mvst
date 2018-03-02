#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

fcopy -iM /etc/default/smartmontools
exit $error
