#!/usr/bin/python2

#Gonna clean up the update scripts a bit and do some reorg, first we're gonna start making some functions and make the update code somewhat readable.

import os, re, sys, string
from manifestVerify import validateManifest


stageDir = '/mvista/arch'
ARCHS = 0
HOSTS = 1

pakList = []

#functions that allow us to do things

def updateManifest(productDir, dirname):
	global stageDir
	os.chdir('%s/%s/updates'%(stageDir, productDir))
	print "Updating Manifest.xml..."
	os.system('%s/updateManifest.py %s package'%(stageDir, dirname))
	return


def getJobList(updateDir, runtypes, apptype, ProdDict):
	os.chdir('%s/SRPMS' % (updateDir))
	rpmname = os.popen('ls *%s*' % (apptype)).readlines()
	i = 0
	while(i < len(rpmname)):
		if(string.count(rpmname[i],'cross')):
			if "crosscopy" not in runtypes:
				runtypes.append("crosscopy")
		elif(string.count(rpmname[i],'host-tool')):
			if "host-tool" not in runtypes:
				runtypes.append("host-toolcopy")
		elif(string.count(rpmname[i],'host') or string.count(rpmname[i],'common')):
			if "hostcopy" not in runtypes:
				runtypes.append("hostcopy")
		else:
			if "copy" not in runtypes:
				runtypes.append("copy")
		i = i + 1
	return

def getDirname():
	try:
		x = input("Please choose the Directory Name: ")
	except SyntaxError:
		print "Bad Syntax"
		sys.exit(1)
	except:
		print "Unknown Error"
		sys.exit(1)
	return x



def selectDirName(updateDir, apptype):
	os.chdir('%s/SRPMS' % (updateDir))
	rpmname = os.popen('ls *%s*' % (apptype)).readlines()
	dirnames = []
	i = 0
	for d in rpmname:
		dirnames.append(string.replace(string.strip(d),'.src.rpm',''))
		print '%s. dirname = %s'%(i,dirnames[i])
		i = i + 1

	print "%s. Cancel Upload"%(i)

	choiceNum = getDirname()

	while( choiceNum > i ):
		print "Invalid Entry"
		choiceNum = getDirname()

	if (choiceNum == i):
		print "Bye!"
		sys.exit(1)
	else:
		dirname = dirnames[choiceNum]
	return dirname


def getVersion(dirname):
	dirRegEx = re.compile(r'.+-(\d+.+)-.*\.|-\d\d\d\d\d\d\d.*')
	extracted = dirRegEx.match(dirname)
	version = extracted.group(1)
	return version


def pickHost():
	pickone = raw_input("Would you like cross copy for single host?[y/N]:  ")
	if pickone in ('y','Y'):
		print "1. windows2000"
		print "2. solaris8"
		try:
			choice = input("Enter Selection:")
			if choice == 1:
				hosttype = 'windows2000'
			elif choice == 2:
				hosttype = 'solaris8'
			else:
				print "Error, dying...."
				sys.exit(1)
		except:
			print "You hit a bad button"
			sys.exit(1)
		return hosttype
	return None

def postProcessAdd(pakName):
	global pakList
	if pakName not in pakList:
		pakList.append(pakName)
	return


def postProcess(targetDir, outFile):
	global stageDir, pakList
	os.chdir('%s/%s/updates'%(stageDir,targetDir))
	for pak in pakList:
		if os.path.exists('%s'%(pak)):
			updateManifest(targetDir, pak)
			outFile.write("%s -> %s\n"%(targetDir, pak))
	print "Validating Manifest Files"
	validateManifest()


def crossCopy(updateDir, pakName, targetDir, prodDict, hosttype, version):
	global ARCHS, HOSTS, stageDir
	if hosttype not in prodDict[targetDir][1] and hosttype != None:
		return #skip, we don't have anything to copy
	print 'making %s in %s/updates...' % (pakName,targetDir)
	os.chdir('%s/%s/updates' % (stageDir,targetDir))
	os.system('mkdir -p %s' % (pakName))
	os.chdir(pakName)
	print 'Currently in %s...' % (targetDir)
	if not os.path.exists('%s/SRPMS'%(updateDir)):
		os.system('mkdir -p SRPMS' )
		os.system('cp -a %s/SRPMS/*%s* SRPMS/' % (updateDir,version))
		os.system('mkdir -p %s/cross' % (subd))
	for subd in prodDict[targetDir][ARCHS]:
		if hosttype != None: #we know its a one host because we're still in here and we know that this hosts is part of the product
			os.system('cp -a %s/%s/cross/%s ./%s/cross/' % (updateDir,subd,hosttype,subd))
  	else:
			for subh in prodDict[targetDir][HOSTS]:
				if len(os.listdir('%s/%s/cross/%s'%(updateDir,subd,subh))) > 0: #don't copy empty host dirs i.e. no prelink in windows
					os.system('cp -a %s/%s/cross/%s ./%s/cross/' % (updateDir,subd,subh,subd))
	postProcessAdd(pakName)
	return




def crossCommonCopy():
	pass

def targetCopy(updateDir, pakName, targetDir, prodDict, version):
	global ARCHS, stageDir
	print "Copying %s"%(targetDir)
#We don't want to make empty directories if there's nothing to copy
	if len(os.listdir('%s/%s/target'%(updateDir,prodDict[targetDir][ARCHS][0]))) < 0:
		return
	else:
		os.chdir('%s/%s/updates' % (stageDir, targetDir))
		os.system('mkdir -p %s' % (pakName))
		os.chdir(pakName)
		if not os.path.exists('%s/SRPMS'%(updateDir)):
			os.system('mkdir -p SRPMS ')
			os.system('cp -a %s/SRPMS/*%s* SRPMS/' % (updateDir,version))
		for subd in prodDict[targetDir][ARCHS]:
			os.system('cp -a %s/%s .' % (updateDir,subd))
		postProcessAdd(pakName)

def hostCopy(updateDir, pakName, targetDir, prodDict, hosttype):
	global HOSTS, stageDir
	if hosttype != None and hosttype not in prodDuct[targetDir][HOSTS]:
		return
	os.chdir('%s/%s/updates' % (stageDir, targetDir))
	os.system('mkdir -p %s/host' % (pakName))
	os.chdir(pakName)
	print 'Currently in %s...' % (targetDir)
	os.system('cp -a %s/SRPMS .' % (updateDir))
	if hosttype != None:
		if len(os.listdir('%s/host/%s'%(updateDir,subd))) > 0: #the app built for particular host, no empty dirs
			os.system('cp -a %s/host/%s host' % (updateDir,hosttype))
			postProcessAdd(pakName)
	else:
		for subd in prodDict[targetDir][HOSTS]:
			if len(os.listdir('%s/host/%s'%(updateDir,subd))) > 0: #the app built for particular host, no empty dirs
				os.system('cp -a %s/host/%s host' % (updateDir,subd))
			postProcessAdd(pakName)



def hostToolCopy():
	pass



