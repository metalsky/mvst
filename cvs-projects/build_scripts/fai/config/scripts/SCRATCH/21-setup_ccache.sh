#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR
#Profile with default ccache dir
fcopy -iM /etc/profile
#Set Permissions, ccache is a partition so we don't have to worry about too much
chroot $target chgrp engr /ccache
chroot $target chmod g+s /ccache
chroot $target ccache -M 10G


exit $error
