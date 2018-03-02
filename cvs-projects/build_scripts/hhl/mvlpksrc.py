#!/usr/bin/python
import os, string, sys

# For mvlpk-base src, do the following once:
# 1- install rpmconfig & platformtest
# 2- install required src.mvls
# 3- rpm -bp for required src.mvls
# 4- install mvlpk-base src.mvl
# 5- rpm -bp mvlpk-base
# 6- tar up BUILD directory
# 
# For the cross src, do the following per architecture
# 1- install rpmconfig & platformtest
# 2- install required src.mvls
# 3- rpm -bp for required src.mvls
# 4- install mvlpk-dev src.mvl
# 5- rpm -bp mvlpk-dev
# 6- tar up BUILD directory

# arguments
# 1- path to required mvls & rpmconfig & platformtest
# 2- architecture
# 3- base|nobase

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s %s %s %s %s' % (sys.argv[0], '<path to rpmconfig mvl>', 
                                   '<path to userland>', 'base|nobase|base-only','<path to pk src mvls>',
                                   '<release number>','<kbv>','<khv>','<path to toolchain>')
  sys.exit(1)

rpmdir = sys.argv[1]
userdir = sys.argv[2]
base = sys.argv[3]
srcrpmdir = sys.argv[4]
release = sys.argv[5]
cvsrelease = string.strip(os.popen('echo ' + release + ' | sed -e "s:\\.::g"').read())
print 'cvs release = ' + cvsrelease
kbv = sys.argv[6]
khv = sys.argv[7]
tooldir = sys.argv[8]
builddir = os.getcwd()
# glibc & gdb are in basereqs, but in tooldir, not user dir
basereqs = ('thttpd','netkit-base',)
devreqs = ('binutils','gcc','gdb')
# set default arch for use in base tar file
arch = 'arm_720t_le'
#arch = 'mips_sb1_fp_be'

def rpmbp(rpm,arch,topdir):
  if rpm != 'gcc' and rpm != 'kernel-headers' and rpm != 'binutils':
    os.system('rpm -bp --dbpath /opt/montavista/rpmdb --rcfile ~/.perpmrc ' +
              '--define "_builddir /var/tmp/BUILD" ' +
              '--define "_topdir ' + topdir + '" ' +
              '--target=' + arch + '-hardhat-linux *' + rpm + '*')
  elif rpm == 'gcc' or rpm == 'binutils':
    os.system('rpm -bp --dbpath /opt/montavista/rpmdb --rcfile ~/.perpmrc ' +
              '--define "_builddir /var/tmp/BUILD" ' +
              '--define "_topdir ' + topdir + '" ' +
              ' --target=' + arch +
              '-hardhat-linux *cross-' + rpm + '-' + arch + '.spec')
  elif rpm == 'kernel-headers':
    os.system('rpm -bp --dbpath /opt/montavista/rpmdb --rcfile ~/.perpmrc ' +
              '--define "_builddir /var/tmp/BUILD" ' +
              '--define "_topdir ' + topdir + '" ' +
              '--define "_hhl_kernel_base_version ' + kbv + '" ' +
              '--define "_hhl_kernel_hhl_version ' + khv + '" ' +
              '--target=' + arch + '-hardhat-linux *' + rpm + '*')
             
def rpmivh(rpm):
  os.system('rpm -ivh --dbpath /opt/montavista/rpmdb --define "_topdir ' +
            builddir + '" ' + rpm)

# setup
def setup():
  os.system('rm -rf /opt/montavista/*')
  os.system('cp -a /var/lib/rpm /opt/montavista/rpmdb')
  os.system('rm -rf /var/tmp/BUILD/*')
  os.system('rm -rf ' + builddir + '/SOURCES/*')
  os.system('rm -rf ' + builddir + '/SPECS/*')
  os.chdir(rpmdir + '/host/common/optional')
  rpmivh('*rpmconfig* *platformtest*')
  os.chdir(rpmdir + '/' + arch + '/target')
  rpmivh('*kernel-headers*')
  rpmivh('*binutils* --ignorearch')
  os.chdir(rpmdir + '/' + arch + '/cross/common')
  rpmivh('*libopt*')

# checkout userland modules
os.chdir(userdir)
for br in basereqs:
  os.system('rm -rf ' + br)
  os.system('cvs co -r ' + cvsrelease + ' ' + br)
os.chdir(tooldir)
for dr in devreqs:
  os.system('rm -rf ' + dr)
  os.system('cvs co -r ' + cvsrelease + ' ' + dr)
  if dr == 'binutils' or dr == 'gcc':
    os.chdir(dr + '/SPECS')
    os.system('make')
    os.chdir(tooldir)
os.system('cvs co -r ' + cvsrelease + ' glibc')
  
setup()
if base == 'base' or base == 'base-only':
  # glibc
  print 'Prepping glibc...'
  os.chdir(tooldir + '/glibc/SPECS')
  rpmbp('glibc',arch,tooldir + '/glibc')
  for r in basereqs:
    print 'Prepping ' + r + '...'
    os.chdir(userdir + '/' + r + '/SPECS')
    rpmbp(r,arch,userdir + '/' + r)
  # gdb
  print 'Prepping gdb...'
  os.chdir(tooldir + '/gdb/SPECS')
  rpmbp('gdb',arch,tooldir + '/gdb')
  #os.chdir(rpmdir + '/SRPMS-delete')
  os.chdir(srcrpmdir + '/build_stuff/SRPMS')
  os.system('rpm -ivh --dbpath /opt/montavista/rpmdb --define "_topdir ' + builddir +
            #'" *mvlpk-base*')
            '" *previewkit-base*')
  os.chdir(builddir + '/SPECS')
  rpmbp('mvlpk-base',arch,builddir)
  os.chdir(builddir)
  os.system('tar -C /var/tmp -cipzf previewkit-base-2.1-' + release + '-src.tar.gz BUILD')

if base != 'base-only':
  setup()
  #archs = ("arm_720t_le", "arm_920t_le", "arm_sa_le", "mips_fp_be", "mips_fp_le", "ppc_74xx", "ppc_7xx", "ppc_82xx", "ppc_8xx", "sh_sh4_le", "x86_586")

  archs = ("arm_720t_le", "arm_920t_le", "arm_sa_le", "arm_sa_be", "arm_xscale_le", "arm_xscale_be", "mips_fp_be", "mips_fp_le", "ppc_405", "ppc_74xx", "ppc_7xx", "ppc_82xx", "ppc_8xx", "sh_sh3_be", "sh_sh3_le", "sh_sh4_be", "sh_sh4_le", "x86_486", "x86_586", "x86_crusoe", "x86_pentium2", "x86_pentium3")

  #archs=("mips_sb1_fp_be",)

  for arch in archs:
    if release == 'mvl2.1.0':
      if arch == "arm_xscale_be":
        rpmdir = '/mvista/dev_area/mvl2.1.0_brh'
      elif arch == "mips_sb1_fp_be":
        rpmdir = '/mvista/dev_area/mvl2.1.0a'
      elif arch == "mips_sony_fp_be":
        rpmdir = '/mvista/dev_area/mvl2.1.0_sony_be'
    else:
      rpmdir = sys.argv[1]
    os.chdir(rpmdir + '/' + arch + '/cross/cluster')
    rpmivh('*binutils*')
    os.chdir(rpmdir + '/host/common/optional')
    rpmivh('*kernel*')
    for r in devreqs:
      os.chdir(tooldir + '/' + r + '/SPECS')
      rpmbp(r,arch,tooldir + '/' + r)
    os.chdir(rpmdir + '/SRPMS-delete')
    os.system('rpm -ivh --dbpath /opt/montavista/rpmdb --define "_topdir ' + builddir +
              #'" *mvlpk-dev*')
              '" *previewkit-dev*')
    os.chdir(builddir + '/SPECS')
    rpmbp('mvlpk-dev',arch,builddir)
  os.chdir(builddir)
  os.system('tar -C /var/tmp -cipzf previewkit-dev-2.1-' + release + '-src.tar.gz BUILD')

# copy tar files
os.system('cp previewkit-base-2.1-' + release + '-src.tar.gz ' + srcrpmdir + '/Sources')
os.system('cp previewkit-dev-2.1-' + release + '-src.tar.gz ' + srcrpmdir + '/Sources')

