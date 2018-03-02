#!/usr/bin/python
import os, sys, string, time

# Args:
# 1- <hostname>
# 2- <foundation path>
#
# This script will delete BUILD, SOURCES, SPECS, SRPMS and RPMS from /chroot/<hostname>/home/build,
# unless foundation == skip

if len(sys.argv) == 1:
  print 'usage: %s %s %s' % (sys.argv[0], '<hostname>','<foundation path>')
  print 'if <foundation path> is "skip" the script will not delete /chroot/<hostname>/home/build/RPMS/install'
  print 'which assumes that the build will be using a released foundation build, currently present'
  print 'on the chrooted environment.'
  sys.exit(1)

hostname = sys.argv[1]
foundation = sys.argv[2]

builddir = '/chroot/%s/home/build' % (hostname)
#node = string.strip(os.popen('hostname').read())

print 'Starting Host Clean...'
#print 'Cleaning %s on %s...' % (builddir,node)
sys.__stdout__.flush()
os.chdir(builddir)
if foundation != 'skip':
  os.system('rm -rf BUILD SOURCES SPECS SRPMS RPMS')
else:
  os.system('rm -rf BUILD SOURCES SPECS SRPMS RPMS/i386 RPMS/noarch')

print 'Host Clean complete'

