#!/usr/bin/env python
import sys, os, commands, cPickle
sys.path.append('./resourceManager')
import resourceManager
import buildConfig
import contentServer
import genContentHtml
import buildEmail
from runCmd import run, crun
import parser

buildtag = sys.argv[1]
starttag = sys.argv[2]
buildid  = sys.argv[3]
distro   = sys.argv[4]
msd      = sys.argv[5]


bcfg = buildConfig.buildConfig(msd)

#Should this go in the config?
buildLink = 'latest_build' + '_' + msd + '-' + bcfg.KernelVersion
bcfg.BuildID = buildid
bcfg.BuildLink = buildLink
splitBuildtag = buildtag.split('_', 1)
splitBuildtag[0] = splitBuildtag[0] + '-%s' % bcfg.KernelVersion
destBuildtag = splitBuildtag[0] + '_' + splitBuildtag[1]
bcfg.BuildTag = destBuildtag

#Figure out the Kernel filename/version
if bcfg.BuildType == 'staging':
	fp = open('/mvista/dev_area/mvl6/latest_collection/%s-fname' % msd)
	kernelFilename = fp.readline().strip()
	bcfg.KernelFilepath = '/mvista/dev_area/mvl6/latest_collection'
	bcfg.KernelFilename = kernelFilename
	fp.close()
elif bcfg.BuildType == 'release':
	fqfile = bcfg.getRequestedVersions()[msd]
	bcfg.KernelFilepath = os.path.split(fqfile)[0]
	bcfg.KernelFilename = os.path.split(fqfile)[1]


pickleFile = open('/home/build/%s-exp/CVSREPOS/build_scripts/mvl6/cfg.cpickle' % buildtag, 'w')
cPickle.dump(bcfg, pickleFile)
pickleFile.close()




node = resourceManager.getResource(buildtag,buildid,'node-64','Mvl6 msd: %s' % msd)
print 'Checked out resource: %s' % node

print 'Setting up chroot environment'
run('''ssh %s "/home/build/%s-exp/CVSREPOS/build_scripts/mvl6/setupChroot.py %s"''' % (node, buildtag, buildtag))



print 'kicking off build %s' % buildtag
run('''ssh %s "/home/build/%s-exp/CVSREPOS/build_scripts/mvl6/kickbuild.py %s %s"''' % (node, buildtag, bcfg.LaunchCommand, buildtag))

print 'Moving DB File to Dev Area'
run('''mkdir /mvista/dev_area/mvl6/%s''' % buildtag)
run('''ssh %s "cp /chroot/centos4/home/build/mvl6-alpha/build/mvl6-alpha-build/mvpkg.db /mvista/dev_area/mvl6/%s/mvpkg.db"''' % (node,buildtag), printOutput=False)
run('''ssh %s "cp /chroot/centos4/home/build/mvl6-alpha/build/mvl6-alpha-build/mvlpkg.db /mvista/dev_area/mvl6/%s/mvlpkg.db"''' % (node,buildtag), printOutput=False)
run('''ssh %s "cp /chroot/centos4_64/home/build/mvl6-alpha/build/mvl6-alpha-build/mvpkg.db /mvista/dev_area/mvl6/%s/mvpkg-64.db"''' % (node,buildtag), printOutput=False)
run('''ssh %s "cp /chroot/centos4_64/home/build/mvl6-alpha/build/mvl6-alpha-build/mvlpkg.db /mvista/dev_area/mvl6/%s/mvlpkg-64.db"''' % (node,buildtag), printOutput=False)
#run('''ssh %s "mv /chroot/centos4/home/build/mvl6-alpha /mvista/dev_area/mvl6/%s"''' % (node,buildtag), printOutput=False)
#run('''ssh %s "mv /chroot/centos4_64/home/build/mvl6-alpha /mvista/dev_area/mvl6/%s/build64"''' % (node,buildtag), printOutput=False)

print 'Copying opt'
run('''ssh %s "cp /chroot/centos4/opt/montavista /mvista/dev_area/mvl6/%s/montavista -R"''' % (node, buildtag))

print 'Moving pstage dir'
run('''ssh %s "mv /chroot/centos4/home/build/pstage /mvista/dev_area/mvl6/%s/pstage"''' % (node,buildtag))
run('''ssh %s "mv /chroot/centos4_64/home/build/pstage /mvista/dev_area/mvl6/%s/pstage64"''' % (node,buildtag))

print 'Moving sources dir'
run('''ssh %s "mv /chroot/centos4/home/build/sources /mvista/dev_area/mvl6/%s/sources"''' % (node,buildtag))

print 'Moving prebuilt dir'
run('''ssh %s "mv /chroot/centos4/home/build/prebuilt /mvista/dev_area/mvl6/%s/prebuilt"''' % (node,buildtag))
run('''ssh %s "mv /chroot/centos4_64/home/build/prebuilt /mvista/dev_area/mvl6/%s/prebuilt64"''' % (node,buildtag))

print 'Moving logfile'
run('''ssh %s "mv /tmp/*.log /mvista/dev_area/mvl6/%s/"''' % (node, buildtag))

print 'Making link to latest_build'
os.chdir('/mvista/dev_area/mvl6/')
os.system('rm -f %s' % buildLink)
os.system('ln -s %s %s' % (destBuildtag, buildLink))

print 'Cleaning up node %s' % node
for chroot in ['centos4', 'centos4_64']:
	run('''ssh %s "rm -rf /chroot/%s/home/build/*"''' % (node, chroot))
	run('''ssh %s "rm -rf /chroot/%s/opt/montavista/*"''' % (node, chroot))

print 'Releasing node: %s' % node
resourceManager.releaseResource(node)

print 'Renaming build to include Kernel Version'
run('mv /mvista/dev_area/mvl6/%s /mvista/dev_area/mvl6/%s' % (buildtag, destBuildtag))


print 'Updating Content'
mycs = contentServer.contentServer(bcfg)
mycs.run()

print 'Generating content.html'
genContentHtml.generate(['/mvista/dev_area/mvl6/%s' % destBuildtag], '/mvista/dev_area/mvl6/%s/content.html' % destBuildtag)

try:
	print 'Attempting to generate top level content.html'
	os.chdir('/mvista/dev_area/mvl6/')
	buildlist = commands.getoutput('ls |grep latest|grep -v collection').split('\n')
	genContentHtml.generate(buildlist, '/mvista/dev_area/mvl6/content.html')
	print 'Succeeded.'
except:
	print 'Failed.'

print 'Generating Collective pages'
if os.path.exists('/mvista/dev_area/mvl6/%s' % destBuildtag):
	collective = parser.parser('/mvista/dev_area/mvl6/%s' % destBuildtag)
	collective.outputHTML('/export/logs',destBuildtag)
	collective.updateSummarySHTML('/export/logs',destBuildtag)
else:
	print 'No exist: /mvista/dev_area/mvl6/%s' % destBuildtag


run('cp %s /mvista/dev_area/mvl6/%s/%s.ip' % (bcfg.IP_VER, destBuildtag, destBuildtag))
run('cp %s /mvista/dev_area/mvl6/%s/%s.toolchain' % (bcfg.TOOLCHAIN_VER, destBuildtag, destBuildtag))


print 'Running ferret trigger'
os.system('ssh ferret -l ferret bin/kickit qalx/buildtrigger %s' % destBuildtag)

print 'Sending email'
be = buildEmail.buildEmail(bcfg)
be.sendEmail()
