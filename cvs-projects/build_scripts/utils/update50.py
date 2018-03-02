#!/usr/bin/python
#Standard
import sys, os 
import pexpect
#Custom
from builddefs import ENGR_AREA
from buildFunctions import mountinstall, umountinstall

#This script will run on a node, this shouldn't be run unless a resource is checked out before hand

releasedProducts =('pro/released/test/mvl500',)
hostname = 'centos3'
scripttest=0

commonApt='/opt/montavista/common/bin/mvl-common-apt-get'


def chroot(hostname, cmd, scripttest):
	os.system('chroot /chroot/%s/ %s'%(hostname,cmd))


def getArchs(product):
	return os.listdir('%s/%s'%(ENGR_AREA,product))

def getSubArch(arch):
	if arch.find('x86') == 0:	
		return 'x86'
	elif arch.find('mips') == 0:	
		return 'mips'
	elif arch.find('arm') == 0:	
		return 'arm'
	elif arch.find('ppc') == 0:	
		return 'ppc'
	

def doUpdate(product, arch):
	edition,release = product.split('/',1)
	editionApt='/opt/montavista/%s/bin/mvl-edition-apt-get'%edition
	print "Mounting"
	mountinstall(hostname,edition,release,arch)
	username = "qa-test_%s"%getSubArch(arch)
	password = "qa-test"
	#common
	print "Common"

	child = pexpect.spawn('chroot /chroot/%s/ %s update'%(hostname,commonApt))
	child.expect('.*Username:.*')
	child.sendline(username)
	child.expect('.*Password:.*')
	child.sendline(password)
	child.expect('.*Username:.*')
	child.sendline(username)
	child.expect('.*Password:.*')
	child.sendline(password)
	child.expect(pexpect.EOF)
	del child
	os.system('chroot /chroot/%s/ %s list-updates > updates.txt'%(hostname,commonApt))
	print "upgrading..."
	if os.popen('grep New updates.txt').readline():
		child = pexpect.spawn(' chroot /chroot/%s %s -y upgrade ' %(hostname, commonApt))
		child.expect('.*Username:.*')
		child.sendline(username)
		child.expect('.*Password:.*')
		child.sendline(password)
		child.expect(pexpect.EOF)
		

	#host/cross
#	os.system('echo "%s\n%s\n%s\n%s" > loginInfo'%(username,password,username,password))
#	chroot(hostname,'%s update < loginInfo'%editionApt,scripttest)
#	chroot(hostname,'%s list-updates < loginInfo > updates.txt'%editionApt,scripttest)
#	if os.popen('grep New updates.txt').readline():
#		os.system('echo "y\n%s\n%s" > loginInfo'%(username,password))
#		chroot(hostname,'%s upgrade < loginInfo'%editionApt,scripttest)
	#target
#	os.system('echo "%s\n%s\n%s\n%s" > loginInfo'%(username,password,username,password))
#	chroot(hostname,'%s update --target=%s < loginInfo"'%(editionApt,arch),scripttest)
#	chroot(hostname,'%s list-updates --target=%s < loginInfo > updates.txt'%(editionApt,arch),scripttest)
#	if os.popen('grep New updates.txt').readline():
#		os.system('echo "y\n%s\n%s" > loginInfo'%(username,password))
#		chroot(hostname,'%s upgrade --target=%s < loginInfo'%(editionApt,arch),scripttest)

	umountinstall(hostname)

def main():
	for product in releasedProducts:
		archs = getArchs(product)
		for arch in archs:
			print arch
			doUpdate(product,arch)
			return

if __name__=="__main__":
	main()



