#!/bin/sh

#Its easier to just copy the appropriate files than do anything else

error=0 ; trap "error=$((error|1))" ERR

cp $target/home/setup/libnss-ldap-shared.conf $target/etc/libnss-ldap.conf
cp $target/home/setup/nsswitch.conf_ldap $target/etc/nsswitch.conf

exit $error


