#!/usr/bin/python
from buildFunctions import *
from resourceManager import *

kbv = '_mvl_kernel_base_version'           # kbv is the kernel base version
khv = '_mvl_kernel_mvl_version'            # khv is the kernel hhl version
dontclean = ['CVS', 'README', 'placeholder', 'platformtest']

# nice level of parrallelization for 2 cpus (go speed racer go)
# doing this on a single cpu will work, but will be somewhat slower
# I have tested this number on 1of9 and the glibc and gcc packages...
# for glibc..
# make -j2:      944.91user 537.83system 13:15.61elapsed 186%CPU
# make -j3:      945.33user 541.36system 13:16.80elapsed 186%CPU
# for cross-gcc-bootstrap:
# make -j2:      164.28user 32.46system 1:59.88elapsed 164%CPU
# make -j3:      163.94user 32.70system 2:01.50elapsed 161%CPU
par_flag = '-j2'
dmake = ' --define dmake\ make\ ' + par_flag

def uninstallbuild():
  printflush('removing MVL packages...')
  getdiskspace(hostname)
  cmd = 'rm -rf %s/*' % installdir
  printflush('--> %s' % cmd)
  chroot(hostname,cmd,scripttest)
  getdiskspace(hostname)

def cleanbuilddirs():
  getdiskspace(hostname)
  systemCmd('rm -f %s/%s/SPECS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -f %s/%s/SRPMS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/SOURCES/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/BUILD/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/RPMS/*' % (chrootdir,builddir),scripttest)
  getdiskspace(hostname)

def rpminstall(path,installpath,rpm,rpmbin,log=''):
  if os.path.exists(path) or scripttest:
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest,log)
  else:
    printflush('path does not exist: ' + path,log,scripttest)
    printflush('not installing ' + rpm,log,scripttest)
    res = 1
  printflush('result of install: ' + str(res),log,scripttest)
  return res

def rpmev(rpm,rpmbin):
  chroot(hostname,rpmbin + ' -ev ' + rpm + ' --nodeps',scripttest)

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

def rpmb(spec,rpmbuild,bcmd,log,getReqFiles=0):
  printflush('Using rpmbuild = ' + rpmbuild,log,scripttest)
  cmd = rpmbuild + ' --clean -' + bcmd + \
                   ' --define \\"_topdir ' + builddir + '\\" ' + \
                   '--define \\"_mvl_build_id ' + buildid + '\\" ' + \
                   '--define \\"vendor MontaVista Software, Inc.\\" ' + \
                   '--define \\"packager <source@mvista.com>\\" ' + \
                   '--define \\"_builddir ' + builddir + '/BUILD\\" ' + \
                   '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' + \
                   '--define \\"_mvl_host_os_build ' + hostname + '\\" ' + \
                   spec
  chroot(hostname,cmd,scripttest,log)
  return wrotecheck(hostname,getReqFiles,minReqApps)

def gitmake(apptype,cmd,rpmbuild,log,getReqFiles=0):
  printflush('Using rpmbuild = ' + rpmbuild,log,scripttest)
  cmd = '%s make LSPTYPE=%s MVL_TARGET_ARCH=%s BUILDID=%s RPM=%s %s' % (cmd,lsptype,target,buildid,rpmbuild,apptype)
  chroot(hostname,cmd,scripttest,log)
  return wrotecheck(hostname,getReqFiles,minReqApps)

def exist(path,name):
  if os.path.exists(path):
    for file in os.listdir(path):
      if string.find(file,name) > -1:
        # file exists, return 1
        return 1
    # made it through all files and didn't find name, so return 0
  return 0

def copysrcrpm(filename,log=''):
  srcres = getResource(buildtag,buildid,'copysrcrpm','copying %s src rpm in buildcore.py' % filename)
  printflush("checking for %s in %s/%s/SRPMS..." % (filename,chrootdir,builddir),log,scripttest)
  srpms = ['srcrpm',]
  if os.path.exists('%s/%s/SRPMS' % (chrootdir,builddir)):
    srpms = os.listdir('%s/%s/SRPMS' % (chrootdir,builddir))
  for srpm in srpms:
    printflush("\tis %s in %s?" % (filename,srpm),log,scripttest)
    #if string.find(srpm,'/' + filename) > -1:
    if string.find(srpm,filename) > -1:
      printflush("\t\tyes.  getting src rpm filename.",log,scripttest)
      srcfile = string.strip(srpm[string.find(srpm,'/' + filename)+1:])
      printflush("\t\tsrcfile is %s" % srcfile,log,scripttest)
      printflush("\tDoes srcfile exist in copy directory",log,scripttest)
      if not os.path.exists('%s/SRPMS/%s' % (cpdir,srcfile)):
        printflush('\t\t%s has not been copied, copying now...' % srcfile,log,scripttest)
        systemCmd('%s %s/%s/SRPMS/%s %s/SRPMS' % (cpall,chrootdir,builddir,srcfile,cpdir),scripttest,log)
      else:
        printflush( "\t\t%s has been copied, skipping copy now" % srcfile,log,scripttest)
    else:
      printflush("\t\tno, looking at next src rpm",log,scripttest)
  releaseResource(srcres)

def buildfilesystem(type):
  returnmsg = ''
  getReqFiles = 0
  # build filesystem package
  if type == 'cross':
    fs = 'cross-filesystem'
    extra = '--cross='
  elif type == 'target':
    fs = 'filesystem'
    extra = '--define \\"_mvl_selinux ' + selinux + '\\" --target='
    getReqFiles = 1
  else:
    return "unknown type for filesystem build...should be cross or target but was " + type
  collectivelog = '%s/%s' % (collectivelogdir,fs)
  bcmd = 'ba ' + extra + target
  mstart(fs,collectivelog,scripttest)
  getdiskspace(hostname)
  if 'userland' in cvspaths.keys():
    srcpath = cvspaths['userland'][0] + '/filesystem'
  else:
    srcpath = 'null'
  printflush('srcpath = ' + srcpath,collectivelog,scripttest)
  if os.path.exists('%s/SOURCES' % srcpath) and os.listdir('%s/SOURCES' % srcpath):
    systemCmd('%s %s/SOURCES/* %s/%s/SOURCES' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
  systemCmd('%s %s/SPECS/* %s/%s/SPECS' % (cpall,srcpath,chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  if rpmb(builddir + '/SPECS/' + fs + '.spec',editionrpmbuild,bcmd,collectivelog,getReqFiles) or scripttest == 1:
    if type == 'cross' and exist(chrootdir+builddir+'/RPMS/noarch','cross-' + target + '-filesystem') or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir+'/RPMS/noarch','cross-' + target + '-filesystem*.mvl',editionrpmbin,collectivelog)
      copysrcrpm('cross-filesystem',collectivelog)
      systemCmd('%s %s/%s/RPMS/noarch/cross-%s-filesystem*.mvl %s/%s/cross/common' % (cpall,chrootdir,
                 builddir,target,cpdir,target),scripttest,collectivelog)
      returnmsg = 'finished'
    elif type == 'target' and exist(chrootdir+builddir+'/RPMS/' + target,fs) or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+target, builddir+'/RPMS/'+target, fs+'*.mvl',
                           editionrpmbin+' '+extra+target+'-linux --nodeps',collectivelog)
      copysrcrpm('filesystem',collectivelog)
      systemCmd('%s %s/%s/RPMS/%s/filesystem*.mvl %s/%s/target' % (cpall,chrootdir,
                 builddir,target,cpdir,target),scripttest,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = fs + " for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: ' + fs + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: ' + fs + ' for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: ' + fs + ' for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = fs + ' for ' + target + ' build failed'
  cleanbuilddirs()
  mstop(fs,collectivelog,scripttest)
  return returnmsg

def buildheaders():
  returnmsg = ''
  getReqFiles = 1
  collectivelog = '%s/%s' % (collectivelogdir,'kernel-headers')
  # build kernel headers
  bcmd = 'ba --define \\"' + kbv + ' ' + kernel + '\\" --define \\"' + khv + ' ' + hhlversion + '\\" --define \\"_mvl_selinux ' + selinux + '\\" ' + '--target=' + target
  if product in ('dev','fe','product'):
    kernelapp = 'kernel-headers'
  elif product not in ('dev','fe'):
    kernelapp = 'kernel-headers-product'
  collectivelog = '%s/%s' % (collectivelogdir,kernelapp)
  # keep the ' at' part in there so the collective doesn't get overwritten by kernel-headers-product
  mstart('%s at' % kernelapp,collectivelog,scripttest)
  getdiskspace(hostname)
  currentdir = os.getcwd()
  if os.path.exists(kspecpath) and not gitkernel:
    os.chdir(kspecpath)
    if os.path.exists('rpm/SOURCES'):
      for srcFile in os.listdir('rpm/SOURCES'):
        systemCmd('%s rpm/SOURCES/%s %s/%s/SOURCES' % (cpall,srcFile,chrootdir,builddir),scripttest,collectivelog)
    else:
      printflush('ERROR: no SOURCES for kernel-headers...check if host-kernel built.',collectivelog,scripttest)
    if os.path.exists('rpm/SPECS'):
      systemCmd('%s rpm/SPECS/* %s/%s/SPECS' % (cpall,chrootdir,builddir),scripttest,collectivelog)
    else:
      printflush('ERROR: no SPECS for kernel-headers...check if host-kernel built.',collectivelog,scripttest)
    os.chdir(currentdir)
    instres = 0
    if rpmb(builddir+'/SPECS/'+kernelapp+'.spec',editionrpmbuild,bcmd,collectivelog,getReqFiles) or scripttest == 1:
      if exist(chrootdir+builddir+'/RPMS/' + target,kernelapp) or scripttest == 1:
        instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,kernelapp+'-'+kernel+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
        copysrcrpm(kernelapp,collectivelog)
        systemCmd('%s %s/%s/RPMS/%s/%s-*.mvl %s/%s/target' % (cpall,chrootdir,builddir,target,
                   kernelapp,cpdir,target),scripttest,collectivelog)
        returnmsg = 'finished'
      elif not exist(chrootdir+builddir+'/RPMS/' + target,kernelapp+'-'):
        returnmsg = kernelapp + " for " + target + " built but wasn't installed...check paths"
      if instres:
        printflush('BUILD ERROR: ' + kernelapp + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
      else:
        printflush('BUILT: ' + kernelapp + ' for ' + target + ' built.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: ' + kernelapp + ' for ' + target + ' did not build.',collectivelog,scripttest)
      returnmsg = kernelapp + ' for ' + target + ' build failed'
  elif os.path.exists(kspecpath) and gitkernel:
    systemCmd('%s %s %s/%s' % (cpall,kspecpath,chrootdir,builddir),scripttest,collectivelog)
    instres = 1
    if gitmake("mvl-"+kernelapp,"cd "+cvspaths["git-kernel"][2]+"; ",editionrpmbuild,collectivelog,getReqFiles) or scripttest == 1:
      if exist(chrootdir+builddir+'/'+cvspaths['git-kernel'][2]+'/MONTAVISTA-BUILD/RPMS/' + target,kernelapp) or scripttest == 1:
        instres = rpminstall(chrootdir+builddir+'/'+cvspaths['git-kernel'][2]+'/MONTAVISTA-BUILD/RPMS/'+target,builddir+'/'+cvspaths['git-kernel'][2]+'/MONTAVISTA-BUILD/RPMS/'+ target,kernelapp+'-'+kernel+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
        systemCmd('%s %s/%s/%s/MONTAVISTA-BUILD/SRPMS/*.src.rpm %s/SRPMS' % (cpall,chrootdir,builddir,cvspaths['git-kernel'][2],cpdir),scripttest,collectivelog)
        systemCmd('%s %s/%s/%s/MONTAVISTA-BUILD/RPMS/%s/%s-*.mvl %s/%s/target' % (cpall,chrootdir, builddir,cvspaths['git-kernel'][2],target,kernelapp,cpdir,target),scripttest,collectivelog)
        returnmsg = 'finished'
      elif not exist(chrootdir+builddir+'/'+cvspaths['git-kernel'][2]+'/MONTAVISAT-BUILD/RPMS/'+target,kernelapp+'-'):
        returnmsg = kernelapp + " for " + target + " built but wasn't installed...check paths"
      if instres:
        printflush('BUILD ERROR: ' + kernelapp + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
      else:
        printflush('BUILT: ' + kernelapp + ' for ' + target + ' built.',collectivelog,scripttest)
    else:
      printflush('BUILD ERROR: ' + kernelapp + ' for ' + target + ' did not build.',collectivelog,scripttest)
    systemCmd('rm -rf %s/%s/%s' % (chrootdir,builddir,cvspaths['git-kernel'][2]),scripttest,collectivelog)
      
  cleanbuilddirs()
  mstop(kernelapp,collectivelog,scripttest)
  return returnmsg

def buildbootstrapglibc():
  returnmsg = ''
  # build bootstrap glibc or uclibc
  if string.find(target,'uclibc') > -1:
    glibcdir = 'uclibc'
  else:
    glibcdir = 'glibc'
  bcmd = 'bb --define \\"_mvl_selinux %s\\" --target=%s-linux' % (selinux,target)
  glibcapp = glibcdir + '-bootstrap'
  collectivelog = '%s/%s' % (collectivelogdir,glibcapp)
  mstart(glibcapp,collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest == 1:
    systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  if rpmb(builddir + '/SPECS/'+glibcapp+'.spec',"PARALLELMFLAGS='"+par_flag+"' "+editionrpmbuild,bcmd,collectivelog) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/' + target,glibcapp) or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,glibcapp+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = glibcapp + " for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: ' + glibcapp + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: ' + glibcapp + ' for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: ' + glibcapp + ' for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = glibcapp + ' for ' + target + ' build failed'
  cleanbuilddirs()
  mstop(glibcapp,collectivelog,scripttest)
  mstop(glibcdir + '-bootstrap',collectivelog,scripttest)
  return returnmsg

def buildbinutils():
  returnmsg = ''
  bcmd = "ba --cross=" + target
  collectivelog = '%s/%s' % (collectivelogdir,'cross-binutils')
  mstart('cross-binutils',collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest == 1:
    systemCmd('%s %s/binutils/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/binutils/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  if rpmb(builddir + '/SPECS/cross-binutils.spec',editionrpmbuild+dmake,bcmd,collectivelog) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/' + hostarch,'cross-' + target + '-binutils') or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir+'/RPMS/'+hostarch,'cross-'+target+'-binutils*.mvl',editionrpmbin,collectivelog)
      copysrcrpm('cross-binutils',collectivelog)
      systemCmd('%s %s/%s/RPMS/%s/cross-%s-binutils*.mvl %s/%s/cross/%s' % (cpall,chrootdir,
                 builddir,hostarch,target,cpdir,target,hostname),scripttest,collectivelog)
      # move testsuite rpms to testing sub directory
      systemCmd('mv %s/%s/cross/%s/*testsuite* %s/%s/cross/%s/testing' % (cpdir,target,hostname,
                 cpdir,target,hostname),scripttest,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = "cross-binutils for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: cross-binutils for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: cross-binutils for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: cross-binutils for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = 'cross-binutils for ' + target + ' build failed'
  cleanbuilddirs()
  mstop('cross-binutils',collectivelog,scripttest)
  return returnmsg

def buildbootstrap(type):
  returnmsg = ''
  bcmd = "bb --cross=" + target
  collectivelog = '%s/%s' % (collectivelogdir,'cross-gcc-bootstrap-%s' % type)
  mstart('cross-gcc-bootstrap-%s' % type,collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest == 1:
    systemCmd('%s %s/gcc/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/gcc/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
  if type == "shared":
    printflush('Removing cross-gcc-bootstrap-static...',collectivelog,scripttest)
    for bsgcc in rpmqa('gcc-bootstrap',editionrpmbin):
      rpmev(string.strip(bsgcc),editionrpmbin) 
  instres = 0
  if rpmb(builddir + '/SPECS/cross-gcc-bootstrap-' + type + '.spec',editionrpmbuild+dmake,bcmd,collectivelog) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/' + hostarch,'cross-' + target + '-gcc-bootstrap-'+type) or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir+'/RPMS/'+hostarch,'cross-'+target+'-gcc-bootstrap*.mvl',editionrpmbin,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = "cross-gcc-bootstrap-" + type + " for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: cross-gcc-bootstrap-' + type + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: cross-gcc-bootstrap-' + type + ' for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: cross-gcc-bootstrap-' + type + ' for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = 'cross-gcc-bootstrap-' + type + ' for ' + target + ' build failed'
  cleanbuilddirs()
  mstop('cross-gcc-bootstrap-%s' % type,collectivelog,scripttest)
  return returnmsg

def buildlibopt():
  returnmsg = ''
  bcmd = "ba --cross=" + target
  collectivelog = '%s/%s' % (collectivelogdir,'cross-libopt')
  mstart('cross-libopt',collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest == 1:
    systemCmd('%s %s/libopt %s/%s' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  cmd = 'make -C libopt NEW_SOURCE=yes RPM=\"%s --define \'_topdir `pwd`\' --define \'_mvl_build_id %s\' --define \'vendor MontaVista Software, Inc.\' --define \'packager <source@mvista.com>\' --cross=%s-linux\" rpm' % (editionrpmbuild,buildid,target)
  if not scripttest:
    f_buildfile = open('%s/%s/liboptbuild.cmd' % (chrootdir,builddir),'w+')
    f_buildfile.write(cmd)
    f_buildfile.close()
  else:
    printflush("command: f_buildfile = open('%s/%s/liboptbuild.cmd' % (chrootdir,builddir),'w+')",collectivelog,scripttest)
    printflush("command: f_buildfile.write(cmd)",collectivelog,scripttest)
    printflush("command: f_buildfile.close()",collectivelog,scripttest)
  systemCmd('chmod +x %s/%s/liboptbuild.cmd' % (chrootdir,builddir),scripttest,collectivelog)
  chroot(hostname,'cd ' + builddir + '; ./liboptbuild.cmd',scripttest,collectivelog)
  if wrotecheck(hostname) or scripttest == 1: 
    if exist(chrootdir+builddir+'/RPMS/noarch','cross-' + target + '-libopt') or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir+'/RPMS/noarch','cross-' + target +'-libopt*.mvl',editionrpmbin,collectivelog)
      copysrcrpm('cross-libopt',collectivelog)
      systemCmd('%s %s/%s/RPMS/noarch/cross-%s-libopt*.mvl %s/%s/cross/common' % (cpall,chrootdir,
                 builddir,target,cpdir,target),scripttest,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = "cross-libopt for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: cross-libopt for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: cross-libopt for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: cross-libopt for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = 'cross-libopt for ' + target + ' build failed'
  cleanbuilddirs()
  systemCmd('rm -rf %s/%s/libopt' % (chrootdir,builddir),scripttest,collectivelog)
  getdiskspace(hostname)
  mstop('cross-libopt',collectivelog,scripttest)
  return returnmsg

def buildaltglibc(abi):
  l_abis = string.split(abi,',')
  returnmsg = ''
  getReqFiles = 1
  if string.find(target,'uclibc') > -1:
    glibcdir = 'uclibc'
  else:
    glibcdir = 'glibc'
  if product in ('dev',) and glibcdir != 'uclibc':
    glibcapp = glibcdir + '-bootstrap-libs'
    getReqFiles = 0
  else:
    glibcapp = glibcdir
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest:
    systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest)
    systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest)
    while l_abis:
      abi = l_abis[0]
      bcmd = 'ba --target=%s-linux --define \\"_mvl_selinux %s\\" --define \\"_mvl_multilib %s\\"' % (target,selinux,abi)
      collectivelog = '%s/%s' % (collectivelogdir,glibcapp + '-' + abi)
      mstart(glibcapp + '-' + abi,collectivelog,scripttest)
      getdiskspace(hostname)
      instres = 0
      buildresults = rpmb(builddir + '/SPECS/'+glibcapp+'.spec',"PARALLELMFLAGS='"+par_flag+"' "+editionrpmbuild,bcmd,collectivelog,getReqFiles)
      l_abis.remove(abi)
      if exist(chrootdir+builddir+'/RPMS/'+target,glibcdir) and not l_abis and buildresults or scripttest == 1:
        for bglibc in rpmqa(glibcdir + '-bootstrap',editionrpmbin+' --target='+target+'-linux'):
          rpmev(string.strip(bglibc),editionrpmbin+' --target='+target+'-linux')
        instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,glibcapp+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
        systemCmd('%s %s/%s/RPMS/%s/%s*.mvl %s/%s/target' % (cpall,chrootdir,builddir,target,glibcdir,cpdir,target),scripttest,collectivelog)
        # move testsuite rpms to testing sub directory
        systemCmd('mv %s/%s/target/*testsuite* %s/%s/target/testing' % (cpdir,target,cpdir,target),scripttest,collectivelog)
        returnmsg = 'finished'
      elif buildresults:
        returnmsg = glibcapp + "-" + abi + " for " + target + " built but wasn't installed"
      else:
        returnmsg =  glibcapp + '-' + abi + ' for ' + target + ' build failed'
      if instres and buildresults:
        printflush('BUILD ERROR: ' + glibcapp + '-' + abi + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
      elif not buildresults:
        printflush('BUILD ERROR: ' + glibcapp + '-' + abi + ' for ' + target + ' did not build.',collectivelog,scripttest)
      else:
        printflush('BUILT: ' + glibcapp + '-' + abi + ' for ' + target + ' built.',collectivelog,scripttest)
      getdiskspace(hostname)
      mstop(glibcapp + '-' + abi,collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: no toolchain repo defined.')
    returnmsg =  glibcapp + '-' + abi + ' for ' + target + ' build failed'
  cleanbuilddirs()
  return returnmsg

def buildglibc():
  returnmsg = ''
  getReqFiles = 1
  if string.find(target,'uclibc') > -1:
    glibcdir = 'uclibc'
  else:
    glibcdir = 'glibc'
  bcmd = 'ba --target=%s-linux --define \\"_mvl_selinux %s\\"' % (target,selinux)
  if product in ('dev',) and glibcdir != 'uclibc':
    glibcapp = glibcdir + '-bootstrap-libs'
    getReqFiles = 0
  else:
    glibcapp = glibcdir
  collectivelog = '%s/%s' % (collectivelogdir,glibcdir)
  mstart(glibcapp,collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest:
    systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],glibcdir,chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  if rpmb(builddir + '/SPECS/'+glibcapp+'.spec',"PARALLELMFLAGS='"+par_flag+"' "+editionrpmbuild,bcmd,collectivelog,getReqFiles) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/'+target,glibcdir) or scripttest == 1:
      if target not in multilibtargets.keys():
        for bglibc in rpmqa(glibcdir + '-bootstrap',editionrpmbin+' --target='+target+'-linux'):
          rpmev(string.strip(bglibc),editionrpmbin+' --target='+target+'-linux')
        instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,glibcapp+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
        systemCmd('%s %s/%s/RPMS/%s/%s*.mvl %s/%s/target' % (cpall,chrootdir,builddir,target,glibcdir,cpdir,target),scripttest,collectivelog)
        # move testsuite rpms to testing sub directory
        systemCmd('mv %s/%s/target/*testsuite* %s/%s/target/testing' % (cpdir,target,cpdir,target),scripttest,collectivelog)
      copysrcrpm(glibcdir,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = glibcapp + " for " + target + " built but wasn't installed...check paths"
    if instres:
      printflush('BUILD ERROR: ' + glibcapp + ' for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: ' + glibcapp + ' for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: ' + glibcapp + ' for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg =  glibcapp + ' for ' + target + ' build failed'
  getdiskspace(hostname)
  mstop(glibcapp,collectivelog,scripttest)
  if target not in multilibtargets.keys():
    cleanbuilddirs()
  return returnmsg

def buildgcc():
  returnmsg = ''
  bcmd = 'ba --cross='+target+'-linux'
  if gcclicense:
    bcmd = bcmd + ' --define \\"_mvl_gcc_license ' + gcclicense + '\\"'
  collectivelog = '%s/%s' % (collectivelogdir,'cross-gcc')
  mstart('cross-gcc',collectivelog,scripttest)
  getdiskspace(hostname)
  if 'toolchain' in cvspaths.keys() or scripttest:
    systemCmd('%s %s/gcc/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
    systemCmd('%s %s/gcc/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['toolchain'][0],chrootdir,builddir),scripttest,collectivelog)
  instres = 0
  # remove bootstrap gcc and rebuild gcc
  for bgcc in rpmqa('cross-' + target + '-gcc-bootstrap',editionrpmbin):
    rpmev(string.strip(bgcc),editionrpmbin)
  spec = 'cross-gcc.spec'
  if rpmb(builddir + '/SPECS/'+spec,editionrpmbuild+dmake,bcmd,collectivelog) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/'+hostarch,'cross-' + target + '-gcc') or scripttest == 1:
      # remove bootstrap gcc and rebuild gcc
      for bgcc in rpmqa('cross-' + target + '-gcc-bootstrap',editionrpmbin):
        rpmev(string.strip(bgcc),editionrpmbin)
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir+'/RPMS/'+hostarch,'cross-' + target + '-*.mvl',editionrpmbin,collectivelog)
      copysrcrpm('cross-gcc',collectivelog)
      systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/cross/%s' % (cpall,chrootdir,builddir,hostarch,
                cpdir,target,hostname),scripttest,collectivelog)
      # move testsuite rpms to testing sub directory
      systemCmd('mv %s/%s/cross/%s/*testsuite* %s/%s/cross/%s/testing' % (cpdir,target,hostname,
                 cpdir,target,hostname),scripttest,collectivelog)
      returnmsg = 'finished'
    else:
      returnmsg = "cross-gcc for " + target + " built but wan't installed...check paths"
    if instres:
      printflush('BUILD ERROR: cross-gcc for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: cross-gcc for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: cross-gcc for ' + target + ' did not build.',collectivelog,scripttest)
    returnmsg = 'cross-gcc for ' + target + ' build failed'
  cleanbuilddirs()
  mstop('cross-gcc',collectivelog,scripttest)
  return returnmsg

def buildtargbinutils():
  getReqFiles = 1
  bcmd = 'ba --target=%s-linux --define \\"_mvl_selinux %s\\"' % (target,selinux)
  spec = 'binutils.spec'
  collectivelog = '%s/%s' % (collectivelogdir,'binutils')
  if rpmb(builddir + '/SPECS/'+spec,editionrpmbuild+dmake,bcmd,collectivelog,getReqFiles) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/'+target,'binutils-2'):
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
      copysrcrpm('binutils',collectivelog)
      systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/target' % (cpall,chrootdir,builddir,target,cpdir,target),scripttest,collectivelog)
      # move testsuite rpms to testing sub directory
      systemCmd('mv %s/%s/target/*testsuite* %s/%s/target/testing' % (cpdir,target,cpdir,target),scripttest,collectivelog)
    else:
      printflush("binutils for " + target + " built but wasn't installed...check paths",collectivelog,scripttest)
    if instres:
      printflush('BUILD ERROR: binutils for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: binutils for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: binutils for ' + target + ' did not build.',collectivelog,scripttest)
  cleanbuilddirs()

def buildtarggcc():
  getReqFiles = 1
  bcmd = 'ba --target=%s-linux --define \\"_mvl_selinux %s\\"' % (target,selinux)
  spec = 'gcc.spec'
  instres = 0
  collectivelog = '%s/%s' % (collectivelogdir,'gcc')
  if rpmb(builddir + '/SPECS/'+spec,editionrpmbuild+dmake,bcmd,collectivelog,getReqFiles) or scripttest == 1:
    if exist(chrootdir+builddir+'/RPMS/'+target,'gcc') or scripttest == 1:
      instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+ target,'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
      copysrcrpm('gcc',collectivelog)
      systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/target' % (cpall,chrootdir,builddir,target,cpdir,target),scripttest,collectivelog)
      # move testsuite rpms to testing sub directory
      systemCmd('mv %s/%s/target/*testsuite* %s/%s/target/testing' % (cpdir,target,cpdir,target),scripttest,collectivelog)
    else:
      printflush("gcc for " + target + " built but wasn't installed...check paths",collectivelog,scripttest)
    if instres:
      printflush('BUILD ERROR: gcc for ' + target + ' built but did not install.',collectivelog,scripttest)
    else:
      printflush('BUILT: gcc for ' + target + ' built.',collectivelog,scripttest)
  else:
    printflush('BUILD ERROR: gcc for ' + target + ' did not build.',collectivelog,scripttest)
  cleanbuilddirs()

#------------------------------------------------------------------------------------------
# This is the function that gets called by buildhhl.py
#------------------------------------------------------------------------------------------
if len(sys.argv) != 4:
  printflush("\nbuildcore.py <data file> <target> <hostname>")
  printflush("\n# of args = " + str(len(sys.argv)))
  printflush("\nHere are the args:")
  for x in sys.argv:
    print x
  sys.exit(1)

datafile = sys.argv[1]
target = sys.argv[2]
hostname = sys.argv[3]

if os.path.exists(datafile):
  exec(open(datafile))
else:
  mstart('buildcore-script-setup')
  printflush("No datafile found.  Stopping build.")
  #os.system('touch %s/buildcore-%s-done' % (logdir,hostname))
  printflush("Finished %s at %s" % (sys.argv[0],gettime()))
  mstop('buildcore-script-setup')
  sys.exit(1)

collectivelogdir = '%s/%s/host/%s' % (collectivelogdir,target,hostname)
makeDir(collectivelogdir,scripttest)
collectivelog = '%s/%s' % (collectivelogdir,'buildcore-script-setup')
mstart('buildcore-script-setup',collectivelog,scripttest)
printflush('targethost = ' + targethost,collectivelog,scripttest)
getdiskspace(hostname)
printflush('<' + sys.argv[0] + '>: starting buildcore for ' + target + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...',collectivelog,scripttest)
printflush("datafile = %s" % datafile,collectivelog,scripttest)

commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
commonrpmbuild = commonrpmbin + 'build'
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
editionrpmbuild = editionrpmbin + 'build'
gitkernel = 0
if 'mvl-kernel-26' in cvspaths.keys():
  kspecpath = cvspaths['mvl-kernel-26'][0]
else:
  for repo in cvspaths.keys():
    if string.find(repo,'git') > -1:
      kspecpath = cvspaths[repo][0]
      gitkernel = 1
  if not gitkernel:
    kspecpath = 'null'
printflush('kspecpath = ' + kspecpath,collectivelog,scripttest)
node = string.strip(os.popen('hostname').read())
printflush('node = ' + node,collectivelog,scripttest)
scriptdir = os.getcwd()

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
systemCmd('mkdir -p %s%s' % (chrootdir,chrootcpdir),scripttest,collectivelog)

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

printflush('architecture is ' + target,collectivelog,scripttest)
printflush('kernel version is ' + kernel + '_' + hhlversion,collectivelog,scripttest)

#----------------------------------------------------------------------
# uninstall any previous packages and clean build areas
#----------------------------------------------------------------------
printflush('Cleaning %s/%s on %s...' % (chrootdir,builddir,node),collectivelog,scripttest)
if os.path.exists('%s/%s' % (chrootdir,builddir)):
  os.chdir('%s/%s' % (chrootdir,builddir))
elif scripttest == 1:
  printflush("cd %s/%s" % (chrootdir,builddir),collectivelog,scripttest)
if foundation != 'skip':
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/host/' + hostname,scripttest,collectivelog)
  if product == 'cge':
    systemCmd('mkdir -p  RPMS/install/host/' + hostname + '/optional',scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/host/common',scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/cross/common',scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/cross/' + hostname,scripttest,collectivelog)
  systemCmd('mkdir -p  RPMS/install/target',scripttest,collectivelog)
  if hostname == 'solaris8':
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
else:
  systemCmd('rm -rf BUILD SOURCES SPECS SRPMS RPMS/i386 RPMS/noarch',scripttest,collectivelog)
  systemCmd('mkdir -p BUILD SOURCES SPECS SRPMS',scripttest,collectivelog)
  if hostname == 'solaris8':
    systemCmd('chown -R build:engr BUILD SOURCES SPECS SRPMS RPMS',scripttest,collectivelog)
os.chdir(scriptdir)
uninstallbuild()

speciallsps = ()

if not os.path.exists(cpdir + '/' + target):
  systemCmd('mkdir -p ' + cpdir + '/' + target,scripttest,collectivelog)
minReqApps = '%s/%s/MVL-%s-apps-%s-%s' % (cpdir,target,edition,target,buildid)
if not os.path.exists(minReqApps):
  systemCmd('touch %s' % minReqApps,scripttest,collectivelog)
#if not os.path.exists(cpdir + '/' + target + '/target/apps'):
#  os.system('mkdir -p ' + cpdir + '/' + target + '/target/apps')
#if not os.path.exists(cpdir + '/' + target + '/target/libs'):
#  os.system('mkdir -p ' + cpdir + '/' + target + '/target/libs')
if not os.path.exists(cpdir + '/' + target + '/target/optional'):
  systemCmd('mkdir -p ' + cpdir + '/' + target + '/target/optional',scripttest,collectivelog)
#if not os.path.exists(cpdir + '/' + target + '/target/provides'):
#  os.system('mkdir -p ' + cpdir + '/' + target + '/target/provides')
if not os.path.exists(cpdir + '/' + target + '/target/testing'):
  systemCmd('mkdir -p ' + cpdir + '/' + target + '/target/testing',scripttest,collectivelog)
if not os.path.exists(cpdir + '/' + target + '/lsps') and product != 'proadk':
  systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps',scripttest,collectivelog)
if not os.path.exists(cpdir + '/installer_rpms/cross/' + target):
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/cross/' + target,scripttest,collectivelog)
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/install_area/cross/' + target,scripttest,collectivelog)
if not os.path.exists(cpdir + '/installer_rpms/target/' + target):
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/target/' + target,scripttest,collectivelog)
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/install_area/target/' + target,scripttest,collectivelog)
if not os.path.exists(cpdir + '/installer_rpms/lsps/' + target) and product != 'proadk':
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/lsps/' + target,scripttest,collectivelog)
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/install_area/lsps/' + target,scripttest,collectivelog)
if not os.path.exists(cpdir + '/installer_rpms/addon') and product != 'proadk':
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/addon/',scripttest,collectivelog)
  systemCmd('mkdir -p ' + cpdir + '/installer_rpms/install_area/addon/',scripttest,collectivelog)
if target == selfhosttarget:
  if not os.path.exists(cpdir + '/installer_rpms/self-hosted/' + target):
    systemCmd('mkdir -p ' + cpdir + '/installer_rpms/self-hosted/' + target,scripttest,collectivelog)
    systemCmd('mkdir -p ' + cpdir + '/installer_rpms/install_area/self-hosted/' + target,scripttest,collectivelog)
if not os.path.exists(cpdir + '/' + target + '/cross'):
  systemCmd('mkdir -p ' + cpdir + '/' + target + '/cross',scripttest,collectivelog)
for host in hosts:
  if not os.path.exists(cpdir + '/' + target + '/cross/' + host + '/testing'):
    systemCmd('mkdir -p ' + cpdir + '/' + target + '/cross/' + host + '/testing',scripttest,collectivelog)
for host in chroothosts:
  if not os.path.exists(cpdir + '/' + target + '/cross/' + host + '/testing'):
    systemCmd('mkdir -p ' + cpdir + '/' + target + '/cross/' + host + '/testing',scripttest,collectivelog)
if not os.path.exists(cpdir + '/' + target + '/cross/common'):
  systemCmd('mkdir -p ' + cpdir + '/' + target + '/cross/common',scripttest,collectivelog)
#if not os.path.exists(cpdir + '/' + target + '/cross/common/adk'):
#  os.system('mkdir -p ' + cpdir + '/' + target + '/cross/common/adk')

#--------------------------------------------------------------------------
# copy common- and host- rpms to install prior to building any apps
#--------------------------------------------------------------------------
getdiskspace(hostname)
if os.path.exists('%s/%s' % (chrootdir,chrootcpdir)):
  os.chdir('%s/%s' % (chrootdir,chrootcpdir))
systemCmd('%s %s/host/common/*.mvl host/common' % (cpall,cpdir),scripttest,collectivelog)
systemCmd('%s %s/host/common/optional/*.mvl host/common' % (cpall,cpdir),scripttest,collectivelog)
systemCmd('%s %s/host/%s/*.mvl host/%s' % (cpall,cpdir,hostname,hostname),scripttest)
if product == 'cge':
  systemCmd('%s %s/host/%s/optional/*.mvl host/%s/optional' % (cpall,cpdir,hostname,hostname),scripttest,collectivelog)
getdiskspace(hostname)
mstop('buildcore-script-setup',collectivelog,scripttest)
os.chdir(scriptdir)
#-----------------------------------------------------------------------------
# Install rpm(s)
#-----------------------------------------------------------------------------
collectivelog = '%s/%s' % (collectivelogdir,'common-rpm_install')
mstart('common-rpm_install',collectivelog,scripttest)
getdiskspace(hostname)
printflush('Installing (rpmc2cpio) previously built version of common-rpm...',collectivelog,scripttest)
chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest,collectivelog)
if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
  # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install
  printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio:",collectivelog,scripttest)
  systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
  systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
  printflush("try recopying common-rpm and re-installing...",collectivelog,scripttest)
  systemCmd('cp -a %s/host/%s/common-rpm* %s/%s/host/%s' % (foundation,hostname,chrootdir,chrootcpdir,hostname),scripttest,collectivelog)
  printflush('Installing (rpmc2cpio) previously built version of common-rpm a second time...',collectivelog,scripttest)
  chroot(hostname,'cd /; for each in /home/build/RPMS/install/host/' + hostname + '/common-rpm-*; do ' + rpm2cpio + ' \$each > /tmp/rpm2cpio-tmp.cpio; cpio -iud < /tmp/rpm2cpio-tmp.cpio; if [ \$? -ne 0 ]; then echo \$each did not install; mv /tmp/rpm2cpio-tmp.cpio /home/build/RPMS/install/common-rpm-install-failed; fi done',scripttest,collectivelog)
  if os.path.exists(chrootdir + '/' + chrootcpdir + '/common-rpm-install-failed'):
    # list the contents of /tmp/rpm2cpio-tmp.cpio for the package that failed to install a second time
    printflush("Here's the contents of /tmp/rpm2cpio-tmp.cpio (2nd try):",collectivelog,scripttest)
    systemCmd('cat %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
    printflush("No use continuing the build...",collectivelog,scripttest)
    systemCmd('rm -f %s/%s/common-rpm-install-failed' % (chrootdir,chrootcpdir),scripttest,collectivelog)
    systemCmd('touch %s/buildremotehost-%s-done' % (logdir,hostname),scripttest,collectivelog)
    printflush("Finished %s at %s" % (sys.argv[0],gettime()),collectivelog,scripttest)
    getdiskspace(hostname)
    mstop('common-rpm_install',collectivelog,scripttest)
    sys.exit(1)
getdiskspace(hostname)
mstop('common-rpm_install',collectivelog,scripttest)

collectivelog = '%s/%s' % (collectivelogdir,'common_hostarch_install')
mstart('common_hostarch_install',collectivelog,scripttest)
getdiskspace(hostname)
printflush('Installing host/' + hostname + '/common* with common-rpm',collectivelog,scripttest)
rdir = '%s/host/%s' % (chrootcpdir,hostname)
# remove --nodeps when error checking is put in
instres = rpminstall(chrootdir+rdir,rdir,'common-*.mvl',commonrpmbin,collectivelog)
if instres:
  printflush('BUILD ERROR: host/' + hostname + '/common* install failed.',collectivelog,scripttest)
  printflush('Installing with --nodeps so build will continue...',collectivelog,scripttest)
  instres = rpminstall(chrootdir+rdir,rdir,'common-*.mvl --nodeps',commonrpmbin,collectivelog)
  if instres:
    printflush('BUILD ERROR: host/' + hostname + '/common* install failed using --nodeps.',collectivelog,scripttest)
else:
  printflush('BUILT: host/' + hostname + '/common* install succeeded.',collectivelog,scripttest)
getdiskspace(hostname)
mstop('common_hostarch_install',collectivelog,scripttest)

collectivelog = '%s/%s' % (collectivelogdir,'common_noarch_install')
mstart('common_noarch_install',collectivelog,scripttest)
getdiskspace(hostname)
printflush('Installing host/common/common* with common-rpm',collectivelog,scripttest)
rdir = '%s/host/common' % chrootcpdir
instres = rpminstall(chrootdir+rdir,rdir,'common-*.mvl',commonrpmbin,collectivelog)
if instres:
  printflush('BUILD ERROR: host/common/common* install failed.',collectivelog,scripttest)
  printflush('Installing with --nodeps so build will continue...',collectivelog,scripttest)
  instres = rpminstall(chrootdir+rdir,rdir,'common-*.mvl --nodeps',commonrpmbin,collectivelog)
  if instres:
    printflush('BUILD ERROR: host/common/common* install failed using --nodeps.',collectivelog,scripttest)
else:
  printflush('BUILT: host/common/common* install succeeded.',collectivelog,scripttest)
getdiskspace(hostname)
mstop('common_noarch_install',collectivelog,scripttest)

collectivelog = '%s/%s' % (collectivelogdir,'host-rpm_install')
mstart('host-rpm_install',collectivelog,scripttest)
getdiskspace(hostname)
rdir = '%s/host/%s' % (chrootcpdir,hostname)
printflush('using rpm2cpio to install host-rpm',collectivelog,scripttest)
chroot(hostname,'cd /; ' + rpm2cpio + ' ' + rdir + '/host-rpm-* | cpio -iud',scripttest,collectivelog)
printflush('Installing host-rpm using host-rpm...',collectivelog,scripttest)
if hostname == 'solaris8':
  instres = rpminstall(chrootdir+rdir,rdir,'host-rpm*.mvl --nodeps',editionrpmbin,collectivelog)
else:
  instres = rpminstall(chrootdir+rdir,rdir,'host-rpm*.mvl',editionrpmbin,collectivelog)
if instres:
  printflush('BUILD ERROR: host-rpm install failed.',collectivelog,scripttest)
else:
  printflush('BUILT: host-rpm install succeeded.',collectivelog,scripttest)
getdiskspace(hostname)
mstop('host-rpm_install',collectivelog,scripttest)

collectivelog = '%s/%s' % (collectivelogdir,'host_noarch_install')
mstart('host_noarch_install',collectivelog,scripttest)
getdiskspace(hostname)
rdir = '%s/host/common' % chrootcpdir
instres = rpminstall(chrootdir+rdir,rdir,'host*.mvl',editionrpmbin,collectivelog)
if instres:
  printflush('BUILD ERROR: host/common/host* install failed.',collectivelog,scripttest)
else:
  printflush('BUILT: host/common/host* install succeeded.',collectivelog,scripttest)
getdiskspace(hostname)
mstop('host_noarch_install',collectivelog,scripttest)

collectivelog = '%s/%s' % (collectivelogdir,'host_hostarch_install')
mstart('host_hostarch_install',collectivelog,scripttest)
getdiskspace(hostname)
rdir = '%s/host/%s' % (chrootcpdir,hostname)
if os.path.exists('%s/%s' % (chrootdir,rdir)):
  os.chdir('%s/%s' % (chrootdir,rdir))
errmsg = "BUILD ERROR: \n"
instres = 0
for installthis in os.popen('ls host-* | grep -v %s | grep -v %s | grep -v %s | grep -v %s | grep -v %s | grep -v %s | grep -v %s' % ('host-rpm','elfutils','comerr','e2fslibs','expat','perl-XML-Parser','ddd')).readlines():
  printflush("Installing %s ..." % string.strip(installthis),collectivelog,scripttest)
  if rpminstall(chrootdir+rdir,rdir,string.strip(installthis),editionrpmbin,collectivelog):
    errmsg = errmsg + '\t\t' + string.strip(installthis) + ' did not install'
    instres = 1
os.chdir(scriptdir)
# move these to defaultdata.dat and <edition>data.dat
dhostrpms = ["comerr","e2fslibs","ddd"]
for dhr in dhostrpms:
  if rpminstall(chrootdir+rdir,rdir,'host-' + dhr + '*',editionrpmbin,collectivelog):
    errmsg = errmsg + '\t\t' + 'host-' + dhr + '* did not install'
    instres = 1
if product == 'cge':
  rdir = '%s/host/%s/optional' % (chrootcpdir,hostname)
  if os.path.exists('%s/%s' % (chrootdir,rdir)):
    os.chdir('%s/%s' % (chrootdir,rdir))
  dhostrpms = ["expat","perl-XML-Parser","tool-perl"]
  for installthis in dhostrpms:
    printflush("Installing host-%s* ..." % installthis,collectivelog,scripttest)
    if rpminstall(chrootdir+rdir,rdir,'host-'+installthis+'*',editionrpmbin,collectivelog):
      errmsg = errmsg + '\t\thost-' + installthis + ' did not install'
      instres = 1
  os.chdir(scriptdir)
if instres:
  printflush(errmsg,collectivelog,scripttest)
else:
  printflush("BUILT: host/" + hostname + "/host* install succeeded.",collectivelog,scripttest)
getdiskspace(hostname)
mstop('host_hostarch_install',collectivelog,scripttest)

printflush('Starting build...')

##################################################################################
# call functions to build filesystem, headers, binutils, bootstrap gcc, glibc, gcc
##################################################################################
if product in ('dev','fe'):
  # Build toolchain for foundation
  printflush('<' + sys.argv[0] + '>: starting toolchain at ' + gettime())
  result = buildfilesystem('cross')
  if result == 'finished':
    result = buildfilesystem('target')
    if result == 'finished':
      result = buildheaders()
      if result == 'finished':
        result = buildbinutils()
        if result == 'finished':
          result = buildbootstrap('static')
          if result == 'finished':
            #if string.find(target,'uclibc') == -1:
            result = buildbootstrapglibc()
            if result == 'finished':
              #if string.find(target,'uclibc') == -1:
              result = buildbootstrap('shared')
              if result == 'finished':
                result = buildlibopt()
                if result == 'finished':
                  result = buildglibc()
                  if result == 'finished' and target in ('ppc_9xx',):
                      result = buildaltglibc('64')
                      if result == 'finished':
                        result = buildgcc()
                  elif result == 'finished' and target in ('x86_amd64','x86_em64t'):
                      result = buildaltglibc('32')
                      if result == 'finished':
                        result = buildgcc()
                  elif result == 'finished' and string.find(target,'mips64') > -1:
                      result = buildaltglibc('64')
                      if result == 'finished':
                        result = buildgcc()
                  elif result == 'finished':
                    result = buildgcc()
  printflush('<' + sys.argv[0] + '>: finished toolchain at ' + gettime())
else:
  # Install foundation toolchain
  if os.path.exists('%s/%s' % (chrootdir,chrootcpdir)):
    os.chdir('%s/%s' % (chrootdir,chrootcpdir))
  collectivelog = '%s/%s' % (collectivelogdir,'foundation toolchain')
  mstart('foundation toolchain',collectivelog,scripttest)
  getdiskspace(hostname)
  errmsg = "BUILD ERROR: \n"
  instres = 0
  if os.path.exists(cpdir + '/' + target + '/cross/common'):
    systemCmd('%s %s/%s/cross/common/*.mvl cross/common' % (cpall,cpdir,target),scripttest,collectivelog)
    getdiskspace(hostname)
    rdir = chrootcpdir+'/cross/common'
    if rpminstall(chrootdir+rdir,rdir,'cross*.mvl',editionrpmbin,collectivelog):
      errmsg = errmsg + '\t\tOne or more <target>/cross/common/cross*.mvl failed to install.'
      instres = 1
    getdiskspace(hostname)
    systemCmd('rm -rf cross/common',scripttest,collectivelog)
    getdiskspace(hostname)
  if os.path.exists(cpdir + '/' + target + '/cross/' + targethost):
    systemCmd('%s %s/%s/cross/%s/*.mvl cross/%s' % (cpall,cpdir,target,hostname,hostname),scripttest,collectivelog)
    getdiskspace(hostname)
    rdir = chrootcpdir+'/cross/'+hostname
    if rpminstall(chrootdir+rdir,rdir,'cross*.mvl',editionrpmbin,collectivelog):
      errmsg = errmsg + '\t\tOne or more <target>/cross/' + targethost + '/ mvl failed to install.'
      instres = 1
    getdiskspace(hostname)
    systemCmd('rm -rf cross/%s' % hostname,scripttest,collectivelog)
    getdiskspace(hostname)
  if os.path.exists(cpdir + '/' + target + '/target'):
    systemCmd('%s %s/%s/target/kernel-headers* target' % (cpall,cpdir,target),scripttest,collectivelog)
    if string.find(target,'uclibc') > -1:
      systemCmd('%s %s/%s/target/uclibc* target' % (cpall,cpdir,target),scripttest,collectivelog)
    else:
      systemCmd('%s %s/%s/target/glibc* target' % (cpall,cpdir,target),scripttest,collectivelog)
    getdiskspace(hostname)
    rdir = chrootcpdir+'/target'
    if rpminstall(chrootdir+rdir,rdir,'kernel-headers*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog):
      errmsg = errmsg + '\t\tkernel-headers*.mvl failed to install.'
      instres = 1
    getdiskspace(hostname)
    if string.find(target,'uclibc') > -1:
      glibc = 'uclibc'
    else:
      glibc = 'glibc'
    if rpminstall(chrootdir+rdir,rdir,glibc+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog):
      errmsg = errmsg + '\t\tglibc*.mvl failed to install.'
      instres = 1
    getdiskspace(hostname)
    systemCmd('rm -rf cross/%s' % hostname,scripttest,collectivelog)
    getdiskspace(hostname)
  os.chdir(builddir)
  if instres:
    printflush(errmsg,collectivelog,scripttest)
  else:
    printflush("BUILT: foundation toolchain installed",collectivelog,scripttest)
  getdiskspace(hostname)
  mstop('foundation toolchain',collectivelog,scripttest)
  if product not in ('bst','devrocket','proadk','propk'):
    result = buildheaders()
  else:
    result = 'finished'

############################################################
# Build 'other tools
############################################################
if result == 'finished':
  crosslist = crossapps.keys()
  crosslist.sort()
  for app in crosslist:
    getReqFiles = 0
    crosspath = crossapps[app][0]
    crosstype = crossapps[app][1]
    crossdir = crossapps[app][2]
    crossspec = crossapps[app][3]
    crossrpmtype = crossapps[app][4]
    if crossrpmtype == 'hostarch':
      crossrpmtype = hostarch
    elif crossrpmtype == 'target':
      crossrpmtype = target
    crossextra = crossapps[app][5]
    crossinst = crossapps[app][6]
    type = '--' + crosstype + '='
    if crossdir in ('etherboot','linux86','syslinux') and string.find(target, 'x86') == -1:
      continue
    elif crossdir == 'lilo' and target != selfhosttarget:
      continue
    elif crossspec == 'glibc-utils' and string.find(target,'uclibc') > -1:
      continue
    if crosstype == 'cross':
      collectivelog = '%s/%s' % (collectivelogdir,crosstype + '-' + crossspec)
      mstart(crosstype + '-' + crossspec,collectivelog,scripttest)
    elif crosstype == 'target':
      getReqFiles = 1
      collectivelog = '%s/%s' % (collectivelogdir,crossspec)
      mstart(crossspec,collectivelog,scripttest)
    getdiskspace(hostname)
    instres = 0
    if os.path.exists(crosspath + '/' + crossdir + '/SPECS') or scripttest == 1:
      systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,crosspath,crossdir,chrootdir,builddir),scripttest,collectivelog)
      systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,crosspath,crossdir,chrootdir,builddir),scripttest,collectivelog)
      if crossspec == 'binutils':
        buildtargbinutils()
      elif crossspec == 'gcc' and crosstype == 'target':
        buildtarggcc()
      else:
        specs = []
        if crossspec in ('gcc-bootstrap-32','gcc-bootstrap-64',):
          specs = ['cross-gcc-bootstrap.spec',]
        elif crossspec in ('gcc-32','gcc-64',) and crosstype == 'cross':
          specs = ['cross-gcc.spec',]
        elif crossspec in ('binutils-32','binutils-64') and crosstype == 'target':
          specs = ['binutils.spec',]
        elif crossspec in ('gcc-32','gcc-64',) and crosstype == 'target':
          specs = ['gcc.spec',]
        elif crossspec in ('glibc-32','glibc-64',) and crosstype == 'target':
          specs = ['glibc.spec',]
        elif crosstype == 'cross':
          if os.path.exists('%s/%s/SPECS' % (crosspath,crossdir)):
            os.chdir('%s/%s/SPECS' % (crosspath,crossdir))
          elif scripttest == 1:
            specs.append('%s-%s-scripttest.spec' % (crosstype,crossspec))
          for sf in os.popen('ls ' + crosstype + '-' + crossspec + '.spec').readlines():
            specs.append(string.strip(sf))
          os.chdir(scriptdir)
        elif crosstype == 'target':
          if os.path.exists('%s/%s/SPECS' % (crosspath,crossdir)):
            os.chdir('%s/%s/SPECS' % (crosspath,crossdir))
          elif scripttest == 1:
            specs.append('%s-scripttest.spec' % crossspec)
          for sf in os.popen('ls ' + crossspec + '.spec').readlines():
            specs.append(string.strip(sf))
          os.chdir(scriptdir)
        if specs:
          for spec in specs:
            if os.path.exists('%s/%s/SPECS' % (crosspath,crossdir)):
              os.chdir('%s/%s/SPECS' % (crosspath,crossdir))
            if os.path.islink(spec):
              spec = os.readlink(spec)
            os.chdir(scriptdir)
            bcmd = 'ba ' + type + target + '-linux ' + crossextra
            if rpmb(builddir+'/SPECS/'+spec,editionrpmbuild,bcmd,collectivelog,getReqFiles) or scripttest == 1:
              copysrcrpm(crossspec,collectivelog)
              for inst in crossinst:
                rpminstdir = '%s/%s/RPMS/%s' % (chrootdir,builddir,crossrpmtype)
                if exist(rpminstdir, inst) or scripttest == 1:
                  if crosstype == 'target' and crossdir == 'glibc':
                    instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'*'+inst+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
                    systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/target' % (cpall,chrootdir,builddir,
                               target,cpdir,target),scripttest,collectivelog)
                  elif crosstype == 'target': 
                    instres = rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'*'+inst+'*.mvl --target='+target+'-linux --nodeps',editionrpmbin,collectivelog)
                    systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/target' % (cpall,chrootdir,builddir,
                               target,cpdir,target),scripttest,collectivelog)
                  else:
                    instres = rpminstall(chrootdir+builddir+'/RPMS/'+crossrpmtype,builddir+'/RPMS/'+crossrpmtype,'*.mvl',editionrpmbin,collectivelog)
                    if crossrpmtype == 'noarch':
                      systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/cross/common' % (cpall,chrootdir,builddir,crossrpmtype,cpdir,target),scripttest,collectivelog)
                    elif crossrpmtype == hostarch:
                      systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/cross/%s' % (cpall,chrootdir,builddir,crossrpmtype,cpdir,target,hostname),scripttest,collectivelog)
                  # move testsuite rpms to testing sub directory
                  systemCmd('mv %s/%s/cross/%s/*testsuite* %s/%s/cross/%s/testing' % (cpdir,target,
                             hostname,cpdir,target,hostname),scripttest,collectivelog)
                  systemCmd('mv %s/%s/target/*testsuite* %s/%s/target/testing' % (cpdir,target,
                             cpdir,target),scripttest,collectivelog)
                if string.find(crossspec,'bootstrap') > -1:
                  systemCmd('rm -f %s/%s/RPMS/%s/*%s*bootstrap*' % (chrootdir,builddir,crossrpmtype,target),scripttest,collectivelog)
                cleanbuilddirs()
              if crosstype == 'cross' and not instres:
                printflush('BUILT: %s-%s for %s built and installed.' % (crosstype,crossspec,target),collectivelog,scripttest)
              elif crosstype == 'cross' and instres:
                printflush("BUILD ERROR: %s-%s for %s built but didn't install." % (crosstype,crossspec,target),collectivelog,scripttest)
              elif crosstype == 'target' and not instres:
                printflush('BUILT: %s for %s built and installed.' % (crossspec,target),collectivelog,scripttest)
              elif crosstype == 'target' and instres:
                printflush("BUILD ERROR: %s for %s built but didn't install." % (crossspec,target),collectivelog,scripttest)
            else:
              if crosstype == 'cross':
                printflush("BUILD ERROR: " + crosstype+ "-" +crossspec + " for " + target + " didn't build.",collectivelog,scripttest)
              elif crosstype == 'target':
                printflush("BUILD ERROR: " + crossspec + " for " + target + " didn't build.",collectivelog,scripttest)
        else:
          if crosstype == 'cross':
            printflush("BUILD ERROR: " + crosstype + "-" + crossspec + " for " + target + " didn't build...no spec",collectivelog,scripttest)
            getdiskspace(hostname)
            mstop(crosstype + '-' + crossspec,collectivelog,scripttest)
          elif crosstype == 'target':
            printflush("BUILD ERROR: " + crossspec + " for " + target + " didn't build...no spec",collectivelog,scripttest)
            getdiskspace(hostname)
            mstop(crossspec,collectivelog,scripttest)
    else:
      if crosstype == 'cross':
        printflush("BUILD ERROR: " + crosstype + "-" + crossspec + " for " + target + " didn't build...no spec",collectivelog,scripttest)
        getdiskspace(hostname)
        mstop(crosstype + '-' + crossspec,collectivelog,scripttest)
      elif crosstype == 'target':
        printflush("BUILD ERROR: " + crossspec + " for " + target + " didn't build...no spec",collectivelog,scripttest)
        getdiskspace(hostname)
        mstop(crossspec,collectivelog,scripttest)
    if crosstype == 'cross':
      getdiskspace(hostname)
      mstop(crosstype + '-' + crossspec,collectivelog,scripttest)
    elif crosstype == 'target':
      getdiskspace(hostname)
      mstop(crossspec,collectivelog,scripttest)

  # build cross mvlt apps
  if mvltapps:
    for ma in mvltapps:
      if target == all_targets[0]:
        bcmd = 'ba --cross='+target+'-linux'
      else:
        bcmd = 'bb --cross='+target+'-linux'
      collectivelog = '%s/%s' % (collectivelogdir,'cross-' + ma)
      mstart('cross-' + ma,collectivelog,scripttest)
      getdiskspace(hostname)
      if 'mvlt' in cvspaths.keys() or scripttest == 1:
        systemCmd('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,cvspaths['mvlt'][0],ma,chrootdir,builddir),scripttest,collectivelog)
        systemCmd('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,cvspaths['mvlt'][0],ma,chrootdir,builddir),scripttest,collectivelog)
      instres = 0
      if rpmb(builddir + '/SPECS/cross-'+ma+'.spec',editionrpmbuild,bcmd,collectivelog):
        if exist(chrootdir+builddir+'/RPMS/'+hostarch,'cross-' + target + '-'+ma):
          instres = rpminstall(chrootdir+builddir+'/RPMS/'+hostarch,builddir+'/RPMS/'+hostarch,'cross-' + target + '-*.mvl',editionrpmbin,collectivelog)
          copysrcrpm('cross-%s' % ma,collectivelog)
          systemCmd('%s %s/%s/RPMS/%s/*.mvl %s/%s/cross/%s' % (cpall,chrootdir,builddir,hostarch,
                    cpdir,target,hostname),scripttest,collectivelog)
        if instres:
          printflush("BUILD ERROR: cross-" + ma + " for " + target + " built but didn't install.",collectivelog,scripttest)
        else:
          printflush('BUILT: cross-' + ma + ' for ' + target + ' built.',collectivelog,scripttest)
      else:
        printflush("BUILD ERROR: cross-" + ma + " for " + target + " didn't build.",collectivelog,scripttest)
      cleanbuilddirs()
      mstop('cross-' + ma,collectivelog,scripttest)

printflush('<' + sys.argv[0] + '>: finished build part at ' + gettime())
#os.system('mv /chroot/%s/home/build/provides-%s %s/%s/target/provides' % (hostname,target,cpdir,target))

# some builds will rebuild cross/target gcc in the edition, so we need to remove 
# the foundation version from dev_area after the edition version has built
if rebuildgcc:
  removefiles = ("gcc","g++","gomp","stdc++")
  for rmfile in removefiles:
    files = os.popen('cd %s/%s/target; ls *%s*' % (cpdir,target,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/target/%s..." % (cpdir,target,file.strip()),collectivelog,scripttest)
        systemCmd('rm -f %s/%s/target/%s' % (cpdir,target,file.strip()),scripttest,collectivelog)
    files = os.popen('cd %s/%s/target/testing; ls *%s*' % (cpdir,target,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/target/testing/%s..." % (cpdir,target,file.strip()),collectivelog,scripttest)
        systemCmd('rm -f %s/%s/target/testing/%s' % (cpdir,target,file.strip()),scripttest,collectivelog)
    files = os.popen('cd %s/%s/cross/%s; ls *%s*' % (cpdir,target,hostname,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/cross/%s/%s..." % (cpdir,target,hostname,file.strip()),collectivelog,scripttest)
        systemCmd('rm -f %s/%s/cross/%s/%s' % (cpdir,target,hostname,file.strip()),scripttest,collectivelog)
    files = os.popen('cd %s/%s/cross/%s/testing; ls *%s*' % (cpdir,target,hostname,rmfile)).readlines()
    for file in files:
      if buildid not in file.strip():
        printflush("Removing foundation file %s/%s/cross/%s/testing/%s..." % (cpdir,target,hostname,file.strip()),collectivelog,scripttest)
        systemCmd('rm -f %s/%s/cross/%s/testing/%s' % (cpdir,target,hostname,file.strip()),scripttest,collectivelog)
  files = os.popen('cd %s/SRPMS; ls *gcc*' % cpdir).readlines()
  for file in files:
    if buildid not in file.strip():
      printflush("Removing foundation file %s/SRPMS/%s..." % (cpdir,file.strip()),collectivelog,scripttest)
      systemCmd('rm -f %s/SRPMS/%s' % (cpdir,file.strip()),scripttest,collectivelog)


if result != 'finished':
  printflush('BUILDCORE ERROR: ' + result)
  printflush('creating result log file...')
  systemCmd('echo "' + result + '" > ' + logdir + '/result-' + target + '-' + 
           buildid + '.log',scripttest)
else:
  systemCmd('touch ' + cpdir + '/host/done/core-' + target,scripttest)
getdiskspace(hostname)
printflush('<' + sys.argv[0] + '>: finished buildcore for ' + target + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')

