#!/usr/bin/python
import signal
from buildFunctions import *

# This script takes the following arguments:
# data file

# buildhhl.py will scp this script and the data file to the build directory
# and then execute it by ssh

# This script runs on each node and figures out what will be built,
# copies the sources & specs and binary rpms to the chrooted host
# environment, installs binary rpms (via chroot command),
# builds rpms (via chroot command), then copies rpms to the cpdir
def uninst(installdir,hostname):
  printflush('uninstalling previous build...')
  chroot(hostname,'rm -rf ' + installdir + '/*',scripttest)
  chroot(hostname,'rm -rf /var/tmp/*',scripttest)
  if hostname == 'solaris8':
    systemCmd('cd /chroot/solaris8/opt; tar -xf /opt/%s' % shttar,scripttest)
    systemCmd('chown -R build:engr /chroot/solaris8/opt/montavista',scripttest)

def rpminstall(chrootpath,installpath,rpm,rpmbin,hostname,log=''):
  if os.path.exists(chrootpath):
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest,log)
  else:
    printflush('chrootpath does not exist: ' + chrootpath,log,scripttest)
    printflush('not installing ' + rpm,log,scripttest)
    res = 1
  printflush('result of install: ' + str(res),log,scripttest)

def rpmb(spec,buildid,rpmbuild,hostname,bcmd,log):
  printflush('Using rpmbuild = ' + rpmbuild,log,scripttest)
  chroot(hostname,rpmbuild + ' --clean -' + bcmd + ' --define \\"_topdir ' + builddir + '\\" ' +
                    '--define \\"_mvl_build_id ' + buildid + '\\" ' +
                    '--define \\"vendor MontaVista Software, Inc.\\" ' +
                    '--define \\"packager <source@mvista.com>\\" ' +
                    '--define \\"_builddir ' + builddir + '/BUILD\\" ' +
                    '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' +
                    '--define \\"_mvl_host_os_build ' + hostname + '\\" ' +
                    spec,scripttest,log)
  return wrotecheck(hostname)

#--------------------------------------------
# main
#--------------------------------------------
if len(sys.argv) != 3:
  printflush('\nusage: %s %s %s' % (sys.argv[0],'<data file>','<hostname>'))
  printflush('\n# of args = ' + str(len(sys.argv)))
  printflush('\nHere are the args:')
  for x in sys.argv:
    printflush(x)
  sys.exit(1)

datafile = sys.argv[1]
hostname = sys.argv[2]
if os.path.exists(datafile):
  exec(open(datafile))

collectivelogdir = '%s/hostapps/%s' % (collectivelogdir,hostname)
collectivelog = '%s/%s' % (collectivelogdir,'buildremothost-setup')
mstart('buildremothost-setup',collectivelog,scripttest)
printflush("Starting %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
#os.putenv('TERM','xterm')
printflush("datafile = %s" % datafile,collectivelog,scripttest)
printflush('hostname = ' + hostname,collectivelog,scripttest)
printflush('copydir = ' + copydir,collectivelog,scripttest)

if hostname == 'solaris8':
  os.environ['PATH'] = '/opt/montavista/common/bin:' + os.environ['PATH']
  if os.popen('uname -r').readline() == '5.10\n':
    pid = os.spawnl(os.P_NOWAIT, '/opt/set-host', 'set-host', '5.8')
    while(os.popen('uname -r').readline() != '5.8\n'):  #This takes a minute to start so we have to wait
      pass
  else:
   pid = None

# this is the directory this script is run from
scriptdir = os.getcwd()
if os.path.exists(datafile):
  printflush('targethost = ' + targethost,collectivelog,scripttest)
else:
  printflush("No datafile found.  Stopping build.",collectivelog,scripttest)
  systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest,collectivelog)
  printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
  mstop('buildremotehost-setup',collectivelog,scripttest)
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

printflush('scriptdir = ' + scriptdir,collectivelog,scripttest)
printflush('builddir = ' + builddir,collectivelog,scripttest)
printflush('chrootdir = ' + chrootdir,collectivelog,scripttest)
printflush('chrootcpdir = ' + chrootcpdir,collectivelog,scripttest)
getdiskspace(hostname)

printflush('--> Building for ' + hostname + '...',collectivelog,scripttest)

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
hostapps = brhhostapps
commonapps = brhcommonapps
noarchapps = brhnoarchapps
commonExcludes = ()
if hostname == 'solaris8':
  commonExcludes = ('gettext','libtool','make','mvlutils','m4','texinfo','minicom','patch','sed','libsepol','checkpolicy','swig','audit','libselinux','libsemanage','policycoreutils','sqlite','setools','man2html')
elif hostname in ('centos3_64','suse90'):
  commonExcludes = ('man2html',)
if product == 'propk':
  hostapps = ['dhcp-previewkit','mkimage-previewkit','tftp-hpa-previewkit','tsload-previewkit',
              'zsrec-previewkit']
elif product == 'bst':
  hostapps = ['bst-certification',]

bcmd = 'bb'
# if nothing to build for hostapps, mvl-installer, exit
if not hostapps and not commonapps and not noarchapps and product not in ('cgeasync','mobiasync','proasync'):
  printflush("no rpms to build",collectivelog,scripttest)
  if product not in ('mls','tsuki'):
    systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest)
    printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
    mstop('buildremotehost-setup',collectivelog,scripttest)
    if hostname == 'solaris8':
      if pid != None:
        os.kill(pid, signal.SIGTERM )
    sys.exit(1)
elif hostname != targethost:
  printflush("Stuff to build:",collectivelog,scripttest)
  for hak in hostapps.keys():
    printflush('%s hostapps:' % hak,collectivelog,scripttest)
    for happ in hostapps[hak]:
      printflush(happ,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)
  for cak in commonapps.keys():
    printflush('%s commonapps:' % cak,collectivelog,scripttest)
    for capp in commonapps[cak]:
      if capp not in commonExcludes:
        printflush(capp,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)
else:
  bcmd = 'ba'
  printflush("Stuff to build:",collectivelog,scripttest)
  for hak in hostapps.keys():
    printflush('%s hostapps:' % hak,collectivelog,scripttest)
    for happ in hostapps[hak]:
      printflush(happ,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)
  if 'host' in noarchapps.keys():
    printflush('host noarchapps:',collectivelog,scripttest)
    for napp in noarchapps['host']:
      printflush(napp,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)
  if 'common' in noarchapps.keys():
    printflush('common noarchapps:',collectivelog,scripttest)
    for napp in noarchapps['common']:
      printflush(napp,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)
  for cak in commonapps.keys():
    printflush('%s commonapps:' % cak,collectivelog,scripttest)
    for capp in commonapps[cak]:
      if capp not in commonExcludes:
        printflush(capp,collectivelog,scripttest)
    printflush('\n',collectivelog,scripttest)

#print 'Cleaning %s on %s...' % (builddir,node)
if os.path.exists('%s/%s' % (chrootdir,builddir)):
  os.chdir('%s/%s' % (chrootdir,builddir))
else:
  printflush('there is no %s/%s on this node...stopping build' % (chrootdir,builddir),collectivelog,scripttest)
  mstop('buildremotehost-setup',collectivelog,scripttest)
  sys.exit(1)  
if foundation != 'skip':
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/host/' + hostname,scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/host/common',scripttest,collectivelog)
  if hostname == 'solaris8':
    systemCmd('ls -la',scripttest,collectivelog)
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
    systemCmd('ls -la',scripttest,collectivelog)
else:
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS/i386 RPMS/noarch',scripttest,collectivelog)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest,collectivelog)
  if hostname == 'solaris8':
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
os.chdir(scriptdir)
getdiskspace(hostname)

#----------------------------------------------
# Uninstall previous build and delete install area
#----------------------------------------------
uninst(installdir,hostname)
getdiskspace(hostname)

printflush('Starting build...',collectivelog,scripttest)
#----------------------------------------
# step 3: build & install common-rpm (if needed)
#----------------------------------------
if product in ('dev','fe'):
  mstop('buildremotehost-setup',collectivelog,scripttest)
  # common-rpm needs to be bootstrapped....built once with the system rpm,
  # then again with mvl-rpm
  if hostname != 'solaris8':
    # copy rpm SOURCES and SPECS
    collectivelog = '%s/%s' % (collectivelogdir,'system-rpm-built-common-rpm')
    mstart('system-rpm-built-common-rpm',collectivelog,scripttest)
    if 'userland' in cvspaths.keys(): 
      systemCmd('%s %s/rpm/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['userland'][0],chrootdir,builddir),scripttest,collectivelog)
      systemCmd('%s %s/rpm/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['userland'][0],chrootdir,builddir),scripttest,collectivelog)
    if rpmb(builddir + '/SPECS/common-rpm.spec',buildid,sysrpmbuild,hostname,bcmd,collectivelog):
      chroot(hostname,'cd /; for each in /home/build/RPMS/' + hostarch + '/common-rpm-*; do rpm2cpio \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/' + hostarch + '/common-rpm-install-failed; fi done',scripttest,collectivelog)
      if os.path.exists(chrootdir + '/' + builddir + '/RPMS/' + hostarch + '/common-rpm-install-failed'):
        # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install
        printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio:",collectivelog,scripttest)
        systemCmd('cat %s/%s/RPMS/' + hostarch + '/common-rpm-install-failed' % (chrootdir,builddir),scripttest,collectivelog)
        systemCmd('rm -f %s/%s/RPMS/' + hostarch + '/common-rpm-install-failed' % (chrootdir,builddir),scripttest,collectivelog)
        printflush("No use continuing the build...",collectivelog,scripttest)
        # don't use systemCmd here because we always want to touch this file so the builds 
        # can continue and don't wait for the file to be touched
        systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest)
        printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
        if hostname == 'solaris8':
          if pid != None:
            os.kill(pid, signal.SIGTERM )
        sys.exit(1)
      printflush('BUILT: system-rpm-built-common-rpm for ' + hostname + ' built.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: system-rpm-built-common-rpm for ' + hostname + ' did not build.',collectivelog,scripttest)
    mstop('system-rpm-built-common-rpm',collectivelog,scripttest)
    # now delete the rpms just built, and rebuild & install using mvl-common-rpm
    chroot(hostname,'rm -rf %s/BUILD %s/RPMS/%s; mkdir -p %s/BUILD' % (builddir,builddir,hostarch,builddir),scripttest)
  if hostname != 'solaris8':
    collectivelog = '%s/%s' % (collectivelogdir,'common-rpm')
    mstart('common-rpm',collectivelog,scripttest)
    if rpmb(builddir + '/SPECS/common-rpm.spec',buildid,commonrpmbuild,hostname,bcmd,collectivelog):
      systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/' + hostarch + '/common-rpm*.mvl ' + 
                cpdir + '/host/' + hostname,scripttest,collectivelog)
      if hostname == targethost:
        cpcmd = '%s %s%s/SRPMS/common-rpm* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
        systemCmd(cpcmd,scripttest)
        chroot(hostname,'rm -rf %s/SRPMS/*' % builddir,scripttest)
      if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'common*.mvl',commonrpmbin,hostname,collectivelog):
        printflush('BUILT: common-rpm for ' + hostname + ' built.',collectivelog,scripttest)
      else:
        printflush('BUILD ERROR: common-rpm for ' + hostname + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: common-rpm for ' + hostname + ' did not build.',collectivelog,scripttest)
    mstop('common-rpm',collectivelog,scripttest)
elif product not in ('mls','tsuki'):
  printflush('Installing (rpmc2cpio) previously built version of common-rpm...',collectivelog,scripttest)
  systemCmd('%s %s/build/host/%s/common-rpm* %s/%s/host/%s' % (cpall,foundation,hostname,chrootdir,chrootcpdir,hostname),scripttest,collectivelog)
  chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest,collectivelog)
  if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
    # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install
    printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio:",collectivelog,scripttest)
    systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
    systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
    printflush("try recopying common-rpm and re-installing...",collectivelog,scripttest)
    systemCmd('%s %s/build/host/%s/common-rpm* %s/%s/host/%s' % (cpall,foundation,hostname,chrootdir,chrootcpdir,hostname),scripttest,collectivelog)
    printflush('Installing (rpmc2cpio) previously built version of common-rpm a second time...',collectivelog,scripttest)
    chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest,collectivelog)
    if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
      # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install a second time
      printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio (2nd try):",collectivelog,scripttest)
      systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
      printflush("No use continuing the build...",collectivelog,scripttest)
      systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest)
      # don't use systemCmd here because we always want to touch this file so the builds 
      # can continue and don't wait for the file to be touched
      systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest)
      mstop('buildremotehost-setup',collectivelog,scripttest)
      printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
      if hostname == 'solaris8':
        if pid != None:
          os.kill(pid, signal.SIGTERM )
      sys.exit(1)
  # now use common-rpm to install common-rpm
  printflush("Using common-rpm to install common-rpm",collectivelog,scripttest)
  rdir = '%s/host/%s' % (chrootcpdir,hostname)
  rpminstall(chrootdir+rdir,rdir,'common-rpm*',commonrpmbin,hostname,collectivelog)
  mstop('buildremotehost-setup',collectivelog,scripttest)
else:
  mstop('buildremotehost-setup',collectivelog,scripttest)

# if there are no common-noarch apps to build, touch common-noarch-done
if 'common' not in noarchapps.keys():
  systemCmd('touch %s/common-noarch-done' % logdir,scripttest)

chroot(hostname,'mkdir -p ' + chrootcpdir + '/host/' + hostname,scripttest)
chroot(hostname,'mkdir -p ' + chrootcpdir + '/host/common',scripttest)
chroot(hostname,'mkdir -p ' + chrootcpdir + '/installer_rpms/host/' + hostname,scripttest)
getdiskspace(hostname)

# now, for all non-devrocket editions, build mvl-edition-rpm
if product not in ('devrocket','mls','tsuki','scripttest','cgeasync','mobiasync','proasync'):
  collectivelog = '%s/%s' % (collectivelogdir,'host-rpm')
  mstart('host-rpm',collectivelog,scripttest)
  # copy rpm SOURCES and SPECS 
  if 'userland' in cvspaths.keys() or scripttest == 1:
    systemCmd('%s %s/rpm/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['userland'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/rpm/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['userland'][0],chrootdir,builddir),scripttest,collectivelog)
  if hostname == 'solaris8':
    rpmspec = '--nodeps ' + builddir + '/SPECS/host-rpm.spec'
  else:
    rpmspec = builddir + '/SPECS/host-rpm.spec'
  if rpmb(rpmspec,buildid,commonrpmbuild,hostname,bcmd,collectivelog) or scripttest == 1:
    chroot(hostname,'cd /; ' + rpm2cpio + ' /home/build/RPMS/' + hostarch +'/host-rpm-* | cpio -iud',scripttest,collectivelog)
    if hostname == targethost:
      cpcmd = '%s %s%s/SRPMS/host-rpm* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
      systemCmd(cpcmd,scripttest)
      chroot(hostname,'rm -rf %s/SRPMS/*' % builddir,scripttest)
    cpcmd = '%s %s%s/RPMS/%s/host-rpm* %s/host/%s' % (cpall,chrootdir,builddir,hostarch,cpdir,hostname)
    systemCmd(cpcmd,scripttest)
    if hostname == 'solaris8':
      if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-rpm*.mvl --nodeps',editionrpmbin,hostname,collectivelog) or scripttest == 1:
        printflush('BUILT: host-rpm for ' + hostname + ' built.',collectivelog,scripttest)
      else:
        printflush('BUILD ERROR: host-rpm for ' + hostname + ' built but did not install.',collectivelog,scripttest)
    else:
      if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-rpm*.mvl',editionrpmbin,hostname,collectivelog) or scripttest == 1:
        printflush('BUILT: host-rpm for ' + hostname + ' built.',collectivelog,scripttest)
      else:
        printflush('BUILD ERROR: host-rpm for ' + hostname + ' built but did not install.',collectivelog,scripttest)
    chroot(hostname,'rm -rf %s/RPMS/%s/host-rpm*' % (builddir,hostarch),scripttest)
  else:
    printflush('BUILD ERROR: host-rpm for ' + hostname + ' did not build.',collectivelog,scripttest)
  mstop('host-rpm',collectivelog,scripttest)
elif product in ('devrocket','cgeasync','mobiasync','proasync'):
  # install host-* rpms
  collectivelog = '%s/%s' % (collectivelogdir,'host_rpms_install')
  mstart('host_rpms_install',collectivelog,scripttest)
  printflush('Installing host-* rpms...',collectivelog,scripttest)
  systemCmd('%s %s/build/host/%s/host-rpm* %s/%s/host/%s' % (cpall,foundation,hostname,chrootdir,chrootcpdir,hostname),scripttest,collectivelog)
  rdir = '%s/host/%s' % (chrootcpdir,hostname)
  if hostname != 'solaris8':
    chroot(hostname,'cd /; ' + rpm2cpio + ' /home/build/RPMS/install/host/' + hostname + '/host-rpm-* | cpio -iud',scripttest,collectivelog)
    rpminstall(chrootdir+rdir,rdir,'host-*',editionrpmbin,hostname,collectivelog)
  else:
    rdir = '/opt/montavista/packages'
    rpminstall(chrootdir+rdir,rdir,'host-tool*.mvl --ignoreos --justdb',commonrpmbin,hostname,collectivelog)
    rdir = '%s/host/%s' % (chrootcpdir,hostname)
    rpminstall(chrootdir+rdir,rdir,'host-* --ignoreos',editionrpmbin,hostname,collectivelog)
  mstop('host_rpms_install',collectivelog,scripttest)
getdiskspace(hostname)

# if host is targethost, build host-kernel rpm
if hostname == targethost and product not in ('devrocket','mls','tsuki','scripttest'):
  # copy kernel source 
  collectivelog = '%s/%s' % (collectivelogdir,'host-kernel')
  mstart('host-kernel',collectivelog,scripttest)
  if 'mvl-kernel-26' in cvspaths.keys():
    systemCmd('mkdir -p %s/%s/kernel/BUILD' % (chrootdir,builddir),scripttest,collectivelog)
    systemCmd('mkdir -p %s/%s/kernel/SRPMS' % (chrootdir,builddir),scripttest,collectivelog)
    systemCmd('mkdir -p %s/%s/kernel/RPMS' % (chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/SOURCES %s/%s/kernel' % (cpall,cvspaths['mvl-kernel-26'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/SPECS %s/%s/kernel' % (cpall,cvspaths['mvl-kernel-26'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/Makefile %s/%s/kernel' % (cpall,cvspaths['mvl-kernel-26'][0],chrootdir,builddir),scripttest,collectivelog)
    if lsptype == 'std':
      makecmd = 'make'
    else:
      makecmd = 'make LSPTYPE=%s' % lsptype
    makestr = "%s TOPDIR=%s/kernel BUILDID=%s HHL_VERSION=%s BASE_VERSION=%s NEW_SOURCE=yes RPM=%s all" % (
             makecmd,builddir,buildid, hhlversion, kernel, editionrpmbuild)
    chroot(hostname,'cd %s/kernel; %s' % (builddir,makestr),scripttest,collectivelog)
    if wrotecheck(hostname) or scripttest == 1:
      # install host-kernel for editon builds, so host-kernel-html will build
      if product in ('cge','pro','mobilinux'):
        rpminstall(chrootdir+builddir+'/kernel/RPMS/noarch',builddir + '/kernel/RPMS/noarch','host-kernel*.mvl',editionrpmbin,hostname,collectivelog)
      systemCmd(cpall + ' ' + chrootdir + builddir + '/kernel/RPMS/noarch/host-kernel*.mvl ' + 
                cpdir + '/host/common/optional',scripttest,collectivelog)
      systemCmd('rm -f ' + chrootdir + builddir + '/kernel/RPMS/noarch/host-kernel*.mvl')
      systemCmd(cpall + ' ' + chrootdir + builddir + '/kernel/SRPMS/host-kernel*.rpm ' + 
                cpdir + '/SRPMS',scripttest,collectivelog)
      systemCmd('rm -f ' + chrootdir + builddir + '/kernel/SRPMS/host-kernel*.rpm')
      systemCmd('mkdir -p %s/rpm' % cvspaths['mvl-kernel-26'][0],scripttest,collectivelog)
      systemCmd(cpall + ' ' + chrootdir + builddir + '/kernel/SOURCES ' + cvspaths['mvl-kernel-26'][0] + '/rpm',scripttest,collectivelog)
      systemCmd(cpall + ' ' + chrootdir + builddir + '/kernel/SPECS ' + cvspaths['mvl-kernel-26'][0] + '/rpm',scripttest,collectivelog)
      printflush("BUILT: host-kernel built.",collectivelog,scripttest)
    else:
      printflush("BUILD ERROR: host-kernel did not build.",collectivelog,scripttest)
  else:
    for repo in cvspaths.keys():
      if string.find(repo,'git-') > -1:
        systemCmd('%s %s %s/%s' % (cpall,cvspaths[repo][0],chrootdir,builddir),scripttest,collectivelog)
        if lsptype == 'std':
          makecmd = 'make'
        else:
          makecmd = 'make LSPTYPE=%s' % lsptype
        makestr = "%s BUILDID=%s RPM=%s mvl-host-kernel" % (makecmd,buildid,editionrpmbuild)
        chroot(hostname,'cd %s/%s; %s' % (builddir,cvspaths[repo][2],makestr),scripttest,collectivelog)
        if wrotecheck(hostname) or scripttest == 1:
          # install host-kernel for editon builds, so host-kernel-html will build
          if product in ('cge','pro','mobilinux'):
            rpminstall(chrootdir+builddir+'/'+cvspaths[repo][2]+'/MONTAVISTA-BUILD/RPMS/noarch',builddir+'/'+cvspaths[repo][2]+'/MONTAVISTA-BUILD/RPMS/noarch','host-kernel*.mvl',editionrpmbin,hostname,collectivelog)
          systemCmd(cpall + ' ' + chrootdir+builddir+'/'+cvspaths[repo][2]+'/MONTAVISTA-BUILD/RPMS/noarch/host-kernel*.mvl ' + cpdir + '/host/common/optional',scripttest,collectivelog)
          systemCmd(cpall + ' ' + chrootdir+builddir+'/'+cvspaths[repo][2]+'/MONTAVISTA-BUILD/SRPMS/host-kernel*.rpm ' + cpdir + '/SRPMS',scripttest,collectivelog)
          systemCmd('mv %s %s-old' % (cvspaths[repo][0],cvspaths[repo][0]),scripttest,collectivelog)
          systemCmd(cpall + ' ' + chrootdir+builddir+'/'+cvspaths[repo][2]+' ' + cvspaths[repo][0],scripttest,collectivelog)
          systemCmd('rm -rf ' + chrootdir+builddir+'/'+cvspaths[repo][2],scripttest,collectivelog)
          printflush("BUILT: host-kernel built.",collectivelog,scripttest)
        else:
          printflush("BUILD ERROR: host-kernel did not build.",collectivelog,scripttest)
  mstop('host-kernel',collectivelog,scripttest)
getdiskspace(hostname)

# if host is targethost, build noarch rpms, otherwise wait for
# noarch rpms to finish (look for done file).
srcpath = ""
if hostname == targethost and product not in ('mls','tsuki') and noarchapps:
  # if an edition build, copy and install the noarch rpms from foundation
  if product not in ('dev','fe'):
    collectivelog = '%s/%s' % (collectivelogdir,'noarch_rpms_install')
    mstart('noarch_rpms_install',collectivelog,scripttest)
    rdir = '%s/host/common' % chrootcpdir
    makeDir('%s/%s' % (chrootdir,rdir),scripttest)
    # copy and install common-* noarch rpms, like common-autoconf, etc.
    systemCmd('%s %s/host/common/common-* %s/%s' % (cpall,cpdir,chrootdir,rdir),scripttest,collectivelog)
    systemCmd('ls -la ' + chrootdir+rdir,scripttest,collectivelog)
    if hostname != "solaris8":
      rpminstall(chrootdir+rdir,rdir,'common-*',commonrpmbin,hostname,collectivelog)
    else:
      rpminstall(chrootdir+rdir,rdir,'common-* --ignoreos',commonrpmbin,hostname,collectivelog)
    # copy and install host-* noarch rpms
    systemCmd('%s %s/host/common/host-* %s/%s' % (cpall,cpdir,chrootdir,rdir),scripttest,collectivelog)
    systemCmd('ls -la ' + chrootdir+rdir,scripttest,collectivelog)
    if hostname != "solaris8":
      rpminstall(chrootdir+rdir,rdir,'host-*',editionrpmbin,hostname,collectivelog)
    else:
      rpminstall(chrootdir+rdir,rdir,'host-* --ignoreos',editionrpmbin,hostname,collectivelog)
    mstop('noarch_rpms_install',collectivelog,scripttest)
  # now build the common & host noarch rpms for all builds
  printflush("Building noarch apps")
  for type in noarchapps.keys():
    printflush("Building %s noarch apps..." % type)
    if type == 'common':
      rpmbuild = commonrpmbuild
      rpmbin = commonrpmbin
    elif type == 'host':
      rpmbuild = editionrpmbuild
      rpmbin = editionrpmbin
    for noarchapp in noarchapps[type]:
      tmpbcmd = bcmd
      srcpath = 'null'
      if noarchapp == 'devrocket-cd-installer':
        if 'mvl-installer' in cvspaths.keys():
          srcpath = cvspaths['mvl-installer'][0]
        spec = 'devrocket-cd-installer'
        instrpm = spec
      elif noarchapp == 'docs-cd-installer':
        if 'mvl-installer' in cvspaths.keys():
          srcpath = cvspaths['mvl-installer'][0]
        spec = 'docs-cd-installer'
        instrpm = spec
      elif noarchapp == 'eclipse-edition':
        if 'userland' in cvspaths.keys():
          srcpath = cvspaths['userland'][0] + '/eclipse-templates'
        spec = type + '-' + noarchapp
        instrpm = type + '-eclipse-enabler-edition'
      elif noarchapp == 'apt-rpm-config' and aptedition:
        tmpbcmd = tmpbcmd + ' --define \\"_edition ' + aptedition + '\\" '
      elif noarchapp == 'kernel-html':
        if 'userland' in cvspaths.keys():
          srcpath = cvspaths['userland'][0] + '/' + noarchapp
        systemCmd('%s %s/host/common/common-db2html*.mvl %s/%s' % (cpall,cpdir,chrootdir,builddir),scripttest)
        rpminstall(chrootdir+builddir+'/',builddir + '/','common-db2html*.mvl',rpmbin,hostname)
        systemCmd('rm -f %s/%s/common-db2html*.mvl' % (chrootdir,builddir),scripttest)
        spec = type + '-' + noarchapp
        instrpm = spec
        tmpbcmd = '-ba --define \\"_mvl_kernel_base_version ' + kernel + '\\" --define \\"_mvl_kernel_mvl_version ' + hhlversion + '\\"'
      else:
        if 'userland' in cvspaths.keys() or scripttest == 1:
          srcpath = cvspaths['userland'][0] + '/' + noarchapp
        spec = type + '-' + noarchapp
        instrpm = spec
      if os.path.exists(srcpath) or scripttest == 1:
        collectivelog = '%s/%s' % (collectivelogdir,spec)
        mstart(spec,collectivelog,scripttest)
        if noarchapp == 'eclipse-templates':
          systemCmd('mkdir -p %s/%s/eclipse-templates/SOURCES' % (chrootdir,builddir),scripttest,collectivelog)
          systemCmd('mkdir -p %s/%s/eclipse-templates/SPECS' % (chrootdir,builddir),scripttest,collectivelog)
          systemCmd('%s %s/SOURCES/* %s/%s/eclipse-templates/SOURCES' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
          systemCmd('%s %s/SPECS/* %s/%s/eclipse-templates/SPECS' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
          etversion = string.strip(os.popen('sudo chroot /chroot/%s /bin/su - build -c "%s"' % 
                                  (hostname,rpmbin + ' --eval "%_mvl_edition_version"')).read())
          chroot(hostname,'cd %s/eclipse-templates; make -C %s/eclipse-templates -f SOURCES/Makefile EDITION=%s BUILDID=%s VERSION=%s all' % (builddir,builddir,edition,buildid,etversion),scripttest,collectivelog)
          systemCmd('%s %s/%s/eclipse-templates/SOURCES/* %s/SOURCES' % 
                   (cpall,chrootdir,builddir,srcpath),scripttest,collectivelog)
          systemCmd('%s %s/%s/eclipse-templates/SPECS/* %s/SPECS' % 
                   (cpall,chrootdir,builddir,srcpath),scripttest,collectivelog)
          getdiskspace(hostname)
          removeDir('%s/%s/eclipse-templates' % (chrootdir,builddir))
        systemCmd('%s %s/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
        systemCmd('%s %s/SPECS/* %s/%s/SPECS' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
        if rpmb(builddir + '/SPECS/' + spec + '.spec',buildid,rpmbuild,hostname,tmpbcmd,collectivelog) or scripttest == 1:
          if noarchapp not in ('devrocket-cd-installer','docs-cd-installer','gettext','mvlutils'):
            cpcmd = '%s %s%s/SRPMS/* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
            systemCmd(cpcmd,scripttest)
            chroot(hostname,'rm -rf %s/SRPMS/*' % builddir,scripttest)
            if not rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir + '/RPMS/noarch',instrpm + '*.mvl',rpmbin,hostname,collectivelog):
              printflush('BUILT: ' + spec + ' built.',collectivelog,scripttest)
            else:
              printflush('BUILD ERROR: ' + spec + ' built but did not install.',collectivelog,scripttest)
          elif noarchapp not in ('devrocket-cd-installer','docs-cd-installer'):
            cpcmd = '%s %s%s/SRPMS/* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
            systemCmd(cpcmd,scripttest)
            chroot(hostname,'rm -rf %s/SRPMS/*' % builddir,scripttest)
            if not rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir + '/RPMS/'+hostarch,instrpm + '*.mvl',rpmbin,hostname,collectivelog):
              printflush('BUILT: ' + spec + ' built.',collectivelog,scripttest)
            else:
              printflush('BUILD ERROR: ' + spec + ' built but did not install.',collectivelog,scripttest)
          if noarchapp == 'apache-ant':
            systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/noarch/' + instrpm + '*.mvl ' + 
                      cpdir + '/host/common',scripttest,collectivelog)
          elif noarchapp in ('gettext','mvlutils'):
            systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/'+hostarch+'/' + instrpm + '*.mvl ' + 
                      cpdir + '/host/'+hostname,scripttest,collectivelog)
          elif noarchapp == 'devrocket-cd-installer':
            systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/noarch/' + instrpm + '*.mvl ' + 
                      cpdir + '/installer_rpms/common',scripttest,collectivelog)
          elif noarchapp == 'docs-cd-installer':
            systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/noarch/' + instrpm + '*.mvl ' + 
                      cpdir + '/installer_rpms/docs-cd',scripttest,collectivelog)
          else:
            systemCmd(cpall + ' ' + chrootdir + builddir + '/RPMS/noarch/' + instrpm + '*.mvl ' + 
                      cpdir + '/host/common',scripttest,collectivelog)
          chroot(hostname,'rm -rf %s/RPMS/noarch/*' % builddir,scripttest)
          chroot(hostname,'rm -rf %s/RPMS/%s/*' % (builddir,hostarch),scripttest)
        else:
          printflush('BUILD ERROR: ' + spec + ' did not build.',collectivelog,scripttest)
        #os.system('rm -f %s/%s/SPECS/* %s/%s/SOURCES/*' % (chrootdir,builddir,chrootdir,builddir))
        getdiskspace(hostname)
        mstop(spec,collectivelog,scripttest)
  # build host src rpms for windows only apps
  winsrcapps = ()
  if product in ('dev','fe',):
    winsrcapps = ('postinstall',)
  elif product in ('cge','mobilinux','pro',) and 's124' not in buildtag:
    winsrcapps = ('postinstall',)
  if winsrcapps:
    for srcapp in winsrcapps:
      if 'userland' in cvspaths.keys() or scripttest == 1:
        srcpath = cvspaths['userland'][0] + '/' + srcapp
      else:
        srcpath = 'null'
      collectivelog = '%s/host-%s-src' % (collectivelogdir,srcapp)
      mstart('host-' + srcapp + '-src',collectivelog,scripttest)
      if os.path.exists(srcpath) or scripttest == 1:
        systemCmd('%s %s/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
        systemCmd('%s %s/SPECS/* %s/%s/SPECS' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
        if rpmb(builddir + '/SPECS/host-' + srcapp + '.spec',buildid,editionrpmbuild,hostname,'bs',collectivelog):
          cpcmd = '%s %s%s/SRPMS/* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
          systemCmd(cpcmd,scripttest)
          chroot(hostname,'rm -rf %s/SRPMS/*' % builddir,scripttest)
          printflush('BUILT: host-' + srcapp + '-src built.',collectivelog,scripttest)
        else:
          printflush('BUILD ERROR: host-' + srcapp + '-src did not build.',collectivelog,scripttest)
      else:
        printflush('BUILD ERROR: host-' + srcapp + '-src did not build...no spec file',collectivelog,scripttest)
      mstop('host-' + srcapp + '-src',collectivelog,scripttest)
  systemCmd('touch %s/common-noarch-done' % logdir,scripttest)
elif product in ('cgeasync','mobiasync','proasync'):
  systemCmd('touch %s/common-noarch-done' % logdir,scripttest)
elif product not in ('mls','tsuki'):
  collectivelog = '%s/%s' % (collectivelogdir,'common_noarch_pause')
  mstart('common_noarch_pause',collectivelog,scripttest)
  printflush("Waiting for common noarch rpms to build...",collectivelog,scripttest)
  waitcheck = 0
  if scripttest in (1,):
    systemCmd('touch %s/common-noarch-done' % logdir,scripttest,collectivelog)
  while not os.path.exists('%s/common-noarch-done' % logdir) and scripttest != 1:
    waitcheck += 1
    systemCmd('sleep 300',scripttest,collectivelog)
    if waitcheck > 48:
      printflush('waited 2 hrs for common-noarch-done, something must be wrong, stopping build.',collectivelog,scripttest)
      systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest,collectivelog)
      printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
      mstop('common_noarch_pause',collectivelog,scripttest)
      if hostname == 'solaris8':
        if pid != None:
          os.kill(pid, signal.SIGTERM )
      sys.exit(1)
  mstop('common_noarch_pause',collectivelog,scripttest)
  # copy and install common-* noarch rpms, like common-autoconf, etc.
  collectivelog = '%s/%s' % (collectivelogdir,'noarch_install')
  mstart('noarch_install',collectivelog,scripttest)
  printflush("Common noarch rpms finished, copying and installing at " + gettime() + "...",collectivelog,scripttest)
  rdir = '%s/host/common' % chrootcpdir
  makeDir('%s/%s' % (chrootdir,rdir),scripttest)
  systemCmd('%s %s/host/common/common-* %s/%s' % (cpall,cpdir,chrootdir,rdir),scripttest,collectivelog)
  systemCmd('ls -la ' + chrootdir+rdir,scripttest,collectivelog)
  if hostname != "solaris8":
    rpminstall(chrootdir+rdir,rdir,'common-*',commonrpmbin,hostname,collectivelog)
  else:
    rpminstall(chrootdir+rdir,rdir,'common-* --ignoreos',commonrpmbin,hostname,collectivelog)
  systemCmd('%s %s/host/common/host-* %s/%s' % (cpall,cpdir,chrootdir,rdir),scripttest,collectivelog)
  systemCmd('ls -la ' + chrootdir+rdir,scripttest,collectivelog)
  if hostname != "solaris8":
    rpminstall(chrootdir+rdir,rdir,'host-*',editionrpmbin,hostname,collectivelog)
  else:
    rpminstall(chrootdir+rdir,rdir,'host-* --ignoreos',editionrpmbin,hostname,collectivelog)
  # install common-* rpms
  if hostname == "solaris8":
    #rdir = '%s/host/solaris8' % (chrootcpdir)
    #os.system('%s %s/host/solaris8/common-* %s/%s' % (cpall,cpdir,chrootdir,rdir))
    #rpminstall(chrootdir+rdir,rdir,'common-* --ignoreos',commonrpmbin,hostname,collectivelog)
    printflush("installing common hostarch rpsm with --justdb",collectivelog,scripttest)
    rdir = '/opt/montavista/packages'
    rpminstall(chrootdir+rdir,rdir,'host-tool-*.mvl --ignoreos --justdb',commonrpmbin,hostname,collectivelog)
  mstop('noarch_install',collectivelog,scripttest)
getdiskspace(hostname)

# for edition builds, copy and install the common- rpms from foundation
if product not in ('dev','fe','mls','tsuki','scripttest'):
  collectivelog = '%s/%s' % (collectivelogdir,'hostarch_install')
  mstart('hostarch_install',collectivelog,scripttest)
  rdir = '%s/host/%s' % (chrootcpdir,hostname)
  systemCmd('%s %s/host/%s/common-* %s/%s' % (cpall,cpdir,hostname,chrootdir,rdir),scripttest,collectivelog)
  systemCmd('rm -f %s/%s/common-rpm*' % (chrootdir,rdir),scripttest,collectivelog)
  if hostname != "solaris8":
    rpminstall(chrootdir+rdir,rdir,'common-*',commonrpmbin,hostname,collectivelog)
  else:
    rpminstall(chrootdir+rdir,rdir,'common-* --ignoreos',commonrpmbin,hostname,collectivelog)
  mstop('hostarch_install',collectivelog,scripttest)

# now build common- hostarch rpms
#if product in ('dev','devrocket','fe'):
if product not in ('mls','tsuki') and commonapps:
  userbuilt = 0
  toolbuilt = 0
  licensingbuilt = 0
  devrocketbuilt = 0
  for commonappkey in commonapps.keys():
    # here's some hackery to make sure that userland apps build before toolchain apps
    # this was done because the toolchain app (elfutils) requires mvlutils (from userland)
    # and python dictionaries don't get key in order they appear in the definition but can be
    # random (the data.dat files have userland listed first and toolchain listed last, but the
    # toolchain apps were being built first...stupid python
    #
    # this same thing had to be done for licensing and devrocket repos
    if commonappkey == 'toolchain' and not userbuilt:
      commonappkey = 'userland'
      userbuilt = 1
    elif commonappkey == 'userland' and not toolbuilt and userbuilt:
      commonappkey = 'toolchain'
      toolbuilt = 1
    elif commonappkey == 'userland':
      userbuilt = 1
    if commonappkey == 'devrocket' and not licensingbuilt:
      commonappkey = 'licensing'
      licensingbuilt = 1
    elif commonappkey == 'licensing' and not devrocketbuilt and licensingbuilt:
      commonappkey = 'devrocket'
      devrocketbuilt = 1
    elif commonappkey == 'licensing':
      licensingbuilt = 1
    if commonappkey in cvspaths.keys():
      srcpath = cvspaths[commonappkey][0]
    else:
      srcpath = 'null'
    for cpr in commonapps[commonappkey]:
      if cpr in commonExcludes:
        continue
      elif hostname == targethost and cpr in ('gettext','mvlutils'):
        continue
      if cpr not in ('binutils','devrocket'):
        systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,cpr,chrootdir,builddir),scripttest)
        systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,srcpath,cpr,chrootdir,builddir),scripttest)
      elif cpr == 'binutils':
        systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],cpr,chrootdir,builddir),scripttest)
        systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],cpr,chrootdir,builddir),scripttest)
      elif cpr == 'devrocket':
        if not os.path.exists('%s/devrocket-buildsh-done' % logdir) and not os.path.exists('%s/devrocket-buildsh-inprogress' % logdir):
          os.system('touch %s/devrocket-buildsh-inprogress' % logdir)
          if product in ('dev','fe','devrocket'):
            printflush('<' + sys.argv[0] + '>: building build_sh at ' + gettime() + '...')
            if 'devrocket' in cvspaths.keys():
              printflush('checking for build directory (' + cvspaths['devrocket'][0] + '/build)')
            if os.path.exists(srcpath + '/build'):
              systemCmd('%s %s %s/%s' % (cpall,srcpath,chrootdir,builddir),scripttest)
              cmd = '%s/devrocket/build/build.sh -cvsroot=:file:%s/devrocket -installdir=%s -tag=%s -release=%s -rpmdir=%s/devrocket/rpm -os=linux -ws=gtk' % (builddir,builddir,builddir + '/common-eclipse-root',buildtag,buildid,builddir)
              chroot(hostname,'cd %s/devrocket; %s' % (builddir,cmd),scripttest)
              if os.path.exists('%s/%s/devrocket/rpm/SPECS/common-devrocket.spec' % (chrootdir,builddir)):
                printflush("copying SOURCES and SPECS to /home/build...")
                if 'devrocket' in cvspaths.keys():
                  systemCmd('%s %s/%s/devrocket/rpm %s' % (cpall,chrootdir,builddir,cvspaths['devrocket'][0]),scripttest)
                else:
                  printflush("couldn't copy results of build.sh...check for devrocket in cvspaths.keys()")
                printflush("removing devrocket repo...SOURCES and SPECS will be copied for build")
                getdiskspace(hostname)
                removeDir('%s/%s/devrocket' % (chrootdir,builddir))
                printflush("BUILT: build_sh ran successfully on %s" % hostname)
              else:
                printflush("BUILD ERROR: build_sh failed on %s" % hostname)
                if product == 'devrocket':
                  printflush('<' + sys.argv[0] + '>: finished build_sh at ' + gettime() + '...')
                  systemCmd('rm -f %s/devrocket-buildsh-inprogress' % logdir,scripttest)
                  os.system('touch %s/devrocket-buildsh-done' % logdir)
                  if hostname == 'solaris8':
                    if pid != None:
                      os.kill(pid, signal.SIGTERM )
                  sys.exit(1)
            else:
              printflush("BUILD ERROR: path " + srcpath + "/build does not exist")
            printflush('<' + sys.argv[0] + '>: finished build_sh at ' + gettime() + '...')
            systemCmd('rm -f %s/devrocket-buildsh-inprogress' % logdir,scripttest)
            os.system('touch %s/devrocket-buildsh-done' % logdir)
        if not os.path.exists('%s/devrocket-buildsh-done' % logdir):
          waitcheck = 0
          while os.path.exists('%s/devrocket-buildsh-inprogress' % logdir):
            printflush("Waiting for devrocket build.sh to finish...")
            waitcheck += 1
            systemCmd('sleep 300',scripttest)
            if waitcheck > 24:
              printflush('waited 2 hrs for devrocket-buildsh-inprogress, something must be wrong, stopping build.')
              os.system('touch %s/buildremotehost-%s-done' % (logdir,hostname))
              printflush("Finished %s at %s" % (sys.argv[0],gettime()))
              if hostname == 'solaris8':
                if pid != None:
                  os.kill(pid, signal.SIGTERM )
              sys.exit(1)
        systemCmd('%s %s/rpm/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,chrootdir,builddir),scripttest)
        systemCmd('%s %s/rpm/SPECS/* %s/%s/SPECS' % (cpall,srcpath,chrootdir,builddir),scripttest)
      if cpr == 'binutils':
        cpr = 'host-tool-binutils'
      else:
        cpr = 'common-' + cpr
      tmpbcmd = bcmd
      if cpr == 'common-apt-rpm-config' and aptedition:
        tmpbcmd = tmpbcmd + ' --define \\"_edition ' + aptedition + '\\" '
      collectivelog = '%s/%s' % (collectivelogdir,cpr)
      mstart(cpr,collectivelog,scripttest)
      # install common-jdk rpms if building common-staf
      #if cpr == 'staf':
        #os.system('%s %s/common/%s/common-jdk* %s/%s' % (cpall,cpdir,hostname,chrootdir,builddir))
        #os.system('%s %s/host/%s/common-jdk* %s/%s' % (cpall,cpdir,hostname,chrootdir,builddir))
        #if hostname != "solaris8":
        #  rpminstall(chrootdir+builddir,builddir,'common-*',commonrpmbin,hostname)
        #else:
        #  rpminstall(chrootdir+builddir,builddir,'common-* --ignoreos',commonrpmbin,hostname)
        #getdiskspace(hostname)
        #os.system('rm -f %s/%s/common-jdk*' % (chrootdir,builddir))
      #if cpr == 'jdk' and hostname != targethost:
      #  rpminstall(chrootdir+chrootcpdir,chrootcpdir,'common-apache*.mvl',commonrpmbin,hostname)
      #if cpr == 'devrocket':
      #  rpminstall(chrootdir+chrootcpdir,chrootcpdir,'common-flexnet-sdk*.mvl',commonrpmbin,hostname)
      if rpmb(builddir + '/SPECS/' + cpr + '.spec',buildid,commonrpmbuild,hostname,tmpbcmd,collectivelog) or scripttest == 1:
        # remove the first if here when common-python will install on solaris 
        # (when bug 13684 is fixed).
        if cpr == 'common-python' and hostname == 'solaris8':
          if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,cpr + '*.mvl --justdb --nodeps',commonrpmbin,hostname,collectivelog):
            printflush('BUILT: ' + cpr + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: ' + cpr + ' built but did not install.',collectivelog,scripttest)
          systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + cpr + '*.mvl ' + 
                    chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
        elif cpr not in ('common-staf',):
          if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,cpr + '*.mvl',commonrpmbin,hostname,collectivelog):
            printflush('BUILT: ' + cpr + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: ' + cpr + ' built but did not install.',collectivelog,scripttest)
          systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + cpr + '*.mvl ' + 
                    chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
        elif cpr == 'common-staf':
          if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,cpr + '*.mvl',commonrpmbin,hostname,collectivelog):
            printflush('BUILT: ' + cpr + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: ' + cpr + ' built but did not install.',collectivelog,scripttest)
          systemCmd('mkdir -p %s%s/host/%s/testing' % (chrootdir,chrootcpdir,hostname),scripttest,collectivelog)
          systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + cpr + '*.mvl ' + 
                    chrootdir + chrootcpdir + '/host/' + hostname + '/testing',scripttest,collectivelog)
        else:
          if not rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir + '/RPMS/noarch',cpr + '*.mvl',commonrpmbin,hostname,collectivelog):
            printflush('BUILT: ' + cpr + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: ' + cpr + ' built but did not install.',collectivelog,scripttest)
          systemCmd('mv ' + chrootdir + builddir + '/RPMS/noarch/' + cpr + '*.mvl ' + 
                    chrootdir + chrootcpdir + '/host/' + hostname + '/testing',scripttest,collectivelog)
      else:
        printflush('BUILD ERROR: ' + cpr + ' did not build.',collectivelog,scripttest)
      mstop(cpr,collectivelog,scripttest)
getdiskspace(hostname)

# for edition builds, install the host- rpms from foundation
if product not in ('dev','fe','mls','tsuki'):
  collectivelog = '%s/%s' % (collectivelogdir,'host_hostarch_install')
  mstart('host_hostarch_install',collectivelog,scripttest)
  rdir = '%s/host/%s' % (chrootcpdir,hostname)
  if product != 'scripttest':
    systemCmd('%s %s/host/%s/host-* %s/%s' % (cpall,cpdir,hostname,chrootdir,rdir),scripttest,collectivelog)
    systemCmd('rm -f %s/%s/host-rpm*' % (chrootdir,rdir),scripttest,collectivelog)
  if hostname != "solaris8":
    rpminstall(chrootdir+rdir,rdir,'host-*',editionrpmbin,hostname,collectivelog)
  else:
    rpminstall(chrootdir+rdir,rdir,'host-* --ignoreos',editionrpmbin,hostname,collectivelog)
  mstop('host_hostarch_install',collectivelog,scripttest)

if os.path.exists(chrootdir + builddir + '/RPMS/' + hostarch):
  for hf in os.listdir(chrootdir + builddir + '/RPMS/' + hostarch):
    #print 'found ' + hf + ' in RPMS/' + hostarch
    #print 'copying ' + hf + ' to ' + chrootcpdir + '/host/' + hostname
    systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' + chrootdir + chrootcpdir + '/host/' + hostname,scripttest)
getdiskspace(hostname)

#---------------------------------
# Build the necessary RPMS
#---------------------------------
# build all host apps
for hk in hostapps.keys():
  if hk in cvspaths.keys():
    srcpath = cvspaths[hk][0]
  else:
    srcpath = 'null'
  for h in hostapps[hk]:
    if h in ('lesstif','tool-perl') and hostname == 'solaris8':
      continue
    if h == 'tool-perl':
      srcmodule = 'perl'
    elif h == 'elfmbind':
      srcmodule = 'numactl'
    else:
      srcmodule = h
    tmpbcmd = bcmd
    if h == 'apt-rpm-config' and aptedition:
      tmpbcmd = tmpbcmd + ' --define \\"_edition ' + aptedition + '\\" '
    collectivelog = '%s/host-%s' % (collectivelogdir,h)
    mstart('host-' + h,collectivelog,scripttest)
    systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,srcmodule,chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,srcpath,srcmodule,chrootdir,builddir),scripttest,collectivelog)
    if os.path.exists(chrootdir + builddir + '/SPECS/host-' + h + '.spec') or scripttest == 1:
      if rpmb(builddir + '/SPECS/host-' + h + '.spec',buildid,editionrpmbuild,hostname,tmpbcmd,collectivelog) or scripttest == 1:
        if h == 'ddd-redhat7x':
          if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-ddd*.mvl',editionrpmbin,hostname,collectivelog):
            printflush('BUILT: host-' + h + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: host-' + h + ' built but did not install.',collectivelog,scripttest)
        elif h not in ['dhcp-previewkit','mkimage-previewkit','tftp-hpa-previewkit','tsload-previewkit','zsrec-previewkit']:
          printflush(' Installing RPMS/' + hostarch + '/host-' + h + '*.mvl...',collectivelog,scripttest)
          if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-' + h + '*.mvl',editionrpmbin,hostname,collectivelog) or scripttest == 1:
            if h == 'e2fsprogs':
              if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-comerr-dev*.mvl',editionrpmbin,hostname,collectivelog) or scropttest == 1:
                if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-ss-dev*.mvl',editionrpmbin,hostname,collectivelog) or scripttest == 1:
                  if not rpminstall(chrootdir+builddir+'/RPMS/' + hostarch,builddir + '/RPMS/' + hostarch,'host-uuid-dev*.mvl',editionrpmbin,hostname,collectivelog) or scripttest == 1:
                    printflush('BUILT: host-' + h + ' built.',collectivelog,scripttest)
                  else:
                    printflush('BUILD ERROR: host-' + h + ' built but did not install.',collectivelog,scripttest)
                else:
                  printflush('BUILD ERROR: host-' + h + ' built but did not install.',collectivelog,scripttest)
              else:
                printflush('BUILD ERROR: host-' + h + ' built but did not install.',collectivelog,scripttest)
            else:
              printflush('BUILT: host-' + h + ' built.',collectivelog,scripttest)
          else:
            printflush('BUILD ERROR: host-' + h + ' built but did not install.',collectivelog,scripttest)
        if os.path.exists(chrootdir + builddir + '/RPMS/' + hostarch):
          for hf in os.listdir(chrootdir + builddir + '/RPMS/' + hostarch):
            #print 'found ' + hf + ' in RPMS/' + hostarch
            if string.find(hf,'host-' + h) > -1 or string.find(hf,'host-arts') > -1:
              if product == 'cge':
                if string.find(hf,'host-tool-perl') > -1 or string.find(hf,'host-expat') > -1 or string.find(hf,'host-perl-XML-Parser') > -1:
                  makeDir(chrootdir + chrootcpdir + '/host/' + hostname + '/optional/',scripttest)
                  printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname + '/optional/ ',collectivelog,scripttest)
                  getdiskspace(hostname)
                  systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                       chrootdir + chrootcpdir + '/host/' + hostname + '/optional/ ',scripttest,collectivelog)
                else:
                  printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
                  getdiskspace(hostname)
                  systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                             chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
              else:
                printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
                getdiskspace(hostname)
                systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' + 
                           chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
            elif string.find(hf,'host-comerr-dev') > -1:
              printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
              getdiskspace(hostname)
              systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                         chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
            elif string.find(hf,'host-e2fslibs-dev') > -1:
              printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
              getdiskspace(hostname)
              systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                         chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
            elif string.find(hf,'host-ss-dev') > -1:
              printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
              getdiskspace(hostname)
              systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                         chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
            elif string.find(hf,'host-uuid-dev') > -1:
              printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
              getdiskspace(hostname)
              systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                         chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
            elif string.find(hf,'host-ddd') > -1 and h == 'ddd-redhat7x':
              printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
              getdiskspace(hostname)
              systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/' + hf + ' ' +
                         chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
      else:
        printflush('BUILD ERROR: host-' + h + ' did not build.',collectivelog,scripttest)
      mstop('host-' + h,collectivelog,scripttest)
    elif os.path.exists(chrootdir + builddir + '/SPECS/mvl-host-' + h + '.spec'):
      collectivelog = '%s/mvl-host-%s' % (collectivelogdir,h)
      mstart('mvl-host-' + h,collectivelog,scripttest)
      if rpmb(builddir + '/SPECS/mvl-host-' + h + '.spec',buildid,editionrpmbuild,hostname,bcmd,collectivelog):
        printflush('BUILT: mvl-host-' + h + ' built.',collectivelog,scripttest)
        if os.path.exists(chrootdir + builddir + '/RPMS/' + hostarch):
          for hf in os.listdir(chrootdir + builddir + '/RPMS/' + hostarch):
            #print 'found ' + hf + ' in RPMS/' + hostarch
            if string.find(hf,'mvl-host-' + h) > -1:
                printflush('moving ' + hf + ' to ' + chrootcpdir + '/host/' + hostname,collectivelog,scripttest)
                getdiskspace(hostname)
                systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch +'/' + hf + ' ' +
                           chrootdir + chrootcpdir + '/host/' + hostname,scripttest,collectivelog)
      else:
        printflush('BUILD ERROR: mvl-host-' + h + ' did not build.',collectivelog,scripttest)
      mstop('mvl-host-' + h,collectivelog,scripttest)
    elif not os.path.exists(chrootdir + builddir + '/SPECS/host-' + h + '.spec'):
      collectivelog = '%s/%s' % (collectivelogdir,h)
      mstart(h,collectivelog,scripttest)
      printflush('BUILD ERROR: ' + h + ' is missing a host- spec file...skipping the build.',collectivelog,scripttest)
      mstop(h,collectivelog,scripttest)
getdiskspace(hostname)
# building mvl-installer host
if 'mvl-installer' in cvspaths.keys() and cvspaths['mvl-installer'][0] != 'skip' and product not in ('devrocket','proasync','bst') or scripttest == 1:
  systemCmd('%s %s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['mvl-installer'][0],chrootdir,builddir),scripttest)
  systemCmd('%s %s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['mvl-installer'][0],chrootdir,builddir),scripttest)
  if os.path.exists(chrootdir + builddir + '/SPECS/host-cd-installer.spec') or scripttest == 1:
    collectivelog = '%s/%s' % (collectivelogdir,'host-cd-installer')
    mstart('host-cd-installer',collectivelog,scripttest)
    if rpmb('--define \\"_os_dir ' + hostname + '\\" ' +
                   builddir + '/SPECS/host-cd-installer.spec',buildid,editionrpmbuild,hostname,bcmd,collectivelog):
      printflush('BUILT: host-cd-installer built.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: host-cd-installer did not build.',collectivelog,scripttest)
    mstop('host-cd-installer',collectivelog,scripttest)
  if os.path.exists(chrootdir + builddir + '/SPECS/host-mvlinstaller.spec') or scripttest == 1:
    collectivelog = '%s/%s' % (collectivelogdir,'host-mvl-installer')
    mstart('host-mvlinstaller',collectivelog,scripttest)
    if rpmb('--define \\"_os_dir ' + hostname + '\\" ' + builddir + '/SPECS/host-mvlinstaller.spec',
            buildid,editionrpmbuild,hostname,bcmd,collectivelog):
      printflush('BUILT: host-mvlinstaller built.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: host-mvlinstaller did not build.',collectivelog,scripttest)
    mstop('host-mvlinstaller',collectivelog,scripttest)
getdiskspace(hostname)

# build tsuki
if product == 'tsuki':
  collectivelog = '%s/%s' % (collectivelogdir,'tsuki')
  mstart('tsuki',collectivelog,scripttest)
  systemCmd('%s /home/build/MV_Java_Key %s/%s' % (cpall,chrootdir,builddir),scripttest,collectivelog)
  systemCmd('%s %s %s/%s' % (cpall,cvspaths['tsuki'][0],chrootdir,builddir),scripttest,collectivelog)
  tsukipath = 'tsuki/releng/com.mvista.releng.builder'
  fulltsukipath = '%s/%s/%s' % (chrootdir,builddir,tsukipath)
  chroot(hostname,"cd %s/scripts; ./mvbuild.sh" % tsukipath,scripttest,collectivelog)
  mstop('tsuki',collectivelog,scripttest)
  # aggregate on dev_area
  collectivelog = '%s/%s' % (collectivelogdir,'tsuki-deployUpdateSite')
  mstart('tsuki-deployUpdateSite',collectivelog,scripttest)
  # don't use JAVA_HOME since java has been added to PATH on all nodes
  #os.system('export JAVA_HOME=/usr/java/j2sdk1.4.1_01; export PATH=$PATH:$JAVA_HOME; ant -f %s/scripts/mv-build.xml deployUpdateSite -Dsrc.updatedir=%s/results/updateSite -Dsrc.scriptdir=%s/scripts/internal_scripts -Ddeploy.updatedir=/mvista/dev_area/tsuki/1.0 -Ddeploy.scriptdir=/mvista/dev_area/tsuki/1.0/scripts' % (fulltsukipath,fulltsukipath,fulltsukipath))
  systemCmd('ant -f %s/scripts/mv-build.xml deployUpdateSite -Dsrc.updatedir=%s/results/updateSite -Dsrc.scriptdir=%s/scripts/internal_scripts -Ddeploy.updatedir=%s/%s -Ddeploy.scriptdir=%s/%s/scripts' % (fulltsukipath,fulltsukipath,fulltsukipath,copydir,version,copydir,version),scripttest,collectivelog)
  mstop('tsuki-deployUpdateSite',collectivelog,scripttest)
elif product == 'mls':
  collectivelog = '%s/%s' % (collectivelogdir,'license_server')
  mstart('license_server',collectivelog,scripttest)
  systemCmd('%s %s %s/%s' % (cpall,cvspaths['licensing'][0],chrootdir,builddir),scripttest,collectivelog)
  chroot(hostname,"cd licensing; install/create_mls_installer %s %s %s" % (buildid,builddir + '/licensing',builddir + '/RPMS'),scripttest,collectivelog)
  mstop('license_server',collectivelog,scripttest)
getdiskspace(hostname)

# copy rpms to dev_area
if product == 'propk':
  systemCmd('mv ' + chrootdir + builddir + '/RPMS/noarch/*previewkit* ' +
            chrootdir + chrootcpdir + '/host/' + hostname,scripttest)

if product not in ('devrocket','mls','tsuki','scripttest'):
  systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/host-cd-installer* ' + chrootdir + chrootcpdir + '/installer_rpms/host/' + hostname,scripttest)
  systemCmd('mv ' + chrootdir + builddir + '/RPMS/' + hostarch + '/host-mvlinstaller* ' + chrootdir + chrootcpdir + '/host/' + hostname,scripttest)

# now copy rpms to cpdir
if product not in ('mls','tsuki',):
  cpcmd = '%s %s%s/host/%s/*.mvl %s/host/%s' % (cpall,chrootdir,chrootcpdir,hostname,cpdir,hostname)
  systemCmd(cpcmd,scripttest)
  cpcmd = '%s %s%s/host/%s/testing/*.mvl %s/host/%s/testing' % (cpall,chrootdir,chrootcpdir,hostname,cpdir,hostname)
  systemCmd(cpcmd,scripttest)
  if product == 'cge':
    cpcmd = '%s %s%s/host/%s/optional/*.mvl %s/host/%s/optional' % (cpall,chrootdir,chrootcpdir,hostname,cpdir,hostname)
    systemCmd(cpcmd,scripttest)
  #mvcmd = 'mv %s/host/%s/*devrocket* %s/common/%s' % (cpdir,hostname,cpdir,hostname)
  #os.system(mvcmd)
  #mvcmd = 'mv %s/host/%s/*jdk* %s/common/%s' % (cpdir,hostname,cpdir,hostname)
  if product in ('dev','fe'):
    #mvcmd = 'mv %s/host/%s/*jdk* %s/host/%s' % (cpdir,hostname,cpdir,hostname)
    #os.system(mvcmd)
    #mvcmd = 'mv %s/host/%s/*jre* %s/common/%s' % (cpdir,hostname,cpdir,hostname)
    #mvcmd = 'mv %s/host/%s/*jre* %s/host/%s' % (cpdir,hostname,cpdir,hostname)
    #os.system(mvcmd)
    mvcmd = 'mv %s/host/%s/*flexnet* %s/common/%s' % (cpdir,hostname,cpdir,hostname)
    systemCmd(mvcmd,scripttest)
  cpcmd = '%s %s%s/installer_rpms %s/' % (cpall,chrootdir,chrootcpdir,cpdir)
  systemCmd(cpcmd,scripttest)
  if hostname == targethost:
    cpcmd = '%s %s%s/SRPMS/* %s/SRPMS' % (cpall,chrootdir,builddir,cpdir)
    systemCmd(cpcmd,scripttest)
    #for drsrc in ('apache-ant','devrocket','flexnet','jdk','jre'):
    for drsrc in ('devrocket',):
      mvcmd = 'mv %s/SRPMS/common-%s*.src.rpm %s/common/SRPMS' % (cpdir,drsrc,cpdir)
      systemCmd(mvcmd,scripttest)
    if 'host' in noarchapps.keys():
      if 'devrocket-cd-installer' in noarchapps['host']:
        systemCmd('rm -f %s/SRPMS/devrocket-cd-installer*.src.rpm' % cpdir,scripttest)
elif product == 'tsuki':
  # copy tsuki build results to dev_area
  #print 'copy part...check to see if logs exists, then uncomment this message'
  collectivelog = '%s/%s' % (collectivelogdir,'tsuki-copybuild')
  mstart('tsuki-copybuild',collectivelog,scripttest)
  tsukipath = '%s/%s/tsuki/releng/com.mvista.releng.builder' % (chrootdir,builddir)
  # don't use JAVA_HOME since java has been added to PATH on all nodes
  #cpcmd = 'export JAVA_HOME=/usr/java/j2sdk1.4.1_01; export PATH=$PATH:$JAVA_HOME; ant -f %s/scripts/mv-build.xml copybuild -Dsrc=%s -Ddest=/mvista/dev_area/tsuki -Dtag=%s' % (tsukipath,tsukipath,buildtag)
  cpcmd = 'ant -f %s/scripts/mv-build.xml copybuild -Dsrc=%s -Ddest=%s -Dtag=%s' % (tsukipath,tsukipath,copydir,buildtag)
  #print cpcmd
  systemCmd(cpcmd,scripttest,collectivelog)
  mstop('tsuki-copybuild',collectivelog,scripttest)
elif product == 'mls':
  cpcmd = '%s %s%s/RPMS/mls* %s/' % (cpall,chrootdir,builddir,cpdir)
  systemCmd(cpcmd,scripttest)
getdiskspace(hostname)

# clean chroot host
logfile = "hostclean-" + hostname + ".log"
log = "%s/%s" % (logdir, logfile)
getdiskspace(hostname)

#The node running this script is the node that will run the cleanup, i'm removing the ssh
os.chdir(scriptdir)
pcmd = './hostclean.py %s %s >> %s 2>&1' % (hostname,foundation,log)
systemCmd(pcmd,scripttest)
# delete dirs created by build.sh (devrocket) and kernel
if hostname == targethost and product not in ('mls','tsuki'):
  removeDir('%s/%s/common-eclipse-root' % (chrootdir,builddir),scripttest)
  removeDir('%s/%s/kernel' % (chrootdir,builddir),scripttest)
  removeDir('%s/%s/kernel-build' % (chrootdir,builddir),scripttest)
  systemCmd('rm -f %s/%s/patch*' % (chrootdir,builddir),scripttest)
if product == 'tsuki':
  removeDir('%s/%s/tsuki' % (chrootdir,builddir),scripttest)
  removeDir('%s/%s/MV_Java_Key' % (chrootdir,builddir),scripttest)
if product == 'mls':
  removeDir('%s/%s/licensing' % (chrootdir,builddir),scripttest)
if hostname == 'solaris8':
  if pid != None:
    os.kill(pid, signal.SIGTERM )
systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest)
getdiskspace(hostname)
printflush("Finished %s at %s" % (sys.argv[0],gettime()))

