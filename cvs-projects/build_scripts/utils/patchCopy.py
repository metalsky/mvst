#!/usr/bin/python

import os, sys, re, shutil, patchchecker

CVS = 0
GIT = 1

GITSERVER = "git.sh.mvista.com"
GITPATH = "/var/cache/git/kernel"

class product:
  def __init__(self, name, patchLocation, devLocation, version):
    self.name = name
    self.patchLocation = patchLocation
    self.devLocation = devLocation
    self.version = version
    return

products = {
	  'bartholome':product('mvlcge30' ,'/home/build/kernel-patches/CVSREPOS/bartholome_patches','/mvista/dev_area/cge/mvlcge310-updates/patches',CVS),
          'blackfoot': product('mvl500' ,'/home/build/kernel-patches/CVSREPOS/blackfoot_patches', '/mvista/dev_area/pro/mvl500-updates/patches', CVS),
          'campbell':  product('mvlcge21' ,'/home/build/kernel-patches/CVSREPOS/campbell_patches','/mvista/dev_area/cge/mvlcge2.1.0-updates/patches',CVS),
          'carbonriver':product('mobilinux410', '/home/build/kernel-patches/CVSREPOS/carbonriver_patches','/mvista/dev_area/mobilinux/mobilinux410-updates/patches',CVS),
          'druid_peak':product('mvlcge31' ,'/home/build/kernel-patches/CVSREPOS/druid_peak_patches','/mvista/dev_area/cge/mvlcge310-updates/patches', CVS),
          'humboldt':  product('mvl31'    ,'/home/build/kernel-patches/CVSREPOS/humboldt_patches','/mvista/dev_area/pro/mvl310-updates/patches', CVS),
          'kapalua':   product('mvlcee31' ,'/home/build/kernel-patches/CVSREPOS/kapalua_patches','/mvista/dev_area/cee/mvlcee310-updates/patches', CVS),
          'patagonia': product('mvl401'   ,'/home/build/kernel-patches/CVSREPOS/patagonia_patches','/mvista/dev_area/pro/mvl401-updates/patches',CVS),
          'lamar':     product('mvlcge401','/home/build/kernel-patches/CVSREPOS/lamar_patches','/mvista/dev_area/cge/mvlcge401-updates/patches', CVS),
          'pebblecreek':     product('mvlcge500','/home/build/kernel-patches/CVSREPOS/pebblecreek_patches','/mvista/dev_area/cge/mvlcge500-updates/patches', CVS),
          'tahoma':   product('moblinix500' ,'/home/build/kernel-patches/CVSREPOS/tahoma_patches','/mvista/dev_area/mobilinux/mobilinux500-updates/patches', CVS),
         # 'sherman':   product('mvl30'  ,'/home/build/kernel-patches/CVSREPOS/sherman_patches','-------',0),
          'makena':    product('mobilinux402', '/home/build/kernel-patches/CVSREPOS/makena_patches','/mvista/dev_area/mobilinux/mobilinux402-updates/patches', CVS),
          'avalanche': product('f2.6.24','/home/build/kernel-patches/GITREPOS/avalanche_patches','/mvista/dev_area/mobilinux/mobilinux5024-updates/patches',GIT),
          'atom': product('f2.6.24-s124atom','/home/build/kernel-patches/GITREPOS/atom_patches','/mvista/dev_area/mvl/atom-updates/patches',GIT),
          'omap': product('f2.6.24-s124omap3','/home/build/kernel-patches/GITREPOS/omap_patches','/mvista/dev_area/mvl/omap-updates/patches',GIT),
          'jackalope': product('pro_5024','/home/build/kernel-patches/GITREPOS/jackalope_patches','/mvista/dev_area/pro/mvl5024-updates/patches',GIT),
          'gittest': product('pro5-release-test','/home/build/kernel-patches/GITREPOS/gittest_patches','/mvista/dev_area/testdir/',GIT)
          }


def updateCVS(patchPath):
  #Run CVS Update in the proper patch path.
  try:
    #print "Run cvs update at %s" % patchPath
    os.chdir(patchPath)
    os.system('cvs update')
  except KeyError:
    print "%s is not a valid distribution" % dist
    sys.exit(1)


def updateGIT(patchPath,repo):
  os.chdir(patchPath)
  os.system("rm -rf %s"%(repo))
  os.system("git-clone %s:%s/%s"%(GITSERVER,GITPATH,repo))
  os.chdir(os.path.join("%s/%s")%(patchPath,repo))
  os.system("git-checkout origin/release")
    


def updateErrata():
  print "Generating new README.errata"
  os.system("for a in $(ls *.mvlpatch);do echo $a; head -n 150 $a >fileout_$a;awk '/^# /' fileout_$a; done >README")
  os.system("rm -f fileout_*")
  os.system("grep -v Signed README > README.errata")
  os.system("rm -f README")
  return


def doWork(argv):
  if len(argv) != 4:
    print "Usage: patchCopy distribution [start-end bug#] [start-end bug#]... (eg. patchCopy lamar 1200-1264 38 1400-1440 42)"
    print 'where distribution in:'
    for dist in products.keys():
      print dist
    sys.exit(1)


  print
  #Collect arguments.
  dist = argv[1]
  flagRange = argv[2]
  bugnum = argv[3]
  flagRange = (flagRange.split('-'))
  newrange = []
  filesToChange = []

  #Format range properly
  for nums in flagRange:
    try:
      newrange.append(int(nums))
    except ValueError:
      print "Invalid range specified."
      sys.exit(1)
      
  flagRange = newrange

  #Make sure range contains 2 arguments.
  if len(flagRange) != 2:
    print "Invalid range specified."
    sys.exit(1)


  patchPath = products[dist].patchLocation
  if products[dist].version == GIT:
    updateGIT(patchPath,products[dist].name)
    patchPath = "%s/%s/MONTAVISTA-BUILD/mvl_patches"%(patchPath,products[dist].name)
    os.chdir(patchPath)
  else:
    updateCVS(patchPath)

  #Build the list of files to tag.
  for files in os.listdir(patchPath):
    if files.split('-')[0]== 'linux':
      patchArg = 2
    else:
      patchArg = 1	
    try:
      if flagRange[0] <= int(files.split('-')[patchArg]) <= flagRange[1]:
        filesToChange.append(files)
    except IndexError: pass
    except ValueError: print "Oops! Need to figure out what to do with this other filename syntax!"; sys.exit(1)
  filesToChange.sort()

  
  for files in filesToChange:
    #print "cvs tag %s-kp-%s %s" % (products[dist].name, bugnum, files)
    #print "cp %s to %s" % (files, products[dist].devLocation)
    if products[dist].version == CVS: #GIT patches are already tagged
      os.system("cvs tag %s-kp-%s %s" % (products[dist].name, bugnum, files))
    shutil.copy(files,products[dist].devLocation)
    
 
    


def main(argv):
  if len(argv) == 1:
	doWork([])

  buildID = argv[1]

  for i in range(2,len(sys.argv))[::2]:
    bugRange = argv[i]
    bugNum = argv[i+1]
    doWork([argv[0], buildID, bugRange, bugNum])

  os.chdir(products[buildID].devLocation)


  #Check to make sure all patches are here.  If not, abort.
  if not patchchecker.checkPatches(products[buildID].devLocation, debug=1):
    print "Patches Missing -- Halting."
    sys.exit(1)
  else:
    print;print "All patches present and accounted for -- Proceeding.";print

  
  updateErrata()
    
  os.system("tar -cf all_current_patches.tar *.mvlpatch")
  os.system("gzip all_current_patches.tar -f")

  fileLines = ["The following information is the MD5 checksums of each file\n" , \
               "contained in this directory.  This information is used to\n" , \
               "verify that the files downloaded from this directory were not\n" , \
               "corrupted during the transfer.\n\n" , \
               "            md5sum                          file\n" , \
               "--------------------------------  ---------------------------\n"]

  readmeFile = open('README.md5sum', 'w')
  readmeFile.writelines(fileLines)
  readmeFile.close()
  os.system("md5sum all_current_patches.tar.gz >> README.md5sum")


  
if __name__ == "__main__":
  main(sys.argv)
