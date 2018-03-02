#!/usr/bin/python

###########################################
#
#               aptRelease.py
#
#  Usage:
#
#
#  aptRelease.py copies rpms from builds to
#  various apt repositories.  This script
#  also runs a handful of programs that 
#  generate package lists and other files
#  needed by apt.
#
############################################

import sys, os, copy, re

DEBUG = 1
NORM = 0

#######################
#      GLOBALS        #
#######################
BASEDIR  = '/mvista/dev_area/apt-tool-layout/repositories'
TOOLPATH = '/opt/montavista/common/bin'
APTREPO  = None
ARCHLIST = []
DEVAREA  = '/mvista/dev_area/'
USAGE    = "Usage: aptRelease.py <edition> <version> <build tag>\n"  
USAGE   += "<edition> - MontaVista Edition - pro, cge, mobilinux, foundation\n" 
USAGE   += "<version> - Product Version.. i.e. 5.0\n"
USAGE   += "<buildtag> - Build Tag.. i.e. pro060781_1234567\n"
FAIL     = -1
SUCCESS  = 1
MODE    = NORM

#Lesser globals with fancier names#
foundationOuttakes = None
srcOuttakes = None
editionOuttakes = None
hostList = ['common']
#######################



######################
#     FUNCTIONS      # 
######################

def system(command, mode):
	if mode == DEBUG:
		sys.stderr.write('%s\n'%command)
	else:
		sys.stderr.write('%s\n'%command)
		os.system(command)


#I'll make this function stupid now, but it will have to take in a lsit of the packages to copy
def copyFiles(edition, buildtag):
	baseSrc = os.path.join(DEVAREA,edition,buildtag,'build') 
	buildid = re.match(r'.+_(.+)',buildtag).group(1)
	packRegex = re.compile(r'(.+)-\d+.*-.*(\d\d\d\d\d\d\d).*\.mvl')
	srcpackRegex = re.compile(r'(.+)-\d.*\.(.+)\.src\.rpm') #group(1) will be everything prior to the version numbers, group(2) is the buildId


	#Copy SRC RPMS
	#We have to sort src rpms into their respective categories: cross,common,host,target
	#for now we'll do this the simple stupid way, sorting based on the name of the source rpm and checking against our src outtakes list
	if edition == 'foundation':
		srcdest = 'SRPMS.main'
		normdest = 'RPMS.main'
		outtakes = foundationOuttakes
	else:
		srcdest = 'SRPMS.edition'
		normdest = 'RPMS.edition'
		outtakes = editionOuttakes

	sourceList = os.listdir('%s/SRPMS/'%baseSrc)
	for src in sourceList:
		print src
		srcMatch = srcpackRegex.match(src)
		#validate that its our build id and not matching anything in the outtakes
		if buildid == srcMatch.group(2) and srcMatch.group(1) not in srcOuttakes:
			if re.match(r'host-tool',src):
				system('cp -a %s/SRPMS/%s %s/common/%s'%(baseSrc, src, APTREPO, srcdest), MODE)
			elif re.match(r'host',src):
				system('cp -a %s/SRPMS/%s %s/host/%s'%(baseSrc, src, APTREPO, srcdest), MODE) 
			elif re.match(r'cross',src):
				system('cp -a %s/SRPMS/%s %s/cross/%s'%(baseSrc, src, APTREPO, srcdest), MODE) 
			elif re.match(r'common',src):
				system('cp -a %s/SRPMS/%s %s/common/%s'%(baseSrc, src, APTREPO, srcdest), MODE)
			else:  #target
				system('cp -a %s/SRPMS/%s %s/target/%s'%(baseSrc, src, APTREPO, srcdest), MODE)

	


	#Host/Common stuff
	for host in hostList:
		src = os.path.join(baseSrc,'host', host)
		if host == 'common':
			host = 'noarch'
		packList = os.listdir(src)	
		for pack in packList:
			packInfo = packRegex.match(pack)
			if re.match(r'common-.+', pack):
				dest = os.path.join(APTREPO, 'common',host)
			else:
				dest = os.path.join(APTREPO, 'host', host)
			if packInfo and buildid == packInfo.group(2) and packInfo.group(1) not in outtakes:
				system('cp -a %s/%s %s/%s'%(src,pack,dest,normdest), MODE)



	#Get host tools
	src = os.path.join(baseSrc, 'host-tools','solaris8')
	dest = os.path.join(APTREPO, 'common', 'solaris8')
	packList = os.listdir(src)
	for pack in packList:
		packInfo = packRegex.match(pack)
		if packInfo and buildid == packInfo.group(2) and packInfo.group(1) not in outtakes:
			system('cp -a %s/%s %s/%s'%(src, pack, dest, normdest), MODE)


	#CP Target Stuff and cross stuff
	for arch in ARCHLIST:
		#target
		src  = os.path.join(baseSrc, arch,'target')
		dest = os.path.join(APTREPO, 'target', arch)
		#We had issues where using * returned too many things.  We'll have to get a listing another way and execute the commands 1 by 1
		todo = os.listdir(src)
		for pack in todo:
			packInfo = packRegex.match(pack)
			if packInfo and buildid == packInfo.group(2) and packInfo.group(1) not in outtakes:
				system('cp -a %s/%s %s/%s'%(src,pack,dest, normdest), MODE)

		todo = os.listdir('%s/optional'%src)
		for pack in todo:
			packInfo = packRegex.match(pack)
			if buildid == packInfo.group(2) and packInfo.group(1) not in outtakes:
				system('cp %s/optional/%s %s/%s'%(src,pack,dest,normdest), MODE)


		#cross
		src = os.path.join(baseSrc, arch,'cross')
		
		for host in hostList:
			if host == 'common':
				dest = os.path.join(APTREPO,'cross', arch, 'noarch')
			else:
				dest = os.path.join(APTREPO,'cross', arch, host)

			packList = os.listdir(os.path.join(src,host))
			for pack in packList:
				packInfo = packRegex.match(pack)
				if packInfo and buildid == packInfo.group(2) and packInfo.group(1) not in outtakes:
					system('cp -a %s/%s/%s %s/%s'%(src,host,pack,dest,normdest), MODE)	



def genPkgList(edition, version):
	chroot = 'sudo chroot /chroot/redhat90 /bin/su - build -c '
	base = os.path.join(APTREPO,'target')
	for arch in ARCHLIST:
		system('%s "%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --meta=updates %s main edition"'%(chroot, TOOLPATH, edition,version,arch, os.path.join(base,arch)), MODE)
		system('%s "%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --meta=security_updates --partial %s main_s edition_s"'%(chroot, TOOLPATH, edition,version,arch, os.path.join(base,arch)), MODE)
		

	base = os.path.join(APTREPO,'cross')
	for arch in ARCHLIST:
		for host in hostList:
			if host == 'common':
				host = 'noarch'
			system('%s "%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --meta=updates %s main edition"'%(chroot, TOOLPATH, edition,version,host, os.path.join(base,arch,host)), MODE)
			

	base = os.path.join(APTREPO,'common')
	for host in hostList:
		if host == 'common':
			host = 'noarch'
		system('%s "%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --meta=updates %s main edition"'%(chroot,TOOLPATH,edition,version,host, os.path.join(base,host)), MODE)
		

	base = os.path.join(APTREPO,'host')
	for host in hostList:
		if host == 'common':
			host = 'noarch'
		system('%s "%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --meta=updates %s main edition"'%(chroot, TOOLPATH, edition,version,host, os.path.join(base,host)), MODE)




	

#Security stuff, we'll do this later
#	os.system('%s/mvl-genbasedir --partial --meta=Security %s/%s main_s edition_s'%(TOOLPATH, edition, APTREPO, arch))

def setupRepoEnv(edition, version):

	for packType in ('target','host','common','cross'):	
		#SRPMS
		srpms = os.path.join(APTREPO, packType, 'SRPMS.main')
		if edition == 'foundation':
			if not os.path.exists(srpms):
				os.makedirs(srpms)
			else:
				system('rm -rf %s'%srpms,MODE)
				os.makedirs(srpms)
		else:
			if not os.path.exists(srpms):
				os.makedirs(os.path.join(BASEDIR, version, edition, packType,'SRPMS.edition'))
				os.symlink(os.path.join(BASEDIR, version, 'foundation', packType, 'SRPMS.main'),srpms)


		#RPMS
		#Host is not arch specific, neither is common do them outside
	for packType in ('host','common'):
		for host in hostList:
			if host == 'common':
				host = 'noarch'
			main = os.path.join(APTREPO, packType, host, 'RPMS.main')
			try:
				if edition == 'foundation':
					if packType == 'common':
						if not os.path.exists(main):
							os.makedirs(main)
						else:
							system('rm -rf %s'%main, MODE)
							os.makedirs(main)
					elif packType == 'host':
						repoDir = os.path.join(APTREPO, packType, host, 'RPMS.main')
						if not os.path.exists(repoDir):
							os.makedirs(repoDir)
						else:
							system('rm -rf %s'%repoDir)
							os.makedirs(repoDir)

				else:
					if packType == 'common':
						os.makedirs(os.path.join(APTREPO, packType, host, 'RPMS.edition'))
						os.symlink(os.path.join(BASEDIR,version,'foundation', packType, host,'RPMS.main'),main)

					elif packType == 'host':
						repoDir = os.path.join(APTREPO, packType, host, 'RPMS.edition')
						os.makedirs(repoDir)		
						os.symlink(os.path.join(BASEDIR,version,'foundation', packType, host, 'RPMS.main'),main)
			except:
				return FAIL
	


	for arch in ARCHLIST:
		packType = 'target'
		main = os.path.join(APTREPO, packType, arch, 'RPMS.main')
		main_s = os.path.join(APTREPO, packType, arch, 'RPMS.main_s')
		if edition == 'foundation':
			if not os.path.exists(main):
				os.makedirs(main)
			if not os.path.exists(main_s):
				os.makedirs(main_s)
		else:
			repoDir = os.path.join(APTREPO, packType, arch)
			os.makedirs(os.path.join(repoDir,'RPMS.edition'))
			os.symlink(os.path.join(BASEDIR,version,'foundation', packType, arch,'RPMS.main'),main)			

			os.makedirs(os.path.join(repoDir,'RPMS.edition_s'))
			os.symlink(os.path.join(BASEDIR,version,'foundation', packType, arch,'RPMS.main_s'),main_s)			

		packType = 'cross'
		main = os.path.join(APTREPO, packType, 'RPMS.main') 
		for host in hostList:
			if host == 'common':
				host = 'noarch'
			main = os.path.join(APTREPO, packType, arch, host, 'RPMS.main')
			if edition == 'foundation':
				if not os.path.exists(main):
					os.makedirs(main)
				else:
					system('rm -rf %s'%main, MODE)
					os.makedirs(main)

			else:	
				repoDir = os.path.join(APTREPO, packType, arch, host, 'RPMS.edition')
				os.makedirs(repoDir)
				os.symlink(os.path.join(BASEDIR, version, 'foundation', packType, arch, host,'RPMS.main'),main)			

	return SUCCESS


#So we're gonna be a bit tricky here, the easiest thing to do is probably to exec the conf that was used in the actual build
#We'll use that to get the outtakes too.  Since I don't know that the names will remain the same in that file forever, I'd rather
#Have a single function exec the conf file and then deep copy the information to something local
def extractConfig(buildtag, edition):
	global ARCHLIST, foundationOuttakes, srcOuttakes, editionOuttakes, hostList
	#NOTE - Abstract this CVS call or you'll be sorry
	os.chdir('/home/build')
	tmpDir = 'apt_%s'%buildtag
	os.system('cvs -Q -d :ext:rodan:/cvsdev/build_scripts export -r %s -d %s hhl'%(buildtag,tmpDir))
	tmpDir = '/home/build/%s'%tmpDir
	os.chdir(tmpDir)
	#This part here will probably change, we'll end up needing to open all of the config files to extract their relative "outtakes"
	#So, we need a couple things:
	#
	#  1.  What is built in foundation but not in all three editions
	#  2.  Outtakes from an edition (if edition)
	#  3.  SRPM outtakes from edition (if edition)
	#  4.  Arches used
	#
	#  We'll open each of the major data.dat files, extract its outtakes and combine for a "don't copy" list of foundation apps
	proDict = {}
	cgeDict = {}
	mobDict = {}
	founDict = {}
	foundationOuttakes = []
	srcOuttakes = []
	exec(open('pedata.dat'),proDict)
	foundationOuttakes += proDict['outtakes']
	srcOuttakes += proDict['srcouttakes']
	if edition == 'pro':
		editionOuttakes = copy.deepcopy(proDict['outtakes'])
		local_targets = copy.deepcopy(proDict['all_targets'])
		hostList.append(proDict['chroothosts'])
		hostList.append(proDict['hosts'])
		print local_targets

	exec(open('cgedata.dat'),cgeDict)
	foundationOuttakes += cgeDict['outtakes']
	srcOuttakes += cgeDict['srcouttakes']
	if edition == 'cge':
		editionOuttakes = copy.deepcopy(cgeDict['outtakes'])
		local_targets = copy.deepcopy(cgeDict['all_targets'])
		hostList.append(cgeDict['chroothosts'])
		hostList.append(cgeDict['hosts'])

	exec(open('mobilinuxdata.dat'),mobDict)
	foundationOuttakes += mobDict['outtakes']
	srcOuttakes += mobDict['srcouttakes']
	if edition == 'mobilinux':
		editionOuttakes = copy.deepcopy(mobDict['outtakes'])
		local_targets = copy.deepcopy(mobDict['all_targets'])
		hostList.append(mobDict['chroothosts'])
		hostList.append(mobDict['hosts'])

	exec(open('fedata.dat'), founDict)
	foundationOuttakes += founDict['outtakes']
	if edition == 'foundation':
		local_targets = copy.deepcopy(founDict['all_targets'])
		hostList.append(founDict['chroothosts'])
		hostList.append(founDict['hosts'])

	#We need to clean the archlist, all the -o32 and -n64 arches aren't real arches, they are just used by the build engine
	for arch in local_targets:
		if not re.match(r'.+-o32|.+-64|.+-n64|.+-32',arch):
			ARCHLIST.append(arch)
	if MODE == DEBUG:
		print "#Foundation outtakes# "
 		print foundationOuttakes
		print "Source outtakes#"
		print srcOuttakes
	print tmpDir
	os.system('rm -rf %s'%(tmpDir))



def checkArgs(edition, buildtag):
	if edition not in ('foundation','cge','pro','mobilinux'):
		sys.stderr.write('Error: Bad Edition -> %s\n'%edition)
		return FAIL

	if not os.path.exists(os.path.join(DEVAREA,edition,buildtag)):
		sys.stderr.write('Error: Unable to locate build -> %s/%s\n'%(edition,buildtag))
		return FAIL
	return SUCCESS


######################
#   MAIN FUNCTION    #
######################
def releaseProduct(edition, version, buildtag):
	global APTREPO 
	if checkArgs(edition, buildtag) == FAIL:
		raise ValueError, 'Error Occured in Parameter Check, Aborting...'
		
	APTREPO = os.path.join(BASEDIR, version, edition)
	os.system('rm -rf ' + APTREPO)
	extractConfig(buildtag, edition)
	setupRepoEnv(edition, version)
	copyFiles(edition, buildtag)
	genPkgList(edition, version)
	return 


def main(argv):
	if len(argv) != 4:
		sys.stderr.write(USAGE)
		sys.exit(1)
	releaseProduct(argv[1],argv[2],argv[3])


if __name__ == "__main__":
	main(sys.argv)
	sys.exit(1)



