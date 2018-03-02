#!/usr/bin/python
import os, sys, string

# this script runs via ssh on bfnode (which has a floppy disk in the floppy drive)
# and is called once by installimage.py during the target cd creation.
# It does the following:
# 1) installs cross-lilo  
# 2) runs mkfloppy from userland/hhl-install/SOURCES
# 3) copies the bootflopy image to the build area

# Arguments:
# 1- path to mvls (like /mvista/dev_area/foundation/fb030618)
# 2- self hosted target architecture
# 3- kernel base version_kernel hhl version
# 4- hhldist
# 5- rpmbin
# 6- shidir (where the self-hosted-installer and generic-hhl_install lsp are installed)
# 7- version

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s %s %s %s' % (sys.argv[0],'<cpdir>', '<installtarget>',
                                  '<kernel version (2.4.18_mvl30)>','<hhldist>',
				  '<rpmbin>','<shidir>','<version>')
  sys.exit(1)

cpdir = sys.argv[1]
installtarget = sys.argv[2]
kernelversion = sys.argv[3]
hhldist = sys.argv[4]
rpmbin = sys.argv[5]
shidir = sys.argv[6]
version = sys.argv[7]

builddir = os.getcwd()
targ = string.split(installtarget,'_')
crossroot = '/opt/montavista/devkit/' + targ[0] + '/' + targ[1]
print 'crossroot = ' + crossroot

# use host-rpm to install cross-lilo
os.chdir(cpdir + '/' + installtarget + '/cross/cluster')
os.system(rpmbin + ' -ivh *lilo* --nodeps')

# create directory for bootflop.img
os.system('mkdir -p ' + shidir + '/' + installtarget + '/bootimg')

# run mkfloppy
os.chdir(builddir)
os.system('sudo ./mkfloppy -v -z -o ' + shidir + '/' + installtarget + '/bootimg/bootflop.img ' +
          '--kernelversion ' + kernelversion + ' --installroot ' +
          shidir + '/' + installtarget + ' --crossroot ' + crossroot + ' --edition ' + hhldist +
          ' --version ' + version)

