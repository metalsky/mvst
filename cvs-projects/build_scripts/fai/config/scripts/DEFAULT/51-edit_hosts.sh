#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

echo "10.0.0.6 rodan" >> $target/etc/hosts
exit $error
