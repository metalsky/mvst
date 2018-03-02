#!/usr/bin/python

###########################################
#		makeLabels.py
#
#  Take label templates and generate D Labels
#
#
###########################################
import os,sys,re,string

processorFamily = {
"arm_720t_be":	"ARMv3",
"arm_720t_le":	"ARMv3",
"arm_v4t_le": 	"ARMv4",
"arm_v4t_be": 	"ARMv4",
"arm_v5t_le": 	"ARMv5",
"arm_v6_vfp_le": "ARMv6",
"mips2_fp_le":	"MIPSfp",
"mips2_fp_be":	"MIPSfp",
"mips2_nfp_be":	"MIPSnfp",
"mips2_nfp_le":	"MIPSnfp",
"mips64_fp_be":	"MIPSfp64",
"mips64_fp_le":	"MIPSfp64",
"ppc_405":	"PowerPC400",
"ppc_440":	"PowerPC400",
"ppc_440ep":	"PowerPC400",
"ppc_7xx":	"PowerPC700",
"ppc_74xx":	"PowerPC7400",
"ppc_8xx":	"PowerQUICC I",
"ppc_82xx":	"PowerQUICC II",
"ppc_83xx":	"PowerQUICC II Pro",
"ppc_85xx":	"PowerQUICC III",
"ppc_9xx":	"PowerPC64",
"sh_sh3_le":	"SH3",
"sh_sh4_le":	"SH4",
"x86_586":	"X86",
"x86_pentium":	"X86",
"x86_pentium2":	"X86",
"x86_pentium3":	"X86",
"x86_pentium4":	"X86",
"x86_amd64":	"AMD64",
"x86_em64t":	"EM64T",
"arm_xscale_be":"XScale",
"arm_xscale_le":"XScale",
"arm_iwmmxt_le":"Xscale-iWMMXt",
"xtensa_linux_be":"Xtensa",
"xtensa_linux_le":"Xtensa",
"xtensa_linux_test":"Xtensa"
}

vendorProcessorFam = {}

typeDict = {
"target": "Target Binaries",
"cross":  "Cross Binaries",
"lsps":   "Linux Support Packages",
"docs":   "Documentation",
"host":   "Host Binaries",
"devrocket": "DevRocket",
"src":    "Sources"
}


editionDict = {
"pro":  "Professional Edition",
"cge":  "Carrier Grade Edition",
"cee":  "Consumer Electronics Edition",
"mobilinux": "Mobilinux"
}

class LabelData:
  def __init__(self,type,buildid,arch):
    self.type = type
    self.buildid = buildid
    self.arch = arch

def parseTemplate(edition, version, subVersion, isoName, labelData):
  global processorFamily, editionDict
  #open the template file
  try:
    templateFile = open("/mvista/dev_area/cd_label_templates/%s.template"%(labelData.type),"r")
    if labelData.arch is not None:
      labelFile = open("%s-%s-%s.lay"%(labelData.type, labelData.arch, labelData.buildid), "w")
    else:
      labelFile = open("%s-%s-%s.lay"%(labelData.type, edition, labelData.buildid), "w")
    
  except IOError:
    print "Error Opening Files"
    sys.exit(1)
 
  regexp = re.compile(r"\%\w+\%")
  for line in templateFile.readlines(): 
    matched = regexp.search(line)
    if matched:
      if matched.group(0) == "%version%":
        line = regexp.sub(version,line)
  
      elif matched.group(0) == "%iso%":
        line = regexp.sub(isoName,line)
     
      elif matched.group(0) == "%subversion%":
        line = regexp.sub(subVersion,line)

      elif matched.group(0) == "%arch%":
        line = regexp.sub(labelData.arch,line)

      elif matched.group(0) == "%archfamily%":
        line = regexp.sub(processorFamily[labelData.arch],line)      

      elif matched.group(0) == "%edition%":
        line = regexp.sub(editionDict[edition],line)

      elif matched.group(0) == "%build%":
        line = regexp.sub(labelData.buildid,line)
     
      else:
        print "Matched Unknown Macro %s"%(matched.group(0))
        sys.exit(1) 
    labelFile.write(line) 

    #and loop for the next line
  return


def main(argv=sys.argv):
  product = None
  version = None
  labelDict = {}
  labelDir = "CDLABELS"
  if len(argv) != 3:
    print "Invalid Args"
    print "Usage: makeLabels.py <version> <release>"
    print "makeLabels.py 4.0 4.0.1"
    print "Be sure to run this from a cdimages directory"
    sys.exit(1)

  #Locate the Templates Dir
  if not os.path.exists("/mvista/dev_area/cd_label_templates"):
    print "I can't find the templates directory, quitting...."
    sys.exit(1)
#Some setup
  if not os.path.exists(labelDir):
    os.system("mkdir %s"%(labelDir))
  regexp = re.compile(r"(\w+)-(\w+)-(\d+)")
  version = argv[1]
  subVersion = argv[2] 
#build a dictionary of the work we gotta do
  print "Building list of work to do..."
  for dir in os.popen('ls *.iso').readlines():
    dir = string.replace(dir, '\012','')
    matched = regexp.match(dir)
    if matched:
      if matched.group(1) in ("host",):    
        product = matched.group(2)
        labelDict[dir] = LabelData(matched.group(1),matched.group(3),None)
      elif matched.group(1) in ("docs","src","devrocket"):
        labelDict[dir] = LabelData(matched.group(1),matched.group(3),None)
      elif matched.group(1) in ("lsps","cross","target"):
        labelDict[dir] = LabelData(matched.group(1),matched.group(3),matched.group(2) )
      else:
        print "Unknown Iso type found, fix your script dummy"
        sys.exit(1)

#Run through the dict loading the proper template and going nuts
  os.chdir(labelDir)
  for dir in labelDict.keys():
    parseTemplate(product, version, subVersion, dir, labelDict[dir])

  return


if __name__ == "__main__":
  main()

