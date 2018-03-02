#!/bin/sh
error=0 ; trap "error=$((error|1))" ERR

cp $target/home/setup/keys/ $target/etc/ssh/
exit $error

