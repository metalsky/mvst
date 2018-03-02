#!/usr/bin/python
import os, sys, re, string, time

# this script takes rpms out of a foundation build and puts them in the
# appropriate updates directories

# args:
# 1- build tag
# 2- app name
# 3- bug
# 4- applist , separated (in case multiple different named rpms need to be copied, like the app name is
#    gcc, but you need to copy gcc, cpp, g++, libstdc++)
# 5- product (to determine archs/hosts to copy)
# 6- type (host/target/cross)
# 7- arch (optional to upload a single arch)

valid_products = {
'foundation_two':
  [ string.split("arm_iwmmxt_le arm_v4t_le arm_v5t_le arm_v6_vfp_be arm_v6_vfp_le arm_xscale_be arm_xscale_le mips2_fp_be mips2_fp_le mips2_nfp_be mips2_nfp_le mips64_fp_be mips64_fp_le mips_vr4133_le mips_vr4133_be ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx ppc_9xx sh_sh3_le sh_sh4_le x86_586 x86_amd64 x86_em64t x86_pentium3 x86_pentium4 arm_v6_vfp_le_uclibc arm_iwmmxt_le_uclibc arm_v5t_le_uclibc mips64_octeon_be ppc_83xx_nfp xtensa_linux_be xtensa_linux_le arm_iwmmxt2_le arm_iwmmxt2_le_uclibc mips64_octeon_v2_be", " "),
   string.split("redhat90 solaris8 suse90 windows2000"," "),
   '/mvista/dev_area/foundation/foundation_two-updates' ],
'foundation_two_cge400':
  [ string.split("x86_pentium3 x86_pentium4", " "),
   string.split("redhat90 solaris8"," "),
   '/mvista/dev_area/foundation/foundation_two-updates' ],
'cge401':
  [ string.split("x86_pentium3 x86_pentium4 ppc_74xx ppc_7xx ppc_9xx x86_em64t ppc_85xx ppc_440 x86_amd64", " "),
   string.split("redhat90 solaris8"," "),
   '/mvista/dev_area/cge/mvlcge401-updates' ],
'mbl410':
  [ string.split("arm_iwmmxt_le arm_iwmmxt_le_uclibc arm_v6_vfp_le arm_v6_vfp_le_uclibc", " "),
   string.split("redhat90 windows2000 suse90"," "),
   '/mvista/dev_area/mobilinux/mobilinux410-updates' ],
'foundation_one':
  [ string.split("arm_720t_be arm_720t_le arm_iwmmxt_le arm_sa_le arm_v4t_be arm_v4t_le arm_v5t_le arm_xscale_be arm_xscale_le mips_fp_be mips_fp_le mips_nfp_le ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx sh_sh3_be sh_sh3_le sh_sh4_be sh_sh4_le x86_486 x86_586 x86_crusoe x86_pentium x86_pentium2 x86_pentium3 x86_pentium4", " "),
   string.split("mandrake91 redhat73 redhat80 redhat90 solaris7 suse90 windows2000"," "),
   '/mvista/dev_area/foundation/foundation_one-updates' ],
'foundation_one64':
  [ string.split("mips64_fp_be x86_amd64 x86_em64t", " "),
   string.split("mandrake91 redhat73 redhat80 redhat90 solaris7 suse90 windows2000"," "),
   '/mvista/dev_area/foundation/foundation_one64-updates' ],
'foundation-cee':
  [ string.split("arm_iwmmxt_le arm_v4t_le arm_v5t_le sh_sh3_le x86_586 ", " "),
    string.split("redhat73 redhat90 windows2000"," "),
    '/mvista/dev_area/foundation/foundation_one-updates' ],
'foundation-cge':
  [ string.split("", " "),
    string.split(""," "),
    '/mvista/dev_area/foundation/foundation_one-updates' ],
'pro':
  [ string.split("arm_720t_le arm_sa_le arm_v4t_le arm_xscale_be arm_xscale_le mips_fp_be mips_fp_le mips_nfp_le ppc_405 ppc_440 ppc_74xx ppc_7xx ppc_82xx ppc_8xx sh_sh3_be sh_sh3_le sh_sh4_be sh_sh4_le x86_486 x86_586 x86_crusoe x86_pentium2 x86_pentium3 x86_pentium4 xtensa_linux_be xtensa_linux_le", " "),
     string.split("mandrake91 redhat73 redhat90 solaris7 suse90 windows2000"," "),
     '/mvista/dev_area/pro/mvl310-updates' ],
'pro401':
  [ string.split("arm_v4t_le arm_v5t_le arm_xscale_be arm_xscale_le mips2_fp_be mips2_fp_le mips2_nfp_le mips64_fp_be mips64_octeon_be ppc_405 ppc_440 ppc_440ep ppc_74xx ppc_7xx ppc_82xx ppc_85xx ppc_8xx ppc_9xx ppc_9xx x86_586 mips_vr4133_be mips_vr4133_le xtensa_linux_le sh_sh4_le ppc_83xx_nfp x86_pentium3", " "),
     string.split("redhat90 solaris8 suse90 windows2000"," "),
     '/mvista/dev_area/pro/mvl401-updates' ],
'cee':
  [ "arm_v4t_le",
     string.split("redhat73 redhat90 windows2000"," "),
     '/mvista/dev_area/cee/mvlcee310-updates' ],
'mobilinux':
  [ string.split("arm_iwmmxt_le arm_v6_vfp_le arm_v5t_le", " "), string.split("redhat90 suse90 windows2000"," "), '/mvista/dev_area/mobilinux/mobilinux400-updates' ],

'foundation_em64t':
  [ string.split("x86_em64t", " "),
   string.split("redhat90 redhat73 redhat80 "," "),
   '/mvista/dev_area/foundation/foundation_em64t-updates' ],
}
if len(sys.argv) == 1:
  print "\nUsage: %s %s %s %s %s %s %s %s" % (sys.argv[0],'<buildtag>','<app name>',
         '<bug number>','<app list>','<product>','<app type>','[arch]')
  print "valid types are:  target, target-opt, host, common, common-host, cross-common, cross-host, host-tools"
  print "valid products are: "
  vps = valid_products.keys()
  vps.sort()
  for vp in vps:
    print vp
  print "[arch] is optional and if an arch is specified, only that arch will be moved"
  print "\nOr\nUsage: %s products" % sys.argv[0]
  print "\nwhich will list the valid products\n"
  print "\nNumber of args = " + str(len(sys.argv))
  print "\nHere are the args:\n"
  for a in sys.argv:
    print a
  print "\nUsage: %s %s %s %s %s %s %s %s" % (sys.argv[0],'<buildtag>','<app name>',
         '<bug number>','<app list>','<product>','<app type>','[arch]')
  sys.exit(1)

if len(sys.argv) == 2 and sys.argv[1] == "products":
  print "valid products:"
  for p in valid_products.keys():
    print "\t " + p
  sys.exit(1)

buildtag = sys.argv[1]
app = sys.argv[2]
bug = sys.argv[3]
applist = string.split(sys.argv[4],',')
product = sys.argv[5]
type = sys.argv[6]

if product in valid_products.keys():
  archs = valid_products[product][0]
  hosts = valid_products[product][1]
  cpdir = valid_products[product][2]
else:
  print "unknown product...try again"
  sys.exit(1)
if len(sys.argv) == 8:
  archs = [sys.argv[7],]

cpdir = cpdir + '/' + app + '-' + bug + '-' + string.strip(string.split(buildtag,'_')[1])
if not os.path.exists(cpdir):
  os.system('mkdir -p ' + cpdir + '/SRPMS')
if type == "target":
  os.system('cp -a %s/../../%s/SRPMS/%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for a in archs:
    if os.path.exists('%s/../../%s/%s' % (cpdir,buildtag,a)):
      os.system('mkdir -p %s/%s/target' % (cpdir,a))
      for mvl in applist:
        os.system('cp -a %s/../../%s/%s/target/%s-* %s/%s/target' % (cpdir,buildtag,a,mvl,cpdir,a))
        if (len(os.popen('find %s/../../%s/%s/target/ | grep %s_64'%(cpdir,buildtag,a,mvl)).readlines()) > 0): 
          os.system('cp -a  %s/../../%s/%s/target/%s_64-* %s/%s/target' % (cpdir,buildtag,a,mvl,cpdir,a))
        if (len(os.popen('find %s/../../%s/%s/target/ | grep %s_32'%(cpdir,buildtag,a,mvl)).readlines()) > 0):
          os.system('cp -a  %s/../../%s/%s/target/%s_32-* %s/%s/target' % (cpdir,buildtag,a,mvl,cpdir,a))



elif type == "target-opt":
  os.system('cp -a %s/../../%s/SRPMS/%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for a in archs:
    if os.path.exists('%s/../../%s/%s' % (cpdir,buildtag,a)):
      os.system('mkdir -p %s/%s/target/optional' % (cpdir,a))
      for mvl in applist:
        os.system('cp -a %s/../../%s/%s/target/optional/%s-* %s/%s/target/optional' % (cpdir,buildtag,a,mvl,cpdir,a))
        if (len(os.popen('find %s/../../%s/%s/target/ | grep %s_64'%(cpdir,buildtag,a,mvl)).readlines()) > 0):
            os.system('cp -a  %s/../../%s/%s/target/%s_64-* %s/%s/target' % (cpdir,buildtag,a,mvl,cpdir,a))

elif type == "common":
  os.system('cp -a %s/../../%s/SRPMS/common-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  if os.path.exists('%s/../../%s/host/common' % (cpdir,buildtag)):
    os.system('mkdir -p %s/host/common' % (cpdir))
    for mvl in applist:
      os.system('cp -a %s/../../%s/host/common/common-%s-* %s/host/common' % (cpdir,buildtag,mvl,cpdir))

elif type == "common-host":
  os.system('cp -a %s/../../%s/SRPMS/common-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for h in hosts:
    if os.path.exists('%s/../../%s/host/%s' % (cpdir,buildtag,h)):
      os.system('mkdir -p %s/host/%s' % (cpdir,h))
      for mvl in applist:
        os.system('cp -a %s/../../%s/host/%s/common-%s-* %s/host/%s' % (cpdir,buildtag,h,mvl,cpdir,h))
elif type == "host":
  os.system('cp -a %s/../../%s/SRPMS/host-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for h in hosts:
    if os.path.exists('%s/../../%s/host/%s' % (cpdir,buildtag,h)):
      os.system('mkdir -p %s/host/%s' % (cpdir,h))
      for mvl in applist:
        os.system('cp -a %s/../../%s/host/%s/host-%s-* %s/host/%s' % (cpdir,buildtag,h,mvl,cpdir,h))
elif type == "host-tools":
  os.system('cp -a %s/../../%s/SRPMS/host-tool-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for h in hosts:
    if os.path.exists('%s/../../%s/host-tools/%s' % (cpdir,buildtag,h)):
      os.system('mkdir -p %s/host-tools/%s' % (cpdir,h))
      for mvl in applist:
        os.system('cp -a %s/../../%s/host-tools/%s/host-tool-%s-* %s/host-tools/%s' % (cpdir,buildtag,h,mvl,cpdir,h))

elif type == "cross-host":
  os.system('cp -a %s/../../%s/SRPMS/cross-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for a in archs:
    if os.path.exists('%s/../../%s/%s' % (cpdir,buildtag,a)):
      for h in hosts:
        if os.path.exists('%s/../../%s/%s/cross/%s' % (cpdir,buildtag,a,h)):
          os.system('mkdir -p %s/%s/cross/%s' % (cpdir,a,h))
          for mvl in applist:
            os.system('cp -a %s/../../%s/%s/cross/%s/cross-%s-%s-* %s/%s/cross/%s' % (cpdir,buildtag,a,h,a,mvl,cpdir,a,h))
            if (len(os.popen('find %s/../../%s/%s/cross/%s/ | grep %s*_*64'%(cpdir,buildtag,a,h,mvl)).readlines()) > 0): 
              os.system('cp -a  %s/../../%s/%s/cross/%s/%s*_*64-* %s/%s/cross/%s' % (cpdir,buildtag,a,h,mvl,cpdir,a,h))
            if (len(os.popen('find %s/../../%s/%s/cross/%s | grep %s*_*32'%(cpdir,buildtag,a,h,mvl)).readlines()) > 0):
              os.system('cp -a  %s/../../%s/%s/cross/%s/%s*_*32-* %s/%s/cross/%s' % (cpdir,buildtag,a,h,mvl,cpdir,a,h))
elif type == "cross-common":
  os.system('cp -a %s/../../%s/SRPMS/cross-%s-* %s/SRPMS' % (cpdir,buildtag,app,cpdir))
  for a in archs:
    if os.path.exists('%s/../../%s/%s' % (cpdir,buildtag,a)):
      os.system('mkdir -p %s/%s/cross/common' % (cpdir,a))
      for mvl in applist:
        os.system('cp -a %s/../../%s/%s/cross/common/cross-*%s-* %s/%s/cross/common' % (cpdir,buildtag,a,mvl,cpdir,a))
else:
  print "unknown type...try again"
  sys.exit(1)


