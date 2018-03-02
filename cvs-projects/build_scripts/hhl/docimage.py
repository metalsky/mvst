#!/usr/bin/python
import sys, os, string, re, getopt, time

# docimages.py

# This script will check out and tag the doc cds and then create the doc cdimage


#if len(sys.argv) == 1:
#  print 'usage: %s %s %s %s %s %s ' % (sys.argv[0],'<product>','<cpdir>','<buildid>','<buildtag>','<branch>')
#  sys.exit(1)
if len(sys.argv) == 1:
  print 'usage: %s %s %s %s' % (sys.argv[0],'<conf file>','<branch>','<product>')
  sys.exit(1)

#product = sys.argv[1]
#print 'product = ' + product
conf = sys.argv[1]
print 'conf = ' + conf
#cpdir = sys.argv[2]
#print 'cpdir = ' + cpdir
#buildid = sys.argv[3]
#print 'buildid = ' + buildid
#buildtag = sys.argv[4]
#print 'buildtag = ' + buildtag
branch = sys.argv[2]
print 'branch = ' + branch
#----------------------------------------------------------
# header for readme file
#----------------------------------------------------------
header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory were not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]

#------------------------------------------------------------------------------------------
# 
#------------------------------------------------------------------------------------------
def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

#------------------------------------------------------------------------------------------
builddir = os.getcwd()
#------------------------------------------------------------------------------------------
# Read <product>data.dat
#------------------------------------------------------------------------------------------
#if product == 'fe':
#        conf = open(builddir + '/fedata.dat')
#        product = 'foundation'
#elif product == 'asyncfe':
#        conf = open(builddir + '/asyncfedata.dat')
#        product = 'foundation'
#elif product == 'pro':
#        conf = open(builddir + '/pedata.dat')
#elif product == 's124omap3':
#        conf = open(builddir + '/s124omap3data.dat')
#	product = 'mvl'
#elif product == 'prodb':
#        conf = open(builddir + '/prodbdata.dat')
#        product = 'pro'
#elif product == 'proasync':
#        conf = open(builddir + '/peasyncdata.dat')
#        product = 'pro'
#elif product == 'prom64async':
#        conf = open(builddir + '/m64peasyncdata.dat')
#        product = 'pro'
#elif product == 'cge':
#        conf = open(builddir + '/cgedata.dat')
#elif product == 'mobilinux':
#        conf = open(builddir + '/mobilinuxdata.dat')
#elif product == 'mobicarbon':
#        conf = open(builddir + '/mobicarbondata.dat')
#	product = 'mobilinux'
#elif product == 'mobiasync':
#        conf = open(builddir + '/mobiasyncdata.dat')
#elif product == 'cgeasync':
#        conf = open(builddir + '/cgeasyncdata.dat')
#elif product == 'dev':
#        conf = open(builddir + '/devdata.dat')
#elif product == 'mips64':
#        conf = open(builddir + '/mips64data.dat')
#        product = 'dev'
#elif product == 'feeclipse':
#        conf = open(builddir + '/feeclipsedata.dat')
#        product = 'foundation'
#else:
#        print 'Unrecognized product specified...Stopping build.'
#        sys.exit(1)
exec(open(conf))
product = sys.argv[3]

########Installer STUFF###################
installrpmdir = cpdir + '/installer_rpms'
didir = installrpmdir + '/install_area/docs-cd'

tmppath = '/tmp/%s' % buildtag
#-------------------------------------------------------------------
docsexpdir = "%s/Documentation/%s" % (tmppath,docsmodule)
print "Docsexpdir %s"%(docsexpdir)

cvsopts = 'cvs -Q -d :ext:build@cvs.sh.mvista.com:/cvsdev/'
#--------------------------------------------------------------------
#Create cdimage directory if needed
#-------------------------------------------------------------------
cddir = '/mvista/dev_area/' + product + '/' + buildtag + '/cdimages'
print 'cddir = ' + cddir
if not os.path.exists(cddir):
  os.system('mkdir -p ' + cddir)
dvddir = '/mvista/dev_area/' + product + '/' + buildtag + '/dvdimages'
print 'dvddir = ' + dvddir
if not os.path.exists(dvddir):
  os.system('mkdir -p ' + dvddir)
#-------------------------------------------------------------------
# make a temporary cd directory to build cdimages locally, then copy images to dev_area
#-------------------------------------------------------------------
cdtempdir = '/var/tmp/CDTEMP'
os.system('mkdir -p ' + cdtempdir)
#------------------------------------------------------------------------
# create README.md5sum file
#------------------------------------------------------------------------
os.chdir(cddir)
for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
#------------------------------------------------------------------------
# set log dirs
#------------------------------------------------------------------------
if product in ('dev','foundation'):
  logdir = '/mvista/dev_area/foundation/' + buildtag + '/logs'
else:
  logdir = '/mvista/dev_area/' + product + '/' + buildtag + '/logs'
#------------------------------------------------------------------------------------------
# update and retag the docs
#------------------------------------------------------------------------------------------
# tag & export Documentation
#------------------------------------------------------------------------
print "tmppath=%s"%(tmppath)
if not os.path.exists(tmppath):
  os.system('mkdir -p ' + tmppath)
os.chdir(tmppath)
# since this is used for docs cd respins, remove the existing buildtag on the Docs repo since they
# can't use branches right
print 'Removing existing ' + buildtag + ' tag...'
os.system(cvsopts + 'Documentation rtag -d %s .' % buildtag)
if branch != "null":
  print 'Using ' + branch
  print 'Applying rtag ' + buildtag + ' in Documentation repository...'
  os.system(cvsopts + 'Documentation rtag -R -F -r %s %s %s' % (branch,buildtag,docsmodule))
else:
  print 'Applying rtag ' + buildtag + ' in Documentation repository...'
  os.system(cvsopts + 'Documentation rtag -R -D now -F %s %s' % (buildtag,docsmodule))
#OMG, before we try to export check and see if we already have an exported respository and KILL it
if os.path.exists("%s/Documentation" % tmppath):
  os.system('rm -rf %s/Documentation' % tmppath)
os.system(cvsopts + 'Documentation export -r %s -d Documentation .' % (buildtag))
sys.__stdout__.flush()
#-----------------------------------------------------------------------------------------
# copy the docs to your build area
#------------------------------------------------------------------------------------------
if os.path.exists(docsexpdir):
  os.chdir(docsexpdir)
  os.system('find | grep CVS | xargs rm -rf')
  os.chdir(tmppath)
  for deleteme in docsgp.keys():
    if os.path.exists(cpdir + '/' + string.strip(docsgp[deleteme])):
      os.system('rm -rf %s/%s' % (cpdir,string.strip(docsgp[deleteme])))
  os.system('cp -a %s/* %s' % (docsexpdir,cpdir))
sys.__stdout__.flush()

#------------------------------------------------------------------------------------------
# Now let's create the doc cdimage
#------------------------------------------------------------------------------------------
print 'creating the docs cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
cd = 'docs'
mkisocmd = 'mkisofs -quiet -r -J -joliet-long -allow-leading-dots -no-split-symlink-components -no-split-symlink-fields '
mkisocmd = mkisocmd + '-V ' + cd + ' -o ' + cd + '-' + product + '-' + buildid + '.iso '
mkisocmd = mkisocmd + '-x CVS -hide-rr-moved '
mkisocmd = mkisocmd + '-graft-points '
for gp in docsgp.keys():
  if os.path.exists(cpdir + '/' + string.strip(docsgp[gp])):
    mkisocmd = mkisocmd + gp + '=' + cpdir + '/' + docsgp[gp]

#added by Carl
for installdir in os.listdir(didir):
  if os.path.isdir(didir + '/' + installdir):
    mkisocmd = mkisocmd + installdir + '/=' + didir + '/' + installdir + '/ '

os.chdir(cdtempdir)
if not os.system(mkisocmd):
  os.system('md5sum ' + cd + '-' + product + '-' + buildid + '.iso > md5sum')
  os.system('mv ' + cdtempdir + '/' + cd + '-' + product + '-' + buildid + '.iso ' + cddir)
  os.chdir(cddir)
  os.system('cat ' + cdtempdir + '/md5sum >> README.md5sum')
  os.chdir(dvddir)
  os.system('cat ' + cdtempdir + '/md5sum >> README.md5sum')
  os.system('rm -f %s-%s-%s.iso' % (cd,product,buildid))
  os.system('ln %s/%s-%s-%s.iso .' % (cddir,cd,product,buildid))
  print "BUILT: doc cdimage built"
else:
  print "BUILD ERROR: doc cdimage did not build."
os.chdir(builddir)

os.system('rm -rf %s' % tmppath)

#------------------------------------------------------------------------------------------
print 'Finished creating the doc cdimage for ' + product + ' ' + buildid + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
