#!/bin/sh


echo "/home /etc/auto.home --timeout=60" >> $target/etc/auto.master
fcopy -iM /etc/auto.home

exit $error

