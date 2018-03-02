#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR
cat $target/home/setup/supermicro_i686_lmsensors >> $target/etc/modules
exit $error

