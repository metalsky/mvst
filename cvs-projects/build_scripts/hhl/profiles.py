#!/usr/bin/python
import sys, os, string, re, shutil, rpm, time

dontclean = ['CVS', 'README', 'placeholder', 'platformtest']

def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'
#-----------------------------------------------------------------------------------------
# profile.py 
# This script creates the profile files for the installer and copies the docs.
# Modified 		By		Defect/Reason
#  03/07/28		Annette Roll   Initial add to cvs 
#	
#------------------------------------------------------------------------------------------
if len(sys.argv) == 1:
  print 'usage: %s %s %s %s' % (sys.argv[0],'<product>','<cpdir>','<buildtag>')
  sys.exit(1)

product = sys.argv[1]
print 'product = ' + product
cpdir = sys.argv[2]
print 'cpdir = ' + cpdir
buildtag = sys.argv[3]
print 'buildtag = ' + buildtag

#------------------------------------------------------------------------------------------
# Read <product>data.dat
#------------------------------------------------------------------------------------------
builddir = os.getcwd()
logdir = '/mvista/dev_area/' + product + '/logs/' + buildtag
if product == 'fe':
        conf = open(builddir + '/fedata.dat')
elif product == 'pe':
        conf = open(builddir + '/pedata.dat')
elif product == 'cge':
        conf = open(builddir + '/cgedata.dat')
elif product == 'dev':
        conf = open(builddir + '/devdata.dat')
else:
        print 'Unrecognized product specified...Stopping build.'
        sys.exit(1)
exec(conf)
#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
print '<' + sys.argv[0] + '>: creating profile files for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
archs = all_targets
for target in archs:
  if len(string.split(target,'_')) == 2:
    p = string.split(target,'_')[0]
    t = string.split(target,'_')[1]
  else:
    p = string.split(target,'_')[0]
    t = string.split(target,'_')[1] + '_' + string.split(target,'_')[2]
  ############################################################
  # Create profile files for installer and copy documentation
  #  Step 1. create the directories for each target
  #  Step 2. cd into the buildtag directory
  #  Step 3. generate the target and lsp profiles.
  #  Step 4. copy the documentation from exported area to cpdir.
  ############################################################

  # generating profile files for partition size during install
  profilepath =  cpdir + '/profile_files/' + target + '/etc/profiles/' + target
  if not os.path.exists(profilepath):
    os.system('mkdir -p' + profilepath)
  targetprofile = installdir + '/devkit/' + p + '/' + t + '/target'
  lspprofile = installdir + '/devkit/lsp'
  profilelocal= cpdir + '/' 
  if not os.path.exists(profilepath + '/lsps'):
    os.system('mkdir -p ' + profilepath + '/lsps' )
  os.system(installdir + '/host/bin/mvl-rpm -qp --dump ' + profilelocal + 
            target + '/target/*.mvl | sed -e "s:' + targetprofile + '::g" > ' + 
            profilepath + '/' + '/profile')
  os.chdir(cpdir + '/' + target + '/lsps')
  dirlist = os.listdir('.')
  for d in dirlist:
    if not os.path.exists(profilepath + '/lsps/' + d):
      os.system('mkdir -p ' + profilepath + '/lsps/' + d )
    os.chdir(profilelocal + target + '/lsps/' + d)
    os.system(installdir + '/host/bin/mvl-rpm --nodigest -qp --dump */*.mvl | ' +
                'sed -e "s:' + lspprofile  + '::g" | ' +
                'sed -e "s:' + targetprofile  + '::g" > ' + 
                profilepath + '/lsps/' + d + '/profile')
    sys.__stdout__.flush()

  print '<' + sys.argv[0] + '>: finished creating profile files for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'

