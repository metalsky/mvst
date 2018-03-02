#!/usr/bin/python
import os, sys, string

def genTechPreviewDirectory(buildtag):
  hosts = ('centos3','suse90','windows2000')
  tpbuildtag = 'fthreetp' + string.split(buildtag,'fthree')[1]
  sourcePath = '/mvista/dev_area/foundation/%s/build' % buildtag
  tpPath = '/mvista/dev_area/foundation/%s/build' % tpbuildtag
  print 'Generating an x86_586 build directory based on a subset of %s' % sourcePath
  if not os.path.exists(tpPath):
    os.system('mkdir -p %s' % tpPath)
  else:
    print 'Cleaning existing path: %s' % tpPath
    os.system('rm -rf %s/*' % tpPath)
  # link SRPMS
  print 'linking SRPMS ...'
  os.system('mkdir -p %s/SRPMS' % tpPath)
  os.system('ssh dumbo "cd %s/SRPMS; ln %s/SRPMS/* ."' % (tpPath,sourcePath))
  # link etc
  print 'linking etc/ ...'
  os.system('mkdir -p %s/etc/config/volume' % tpPath)
  os.system('ssh dumbo "cd %s/etc/config/volume; ln %s/etc/config/volume/*host* ."' % (tpPath,
             sourcePath))
  os.system('ssh dumbo "cd %s/etc/config/volume; ln %s/etc/config/volume/*x86_586-* ."' % (tpPath,
             sourcePath))
  # link host
  print 'linking host/ ...'
  os.system('mkdir -p %s/host/common/optional' % tpPath)
  os.system('ssh dumbo "cd %s/host/common; ln %s/host/common/*.mvl ."' % (tpPath,
             sourcePath))
  os.system('ssh dumbo "cd %s/host/common/optional; ln %s/host/common/optional/* ."' % (tpPath,
             sourcePath))
  for host in hosts:
    print 'linking host/%s ...' % host
    os.system('mkdir -p %s/host/%s' % (tpPath,host))
    os.system('ssh dumbo "cd %s/host/%s; ln %s/host/%s/*.mvl ."' % (tpPath,host,sourcePath,host))
  # link install
  print 'linking install ...'
  os.system('ssh dumbo "cd %s; ln %s/install ."' % (tpPath,sourcePath))
  # link install-components
  print 'linking install-components/ ...'
  os.system('mkdir -p %s/install-components/host' % tpPath)
  os.system('cp -a %s/install-components/cross-control/ %s/install-components/' % (sourcePath,tpPath))
  os.system('cp -a %s/install-components/host/common %s/install-components/host' % (sourcePath,tpPath))
  for host in hosts:
    os.system('cp -a %s/install-components/host/%s %s/install-components/host' % (sourcePath,host,
               tpPath))
  os.system('cp -a %s/install-components/webpages %s/install-components' % (sourcePath,tpPath))
  # link x86_586
  print 'linking x86_586/cross ...'
  os.system('mkdir -p %s/x86_586/cross/common' % tpPath)
  os.system('ssh dumbo "cd %s/x86_586/cross/common; ln %s/x86_586/cross/common/*.mvl ."' % (tpPath,
             sourcePath))
  for host in hosts:
    os.system('mkdir -p %s/x86_586/cross/%s' % (tpPath,host))
    os.system('ssh dumbo "cd %s/x86_586/cross/%s; ln %s/x86_586/cross/%s/*.mvl ."' % (tpPath,host,
               sourcePath,host))
  print 'linking x86_586/target ...'
  os.system('mkdir -p %s/x86_586/target' % tpPath)
  f_apps = open('./techpreviewapps','r')
  l_apps = f_apps.readlines()
  f_apps.close()
  for app in l_apps:
    app = string.strip(app)
    print 'linking x86_586/target/%s*.mvl ...' % app
    os.system('ssh dumbo "cd %s/x86_586/target; ln %s/x86_586/target/%s*.mvl ."' % (tpPath,
               sourcePath,app))
  print 'linking x86_586/lsps ...'
  os.system('mkdir -p %s/x86_586/lsps' % tpPath)
  os.system('cp -a %s/x86_586/lsps/x86-pc_target-x86_586 %s/x86_586/lsps' % (sourcePath,tpPath))

def main():
  if len(sys.argv) != 2:
    print 'usage: %s <buildtag>' % sys.argv[0]
    sys.exit(1)
  elif string.find(sys.argv[1],'fthree') == -1:
    print '<buildtag> must be an fthree <buildtag>'
    sys.exit(1)
  else:
    genTechPreviewDirectory(sys.argv[1])

if __name__ == "__main__":
  main()
