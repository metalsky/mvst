#!/usr/bin/python

import os, sys




def main(argv):
	if len(argv) < 2:
		print "Usage: %s <chroot>"%argv[0]
		sys.exit(1)
	chroot = argv[1]
	if chroot == "centos3_64":
		os.system('dsh -cM -g node_64 -- "umount /chroot/centos3_64/proc"')
		os.system('dsh -cM -g node_64 -- "rm -rf /chroot/centos3_64"')
		os.system('dsh -cM -g node_64 -- "tar -C /chroot -jxvf /home/setup/chroots/centos3_64.tar.bz2"')
		os.system('dsh -cM -g node_64 -- "mount /chroot/centos3_64/proc"')
		os.system('dsh -cM -g node_64 -- "echo "127.0.0.1 $(hostname --fqdn)      $(hostname)" > /chroot/centos3_64/etc/hosts" ')
	else:
		os.system('dsh -acM -- "umount /chroot/%s/proc"'%chroot)
		os.system('dsh -acM -- "rm -rf /chroot/%s"'%chroot)
		os.system('dsh -acM -- "tar -C /chroot -jxvf /home/setup/chroots/%s.tar.bz2"'%chroot)
		os.system('dsh -acM -- "echo "127.0.0.1 $(hostname --fqdn)      $(hostname)" > /chroot/%s/etc/hosts"'%chroot)
		os.system('dsh -acM -- "mount /chroot/%s/proc"'%chroot)
	return
			
			
if __name__== "__main__":
	main(sys.argv)

