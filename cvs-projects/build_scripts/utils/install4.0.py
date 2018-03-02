#!/usr/bin/python
import os, sys, re, string, time, threading, traceback
import resourceManager
# This script will install the host/redhat90, common, target and cross common apps needed to be set up a build env.

# args:
# 1- edition (product)
# 2- reltag


mvldir = None
destination = None
edition = None
editionrpmbin = None
commonrpmbin = None
buildid = None

def gettime():
	t_time = time.localtime(time.time())
	s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
	f_time = time.mktime(t_time)
	return s_time + ' [' + str(f_time) + ']'

def chroot(node,command):
	sshcmd = 'ssh root@'
	cmd = "chroot /chroot/redhat90 /bin/su - root -c '%s' >> /chroot/redhat90/home/build/chroot.log 2>&1 " % (command)
	#print 'chroot command: ' + cmd
	res = os.system('%s%s "%s"' % (sshcmd,node,cmd))
	return res







def installThread(arch):
	node = resourceManager.getResource('Install Release','install_%s'%arch,'node','Installing %s for engr_area'%arch)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# prep 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	print node
	os.system('ssh %s "sudo rm -rf /opt/montavista/*"' %node)
	os.system('ssh %s "sudo mkdir -p /chroot/redhat90/mnt/cdrom"'%node)
#mount lost, install rpm
	os.system('ssh %s "sudo mount -o loop %s/cdimages/host-%s-* /chroot/redhat90/mnt/cdrom "'%(node,mvldir,edition))
	chroot(node,'cd /; rpm2cpio /mnt/cdrom/host/redhat90/common-rpm-4* | cpio -iud')
	chroot(node,'cd /; rpm2cpio /mnt/cdrom/host/redhat90/common-rpm-b* | cpio -iud')
	chroot(node,'cd /; rpm2cpio /mnt/cdrom/host/redhat90/common-rpm-d* | cpio -iud')
	chroot(node,'cd /; rpm2cpio /mnt/cdrom/host/redhat90/host-rpm* | cpio -iud')


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# install the edition
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	image = '/mnt/cdrom/host/redhat90' 
	chroot(node, 'cd %s; ls common-rpm*.mvl | xargs %s -Uvh ' % (image, commonrpmbin))
	chroot(node,'cd %s; ls host-rpm*.mvl | xargs %s -Uvh ' % (image, editionrpmbin))
	chroot(node, 'cd %s; ls common*.mvl | grep -v rpm | grep -v apache-ant | grep -v flexnet | xargs %s -Uvh ' % (image, commonrpmbin))
	chroot(node,'cd %s; ls host*.mvl | grep -v rpm | xargs %s -Uvh ' % (image,editionrpmbin))

	image = '/mnt/cdrom/host/common' 
	chroot(node, 'cd %s; ls common*.mvl | grep -v eclipse | xargs %s -Uvh ' % (image, commonrpmbin))
	chroot(node,'cd %s; ls host*.mvl | grep -v eclipse | xargs %s -Uvh ' % (image, editionrpmbin))
	os.system('ssh %s "sudo umount /chroot/redhat90/mnt/cdrom"'%node)

#Cross
	os.system('ssh %s "sudo mount -o loop %s/cdimages/cross-%s-* /chroot/redhat90/mnt/cdrom "'%(node,mvldir,arch))
	image = '/mnt/cdrom/%s/cross/common' % (arch)
	chroot(node,'cd %s; ls *.mvl | grep -v eclipse | xargs %s -Uvh ' % (image,editionrpmbin))
	image = '/mnt/cdrom/%s/cross/redhat90' % (arch)
	chroot(node, 'cd %s; %s -Uvh *.mvl ' % (image,editionrpmbin))
	os.system('ssh %s "sudo umount /chroot/redhat90/mnt/cdrom"'%node)

#target
	os.system('ssh %s "sudo mount -o loop %s/cdimages/target-%s-* /chroot/redhat90/mnt/cdrom "'%(node,mvldir,arch))
	image = '/mnt/cdrom/%s/target' % (arch)
	chroot(node, 'cd %s; %s -Uvh *.mvl --target=%s-linux ' % (image, editionrpmbin,arch))
	os.system('ssh %s "sudo umount /chroot/redhat90/mnt/cdrom"'%node)

# move and clean up
	os.system('ssh %s "mkdir -p %s/%s"'%(node,destination,arch))
	os.system('ssh %s "sudo cp -a /chroot/redhat90/opt/montavista %s/%s/"'%(node, destination,arch))
	os.system('ssh %s "sudo rm -rf /chroot/redhat90/opt/montavista/* "'%node)
	os.system('ssh %s "sudo rm -rf /chroot/redhat90/home/build/chroot.log"'% node)
	print "made it to the end"
	resourceManager.releaseResource(node)
	return
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main(argv):
	global mvldir, destination, edition, editionrpmbin, commonrpmbin, buildid
	if len(argv) != 4:
	  print "\nUsage: %s <edition> <location> <buildid>" % (argv[0])
	  sys.exit(1)

	edition = argv[1]
	print "edition = " + edition
	mvldir = argv[2]

	buildid = argv[3]

	sys.__stdout__.flush()

	if edition == "pro":
		destination = "/mvista/engr_area/%s/released/mvl401" % (edition)
	elif edition == "cge":
		destination = "/mvista/engr_area/%s/released/mvlcge401" % (edition)
	elif edition == "mobilinux41":
		destination = "/mvista/engr_area/mobilinux/released/moblinux410" 
		edition = "mobilinux"
	elif edition == "mobilinux40":
		destination = "/mvista/engr_area/mobilinux/released/moblinux402" 
		edition = "mobilinux"
	else:
		sys.stderr.write('Unknown edition')
		sys.exit(1)

	os.system('mkdir -p %s'%(destination))

	commonrpmbin = "/opt/montavista/common/bin/mvl-common-rpm"
	editionrpmbin = "/opt/montavista/%s/bin/mvl-edition-rpm" % (edition)
	print "mvldir = " + mvldir
	print "commonrpmbin = " + commonrpmbin
	print "editionrpmbin = " + editionrpmbin 
	print "destination = " + destination
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#get archs:
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	log = open(os.path.join(mvldir,'logs','buildhhl-%s.log'%buildid),'r')

	archs = []
	for line in log.readlines():
		if re.match(r'x.*|mips2.*|arm.*|ppc.*|xtensa.*',line):
			archs.append(string.strip(line,'\n'))
		if re.match(r'Using',line): #in the log Using is printed after the archs, we don't want to scan anymore after that
			break

	threads = []
	for arch in archs:
		threads.append(threading.Thread(target=installThread,args=(arch,)))
	print archs

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

	print "Installation Completed, yay!"


if __name__=="__main__":
	main(sys.argv)



