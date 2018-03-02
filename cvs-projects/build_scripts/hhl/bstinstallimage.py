#!/usr/bin/python
import sys, os, string, re, getopt, time

# installimages.py


#volume file stuff:
old = ('-00000')
new = ('-00001')

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s' % (sys.argv[0],'<cpdir>','<buildtag>','<buildid>','<product>')
  sys.exit(1)
cpdir = sys.argv[1]
buildtag = sys.argv[2]
buildid = sys.argv[3]
product = sys.argv[4]
header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory were not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]
#------------------------------------------------------------------------------------------
def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

#------------------------------------------------------------------------------------------
builddir = os.getcwd()
print 'cpdir = ' + cpdir
cddir = '/mvista/dev_area/' + product + '/cdimages/' + buildtag
print 'cddir = ' + cddir
os.system('mkdir -p ' + cddir)
installrpmdir = cpdir + '/installer_rpms'
iadir = installrpmdir + '/install_area'
voldir = '/etc/config/volume'
addonidir = iadir + '/addon'
print 'addon_installdir = ' + addonidir
rpmbin = '/opt/montavista/host/bin/mvl-rpm-forward '
os.chdir(cddir)
for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
os.chdir(builddir)
logdir = '/mvista/dev_area/' + product + '/logs/' + buildtag
#------------------------------------------------------------------------------------------
# Read <product>data.dat
#------------------------------------------------------------------------------------------
if product == 'bst':
        conf = open(builddir + '/bstdata.dat')
else:
        print 'Unrecognized product specified...Stopping build.'
        sys.exit(1)
exec(conf)

#-----------------------------------------------------------------------------------------
# Let's check for the bst-addon-cd-installer-noarch.mvl
#------------------------------------------------------------------------------------------
if bstcdinstall:
  print '<' + sys.argv[0] + '>: checking for the bst-addon installer for ' + sys.argv[1] + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
  af = string.strip(os.popen('ls ' + installrpmdir + '/addon/*cd-installer*').read())
  if not os.path.exists(af):
    print 'bst-addon-cd-installer.mvl does not exist ... skipping ' + sys.argv[0] + ' ...'
  #if it's there let's install it
  else:
    print 'installing bst-addon-cd-installer.mvl ...'
    sys.__stdout__.flush()
    os.system(rpmbin  + '-forward -ihv  ' + installrpmdir + '/addon/bst-addon-cd-installer*.mvl --prefix ' +
              addonidir + ' --nodeps --force --ignoreos --ignorearch')
    sys.__stdout__.flush()
    # Change the volume file
    os.chdir(addonidir + '/' + voldir)
    contents = os.listdir('.')
    for c in contents:
      print 'For ' + c + ' moving ' + old + ' to ' + new + ' ...'
      os.system('mv ' + c + ' ' + string.replace(c,old,new))
    sys.__stdout__.flush()
#------------------------------------------------------------------------------------------
# Now let's create the bst-creation-cdimage
#------------------------------------------------------------------------------------------
if mkbstcreationcd:
  print 'creating the bst creation cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
  os.chdir(cddir)
  mkisocmd = 'mkisofs -quiet -r -J -joliet-long -L -no-split-symlink-components -no-split-symlink-fields '
  mkisocmd = mkisocmd + '-V bst-creation -o bst-creation-' + buildid + '.iso '
  mkisocmd = mkisocmd + '-x cluster '
  mkisocmd = mkisocmd + '-x optional '
  mkisocmd = mkisocmd + '-x lsps ' 
  mkisocmd = mkisocmd + '-x done ' 
  mkisocmd = mkisocmd + '-x cross ' 
  mkisocmd = mkisocmd + '-graft-points '
  mkisocmd = mkisocmd + 'host/=' + cpdir + '/host '
  mkisocmd = mkisocmd + 'etc/=' + addonidir + '/etc '
  mkisocmd = mkisocmd + 'docs/=' + cpdir + '/docs '
  mkisocmd = mkisocmd + 'SRPMS/=' + cpdir + '/SRPMS '
  mkisocmd = mkisocmd + 'install-components/=' + addonidir + '/install-components '
  mkisocmd = mkisocmd + 'README=' + cpdir + '/README '
  for a in all_targets:
    mkisocmd = mkisocmd + a + '=' + cpdir + '/' + a + ' ' 
  print 'mkisocmd is ... ' + mkisocmd
  os.system(mkisocmd)
#------------------------------------------------------------------------------------------
# Now let's create the distribution-cdimage
#------------------------------------------------------------------------------------------
if mkbstdistcd:
  print 'creating the bst distribution cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
  sys.__stdout__.flush()
  for a in all_targets:
    mkisocmd = 'mkisofs -quiet -r -J -joliet-long -L -no-split-symlink-components -no-split-symlink-fields '
    mkisocmd = mkisocmd + '-V distribution-image' + a + ' -o distribution-image-' + a + '-' + buildid + '.iso '
    mkisocmd = mkisocmd + '-x cluster '
    mkisocmd = mkisocmd + '-x optional '
    mkisocmd = mkisocmd + '-x lsps ' 
    mkisocmd = mkisocmd + '-x done ' 
    mkisocmd = mkisocmd + '-x target ' 
    mkisocmd = mkisocmd + '-graft-points '
    mkisocmd = mkisocmd + 'host/=' + cpdir + '/hostdist '
    mkisocmd = mkisocmd + 'etc/=' + addonidir + '/etc '
    mkisocmd = mkisocmd + 'docs/=' + cpdir + '/docs '
    mkisocmd = mkisocmd + 'install-components/=' + addonidir + '/install-components '
    mkisocmd = mkisocmd + 'README=' + cpdir + '/README '
    mkisocmd = mkisocmd + a + '/cross/common/=' + cpdir + '/' + a  + '/cross/common '
    print 'mkisocmd is ... ' + mkisocmd
    os.system(mkisocmd)
#------------------------------------------------------------------------------------------
# Now let's create the md5sums for the cdimages
#------------------------------------------------------------------------------------------
os.chdir(cddir)
images = os.listdir('.') 
for i in images:
  os.system('md5sum ' + i + ' >> README.md5sum')
#------------------------------------------------------------------------------------------
# Now let's create the boms for the cdimages
#------------------------------------------------------------------------------------------
if mkcdbom:
  print 'creating the boms for ' + product + ' ' + buildid + ' at ' + gettime() + '...'
  os.chdir(builddir)
  os.system('./bommaker.py %s %s "' % (product,buildtag))
  print 'bommaker finished at ' + gettime()
  sys.__stdout__.flush()

print 'bstinstallimage is done'


