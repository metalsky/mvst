#!/usr/bin/python
import os, sys, string

# and is called once by installimage.py during the target cd creation.
# It does the following:
# 1) installs cross-isolinux
# 2) runs mk_isolinux_cfg, which makes the isolinux.cfg file, and copies
#    that and isolinux.bin to the install cd directory tree.

# Arguments:
# 1- path to mvls (like /mvista/dev_area/foundation/fb030618)
# 2- self hosted target architecture
# 3- kernel base version_kernel mvl version
# 4- mvldist
# 5- shidir (where the self-hosted-installer and generic-mvl_install lsp are installed)
# 6- version
# 7- buildid
# 8- x86 lsp name

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s %s %s %s %s' % (sys.argv[0],'<cpdir>', '<installtarget>',
                                  '<kernel version (2.4.18_mvl30)>','<mvldist>',
				  '<shidir>','<version>','<buildid>','<x86lsp>')
  sys.exit(1)

cpdir = sys.argv[1]
installtarget = sys.argv[2]
kernelversion = sys.argv[3]
mvldist = sys.argv[4]
shidir = sys.argv[5]
version = sys.argv[6]
buildid = sys.argv[7]
x86lsp = sys.argv[8]

builddir = os.getcwd()
targ = string.split(installtarget,'_')
isolinux_tmpdir='/tmp/isolinux-' + buildid
crossroot = isolinux_tmpdir + '/devkit/' + targ[0] + '/' + targ[1]
print 'crossroot = ' + crossroot
sys.__stdout__.flush()

# use host-rpm to install cross-isolinux
os.chdir(cpdir + '/' + installtarget + '/cross/common')
os.system('cp -a /var/lib/rpm /tmp/rpmdbfoo')
os.system('rpm --dbpath /tmp/rpmdbfoo --prefix ' + isolinux_tmpdir + ' -ivh *isolinux* --nodeps')
os.system('rm -rf /tmp/rpmdbfoo')

# run mk_isolinux_cfg
os.chdir(builddir)
os.system('./mk_isolinux_cfg ' + 
          ' --kernelversion ' + kernelversion +
	  ' --installroot ' + shidir + 
	  ' --crossroot ' + crossroot +
	  ' --edition ' + mvldist + 
          ' --version ' + version +
	  ' ' + x86lsp)

# clean up after ourselves.  retarded.
os.system('rm -rf ' + isolinux_tmpdir)

