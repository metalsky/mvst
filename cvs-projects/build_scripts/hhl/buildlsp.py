#!/usr/bin/python
from buildFunctions import *

# Take cdk repository, target, kernel, kernel repository and
# cpdir as args.
# Read lsp.dat to get list of all lsp spec files for a given target
# for each item in list, copy spec file to cdk spec directory, and 
# all files in sources directory to cdk sources directory
# and rpm -ba each item.  Then copy src.mvl and .mvl to
# cpdir

def sudochroot(command):
  if hostname != "solaris8":
    cmd = 'sudo chroot /chroot/%s /bin/su - -c "%s" > /chroot/%s/home/build/chroot.log 2>&1' % (hostname,command,hostname)
  else:
    cmd = 'chroot /chroot/%s /bin/su - root -c "%s" > /chroot/%s/home/build/chroot.log 2>&1' % (hostname,command,hostname)
  #printflush('chroot command: ' + cmd)
  if not scripttest:
    res = os.system(cmd)
    systemCmd('cat /chroot/%s/home/build/chroot.log' % (hostname),scripttest)
  else:
    printflush('command: ' + cmd)
    res = 1
  return res

def cleanbuilddirs():
  getdiskspace(hostname)
  systemCmd('rm -f %s/%s/SPECS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -f %s/%s/SRPMS/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/SOURCES' % (chrootdir,builddir),scripttest)
  systemCmd('mkdir %s/%s/SOURCES' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/BUILD/*' % (chrootdir,builddir),scripttest)
  systemCmd('rm -rf %s/%s/RPMS/*' % (chrootdir,builddir),scripttest)
  getdiskspace(hostname)

def uninst():
  getdiskspace(hostname)
  printflush('uninstalling build...')
  if not mktar:
    chroot(hostname,'rm -rf ' + installdir + '/*', scripttest)
    chroot(hostname,'rm -rf /var/tmp/*',scripttest)
  else:
    sudochroot('rm -rf ' + installdir + '/*')
    sudochroot('rm -rf /var/tmp/*')
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

def rpmb(spec,rpmbuild,bcmd):
  printflush('Using rpmbuild = ' + rpmbuild)
  cmd = rpmbuild + ' --clean -' + bcmd + \
                   ' --define \\"_topdir ' + builddir + '\\" ' + \
                   '--define \\"_mvl_build_id ' + buildid + '\\" ' + \
                   '--define \\"vendor MontaVista Software, Inc.\\" ' + \
                   '--define \\"packager <source@mvista.com>\\" ' + \
                   '--define \\"_builddir ' + builddir + '/BUILD\\" ' + \
                   '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' + \
                   '--define \\"_mvl_host_os_build ' + hostname + '\\" ' + \
                   spec
  #printflush('cmd = ' + cmd)
  chroot(hostname,cmd,scripttest)
  return wrotecheck(hostname)

def exist(path,name):
  if os.path.exists(path):
    for file in os.listdir(path):
      if string.find(file,name) > -1:
        # file exists, return 1
        return 1
    # made it through all files and didn't find name, so return 0
  return 0

def copySources(lspdir):
  printflush("copying SOURCES for " + lspdir + "...")
  if not os.path.exists(lsppath + '/' + lspdir + '/SOURCES'):
    printflush('path ' + lsppath + '/' + lspdir + '/SOURCES does not exist...')
  else:
    ldir =  os.listdir(lsppath + '/' + lspdir + '/SOURCES')
    for x in ldir:
      if string.find(x, 'CVS') == -1:
        #shutil.copy(lsppath + '/' + lspdir + '/SOURCES/' + x, chrootdir + '/' + builddir + '/SOURCES')
        systemCmd('cp -a ' + lsppath + '/' + lspdir + '/SOURCES/' + x + ' ' + chrootdir + '/' + builddir + '/SOURCES')
  printflush("contents of SOURCES:")
  systemCmd('ls -la %s/%s/SOURCES' % (chrootdir,builddir))

def copySpec(lspdir,lsp):
  printflush("copying SPECS for " + lspdir + "...")
  if os.path.exists(lsppath + '/' + lspdir + '/SPECS'):
    foundlsp = 0
    for l in os.listdir(lsppath + '/' + lspdir + '/SPECS'):
      if string.find(l,lsp) > -1:
        foundlsp = 1
        shutil.copy(lsppath + '/' + lspdir + '/SPECS/' + l, chrootdir + '/' + builddir + '/SPECS')
    if not foundlsp:
      printflush('could not find any spec files matching ' + lsppath + '/' + lspdir + '/SPECS/*' + l + '*...')
  else:
    printflush('path ' + lsppath + '/' + lspdir + '/SPECS does not exist...')

def buildlsp(lsp,prek,lsptype):
  kerneldefs = ' --define \\"_mvl_kernel_base_version ' + kernel + '\\"' + \
               ' --define \\"_mvl_kernel_mvl_version ' + hhlversion + '\\"' + \
               ' --define \\"_mvl_lsp_rev ' + lsprev + '\\"'
  rval = 0
  if lsptype == 'cross':
    lspspec = 'cross-lsp-' + lsp
    bcmd = 'ba --cross=' + target + '-linux' + kerneldefs
  elif lsptype == 'target':
    lspspec = 'lsp-' + lsp
    bcmd = 'ba --target=' + target + '-linux ' + kerneldefs
  elif lsptype == 'enabler':
    lspspec = 'cross-lsp-eclipse-enabler-' + lsp
    lsptype = 'cross'
    bcmd = 'ba --cross=' + target + '-linux' + kerneldefs
  if os.path.exists(chrootdir+builddir+'/SPECS/' + lspspec + '.spec') or scripttest == 1:
    mstart(lspspec)
    getdiskspace(hostname)
    if prek == 'noprek':
      if rpmb(builddir+'/SPECS/' +lspspec+ '.spec',rpmbuild,bcmd):
        printflush('BUILT: ' + lspspec + ' for ' + target + ' built.')
        if lsptype == 'cross' and string.find(lspspec,'eclipse') == -1:
          rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir+'/RPMS/noarch','cross-*-lsp-'+lsp+'*',rpmbin)
        elif lsptype == 'target':
          rpminstall(chrootdir+builddir+'/RPMS/'+target,builddir+'/RPMS/'+target,'lsp-'+lsp+'*',rpmbin + ' --target=' + target + '-linux')
        rval = 1
      else:
        printflush('BUILD ERROR: ' + lspspec + ' for ' + target + ' did not build.')
    else:
      if rpmb(builddir+'/SPECS/' +lspspec+ '.spec',rpmbuild+' --define \\"_mvl_prek_on true\\"',bcmd):
        printflush('BUILT: ' + lspspec + '-prek for ' + target + ' built.')
        rval = 1
        if lsptype == 'cross' and string.find(lspspec,'eclipse') == -1:
          rpminstall(chrootdir+builddir+'/RPMS/noarch',builddir+'/RPMS/noarch','cross-*-lsp-'+lsp+'*',rpmbin)
      else:
        printflush('BUILD ERROR: ' + lspspec + '-prek for ' + target + ' did not build.')
  elif string.find(lspspec,"eclipse-enabler-generic_x86-hhl_install") == -1:
    printflush('<' + sys.argv[0] + '>: building ' + lspspec + ' at ' + gettime() + '...')
    printflush('BUILD ERROR: No SPEC file for ' + lspspec + '.')
  getdiskspace(hostname)
  mstop(lspspec)
  return rval

def copyrpms(lsp):
  getdiskspace(hostname)
  # copy src rpms
  srcdir = os.listdir(chrootdir+builddir+'/SRPMS')
  for x in srcdir:
    #printflush('found:  ' + x)
    if string.find(x, lsp) > -1:
      shutil.copy(chrootdir+builddir+'/SRPMS/' + x, cpdir + '/SRPMS')
  # cross-lsp & enabler
  if string.find(lsp,'previewkit') == -1:
    if os.path.exists(chrootdir+builddir+'/RPMS/noarch'):
      rpmdir = os.listdir(chrootdir+builddir+'/RPMS/noarch')
      for x in rpmdir:
        if string.find(x,lsp) > -1:
          if len(string.split(lsp,'-mips_fp_be')) > 1:
            lsp = string.split(lsp,'-mips_fp_be')[0]
          elif len(string.split(lsp,'-mips_fp_le')) > 1:
            lsp = string.split(lsp,'-mips_fp_le')[0]
          elif len(string.split(lsp,'-mips2_fp_be')) > 1:
            lsp = string.split(lsp,'-mips2_fp_be')[0]
          elif len(string.split(lsp,'-mips2_fp_le')) > 1:
            lsp = string.split(lsp,'-mips2_fp_le')[0]
          elif len(string.split(lsp,'-arm_xscale_be')) > 1:
            lsp = string.split(lsp,'-arm_xscale_be')[0]
          elif len(string.split(lsp,'-arm_xscale_le')) > 1:
            lsp = string.split(lsp,'-arm_xscale_le')[0]
          elif len(string.split(lsp,'-sh_sh3_be')) > 1:
            lsp = string.split(lsp,'-sh_sh3_be')[0]
          elif len(string.split(lsp,'-sh_sh3_le')) > 1:
            lsp = string.split(lsp,'-sh_sh3_le')[0]
          elif len(string.split(lsp,'-sh_sh4_be')) > 1:
            lsp = string.split(lsp,'-sh_sh4_be')[0]
          elif len(string.split(lsp,'-sh_sh4_le')) > 1:
            lsp = string.split(lsp,'-sh_sh4_le')[0]
          if not os.path.exists(cpdir + '/' + target + '/lsps/' + lsp):
            systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps/' + lsp,scripttest)
          if not os.path.exists(cpdir + '/' + target + '/lsps/' + lsp + '/common'):
            systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps/' + lsp + '/common',scripttest)
          shutil.copy(chrootdir+builddir+'/RPMS/noarch/' + x, cpdir +'/'+target+ '/lsps/' + lsp + '/common')
    # target-lsp
    if os.path.exists(chrootdir+builddir+'/RPMS/' + target):
      rpmdir = os.listdir(chrootdir+builddir+'/RPMS/' + target)
      for x in rpmdir:
        if string.find(x,lsp) > -1:
          if not os.path.exists(cpdir + '/' + target + '/lsps/' + lsp):
            systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps/' + lsp,scripttest)
          if not os.path.exists(cpdir + '/' + target + '/lsps/' + lsp + '/target'):
            systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps/' + lsp + '/target',scripttest)
          shutil.copy(chrootdir+builddir+'/RPMS/'+target+'/'+x, cpdir + '/' +target+'/lsps/'+lsp+ '/target')
    else:
      printflush(chrootdir+builddir+"/RPMS/" + target + " doesn't exist...must not have built")
  else:
    if os.path.exists(chrootdir+builddir + '/RPMS/noarch'):
      rpmdir = os.listdir(chrootdir+builddir + '/RPMS/noarch')
      for x in rpmdir:
        if string.find(x, lsp) > -1:
          if not os.path.exists(cpdir + '/' + target + '/lsps/' + lsp):
            systemCmd('mkdir -p ' + cpdir + '/' + target + '/lsps/' + lsp,scripttest)
          shutil.copy(chrootdir+builddir + '/RPMS/noarch/' + x, cpdir + '/' + target + '/lsps/' + lsp)
    else:
      rpmsbuilt = os.listdir(chrootdir+builddir + '/RPMS/noarch')
      rb = 'foo'
      for r in rpmsbuilt:
        if string.find(r,target + '-lsp') > -1:
          rb = 'good'
      if rb == 'foo':
        printflush(chrootdir+builddir + "/RPMS/noarch has no target lsps...must not have built")
  getdiskspace(hostname)

if len(sys.argv) < 3:
  printflush("\nbuildlsp.py <data file> <target> <hostname>")
  printflush("\n# of args = " + str(len(sys.argv)))
  printflush("\nHere are the args:")
  for x in sys.argv:
    printflush(x)
  sys.exit(1)

datafile = sys.argv[1]
target = sys.argv[2]
hostname = sys.argv[3]

printflush('<' + sys.argv[0] + '>: starting buildlsp for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')
printflush("datafile = %s" % datafile)
if os.path.exists(datafile):
  exec(open(datafile))
  printflush('targethost = ' + targethost)
else:
  printflush("No datafile found.  Stopping build.")
  printflush("Finished %s at %s" % (sys.argv[0],gettime()))
  sys.exit(1)

rpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
rpmbuild = rpmbin + 'build'
node = string.strip(os.popen('hostname').read())
printflush('node = ' + node)
scriptdir = os.getcwd()

# this is the directory in the chroot environment where rpm are built
builddir = '/home/build'

# this is the chroot directory
chrootdir = '/chroot/%s' % (hostname)

printflush('scriptdir = ' + scriptdir)
printflush('builddir = ' + builddir)
printflush('chrootdir = ' + chrootdir)

# check to see if system rpm uses rpm or rpmbuild
if hostname in ('centos3','redhat80','redhat90','suse90'):
  cpall = 'cp -a'
  hostarch = 'i386'
elif hostname == 'solaris8':
  cpall = 'cp -rp'
  hostarch = 'sun4u'
else:
  cpall = 'cp -a'
  hostarch = 'i386'

printflush('architecture is ' + target)
printflush('kernel version is ' + kernel + '_' + hhlversion)
printflush('--> Building on ' + hostname + '...')
lsppath = ''
if 'lsp' in cvspaths.keys():
  lsppath = cvspaths['lsp'][0]
else:
  for repo in cvspaths.keys():
    if string.find(repo,'git') > -1:
      lsppath = cvspaths[repo][0] + '/MONTAVISTA-BUILD/LSPS'
  if not lsppath:
    lsppath = 'null'
printflush('lsp path is ' + lsppath + '...')
cleanbuilddirs()

printflush('cp %s/bin/true %s/opt/montavista/common/bin/mvl-license' % (chrootdir,chrootdir))
systemCmd('cp %s/bin/true %s/opt/montavista/common/bin/mvl-license' % (chrootdir,chrootdir))
exec(open(lspdat))
if target in lsps.keys():
  for lsplist in lsps[target]:
    lspdir = lsplist[0]
    lsp = lsplist[1]
    printflush('lspdir = ' + lspdir)
    printflush('lsp = ' + lsp)
    getdiskspace(hostname)
    copySources(lspdir)
    copySpec(lspdir,lsp)
    getdiskspace(hostname)
    printflush('--> Building ' + lsp )
    if string.find(lsp,'previewkit') > -1:
      if buildlsp(lsp,'noprek','cross'):
        if buildlsp(lsp,'noprek','target'):
          if buildlsp(lsp,'prek','target'):
            copyrpms(lsp)
    else:
      if buildlsp(lsp,'noprek','cross'):
        buildlsp(lsp,'noprek','enabler')
        if buildlsp(lsp,'noprek','target'):
          copyrpms(lsp)

if mktar:
  mstart('tarball')
  # copy the rpms required to be installed as root
  systemCmd('mkdir -p /chroot/%s/home/build/tarapps' % hostname,scripttest)
  for app in requiredTarApps:
    systemCmd('cp -a %s/%s/target/%s* /chroot/%s/home/build/tarapps' % (cpdir,target,app,hostname),scripttest)
  # install the required rpms using sudo and delete required rpms
  rpminstall(chrootdir + builddir + '/tarapps', builddir + '/tarapps', '* --nodeps --force', 'sudo ' + rpmbin + ' --target=' + target + '-linux')
  systemCmd('rm -rf /chroot/%s/home/build/tarapps' % hostname,scripttest)
  # use sudo to setugids
  printflush('running %s --setugids -a' % rpmbin)
  sudochroot('%s --setugids -a' % rpmbin)
  printflush('running %s --target=%s-linux --setugids -a' % (rpmbin,target))
  sudochroot('%s --target=%s-linux --setugids -a' % (rpmbin,target))
  # make tar file
  os.chdir('/chroot/%s' % hostname)
  if not os.path.exists('./home/build/buildtars'):
    systemCmd('mkdir -p ./home/build/buildtars',scripttest)
  printflush('make tar of /opt/montavista in %s chroot for %s at %s' % (hostname,target,gettime()))
  systemCmd('sudo tar -cpjf ./home/build/buildtars/%s-%s-%s.tar.bz2 opt/montavista' % (dvdname,target,buildid),scripttest)
  systemCmd('ls -lah ./home/build/buildtars/%s-%s-%s.tar.bz2' % (dvdname,target,buildid),scripttest)
  printflush('finished making tar of /opt/montavista in %s chroot for %s at %s' % (hostname,target,gettime()))
  if not os.path.exists('%s/../installs' % cpdir):
    systemCmd('mkdir -p %s/../installs' % cpdir,scripttest)
  printflush('moving tar of /opt/montavista in %s chroot for %s to dev_area at %s' % (hostname,target,gettime()))
  systemCmd('sudo mv ./home/build/buildtars/%s-%s-%s.tar.bz2 %s/../installs' % (dvdname,target,buildid,cpdir),scripttest)
  printflush('finished moving tar of /opt/montavista in %s chroot for %s to dev_area at %s' % (hostname,target,gettime()))
  systemCmd('rm -rf ./home/build/buildtars',scripttest)
  mstop('tarball')
#----------------------------------------------
# Uninstall build and delete install area
#----------------------------------------------
uninst()
cleanbuilddirs()

printflush('<' + sys.argv[0] + '>: finished buildlsp for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...')
getdiskspace(hostname)

