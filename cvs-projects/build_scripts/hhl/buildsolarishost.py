#!/usr/bin/python
import signal
from buildFunctions import *

# Arguments:
# build_id
# path to sources for build
# build tag
# product
# hosttoolpath
# sht
# scripttest

def rpminstall(chrootpath,installpath,rpm,rpmbin,hostname,log):
  if os.path.exists(chrootpath):
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest,log)
  else:
    printflush('chrootpath does not exist: ' + chrootpath,log,scripttest)
    printflush( 'not installing ' + rpm,log,scripttest)
    res = 1
  printflush('result of install: ' + str(res),log,scripttest)

def rpminst(rpm,rpmbin,hostname,log):
  res = chroot(hostname,rpmbin + ' -Uvh ' + rpm + ' --ignoreos',scripttest,log)
  printflush('result of install: ' + str(res),log,scripttest)

def rpminst_q(rpm,rpmbin,hostname,log):
  chroot(hostname,rpmbin + ' -U ' + rpm + ' --ignoreos',scripttest,log)

def rpmbnt(spec,buildid,rpmbuild,hostname,log):
  printflush('Using rpmbuild = ' + rpmbuild,log,scripttest)
  chroot(hostname,rpmbuild + ' --clean --define \\"_topdir ' + builddir + '\\" ' +
                    '--define \\"_mvl_build_id ' + buildid + '\\" ' +
                    '--define \\"vendor MontaVista Software, Inc.\\" ' +
                    '--define \\"packager <source@mvista.com>\\" ' +
                    '--define \\"_builddir ' + builddir + '/BUILD\\" ' +
                    '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' +
                    #'--define \\"_mvl_host_os_build ' + hostname + '\\" ' +
                    spec,scripttest,log)
  return wrotecheck(hostname)

####################################

if len(sys.argv) != 9:
  print "Usage: %s <buildid> <cvs path> <buildtag> <product> <hosttoolpath> <sht> <collectivelogdir> <scripttest>" % sys.argv[0]
  print '\n# of args = ' + str(len(sys.argv))
  print '\nHere are the args:'
  for x in sys.argv:
    print x
  sys.exit(1)

printflush("Starting %s at %s" % (sys.argv[0],gettime()))
scripttest = int(sys.argv[8])
collectivelogdir = sys.argv[7] + '/hosttool/solaris'
collectivelog = '%s/buildsolarishost-setup' % collectivelogdir
mstart('buildsolarishost-setup',collectivelog,scripttest)
printflush("host: %s" % os.uname()[1],collectivelog,scripttest)

buildid = sys.argv[1]
printflush("buildid = %s" % buildid,collectivelog,scripttest)
srcpath = sys.argv[2]
printflush("srcpath = %s" % srcpath,collectivelog,scripttest)
tag = sys.argv[3]
printflush("tag = %s" % tag,collectivelog,scripttest)
product = sys.argv[4]
printflush("product = %s" % product,collectivelog,scripttest)
hosttoolpath = sys.argv[5]
printflush("hosttoolpath = %s" % hosttoolpath,collectivelog,scripttest)
sht = int(sys.argv[6])
printflush("sht = %s" % str(sht),collectivelog,scripttest)
printflush("collectivelogdir = %s" % collectivelogdir,collectivelog,scripttest)
printflush("scripttest = %s" % str(scripttest),collectivelog,scripttest)
hostname = 'solaris8'
scriptdir = os.getcwd()
printflush("scriptdir = %s" % scriptdir,collectivelog,scripttest)
chrootdir = "/chroot/%s" % hostname
printflush("chrootdir = %s" % chrootdir,collectivelog,scripttest)
installdir = "/opt/montavista"
printflush("installdir = %s" % installdir,collectivelog,scripttest)
builddir = "/home/build"
printflush("builddir = %s" % builddir,collectivelog,scripttest)

commonrpmbin = "%s/common/bin/mvl-common-rpm" % installdir
commonrpmbuild = "%s/common/bin/mvl-common-rpmbuild" % installdir

os.environ['PATH'] = '/opt/montavista/common/bin:' + os.environ['PATH']
if os.popen('uname -r').readline() == '5.10\n':
  pid = os.spawnl(os.P_NOWAIT, '/opt/set-host', 'set-host', '5.8')
  while(os.popen('uname -r').readline() != '5.8\n'):  #This takes a minute to start so we have to wait
    pass
else:
  pid = None

# clean build area
dirs = ["BUILD","RPMS","SOURCES","SPECS","SRPMS"]
for d in dirs:
  removeDir('%s/%s/%s' % (chrootdir,builddir,d))
  systemCmd('mkdir -p %s/%s/%s' % (chrootdir,builddir,d),scripttest,collectivelog)
  systemCmd('chown -R build:engr %s/%s/%s' % (chrootdir,builddir,d),scripttest,collectivelog)

systemCmd('mkdir -p /mvista/dev_area/foundation/%s/build/host-tools/solaris8' % tag,scripttest,collectivelog)
systemCmd('chown -R build:engr /mvista/dev_area/foundation/%s/build/host-tools' % tag,scripttest,collectivelog)
makeDir('%s/build/host-tools/solaris8' % hosttoolpath,scripttest)
makeDir('%s/build/SRPMS' % hosttoolpath,scripttest)
systemCmd('chown -R build:engr %s' % hosttoolpath,scripttest,collectivelog)
mstop('buildsolarishost-setup',collectivelog,scripttest)

# build common-rpm
collectivelog = '%s/%s' % (collectivelogdir,'common-rpm')
mstart('common-rpm',collectivelog,scripttest)
# copy SOURCES and SPECS for rpm
systemCmd('cp %s/userland/rpm/SOURCES/* %s/%s/SOURCES' % (srcpath,chrootdir,builddir),scripttest,collectivelog)
systemCmd('cp %s/userland/rpm/SPECS/* %s/%s/SPECS' % (srcpath,chrootdir,builddir),scripttest,collectivelog)
if rpmbnt(builddir + '/SPECS/common-rpm.spec',buildid,commonrpmbuild+' -bb',hostname,collectivelog) or scripttest == 1:
  rpminstall(chrootdir+builddir+'/RPMS/sun4u',builddir + '/RPMS/sun4u','common-rpm*.mvl',commonrpmbin,hostname,collectivelog)
  printflush("BUILT: common-rpm built.",collectivelog,scripttest)
  systemCmd('cp %s/%s/RPMS/sun4u/common-rpm*.mvl /mvista/dev_area/foundation/%s/build/host/%s' % (chrootdir,builddir,tag,hostname),scripttest,collectivelog)
  mstop('common-rpm',collectivelog,scripttest)
else:
  printflush("BUILD ERROR: common-rpm did not build...stopping build",collectivelog,scripttest)
  mstop('common-rpm',collectivelog,scripttest)
  if scripttest != 1:
    if pid != None:
      os.kill(pid, signal.SIGTERM )
    sys.exit(1)

# install common-autoconf and common-automake
collectivelog = '%s/%s' % (collectivelogdir,'common-autoconf_install')
mstart('common-autoconf_install',collectivelog,scripttest)
systemCmd('cp /mvista/dev_area/foundation/%s/build/host/common/common-autoconf* %s/%s' % (tag,chrootdir,builddir),scripttest,collectivelog)
rpminst(builddir + "/common-autoconf*.mvl",commonrpmbin,hostname,collectivelog)
mstop('common-autoconf_install',collectivelog,scripttest)
collectivelog = '%s/%s' % (collectivelogdir,'common-automake_install')
mstart('common-automake_install',collectivelog,scripttest)
systemCmd('cp /mvista/dev_area/foundation/%s/build/host/common/common-automake* %s/%s' % (tag,chrootdir,builddir),scripttest,collectivelog)
rpminst(builddir + "/common-automake*.mvl",commonrpmbin,hostname,collectivelog)
mstop('common-automake_install',collectivelog,scripttest)
systemCmd('rm -f %s/%s/common-*.mvl' % (chrootdir,builddir),scripttest)

# build common- rpms
commons = ("gettext","libtool","make","mvlutils","elfutils","m4","texinfo","minicom","patch","sed")
for common in commons:
  if common == "elfutils":
    repo = "toolchain"
  else:
    repo = "userland"
  collectivelog = '%s/%s-%s' % (collectivelogdir,'common',common)
  mstart('common-' + common,collectivelog,scripttest)
  systemCmd('cp %s/%s/%s/SOURCES/* %s/%s/SOURCES' % (srcpath,repo,common,chrootdir,builddir),scripttest,collectivelog)
  systemCmd('cp %s/%s/%s/SPECS/* %s/%s/SPECS' % (srcpath,repo,common,chrootdir,builddir),scripttest,collectivelog)
  if rpmbnt(builddir+'/SPECS/common-'+common+'.spec',buildid,commonrpmbuild+' -bb',hostname,collectivelog) or scripttest == 1:
    if rpminstall(chrootdir+builddir+'/RPMS/sun4u',builddir+'/RPMS/sun4u','common-' + common + '*.mvl',commonrpmbin,hostname,collectivelog):
      printflush("BUILD ERROR: common-%s built but did not install" % common,collectivelog,scripttest)
      mstop('common-' + common,collectivelog,scripttest)
    else:
      systemCmd('cp %s/%s/RPMS/sun4u/common-%s*.mvl /mvista/dev_area/foundation/%s/build/host/%s' % (chrootdir,builddir,common,tag,hostname),scripttest,collectivelog)
      if common == "texinfo":
        systemCmd('cp %s/%s/RPMS/sun4u/common-info*.mvl /mvista/dev_area/foundation/%s/build/host/%s' % (chrootdir,builddir,tag,hostname),scripttest,collectivelog)
      printflush("BUILT: common-%s built." % common,collectivelog,scripttest)
  else:
    printflush("BUILD ERROR: common-%s did not build...stopping build" % common,collectivelog,scripttest)
    mstop('common-' + common,collectivelog,scripttest)
    if common != "elfutils":
      if pid != None:
        os.kill(pid, signal.SIGTERM )
      sys.exit(1)
  mstop('common-' + common,collectivelog,scripttest)

if sht:
  # get list of mvls to build
  buildlist = os.popen('cat %s/solaris.dat | grep -v rpm' % scriptdir).readlines()
  printflush("--> building the following:")
  for pkg in buildlist:
    printflush(pkg)

  # build each mvl 
  for pkg in buildlist:
    pkg = string.strip(string.split(pkg,'host-tool-')[1])
    collectivelog = '%s/%s-%s-%s' % (collectivelogdir,'host','tool',pkg)
    mstart('host-tool-' + pkg,collectivelog,scripttest)
    if pkg == "binutils" or pkg == "gcc":
      systemCmd('cp %s/toolchain/%s/SOURCES/* %s/%s/SOURCES' % (srcpath,pkg,chrootdir,builddir),scripttest,collectivelog)
      systemCmd('cp %s/toolchain/%s/SPECS/* %s/%s/SPECS' % (srcpath,pkg,chrootdir,builddir),scripttest,collectivelog)
    else:
      systemCmd('cp %s/userland/%s/SOURCES/* %s/%s/SOURCES' % (srcpath,pkg,chrootdir,builddir),scripttest,collectivelog)
      systemCmd('cp %s/userland/%s/SPECS/* %s/%s/SPECS' % (srcpath,pkg,chrootdir,builddir),scripttest,collectivelog)
    if rpmbnt(builddir+'/SPECS/host-tool-'+pkg+'.spec',buildid,commonrpmbuild+' -ba',hostname,collectivelog) or scripttest == 1:
      if pkg == "gcc":
        rpmsforinstall = "*cpp*.mvl %s/RPMS/sun4u/*gcc-*.mvl %s/RPMS/sun4u/*g++*.mvl %s/RPMS/sun4u/*libgcc1*.mvl %s/RPMS/sun4u/*libstdc++*.mvl" % (builddir,builddir,builddir,builddir)
      elif pkg == "mvlutils":
        rpmsforinstall = "*libgetopt*.mvl %s/RPMS/sun4u/*mktemp*.mvl" % builddir
      else:
        rpmsforinstall = "*%s*.mvl" % pkg
      if not rpminstall(chrootdir+builddir+'/RPMS/sun4u',builddir+'/RPMS/sun4u',rpmsforinstall,commonrpmbin,hostname,collectivelog):
        printflush("BUILT: host-tool-%s built." % pkg,collectivelog,scripttest)
      else:
        printflush("BUILD ERROR: host-tool-%s built but did not install all rpms" % pkg,collectivelog,scripttest)
    else:
      printflush("BUILD ERROR: host-tool-%s did not build." % pkg,collectivelog,scripttest)
    mstop('host-tool-' + pkg,collectivelog,scripttest)

  # Copy remaining .mvls
  systemCmd('cp %s/%s/RPMS/sun4u/host-tool*.mvl %s/build/host-tools/%s' % (chrootdir,builddir,hosttoolpath,hostname),scripttest)
  systemCmd('cp %s/%s/SRPMS/host-tool*.src.rpm %s/build/SRPMS' % (chrootdir,builddir,hosttoolpath),scripttest)

if pid != None:
  os.kill(pid, signal.SIGTERM )
printflush("--> build ended at %s" % gettime())
