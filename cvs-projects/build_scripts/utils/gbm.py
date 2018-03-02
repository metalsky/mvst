#!/usr/bin/python

import os, sys, re

mountPoint = '/mnt/gbm'
sourcesDict = {}
workingDir = sys.argv[1]
errorList = []
DONE = 1

def loadSourcesDict(srcIso):
	global sourcesDict
	mountCD('%s'%(srcIso))
	for rpm in os.listdir('%s/SRPMS'%(mountPoint)):
		sourcesDict[rpm] = []
	for rpm in os.listdir('%s/host-tools/windows2000/SRPMS'%(mountPoint)):
		sourcesDict[rpm] = []
	umountCD()
#	print sourcesDict.keys()

def verifyRpms(isoList):
	global errorList, sourcesDict
	for iso in isoList:
		print iso
		mountCD('%s'%(iso))
		for rpm in os.popen('find %s | grep .*\.mvl'%mountPoint).readlines():
			rpm = rpm.strip('\n')
			try:
				srcRpm = os.popen('rpm -qip %s | grep Source'%rpm).readline().split()[-1]
			
				if sourcesDict.has_key(srcRpm):
					sourcesDict[srcRpm].append(rpm.split()[-1])
				else:
					errorList.append(rpm.split()[-1])
			except:
				pass
#				print "Error processing: %s"%rpm
		umountCD()
		

def umountCD():
	os.system('sudo umount %s'%mountPoint)

def mountCD(cdPath):
	if not os.path.exists(mountPoint):
		os.system('mkdir -p %s'%mountPoint)
	print "Mounting: %s"%cdPath
	os.system('sudo mount -o loop %s %s'%(cdPath, mountPoint))


def main(argv):
	global workingDir
	if not os.path.exists(argv[1]):
		print "this isn't a dir"
		sys.exit(1)
	workingdir = argv[1]
	isoArchList = []
	for iso in os.popen('ls %s/*host*.iso'%workingDir).readlines():
		isoArchList.append(iso.strip('\n'))
	srcIso =  os.popen('ls %s/src*.iso'%argv[1]).readline().strip('\n')
#	print srcIso
#	print isoArchList
	loadSourcesDict(srcIso)
	verifyRpms(isoArchList)
	for key in sourcesDict.keys():
		os.system('echo "%s:%s" >> outfile '%(key,sourcesDict[key]))

	for entry in errorList:
		os.system('echo "No Owner: %s" >> outfile'%entry)










if __name__=="__main__":
	main(sys.argv)


