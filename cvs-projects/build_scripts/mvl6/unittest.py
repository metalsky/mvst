#!/usr/bin/env python
import sys,os, commands

def installersDiffer(node, installer_a, installer_b):
	'''Return true if the installers are different, False if they are identical'''

	installers = [installer_a, installer_b]
	x = 1
	estr = ''

	for installer in installers:
#		os.system('scp %s %s:/tmp/inst%s' % (installer, node, x))
#		os.system('ssh %s "mkdir /tmp/%s"' % (node, x))
#		os.system('ssh %s "/tmp/inst%s --mode silent --prefix /tmp/%s"' % (node, x, x))
		x += 1

	diffText =  commands.getoutput('ssh %s "diff -urp /tmp/1 /tmp/2 -x *-uninstall*"' % node)

	if diffText == estr:
		print 'False'
		return False
	else:
		print 'True'
		return True
		

if sys.argv[1] == 'instdiff':
	installersDiffer('node-1', \
					 '/mvista/dev_area/integration_platform/toolchain_090911_0903018/build/installers/MVL-Toolchain-arm-gnueabi-4.3.0-Linux-x86-Install', \
				     '/mvista/dev_area/integration_platform/toolchain_090911_0903016/build/installers/MVL-Toolchain-arm-gnueabi-4.3.0-Linux-x86-Install')
	

if sys.argv[1] == 'ipsource':
	import IPSource
	myip = IPSource.IPSource()
	fetchWorked = myip.Fetch()
	print "fetch done, returned %s" % fetchWorked
	myip.Install()

elif sys.argv[1] == 'buildlog':
	import parser
	myparser = parser.parser('/home/rell/buildlog-2.log')
	myparser.outputHTML('testbuild0000000')

elif sys.argv[1] == 'bashrc':
	import commands
	if not commands.getstatusoutput('sudo cp ./build_bashrc.sh /chroot/centos3/home/build')[0]:
		print 'copied succesfully'

elif sys.argv[1] == 'ib':
	BuildLink = 'latest_build_arm-versatile-1176-2.6.28'
	BuildTag = 'arm-versatile-1176-2.6.28_111_111'
		
	print 'os makedirs: /chroot/centos4/home/build/latest_prebuilt'
	prebuiltArchDirs = []
	lastPrebuiltsDir = os.path.join('/mvista/dev_area/mvl6/', BuildLink, 'content/prebuilt', BuildTag.split('_')[0])
	print 'latestprebuilts: %s' % lastPrebuiltsDir
	print lastPrebuiltsDir
	for file in os.listdir(lastPrebuiltsDir):
		testPath = os.path.join(lastPrebuiltsDir, file)
		if os.path.isdir(testPath) and file not in ['conf', 'pstage']:
			print 'cp %s /chroot/centos4/home/build/' % testPath
			print prebuiltArchDirs
			prebuiltArchDirs.append(file)
		

	
