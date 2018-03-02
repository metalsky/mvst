#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

fcopy -iM /etc/quilt.quiltrc 
exit $error
