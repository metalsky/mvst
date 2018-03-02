#!/usr/bin/python
import sys, os, string, re, shutil, rpm, time


def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'
#-----------------------------------------------------------------------------------------
# bommaker.py 
# This script creates the bom files for each of the cdimages.
# Modified 		By		Defect/Reason
#  03/08/25		Annette Roll   Initial add to cvs 
#	
#------------------------------------------------------------------------------------------
if len(sys.argv) == 1:
  print 'usage: %s %s %s %s' % (sys.argv[0],'<product>','<buildtag>','<image path>')
  sys.exit(1)

product = sys.argv[1]
if product in ('dev','fe'):
  product = 'foundation'
print 'product = ' + product
buildtag = sys.argv[2]
print 'buildtag = ' + buildtag
imagepath = sys.argv[3]
print 'imagepath = ' + imagepath
#------------------------------------------------------------------------------------------
print '<' + sys.argv[0] + '>: creating BOMS for ' + sys.argv[2] + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
os.chdir(imagepath)
os.system('mkdir BOMS')
if not os.path.exists('/mnt/tmp'):
  os.system('sudo mkdir /mnt/tmp')
bomfiles = os.popen('ls *.iso').readlines()
for b in bomfiles:
  bf = string.split(string.strip(b),'.')[0]
  os.system('sudo mount -r -o loop ' + string.strip(b) + ' /mnt/tmp')
  os.chdir('/mnt/tmp')
  os.system('ls -R > ' + imagepath + '/BOMS/' + bf + '.bom')
  os.chdir(imagepath)
  os.system('sudo umount /mnt/tmp')
  print '<' + sys.argv[0] + '>: Finished creating BOM for ' + b + ' at ' + gettime() + ' on: ' + string.strip(os.popen('hostname').read()) + '...'
sys.__stdout__.flush()
    

