#!/usr/bin/python
import os, string, sys, shutil, time, chroot, buildutils

# This script takes the following arguments:
# buildtag = build tag
# buildid
# product
# hostname = host name where chroot build is done (redhat90, suse90, etc.)
# cpdir
# foundation
# userpath
# logpath
# edition

# buildhhl.py will scp this script to the build directory
# and then execute it by ssh

# This script runs for each host and build all versions of rpm (common if needed and edition).
# It copies the rpm directory from the userland export to the chrooted host
# environment, builds rpm(s) (via chroot command), then copies rpms to the cpdir

def uninst(installdir,hostname):
  print 'uninstalling previous build...'
  sys.__stdout__.flush()
  chroot.chrootcmd(hostname,'rm -rf ' + installdir + '/*')

def rpminstall(chrootpath,installpath,rpm,rpmbin,hostname):
  if os.path.exists(chrootpath):
    chroot.chrootcmd(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm)

def rpminst_q(rpm,rpmbin,hostname):
  chroot.chrootcmd(hostname,rpmbin + ' -U ' + rpm)

def rpmbbnt(spec,buildid,rpmbuild,hostname):
  chroot.chrootcmd(hostname,rpmbuild + ' -bb --clean --define \\"_topdir ' + builddir + '\\" ' +
                    '--define \\"_mvl_build_id ' + buildid + '\\" ' +
                    '--define \\"vendor MontaVista Software, Inc.\\" ' +
                    '--define \\"packager <source@mvista.com>\\" ' +
                    '--define \\"_builddir ' + builddir + '/BUILD\\" ' +
                    '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' +
                    '--define \\"_mvl_host_os_build ' + hostname + '\\" ' + spec)
  return chroot.wrotecheck(hostname)

def touchresultfile(result):
  print 'touching result file in %s/%s-rpm-%s' % (logpath,hostname,result)
  os.system('touch %s/%s-rpm-%s' % (logpath,hostname,result))

#--------------------------------------------
# main
#--------------------------------------------
if len(sys.argv) != 10:
  print '\nusage: %s %s %s %s %s %s %s %s %s %s' % (sys.argv[0],'<buildtag>',
        '<buildid>','<product>','<hostname>','<cpdir>','<foundation>',
        '<userland path>','<log path>','<edition>')
  print '\n# of args = ' + str(len(sys.argv))
  print '\nHere are the args:'
  for x in sys.argv:
    print x
  sys.exit(1)

os.putenv('TERM','xterm')
buildtag = sys.argv[1]
buildid = sys.argv[2]
installdir = '/opt/montavista'
commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
product = sys.argv[3]
hostname = sys.argv[4]
print 'hostname = ' + hostname
sys.__stdout__.flush()
node = string.strip(os.popen('hostname').read())
print 'node = ' + node
sys.__stdout__.flush()
cpdir = sys.argv[5]
foundation = sys.argv[6]
userpath = sys.argv[7]
logpath = sys.argv[8]
edition = sys.argv[9]
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'

# this is the directory this script is run from
scriptdir = os.getcwd()
                                                                                         
# this is the directory in the chroot environment where rpm are built
builddir = '/home/build'
                                                                                          
# this is the chroot directory
chrootdir = '/chroot/%s' % (hostname)

# this is the cpdir in the chroot environment
chrootcpdir = '/home/build/RPMS/install' 
print 'scriptdir = ' + scriptdir
print 'builddir = ' + builddir
print 'chrootdir = ' + chrootdir
print 'chrootcpdir = ' + chrootcpdir

print '--> Building for ' + hostname + '...'
sys.__stdout__.flush()

# check to see if system rpm uses rpm or rpmbuild
if hostname in ('centos3','redhat80','redhat90','suse90'):
  sysrpm = 'rpmbuild'
else:
  sysrpm = 'rpm'

commonrpmbuild = commonrpmbin + 'build'

#----------------------------------------------
# Uninstall previous build and delete install area
#----------------------------------------------
uninst(installdir,hostname)

#----------------------------------------------
# all builds will build an edition rpm, so check for successfull build of host-rpm
# and touch a file for success or failure, which buildhhl.py will check for before continuing
# the build
#----------------------------------------------
hostrpmbuilt = 0

#----------------------------------------
# common-rpm
#----------------------------------------
# If build is a foundation build, common-rpm must be built
#
# To build common-rpm, copy the userland/rpm directories to the chroot environment
# then build common-rpm, install it with rpm2cpio, then rebuild it using common-rpm
#
bootstrapcrossrpm = 0
if product in ('fe','dev'):
  os.system('cp -a %s/rpm/* %s/%s' % (userpath,chrootdir,builddir))
  os.system('mkdir -p %s/%s/BUILD %s/%s/RPMS' % (chrootdir,builddir,chrootdir,builddir))
  buildutils.mstart('bootstrap-common-rpm')
  if rpmbbnt(builddir + '/SPECS/common-rpm.spec',buildid,sysrpm,hostname):
    chroot.chrootcmd(hostname,'cd /; rpm2cpio ' + builddir + '/RPMS/i386/common-rpm-4* | cpio -iud')
    chroot.chrootcmd(hostname,'cd /; rpm2cpio ' + builddir + '/RPMS/i386/common-rpm-dev* | cpio -iud')
    chroot.chrootcmd(hostname,'cd /; rpm2cpio ' + builddir + '/RPMS/i386/common-rpm-build* | cpio -iud')
    print 'BUILT: common-rpm for ' + hostname + ' built.'
  else:
    print 'BUILD ERROR: common-rpm for ' + hostname + ' did not build.'
    bootstrapcrossrpm = 1
  sys.__stdout__.flush()
  buildutils.mstop('bootstrap-common-rpm')
  if bootstrapcrossrpm:
    print 'boostrap build for common-rpm failed, stopping build.'
    touchresultfile('failed')
    sys.exit(1)
  else:
    # use common-rpm to build common-rpm
    os.system('rm -rf %s/%s/BUILD %s/%s/RPMS' % (chrootdir,builddir,chrootdir,builddir))
    os.system('mkdir -p %s/%s/BUILD %s/%s/RPMS' % (chrootdir,builddir,chrootdir,builddir))
    buildutils.mstart('common-rpm')
    if rpmbbnt(builddir + '/SPECS/common-rpm.spec',buildid,commonrpmbuild,hostname):
      rpminstall(chrootdir+builddir+'/RPMS/i386',builddir + '/RPMS/i386','common*.mvl',commonrpmbin,hostname)
      print 'BUILT: common-rpm for ' + hostname + ' built.'
    else:
      print 'BUILD ERROR: common-rpm for ' + hostname + ' did not build.'
    sys.__stdout__.flush()
    buildutils.mstop('common-rpm')

#----------------------------------------
# build edition-rpm
#----------------------------------------
if product not in ('dev','fe'):
  print 'Installing (rpmc2cpio) common-rpm from foundation...'
  sys.__stdout__.flush()
  # copy common-rpm rpms to chroot & install
  os.system('cp -a %s/host/%s/common-rpm* %s/%s/host/%s' % (foundation,hostname,chrootdir,chrootcpdir,hostname))
  sys.__stdout__.flush()
  chroot.chrootcmd(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/*rpm-*; do rpm2cpio \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done')
  if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
    # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install
    print "Here's the contents of /tmp/rpm2cpio-tmp.cpio:"
    sys.__stdout__.flush()
    os.system('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir))
    os.system('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir))
    print "try recopying common-rpm and re-installing..."
    sys.__stdout__.flush()
    os.system('cp -a %s/host/%s/host-rpm* %s/%s/host/%s' % (foundation,hostname,chrootdir,chrootcpdir,hostname))
    sys.__stdout__.flush()
    print 'Installing (rpmc2cpio) previously built version of host-rpm a second time...'
    sys.__stdout__.flush()
    chroot.chrootcmd(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/*rpm-*; do rpm2cpio \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done')
    if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
      # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install a second time
      print "Here's the contents of /tmp/rpm2cpio-tmp.cpio (2nd try):"
      sys.__stdout__.flush()
      os.system('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir))
      print "No use continuing the build..."
      sys.__stdout__.flush()
      os.system('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir))
      sys.exit(1)
  sys.__stdout__.flush()
  
buildutils.mstart('host-rpm')
if rpmbbnt(builddir + '/SPECS/host-rpm.spec',buildid,commonrpmbuild,hostname):
  chroot.chrootcmd(hostname,'cd /; rpm2cpio ' + builddir + '/RPMS/i386/host-rpm-4* | cpio -iud')
  rpminstall(chrootdir+builddir+'/RPMS/i386',builddir + '/RPMS/i386','host*.mvl',editionrpmbin,hostname)
  print 'BUILT: host-rpm for ' + hostname + ' built.'
  touchresultfile('succeeded')
else:
  print 'BUILD ERROR: host-rpm for ' + hostname + ' did not build.'
sys.__stdout__.flush()
buildutils.mstop('host-rpm')

chroot.chrootcmd(hostname,'mkdir -p ' + chrootcpdir + '/host/' + hostname)
if os.path.exists(chrootdir + builddir + '/RPMS/i386'):
  for hf in os.listdir(chrootdir + builddir + '/RPMS/i386'):
    #print 'found ' + hf + ' in RPMS/i386'
    #print 'copying ' + hf + ' to ' + chrootcpdir + '/host/' + hostname
      os.system('mv ' + chrootdir + builddir + '/RPMS/i386/' + hf + ' ' + chrootdir + chrootcpdir + '/host/' + hostname)

# now copy rpms to cpdir
os.system('mkdir -p %s/host' % (cpdir))
cpcmd = 'cp -a %s%s/host/%s %s/host' % (chrootdir,chrootcpdir,hostname,cpdir)
os.system(cpcmd)

# clean chroot host, but don't uninstall common/host-rpm
os.system('rm -rf %s/%s/BUILD %s/%s/RPMS' % (chrootdir,builddir,chrootdir,builddir))
os.system('rm -rf %s/%s/SOURCES %s/%s/SPECS' % (chrootdir,builddir,chrootdir,builddir))

