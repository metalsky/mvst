#!/usr/bin/python
import sys
sys.path.append('./resourceManager')
sys.path.append('/home/build/bin/utils')
from resourceManager import *
from buildFunctions import *
from datetime import datetime
import os, commands, re

# launch.py passes in buildtag (ipmvl6_YYMMDD_09xxxxx) and starttag, for changelog
# get git resource
# clone/checkout/tag git repo, capture log
# release git resource
# get node resource
# copy source to chroot on node
# give make all chroot command, capture log
# do toolchain linking, capture log
# do make clean, capture log
# release node resource
# copy tars to dev_area

if len(sys.argv) != 3:
  printflush('\nusage: %s %s %s' % (sys.argv[0],'<buildtag>','<starttag>'))
  printflush('\n# of args = ' + str(len(sys.argv)))
  printflush('\nHere are the args:')
  for x in sys.argv:
    printflush(x)
  sys.exit(1)

def getArch(tcFile):
	#This needs to match versioned and nonversioned files, hence the separate function
	str_RE = re.compile(r'MVL-Toolchain-(.*)-\d.*')
	arch = str_RE.match(tcFile).group(1)
	return arch

def getVer(tcFile):
	#should work on old and new filenames
	str_RE = re.compile(r'MVL-Toolchain-.*?-(\d.*?\d)-.*')
	ver = str_RE.match(tcFile).group(1)
	return ver
	

def getCsid(tcFile):
	'''Requires a full path to tcFile'''
	return commands.getoutput("%s --version|sed 's/^.*\.//'|sed 's/)//'" % tcFile).split('\n')[0]

def getToolchainVersions(dir):
	'''Given an installer directory, make a dictionary.  Keys are archs, values are tuples (version, revision).'''
	retDict = {}
	ARCH, VER, CSID, REV = 1,2,3,4
	file_RE = re.compile(r'MVL-Toolchain-(.*)-([\d\.]+\d)-(\d+)-(\d{10})-.*')
	for file in os.listdir(dir):
		matchObj = file_RE.match(file)
		if matchObj:
			retDict[matchObj.group(ARCH)] = (matchObj.group(VER), matchObj.group(CSID), matchObj.group(REV))

	return retDict

def rcToolchain(arch, ver, csid, rev):
	return 'MVL-Toolchain-%s-%s-%s-%s-Linux-x86-Install' % (arch, ver, csid, rev)

def checkChanges(dir):
	'''Check to see if the repo has changed.  Return True if it has, False if not.'''
	unchanged = ''
	currentDir = os.getcwd()
	os.chdir(dir)
	newestTag = commands.getoutput('git tag -l | grep build/ipmvl6 | tail -n1')
	isChanged = commands.getoutput('git log %s..HEAD' % newestTag)
	os.chdir(currentDir)
	if isChanged == unchanged:
		return False
	return True


def installersDiffer(node, installer_a, installer_b):
	'''Return true if the installers are different, False if they are identical'''

	if not os.path.exists(installer_a) or not os.path.exists(installer_b):
		return True

	installers = [installer_a, installer_b]
	x = 1
	estr = ''
	cleancmd = 'ssh %s "rm -rf /tmp/*"' % node
	os.system(cleancmd)
	
	for installer in installers:
		os.system('scp %s %s:/tmp/inst%s' % (installer, node, x))
		os.system('ssh %s "mkdir /tmp/%s"' % (node, x))
		os.system('ssh %s "/tmp/inst%s --mode silent --prefix /tmp/%s"' % (node, x, x))
		x += 1

	diffText =  commands.getoutput('''ssh %s "diff -urp /tmp/1 /tmp/2 -x *-uninstall* | grep -e recursive\ directory\ loop"''' % node)
	print diffText
	os.system(cleancmd)

	if diffText == estr:
		return False
	else:
		return True
	
def mstart(app,log='',scripttest=0):
  startmsg = '<' + sys.argv[0] + '>: building ' + app + ' at ' + gettime() + '...'
  if scripttest == 1:
    printflush(startmsg)
  elif log:
    printflush(startmsg,log,noprint=1)
  else:
    printflush(startmsg)

def mstop(app,log='',scripttest=0):
  stopmsg = '<' + sys.argv[0] + '>: finished ' + app + ' at ' + gettime() + '...'
  if scripttest == 1:
    printflush(stopmsg)
  elif log:
    printflush(stopmsg,log,noprint=1)
  else:
    printflush(stopmsg)

def genCollectivePages():
  header = '<!--#include virtual="/include/header.inc" -->\n'
  footer = '<!--#include virtual="/include/footer.inc" -->\n'
  intro = '<h1>These are the build logs for the %s  build.</h1>\n' % buildtag
  intro = intro + '<br><h4>previous tag = %s</h4><br>\n' % starttag
  prepurl = '<Font size=+2><a href=/logs/%s/buildip-%s.log>prep</a></font><br>\n' % (buildtag,buildid)
  srcurl = '<Font size=+2><a href=/logs/%s/ipsrc-%s.log>source</a></font><br>\n' % (buildtag,buildid)
  buildurl = '<Font size=+2><a href=/logs/%s/ipbuild-%s.log>build</a></font><br>\n' % (buildtag,buildid)
  builddirurl = '<Font size=+2><a href=/dev_area/integration_platform/%s/build>build dir</a></font>' % buildtag
  os.system('mkdir /export/logs/%s' % buildtag)
  f_build = open('/export/logs/%s/build.shtml' % buildtag, 'w')
  f_build.write(header)
  f_build.write(intro)
  f_build.write(prepurl)
  f_build.write(srcurl)
  f_build.write(buildurl)
  f_build.write(builddirurl)
  f_build.write(footer)
  f_build.close()
  os.system('cp %s /export/logs/%s' % (ippreplog,buildtag))
  os.system('cp %s /export/logs/%s' % (ipsrclog,buildtag))
  os.system('cp %s /export/logs/%s' % (ipbuildlog,buildtag))

def genCollective():
  os.chdir(builddir)
  os.system("./GenCollective %s %s %s" % (buildtag,"/export/logs",changelog))

buildtag = sys.argv[1]
starttag = sys.argv[2]

host = 'centos4'
#host = 'centos5'
#host = 'centos3'

versionstring = datetime.now().strftime("%y%m%d%H%M")


buildid = buildtag.split('_')[-1:][0]
homepath = '/home/build/%s-exp/CVSREPOS' % buildtag
builddir = os.getcwd()

#toolchaindir = '/mvista/dev_area/integration_platform/toolchains/current'
cpdir = '/mvista/dev_area/integration_platform/%s/build' % buildtag
logdir = '/mvista/dev_area/integration_platform/%s/logs' % buildtag
ippreplog = '%s/buildip-%s.log' % (logdir,buildid)
ipsrclog = '%s/ipsrc-%s.log' % (logdir,buildid)
ipbuildlog = '%s/ipbuild-%s.log' % (logdir,buildid)
systemCmd('mkdir -p %s %s' % (cpdir,logdir))
systemCmd('touch %s' % ippreplog)

# email build_status
greet = 'Starting buildip.py on ' + os.popen('uname -n').read().strip() + ' at ' + gettime()
os.system('echo "' + greet + '" | /usr/bin/Mail -s "Build starting for Int. Platform" build_status@mvista.com')
printflush("Starting %s at %s" % (sys.argv[0],gettime()),ippreplog,noprint=1)
mstart('%s-setup' % sys.argv[0],ippreplog)

printflush('buildtag = %s' % buildtag,ippreplog,noprint=1)
printflush('starttag = %s' % starttag,ippreplog,noprint=1)
printflush('buildid = %s' % buildid,ippreplog,noprint=1)
printflush('cpdir = %s' % cpdir,ippreplog,noprint=1)
printflush('logdir = %s' % logdir,ippreplog,noprint=1)

srcpath = homepath+'/integration-platform-build'
srcrepo = 'mvl6/integration-platform-build'
srcdir = 'integration-platform-build'
srcbranch = 'dev'
branchtype = 'branch'
tooldir = '/mvista/dev_area/integration_platform/toolchains/codesourcery/current/binary/merged'
if not os.path.exists(tooldir):
  tooldir = '/mvista/dev_area/integration_platform/toolchains/codesourcery/current/binary'
manifest = '/mvista/dev_area/integration_platform/toolchains/codesourcery/current/manifest'
printflush('toolchains copied from %s' % tooldir,ippreplog,noprint=1)

mstop('%s-setup' % sys.argv[0],ippreplog)

mstart('integration-platform-src',ipsrclog)
brmRepo = getResource(buildtag,buildid,'git_ip',"Clone and Tag")
printflush('Sucessfully checked out git_ip for ' + srcrepo + ' repository at ' + gettime() + '...',ipsrclog,noprint=1)
printflush('Cloning, check out and tagging ' + buildtag + ' in ' + srcrepo + ' repository at ' + gettime() + '...',ipsrclog,noprint=1)
os.chdir(homepath)
f_ipsrclog = open(ipsrclog,'a')
s_log = os.popen('%sclone %s/%s 2>&1' % (gitcmd,gitroot,srcrepo)).read()

repoChanged = checkChanges(os.path.join(homepath, 'integration-platform-build'))
doToolchain = 'toolchain' in buildtag
doIP		= 'ipmvl6' in buildtag

'Should not be possible, but lets catch it anyway'
if ( doToolchain and doIP ) or ( not doToolchain and not doIP ):
	doIP = True
	doToolchain = False
	printflush('problem with buildtag.  defaulting to IP build')


#FIXME: DEBUG
repoChanged = True
if repoChanged:

	f_ipsrclog.write(s_log)
	#os.system('%scheckout origin/%s >> %s 2>&1 < /dev/null' % (gitcmd,srcbranch,log))
	os.chdir(srcpath)
	s_log = os.popen('%stag -a -f -m "Build System Tag" build/%s 2>&1' % (gitcmd,buildtag)).read()
	f_ipsrclog.write(s_log)
	s_log = os.popen('%spush --tags 2>&1' % gitcmd).read()
	f_ipsrclog.write(s_log)
	f_ipsrclog.close()

	printflush('making changelog for ' + srcrepo + ' at ' + gettime() + '...',ipsrclog,noprint=1)
	changelog = '%s/ip-%s-%s-Changelog' % (logdir,starttag,buildtag)
	#sourceControlChangelog('git','git_ip',starttag,buildtag,srcrepos,changelog,log,0)
	os.system('%slog --pretty=full build/%s..build/%s >> %s 2>&1' % (gitcmd,starttag,buildtag,changelog))
	releaseResource(brmRepo)
	mstop('integration-platform-src',ipsrclog)

	mstart('integration-platform',ipbuildlog)
	node = getResource(buildtag,buildid,'node','Integration-Platform Build')
	printflush('Got node %s' % node)
	printflush('Using %s to build' % node,ipbuildlog,noprint=1)
	# setup centos3 env
	if host == 'centos3':
	  os.system('sudo ssh %s "cp /chroot/centos3/etc/nsswitch.conf /chroot/centos3/etc/nsswitch.buildtmp" >> %s 2>&1 < /dev/null' % (node,ipbuildlog))
	  os.system('sudo ssh %s "echo \\"search sh.mvista.com\\" > /chroot/centos3/etc/resolve.conf" >> %s 2>&1 < /dev/null' % (node,ipbuildlog)) 
	  os.system('sudo ssh %s "echo \\"nameserver 10.40.0.2\\" >> /chroot/centos3/etc/resolve.conf" >> %s 2>&1 < /dev/null' % (node,ipbuildlog)) 
	  os.system('sudo ssh %s "echo \\"hosts:	files dns\\" >> /chroot/centos3/etc/nsswitch.conf" >> %s 2>&1 < /dev/null' % (node,ipbuildlog)) 
	
	os.system('scp -r %s/integration-platform-build %s:/chroot/%s/home/build >> %s 2>&1' % (homepath,node,host,ipbuildlog))
	# copy toolchians to be included in installer
	os.system('ssh %s "mkdir -p /chroot/%s/home/build/integration-platform-build/BUILD/toolchains"' % (node,host))
	os.system('scp -r %s/* %s:/chroot/%s/home/build/integration-platform-build/BUILD/toolchains >> %s 2>&1' % (tooldir,node,host,ipbuildlog))
	os.system('scp -r %s %s:/chroot/%s/home/build/integration-platform-build/BUILD/toolchains >> %s 2>&1' % (manifest,node,host,ipbuildlog))

	if starttag != 'skip':
	  os.system('ssh %s "sudo chroot /chroot/%s /bin/su - build -c \\"cd /home/build/integration-platform-build; make -C /home/build/integration-platform-build CURRENT_TAG=%s all\\"" >> %s 2>&1 < /dev/null' % (node,host,buildtag,ipbuildlog))
	else:
	  os.system('ssh %s "sudo chroot /chroot/%s /bin/su - build -c \\"cd /home/build/integration-platform-build; make -C /home/build/integration-platform-build PREVIOUS_TAG=%s CURRENT_TAG=%s all\\"" >> %s 2>&1 < /dev/null' % (node,host,starttag,buildtag,ipbuildlog))

	changedToolchains = []
	#IP Tarball
	#Toolchain Installers
	if doToolchain:
		os.system('rsync -rz --exclude=MVL-Integration-Platform-1.0.0-Linux-x86-Install %s:/chroot/%s/home/build/integration-platform-build/installers %s >> %s 2>&1' % (node,host,cpdir,ipbuildlog))
		oldtc = '/mvista/dev_area/integration_platform/latest_toolchain'
		oldToolchains = getToolchainVersions(os.path.join(oldtc, 'build/installers'))
		print 'oldToolchains:'
		print oldToolchains

		for installer in os.listdir(os.path.join(cpdir, 'installers')):
			VER, CSID, REV = 0,1,2
			arch = getArch(installer)
			ver = getVer(installer)
			csid = getCsid(os.path.join(cpdir, 'installers', installer))
			print 'getArch returned: %s' % arch
			print 'getVer returned: %s' % ver
			print 'getCsid returned: %s' % csid
			oldTcFilename = rcToolchain(arch, oldToolchains[arch][VER], oldToolchains[arch][CSID], oldToolchains[arch][REV])



			printflush('comparing installers: %s and %s' % (os.path.join(cpdir, 'installers', installer), os.path.join(oldtc, 'build/installers', oldTcFilename)))
			diff = installersDiffer(node, os.path.join(cpdir, 'installers', installer), os.path.join(oldtc, 'build/installers', oldTcFilename))

			if diff:
				os.system('mv %s/installers/%s %s/installers/%s' % (cpdir, installer, cpdir, rcToolchain(arch, ver, csid, versionstring)))
				changedToolchains.append(installer)
			else:
				os.system('mv %s/installers/%s %s/installers/%s' % (cpdir, installer, cpdir, rcToolchain(arch, ver, csid, oldToolchains[arch][REV])))
				


	elif doIP:
		os.system('scp -r %s:/chroot/%s/home/build/integration-platform-build/images/* %s >> %s 2>&1' % (node,host,cpdir,ipbuildlog))
		os.system('mkdir %s/installers' % cpdir)
		os.system('scp %s:/chroot/%s/home/build/integration-platform-build/installers/MVL-Integration-Platform-1.0.0-Linux-x86-Install %s/installers/MVL-Integration-Platform-%s-Linux-x86-Install >> %s 2>&1' \
				  % (node,host,cpdir,versionstring,ipbuildlog))
	else:
		printflush('debug: We shouldnt be here.')


	os.chdir(cpdir)
	#os.system('ln %s/* .' % toolchaindir)
#	os.system('ssh %s "rm -rf /chroot/%s/home/build/integration-platform-build"' % (node,host))
#	releaseResource(node)
else:
	releaseResource(brmRepo)
	printflush('No changes detected.  Halting Build.')

#if host == 'centos3':
#  os.system('sudo ssh %s "rm -f /chroot/centos3/etc/nsswitch.conf /chroot/centos3/etc/resolve.conf" >> %s 2>&1 < /dev/null' % (node,log))
#  os.system('sudo ssh %s "mv /chroot/centos3/etc/nsswitch.buildtmp /chroot/centos3/etc/nsswitch.conf" >> %s 2>&1 < /dev/null' % (node,log))
mstop('integration-platform',ipbuildlog)

# if no installers dir, build failed
#if os.path.exists(cpdir + '/installers'):
if doToolchain:
	#os.system('cd /mvista/dev_area/integration_platform; rm -f latest_toolchain; ln -s %s latest_toolchain' % buildtag)
	printflush('changed tcs: %s\n' % changedToolchains)
elif doIP:
	os.system('cd /mvista/dev_area/integration_platform; rm -f latest_ip; ln -s %s latest_ip' % buildtag)

if repoChanged:
	genCollective()
#	os.system('ssh ferret -l ferret bin/kickit qalx/buildtrigger %s' % buildtag)
else:
	os.chdir('/mvista/dev_area/integration_platform')
	f_ipsrclog.close()
	printflush('rm -rf %s' %buildtag)
	os.system('sudo rm -rf %s' % buildtag)


fini = 'Finished buildip.py on ' + os.popen('uname -n').read().strip() + ' at ' + gettime()
os.system('echo "' + fini + '" | /usr/bin/Mail -s "Build finished for Int. Platform" build_status@mvista.com')

