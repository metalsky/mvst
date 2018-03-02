#!/usr/bin/python
import os, string, sys, threading, signal
from resourceManager import *

nodetype	= 'node'
windows		= 1
cygport 	= '322'

def getCygwin():
  usableCygwin = ('cygwin-1','cygwin-2','cygwin-3','cygwin-4','cygwin-5','cygwin-6','cygwin-7','cygwin-8','cygwin-9','cygwin-12','cygwin-18','cygwin-20')
  failures = []
  cygnode = getResource(buildtag,buildid,"cygwin","adk build")
  print "got cygnode = " + cygnode
  while cygnode not in usableCygwin:
    print cygnode + " is not usable for ADK builds, getting a new resource"
    failures.append(cygnode)
    cygnode = getResource(buildtag,buildid,"cygwin","adk build")
    print "got cygnode = " + cygnode
  for cygfailure in failures:
    print "releasing " + cygfailure
    releaseResource(cygfailure)
  return cygnode

def genREADME():
  header = [ "The following information is the MD5 checksums of each file",
          "contained in this directory.  This information is used to",
          "verify that the files downloaded from this directory were not",
          "corrupted during the transfer.",
          " ",
          "            md5sum                          file",
          "--------------------------------  ---------------------------"]
  os.chdir(adkimagedir)
  os.system('rm -f README.md5sum')
  for h in header:
    os.system('echo "' + h + '" >> README.md5sum')
  os.chdir(builddir)

def chroot(node,command,host):
  if host != "solaris8":
    sshcmd = 'ssh '
    cmd = "sudo chroot /chroot/%s /bin/su - -c '%s' >> /chroot/%s/home/build/chroot.log 2>&1" % (host,command,host)
  else:
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
  if host in hosts:
    if host != 'solaris8':
      sshcmd = 'ssh '
      rpm2cpio = 'rpm2cpio'
      resource = nodetype
      extra = ''
    else:
      sshcmd = 'ssh root@'
      rpm2cpio = '/home/build/mnt/install-components/host/common/bin/rpm2cpio'
      resource = 'solaris'
      extra = '--ignoreos'
      expPath = 'export PATH=/opt/montavista/common/bin:/opt/montavista/%s/bin:$PATH' % edition
    # check out node
    node = getResource(buildtag,buildid,resource,"adk " + host + " build")
    print 'building adk for %s on %s using %s...' % (target,host,node)
    # clean node
    os.system('%s%s "rm -rf /chroot/%s/opt/montavista/*"' % (sshcmd,node,host))
    os.system('%s%s "rm -rf /chroot/%s/home/build/chroot.log"' % (sshcmd,node,host))
    os.system('%s%s "touch /chroot/%s/home/build/chroot.log"' % (sshcmd,node,host))
    # make mount point
    os.system('%s%s "mkdir -p /chroot/%s/home/build/mnt"' % (sshcmd,node,host))
    os.system('%s%s "mkdir -p /chroot/%s/home/build/mntx86"' % (sshcmd,node,host))
    # mount dvd iso in chroot
    if host != 'solaris8':
      os.system('%s%s "sudo mount -o loop %s/%s-host-%s-%s.iso /chroot/%s/home/build/mnt"' % (sshcmd,node,copydir,edition,target,buildid,host))
      if target != 'x86_586':
        os.system('%s%s "sudo mount -o loop %s/%s-host-x86_586-%s.iso /chroot/%s/home/build/mntx86"' % (sshcmd,node,copydir,edition,buildid,host))
    else:
      os.system('scp -qr %s/%s/host root@%s:/chroot/%s/home/build/mnt' % (adkmount,target,node,host))
      os.system('scp -qr %s/%s/host-tools root@%s:/chroot/%s/home/build/mnt' % (adkmount,target,node,host))
      os.system('scp -qr %s/%s/install-components root@%s:/chroot/%s/home/build/mnt' % (adkmount,target,node,host))
      os.system('scp -qr %s/%s/%s root@%s:/chroot/%s/home/build/mnt' % (adkmount,target,target,node,host))
      if includeUclibc:
        os.system('scp -qr %s/%s/%s_uclibc root@%s:/chroot/%s/home/build/mnt' % (adkmount,target,target,node,host))
      if target != 'x86_586':
        os.system('scp -qr %s/x86_586/x86* root@%s:/chroot/%s/home/build/mntx86' % (adkmount,node,host))
    # rpm2cpio install common/host rpm
    chroot(node,'echo "installing common/host rpm with rpm2cpio"',host)
    chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-4* | cpio -iud' % (rpm2cpio,host),host)
    chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-b* | cpio -iud' % (rpm2cpio,host),host)
    chroot(node,'cd /; %s /home/build/mnt/host/%s/common-rpm-d* | cpio -iud' % (rpm2cpio,host),host)
    chroot(node,'cd /; %s /home/build/mnt/host/%s/host-rpm-* | cpio -iud' % (rpm2cpio,host),host)
    # for solaris, install gcc host-tools with rpm2cpio
    inithosttools = ('binutils-2','binutils-dev','binutils-doc','gcc-4','gcc-doc','g++','libgcc1','libstdc++6-4','libstdc++6-dev')
    if host == 'solaris8':
      chroot(node,'echo "installing host-tool rpms with common-rpm"',host)
      for hosttool in inithosttools:
        chroot(node,'cd /; %s /home/build/mnt/host-tools/%s/host-tool-%s* | cpio -iud' % (rpm2cpio,host,hosttool),host)
    # install common rpms
    chroot(node,'echo "installing common rpms with common-rpm"',host)
    if host == 'solaris8':
      chroot(node,'echo "installing common-rpm and select host-tool rpms with common-rpm using --justdb"',host)
      s_install = ''
      for hosttool in inithosttools:
        s_install = 'host-tool-' + hosttool + '* ' + s_install
      s_install = '../../host/solaris8/common-rpm* ' + s_install
      chroot(node,'cd /home/build/mnt/host-tools/%s; /opt/montavista/common/bin/mvl-common-rpm -Uvh %s --justdb %s' % (host,s_install,extra),host)
      chroot(node,'cd /home/build/mnt/host-tools/%s; rm -f %s' % (host,s_install),host)
      chroot(node,'echo "installing host-rpm with host-rpm using --justdb"',host)
      chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/host/%s/host-rpm* %s --justdb' % (edition,host,extra),host)
      chroot(node,'rm -f /home/build/mnt/host/%s/host-rpm*' % host,host)
      chroot(node,'/opt/montavista/common/bin/mvl-common-rpm -Uvh /home/build/mnt/host-tools/solaris8/host-tool* %s' % extra,host)
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
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -qa | grep host-apt-rpm-plugin-devrocket | xargs /opt/montavista/%s/bin/mvl-edition-rpm -ev --nodeps' % (edition,edition),host)
    # install cross rpms
    chroot(node,'echo "installing cross rpms with edition-rpm"',host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s/cross/common/cross-* %s' % (edition,target,extra),host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s/cross/%s/cross-* %s' % (edition,target,host,extra),host)
    if includeUclibc:
      chroot(node,'echo "%s has a _uclibc target, installing cross uclibc rpms with edition-rpm"' % target,host)
      chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s_uclibc/cross/common/cross-* %s ' % (edition,target,extra),host)
      chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mnt/%s_uclibc/cross/%s/cross-* %s' % (edition,target,host,extra),host)
    # install x86_586 & x86_586_uclibc cross rpms for non x86_586 targets
    if target != 'x86_586':
      for tmptarg in x86targs:
        chroot(node,'echo "installing %s cross rpms with edition-rpm"' % tmptarg,host)
        chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mntx86/%s/cross/common/cross-* %s' % (edition,tmptarg,extra),host)
        chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm -Uvh /home/build/mntx86/%s/cross/%s/cross-* %s' % (edition,tmptarg,host,extra),host)
    # edition rpm to install all target rpms with --justdb
    chroot(node,'echo "installing target rpms with edition-rpm and --justdb"',host)
    chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mnt/%s/target/*.mvl --nodeps --justdb %s' % (edition,target,target,extra),host)
    if includeUclibc:
      chroot(node,'echo "installing uclibc target rpms with edition-rpm and --justdb"',host)
      chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s_uclibc-linux -Uvh /home/build/mnt/%s_uclibc/target/*.mvl --nodeps --justdb %s' % (edition,target,target,extra),host)
    # include x86_586 rpm install for non x86_586 targets (inc _uclibc)
    if target != 'x86_586':
      for tmptarg in x86targs:
        chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mntx86/%s/target/*.mvl --nodeps --justdb %s' % (edition,tmptarg,tmptarg,extra),host)
    # edition rpm to install selected target rpms, using adk_targetapps_<target> files
    chroot(node,'echo "installing common target rpms with edition-rpm"',host)
    if includeUclibc:
      chroot(node,'echo "%s has a _uclibc target, installing common uclibc target rpms with edition-rpm"' % target,host)
    f_common = open(builddir + '/adk/' + commonapps,'r')
    for file in f_common.readlines():
      if os.popen('%s%s "ls /chroot/%s/home/build/mnt/%s/target/%s*"' % (sshcmd,node,host,target,string.strip(file))).readlines():
        chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mnt/%s/target/%s* --nodeps --force %s' % (edition,target,target,string.strip(file),extra),host)
      if includeUclibc:
        if os.popen('%s%s "ls /chroot/%s/home/build/mnt/%s_uclibc/target/%s*"' % (sshcmd,node,host,target,string.strip(file))).readlines():
          chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s_uclibc-linux -Uvh /home/build/mnt/%s_uclibc/target/%s* --nodeps --force %s' % (edition,target,target,string.strip(file),extra),host)
      # include x86_586 rpm install for non x86_586 targets (inc _uclibc)
      if target != 'x86_586':
        for tmptarg in x86targs:
          if os.popen('%s%s "ls /chroot/%s/home/build/mntx86/%s/target/%s*"' % (sshcmd,node,host,tmptarg,string.strip(file))).readlines():
            chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mntx86/%s/target/%s* --nodeps --force %s' % (edition,tmptarg,tmptarg,string.strip(file),extra),host)
    f_common.close()
    # install target specific target apps
    f_targ = open('%s/adk/%s_%s' % (builddir,targetappsprefix,target))
    for file in f_targ.readlines():
      if os.popen('%s%s "ls /chroot/%s/home/build/mnt/%s/target/%s*"' % (sshcmd,node,host,target,string.strip(file))).readlines():
        chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mnt/%s/target/%s* --nodeps --force %s' % (edition,target,target,string.strip(file),extra),host)
    f_targ.close()
    # install _uclibc specific target apps if target has _uclibc target
    if includeUclibc:
      f_targ = open('%s/adk/%s_%s_uclibc' % (builddir,targetappsprefix,target))
      for file in f_targ.readlines():
        if os.popen('%s%s "ls /chroot/%s/home/build/mnt/%s_uclibc/target/%s*"' % (sshcmd,node,host,target,string.strip(file))).readlines():
          chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s_uclibc-linux -Uvh /home/build/mnt/%s_uclibc/target/%s* --nodeps --force %s' % (edition,target,target,string.strip(file),extra),host)
      f_targ.close()
    # install x86_586 and x86_586_uclibc specific target apps for non x86_586 targets
    if target != 'x86_586':
      for tmptarg in x86targs:
        f_targ = open('%s/adk/%s_%s' % (builddir,targetappsprefix,tmptarg))
        for file in f_targ.readlines():
          if os.popen('%s%s "ls /chroot/%s/home/build/mntx86/%s/target/%s*"' % (sshcmd,node,host,tmptarg,string.strip(file))).readlines():
            chroot(node,'/opt/montavista/%s/bin/mvl-edition-rpm --target=%s-linux -Uvh /home/build/mntx86/%s/target/%s* --nodeps --force %s' % (edition,tmptarg,tmptarg,string.strip(file),extra),host)
        f_targ.close()
    if host != 'solaris8':
      os.system('ssh %s "sudo umount /chroot/%s/home/build/mnt"' % (node,host))
      if target != 'x86_586':
        os.system('ssh %s "sudo umount /chroot/%s/home/build/mntx86"' % (node,host))
    else:
      os.system('ssh root@%s "rm -rf /chroot/%s/home/build/mnt"' % (node,host))
      os.system('ssh root@%s "rm -rf /chroot/%s/home/build/mntx86"' % (node,host))
    # tar up /opt/montavista
    if host != 'solaris8':
      os.system('%s%s "cd /chroot/%s/opt; sudo tar -cf %s/%s-%s-%s.tar montavista"' % (sshcmd,node,host,
                 builddir,host,target,buildid))
      os.system('sudo scp %s:%s/%s-%s-%s.tar %s' % (node,builddir,host,target,buildid,adktardir))
    else:
      os.system('%s%s "cd /chroot/%s/opt; tar -cf %s/%s-%s-%s.tar montavista"' % (sshcmd,node,host,
                 builddir,host,target,buildid))
      os.system('scp root@%s:%s/%s-%s-%s.tar %s' % (node,builddir,host,target,buildid,adktardir))
    # clean node
    if host != 'solaris8':
      os.system('%s%s "sudo rm -rf /chroot/%s/opt/montavista/*"' % (sshcmd,node,host))
      os.system('%s%s "sudo rm -rf %s/%s-%s-%s.tar"' % (sshcmd,node,builddir,host,target,buildid))
    else:
      os.system('%s%s "rm -rf /chroot/%s/opt/montavista/*"' % (sshcmd,node,host))
      os.system('%s%s "rm -rf %s/%s-%s-%s.tar"' % (sshcmd,node,builddir,host,target,buildid))
    os.system('%s%s "rm -rf /chroot/%s/home/build/mnt"' % (sshcmd,node,host))
    os.system('%s%s "rm -rf /chroot/%s/home/build/mntx86"' % (sshcmd,node,host))
    # copy log
    os.system('%s%s "cp /chroot/%s/home/build/chroot.log %s/%s-%s-%s.log"' % (sshcmd,node,host,logdir,host,target,buildid))
    releaseResource(node)
  # add windows junk (the same steps as above, although not using chroot commands)
  elif host == 'cygwin':
    log = '/home/build/dailybuild/chroot.log'
    cygmnt = '/home/build/dailybuild/mnt'
    cygmntx86 = '/home/build/dailybuild/mntx86'
    exppath = 'export PATH=/bin:/sbin:/usr/bin'
    commonrpm = '/opt/montavista/common/bin/mvl-common-rpm'
    editionrpm = '/opt/montavista/%s/bin/mvl-edition-rpm' % edition
    # check out node
    cygnode = getCygwin()
    print 'building adk for %s on %s using %s...' % (target,host,cygnode)
    # clean node
    os.system('ssh -p %s %s "rm -rf /opt/montavista/*"' % (cygport,cygnode))
    os.system('ssh -p %s %s "rm -rf %s"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "touch %s"' % (cygport,cygnode,log))
    # make mount point
    os.system('ssh -p %s %s "mkdir -p %s"' % (cygport,cygnode,cygmnt))
    os.system('ssh -p %s %s "mkdir -p %s"' % (cygport,cygnode,cygmntx86))
    # copy host rpms from dvd iso mount
    os.system('scp -r -q -P %s %s/%s/host %s:%s' % (cygport,adkmount,target,cygnode,cygmnt))
    for tmptarg in x86targs:
      os.system('scp -r -q -P %s %s/x86_586/%s %s:%s' % (cygport,adkmount,tmptarg,cygnode,cygmntx86))
    # rpm2cpio install common/host rpm
    os.system('ssh -p %s %s "echo \'installing common/host rpm with rpm2cpio\' >> %s 2>&1"' % (cygport, cygnode,log))
    os.system('ssh -p %s %s "%s; cd /; rpm2cpio %s/host/windows2000/common-rpm-4* | cpio -iud >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,log))
    os.system('ssh -p %s %s "%s; cd /; rpm2cpio %s/host/windows2000/common-rpm-b* | cpio -iud >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,log))
    os.system('ssh -p %s %s "%s; cd /; rpm2cpio %s/host/windows2000/common-rpm-d* | cpio -iud >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,log))
    os.system('ssh -p %s %s "%s; cd /; rpm2cpio %s/host/windows2000/host-rpm-* | cpio -iud >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,log))
    # install common rpms
    os.system('ssh -p %s %s "echo \'installing common rpms with common-rpm\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/host/windows2000/common-rpm* --justdb >> %s 2>&1"' % (cygport, cygnode,exppath,commonrpm,cygmnt,log))
    os.system('ssh -p %s %s "%s; ls %s/host/windows2000/common* | grep -v common-rpm | xargs %s -Uvh --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,commonrpm,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/host/common/common* >> %s 2>&1"' % (cygport,cygnode,exppath, commonrpm,cygmnt,log))
    # install host rpms
    os.system('ssh -p %s %s "echo \'installing host rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/host/windows2000/host-rpm* --justdb >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,cygmnt,log))
    os.system('ssh -p %s %s "%s; ls %s/host/windows2000/host* | grep -v host-rpm | grep -v postinstall | xargs %s -Uvh >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,editionrpm,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/host/common/host* >> %s 2>&1"' % (cygport,cygnode,exppath, editionrpm,cygmnt,log))
    # uninstall common-apt-rpm-plugin-devrocket
    os.system('ssh -p %s %s "echo \'uninstalling common/host apt-rpm-plugin-devrocket\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "%s; %s -qa | grep apt-rpm-plugin-devrocket | xargs %s -ev --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,commonrpm,commonrpm,log))
    # uninstall host-apt-rpm-plugin-devrocket
    os.system('ssh -p %s %s "%s; %s -qa | grep apt-rpm-plugin-devrocket | xargs %s -ev --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,editionrpm,log))
    # install required x86_586 cross & target rpms, for non x86_586 targets
    # then create tar file of devkit/x86, then delete devkit/x86 and install main target and 
    # make tarfile of montavista
    if target != 'x86_586':
      for tmptarg in x86targs:
        os.system('ssh -p %s %s "mkdir -p %s/%s"' % (cygport,cygnode,cygmntx86,tmptarg))
        os.system('ssh -p %s %s "chmod -R u+w %s/%s"' % (cygport,cygnode,cygmntx86,tmptarg))
        os.system('scp -r -q -P %s %s/x86_586/%s/cross %s:%s/%s' % (cygport,adkmount,tmptarg,cygnode, cygmntx86,tmptarg))
        os.system('ssh -p %s %s "echo \'install cross %s rpms with edition-rpm\' >> %s 2>&1"' % (cygport, cygnode,tmptarg,log))
        os.system('ssh -p %s %s "%s; %s -Uvh %s/%s/cross/common/cross* >> %s 2>&1"' % (cygport,cygnode, exppath,editionrpm,cygmntx86,tmptarg,log))
        os.system('ssh -p %s %s "%s; %s -Uvh %s/%s/cross/windows2000/cross* >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,cygmntx86,tmptarg,log))
        os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmntx86))
      for tmptarg in x86targs:
        os.system('ssh -p %s %s "mkdir -p %s/%s"' % (cygport,cygnode,cygmntx86,tmptarg))
        os.system('ssh -p %s %s "chmod -R u+w %s/%s"' % (cygport,cygnode,cygmntx86,tmptarg))
        os.system('scp -r -q -P %s %s/x86_586/%s/target %s:%s/%s' % (cygport,adkmount,tmptarg,cygnode,cygmntx86,tmptarg))
        # install all target rpms with --justdb
        os.system('ssh -p %s %s "echo \'install all %s target rpms with edition-rpm using --justdb\' >> %s 2>&1"' % (cygport,cygnode,tmptarg,log))
        os.chdir('%s/x86_586/%s/target' % (adkmount,tmptarg))
        for file in os.popen('ls *.mvl').readlines():
          os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh --justdb %s/%s/target/%s --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,tmptarg,cygmntx86,tmptarg,string.strip(file),log))
        os.chdir(builddir)
        # install common target rpms
        os.system('ssh -p %s %s "echo \'install %s common target rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,tmptarg,log))
        f_common = open(builddir + '/adk/' + commonapps,'r')
        for file in f_common.readlines():
          if os.popen('ls %s/x86_586/%s/target/%s*' % (adkmount,tmptarg,string.strip(file))).readlines():
            os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh %s/%s/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,tmptarg,cygmntx86,tmptarg,string.strip(file),log))
        f_common.close()
        # install x86_586 and x86_586_uclibc specific target apps for non x86_586 targets
        f_targ = open('%s/adk/%s_%s' % (builddir,targetappsprefix,tmptarg))
        os.system('ssh -p %s %s "echo \'install %s specific target rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,tmptarg,log))
        for file in f_targ.readlines():
          if os.popen('ls %s/x86_586/%s/target/%s*' % (adkmount,tmptarg,string.strip(file))).readlines():
            os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh %s/%s/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,tmptarg,cygmntx86,tmptarg,string.strip(file),log))
        f_targ.close()
        os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmntx86))
      # print disk usage after install
      os.system('ssh -p %s %s "echo \'disk usage after x86_586 install\' >> %s 2>&1"' % (cygport,cygnode,log))
      os.system('ssh -p %s %s "%s; df -h >> %s 2>&1"' % (cygport,cygnode,exppath,log))
      # tar up /opt/montavista/devkit/x86
      os.system('ssh -p %s root@%s "cd /opt/montavista/%s/devkit; tar -cf /home/build/dailybuild/windows2000-%s-x86-%s.tar x86"' % (cygport,cygnode,edition,target,buildid))
      os.system('scp -q -P %s root@%s:/home/build/dailybuild/windows2000-%s-x86-%s.tar %s' % (cygport,cygnode,target,buildid,adktardir))
      os.system('sudo chown root.root %s/windows2000-%s-x86-%s.tar' % (adktardir,target,buildid))
      # clean node
      os.system('ssh -p %s %s "%s; rm -rf /opt/montavista/%s/devkit/x86 >> %s 2>&1"' % (cygport,cygnode,exppath,edition,log))
      os.system('ssh -p %s %s "%s; rm -rf %s >> %s 2>&1"' % (cygport,cygnode,exppath,cygmntx86,log))
      os.system('ssh -p %s root@%s "rm -rf /home/build/dailybuild/windows2000-%s-x86-%s.tar"' % (cygport,cygnode,target,buildid))

    # delete host directory and copy cross
    os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmnt))
    os.system('ssh -p %s %s "mkdir -p %s/%s"' % (cygport,cygnode,cygmnt,target))
    os.system('ssh -p %s %s "chmod -R u+w %s/%s"' % (cygport,cygnode,cygmnt,target))
    os.system('scp -r -q -P %s %s/%s/%s/cross %s:%s/%s' % (cygport,adkmount,target,target,cygnode,cygmnt,target))
    # install cross rpms (plus uclibc if needed, plus x86_586, and x86_586_uclibc if needed)
    os.system('ssh -p %s %s "echo \'install cross rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/%s/cross/common/cross* >> %s 2>&1"' % (cygport,cygnode, exppath,editionrpm,cygmnt,target,log))
    os.system('ssh -p %s %s "%s; %s -Uvh %s/%s/cross/windows2000/cross* >> %s 2>&1"' % (cygport,cygnode, exppath,editionrpm,cygmnt,target,log))
    os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmnt))
    if includeUclibc:
      os.system('ssh -p %s %s "mkdir -p %s/%s_uclibc"' % (cygport,cygnode,cygmnt,target))
      os.system('ssh -p %s %s "chmod -R u+w %s/%s_uclibc"' % (cygport,cygnode,cygmnt,target))
      os.system('scp -r -q -P %s %s/%s/%s_uclibc/cross %s:%s/%s_uclibc' % (cygport,adkmount,target, target,cygnode,cygmnt,target))
      os.system('ssh -p %s %s "echo \'install cross uclibc rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,log))
      os.system('ssh -p %s %s "%s; %s -Uvh %s/%s_uclibc/cross/common/cross* >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,cygmnt,target,log))
      os.system('ssh -p %s %s "%s; %s -Uvh %s/%s_uclibc/cross/windows2000/cross* >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,cygmnt,target,log))
    os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmnt))
    # copy target rpms
    os.system('ssh -p %s %s "mkdir -p %s/%s"' % (cygport,cygnode,cygmnt,target))
    os.system('ssh -p %s %s "chmod -R u+w %s/%s"' % (cygport,cygnode,cygmnt,target))
    os.system('scp -r -q -P %s %s/%s/%s/target %s:%s/%s' % (cygport,adkmount,target,target, cygnode,cygmnt,target))
    if includeUclibc:
      os.system('ssh -p %s %s "mkdir -p %s/%s_uclibc"' % (cygport,cygnode,cygmnt,target))
      os.system('ssh -p %s %s "chmod -R u+w %s/%s_uclibc"' % (cygport,cygnode,cygmnt,target))
      os.system('scp -r -q -P %s %s/%s/%s_uclibc/target %s:%s/%s_uclibc' % (cygport,adkmount,target,target, cygnode,cygmnt,target))
    # install all target rpms (with _uclibc) using --justdb
    os.system('ssh -p %s %s "echo \'install all target rpms with edition-rpm using --justdb\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.chdir('%s/%s/%s/target' % (adkmount,target,target))
    for file in os.popen('ls *.mvl').readlines():
      os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh --justdb %s/%s/target/%s --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
    os.chdir(builddir)
    if includeUclibc:
      os.chdir('%s/%s/%s_uclibc/target' % (adkmount,target,target))
      for file in os.popen('ls *.mvl').readlines():
        os.system('ssh -p %s %s "%s; %s --target=%s_uclibc-linux -Uvh --justdb %s/%s_uclibc/target/%s --nodeps >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
      os.chdir(builddir)
    # install common target rpms (with _uclibc)
    os.system('ssh -p %s %s "echo \'install common target rpms with edition-rpm\' >> %s 2>&1"' % (cygport, cygnode,log))
    f_common = open(builddir + '/adk/' + commonapps,'r')
    for file in f_common.readlines():
      if os.popen('ls %s/%s/%s/target/%s*' % (adkmount,target,target,string.strip(file))).readlines():
        os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh %s/%s/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
      if includeUclibc:
        if os.popen('ls %s/%s/%s_uclibc/target/%s*' % (adkmount,target,target,string.strip(file))).readlines():
          os.system('ssh -p %s %s "%s; %s --target=%s_uclibc-linux -Uvh %s/%s_uclibc/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
    f_common.close()
    # install target specific taregt apps
    os.system('ssh -p %s %s "echo \'install %s target rpms with edition-rpm\' >> %s 2>&1"' % (cygport, cygnode,target,log))
    f_targ = open('%s/adk/%s_%s' % (builddir,targetappsprefix,target))
    for file in f_targ.readlines():
      if os.popen('ls %s/%s/%s/target/%s*' % (adkmount,target,target,string.strip(file))).readlines():
        os.system('ssh -p %s %s "%s; %s --target=%s-linux -Uvh %s/%s/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
    f_targ.close()
    if includeUclibc:
      # install uclibc target specific taregt apps
      os.system('ssh -p %s %s "echo \'install %s_uclibc target rpms with edition-rpm\' >> %s 2>&1"' % (cygport,cygnode,target,log))
      f_targ = open('%s/adk/%s_%s_uclibc' % (builddir,targetappsprefix,target))
      for file in f_targ.readlines():
        if os.popen('ls %s/%s/%s_uclibc/target/%s*' % (adkmount,target,target,string.strip(file))).readlines():
          os.system('ssh -p %s %s "%s; %s --target=%s_uclibc-linux -Uvh %s/%s_uclibc/target/%s* --nodeps --force >> %s 2>&1"' % (cygport,cygnode,exppath,editionrpm,target,cygmnt,target,string.strip(file),log))
      f_targ.close()
    os.system('ssh -p %s %s "rm -rf %s/*"' % (cygport,cygnode,cygmnt))
    # print disk usage after install
    os.system('ssh -p %s %s "echo \'disk usage after install\' >> %s 2>&1"' % (cygport,cygnode,log))
    os.system('ssh -p %s %s "%s; df -h >> %s 2>&1"' % (cygport,cygnode,exppath,log))
    # tar up /opt/montavista
    os.system('ssh -p %s root@%s "cd /opt; tar -cf /home/build/dailybuild/windows2000-%s-%s.tar montavista"' % (cygport,cygnode,target,buildid))
    os.system('scp -q -P %s root@%s:/home/build/dailybuild/windows2000-%s-%s.tar %s' % (cygport,cygnode, target,buildid,adktardir))
    os.system('sudo chown root.root %s/windows2000-%s-%s.tar' % (adktardir,target,buildid))
    # clean node
    os.system('ssh -p %s %s "%s; rm -rf /opt/montavista/* >> %s 2>&1"' % (cygport,cygnode,exppath,log))
    os.system('ssh -p %s %s "%s; rm -rf %s >> %s 2>&1"' % (cygport,cygnode,exppath,cygmnt,log))
    os.system('ssh -p %s %s "%s; rm -rf %s >> %s 2>&1"' % (cygport,cygnode,exppath,cygmntx86,log))
    os.system('ssh -p %s root@%s "rm -rf /home/build/dailybuild/windows2000-%s-%s.tar"' % (cygport,cygnode,target,buildid))
    # copy log
    os.system('ssh -p %s %s "scp %s overlord:%s/cygwin-%s-%s.log"' % (cygport,cygnode,log,logdir,target,buildid))
    releaseResource(cygnode)

def createInstaller(host,target):
  # get resource, run create_adk_installer, return resource
  node = getResource(buildtag,buildid,nodetype,"adk " + host + " " + target + " installer build")
  print 'building adk installer for %s on %s using %s...' % (target,host,node)
  log = '%s/%s-%s-%s-installer.log' % (logdir,host,target,buildid)
  if host == 'linux':
    os.system('ssh %s "cd %s/adk; sudo ./create_adk_installer %s %s %s %s %s/%s/linux %s/adk > %s 2>&1"' % (node,builddir,host,target,buildid,adktardir,adkdir,target,builddir,log))
  elif host == 'solaris8':
    os.system('ssh %s "cd %s/adk; sudo ./create_adk_installer %s %s %s %s %s/%s/solaris %s/adk > %s 2>&1"' % (node,builddir,host,target,buildid,adktardir,adkdir,target,builddir,log))
  else:
    os.system('ssh %s "cd %s/adk; sudo ./create_adk_installer %s %s %s %s %s/%s/windows %s/adk %s > %s 2>&1"' % (node,builddir,host,target,buildid,adktardir,adkdir,target,builddir,adkcygwintar,log))
  releaseResource(node)

def createIso(target,cdhost):
  cdnode = getResource(buildtag,buildid,nodetype,"Making ADK CD Images")
  print "making %s cd for %s on %s..." % (target,cdhost,cdnode)
  sys.__stdout__.flush()
  cdtempdir = '/var/tmp/CDTEMP'
  mkisocmd = 'mkisofs -quiet -r -J -joliet-long -allow-leading-dots -no-split-symlink-components '
  mkisocmd = mkisocmd + '-no-split-symlink-fields '
  #mkisocmd = mkisocmd + '-V ' + edition + '-50-' + target + '-adk-' + cdhost + ' '
  mkisocmd = mkisocmd + '-V ' + voledition + '-' + target + '-adk-' + cdhost + ' '
  mkisocmd = mkisocmd + '-o ' + edition + '-adk-' + target + '-' + cdhost + '-' + buildid + '.iso -graft-points '
  mkisocmd = mkisocmd + 'InstallGuide-ADK_5_0.pdf=' + adkdir + '/' + target + '/InstallGuide-ADK_5_0.pdf '
  mkisocmd = mkisocmd + 'LICENSE.txt=' + adkdir + '/' + target + '/LICENSE.txt '
  mkisocmd = mkisocmd + 'README.txt=' + adkdir + '/' + target + '/README.txt '
  mkisocmd = mkisocmd + cdhost + '/=' + adkdir + '/' + target + '/' + cdhost + '/ '
  mkisocmd = mkisocmd + 'VirtualTargets/=' + adkdir + '/' + target + '/VirtualTargets/ '
  if cdhost == 'windows':
    mkisocmd = mkisocmd + 'autorun.inf=' + adkdir + '/' + target + '/autorun.inf '
    mkisocmd = mkisocmd + 'mvista.ico=' + adkdir + '/' + target + '/mvista.ico '
  os.system('ssh %s "mkdir -p %s; cd %s; %s"' % (cdnode,cdtempdir,cdtempdir,mkisocmd))
  os.system('ssh %s "cd %s; md5sum *.iso > md5sum"' % (cdnode,cdtempdir))
  os.system('ssh %s "cp %s/*.iso %s"' % (cdnode,cdtempdir,adkimagedir))
  r_md5sum = getResource(buildtag,buildid,"md5sum","Adding ADK md5sum")
  os.system('ssh %s "cat %s/md5sum >> %s/README.md5sum"' % (cdnode,cdtempdir,adkimagedir))
  releaseResource(r_md5sum)
  os.system('ssh %s "rm -rf %s"' % (cdnode,cdtempdir))
  releaseResource(cdnode)
  return

# usage
if len(sys.argv) != 8:
  print 'usage: %s %s %s %s %s %s %s %s' % (sys.argv[0],'<buildtag>','<tar|skip>','<exe|skip>','<iso|skip>','<clean|noclean>','<tsuki installer path>','<pro|mobilinux>')
  sys.exit(1)
buildtag = sys.argv[1]
if string.find(buildtag,'blackfoot') == -1 and string.find(buildtag,'tahoma') == -1:
  print 'must use blackfoot buildtag, try again'
  sys.exit(1)

buildid = string.split(buildtag,'_')[1]
print 'using buildid = ' + buildid
builddir = os.getcwd()

if sys.argv[2] == 'tar':
  makeTar = 1
elif sys.argv[2] == 'skip':
  makeTar = 0
else:
  print 'value not tar or skip, bye!'
  sys.exit(1)

if sys.argv[3] == 'exe':
  makeExe = 1
elif sys.argv[3] == 'skip':
  makeExe = 0
else:
  print 'value not exe or skip, bye!'
  sys.exit(1)

if sys.argv[4] == 'iso':
  makeIso = 1
elif sys.argv[4] == 'skip':
  makeIso = 0
else:
  print 'value not iso or skip, bye!'
  sys.exit(1)

if sys.argv[5] == 'clean':
  clean = 1
elif sys.argv[5] == 'noclean':
  clean = 0
else:
  print 'value not clean or noclean, bye!'
  sys.exit(1)

tsukidir = sys.argv[6]
edition = sys.argv[7]

copydir = '/mvista/dev_area/%s/%s/dvdimages' % (edition,buildtag)
if not os.path.exists(copydir):
  print 'path %s does not exists, check your buildtag' % copydir
  sys.exit(1)

if edition == 'pro':
  # testing targets, remove and use the commented lines below for real builds
  adk_uclibc_targets      = ()
  adk_targets             = ('ppc_440',)
  #hosts                  = ('centos3',)
  #windows                = 0
  targetappsprefix = 'adk_targetapps'
  voledition == 'edition'
  #adk_uclibc_targets     = ('arm_v5t_le', 'arm_xscale_be', 'mips2_fp_be', 'mips2_fp_le', 'x86_586',)
  #adk_targets            = ('x86_em64t','mips64_fp_be','ppc_440','ppc_440ep','ppc_83xx','ppc_85xx', 'x86_pentium3', 'x86_pentium4')
  hosts                   = ('centos3','solaris8','suse90')
  installhosts            = ('linux','solaris8')
elif edition == 'mobilinux':
  # testing targets, remove and use the commented lines below for real builds
  #hosts                  = ()
  #windows                = 0
  voledition == 'mbl'
  targetappsprefix = 'mobilinux_adk_targetapps'
  adk_uclibc_targets     = ('arm_v6_vfp_le',)
  #adk_uclibc_targets     = ('arm_v5t_le',)
  adk_targets            = ()
  hosts                   = ('centos3','centos3_64','suse90')
  #hosts                   = ('centos3','suse90',')
  installhosts            = ('linux',)
else:
  print 'unrecognized %s edition...only pro and mobi are supported at this time.' % edition
  sys.exit(1)

commonapps = targetappsprefix + '_common'
logdir = '/mvista/dev_area/%s/%s/logs/adk' % (edition,buildtag)
adkimagedir = '/mvista/dev_area/%s/%s/adkimages' % (edition,buildtag)
adkdir = '/mvista/dev_area/%s/%s/adk' % (edition,buildtag)
adktardir = '/mvista/dev_area/%s/%s/adktars' % (edition,buildtag)
adkvmwaredir = '/mvista/dev_area/%s/%s/adkvmware' % (edition,buildtag)
adkdocsdir = '/mvista/dev_area/%s/%s/adkdocs' % (edition,buildtag)
if not os.path.exists(adkvmwaredir):
  os.system('mkdir -p %s' % adkvmwaredir)
adkcygwintar = '/mvista/dev_area/%s/%s/adkcygwintar/cht-0702774.tar' % (edition,buildtag)
adkmount = '/var/tmp/adkmounts'

if makeTar:
  if not os.path.exists(logdir):
    os.system('mkdir -p %s' % logdir)
  elif clean:
    print 'removing %s/*' % logdir
    os.system('rm -rf %s/*' % logdir)
  if not os.path.exists(adktardir):
    os.system('mkdir -p %s' % adktardir)
  elif clean:
    print 'removing %s/*' % adktardir
    os.system('rm -rf %s/*' % adktardir)
  if not os.path.exists(adkmount):
    os.system('mkdir -p %s' % adkmount)

  node_threads = []
  cygwin_threads = []

  # make mount point for x86_586 for solaris & windows
  os.system('mkdir -p %s/x86_586' % adkmount)
  os.system('sudo mount -o loop %s/%s-host-x86_586-%s.iso %s/x86_586' % (copydir,edition,buildid,adkmount))
  for target in adk_uclibc_targets:
    if target != 'x86_586':
      # make mount point for solaris & windows
      os.system('mkdir -p %s/%s' % (adkmount,target))
      os.system('sudo mount -o loop %s/%s-host-%s-%s.iso %s/%s' % (copydir,edition,target,buildid,adkmount,target))
    # add argument to buildThread to indicate uclibc is inculded
    for host in hosts:
      t = threading.Thread(target=buildThread, name=target, args=(host,target,1))
      node_threads.append(t)
    if windows:
      ct = threading.Thread(target=buildThread, name=target, args=('cygwin',target,1))
      cygwin_threads.append(ct)
  for target in adk_targets:
    if target != 'x86_586':
      # make mount point for solaris & windows
      os.system('mkdir -p %s/%s' % (adkmount,target))
      os.system('sudo mount -o loop %s/%s-host-%s-%s.iso %s/%s' % (copydir,edition,target,buildid,adkmount,target))
    for host in hosts:
      t = threading.Thread(target=buildThread, name=target, args=(host,target,0))
      node_threads.append(t)
    if windows:
      ct = threading.Thread(target=buildThread, name=target, args=('cygwin',target,0))
      cygwin_threads.append(ct)

  for t in node_threads:
    t.start()
  for c in cygwin_threads:
    c.start()
  for t in node_threads:
    t.join()
  for c in cygwin_threads:
    c.join()
 
  # unmount mount points
  for target in adk_uclibc_targets:
    os.system('sudo umount %s/%s' % (adkmount,target))
  for target in adk_targets: 
    os.system('sudo umount %s/%s' % (adkmount,target))
  os.system('sudo umount %s/x86_586' % adkmount)
  os.system('rm -rf %s' % adkmount)

if makeExe:
  # for each tar, untar on linux host and issue bitrock installbuilder command
  print 'making threads for installbuilder builds'
  if not os.path.exists(adkdir):
    os.system('mkdir -p %s' % adkdir)
  elif clean:
    print 'removing %s/*' % adkdir
    os.system('sudo rm -rf %s/*' % adkdir)
  node_threads = []
  for target in adk_uclibc_targets:
    for host in installhosts:
      t = threading.Thread(target=createInstaller, name=target, args=(host,target))
      node_threads.append(t)
    if windows:
      t = threading.Thread(target=createInstaller, name=target, args=('windows2000',target))
      node_threads.append(t)
  for target in adk_targets:
    for host in installhosts:
      t = threading.Thread(target=createInstaller, name=target, args=(host,target))
      node_threads.append(t)
    if windows:
      t = threading.Thread(target=createInstaller, name=target, args=('windows2000',target))
      node_threads.append(t)
  for t in node_threads:
    t.start()
  for t in node_threads:
    t.join()

if makeIso:
  # export latest docs
  if os.path.exists(adkdocsdir):
    os.system('rm -rf %s' % adkdocsdir)
  os.system('mkdir -p %s' % adkdocsdir)
  os.chdir('%s/..' % adkdocsdir)
  os.system('cvs -d :ext:cvs.sh.mvista.com:/cvsdev/Documentation export -D now -d adkdocs adk/%s' % edition) 
  # link virtual target vmware images to each adk/<target> directory to be included on iso image
  # copy VMWare installer and jre from adk directory
  isohosts = []
  if windows:
    isohosts.append('windows')
  for h in installhosts:
    if h == 'solaris8':
      isohosts.append('solaris')
    else:
      isohosts.append(h)
  for target in adk_uclibc_targets:
    for host in isohosts:
      os.chdir('%s/%s/%s' % (adkdir,target,host))
      os.system('sudo rm -f VMware-player*')
      os.system('sudo rm -f jre-1_5_0_11*')
      os.system('sudo rm -f devrocket-5*')
      os.system('sudo cp -a %s/adk/jre-*%s* .' % (builddir,host))
      os.system('sudo cp -a %s/devrocket-5*%s* .' % (tsukidir,host))
      if host in ('linux',):
        os.system('sudo cp -a %s/adk/VMware-player*.rpm .' % builddir)
      elif host != 'solaris':
        os.system('sudo cp -a %s/adk/VMware-player*.exe .' % builddir)
    if not os.path.exists('%s/%s/VirtualTargets' % (adkdir,target)):
      os.system('sudo mkdir -p %s/%s/VirtualTargets' % (adkdir,target))
    os.chdir('%s/%s/VirtualTargets' % (adkdir,target))
    os.system('sudo rm -f *.zip')
    os.system('sudo ln %s/* .' % adkvmwaredir)
    os.chdir('%s/%s' % (adkdir,target))
    os.system('sudo rm -f mvista.ico autorun.inf')
    os.system('sudo cp -a %s/adk/mvista.ico .' % builddir)
    os.system('sudo cp -a %s/adk/autorun.inf .' % builddir)
    os.system('sudo cp -a %s/* .' % adkdocsdir)
  for target in adk_targets: 
    for host in isohosts:
      os.chdir('%s/%s/%s' % (adkdir,target,host))
      os.system('sudo rm -f VMware-player*')
      os.system('sudo rm -f jre-1_5_0_11*')
      os.system('sudo rm -f devrocket-5*')
      os.system('sudo cp -a %s/adk/jre-*%s* .' % (builddir,host))
      os.system('sudo cp -a %s/devrocket-5*%s* .' % (tsukidir,host))
      if host in ('linux',):
        os.system('sudo cp -a %s/adk/VMware-player*.rpm .' % builddir)
      elif host != 'solaris':
        os.system('sudo cp -a %s/adk/VMware-player*.exe .' % builddir)
    if not os.path.exists('%s/%s/VirtualTargets' % (adkdir,target)):
      os.system('sudo mkdir -p %s/%s/VirtualTargets' % (adkdir,target))
    os.chdir('%s/%s/VirtualTargets' % (adkdir,target))
    os.system('sudo rm -f *.zip')
    os.system('sudo ln %s/* .' % adkvmwaredir)
    os.chdir('%s/%s' % (adkdir,target))
    os.system('sudo rm -f mvista.ico autorun.inf')
    os.system('sudo cp -a %s/adk/mvista.ico .' % builddir)
    os.system('sudo cp -a %s/adk/autorun.inf .' % builddir)
    os.system('sudo cp -a %s/* .' % adkdocsdir)
  # make dvd iso images
  print 'making threads for dvd iso builds'
  if not os.path.exists(adkimagedir):
    os.system('mkdir -p %s' % adkimagedir)
  elif clean:
    print 'removing %s/*' % adkimagedir
    os.system('rm -rf %s/*' % adkimagedir)
  genREADME()
  node_threads = []
  for target in adk_uclibc_targets:
    for host in isohosts:
      t = threading.Thread(target=createIso, name=target, args=(target,host))
      node_threads.append(t)
  for target in adk_targets:
    for host in isohosts:
      t = threading.Thread(target=createIso, name=target, args=(target,host))
      node_threads.append(t)
  for t in node_threads:
    t.start()
  for t in node_threads:
    t.join()

