#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

#We need to mount /home/ now for the rest of the setup
mount overlord:/home $target/home
exit $error
