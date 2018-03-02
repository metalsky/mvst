#!/usr/bin/python

import sys, os, string, re, shutil, rpm, time


def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'
def getrandomdir():
  return string.strip(os.popen('cat /mvista/ftp/arch/fileout').read())
#-----------------------------------------------------------------------------------------
# releaseupload.py
# This script will upload cdimages to staging area of the MVZ.
# Modified 		By		Defect/Reason
#  03/08/29		Annette Roll    Initial add to cvs 
# Arguments: 
#	product = pe, cge, cee, etc
#	build_id = the full product release mvlcee300_innovator
#------------------------------------------------------------------------------------------
if len(sys.argv) == 1:
  print 'usage: %s %s %s %s ' % (sys.argv[0], '<build_id>', '<archdir>','<imagedir>' )
  print 'build_id = the full product release: i.e. mvlcge300_x335 '
  print 'archdir = The arch directory for a new release'
  print 'imagedir = The arch or board of the cdimage you want moved over.'
  sys.exit(1)

print '***********************************************************************************************'
print '<' + sys.argv[0] + '>: starting staging area upload for ' + sys.argv[3] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()

print '***********************************************************************************************'
build_id = sys.argv[1]
print 'build_id = ' + build_id
archdir = sys.argv[2]
print 'arch directory = ' + archdir
imagedir = sys.argv[3]
print 'The image is = ' + imagedir 
cpdir = '/mvista/dev_area'
print 'cpdir = ' + cpdir
updatedir = cpdir + '/' + build_id
print 'updatedir = ' + updatedir 
cdcpdir = cpdir + '/cdimages/' + build_id
print 'cdcpdir = ' + cdcpdir
mvzf = '/mvista/ftp'
mvza = '/mvista/ftp/arch'
mvzc = '/mvista/ftp/cust'
logdir = '/mvista/dev_area/logs/' + build_id
logfile = logdir + '/' + build_id + '.log'
whereiam = os.getcwd()
  ############################################################
  # Upload the release to the staging area
  #  Step 1.  Create the log directory
  #  Step 2.  Create the ../cust/<randpass 30> directory
  #  Step 3.  Create the directory structure in new cust dir
  #  Step 4.  cp images to new directory structure
  #  Step 5.  Create README.md5sum
  #  Step 6.  Run md5sum --check on images
  #  Step 7.  Create links in arch directory
  #  Step 8. Put everything out into logs for review
  #  Step 9. Send email to build@mvista with all info:
  #	      cust dir, md5sum results, arch dir
############################################################
# Step 1. Create the log file
############################################################
#print '*********************************************************************************************'
#print 'log directory ' + logdir + ' will be created'
#if not os.path.exists( logdir ):
#  os.system ('mkdir -p ' + logdir )
#print '*****************************************************************************************'
############################################################
# Step 2. Create the randpass directory
############################################################
print '*****************************************************************************************'
os.chdir(mvza)
os.system('./randpass 30 > fileout')
print 'cust directory is ' + getrandomdir() + '...'
print 'arch directory = ' + archdir
os.chdir(mvzf)
os.system('mkdir ./cust/' + getrandomdir()) 
newdir = mvzf + '/cust/' + getrandomdir()
os.chdir(newdir)
os.system('echo "I am in `pwd`"')
sys.__stdout__.flush()
############################################################
# Step 3. create the cdimages cd and update directories
print '*****************************************************************************************'
print 'The cdimages, cd and update directories will be created'
print '*****************************************************************************************'
ulds = ('cdimages','cd','updates')
for d in ulds:
  if not os.path.exists(d):
    os.mkdir(d)
    print  d + ' directory has been created'
    sys.__stdout__.flush() 
############################################################
# Step 3. copy the cdimages into the new cdimages directory
print '******************************************************************************************'
print 'The cdimages will be copied to the cdimages directory'
os.chdir(newdir + '/cdimages')
os.system('cp -a ' + cdcpdir + '/*' + imagedir + '*.iso . ') 
############################################################
# Step 4. Create and run the md5sum check
############################################################
print '******************************************************************************************'
print 'Creating the md5sum log'
header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory was not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]
os.chdir(newdir + '/cdimages')
if not os.path.isfile(newdir + '/cdimages/README.md5sum' ):
  for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
os.system('cat ' + cdcpdir + '/README.md5sum | grep ' + imagedir + ' >> README.md5sum')
print 'Running a md5sum check on the image(s)'
os.chdir(newdir + '/cdimages')
os.system('md5sum --check README.md5sum ') 
############################################################
# Step 5. link the arch directory to the cust directory
############################################################
print '*****************************************************************************************'
print 'Linking the  to ../arch/' + archdir + ' ....'
os.chdir( mvza )
os.system('ln -s ../cust/' + getrandomdir() + '  ' +  archdir ) 
###########################################################
