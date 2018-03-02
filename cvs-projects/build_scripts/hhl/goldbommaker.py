#!/usr/bin/python
import sys, os, string, re, shutil, rpm, time


def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'
#-----------------------------------------------------------------------------------------
# goldbommaker.py 
# This script creates the bom files for each of the cdimages.
# Modified 		By		Defect/Reason
#  05/03/18		Annette Roll   Initial add to cvs 
#	
#------------------------------------------------------------------------------------------
if len(sys.argv) == 1:
  print 'usage: %s %s %s' % (sys.argv[0],'<product>','<buildtag>')
  sys.exit(1)

product = sys.argv[1]
print 'product = ' + product
buildtag = sys.argv[2]
print 'buildtag = ' + buildtag

#------------------------------------------------------------------------------------------
cddir = '/mvista/dev_area/' + product + '/cdimages/' + buildtag
print 'cddir = ' + cddir
l = cddir + '/GMBOMS/goldbom.log'

#------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------
print '<' + sys.argv[0] + '>: creating GOLD MASTER BOMS for ' + sys.argv[2] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
os.chdir(cddir)
if not os.path.exists('mkdir GMBOMS'):
  os.system('mkdir -p GMBOMS')
bomfiles = os.popen('ls *.iso | grep -v src').readlines()
for b in bomfiles:
  bf = string.split(string.strip(b),'.')[0]
  cmd = 'sudo mount -o loop ' + string.strip(b) + ' /mnt/tmp'
  #print 'cmd = ' + cmd
  os.system(cmd)
  os.chdir('/mnt/tmp')
  os.system('find | grep -v install | grep mvl$ > ' + cddir + '/GMBOMS/' + bf + '.gmbom')
  for a in os.popen('find | grep -v install | grep mvl$').readlines():
    cmd = 'rpm -qp --qf "%{SOURCERPM}\\n" ' + string.strip(a) + ' >> ' + cddir + '/GMBOMS/goldbom.log'
    #print 'cmd = ' + cmd
    os.system(cmd)
  os.chdir(cddir)
  os.system('sudo umount /mnt/tmp')
srcimage = os.popen('ls *.iso | grep src').readlines()
for s in srcimage:
  bf = string.split(string.strip(s),'.')[0]
  cmd = 'sudo mount -o loop ' + string.strip(s) + ' /mnt/tmp'
  os.system(cmd)
  os.chdir('/mnt/tmp')
  os.system('ls -R | sort > ' + cddir + '/GMBOMS/' + bf + '.gmbom')
print '<' + sys.argv[0] + '>: Finished creating GOLD MASTER BOMS for ' + string.strip(b) + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
    

