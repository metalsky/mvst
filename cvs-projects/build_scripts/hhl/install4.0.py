#!/usr/bin/python
import os, sys, re, string, time

# This script will install the host/cluster, common, target and cross common apps needed to be set up a build env.

# args:
# 1- edition (product)
# 2- reltag
# 3- archs, archs


def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'

if str(len(sys.argv)) not in ("4",):
  print "\nUsage: %s <edition> <edition build tag> <archs,archs>" % (sys.argv[0])
  sys.exit(1)

edition = sys.argv[1]
print "edition = " + edition
reltag = sys.argv[2]
print "buildtag = " + reltag
archs = string.split(sys.argv[3],',')
for a in archs:
  print "arch = " + a
commonrpmbin = "/opt/montavista/common/bin/mvl-common-rpm"
editionrpmbin = "/opt/montavista/%s/bin/mvl-edition-rpm" % (edition)
sys.__stdout__.flush()

if reltag[0] == '/':
  mvldir = reltag
elif edition == "pro":
  mvldir = "/mvista/dev_area/%s/%s" % (edition,reltag)
elif edition == "cge":
  mvldir = "/mvista/dev_area/%s/%s" % (edition,reltag)
elif edition == "cee":
  mvldir = "/mvista/dev_area/%s/%s" % (edition,reltag)
mvlkrnl = "%s/host/common/optional" % (mvldir)
print "mvldir = " + mvldir
print "mvlkrnl = " + mvlkrnl
print "commonrpmbin = " + commonrpmbin
print "editionrpmbin = " + editionrpmbin 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#get archs:
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for a in archs:
  print "installing for arch(s) = " + a
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# clean /opt/montavista 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
os.chdir('/opt/montavista')
os.system('rm -rf config devkit lup %s common' % (edition))
os.chdir('/')
os.system('rpm2cpio %s/host/cluster/common-rpm-4* | cpio -iud' % (mvldir))
os.system('rpm2cpio %s/host/cluster/common-rpm-b* | cpio -iud' % (mvldir))
os.system('rpm2cpio %s/host/cluster/common-rpm-d* | cpio -iud' % (mvldir))
os.system('rpm2cpio %s/host/cluster/host-rpm* | cpio -iud' % (mvldir))
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# install the edition
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
print 'Installing the edition ' + edition 
os.chdir('%s/host/cluster' % (mvldir))
os.system('echo "Installing from  `pwd`"')
os.system('ls common-rpm*.mvl | xargs %s -Uvh ' % (commonrpmbin))
os.system('ls host-rpm*.mvl | xargs %s -Uvh ' % (editionrpmbin))
os.system('ls common*.mvl | grep -v rpm | grep -v apache-ant | grep -v flexnet | xargs %s -Uvh ' % (commonrpmbin))
os.system('ls host*.mvl | grep -v rpm | xargs %s -Uvh ' % (editionrpmbin))
sys.__stdout__.flush()
os.chdir('%s/host/common' % (mvldir))
os.system('echo "Installing from  `pwd`"')
os.system('ls common*.mvl | grep -v eclipse | xargs %s -Uvh ' % (commonrpmbin))
os.system('ls host*.mvl | grep -v eclipse | xargs %s -Uvh ' % (editionrpmbin))
sys.__stdout__.flush()
for arch in archs:
  print "installing  for %s " % (arch)
  os.chdir('%s/%s/cross/common' % (mvldir,arch))
  os.system('echo "Installing from  `pwd`"')
  os.system('ls *.mvl | grep -v eclipse | xargs %s -Uvh ' % (editionrpmbin))
  os.chdir('%s/%s/cross/cluster' % (mvldir,arch))
  os.system('echo "Installing from  `pwd`"')
  os.system('%s -Uvh *.mvl ' % (editionrpmbin))
  os.chdir('%s/%s/target' % (mvldir,arch))
  os.system('echo "Installing from  `pwd`"')
  os.system('%s -Uvh *.mvl --target=%s-linux ' % (editionrpmbin,arch))
  sys.__stdout__.flush()
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
