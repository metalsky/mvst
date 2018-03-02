#!/usr/bin/python
from buildFunctions import *

def getprovides():
  f_logfile = open('/chroot/%s/home/build/chroot.log' % (hostname),'r')
  logfile = f_logfile.readlines()
  f_logfile.close()
  providesfile = open('/chroot/%s/home/build/provides-%s' % (hostname,target),'a')
  Length = len(logfile)
  linenum = 0
  firstfile = 0
  while linenum < Length and string.find(logfile[linenum], 'Processing files:') == -1:
    linenum+=1
  while linenum < Length:
    if string.find(logfile[linenum],'Processing files:') != -1:
      rpmfilename = string.split(logfile[linenum],' ')[2]
      if string.find(rpmfilename,'common') == -1 and string.find(rpmfilename,'cross') ==-1 and string.find(rpmfilename,'host') ==-1:
        if not firstfile:
          firstfile = 1
        else:
          providesfile.write('\n')
        providesfile.write(rpmfilename)
      linenum+=1
    elif string.find(logfile[linenum],'Provides:') != -1:
      provides = logfile[linenum]
      if string.find(rpmfilename,'common') == -1 and string.find(rpmfilename,'cross') ==-1 and string.find(rpmfilename,'host') ==-1:
        providesfile.write(provides)
      linenum+=1
    elif string.find(logfile[linenum],'Requires:') != -1:
      requires = logfile[linenum]
      if string.find(rpmfilename,'common') == -1 and string.find(rpmfilename,'cross') ==-1 and string.find(rpmfilename,'host') ==-1:
        providesfile.write(requires)
      linenum+=1
    else:
      linenum+=1
  providesfile.write('\n')
  providesfile.close()

def makebuilddirs():
  dirs = ('SPECS','SOURCES','SRPMS','BUILD','RPMS')
  for d in dirs:
    systemCmd('rm -rf %s/%s/%s' % (chrootdir,builddir,d),scripttest)
    systemCmd('mkdir -p %s/%s/%s' % (chrootdir,builddir,d),scripttest)

def cleanbuilddirs():
  printflush('cleaning build directories...')
  getdiskspace(hostname)
  systemCmd('rm -f %s/%s/SPECS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -f %s/%s/SRPMS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/SOURCES/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/BUILD/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/RPMS/*' % (chrootdir,builddir),scripttest)
  getdiskspace(hostname)

def uninst(installdir,hostname):
  printflush('uninstalling previous build...')
  getdiskspace(hostname)
  chroot(hostname,'rm -rf ' + installdir + '/*',scripttest)
  if hostname == 'solaris8':
    systemCmd('cd /chroot/solaris8/opt; tar -xf /opt/montavista.f3.tar',scripttest)
    systemCmd('chown -R build:engr /chroot/solaris8/opt/montavista',scripttest)
  getdiskspace(hostname)

def rpminstall(path,installpath,rpm,rpmbin):
  if os.path.exists(path):
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest)
  else:
    printflush('path does not exist: ' + path)
    printflush('not installing ' + rpm)
    res = 1
  printflush('result of install: ' + str(res))
  return res

def rpmev(rpm,rpmbin):
  printflush('uninstalling: ' + rpm)
  chroot(hostname,rpmbin + ' -ev ' + rpm + ' --nodeps',scripttest)

def rpminst(rpm,rpmbin):
  res = chroot(hostname,rpmbin + ' -Uvh ' + rpm + ' --ignoreos',scripttest)
  printflush('result of install: ' + str(res))
  return res

def rpminst_q(rpm,rpmbin):
  res = chroot(hostname,rpmbin + ' -U ' + rpm + ' --ignoreos',scripttest)
  printflush('result of install: ' + str(res))
  return res

def rpmqa(query,rpmbin):
  command = '%s -qa | grep %s' % (rpmbin,query)
  if hostname != "solaris8":
    cmd = 'sudo chroot /chroot/%s /bin/su - build -c "%s"' % (hostname,command)
  else:
    cmd = 'chroot /chroot/%s /bin/su - build -c "%s"' % (hostname,command)
  if not scripttest:
    results = os.popen(cmd).readlines()
  else:
    printflush('command: ' + cmd)
    results = []
  return results

def rpmb(spec,rpmbuild,bcmd,reqFiles):
  printflush('Using rpmbuild = ' + rpmbuild)
  cmd = rpmbuild + ' --clean -' + bcmd + \
                   ' --define \\"_topdir ' + builddir + '\\" ' + \
                   '--define \\"_mvl_build_id ' + buildid + '\\" ' + \
                   '--define \\"vendor MontaVista Software, Inc.\\" ' + \
                   '--define \\"packager <source@mvista.com>\\" ' + \
                   '--define \\"_builddir ' + builddir + '/BUILD\\" ' + \
                   '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' + \
                   '--define \\"_mvl_host_os_build ' + hostname + '\\" ' + \
                   '--define \\"_mvl_selinux ' + selinux + '\\" ' + \
                   spec
  #printflush('cmd = ' + cmd)
  chroot(hostname,cmd,scripttest)
  return wrotecheck(hostname,reqFiles,minReqApps)

def exist(path,name):
  if os.path.exists(path):
    for file in os.listdir(path):
      if string.find(file,name) > -1:
        # file exists, return 1
        return 1
    # made it through all files and didn't find name, so return 0
  return 0

if len(sys.argv) < 7 or len(sys.argv) > 8:
  printflush("\nbuildtargetapps.py <data file> <target> <hostname> <app file> <alt> <run #> [installf]")
  printflush("\n# of args = " + str(len(sys.argv)))
  printflush("\nHere are the args:")
  for x in sys.argv:
    printflush(x)
  sys.exit(1)
                                                                                                             
datafile = sys.argv[1]
target = sys.argv[2]
hostname = sys.argv[3]
appfile = sys.argv[4]
alt = sys.argv[5]
runnum = sys.argv[6]
installf = 1
if len(sys.argv) == 8:
  installf = sys.argv[7]

mstart('buildtargetapps-%s-%s-script-setup' % (runnum,target))
getdiskspace(hostname)
printflush('<' + sys.argv[0] + '>: starting buildtargetapps for ' + target + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')
printflush("datafile = %s" % datafile)
if os.path.exists(datafile):
  exec(open(datafile))
  printflush('targethost = ' + targethost)
else:
  printflush("No datafile found.  Stopping build.")
  printflush("Finished %s at %s" % (sys.argv[0],gettime()))
  mstop('buildtargetapps-%s-%s-script-setup' % (runnum,target))
  sys.exit(1)

commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
commonrpmbuild = commonrpmbin + 'build'
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
editionrpmbuild = editionrpmbin + 'build'
if 'mvl-kernel-26' in cvspaths.keys():
  kspecpath = cvspaths['mvl-kernel-26'][0]
else:
  kspecpath = "null"
node = string.strip(os.popen('hostname').read())
printflush('node = ' + node)
scriptdir = os.getcwd()

# this is the directory in the chroot environment where rpm are built
builddir = '/home/build'

# this is the chroot directory
chrootdir = '/chroot/%s' % (hostname)

# this is the cpdir in the chroot environment
chrootcpdir = '%s/home/build/RPMS/install' % chrootdir
printflush('scriptdir = ' + scriptdir)
printflush('builddir = ' + builddir)
printflush('chrootdir = ' + chrootdir)
printflush('chrootcpdir = ' + chrootcpdir)

# check to see if system rpm uses rpm or rpmbuild
if hostname in ('centos3','redhat80','redhat90','suse90'):
  sysrpmbuild = 'rpmbuild'
  sysrpmbin = 'rpm'
  rpm2cpio = 'rpm2cpio'
  cpall = 'cp -a'
  hostarch = 'i386'
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

getReqFiles = 0
minReqApps = '%s/%s/MVL-%s-apps-%s-%s' % (cpdir,target,edition,target,buildid)
if appfile == libraryapps:
  getReqFiles = 1

if target in abitargets:
  nonAbiTarget = string.split(target,'-')[0]
  printflush('architecture is ' + target)
  printflush('building as %s, with abi value of %s' % (nonAbiTarget,alt))
  target = nonAbiTarget
  uninst(installdir,hostname)
  makebuilddirs()
  minReqApps = '%s/%s/MVL-%s-apps-%s-%s' % (cpdir,target,edition,target,buildid)
  getReqFiles = 1
else:
  printflush('architecture is ' + target)
printflush('kernel version is ' + kernel + '_' + hhlversion)

# add ltt-usertrace to uclibcxcludes if target is non-arm uclibc target
if string.find(target,'uclibc') > -1 and string.find(target,'arm') == -1:
  uclibcxcludes.append('ltt-usertrace')

printflush('--> Building on ' + hostname + '...')

# define variables for userland, toolchain, installer, mvlt and mvltest repository paths
path = "null"
toolpath = "null"
mvlinstallerpath = "null"
mvltpath = "null"
mvltest = "null"
devtestpath = "null"
if 'userland' in cvspaths.keys():
  path = cvspaths['userland'][0]
if 'toolchain' in cvspaths.keys():
  toolpath = cvspaths['toolchain'][0]
if 'mvl-installer' in cvspaths.keys():
  mvlinstallerpath = cvspaths['mvl-installer'][0]
if 'mvlt' in cvspaths.keys():
  mvltpath = cvspaths['mvlt'][0]
if 'mvltest' in cvspaths.keys():
  mvltest = cvspaths['mvltest'][0]
if 'devtest' in cvspaths.keys():
  devtestpath = cvspaths['devtest'][0]

cleanbuilddirs()

bpath = path
building = 0

if os.path.exists(cpdir + '/' + target + '/target') or scripttest:
  #existingrpms = os.listdir(cpdir + '/' + target + '/target')
  flag = '# ' + target
  endline = '# end'
  fbuild = open(appfile, 'r')
  bonnie = 0
  while 1:
    pak = string.strip(fbuild.readline())
    if pak == flag:
      if product in ('dev','fe','cge') and alt != "null":
        # install all common/host/cross/target apps from non-abi target since this build
        # is only building the multilib apps and did not run build core.
        printflush('<' + sys.argv[0] + '>: installing foundation apps for ' + target + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')
        # common-rpm & common apps
        systemCmd('mkdir -p %s' % chrootcpdir,scripttest)
        systemCmd('%s %s/host/common/common*.mvl %s' % (cpall,cpdir,chrootcpdir),scripttest)
        systemCmd('%s %s/host/%s/common*.mvl %s' % (cpall,cpdir,hostname,chrootcpdir),scripttest)
        chroot(hostname,'cd /; rpm2cpio %s/RPMS/install/common-rpm-4* | cpio -iud' % builddir,scripttest)
        chroot(hostname,'cd /; rpm2cpio %s/RPMS/install/common-rpm-b* | cpio -iud' % builddir,scripttest)
        chroot(hostname,'cd /; rpm2cpio %s/RPMS/install/common-rpm-d* | cpio -iud' % builddir,scripttest)
        rpminst(builddir+'/RPMS/install/*.mvl',commonrpmbin)
        systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
        # host-rpm & host apps
        systemCmd('%s %s/host/common/host*.mvl %s' % (cpall,cpdir,chrootcpdir),scripttest)
        systemCmd('%s %s/host/%s/host*.mvl %s' % (cpall,cpdir,hostname,chrootcpdir),scripttest)
        chroot(hostname,'cd /; rpm2cpio %s/RPMS/install/host-rpm-4* | cpio -iud' % builddir,scripttest)
        rpminst(builddir+'/RPMS/install/*.mvl',editionrpmbin)
        systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
        # cross apps
        systemCmd('%s %s/%s/cross/common/*.mvl %s' % (cpall,cpdir,target,chrootcpdir),scripttest)
        systemCmd('%s %s/%s/cross/%s/*.mvl %s' % (cpall,cpdir,target,hostname,chrootcpdir),scripttest)
        rpminst(builddir+'/RPMS/install/*.mvl',editionrpmbin)
        systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
        # target apps
        cpapps = []
        cpapps = os.listdir('%s/%s/target' % (cpdir,target))
        for cpapp in cpapps:
          if os.path.isfile('%s/%s/target/%s' % (cpdir,target,cpapp)):
            systemCmd('%s %s/%s/target/%s %s' % (cpall,cpdir,target,cpapp,chrootcpdir),scripttest)
        os.chdir(chrootcpdir)
        systemCmd('ls -1 *.mvl > installme.txt',scripttest)
        rpminst(builddir+'/RPMS/install/installme.txt --target='+target+'-linux --nodeps','cd ' + builddir + '/RPMS/install; ' + editionrpmbin)
        systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
        os.chdir(scriptdir)
        getdiskspace(hostname)
        printflush('<' + sys.argv[0] + '>: finished install at ' + gettime())
      elif product not in ('dev','fe') and installf:
        # install all foundation target apps
        printflush('<' + sys.argv[0] + '>: installing foundation target apps for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')
        systemCmd('mkdir -p %s' % chrootcpdir,scripttest)
        systemCmd('cd %s/%s/target; %s *.mvl %s' % (cpdir,target,cpall,chrootcpdir),scripttest)
        # remove glibc & kernel-headers rpms since they were installed by buildcore.py
        for removerpm in removerpms:
          systemCmd('rm -f %s/%s*' % (chrootcpdir,removerpm),scripttest)
        rpminst(builddir+'/RPMS/install/*.mvl --target='+target+'-linux --nodeps',editionrpmbin)
        if product == 'propk':
          systemCmd('%s %s/%s/target/optional/thttpd*.mvl %s' % (cpall,cpdir,target,chrootcpdir),scripttest)
          rpminst(builddir+'/RPMS/install/thttpd*.mvl --target='+target+'-linux --nodeps',editionrpmbin)
        # mobilinux needs to uninstall conflicting apps
        elif product in ('mobiasync','mobilinux'):
          for app in mobilinuxUninstall:
            printflush("Uninstalling app: %s "%(app))
            printflush("Running an rpm query...")
            removeList = rpmqa(app,editionrpmbin + ' --target=' + target + '-linux')
            printflush("Packages to remove are: %s" % removeList)
            for appToRemove in removeList:
              printflush("Removing: %s" % appToRemove)
              rpmev(appToRemove,editionrpmbin + ' --target=' + target + '-linux --nodeps')
        systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
        getdiskspace(hostname)
        printflush('<' + sys.argv[0] + '>: finished install at ' + gettime())
      printflush('cp %s/bin/true %s/opt/montavista/common/bin/mvl-license' % (chrootdir,chrootdir))
      systemCmd('cp %s/bin/true %s/opt/montavista/common/bin/mvl-license' % (chrootdir,chrootdir))
      mstop('buildtargetapps-%s-%s-script-setup' % (runnum,target))
      while 1:
        skipexistingrpm = 0          # this is a flag that is initially set to 0.
                                     # Since netperf is built
                                     # at least once in buildcore.py, this script
                                     # will check to see if the package being built
                                     # has been built (if so, skipexistingrpm is set to 1).
                                     # If not, it builds it, otherwise it won't.
        #pak is equal to the directory the spec file will live in 
        #packname is equal to the .spec file name
        pak = string.strip(fbuild.readline())
        reqFiles = getReqFiles
        if product == 'pro' and pak == 'netbase':
          reqFiles = 0
        if string.find(pak, '#') > -1:
          if building == 1:
            break
          else:
            continue
        elif pak == 'null':
          if building == 0:
            building = 1
          break
        elif string.find(target,'uclibc') > -1 and pak in uclibcxcludes:
          continue
        elif string.find(target,'xtensa') > -1 and pak in xtensaxcludes:
          continue
        elif pak == 'libiconv' and string.find(target,'uclibc') == -1:
          continue
        elif pak == 'libunwind' and string.find(target,'ppc') > -1:
          continue
        elif pak == 'libunwind' and string.find(target,'uclibc') > -1 and string.find(target,'x86') > -1:
          continue
        else:
          building = 1
          #for e_rpm in existingrpms:
          #  if alt == 'null':
          #    tmp = re.match(pak + '-(.+)',e_rpm)
          #    if tmp:
          #      print pak + ' exists as ' + e_rpm 
          #      print 'skipping ' + pak + '...'
          #      skipexistingrpm = 1
          if skipexistingrpm == 0:
            #print pak + '...'
            altpakname = ''
            pakname = pak
            if alt != "null":
              bcmd = 'bb --target='+target+'-linux'
            else:
              bcmd = 'ba --target='+target+'-linux'
            if pak == 'bonnie':
              pak = 'bonnie++'
              pakname = 'bonnie++'
            elif pak == 'application-man-html':
              pakname = 'host-application-man-html'
            elif pak == 'e100-telco-hard':
              pak = 'e100'
            elif pak == 'previewkit-base':
              pak = 'mvlpk'
            elif pak == 'pxelinux-previewkit':
              pak = 'pxelinux'
            elif pak == 'ixpctl-previewkit':
              pak = 'ixpctl'
            elif pak == 'libaudiofile':
              pak = 'audiofile'
            elif pak == 'TinyX':
              pak = 'XFree86'
            elif pak == 'glib2':
              pak = 'glib2.0'
            elif pak == 'gtk2-directfb':
              pak = 'gtk2'
            elif pak == 'cairo-directfb':
              pak = 'cairo'
            elif pak == 'pango-directfb':
              pak = 'pango'
            elif pak == 'libmng':
              pak = 'mng'
            elif pak == 'busybox-static':
              pak = 'busybox'
            elif pak == 'udev-static':
              pak = 'udev'
            elif pak in ('dspbridge-mpu-api','dspbridge-samples'):
              pak = 'dspbridge'
            elif pak == 'omapvideoout':
              pakname = 'omap_videoout_header'
            elif pak == 'rpm-edition':
              pak = 'rpm'
              if product not in ('dev','fe'):
                systemCmd('rm -f %s/%s/target/rpm-edition*.mvl' % (cpdir,target),scripttest)
              else:
                # don't put rpm-edition from foundation in the apps list file since the editions
                # put it there
                reqFiles = 0
            elif pak in ('lsb-3.1.0','lsb-3.0.0','lsb-2.1.0','lsb-helpers'):
              pak = 'lsb'
            elif pak in ('uSDE','uSDE-installer'):
              pak = 'sde'
            elif pak in ('installation-enum-hooks',):
              pak = 'install-enum-hooks'
            elif pak == 'self-hosted-installer':
              pak = ''
              if product == 'cge':
                for uninstall in rpmqa('uSDE',editionrpmbin+' --target='+target+'-linux'):
                  rpmev(string.strip(uninstall),editionrpmbin+' --target='+target+'-linux')
              systemCmd('mkdir -p %s' % chrootcpdir,scripttest)
              for r in ('install-libuSDE','install-uSDE','installation-enum'):
                printflush('copying %s* from %s/%s/target/optional to %s...' % (r,cpdir,target,chrootcpdir))
                systemCmd('ls %s/%s/target/optional/%s*.mvl' % (cpdir,target,r),scripttest)
                systemCmd('cd %s/%s/target/optional; %s %s*.mvl %s' % (cpdir,target,cpall,r,chrootcpdir),scripttest)
                rpminst(builddir+'/RPMS/install/*.mvl --target='+target+'-linux --nodeps',editionrpmbin)
                systemCmd('rm -rf %s/*' % chrootcpdir,scripttest)
            elif pak in ('arch-cd-installer','cross-cd-installer','lsps-cd-installer','bst-addon-cd-installer'):
              pak = ''
            elif pak == 'bst-stress':
              pak = 'stress'
            elif 's124atom' in buildtag and pak == 'applewmproto':
              mstart('graphics_uninstall')
              for r_app in x11uninstall:
                for uninstall in rpmqa(r_app,editionrpmbin+' --target='+target+'-linux'):
                  rpmev(string.strip(uninstall),editionrpmbin+' --target='+target+'-linux')
              printflush('removing /opt/montavista/mvl/devkit/x86/586/target/etc/X11...')
              systemCmd('rm -rf /chroot/centos3/opt/montavista/mvl/devkit/x86/586/target/etc/X11',scripttest)
              mstop('graphics_uninstall')
            else:
              pakname = pak
            if alt == '32':
              altpakname = pakname + '-32'
            elif alt == 'o32':
              altpakname = pakname + '-o32'
            elif alt == '64':
              altpakname = pakname + '-64'
            if pak in ('elfutils','gdb','gdb-32','gdb-64','gdb-o32','prelink'):
              bpath = toolpath
            elif pak == 'compat-redhat62':
              bpath = toolpath
              pak = 'gcc'
            elif pak == 'compat-redhat73':
              bpath = toolpath
              pak = 'gcc'
            elif pakname in ('arch-cd-installer','self-hosted-installer','cross-cd-installer','lsps-cd-installer','bst-addon-cd-installer'):
              bcmd = 'bb --target='+target+'-linux'
              bpath = mvlinstallerpath
            elif pakname in ('mvltd','mvlttools'):
              bpath = mvltpath
            elif pakname == 'bst-stress':
              bpath = mvltest + '/common/kernel'
            elif pak in ('ltp','staf'):
              bpath = devtestpath
            else:
              bpath = path
            #print 'using ' + pakname + '.spec...'
            if altpakname:
              mstart(altpakname)
            else:
              mstart(pakname)
            getdiskspace(hostname)
            if os.path.exists(bpath + '/' + pak + '/SPECS/' + pakname + '.spec'):
              systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,bpath,pak,chrootdir,builddir),scripttest)
              systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,bpath,pak,chrootdir,builddir),scripttest)
              if alt == '32':
                extra = ' --define \\"_mvl_multilib 32\\"'
              elif alt == 'o32':
                extra = ' --define \\"_mvl_multilib o32\\"'
              elif alt == '64':
                extra = ' --define \\"_mvl_multilib 64\\"'
              elif pak == 'apt-rpm-config' and aptedition:
                extra = ' --define \\"_edition %s\\"' % aptedition
              else:
                extra = ''
              if rpmb(builddir+'/SPECS/'+pakname+'.spec',editionrpmbuild+extra,bcmd,reqFiles):
                getdiskspace(hostname)
                if os.path.exists(chrootdir+builddir+'/RPMS/'+target):
                  for cpfile in os.listdir(chrootdir+builddir+'/RPMS/'+target):
                    opt = 0
		    testapp = 0
                    for opapp in optionalApps:
                      if string.find(cpfile,opapp) > -1:
                        opt = 1
                        if pakname in ('uSDE','uSDE-installer'):
                          rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'*.mvl',editionrpmbin+' --target='+target+'-linux --nodeps')
                        break
                    for tapp in testapps:
                      if string.find(cpfile,tapp) > -1:
                        testapp = 1
                        break
                    if opt:
                      if cpfile != 'CVS' and cpfile != 'CVSROOT' and cpfile != 'placeholder':
                        printflush('moving ' + cpfile + ' to optional...')
                        if string.find(cpfile,'mvl') > -1:
                          printflush('moving ' + cpfile)
                          systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile +
                                      ' ' + cpdir + '/' + target + '/target/optional',scripttest)
                    elif testapp:
                      if cpfile != 'CVS' and cpfile != 'CVSROOT' and cpfile != 'placeholder':
                        printflush('moving ' + cpfile + ' to testing...')
                        if string.find(cpfile,'mvl') > -1:
                          printflush('moving ' + cpfile)
                          systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile +
                                    ' ' + cpdir + '/' + target + '/target/testing',scripttest)
                if pak == 'netkit-base':
                  if alt in ('32','64',):
                    rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'netkit-inetd*'+ alt+'*.mvl',editionrpmbin+' --target='+target+'-linux --nodeps')
                  else:
                    rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'netkit-inetd*'+ '.mvl',editionrpmbin+' --target='+target+'-linux --nodeps')
                elif pakname not in ('ixpctl-previewkit','pxelinux-previewkit','arch-cd-installer','self-hosted-installer','lsps-cd-installer','cross-cd-installer'):
                  if alt in ('32','64',):
                    rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'*'+
                               alt+'*.mvl',editionrpmbin+' --target='+target+'-linux --nodeps')
                  else:
                    rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'*.mvl',editionrpmbin+' --target='+target+'-linux --nodeps')
                if altpakname:
                  printflush('BUILT: ' + altpakname + ' for ' + target + ' built.')
                  getdiskspace(hostname)
                  mstop(altpakname)
                else:
                  printflush('BUILT: ' + pakname + ' for ' + target + ' built.')
                  getdiskspace(hostname)
                  mstop(pakname)
              else:
                if altpakname:
                  printflush('BUILD ERROR: ' + altpakname + ' for ' + target + ' did not build.')
                  getdiskspace(hostname)
                  mstop(altpakname)
                else:
                  printflush('BUILD ERROR: ' + pakname + ' for ' + target + ' did not build.')
                  getdiskspace(hostname)
                  mstop(pakname)
            else:
              if altpakname:
                printflush('BUILD ERROR: ' + altpakname + ' for ' + target + ' did not build, no spec file.')
                getdiskspace(hostname)
                mstop(altpakname)
              else:
                printflush('BUILD ERROR: ' + pakname + ' for ' + target + ' did not build, no spec file.')
                getdiskspace(hostname)
                mstop(pakname)
            if os.path.exists(chrootdir+builddir+'/RPMS/'+target):
              systemCmd('mv ' + chrootdir+builddir+'/SRPMS/* ' + cpdir + '/SRPMS',scripttest) 
              for cpfile in os.listdir(chrootdir+builddir+'/RPMS/'+target):
                if cpfile != 'CVS' and cpfile != 'CVSROOT' and cpfile != 'placeholder':
                  #print 'cpfile = ' + cpfile
                  if string.find(cpfile,'mvl') > -1 and string.find(cpfile,'cd-install') == -1 and string.find(cpfile,'self-hosted') == -1: 
                    #print 'cpfile= ' + cpfile + '...'
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile +
                              ' ' + cpdir + '/' + target + '/target',scripttest)
                  elif string.find(cpfile,'cross-' + target + '-cd-install') > -1:
                    printflush('moving ' + cpfile + ' to ' + cpdir + '/installer_rpms/cross/' + target + '...' )
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile + ' ' + cpdir +
                              '/installer_rpms/cross/' + target,scripttest)
                  elif string.find(cpfile,'arch-' + target + '-cd-install') > -1:
                    printflush('moving ' + cpfile + ' to ' + cpdir + '/installer_rpms/target/' + target + '...')
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile + ' ' + cpdir +
                              '/installer_rpms/target/' + target,scripttest)
                  elif string.find(cpfile,'lsps-' + target + '-cd-install') > -1:
                    printflush('moving ' + cpfile + ' to ' + cpdir + '/installer_rpms/lsps/' + target + '...' )
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile + ' ' + cpdir +
                              '/installer_rpms/lsps/' + target,scripttest)
                  elif string.find(cpfile,'self-hosted') > -1:
                    printflush('moving ' + cpfile + ' to ' + cpdir + '/installer_rpms/self-hosted/' + target + '...')
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/'+target+'/' + cpfile + ' ' + cpdir +
                              '/installer_rpms/self-hosted/' + target,scripttest)
            elif os.path.exists(chrootdir+builddir+'/RPMS/noarch') and (pak in targnoarch or pakname in targnoarch):
              systemCmd('mv ' + chrootdir+builddir+'/SRPMS/* ' + cpdir + '/SRPMS',scripttest) 
              for cpfile in os.listdir(chrootdir+builddir+'/RPMS/noarch'):
                if cpfile != 'CVS' and cpfile != 'CVSROOT' and cpfile != 'placeholder':
                  #print 'cpfile = ' + cpfile
                  if string.find(cpfile,'mvl') > -1:
                    #print 'cpfile= ' + cpfile + '...'
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/noarch/' + cpfile + ' ' + cpdir +
                              '/' + target + '/target',scripttest)
            elif os.path.exists(chrootdir+builddir+'/RPMS/noarch') and pak == 'application-man-html':
              systemCmd('mv ' + chrootdir+builddir+'/SRPMS/* ' + cpdir + '/SRPMS',scripttest) 
              for cpfile in os.listdir(chrootdir+builddir+'/RPMS/noarch'):
                if cpfile not in ('CVS','CVSROOT','placeholder'):
                  if string.find(cpfile,'mvl') > -1:
                    printflush('moving ' + cpfile)
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/noarch/' + cpfile + ' ' +
                               cpdir + '/host/common',scripttest) 
            elif os.path.exists(chrootdir+builddir+'/RPMS/noarch') and string.find(pakname,'preview') > -1:
              systemCmd('mv ' + chrootdir+builddir+'/SRPMS/* ' + cpdir + '/SRPMS',scripttest) 
              for cpfile in os.listdir(chrootdir+builddir+'/RPMS/noarch'):
                if cpfile not in ('CVS','CVSROOT','placeholder'):
                  if string.find(cpfile,'mvl') > -1:
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/noarch/' + cpfile + ' ' + cpdir +
                              '/' + target + '/target',scripttest)
            elif os.path.exists(chrootdir+builddir+'/RPMS/noarch') and string.find (pakname,'bst-addon-cd-installer') > -1:
              for cpfile in os.listdir(chrootdir+builddir+'/RPMS/noarch'):
                if cpfile not in ('CVS','CVSROOT','placeholder'):
                  if string.find(cpfile,'mvl') > -1:
                    systemCmd('mv ' + chrootdir+builddir+'/RPMS/noarch/' + cpfile + ' ' + cpdir +
                              '/installer_rpms/addon/',scripttest) 
            cleanbuilddirs()

    elif building == 1 or pak == endline:
      break

  fbuild.close()
  printflush('existing /var/tmp/* directories:')
  systemCmd('ls /var/tmp/*',scripttest)
else:
  printflush(cpdir + "/" + target + "/target doesn't exist...something bad happened!!!\n")

os.chdir(builddir)
#systemCmd('cat /chroot/%s/home/build/provides-%s >> %s/%s/target/provides/provides-%s' % (hostname,target,cpdir,target,target),scripttest)
getdiskspace(hostname)

printflush('<' + sys.argv[0] + '>: finished buildtargetapps for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')

