#!/usr/bin/env python
import commands, sys, os, time
import cPickle
#Fetch Integration Platform and install.
import IPSource
from runCmd import run, crun

buildtag = sys.argv[1]
print 'Fetching MVL Git Repos...'
run('sudo mkdir /chroot/centos4/opt/montavista/content -p')
run('sudo rm -rf /tmp/*')
run('sudo rm -rf /chroot/centos4_64/opt/montavista/*')
run('sudo rm -rf /chroot/centos4/home/build/.mvl-content')
run('sudo rm -rf /chroot/centos4_64/home/build/.mvl-content')
run('sudo chown build:engr /chroot/centos4/opt/montavista')
run('sudo chown build:engr /chroot/centos4/opt/montavista/content')


cfgFile = open('/home/build/%s-exp/CVSREPOS/build_scripts/mvl6/cfg.cpickle' % buildtag, 'r')
bcfg = cPickle.load(cfgFile)
cfgFile.close()
repos = bcfg.CollectionRepos
print 'The following repos are associated with msd %s:' % bcfg.getMSDName()
print repos

print 'Fetching and installing IP and Install Image'
buildSources = IPSource.IPSource(bcfg)
buildSources.Fetch()
buildSources.Install()

try:
	if bcfg.IsIncremental:
		os.makedirs('/chroot/centos4/home/build/latest_prebuilt')
		prebuiltArchDirs = []
		lastPrebuiltsDir = os.path.join('/mvista/dev_area/mvl6/', bcfg.BuildLink, 'content/prebuilt', bcfg.BuildTag.split('_')[0])
		for file in os.listdir(lastPrebuiltsDir):
			testPath = os.path.join(lastPrebuiltsDir, file)
			if os.path.isdir(testPath) and file not in ['conf', 'pstage']:
				os.system('cp %s /chroot/centos4/home/build/latest_prebuilt/ -R' % testPath)
				prebuiltArchDirs.append(file)
except:
	print 'Exception raised.  Turning incremental build off.'
	bcfg.IsIncremental = False

		
#Nuke anything in the content dir since we are pulling from git.
run('rm -rf /chroot/centos4/opt/montavista/content/*')
#Make sources dir
os.makedirs('/chroot/centos4/home/build/sources/collection')
#Clean tmp
run('rm -rf /tmp/*')

#Do the cloning
if bcfg.BuildType == 'staging':
	for repoName in repos:
		#Collection
		fp = open('/mvista/dev_area/mvl6/latest_collection/%s-ver' % repoName)
		ver = fp.readline().strip()
		fp.close()
		tarFile = repoName + '-' + ver + '.tar.bz2'
		run('cp /mvista/dev_area/mvl6/latest_collection/%s /chroot/centos4/home/build/' % tarFile)
		run('cp /mvista/dev_area/mvl6/latest_collection/%s /chroot/centos4/home/build/ -R' % repoName)
		run('cp /mvista/dev_area/mvl6/latest_collection/%s-ver /chroot/centos4/home/build/' % repoName)
		#Sources
		if repoName not in ['kernel', 'toolchain']:
			crun('/opt/montavista/bin/git clone git://git.sh.mvista.com/mvl6/%s-sources.git ./sources/collection/%s' % (repoName, repoName))
	
		run('cp /chroot/centos4/home/build/%s* /chroot/centos4/opt/montavista/content/ -R' % repoName)
		run('rm -rf /chroot/centos4/home/build/%s' % repoName)


	run('cp /mvista/dev_area/mvl6/latest_collection/%s /chroot/centos4/opt/montavista/content/' % bcfg.KernelFilename, DBG=True)
	run('tar jxf /chroot/centos4/opt/montavista/content/%s -C /chroot/centos4/opt/montavista/content' % bcfg.KernelFilename)
	run('mv /chroot/centos4/opt/montavista/content/%s /chroot/centos4/opt/montavista/content/kernel' % bcfg.getMSDName())

elif bcfg.BuildType == 'release':
	versionDict = bcfg.getRequestedVersions()
	for repoName in repos:
		file = versionDict[repoName]
		dir = os.path.split(file)[0]
		run('cp %s /chroot/centos4/home/build/' % file)
		run('cp %s/%s /chroot/centos4/home/build/ -R' % (dir, repoName))
		run('cp %s/%s-ver /chroot/centos4/home/build/' % (dir, repoName))
	
		if repoName not in ['kernel', 'toolchain']:
			crun('/opt/montavista/bin/git clone git://git.sh.mvista.com/mvl6/%s-sources.git ./sources/collection/%s' % (repoName, repoName))

		run('cp /chroot/centos4/home/build/%s* /chroot/centos4/opt/montavista/content/ -R' % repoName)
		run('rm -rf /chroot/centos4/home/build/%s' % repoName)

	#Kernels
	run('cp %s /chroot/centos4/opt/montavista/content/' % os.path.join(bcfg.KernelFilepath, bcfg.KernelFilename))
	run('tar jxf /chroot/centos4/opt/montavista/content/%s -C /chroot/centos4/opt/montavista/content' % bcfg.KernelFilename)
	run('mv /chroot/centos4/opt/montavista/content/%s /chroot/centos4/opt/montavista/content/kernel' % bcfg.getMSDName())


		




run('''cp /home/build/%s-exp/CVSREPOS/build_scripts/mvl6/build_bashrc /chroot/centos4/home/build/.bashrc''' % buildtag )
run('''cp /home/build/%s-exp/CVSREPOS/build_scripts/mvl6/local.conf /chroot/centos4/opt/montavista/content/foundation/conf/local.conf''' % buildtag)

#Add commands
fp = open('/chroot/centos4/opt/montavista/content/foundation/conf/local.conf', 'a')
#fp.write('MVL6_BUILDID = "%s"\n' % bcfg.BuildID)
fp.write('PSTAGE_PKG = "${TOPDIR}/prebuilt/${HOST_SYS}/${PSTAGE_PKGNAME}"\n')
fp.write('DL_DIR = "${TOPDIR}/sources/${@get_contentpath(d)}"\n')
fp.write('CFGSIGDATAFILE ?= "${DEPLOY_DIR_PSTAGE}/cfgsigs/${PN}-${PV}-${PR}-${CFGSIGNATURE}"\n')
fp.write('TOPDIR = "/home/build"\n')
fp.write('PACKAGEDB_PREPROCESS = "True"\n')
fp.write('PACKAGEDB_BUILD = "True"\n')

if bcfg.IsIncremental:
	for arch in prebuiltArchDirs:
		fp.write('PSTAGE_PKGPATHS += "file:///home/build/latest_prebuilt/%s/${PSTAGE_PKGNAME}"\n' % arch)

fp.write('PSTAGE_PKGPATHS += "file:///home/build/latest_prebuilt/${PSTAGE_PKGNAME}"\n')
fp.close()

#Disable Licence Management
run('for each in `/bin/ls /chroot/centos4/opt/montavista/tools/*/libexec/gcc/*/*/mvl-license`; do rm $each; ln -s /bin/true $each; done')
run('rm /chroot/centos4/opt/montavista/bin/bblicense; echo -e "#\!/bin/bash\necho \"valid\"\nsleep 30" > /chroot/centos4/opt/montavista/bin/bblicense ; chmod 755 /chroot/centos4/opt/montavista/bin/bblicense')

#Setup 64-bit Stuff
print 'Setting up 64 bit chroot'
run('sudo mkdir /chroot/centos4_64/opt/montavista/content -p')
run('sudo chown build:engr /chroot/centos4_64/opt/montavista')
run('sudo chown build:engr /chroot/centos4_64/opt/montavista/content')
run('cp /chroot/centos4/opt/montavista/* /chroot/centos4_64/opt/montavista/ -R')
run('cp /chroot/centos4/home/build/* /chroot/centos4_64/home/build/ -R')
run('cp /chroot/centos4/home/build/.bashrc /chroot/centos4_64/home/build/')


#fp = open('/chroot/centos4_64/opt/montavista/content/foundation/conf/local.conf', 'a')
#fp.write('BUILD_ARCH = "${@os.uname()[4]}"\n')
#fp.write('BUILD_CC_ARCH = ""\n')
#fp.close()

