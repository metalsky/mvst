#!/usr/bin/python
import rpm
from buildFunctions import *

def cleanbuilddirs():
  os.system('rm -f %s/%s/SPECS/*' % (chrootdir,builddir))
  os.system('rm -f %s/%s/SRPMS/*' % (chrootdir,builddir))
  os.system('rm -rf %s/%s/SOURCES/*' % (chrootdir,builddir))
  os.system('rm -rf %s/%s/BUILD/*' % (chrootdir,builddir))
  os.system('rm -rf %s/%s/RPMS/*' % (chrootdir,builddir))

def rpminstall(path,installpath,rpm,rpmbin):
  if os.path.exists(path):
    res = chroot(hostname,rpmbin + ' -Uvh ' + installpath + '/' + rpm + ' --ignoreos',scripttest)
  else:
    print 'path does not exist: ' + path
    print 'not installing ' + rpm
    res = 1
  print 'result of install: ' + str(res)
  sys.__stdout__.flush()
  return res

def rpmev(rpm,rpmbin):
  chroot(hostname,rpmbin + ' -ev ' + rpm + ' --nodeps',scripttest)
  sys.__stdout__.flush()

def rpminst(rpm,rpmbin):
  res = chroot(hostname,rpmbin + ' -Uvh ' + rpm + ' --ignoreos',scripttest)
  print 'result of install: ' + str(res)
  sys.__stdout__.flush()
  return res

def rpminst_q(rpm,rpmbin):
  res = chroot(hostname,rpmbin + ' -U ' + rpm + ' --ignoreos',scripttest)
  print 'result of install: ' + str(res)
  sys.__stdout__.flush()
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
    print 'command: ' + cmd
    results = []
  return results

def rpmb(spec,rpmbuild,bcmd,getReqFiles=0):
  print 'Using rpmbuild = ' + rpmbuild
  sys.__stdout__.flush()
  
  cmd = rpmbuild + ' --clean -' + bcmd + \
                   ' --define \\"_topdir ' + builddir + '\\" ' + \
                   '--define \\"_mvl_build_id ' + buildid + '\\" ' + \
                   '--define \\"vendor MontaVista Software, Inc.\\" ' + \
                   '--define \\"packager <source@mvista.com>\\" ' + \
                   '--define \\"_builddir ' + builddir + '/BUILD\\" ' + \
                   '--define \\"_rpmdir ' + builddir + '/RPMS\\" ' + \
                   '--define \\"_mvl_host_os_build ' + hostname + '\\" ' + \
                   spec
  #print 'cmd = ' + cmd
  #sys.__stdout__.flush()
  chroot(hostname,cmd,scripttest)
  return wrotecheck(hostname,getReqFiles,minReqApps)

def exist(path,name):
  if os.path.exists(path):
    for file in os.listdir(path):
      if string.find(file,name) > -1:
        # file exists, return 1
        return 1
    # made it through all files and didn't find name, so return 0
  return 0

if len(sys.argv) != 4:
  print "\nbuildtargetapps.py <data file> <target> <hostname>"
  print "\n# of args = " + str(len(sys.argv))
  print "\nHere are the args:"
  for x in sys.argv:
    print x
  sys.exit(1)

datafile = sys.argv[1]
target = sys.argv[2]
hostname = sys.argv[3]
mstart('posttargetapps-setup')
print '<' + sys.argv[0] + '>: starting posttargetapps for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
print "datafile = %s" % datafile
if os.path.exists(datafile):
  exec(open(datafile))
  print 'targethost = ' + targethost
else:
  print "No datafile found.  Stopping build."
  print "Finished %s at %s" % (sys.argv[0],gettime())
  sys.exit(1)

commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
commonrpmbuild = commonrpmbin + 'build'
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
editionrpmbuild = editionrpmbin + 'build'
node = string.strip(os.popen('hostname').read())
print 'node = ' + node
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

minReqApps = '%s/%s/MVL-%s-postapps-%s-%s' % (cpdir,target,edition,target,buildid)
print 'minReqApps = ' + minReqApps
getReqFiles = 0

if product in ('dev',):
  if string.find(target,'uclibc') > -1:
    posttargetapps = { }
  elif target in multilibtargets.keys():
    posttargetapps = {
	'glibc':  ('glibc',cvspaths['toolchain'][0],cpdir + '/' + target + '/target','target',target),
	'glibc-multilib':  ('glibc-multilib',cvspaths['toolchain'][0],cpdir + '/' + target + '/target','target',target),
	}
    if target == 'mips64_octeon_v2_be':
      posttargetapps['glibc-multilib-o32'] = ('glibc-multilib-o32',cvspaths['toolchain'][0],cpdir + '/' + target + '/target','target',target)
  else:
    posttargetapps = {
	'glibc':  ('glibc',cvspaths['toolchain'][0],cpdir + '/' + target + '/target','target',target),
	}
elif product in ('fe',):
    posttargetapps = { }
else:
  posttargetapps = {
	'ramdisk':('cross-ramdisk',cvspaths['userland'][0],cpdir + '/' + target + '/cross/common','cross','noarch'),
	}
print 'post target apps:'
for key in posttargetapps.keys():
  print '   ' + key

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
 
print 'architecture is ' + target
print 'kernel version is ' + kernel + '_' + hhlversion
sys.__stdout__.flush()

print '--> Building on ' + hostname + '...'
sys.__stdout__.flush()
 
cleanbuilddirs()

building = 0
# as defined in the data file:
# posttargetapps :
#      {<app>    : (<src path>, <copy dir>, <type>, <rpmdir>),}
#      where <type> is cross,target or host
#            <rpmdir> is noarch,hostarch or target
mstop('posttargetapps-setup')
for app in posttargetapps.keys():
  appname = posttargetapps[app][0]
  path = posttargetapps[app][1]
  copypath = posttargetapps[app][2]
  apptype = posttargetapps[app][3]
  rpmtype = posttargetapps[app][4]
  if os.path.exists(copypath):
    #existingrpms = os.listdir(copypath)
    #skipexistingrpm = 0          # this is a flag that is initially set to 0.
                                 # this script will check to see if the package being built
                                 # has been built (if so, skipexistingrpm is set to 1).
                                 # If not, it builds it, otherwise it won't.
    #for e_rpm in existingrpms:
    #  if string.find(e_rpm,app) > -1: 
    #    print app + ' exists as ' + e_rpm 
    #    print 'skipping ' + app + '...'
    #    sys.__stdout__.flush()
    #    skipexistingrpm = 1
    #if skipexistingrpm == 0:
      #print app + '...'
      bcmd = 'ba --' + apptype + '=' + target + '-linux'
      specdir = app
      specname = appname
      installFile = '*.mvl'
      if appname == 'glibc':
        getReqFiles = 1
      elif appname == 'glibc-multilib':
        getReqFiles = 1
        bcmd = 'ba --' + apptype + '=' + target + '-linux --define \\"_mvl_multilib ' + multilibtargets[target] + '\\" '
        specdir = 'glibc'
        specname = 'glibc'
        installFile = 'glibc*_%s*' % multilibtargets[target]
      #print 'using ' + appname + '.spec...'
      sys.__stdout__.flush()
      mstart(appname)
      if os.path.exists(path + '/' + specdir + '/SPECS/' + specname + '.spec'):
        os.system('%s %s/%s/SOURCES/* %s/%s/SOURCES' % (cpall,path,specdir,chrootdir,builddir))
        os.system('%s %s/%s/SPECS/* %s/%s/SPECS' % (cpall,path,specdir,chrootdir,builddir))
        if rpmb(builddir+'/SPECS/'+specname+'.spec',editionrpmbuild,bcmd,getReqFiles): 
          if apptype == 'target':
            if not rpminstall(chrootdir+builddir+'/RPMS/'+rpmtype,builddir+'/RPMS/'+rpmtype,installFile,editionrpmbin+' --target='+target+'-linux --nodeps'):
              print 'BUILT: ' + appname + ' for ' + target + ' built.'
            else:
              print 'BUILD ERROR: ' + appname + ' for ' + target + ' built but did not install.'
          else:
            if not rpminstall(chrootdir+builddir+'/RPMS/'+rpmtype,builddir+'/RPMS/'+rpmtype,installFile,editionrpmbin):
              print 'BUILT: ' + appname + ' for ' + target + ' built.'
            else:
              print 'BUILD ERROR: ' + appname + ' for ' + target + ' built but did not install.'
          if scripttest not in ('true','false'):
            for cpfile in os.listdir(chrootdir+builddir+'/RPMS/' + rpmtype):
              if apptype == 'target':
                if string.find(cpfile,'testsuite') > -1:
                  shutil.copy2(chrootdir+builddir+'/RPMS/' + rpmtype + '/' + cpfile,copypath+'/testing')
                elif cpfile not in ('CVS','CVSROOT','placeholder'):
                  shutil.copy2(chrootdir+builddir+'/RPMS/' + rpmtype + '/' + cpfile,copypath)
              elif cpfile not in ('CVS','CVSROOT','placeholder'):
                #print 'cpfile= ' + cpfile + '...'
                shutil.copy2(chrootdir+builddir+'/RPMS/' + rpmtype + '/' + cpfile,copypath)
            for cpfile in os.listdir(chrootdir+builddir+'/SRPMS'):
              if cpfile not in ('CVS','placeholder'):
                cmd = 'cp -fp %s %s' % (chrootdir+builddir+'/SRPMS/' + cpfile,cpdir + '/SRPMS')
                os.system(cmd)
        else:
          print 'BUILD ERROR: ' + appname + ' for ' + target + ' did not build.'
          sys.__stdout__.flush()
      else:
        print 'BUILD ERROR: no spec file for ' + appname
        sys.__stdout__.flush()
      mstop(appname)
  else:
    print copypath + ' does not exist, not building ' + apptype + '-' + app
    sys.__stdout__.flush()

print 'existing /var/tmp/* directories:'
sys.__stdout__.flush()
os.system('ls /var/tmp')
os.chdir(builddir)
print '<' + sys.argv[0] + '>: finished posttargetapps for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'

