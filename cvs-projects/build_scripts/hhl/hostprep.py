#!/usr/bin/python
import os, sys, string, time

# Args:
# 1- <hostname>
# 2- <path> to SRPMS directory & RPMS 
# 3- <target> 
# 4- <foundation path>
# 5- <all|installer> (prep for full build or just installer build)
# 6- <product>
#
# This script will delete BUILD, SOURCES, SPECS, SRPMS and RPMS from /chroot/<hostname>/home/build,
# make BUILD, SOURCES, SPECS, SRPMS and RPMS/install in /chroot/<hostname>/home/build,
# copy all SRPMS from <path> to /chroot/<hostname>/home/build/SRPMS,
# and copy all <foundation path>/host, <foundation path>/<target> rpms to 
#     /chroot/<hostname>/home/build/RPMS/install

if len(sys.argv) != 7:
  print '\nusage: %s %s %s %s %s %s %s' % (sys.argv[0], '<hostname>','<path>','<target>','<foundation path>','<all|installer>', '<product>')
  print '\nwhere <path> is the path to the src.mvls and mvls that need to be copied to'
  print 'the chrooted environment'
  print '\nif <foundation path> is "skip" the script will not delete /chroot/<hostname>/home/build/RPMS/install'
  print 'which assumes that the build will be using a released foundation build, currently present'
  print 'on the chrooted environment.'
  print '\nIf last argument is all, chroot env. will be prepped to build cross & host rpms,'
  print 'otherwise, it will be prepped to just build the cross-mvl-installer rpm.\n'
  print '\n# of args = ' + str(len(sys.argv))
  print '\nHere are the args:'
  for x in sys.argv:
    print x
  sys.exit(1)

hostname = sys.argv[1]
path = sys.argv[2]
target = sys.argv[3]
foundation = sys.argv[4]
buildwhat = sys.argv[5]
product = sys.argv[6]

builddir = '/chroot/%s/home/build' % (hostname)
node = string.strip(os.popen('hostname').read())

if hostname == 'solaris8':
  cpall = 'cp -r'
else:
  cpall = 'cp -a'

if string.find(target,'uclibc') > -1:
  glibc = 'uclibc'
else:
  glibc = 'glibc'

print 'Starting Host Setup for %s...' % (target)
sys.__stdout__.flush()
if buildwhat == 'all':
  print 'Copying src.mvl and mvls from %s to %s on %s' % (path,builddir,node)
  sys.__stdout__.flush()
  if target != 'host':
    os.system('%s %s/SRPMS/cross* %s/SRPMS' % (cpall,path,builddir))
  elif target == "host":
    os.system('%s %s/SRPMS/common-* %s/SRPMS' % (cpall,path,builddir))
    os.system('%s %s/SRPMS/host* %s/SRPMS' % (cpall,path,builddir))
    if os.path.exists('%s/common/SRPMS' % (path)):
      os.system('%s %s/common/SRPMS/* %s/SRPMS' % (cpall,path,builddir))
  os.system('rm -f %s/SRPMS/*lsp*' % (builddir))
  os.system('rm -f %s/SRPMS/*ramdisk*' % (builddir))
  os.system('%s %s/host/common/*.mvl %s/RPMS/install/host/common' % (cpall,path,builddir))
  os.system('%s %s/host/%s/common-* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
  os.system('%s %s/host/%s/host-* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
  if product in ("pro","propk"):
    os.system('%s %s/host/%s/host-tftp-hpa* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
    os.system('%s %s/host/%s/host-mkimage* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
  if product in ('ceeeclipse','dev','fe','feeclipse',):
    os.system('%s %s/common/common/*.mvl %s/RPMS/install' % (cpall,path,builddir))
    #if hostname == 'mandrake91':
    #  os.system('%s /mvista/dev_area/licensing/host/redhat90/common-flexnet-sdk*.mvl %s/RPMS/install' % (cpall,builddir))
    #elif hostname == 'redhat80':
    #  os.system('%s /mvista/dev_area/licensing/host/redhat73/common-flexnet-sdk*.mvl %s/RPMS/install' % (cpall,builddir))
    #elif hostname == 'solaris8':
    #  os.system('%s /mvista/dev_area/licensing/host/solaris7/common-flexnet-sdk*.mvl %s/RPMS/install' % (cpall,builddir))
    #else:
    #  os.system('%s /mvista/dev_area/licensing/host/%s/common-flexnet-sdk*.mvl %s/RPMS/install' % (cpall,hostname,builddir))
  if foundation != "null" and foundation != "skip" and target != "host":
    if product not in ('ceeeclipse','feeclipse','proeclipse'):
      os.system('%s %s/%s/cross/common %s/RPMS/install/%s/cross' % (cpall,path,target,builddir,target))
      os.system('%s %s/%s/cross/%s %s/RPMS/install/%s/cross' % (cpall,path,target,hostname,builddir,target))
      targetrpms = ('binutils','filesystem',glibc,'kernel-headers','gcc','g++','libgcc1',
                   'libstdc++','nasm')
      for tr in targetrpms:
        os.system('%s %s/%s/target/*%s* %s/RPMS/install/%s/target' % (cpall,path,target,tr,builddir,target))
  elif foundation == "null" and target != "host":
    os.system('%s %s/%s/cross/common %s/RPMS/install/%s/cross' % (cpall,path,target,builddir,target))
    targetrpms = ('binutils','filesystem',glibc,'kernel-headers','gcc','g++','libgcc1','libstdc++','nasm')
    for tr in targetrpms:
      os.system('%s %s/%s/target/*%s* %s/RPMS/install/%s/target' % (cpall,path,target,tr,builddir,target))
else:
  #os.system('%s %s/SRPMS/host-rpm* %s/SRPMS' % (cpall,path,builddir))
  os.system('%s %s/host/common/*.mvl %s/RPMS/install/host/common' % (cpall,path,builddir))
  os.system('%s %s/host/%s/common-* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
  os.system('%s %s/host/%s/host-* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
  if product in ('pro','propk'):
    os.system('%s %s/host/%s/host-tftp-hpa* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
    os.system('%s %s/host/%s/host-mkimage* %s/RPMS/install/host/%s' % (cpall,path,hostname,builddir,hostname))
if product in ("propk",):
  os.system('%s %s/SRPMS/*previewkit* %s/SRPMS' % (cpall,path,builddir))
print 'Host Setup complete for %s' % (target)

