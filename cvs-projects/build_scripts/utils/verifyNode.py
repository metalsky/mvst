#!/usr/bin/python


import os, sys, re, traceback, string
import builddefs


MIN_DISK = 3.5		# 21% of a 16G disk, data taken from node-24 based on 3 builds
ChrootList = ('redhat90','centos3','centos3_64','redhat80','redhat73','suse90','mandrake91')


class DiskError(StandardError):
	pass


class SshError(StandardError):
	pass


class ChrootError(StandardError):
	pass


class MountError(StandardError):
	pass


class ArchError(StandardError):
	pass


def checkSsh(hostName, serviceType):
	# ssh for regular nodes are done via resource manager, this verifies that ssh running on alternate ports is working as well
	port = '22'
	username = 'build'

	if serviceType == "node":
		port = '2080'
	elif serviceType == "cygwin-4022":
		port = '4022'
	elif serviceType == "cygwin-322":
		port = '322'

	if os.popen('ssh %s@%s -p %s "echo "hi""'%(username,hostName,port)).readline() == "hi\n":
		return 
	else:
		raise SshError, "Could not ssh to host"

	
def checkChroot(hostName, serviceType):
	if serviceType in ('cygwin-22','cygwin-4022','cygwin-322','node', 'none'):
		return
	else:
		if os.popen('ssh build@%s "ls -d /chroot/%s"'%(hostName,serviceType)).readline() == "/chroot/%s\n"%serviceType:
			pass
		else:
			raise ChrootError, 'Chroot "%s" does not exist'%serviceType

		# We should probably check that proc is mounted too

		if serviceType == "solaris8":
			if os.popen('ssh root@%s mount | grep /chroot/%s/proc'%(hostName,serviceType)).readline():
				return
			else:
				raise ChrootError, "proc is not mounted in chroot"
		else:
			if os.popen('ssh build@%s mount | grep /chroot/%s/proc'%(hostName,serviceType)).readline():
				pass
			else:
				raise ChrootError, "proc is not mounted in chroot"

			# Need to check ownership on /opt/montavista and contents
			if serviceType in ('sol7',):
				pass
			elif len(os.popen('ssh build@%s "ls -ld /chroot/%s/opt/montavista" | grep build'%(hostName,serviceType)).readline()) >= 1:
				pass
			else:
				# Check the top level underneath /opt/montavista - its enough to tell us if we have a root install
				raise ChrootError, "Ownership issues in /chroot/%s/opt/montavista"%serviceType
			
			if serviceType in ('sol7',):
				pass
			elif len(os.popen('ssh build@%s "ls /chroot/%s/opt/montavista/"'%(hostName,serviceType)).readlines()) < 1:
				# empty directory, don't do the next check
				return
			elif len(os.popen('ssh build@%s "ls -l /chroot/%s/opt/montavista" | grep root'%(hostName,serviceType)).readline()) >= 1:
				raise ChrootError, "Ownership issues in /chroot/%s/opt/montavista/"%serviceType


def checkSpace(hostName):
	if re.match(r'node-', hostName) or  re.match(r'cygwin-', hostName):
		drive = os.popen('ssh build@%s df -h / | grep /'%(hostName)).readline()
		# fourth column is space available, we will extract it
		space_avail = string.join(string.split(drive),' ').split(' ')[2]
		parsed = re.match(r'(.+)(\w)',space_avail)
		if parsed.group(2) != 'G':
			raise DiskError, "Disk does not have enough disk space available"
		elif float(parsed.group(1)) < MIN_DISK:
			raise DiskError, "Disk does not have enough disk space available"

	elif re.match(r'solaris8-', hostName):
		pass	
	else:
		raise StandardError, "Unknown host type"


def checkArch(hostName):
	if re.match(r'node-', hostName):
		arch = string.strip(os.popen('ssh %s "uname -m"'%hostName).readline(),'\n')
		if not re.match(r'i686',arch):
			raise ArchError, "Node is not reporting correct architecture - should be i686"


def checkMounts(hostName, serviceType):
	# We need to check *_area, if cluster env ened to check for them inside the cluster env, no mounts to check on cygwin
	mountpoints = (builddefs.DEV_AREA, builddefs.RELEASE_AREA, builddefs.ENGR_AREA, '/home')
	# Check the local filesystem in case it went readonly
	if serviceType != "cygwin":
		os.system('ssh build@%s touch /tmp/testfile'%hostName)
		if os.popen('ssh build@%s ls -ld /tmp/testfile'%hostName).readline():
			os.system('ssh build@%s rm -f /tmp/testfile'%hostName)
		else:
			raise DiskError, "Disk is not writable"

	if serviceType in ("node", "sol7"): # cluster
		for mount in mountpoints:
			if mount == builddefs.ENGR_AREA:
				pass
			elif os.popen('ssh build@%s mount | grep "/chroot/%s%s"'%(hostName, serviceType, mount)).readline():
				pass
			else:
				raise MountError, "Cluster Environment missing mount: %s"%mount

	elif serviceType in ChrootList: # standard node setup
		for mount in mountpoints:
			if os.popen('ssh build@%s mount | grep "on %s"'%(hostName, mount)).readline():
				pass
			else:
				raise MountError, "Node missing mount: %s"%mount

	# this also has to be root because solaris10 doesn't allow build to issue the command "mount"
	# solaris8 can be a sol8 or a sol10 box which both use /mvista/dev_area, on sol8 /mvista/dev_area is a link
	elif serviceType == "solaris8":
		for mount in mountpoints:
			if mount == builddefs.ENGR_AREA:
				pass
			# we just need to know that its mounted somewhere
			elif os.popen('ssh root@%s mount | grep %s'%(hostName, mount)).readline():
				pass
			else:
				raise MountError, "Missing mount: %s"%mount
	
	else:
		#we don't care about cygwin
		return 


def verifyNode(hostName, serviceType):
	if serviceType == 'solaris7':
		serviceType = 'sol7'
	elif serviceType == None:
		serviceType = 'none'
	try:
		checkSsh(hostName, serviceType)
		checkMounts(hostName, serviceType)
		checkSpace(hostName)
		checkChroot(hostName, serviceType)
		checkArch(hostName)

	# any issues go with a failure, but right now we'll just return a fail on any error
	except:
		# todo: If there is a configuration issue we would tag it in the resource manager here before returning the failure
		traceback.print_exc()
		return builddefs.FAIL
	# all is well
	return builddefs.SUCCESS


def printUsage():
	# print usage
	print ""
	print "Usage: %s <HOSTNAME> <SERVICE>" % (sys.argv[0])
	print ""
	print "\tHOSTNAME should be a valid hostname (i.e. node-7 or cygwin-7)"
	print ""
	print "\tSERVICE can be either:"
	print "\t1) A valid chroot environment (i.e. 'centos3_64' or 'node')"
	print "\t2) A valid SSHD (i.e. 'cygwin-22' or 'cygwin-322')"
	print ""


def main(argv):
	if len(sys.argv) != 3:
		printUsage()
		sys.exit(1)
	else:
		print verifyNode(argv[1],argv[2])


if __name__ == "__main__":
	main(sys.argv)
