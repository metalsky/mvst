#!/usr/bin/python

import os, string, sys
hn = string.strip(os.popen('hostname -s').read())

if hn == 'node-7':
  archs = { 'hhl2.0-arm_x20t':   ('arm_720t_le','arm_920t_le'), 
            'hhl2.0-mips':       ('mips_fp_be','mips_fp_le'),}
elif hn == 'node-8':
  archs = { 'hhl2.0-ppc':        ('ppc_74xx','ppc_7xx','ppc_82xx'), }
elif hn == 'node-9':
  archs = { 'hhl2.0-ppc':        ('ppc_8xx','x86_586','x86_crusoe'),
          }
elif hn == 'node-10':
  archs = { 'hhl2.0-ppc':        ('x86_pentium2','x86_pentium3',),
           'hhl2.0-sh':         ('sh_sh3_be',) }
elif hn == 'node-11':
  archs = { 'hhl2.0-sh':         ('sh_sh4_le',),
            'hhl2.0-xscale':     ('arm_xscale_le',),
            'hhl2.0-sa':         ('arm_sa_le',) } 
elif hn == 'node-12':
  archs = { 'hhl2.0-405':        ('ppc_405',),
            'hhl2.0-mips_lexra': ('mips_lexra_fp_be',), 
          }
elif hn == 'node-18':
  archs = { 'hhl2.0-sh':         ('sh_sh3_le','sh_sh4_be'),
            'hhl2.0-ppc':        ('x86_pentium',),
          }

bd = os.getcwd()
apps = ['linux-ftpd',]

for p in apps:
  os.system('mkdir -p /mvista/dev_area/logs/hhl2.0-updates/' + p)
  for archdir in archs.keys():
    for a in archs[archdir]:
      print 'Building for ' + a + ' out of /mvista/release_area/' + archdir + '...'
      os.system('rm -rf /opt/hardhat/*; cp -a /var/lib/rpm /opt/hardhat/rpmdb')
      os.chdir('/mvista/release_area/'+ archdir + '/common')
      os.system('rpm -i *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/tools')
      os.system('rpm -i *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/tools/cluster')
      os.system('rpm -i *.rpm')
      os.chdir('/mvista/release_area/'+ archdir + '/' + a + '/apps')
      os.system('rpm -i --ignorearch *filesystem* *kernel-headers* *binutils* *glibc* *ncurses* *gcc* *cpp* *g++* *libstdc++* *protoize* *flex* *openssl* *libtool* *libwrap* *zlib* *libpam*')
      if string.find(a,'sh_sh3_be') > -1:
        os.chdir('/opt/hardhat/config/rpm/targets')
        os.system('mv sh_sh3_be-linux xxx')
        os.system("sed -e '/hardhat-linux/s/sh3eb/sh/' < xxx > sh_sh3_be-linux")
        os.system('rm -f xxx')
      if string.find(a,'sh_sh4_be') > -1:
        os.chdir('/opt/hardhat/config/rpm/targets')
        os.system('mv sh_sh4_be-linux yyy')
        os.system("sed -e '/hardhat-linux/s/sh4eb/sh/' < yyy > sh_sh4_be-linux")
        os.system('rm -f yyy')
      if string.find(a,'sh_sh3_le') > -1:
        os.chdir('/opt/hardhat/config/rpm/targets')
        os.system('mv sh_sh3_le-linux zzz')
        os.system("sed -e '/hardhat-linux/s/sh3el/sh/' < zzz > sh_sh3_le-linux")
        os.system('rm -f zzz')
      if string.find(a,'sh_sh4_le') > -1:
        os.chdir('/opt/hardhat/config/rpm/targets')
        os.system('mv sh_sh4_le-linux www')
        os.system("sed -e '/hardhat-linux/s/sh4el/sh/' < www > sh_sh4_le-linux")
        os.system('rm -f www') 
      os.chdir(bd + '/' + p)
      os.system('~/bin/mkappnoclean `pwd` hhl2.0 ' + a + ' target-' + p + ' /opt/hardhat/rpmdb ~/.mvlrpmrc > /mvista/dev_area/logs/hhl2.0-updates/' + p + '/' + a + '.log 2>&1')
      if not os.path.exists('/mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS'):
        os.makedirs('/mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS')
      os.system('cp SRPMS/* /mvista/dev_area/hhl2.0-updates/' + p + '/SRPMS')
      if not os.path.exists('/mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps'):
        os.makedirs('/mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps')
      os.system('cp RPMS/' + a + '/* /mvista/dev_area/hhl2.0-updates/' + p + '/' + a + '/apps')


