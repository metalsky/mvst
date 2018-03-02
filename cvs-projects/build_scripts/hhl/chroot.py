#!/usr/bin/python
import os, string, sys

# this script can be imported by the other build scripts and provides the necessary
# chroot build functions

def chrootcmd(hostname,command):
  cmd = 'sudo chroot /chroot/%s /bin/su - build -c "%s" > /chroot/%s/home/build/chroot.log 2>&1' % (hostname,command,hostname)
  #print 'chroot.chrootcmd(): ' + cmd + '\n'
  os.system(cmd)
  os.system('cat /chroot/%s/home/build/chroot.log' % (hostname))
  sys.__stdout__.flush()

def wrotecheck(hostname):
  list = os.popen('cat /chroot/%s/home/build/chroot.log | grep Wrote' % (hostname)).readlines()
  if list:
    return 1
  else:
    return 0


