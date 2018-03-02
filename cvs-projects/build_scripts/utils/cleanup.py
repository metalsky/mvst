#!/usr/bin/python
##########################
#   cleanup.py
#
# until we get better build failure recovery in place, this is a script
# that will clean up all the directories on a node that get polluted
# when a build dies and doesn't clean up after itself.  this is especially
# problematic when it is a build that doesn't run on a regular basis because
# each build cleans up when it starts a build...newer builds will clean up when they
# finish, but for foundation one builds they don't, so when a foundation one build
# dies, it won't cleanup until the next build, which can cause disk space issues
# for regular builds
#
# staring with nodes, but will add cygwin and solaris machines too
##########################
import os, sys, threading, string
from resourceManager import *

def getdiskspace():
  print "Disk Usage:"
  sys.__stdout__.flush()
  if machine_type != 'solaris8':
    os.system('%s "df /"' % sshcmd)
  else:
    os.system('%s "df /chroot"' % sshcmd)
  sys.__stdout__.flush()

# usage
if len(sys.argv) != 2:
  print '\nusage: %s %s' % (sys.argv[0],'<machine name>')
  sys.exit(1)

machine = sys.argv[1]
machine_type = ""
hosts = ("centos3","mandrake91","redhat73","redhat80","redhat90","suse90")
builddirs = ("BUILD","RPMS","SRPMS","SOURCES","SPECS")

if machine_type != 'solaris8':
  sshcmd = 'ssh %s' % machine
else:
  sshcmd = 'ssh root@%s' % machine

if string.find(machine,"node") > -1:
  machine_type = "node"
elif string.find(machine,"solaris7") > -1:
  machine_type = "solaris7"
elif string.find(machine,"solaris8") > -1:
  machine_type = "solaris8"
elif string.find(machine,"cygwin") > -1:
  machine_type = "cygwin"
else:
  print "Unknown machine type, quiting"
  sys.exit(1)

getdiskspace()

if machine_type == "node":
  print "Checking out %s" % machine
  machine_resource = getResource("cleaning","ou812",machine,"Cleaning build leftovers")
  for host in hosts:
    print "Cleaning /chroot/%s/home/build" % host
    for builddir in builddirs:
      os.system('%s "rm -rf /chroot/%s/home/build/%s"' % (sshcmd,host,builddir))
    os.system('%s "rm -rf /chroot/%s/home/build/*profile*"' % (sshcmd,host))
    print "Cleaning /chroot/%s/opt/montavista" % host
    os.system('%s "rm -rf /chroot/%s/opt/montavista/*"' % (sshcmd,host))
    print "Cleaning /chroot/%s/tmp" % host
    os.system('%s "rm -rf /chroot/%s/tmp/*"' % (sshcmd,host))
    print "Cleaning /chroot/%s/var/tmp" % host
    os.system('%s "rm -rf /chroot/%s/var/tmp/*"' % (sshcmd,host))
  print "Cleaning /chroot/node/opt/hardhat"
  os.system('%s "rm -rf /chroot/node/opt/hardhat/*"' % sshcmd)
  print "Cleaning /chroot/node/opt/montavista"
  os.system('%s "rm -rf /chroot/node/opt/montavista/*"' % sshcmd)
  print "Cleaning /chroot/node/opt/mvlcee"
  os.system('%s "rm -rf /chroot/node/opt/mvlcee/*"' % sshcmd)
  print "Cleaning /chroot/node/opt/mvlcge"
  os.system('%s "rm -rf /chroot/node/opt/mvlcge/*"' % sshcmd)
  print "Cleaning /chroot/node/tmp"
  os.system('%s "rm -rf /chroot/node/tmp/*"' % sshcmd)
  print "Cleaning /chroot/node/var/tmp"
  os.system('%s "rm -rf /chroot/node/var/tmp/*"' % sshcmd)
  releaseResource(machine_resource)

getdiskspace()

