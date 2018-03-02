#!/usr/bin/python

import os, string, sys
hn = string.strip(os.popen('hostname -s').read())

if hn == 'node-7':
  archs = { 'hhl2.0-405':        ('ppc_405',),
            'hhl2.0-arm_x20t':   ('arm_720t_le','arm_920t_le'),
            'hhl2.0-mips_lexra': ('mips_lexra_fp_be',), }
elif hn == 'node-8':
  archs = { 'hhl2.0-mips':       ('mips_fp_be','mips_fp_le'),
            'hhl2.0-ppc':        ('ppc_74xx','ppc_7xx','ppc_82xx') }
elif hn == 'node-9':
  archs = { 'hhl2.0-ppc':        ('ppc_8xx','x86_586','x86_crusoe',
                                  'x86_pentium','x86_pentium2'), }
elif hn == 'node-10':
  archs = { 'hhl2.0-sh':         ('sh_sh3_be',) }
elif hn == 'node-11':
  archs = { 'hhl2.0-sh':         ('sh_sh4_le',),
            'hhl2.0-xscale':     ('arm_xscale_le',),
            'hhl2.0-sa':         ('arm_sa_le',) } 
bd = os.getcwd()
apps = ['busybox',]
for p in apps:
  for archdir in archs.keys():
    for a in archs[archdir]:
      print 'Building for ' + a + ' out of /mvista/release_area/' + archdir + '...'
      os.system('rm -rf /opt/hardhat/*; cp -a /var/lib/rpm /opt/hardhat/rpmdb')
      os.chdir('/mvista/release_area/'+ archdir + '/common')
      os.system('rpm -ivh *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/tools')
      os.system('rpm -ivh *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/tools/cluster')
      os.system('rpm -ivh *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/apps')
      os.system('rpm -ivh --ignorearch *filesystem* *kernel-headers* *binutils* *glibc* *ncurses* *gcc* *cpp* *g++* *libstdc++* *protoize* *flex* *openssl* *openssh*')
      os.chdir(bd + '/' + p)
      os.system('mkappnoclean `pwd` hhl2.0 ' + a + ' target-' + p + ' /opt/hardhat/rpmdb ~/.mvlrpmrc')
      if not os.path.exists('/mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS'):
        os.makedirs('/mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS')
      os.system('cp SRPMS/* /mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS')
      if not os.path.exists('/mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps'):
        os.makedirs('/mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps')
      os.system('cp RPMS/' + a + '/* /mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps')


