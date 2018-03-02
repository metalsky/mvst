#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

cp $target/home/setup/fai/snmpd.conf $target/etc/snmp/
cp $target/home/setup/fai/snmpd $target/etc/default/

exit $error
