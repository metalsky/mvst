#!/bin/sh

error=0 ; trap "error=$((error|1))" ERR

cd $target/home/setup/chroots

echo "installing chroot environments:"
mkdir $target/chroot
for i in mandrake91 suse90 redhat73 redhat80 ; do
	CHROOT=$target/chroot/$i
	echo -n "untarring $i environment ..."
	tar -C $target/chroot -xjf $i.tar.bz2
	echo -e "127.0.0.1\tlocalhost" > $CHROOT/etc/hosts
	echo -e "10.23.5.10\tglue.borg.mvista.com\tglue" >> $CHROOT/etc/hosts
	echo -e "10.23.5.3\toverlord.brog.mvista.com\toverlord" >> $CHROOT/etc/hosts
	echo "build::5003:510:Build Monkey:/home/build:/bin/bash" >> $CHROOT/etc/passwd
	echo "engr:x:510:" >> $CHROOT/etc/group
	for j in opt/montavista \
		opt/buildhhl \
		opt/buildhhl/{RPMS,BUILD,SPECS,SRPMS,SOURCES} \
		 home/build \
	 ; do
	 mkdir -p $CHROOT/$j
	 chroot $target chown build.engr /chroot/$i/$j
	done
	cp $CHROOT/usr/lib/rpm/rpmrc $CHROOT/home/build/.${i}ferpmrc
	cat >> $CHROOT/home/build/.${i}ferpmrc <<FERPMRC
macrofiles: /usr/lib/rpm/macros:/opt/montavista/config/rpm/hosts/i686-pc-linux-gnu:/opt/montavista/config/rpm/targets/%{_target}:/opt/montavista/config/rpm/common:~/.rpmmacros
FERPMRC
	chroot $target chown build.engr /chroot/$i/home/build/.${i}ferpmrc
	cat > $CHROOT/home/build/.mvlmacros <<MVLMACROS
%_build_name_fmt %%{ARCH}/%%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.mvl
MVLMACROS
	echo "done"
	echo "export LM_LICENSE_FILE=27000@overlord:27000@starscream" >> $CHROOT/home/build/.bash_profile
	echo -e "proc\t\t/chroot/$i/proc\tproc\tdefaults\t0 0" >> $target/etc/fstab
done
exit $error
