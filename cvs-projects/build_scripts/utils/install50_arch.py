#!/usr/bin/python
import os, string, sys, threading, signal, re
from resourceManager import *

host			= 'centos3'
nodetype	= 'oldnode'
edition         = None
release         = None
buildid         = None
copydir         = None

node = None

def chroot(node,command,host):
  sshcmd = 'ssh root@'
  cmd = "chroot /chroot/%s /bin/su - root -c '%s' >> /chroot/%s/home/build/chroot.log 2>&1" % (host,command,host)
  #print 'chroot command: ' + cmd
  res = os.system('%s%s "%s"' % (sshcmd,node,cmd))
  sys.__stdout__.flush()
  return res

def buildThread(host,target,includeUclibc):
  # host = linux chroot or windows
  # target = target
  # includeUclibc = boolean
  x86targs = ()
  if target != 'x86_586' and includeUclibc:
    x86targs = ('x86_586','x86_586_uclibc')
  elif target != 'x86_586' and not includeUclibc:
    x86targs = ('x86_586',)

  sshcmd = 'ssh '
  rpm2cpio = 'rpm2cpio'
  resource = nodetype
  extra = ''

  # check out node
 # node = getResource("Manual Installer Scripts",buildid,resource,"installing %s to node "%target)
  # clean node
  os.system('%s%s "sudo rm -rf /chroot/%s/opt/montavista/*"' % (sshcmd,node,host))
  os.system('%s%s "sudo rm -rf /chroot/%s/home/build/chroot.log"' % (sshcmd,node,host))
  os.system('%s%s "touch /chroot/%s/home/build/chroot.log"' % (sshcmd,node,host))
  # make mount point
  os.system('%s%s "mkdir -p /chroot/%s/home/build/mnt"' % (sshcmd,node,host))
  # mount dvd iso in chroot

  os.system('%s%s "sudo mount -o loop %s/%s-host-%s-%s.iso /chroot/%s/home/build/mnt"' % (sshcmd,node,
                 copydir,edition,target,buildid,host))

  # rpm2cpio install common/host rpm
  chroot(node,'echo "installing common/host rpm with rpm2cpio"',host)
  chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-4* | cpio -iud' % (rpm2cpio,host),host)
  chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-b* | cpio -iud' % (rpm2cpio,host),host)
  chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-d* | cpio -iud' % (rpm2cpio,host),host)
  chroot(node,'cd /; %s /home/build/mnt/host/%s/host-rpm-* | cpio -iud' % (rpm2cpio,host),host)
  # for solaris, install gcc host-tools with rpm2cpio
    # install common rpms
  chroot(node,'echo "installing common rpms with common-rpm"',host)
  chroot(node,'/opt/montavista/common/bin/mvl-common-rpm -Uvh /home/build/mnt/host/%s/common* %s' % (host,extra),host)
  chroot(node,'/opt/montavista/common/bin/mvl-common-rpm -Uvh /home/build/mnt/host/common/common* %s' % extra,host)
  # install host rpms
  chroot(node,'echo "installing host rpms with edition-rpm"',host)
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/host/%s/host-* %s' % (edition,host,extra),host)
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/host/common/host-* %s' % (edition,extra),host)
  # uninstall common-apt-rpm-plugin-devrocket
  chroot(node,'echo "uninstalling common/host apt-rpm-plugin-devrocket"',host)
  chroot(node,'/opt/montavista/common/bin/mvl-common-rpm -qa | grep common-apt-rpm-plugin-devrocket | xargs /opt/montavista/common/bin/mvl-common-rpm -ev --nodeps',host)
  # uninstall host-apt-rpm-plugin-devrocket
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -qa | grep host-apt-rpm-plugin-devrocket | xargs /opt/montavista/%s/bin/mvl-edition-rpm -ev --nodeps'%(edition,edition),host)
  # install cross rpms
  chroot(node,'echo "installing cross rpms with edition-rpm"',host)
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s/cross/common/cross-* %s' % (edition,target,extra),host)
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s/cross/%s/cross-* %s' % (edition,target,host,extra),host)
  if includeUclibc:
    chroot(node,'echo "%s has a _uclibc target, installing cross uclibc rpms with edition-rpm"' % target,host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s_uclibc/cross/common/cross-* %s ' % (edition,target,extra),host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s_uclibc/cross/%s/cross-* %s' % (edition,target,host,extra),host)
  # install x86_586 & x86_586_uclibc cross rpms for non x86_586 targets

# edition rpm to install all target rpms 
  chroot(node,'echo "installing target rpms with edition-rpm "',host)
  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mnt/%s/target/*.mvl --nodeps %s' % (edition,target,target,extra),host)
  if includeUclibc:
    chroot(node,'echo "installing uclibc target rpms with edition-rpm"',host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s_uclibc-linux -Uvh /home/build/mnt/%s_uclibc/target/*.mvl --nodeps %s' % (edition,target,target,extra),host)


##target shit below

  # edition rpm to install selected target rpms, using adk_targetapps_<target> files
  chroot(node,'echo "installing common target rpms with edition-rpm"',host)
  if includeUclibc:
    chroot(node,'echo "%s has a _uclibc target, installing common uclibc target rpms with edition-rpm"' % target,host)

  chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mnt/%s/target/* --nodeps --force %s' % (edition,target,target,extra),host)
  if includeUclibc:
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s_uclibc-linux -Uvh /home/build/mnt/%s_uclibc/target/* --nodeps --force %s' % (edition,target,target,extra),host)

  #umount
  os.system('ssh %s "sudo umount /chroot/%s/home/build/mnt"' % (node,host))
  print "Complete! - Clean node when you are done!"


#  releaseResource(node)



def main(argv):
  global edition, release, buildid, copydir, node
  # usage
  if len(sys.argv) != 6:
    print 'usage: %s %s %s %s %s %s' % (argv[0],'<path to release>', '<buildid>','<edition>','<node>','<target>')
    sys.exit(1)
  path = argv[1]
  buildid = argv[2]
  edition = argv[3]
  node = argv[4]
  target = argv[5]
  if edition == "pro":
    release = 'mvl500'
  if edition == "cge":
    release = 'mvlcge500'
  if edition == "mobilinux":
    release = "mobilinux500"
  if edition == "blacktop":
    release = "blacktop"
    edition = "mobilinux"

  print 'using buildid = ' + buildid
  builddir = os.getcwd()


  copydir = '%s/dvdimages' %(path)
  if not os.path.exists(copydir):
    print 'path %s does not exist' % copydir
    sys.exit(1)

  buildThread(host,target,0)


    



if __name__ == "__main__":
  main(sys.argv)


