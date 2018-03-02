#!/usr/bin/python2

import sys, os, string, re
from manifestVerify import validateManifest
from updateLib import *

if len(sys.argv) == 1:
  print 'usage: %s %s %s %s %s' % (sys.argv[0],'<app>','<bug>','<product>','<build_id>')
  sys.exit(1)

app = sys.argv[1]
bug = sys.argv[2]
product = sys.argv[3]
id = sys.argv[4]
cd = os.getcwd()

apptype = 'foundation'

if product == 'all31':
  if apptype == 'foundation':
    cpfrom = '/mvista/dev_area/foundation/foundation_one-updates'
  prodDict = 	{
	'mvl3.1-arm':				[['arm_720t_le','arm_v4t_le'],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvl3.1-mips':				[['mips_fp_be','mips_fp_le','mips_nfp_le'],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvl3.1-ppc':				[['ppc_405','ppc_74xx','ppc_7xx','ppc_82xx','ppc_8xx','ppc_440',],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvl3.1-sh':				[['sh_sh3_be','sh_sh3_le','sh_sh4_be','sh_sh4_le'],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvl3.1-strngarm':			[['arm_sa_le','arm_xscale_be','arm_xscale_le'],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvl3.1-x86':				[['x86_486','x86_586','x86_crusoe','x86_pentium2','x86_pentium3','x86_pentium4'],
						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

#	'mvl3.1-xtensa':		        [['xtensa_linux_le','xtensa_linux_be'],
#						 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']],

	'mvlcge3.1-x86':			[['x86_pentium2','x86_pentium3','x86_pentium4'],
						 ['redhat73','redhat80','redhat90','solaris7']],

	'mvlcge3.1-ppc':			[['ppc_440','ppc_7xx','ppc_74xx','ppc_82xx',],
						 ['redhat73','redhat80','redhat90','solaris7']],

	'mvlcge3.1-strngarm':			[['arm_xscale_be',],
						 ['redhat73','redhat80','redhat90','solaris7']],

	'mvlcee3.1-ti-omap16xx_gsm_gprs':	[['arm_v4t_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-hitachi-ms7300cp01':		[['sh_sh3_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-ti-omap-730_gsm_gprs':	[['arm_v4t_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-intel-mainstone-pxa27x':	[['arm_iwmmxt_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-motorola-mx21ads':		[['arm_v4t_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-hitachi-ms73180cp01':	[['sh_sh3_le',],
						 ['redhat73','redhat90','windows2000']],

	'mvlcee3.1-ti-omap2420_gsm_gprs':	[['arm_v5t_le',],
						 ['redhat73','redhat90','windows2000']],

        'mvlcee3.1-samsung-24a0':		[['arm_v4t_le',],
						 ['redhat73','redhat90','windows2000']]
		}

elif product == 'mvl31special':
  cpfrom = '/mvista/dev_area/foundation/foundation_one-updates'
  prodDict =        {
        'mvl3.1-ppc':                           [['ppc_440ep','ppc_85xx'],
                                                 ['mandrake91','redhat73','redhat90','solaris7','suse90','windows2000']]
               }
elif product == 'mvl31-64':
  cpfrom = '/mvista/dev_area/foundation/foundation_one64-updates'
  prodDict =      {
        'mvl3.1-mips':                          [['mips64_fp_be'],
                                                 ['redhat73','redhat90','solaris7','suse90','windows2000']],
        'mvlcge3.1-em64t':                      [['x86_em64t'],
                                                 ['redhat73','redhat80','redhat90','solaris7']]
             }


elif product == 'all40':
  cpfrom = '/mvista/dev_area/foundation/foundation_two-updates'
  prodDict = {
         'mvl4.0.1-x86':           	[['x86_586',],
    			 		['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc400':        	[['ppc_440','ppc_440ep'],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc700':        	[['ppc_7xx',],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc7400':       	[['ppc_74xx',],
                                         ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-xscale':        	[['arm_xscale_be',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-armv5':         	[['arm_v5t_le',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-mipsfp':        	[['mips2_fp_be', 'mips2_fp_le',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-powerpc64':         	[['ppc_9xx',],
                                        ['redhat90','suse90','solaris8','windows2000']],

         'mvl4.0.1-mips64fp':		[['mips64_fp_be',],
					 ['redhat90','solaris8','suse90','windows2000']],

	 'mvl4.0.1-powerquiccii':	[['ppc_82xx',],
					 ['redhat90','solaris8','suse90','windows2000']],

	 'mvl4.0.1-powerquicciii':	[['ppc_85xx',],
					 ['redhat90','solaris8','suse90','windows2000']],
	 
         'mvlcge4.0.1-x86':        	[['x86_pentium3','x86_pentium4'],
					 ['redhat90','solaris8']],

         'mvlcge4.0.1-ppc700':           [['ppc_7xx',],
                                         ['redhat90','solaris8']],
         
         'mvlcge4.0.1-ppc7400':          [['ppc_74xx',],
                                         ['redhat90','solaris8']],

         'mvlcge4.0.1-ppc900':           [['ppc_9xx',],
                                         ['redhat90','solaris8']],

         'mvlcge4.0.1-em64t':           [['x86_em64t',],
                                         ['redhat90','solaris8']],

         'mobilinux4.0.2-arm_iwmmxt':    [['arm_iwmmxt_le',],
					 ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-armv6':         [['arm_v6_vfp_le',],
                                         ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-armv5':         [['arm_v5t_le',],
                                         ['redhat90','suse90','windows2000']],

         'mobilinux4.0.2-philips_armv5': [['arm_v5t_le',],
                                         ['redhat90','suse90','windows2000']]

}

else:
  print "Invalid product selection"
  sys.exit(1)

dirname = ''
dirnames = []
runtypes = []
updateDir = '%s/%s-%s-%s'%(cpfrom,app,bug,id)

apptype = string.split(app,'.')[0]

getJobList(updateDir, runtypes, apptype, prodDict)

####################


pakName = selectDirName(updateDir, apptype)


print ":::REVIEW:::"
print "pakName: %s"%(pakName)
print "Jobs: %s"%(runtypes)
raw_input("Press a key to continue")

#### Below being replaced by selectDirName

#os.chdir('%s/SRPMS' % (updateDir))
#i = 0
#for d in rpmname:
#  dirnames.append( string.replace(string.replace(string.strip(d),'hhl-'+apptype+'-',''),'.src.rpm','') )
#  print '%s. dirname = %s'%(i,dirnames[i])
#  i = i + 1
#print "%s. Cancel Upload"%(i)
#print "Runtype = %s"%(runtype)
#if runtype == 'crosscopy' and i == 1:
#  crossOnly = 1
#no more cross only using the new method for updates
#print "crossonly = %s"%(crossOnly)
#print runtypes
#choiceNum = getDirname()
#while( choiceNum > i ):
#  print "Invalid Entry"
#  choiceNum = getDirname()

#if (choiceNum == i):
#  print "Bye!"
#  sys.exit(1)
#else:
#  dirname = dirnames[choiceNum]

os.chdir(cd)

#We have dirname, we're gonna grab the version of it so we only copy files that have the same versioning as what we've chosen

version = getVersion(pakName)
print version
#sys.exit(1)

try:
  outputFile = open(id,"a")
except IOError:
  print "Can't open file for writing"
  sys.exit(1)

outputFile.write("\n\n")


keys = prodDict.keys()
keys.sort()
#if runtype == 'crosscopy' and os.path.exists('%s/%s/cross/common'%(updateDir,prodDict[keys[0]][0][0])):
#  runtype = 'crosscommon'
#  print "This is Cross Common"
#  raw_input("Hit Enter to Continue")

#choice = 0

#replaced by pickhost
if 'crosscopy' in runtypes or 'hostcopy' in runtypes:
  hosttype = pickHost()
else:
  hosttype = None

######################

for targetDir in keys:
  for runtype in runtypes:
    if runtype == 'copy':
      targetCopy(updateDir, pakName, targetDir, prodDict, version)
    elif runtype == 'crosscopy':
      crossCopy(updateDir, pakName, targetDir, prodDict, hosttype, version)
    elif runtype == 'hostcopy':
      hostCopy(updateDir, pakName, targetDir, prodDict, hosttype)

#  elif runtype =='crosscommon':
#    os.chdir('/mvista/arch/%s/updates' % (dir))
#    print 'making %s in %s/updates...' % (dirname,dir)
#    os.system('mkdir -p %s' % (dirname))
#    os.chdir(dirname)
#    os.system('mkdir -p SRPMS' )
#    os.system('cp -a %s/%s-%s-%s/SRPMS/*%s* SRPMS/' % (cpfrom,app,bug,id,version))
#    for subd in prodDict[dir][0]:
#      os.system('cp -a %s/%s-%s-%s/%s/cross/ ./%s/' % (cpfrom,app,bug,id,subd,subd))
#    updateManifest(dir, dirname)  
#    validateManifest()
#    outputFile.write("%s -> %s\n"%(dir,dirname))


#  elif runtype == 'host-toolcopy':
#    if 'solaris8' in prodDict[dir][1]: #this is a hack and should change
#      print 'making %s in %s/updates...' % (dirname,dir)
#      os.chdir('/mvista/arch/%s/updates' % (dir))
#      os.system('mkdir -p %s' % (dirname))
#      os.chdir(dirname)
#      os.system('cp -a %s/%s-%s-%s/SRPMS .' % (cpfrom,app,bug,id))
#      os.system('cp -a %s/%s-%s-%s/host-tools .' % (cpfrom,app,bug,id))
#      updateManifest(dir, dirname)  
#      validateManifest()
#      outputFile.write("%s -> %s\n"%(dir,dirname))

    else:
      print "Invalid operation"
      sys.exit(1)

for targetDir in keys:
  postProcess(targetDir, outputFile)


  os.chdir(cd)

