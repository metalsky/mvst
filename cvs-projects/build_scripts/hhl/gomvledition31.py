#!/usr/bin/python
import os, sys, re, string, time

# this script creates an updated application package for cge3.1
# it cleans /opt/montavista/devkit, /opt/montavista/common, /opt/montavista/config
# it updates host-rpm & host-popt to the 3.1 shipped version
# installs the tools & kernel
# creates tag & buildid & checks in to taglist file
# applies a tag to userland repository
# exports userland app repositories
# builds the applications for {app}
# copies the src.rpm and mvls to /mvista/dev_area/<edition>/mvlcge310-updates/<app-bugid>

# args:
# 1- edition (product)
# 2- reltag
# 4- app name (i.e. XFree86.cge)
# 5- type (i.e. target, cross, noarch)
# 6- bugid
# 7- buildid
# 8- tag
# 9- builddir
# 10- copydir
# 11- logdir
# 12- ubranch 


def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

def mstart(app):
  print '<' + sys.argv[0] + '>: building ' + app + ' at ' + gettime() + '...'
  sys.__stdout__.flush()
                                                                                                                   
def mstop(app):
  print '<' + sys.argv[0] + '>: finished ' + app + ' at ' + gettime() + '...'
  sys.__stdout__.flush()

if str(len(sys.argv)) not in ("13",):
  print "\nUsage: %s <edition> <edition release tag> <app name> <type> <bugid> <buildid> <tag> <builddir> <cpdir> <logdir> <ubranch> <clean|noclean>" % (sys.argv[0])
  sys.exit(1)

edition = sys.argv[1]
print "edition = " + edition
reltag = sys.argv[2]
print "reltag = " + reltag
app = sys.argv[3]
print "appname = " + app
type = sys.argv[4]
print "application type = " + type
bugid = sys.argv[5]
print "bugid = " + bugid
buildid = sys.argv[6]
print "buildid = " + buildid
tag = sys.argv[7]
print "tag = " + tag
builddir = sys.argv[8]
print "builddir = " + builddir
cpdir = sys.argv[9]
print "cpdir = " + cpdir
logdir = sys.argv[10]
print "logdir = " + logdir
ubranch = sys.argv[11]
print "ubranch = " + ubranch
clean = sys.argv[12]
print "clean = " + clean
rpmbin = "/opt/montavista/host/bin/mvl-rpm"
print "rpmbin = " + rpmbin
sys.__stdout__.flush()


if edition == "pro":
  mvldir = "/mvista/dev_area/%s/%s" % (edition,reltag)
elif edition == "cge":
  mvldir = "/mvista/release_area/%s/%s" % (edition,reltag)
mvlkrnl = "%s/host/common/optional" % (mvldir)
print "mvldir = " + mvldir
print "ubranch = " + ubranch
print "mvlkrnl = " + mvlkrnl
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#get archs:
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
hn=string.strip(os.popen('hostname').read())
print "hostname = " + hn
if hn == 'node-1':
 archs=('x86_pentium2',)
#  archs=('arm_xscale_be',)
elif hn == 'node-2':
  archs=('x86_pentium3',)
elif hn == 'node-3':
  archs=('x86_pentium4',)
elif hn == 'node-4':
  archs=('ppc_7xx',)
elif hn == 'node-5':
  archs=('ppc_440',)
 # archs=('ppc_74xx',)
  #archs=('ppc_440','ppc_74xx')
elif hn == 'node-13':
  archs=('ppc_74xx',)
  #archs=('ppc_440',)
elif hn == 'node-10':
  archs=('sh_sh3_be',)
elif hn == 'node-11':
  archs=('mips_fp_be',)
elif hn == 'node-12':
  archs=('sh_sh4_be',)
elif 'hn' == 'node-17':
  archs=('sh_sh4_le',)
elif hn == 'node-18':
  archs=('x86_486',)
elif hn == 'node-19':
  archs=('x86_pentium3',)
elif hn == 'node-20':
  archs=('arm_920t_le',)
elif hn == 'node-21':
  archs=('arm_xscale_le',)
elif hn == 'node-22':
  archs=('arm_sa_le',)
elif hn == 'node-23':
  archs=('mips_fp_le',)
elif hn == 'node-24':
  archs=('ppc_7xx','ppc74xx')
elif hn == 'node-25':
  archs=('ppc_405',)
elif hn == 'node-26':
  archs=('arm_sa_be','xtensa_linux_be')
elif hn == 'node-27':
  archs=('arm_720t_le','x86_586')
elif hn == 'node-28':
  archs=('x86_crusoe','x86_pentium2')
elif hn == 'node-29':
  archs=('arm_xscale_be','sh_sh3_le')
elif hn == 'node-30':
  archs=('xtensa_linux_le','mips_nfp_le')
elif hn == 'node-31':
  archs=('ppc_8xx','ppc_82xx')
for a in archs:
  print "Building for arch(s) = " + a
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# clean /opt/montavista 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if clean == 'clean':
  os.chdir('/opt/montavista')
  os.system('rm -rf config devkit lup rpmdb')
  if os.path.exists('host'):
    sys.__stdout__.flush()
    os.system(rpmbin + '-forward -qa | grep -v host-rpm- | grep -v host-popt | xargs ' + rpmbin + '-forward --quiet -e --nodeps')
    sys.__stdout__.flush()
  else:
    os.chdir('/')
    os.system('rpm2cpio %s/host/cluster/host-rpm-4* | cpio -iud' % (mvldir))
    os.system('rpm2cpio %s/host/cluster/host-rpm-b* | cpio -iud' % (mvldir))
    os.system('rpm2cpio %s/host/cluster/host-rpm-d* | cpio -iud' % (mvldir))
    os.system('rpm2cpio %s/host/cluster/host-popt* | cpio -iud' % (mvldir))
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# install the edition
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  print 'Installing the edition ' + edition 
  os.chdir(mvldir + '/host/cluster')
  os.system('echo "Installing from  `pwd`"')
  os.system(rpmbin + "-forward -Uvh *.mvl --nodeps --force")
  sys.__stdout__.flush()
  os.chdir(mvldir + '/host/common')
  os.system('echo "Installing from  `pwd`"')
  os.system(rpmbin + "-forward -ivh *.mvl --nodeps")
  sys.__stdout__.flush()
  os.chdir(mvlkrnl)
  os.system('echo "Installing from  `pwd`"')
  os.system(rpmbin + "-forward -ivh *.mvl --nodeps")
  sys.__stdout__.flush()
  for arch in archs:
    print "building " + app + " for " + arch + " on " + hn
    os.chdir(mvldir + '/' + arch + '/cross/common')
    os.system('echo "Installing from  `pwd`"')
    os.system(rpmbin + "-forward -ivh *.mvl --nodeps")
    sys.__stdout__.flush()
    os.chdir(mvldir + '/' + arch + '/cross/cluster')
    os.system('echo "Installing from  `pwd`"')
    os.system(rpmbin + "-forward -ivh *.mvl --nodeps")
    sys.__stdout__.flush()
    if type == 'target':
      os.chdir(mvldir + '/' + arch + '/target')
      os.system('echo "Installing from  `pwd`"')
      if app == 'XFree86.cge': 
        os.system('ls *.mvl | grep -v XFree | xargs ' + rpmbin + "-forward -ivh --ignorearch --nodeps")
      if app == 'evlog-telco': 
        os.system('ls *.mvl | grep -v evlog | grep -v ' + app + ' | xargs ' + rpmbin + "-forward -ivh --ignorearch --nodeps")
        os.chdir('/mvista/dev_area/cge/mvlcge310-updates/evlog-6310/' + arch + '/target')
        os.system(rpmbin + "-forward -ivh *.mvl --ignorearch --nodeps")
      else:
        os.system('ls *.mvl | grep -v ' + app + ' | xargs ' + rpmbin + "-forward -ivh --ignorearch --nodeps")
      sys.__stdout__.flush()
else:
  os.system(rpmbin + '-forward -qa  | grep ' + app + ' | xargs ' + rpmbin + '-forward -e --nodeps')
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Get ready to build
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for arch in archs:
  logfile = a + '-' + app + '-' + buildid + '.log'
  os.chdir(builddir + '/' + app)
  if type == 'cross' and app in (gcc, binutils):
    os.chdir(builddir + '/' + app + '/SPECS')
    os.system('make')
    os.chdir(builddir + '/' + app)
    os.system('/home/build/bin/mk3.1appnoclean `pwd` ' + buildid + ' ' + arch + ' cross-' + app + ' ' + rpmbin +
              ' > ' + logdir + '/' + logfile + ' 2>&1')
  elif type == 'target':
    os.chdir(builddir + '/' + app)
    if app == 'XFree86.cge':
      xapp = 'XFree86'
      os.system('/home/build/bin/mk3.1appnoclean `pwd` ' + buildid + ' ' + arch + ' ' + xapp + ' ' + rpmbin + ' > ' + logdir
                + '/' + logfile + ' 2>&1 ')
    else:
      os.system('/home/build/bin/mk3.1appnoclean `pwd` ' + buildid + ' ' + arch + ' ' + app + ' ' + rpmbin + ' > ' + logdir
               + '/' + logfile + ' 2>&1 ')
  sys.__stdout__.flush()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# copy 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  if not os.path.exists(cpdir):
    os.mkdir(cpdir)
  if type == 'cross':
    if not os.path.exists(cpdir + '/' + arch + '/cross/common'):
      os.system('mkdir -p ' + cpdir + '/' + arch + '/cross/common')
    os.system('cp -a ' + builddir + '/' + app + '/RPMS/noarch/*' + arch + '* ' + cpdir + '/' + arch + '/cross/common/') 
  if type == 'target':
    if not os.path.exists(cpdir + '/' + arch + '/target'):
      os.system('mkdir -p ' + cpdir + '/' + arch + '/target')
    print "copying " + app + " for " + arch + " on " + hn + " to " + cpdir + "/" + arch + "/target/"
    os.system('cp -a ' + builddir + '/' + app + '/RPMS/' + arch + '/* ' + cpdir + '/' + arch + '/target/') 
  if not os.path.exists(cpdir + '/SRPMS'):
    os.system('mkdir -p ' + cpdir + '/SRPMS')
  print "copying src.rpm for " + app + " for " + arch + " on " + hn + " to " + cpdir + "/SRPMS"
  os.system('cp -a ' + builddir + '/' + app + '/SRPMS/* ' + cpdir + '/SRPMS/') 
  print "Finished building and copying " + app + '-' + buildid 
