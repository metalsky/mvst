#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

cd $target/etc
# Create mount point for /mvista/dev_area and /mvista/archive
echo "Creating Mount points"
mkdir -p $target/mvista/dev_area $target/mvista/release_area $target/mvista/engr_area

# Add mounts to /etc/fstab:
echo "Adding /mvista/dev_area and /home to /etc/fstab"
cp fstab fstab.new
cat >> fstab.new <<FSTAB
dumbo:/vol/dev_area  /mvista/dev_area        nfs     ro,tcp,rsize=32768,wsize=32768,noatime,hard 0 0
dumbo:/vol/release   /mvista/release_area nfs     ro,tcp,rsize=32768,wsize=32768,noatime,hard 0 0
dumbo:/vol/engr_area /mvista/engr_area nfs 	ro,tcp,rsize=8192,wsize=8192,noatime,hard 0 0

FSTAB
mv fstab.new fstab
exit $error
