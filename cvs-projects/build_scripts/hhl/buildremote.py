#!/usr/bin/python
import signal
from buildFunctions import *

# This script takes the following arguments:
# datafile
# hostname = machine name where chroot build is done
# target

# buildhhl.py will scp this script to the build directory
# and then execute it by ssh

# This script runs on each node and figures out what will be built,
# grabs the right src.rpms and rpms, copies them to the chrooted host
# environment, installs src.rpms & binary rpms (via chroot command),
# builds rpms (via chroot command), then copies rpms to the cpdir
def uninst(installdir,hostname):
  printflush('uninstalling previous build...')
  chroot(hostname,'rm -rf ' + installdir + '/*',scripttest)
  chroot(hostname,'rm -rf /var/tmp/*',scripttest)
  if hostname == 'solaris8':
    systemCmd('cd /chroot/solaris8/opt; tar -xf /opt/montavista.f3.tar',scripttest)
    systemCmd('chown -R build:engr /chroot/solaris8/opt/montavista',scripttest)

def rpminstall(chrootpath,installpath,rpm,rpmbin,hostname):
  if os.path.exists(chrootpath):
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest)
  else:
    printflush('chrootpath does not exist: ' + chrootpath)
    printflush('not installing ' + rpm)
    res = 1
  printflush('result of install: ' + str(res))
  return res

def rpminst(rpm,rpmbin,hostname):
  res = chroot(hostname,rpmbin + ' -Uvh ' + rpm + ' --ignoreos',scripttest)
  printflush('result of install: ' + str(res))
  return res

def rpminst_q(rpm,rpmbin,hostname):
  res = chroot(hostname,rpmbin + ' -U ' + rpm + ' --ignoreos',scripttest)
  printflush('result of install: ' + str(res))
  return res

def rpmbb(target,spec,buildid,rpmbuild,type,hostname):
  targopt = '--' + type + '=' + target + '-linux --clean'
  chroot(hostname,rpmbuild + ' ' + targopt + ' -bb --define \\"_topdir ' + builddir + '\\" ' +
                  '--define \\"_mvl_build_id ' + buildid + '\\" ' +
                  '--define \\"vendor MontaVista Software, Inc.\\" ' +
                  '--define \\"packager <source@mvista.com>\\" ' +
                  '--define \\"_builddir ' + builddir + '/BUILD\\" ' +
                  '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' +
                  spec,scripttest)
  return wrotecheck(hostname)

def rpmbbnt(spec,buildid,rpmbuild,hostname):
  printflush('Using rpmbuild = ' + rpmbuild)
  chroot(hostname,rpmbuild + ' --clean -bb --define \\"_topdir ' + builddir + '\\" ' +
                    '--define \\"_mvl_build_id ' + buildid + '\\" ' +
                    '--define \\"vendor MontaVista Software, Inc.\\" ' +
                    '--define \\"packager <source@mvista.com>\\" ' +
                    '--define \\"_builddir ' + builddir + '/BUILD\\" ' +
                    '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' +
                    '--define \\"_mvl_host_os_build ' + hostname + '\\" ' +
                    spec,scripttest)
  return wrotecheck(hostname)

def buildgcc(target,buildid,rpmbin,rpmbuild,builddir,hostname):
  mstart('cross-binutils')
  spec = builddir + '/SPECS/cross-binutils.spec'
  if rpmbb(target,spec,buildid,rpmbuild,'cross',hostname):
    rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir+'/RPMS/'+hostarch,'cross-'+target+'-binutils*.mvl',rpmbin,hostname)
    printflush('BUILT: cross-binutils for ' + target + ' built.')
  else:
    printflush('BUILD ERROR: cross-binutils for ' + target + ' did not build.')
  mstop('cross-binutils')
  mstart('cross-gcc')
  spec = builddir + '/SPECS/cross-gcc.spec'
  gccrpmbuild = rpmbuild
  if gcclicense:
    gccrpmbuild = rpmbuild + ' --define \\"_mvl_gcc_license ' + gcclicense + '\\"'
  if rpmbb(target,spec,buildid,gccrpmbuild,'cross',hostname):
    rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir+'/RPMS/'+hostarch,'cross-'+target+'-g*.mvl',rpmbin,hostname)
    printflush('BUILT: cross-gcc for ' + target + ' built.')
  else:
    printflush('BUILD ERROR: cross-gcc for ' + target + ' did not build.')
  mstop('cross-gcc')

#--------------------------------------------
# main
#--------------------------------------------
if len(sys.argv) != 4:
  printflush('\nusage: %s %s %s %s' % (sys.argv[0],'<data file>','<hostname>','<target>'))
  printflush('\n# of args = ' + str(len(sys.argv)))
  printflush('\nHere are the args:')
  for x in sys.argv:
    printflush(x)
  sys.exit(1)

printflush("Starting %s at %s" % (sys.argv[0],gettime()))
mstart('%s-setup' % sys.argv[0])
#os.putenv('TERM','xterm')
datafile = sys.argv[1]
printflush("datafile = %s" % datafile)
hostname = sys.argv[2]
printflush('hostname = ' + hostname)
target = sys.argv[3]
printflush('target = ' + target)
getdiskspace(hostname)
if hostname == 'solaris8':
  os.environ['PATH'] = '/opt/montavista/common/bin:' + os.environ['PATH']
  if os.popen('uname -r').readline() == '5.10\n':
    pid = os.spawnl(os.P_NOWAIT, '/opt/set-host', 'set-host', '5.8')
    while(os.popen('uname -r').readline() != '5.8\n'):  #This takes a minute to start so we have to wait
      pass
  else:
   pid = None

node = string.strip(os.popen('hostname').read())
printflush('node = ' + node)
# this is the directory this script is run from
scriptdir = os.getcwd()
if os.path.exists(datafile):
  exec(open(datafile))
  printflush('targethost = ' + targethost)
else:
  printflush("No datafile found.  Stopping build.")
  systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest)
  mstop('%s-setup' % sys.argv[0])
  printflush("Finished %s at %s" % (sys.argv[0],gettime()))
  if hostname == 'solaris8':
    if pid != None:
      os.kill(pid, signal.SIGTERM )
  sys.exit(1)

installdir = '/opt/montavista'
commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
commonrpmbuild = installdir + '/common/bin/mvl-common-rpmbuild'
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
editionrpmbuild = installdir + '/' + edition + '/bin/mvl-edition-rpmbuild'
                                                                                         
# this is the directory in the chroot environment where rpm are built
builddir = '/home/build'
                                                                                          
# this is the chroot directory
chrootdir = '/chroot/%s' % (hostname)

# this is the cpdir in the chroot environment
chrootcpdir = '/home/build/RPMS/install' 

printflush('scriptdir = ' + scriptdir)
printflush('builddir = ' + builddir)
printflush('chrootdir = ' + chrootdir)
printflush('chrootcpdir = ' + chrootcpdir)

printflush('--> Building for ' + hostname + '...')

# check to see if system rpm uses rpm or rpmbuild
if hostname in ('centos3','redhat80','redhat90','suse90'):
  sysrpmbuild = 'rpmbuild'
  sysrpmbin = 'rpm'
  rpm2cpio = 'rpm2cpio'
  cpall = 'cp -a'
  hostarch = 'i386'
elif hostname in ('centos3_64',):
  sysrpmbuild = 'rpmbuild'
  sysrpmbin = 'rpm'
  rpm2cpio = 'rpm2cpio'
  cpall = 'cp -a'
  hostarch = 'x86_64'
elif hostname == 'solaris8':
  sysrpmbuild = '/opt/montavista/common/bin/mvl-common-rpmbuild'
  sysrpmbin = '/opt/montavista/common/bin/mvl-common-rpm'
  rpm2cpio = '/opt/montavista/common/bin/rpm2cpio'
  cpall = 'cp -rp'
  hostarch = 'sun4u'
else:
  sysrpmbuild = 'rpm'
  sysrpmbin = 'rpm'
  rpm2cpio = 'rpm2cpio'
  cpall = 'cp -a'
  hostarch = 'i386'

#---------------------------------
# define packages to build
#---------------------------------
if product not in ('dev','fe'):
  mvltapps = ()

if string.find(target,'x86') > -1 and string.find(target,'uclibc') == -1 and product in ('dev','fe'):
  crossapps = x86brcrossapps
elif string.find(target,'x86') > -1 and string.find(target,'uclibc') > -1 and product in ('dev','fe'):
  crossapps = x86uclibcbrcrossapps
elif string.find(target,'uclibc') > -1 and product in ('dev','fe'):
  crossapps = uclibcbrcrossapps
elif product in ('dev','fe','pro','cge','mobilinux','scripttest'):
  crossapps = brcrossapps
elif product == 'propk':
  crossapps = ('previewkit-dev',)
else:
  crossapps = ()

if not crossapps and not mvltapps:
  printflush("No apps defined.  Exiting build")
  mstop('%s-setup' % sys.argv[0])
  printflush("Finished %s at %s" % (sys.argv[0],gettime()))
  if hostname == 'solaris8':
    if pid != None:
      os.kill(pid, signal.SIGTERM )
  sys.exit(0)

#printflush('Cleaning %s on %s...' % (builddir,node))
os.chdir('%s/%s' % (chrootdir,builddir))
if foundation != 'skip':
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS',scripttest)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest)
  systemCmd('mkdir -p  RPMS/install/host/' + hostname + ' RPMS/install/' + target + '/cross',scripttest)
  systemCmd('mkdir -p  RPMS/install/host/common',scripttest)
  systemCmd('mkdir -p  RPMS/install/' + target + '/target',scripttest)
  if hostname == 'solaris8':
    systemCmd('ls -la',scripttest)
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest)
    systemCmd('ls -la',scripttest)
else:
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS/i386 RPMS/noarch',scripttest)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest)
  if hostname == 'solaris8':
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest)
os.chdir(scriptdir)
getdiskspace(hostname)

logfile = "hostprep-%s.log" % (hostname)
log = "%s/%s" % (logdir, logfile)
printflush("Running hostprep...")
pcmd = 'ssh %s "cd %s; ./hostprep.py %s %s %s %s %s %s" >> %s 2>&1' % (node,scriptdir,
         hostname, cpdir, target,foundation, 'all', product, log)
systemCmd(pcmd,scripttest)
getdiskspace(hostname)

#----------------------------------------------
# Uninstall previous build and delete install area
#----------------------------------------------
uninst(installdir,hostname)
getdiskspace(hostname)

# install all src.mvls
printflush('Installing src mvls...')
rpminst(builddir + '/SRPMS/*.src.rpm --define \\"_topdir ' + builddir + '\\"',sysrpmbin,hostname)
getdiskspace(hostname)
#----------------------------------------
# step 3: build & install common-rpm (if needed)
#----------------------------------------
printflush('Installing (rpmc2cpio) previously built version of common-rpm...')
chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest)
if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
  # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install
  printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio:")
  systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest)
  systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest)
  printflush("try recopying common-rpm and re-installing...")
  systemCmd('cp -a %s/build/host/%s/common-rpm* %s/%s/host/%s' % (foundation,hostname,chrootdir,chrootcpdir,hostname),scripttest)
  printflush('Installing (rpmc2cpio) previously built version of common-rpm a second time...')
  chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest)
  if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
    # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install a second time
    printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio (2nd try):")
    systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest)
    printflush("No use continuing the build...")
    systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest)
    printflush('BUILD ERROR: ' + sys.argv[0] + '-setup for ' + target + ' did not build.')
    mstop('%s-setup' % sys.argv[0])
    if hostname == 'solaris8':
      if pid != None:
        os.kill(pid, signal.SIGTERM )
    sys.exit(1)
getdiskspace(hostname)

# now use common-rpm to install common-rpm
printflush("Using common-rpm to install common-rpm")
rdir = '%s/host/%s' % (chrootcpdir,hostname)
rpminstall(chrootdir+rdir,rdir,'common-rpm*',commonrpmbin,hostname)
chroot(hostname,'mkdir -p ' + chrootcpdir + '/' + target + '/cross/' + hostname,scripttest)
chroot(hostname,'mkdir -p ' + chrootcpdir + '/installer_rpms/host/' + hostname,scripttest)

# install common-* noarch rpms, like common-autoconf, etc.
printflush("Using common-rpm to install common noarch rpms")
rdir = '%s/host/common' % (chrootcpdir)
if hostname != "solaris8":
  rpminstall(chrootdir+rdir,rdir,'common-*',commonrpmbin,hostname)
else:
  rpminstall(chrootdir+rdir,rdir,'common-* --ignoreos',commonrpmbin,hostname)

# install common-* rpms, like common-gettext, etc.
printflush("Using common-rpm to install common hostarch rpms")
rdir = '%s/host/%s' % (chrootcpdir,hostname)
if os.path.exists(chrootdir+rdir):
  os.chdir(chrootdir+rdir)
rpmlist = os.popen('ls common* | grep -v rpm | grep -v elfutils | grep -v expat').readlines()
os.chdir(scriptdir)
for installrpm in rpmlist:
  if hostname != "solaris8":
    rpminstall(chrootdir+rdir,rdir,string.strip(installrpm),commonrpmbin,hostname)
  else:
    rpminstall(chrootdir+rdir,rdir,string.strip(installrpm) + ' --ignoreos',commonrpmbin,hostname)
if hostname != "solaris8":
  rpminstall(chrootdir+rdir,rdir,"common-apt-rpm*",commonrpmbin,hostname)
  rpminstall(chrootdir+rdir,rdir,"common-elfutils*",commonrpmbin,hostname)
  rpminstall(chrootdir+rdir,rdir,"common-expat*",commonrpmbin,hostname)
else:
  rpminstall(chrootdir+rdir,rdir,'common-apt-rpm* --ignoreos',commonrpmbin,hostname)
  rpminstall(chrootdir+rdir,rdir,'common-elfutils* --ignoreos',commonrpmbin,hostname)
  rpminstall(chrootdir+rdir,rdir,'common-expat* --ignoreos',commonrpmbin,hostname)

# install host-* rpms
printflush('installing host-rpm')
rdir = '%s/host/%s' % (chrootcpdir,hostname)
if os.path.exists(chrootdir+rdir):
  os.chdir(chrootdir+rdir)
chroot(hostname,'cd /; ' + rpm2cpio + ' /home/build/RPMS/install/host/' + hostname + '/host-rpm-* | cpio -iud',scripttest)
#if hostname == 'solaris8':
#  rpminstall(chrootdir+rdir,rdir,'host-rpm*.mvl --nodeps',editionrpmbin,hostname)
#else:
#  rpminstall(chrootdir+rdir,rdir,'host-rpm*.mvl',editionrpmbin,hostname)
printflush('installing host rpms')
if hostname != "solaris8":
  rpminstall(chrootdir+rdir,rdir,'host-*',editionrpmbin,hostname)
else:
  rdir = '/opt/montavista/packages'
  systemCmd('cp /opt/montavista/packages %s/opt/montavista' % (chrootdir),scripttest)
  rpminstall(chrootdir+rdir,rdir,'host-tool*.mvl --ignoreos --justdb',commonrpmbin,hostname)
  systemCmd('rm -rf %s/opt/montavista/packages' % chrootdir,scripttest)
  rdir = '%s/host/%s' % (chrootcpdir,hostname)
  rpminstall(chrootdir+rdir,rdir,'host-* --ignoreos',editionrpmbin,hostname)

rpminstall(chrootdir+chrootcpdir+'/'+target+'/cross/common',chrootcpdir+'/'+target+'/cross/common','*filesystem*.mvl',editionrpmbin,hostname)
rpminstall(chrootdir+chrootcpdir+'/'+target+'/cross/common',chrootcpdir+'/'+target+'/cross/common','*libopt*.mvl',editionrpmbin,hostname)
rpminstall(chrootdir+chrootcpdir+'/'+target+'/cross/common',chrootcpdir+'/'+target+'/cross/common','*libtool*.mvl',editionrpmbin,hostname)

if os.path.exists(chrootdir + builddir + '/RPMS/' + hostarch):
  for hf in os.listdir(chrootdir + builddir + '/RPMS/' + hostarch):
    #print 'found ' + hf + ' in RPMS/' + hostarch
    #print 'copying ' + hf + ' to ' + chrootcpdir + '/host/' + hostname
      systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' + chrootdir + chrootcpdir + '/host/' + hostname,scripttest)
#----------------------------------------
# Install needed RPMS from chrootcpdir
#----------------------------------------
rdir = '%s/%s/target' % (chrootcpdir,target)
if string.find(target,'uclibc') > -1:
  glibcdir = 'uclibc'
else:
  glibcdir = 'glibc'
if product in ('dev',) and string.find(target,'uclibc') == -1:
  noarchrpms = ['kernel-headers',glibcdir + '-bootstrap','binutils']
elif product in ('dev',) and string.find(target,'uclibc') > -1:
  noarchrpms = ['kernel-headers',glibcdir,'binutils']
elif product in ('dev','fe','pro','proasync','propk','scripttest'):
  noarchrpms = ['kernel-headers',glibcdir,'binutils']
else:
  noarchrpms = ['kernel-headers',glibcdir]
for nr in noarchrpms:
  rpminstall(chrootdir+rdir,rdir,nr + '*',editionrpmbin + ' --nodeps --target='+target+'-linux --nodeps',hostname)

if product == "propk":
  pkrdir = "/home/build/RPMS/install/host/' + hostname"
  pkhrpms = "*mkimage* *tftp-hpa*"
  rpminstall(chrootdir+pkrdir,pkrdir,pkhrpms,editionrpmbin,hostname)
getdiskspace(hostname)
mstop('%s-setup' % sys.argv[0])

#---------------------------------
# Build the necessary RPMS
#---------------------------------
if product in ('dev','fe'):
  buildgcc(target,buildid,editionrpmbin,editionrpmbuild,builddir,hostname)
else:
  # install toolchain
  rpminstall(chrootdir+chrootcpdir+'/'+target+'/cross/common',chrootcpdir+'/'+target+'/cross/common','*.mvl',editionrpmbin,hostname)
  rpminstall(chrootdir+chrootcpdir+'/'+target+'/cross/'+hostname,chrootcpdir+'/'+target+'/cross/'+hostname,'*.mvl',editionrpmbin,hostname)
getdiskspace(hostname)

for app in crossapps:
  if app in ('gccfalse','gcctrue'):
    startapp = 'gcc'
  else:
    startapp = app
  if os.path.exists(chrootdir + builddir + '/SPECS/cross-' + startapp + '.spec') and startapp != 'gcc-alt' or scripttest == 1:
    mstart('cross-' + startapp)
    if app == 'gccfalse':
      bs = builddir + '/SPECS/cross-gcc.spec --define \\"_mvl_gcc_license false\\"'
    elif app == 'gcctrue':
      bs = builddir + '/SPECS/cross-gcc.spec --define \\"_mvl_gcc_license true\\"'
    elif app == 'apt-rpm-config' and aptedition:
      bs = builddir + '/SPECS/cross-' + app + '.spec --define \\"_edition ' + aptedition + '\\"'
    else:
      bs = builddir + '/SPECS/cross-' + app + '.spec'
    if rpmbb(target,bs,buildid,editionrpmbuild,'cross',hostname):
      # don't install rebuilt cross-gcc since foundation version is still installed
      if startapp not in ('gcc','previewkit-dev'):
        rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir+'/RPMS/' + hostarch,'cross-'+target+'-'+startapp+'*.mvl',editionrpmbin,hostname)
      printflush('BUILT: cross-' + startapp + ' for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-' + startapp + ' for ' + target + ' did not build.')
    mstop('cross-' + startapp)
  elif startapp == 'gcc-alt' and os.path.exists(chrootdir + builddir + '/SPECS/cross-gcc.spec') and target in ('ppc_9xx',):
    mstart('cross-gcc-64')
    bs = builddir + '/SPECS/cross-gcc.spec --define \\"_mvl_multilib 64\\"'
    if rpmbb(target,bs,buildid,editionrpmbuild,'cross',hostname):
      printflush('BUILT: cross-gcc-64 for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-gcc-64 for ' + target + ' did not build.')
    mstop('cross-gcc-64')
  elif startapp == 'gcc-alt' and os.path.exists(chrootdir + builddir + '/SPECS/cross-gcc.spec') and target in ('x86_amd64','x86_em64t',):
    mstart('cross-gcc-32')
    bs = builddir + '/SPECS/cross-gcc.spec --define \\"_mvl_multilib 32\\"'
    if rpmbb(target,bs,buildid,editionrpmbuild,'cross',hostname):
      printflush('BUILT: cross-gcc-32 for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-gcc-32 for ' + target + ' did not build.')
    mstop('cross-gcc-32')
  elif startapp == 'gcc-alt' and os.path.exists(chrootdir + builddir + '/SPECS/cross-gcc.spec'):
    mstart('cross-gcc-n64')
    bs = builddir + '/SPECS/cross-gcc.spec --define \\"_mvl_multilib n64\\"'
    if rpmbb(target,bs,buildid,editionrpmbuild,'cross',hostname):
      printflush('BUILT: cross-gcc-n64 for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-gcc-n64 for ' + target + ' did not build.')
    mstop('cross-gcc-n64')
  else:
    mstart('cross-' + startapp)
    printflush("BUILD ERROR: cross-" + startapp + " is missing a spec file...skipping the build.")
    mstop('cross-' + startapp)
getdiskspace(hostname)

# build cross-mvlt apps
for ma in mvltapps:
  mstart('cross-' + ma)
  if os.path.exists(chrootdir + builddir + '/SPECS/cross-' + ma + '.spec') or scripttest == 1:
    if rpmbb(target,builddir + '/SPECS/cross-' + ma + '.spec',buildid,editionrpmbuild,'cross',hostname):
      printflush('BUILT: cross-' + ma + ' for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-' + ma + ' for ' + target + ' did not build.')
  else:
    printflush("BUILD ERROR: cross-" + ma + " is missing a spec file...skipping the build.")
  mstop('cross-' + ma)
getdiskspace(hostname)

# build cross-prelink
if product in ('dev','fe'):
  if os.path.exists(chrootdir + builddir + '/SPECS/cross-prelink.spec') or scripttest == 1:
    mstart('cross-prelink')
    if rpmbb(target,builddir + '/SPECS/cross-prelink.spec',buildid,editionrpmbuild,'cross',hostname):
      printflush('BUILT: cross-prelink for ' + target + ' built.')
    else:
      printflush('BUILD ERROR: cross-prelink for ' + target + ' did not build.')
    mstop('cross-prelink')
  else:
    printflush("BUILD ERROR: cross-prelink is missing a spec file...skipping the build.")
getdiskspace(hostname)

# copy rpms to dev_area
printflush("Copying rpm to dev_area")
systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/*cross*.mvl ' + 
          chrootdir + chrootcpdir + '/' + target + '/cross/' + hostname,scripttest)
getdiskspace(hostname)

if product == 'propk':
  systemCmd('mv ' + chrootdir + builddir + '/RPMS/noarch/*previewkit* ' +
            chrootdir + chrootcpdir + '/host/' + hostname,scripttest)


# now copy rpms to cpdir
cpcmd = 'cp -a %s%s/%s/cross/%s %s/%s/cross' % (chrootdir,chrootcpdir,target,hostname,cpdir,target)
printflush('copying the following:')
systemCmd('ls %s%s/%s/cross/%s' % (chrootdir,chrootcpdir,target,hostname),scripttest)
systemCmd(cpcmd,scripttest)
if os.popen('ls %s/%s/cross/%s/*testsuite*' % (cpdir,target,hostname)).readlines():
  if not os.path.exists('%s/%s/cross/%s/testing' % (cpdir,target,hostname)):
    systemCmd('mkdir -p %s/%s/cross/%s/testing' % (cpdir,target,hostname),scripttest)
  systemCmd('mv %s/%s/cross/%s/*testsuite* %s/%s/cross/%s/testing' % (cpdir,target,hostname,
             cpdir,target,hostname),scripttest)
cpcmd = 'cp -a %s%s/installer_rpms %s/' % (chrootdir,chrootcpdir,cpdir)
systemCmd(cpcmd,scripttest)
getdiskspace(hostname)
# now remove foundation version of cross-gcc if the build rebuilt cross-gcc
if rebuildgcc:
  removefiles = ("gcc","g++","gomp","stdc++")
  for rmfile in removefiles:
    files = os.popen('cd %s/%s/cross/%s; ls *%s*' % (cpdir,target,hostname,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/cross/%s/%s..." % (cpdir,target,hostname,file.strip()))
        systemCmd('rm -f %s/%s/cross/%s/%s' % (cpdir,target,hostname,file.strip()),scripttest)
    files = os.popen('cd %s/%s/cross/%s/testing; ls *%s*' % (cpdir,target,hostname,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/cross/%s/testing/%s..." % (cpdir,target,hostname,file.strip()))
        systemCmd('rm -f %s/%s/cross/%s/testing/%s' % (cpdir,target,hostname,file.strip()),scripttest)

#----------------------------------------------
# Uninstall build and delete install area
#----------------------------------------------
uninst(installdir,hostname)
getdiskspace(hostname)

# clean chroot host
printflush("Running hostclean...")
logfile = "hostclean-" + hostname + ".log"
log = "%s/%s" % (logdir, logfile)
pcmd = 'ssh %s "cd %s; ./hostclean.py %s %s >>" %s 2>&1' % (node,scriptdir,hostname,foundation,log)
systemCmd(pcmd,scripttest)
if hostname == 'solaris8':
  if pid != None:
    os.kill(pid, signal.SIGTERM )
getdiskspace(hostname)
printflush("Finished %s at %s" % (sys.argv[0],gettime()))
