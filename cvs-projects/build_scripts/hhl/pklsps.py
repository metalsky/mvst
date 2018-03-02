#!/usr/bin/python
import os, string

kbv = '2.4.17'
khv = 'mvl21'

pklist = { 
          'x86_586':     [('generic_x86', 'generic_x86-pc_target'),],
          'mips_fp_be':  [('MIPS', 'mips-malta-mips_fp_be'),],
          'mips_fp_le':  [('MIPS', 'mips-malta-mips_fp_le',),],
          'ppc_8xx':     [('EmbeddedPlanet', 'embeddedplanet-linuxplanet'),],
          'ppc_7xx':     [('Motorola','motorola-sandpoint'),],
          'ppc_74xx':    [('Motorola','motorola-sandpoint'),],
          'ppc_82xx':    [('Motorola','motorola-sandpoint'),],
          'arm_sa_le':   [('ADS', 'ads-gcplus'),('Intrinsyc', 'intrinsyc-cerfboard')],
          'arm_720t_le': [('ARM', 'arm-integrator'),],
          'arm_920t_le': [('ARM', 'arm-integrator'),],
          'sh_sh4_le':   [('Hitachi', 'hitachi-ms7751se01-sh_sh4_le'),]
         }

# cluster build nodes
borg = ('node-1','node-2','node-3','node-4','node-5','node-6','node-7','node-8','7of9','8of9')
uname = string.strip(os.popen('hostname -s').read())
if uname in borg:
	penodes 	= string.split('node-1 node-2 node-3 node-4 node-5 node-6', ' ')
        cgenodes	= string.split('7of9 8of9', ' ')
        xnodes          = string.split('7of9', ' ')
        othernodes      = string.split('node-1', ' ')
else:
        nodes           = ()

