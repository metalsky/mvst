#!/usr/bin/env python

#########
#
# Imports
#
#########

import string
import sys
import os
import getopt
import popen2
import re
from types import *
import pickle
import getpass

#########
#
# Globals
#
#########

commandLine=sys.argv
searchDirs= ['host', 'common', 'host-tools' ]
hostList = { }
archList = { }
Packages = { }
normalizeTarget = [ "_n64", "_o32", "_64", "_32" ]
normalizeHost = ["host-"]
normalizeCommon = ["common-"]
normalizeCross = ["cross-", "_n64", "_o32", "_64", "_32"]


#####################
#
# FindList Generation
#
#####################

def findListGen(directory):
	tmpStorage = "/tmp/versiontable-findlist"
	findListMount = "/tmp/versiontable-mount"
	dirSplit = os.path.split(directory)
	if (dirSplit[1] == ""):
		dirSplit = os.path.split(dirSplit[0])
	cdImageDir = "%s/%s/cdimages" % (dirSplit[0], dirSplit[1])
	cdImages = os.listdir(cdImageDir)
	if not os.path.isdir(tmpStorage):
		os.mkdir(tmpStorage)
	if not os.path.isdir(findListMount):
		os.mkdir(findListMount)
	FindList = ""
	for iso in cdImages:
		if (iso != "README.md5sum"):
			os.system("cp %s/%s %s" % (cdImageDir, iso, tmpStorage))
			os.system("mount -o loop %s/%s %s" % (tmpStorage, iso, findListMount))
			listfd = popen2.popen2("cd %s; find . -type f | sed s,\\./,," % (findListMount))
			FindList = FindList + listfd[0].read()
			os.system("umount %s" % (findListMount))
			os.system("rm %s/%s" % (tmpStorage, iso))
	return FindList

####################
#
# Rpm Info Gathering
#
####################

def getRpmInfo(rpmPath,optional):
	  rpmInfoFd = popen2.popen3("rpm -qp --queryformat '%%{NAME}\n%%{VERSION}\n%%{RELEASE}\n%%{LICENSE}\n%%{GROUP}\n%%{SOURCERPM}\n' %s" % (rpmPath))

	  rpmInfo=rpmInfoFd[0].readlines()
	  rpmError=rpmInfoFd[2].read()
	  if (len(rpmError) == 0):
	    rpmInfoDict={'Name':string.replace(rpmInfo[0],'\n',''), \
		     'Version': string.replace(rpmInfo[1],'\n',''), \
		     'Revision': string.replace(rpmInfo[2],'\n',''), \
                     'Optional': optional, \
		     'License': string.replace(rpmInfo[3],'\n',''), \
		     'Group': string.replace(rpmInfo[4],'\n',''), \
		     'SRPM': string.replace(rpmInfo[5],'\n','')}
	    return rpmInfoDict
	  else:
	    return {} 
	
def getSubClasses(textDict):
	tempTextDict = { }
	for Dir in textDict.keys():
		tempTextDict = { }
		for each in textDict[Dir]:
			set_re = re.compile("^([a-zA-Z0-9]*)/(.*mvl)$", re.MULTILINE)
			for name, val  in set_re.findall(each):
				if not tempTextDict.has_key(name):
					tempTextDict[name] = [ ]
				tempTextDict[name] = tempTextDict[name] + [ val ]

def loadDict(pathList,dict,basePath):
	localDict = {}
	if (len(pathList) == 1):
		optional=0
		if(os.path.isfile(os.path.join(basePath,pathList[0]))):
			dict[pathList[0]] = getRpmInfo(os.path.join(basePath,pathList[0]),0)
		else:
			dict[pathList[0]] = getRpmInfo(os.path.join(basePath,"optional/",pathList[0]), 1)
		return dict
	if not dict.has_key(pathList[0]):
		dict[pathList[0]] = {}
	dict[pathList[0]] = loadDict(pathList[1:],dict[pathList[0]], os.path.join(basePath,pathList[0]))
	return dict

def getClasses(text, basePath):
	textDict = { }
	dirs = [ ]
	set_re=re.compile( "^(.*mvl)$" , re.MULTILINE )	
	for val in set_re.findall( text ):
		dirs = string.split( val , "/" )
		if not textDict.has_key(dirs[0]):
			textDict[dirs[0]]={}
			
		textDict[dirs[0]] = loadDict(dirs[1:],textDict[dirs[0]], '%s%s' % (basePath,dirs[0]))
	return textDict

def parseText(text):
	return string.split(text,"\n")

def parseBoms(basedir, bomdir):
	boms = os.listdir(bomdir)
	fullfind=""
	dirfind = re.compile("^./(.+):$", re.MULTILINE)
	rpmfind = re.compile("^(.*).mvl$", re.MULTILINE)
	dir=""
	for each in boms:
		bom = open("%s/%s" % (bomdir,each)).readlines()
		for line in bom:
			newdir = dirfind.findall(line)
			if (len(newdir) == 1):
				dir = newdir[0]
			elif rpmfind.findall(line):
				fullfind = "%s%s/%s/%s\n" % ( fullfind, basedir, dir, string.replace(line,'\n',''))
	return fullfind	

###################
#
# Display component
#
###################

def getType(dict, path):
	pathsplit = string.split(path, "/")
	pathlen = len(pathsplit)
	if archList.has_key(pathsplit[0]):
		if (pathsplit[1] == "cross"):
			return "cross"
		if (pathsplit[1] == "target"):
			return "target"
		if (pathsplit[1] == "lsps"):
			return "lsp"
	if pathsplit[0] == "host":
		if (string.split(pathsplit[2], "-")[0] == "host"):
			return "host"
		if (string.split(pathsplit[2], "-")[0] == "common"):
			return "common"
		if ((pathsplit[1] == "common") and (pathsplit[2] == "adk")):
			return "host"
	if pathsplit[0] == "common":
		return "common"
	if pathsplit[0] == "host-tools":
		return "host-tool"
	return "unknown"	

def getHost(type, path, packageHostList):
	pathsplit = string.split(path, "/")
	pathlen = len(pathsplit)
	if (type == "target"):
		return "N/A"
	if (type == "lsp"):
		return "N/A"
	if (pathsplit[pathlen - 2] == "common"):
		return "All"
	if (pathsplit[pathlen - 2] == "adk"):
		return "All"
	if hostList.has_key(pathsplit[pathlen - 2]):
		if packageHostList == "":
			return pathsplit[pathlen - 2]
		else:
			if (string.find(packageHostList, pathsplit[pathlen - 2]) == -1):
				return "%s,%s" % (packageHostList, pathsplit[pathlen - 2])
			else:
				return packageHostList
	if (pathsplit[pathlen - 3] == "windows2000"):
		return pathsplit [ pathlen - 3 ]
	if (pathsplit[pathlen - 2] == "cluster"):
		return packageHostList

	return "unknown"


def normalizeName(type, name):
	newName = name
	if (type == "target"):
		for each in normalizeTarget:
			newName = string.replace(newName, each,"")
	if (type == "common"):
		for each in normalizeCommon:
			newName = string.replace(newName, each,"")
	if (type == "host"):
		for each in normalizeHost:
			newName = string.replace(newName, each,"")
	if (type == "cross"):
		for each in normalizeCross:
			newName = string.replace(newName, each,"")
		for each in archList.keys():
			newName = string.replace(newName, "%s-" % each,"")
	return newName
def tree_collapse(dict,path,includeLsps):
	if dict.has_key("Version"):
		type = getType(dict,path)
		if (type == "lsp") and not includeLsps:
			return
		if not Packages.has_key(type):
			Packages[type] = { }
		name = normalizeName(type,dict['Name'])
		if not Packages[type].has_key(name):
			Packages[type][name] = \
				{'Version':dict['Version'], \
	            		'Optional': dict['Optional'], \
	            		'Revision': dict['Revision'], \
	            		'SRPM': dict['SRPM'], \
	            		'Group': dict['Group'], \
	            		'License': dict['License'], \
	            		'Hosts': ""}
		Packages[type][name]["Hosts"] = getHost(type, path, Packages[type][name]["Hosts"])
	else:
		for each in dict.keys():
			if (path == ""):
				tree_collapse(dict[each],"%s" % (each), includeLsps)
			else:
				tree_collapse(dict[each],"%s/%s" % (path, each), includeLsps)

def display_package(type,package,delimiter):
	
	Delimit = {"Tab":{"Head":"","Mid":"\t","Tail":""}, \
		   "Wiki":{"Head":"|", "Mid":"|","Tail":"|"}} 

	line = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % \
		(Delimit[delimiter]["Head"], \
		type, \
		Delimit[delimiter]["Mid"], \
		package, \
		Delimit[delimiter]["Mid"], \
		Packages[type][package]['Group'], \
		Delimit[delimiter]["Mid"], \
		Packages[type][package]['Version'], \
		Delimit[delimiter]["Mid"], \
		Packages[type][package]['Revision'], \
		Delimit[delimiter]["Mid"], \
		Packages[type][package]['License'], \
		Delimit[delimiter]["Mid"], \
		Packages[type][package]['SRPM'])

	if Packages[type][package]['Optional']:
		line = "%s%syes" % (line, Delimit[delimiter]["Mid"])
	else:
		line = "%s%sno"  % (line, Delimit[delimiter]["Mid"])

	line = "%s%s%s%s\n" % (line, Delimit[delimiter]["Mid"],Packages[type][package]['Hosts'],Delimit[delimiter]["Tail"])

	return line
 
def display_output(delimiter):
	text = ""
	for type in Packages.keys():
		for package in Packages[type].keys():
			text = "%s%s" % (text, display_package(type, package, delimiter))
	return text

def displayPrep(rpmDict,includeLsps):

	hostIgnore = { "common":1, "cluster":1}
	archIgnore = { "common":1, "host":1, "host-tools":1, "usr":1 }

	for each in rpmDict['host'].keys():
		if not hostIgnore.has_key(each):
	 		hostList[each] = 1

	for each in rpmDict.keys():
		if not archIgnore.has_key(each):
			archList[each] = 1

	tree_collapse(rpmDict,"",includeLsps)

def usage():
	print "\n%s \n" \
	      "\t-d <directory>         | * Directory of the build\n" \
	      "\t-a                     | Run all parts, ignore intermediate datafiles\n" \
	      "\t-l                     | Inlcude LSPs in the display data\n" \
	      "\t-h                     | Usage information \n" \
	      "\t-o <output direcotry>  | All the intermediate files and display data will be place in directory\n" \
	      "\t                       | otherwise it will be placed in pwd\n" \
	      "\t\n" \
	      "\tSelect in one of the following or %s will use find to determine which files to display\n" \
	      "\t\n" \
	      "\t-b <bom directory>     | Directory containing BOMs of each CD\n" \
	      "\t-r                     | Create a CD BOM list from the cds (expects the cds to be in ../cdimages/<buildid>\n" \
	      "\t-f <findlist>          | A list generated by cancatinating finds of the files under the cdimages| \n" \
	      "\t\n" \
	      "\t* - required\n" \
	      "\t\n" %( commandLine[0],commandLine[0])
	sys.exit(1)


######################
#
# Main Section
#
######################


def main():

######################
# Comand Line parsing
######################

	bomdir=""
	findListFile=""
	runDisplay=0
	runAll=0
	outputDir=""
	findList = ""
	arches=[]
	classDict = {}
	WorkingDir=""
	includeLsps = 0
	runBoms=0
	
	try:
        	opts, args = getopt.getopt(sys.argv[1:], "hd:b:f:rao:l", [])
	except:	
		usage()

	for o, a in opts:
		if ( o == "-d" ):
			WorkingDir=a
		if ( o == "-b" ):
			bomdir=a
		if ( o == "-f"):
			findListFile=a
		if ( o == "-r"):
			runBoms=1
		if ( o == "-a"):
			runAll=1
		if ( o == "-o"):
			outputDir=a
		if ( o == "-l"):
			includeLsps = 1		
		if ( o == "-h"):
			usage()
	if ( WorkingDir == ""):
		usage()

	if outputDir and not os.path.exists(outputDir):
		os.system("mkdir -p " + outputDir)
		if not os.path.exists(outputDir):
			sys.stderr.write("Could not find or create %s\n" % outputDir)
			sys.exit(1)
	elif not outputDir:
		outputDir = os.getcwd()

######################
# Parse Build README
######################
	readme = open("%s/README.build" % (WorkingDir)).read()
	readmeLines = parseText(readme)
	collectArch=0
	BuildTag=""
	for each in readmeLines:
		if ( not  string.find(each,"Using")):
			collectArch = 0
			if not BuildTag:
				BuildTag = string.split(each, " ")[1]
		elif collectArch:
			arches=arches + [each]
		elif ( each == "Building the following architectures:"):
		   collectArch = 1

	sys.stderr.write("Build ID         : %s\n" % BuildTag)
	sys.stderr.write("Output directory : %s\n\n" % outputDir)
	if runBoms:
		sys.stderr.write("Creating BOMs....")
		findList = findListGen(WorkingDir)
		sys.stderr.write("done.\n")
	elif os.path.exists("%s/%s.findList" % (outputDir,BuildTag)) and not runAll:
		sys.stderr.write("Reading in %s/%s.findList...." % (outputDir,BuildTag)) 
		findListFD = open("%s/%s.findList" % (outputDir,BuildTag))
		findList = findListFD.read()
		sys.stderr.write("done.\n")
	if os.path.exists("%s/%s.data" % (outputDir,BuildTag)) and not runAll:
		sys.stderr.write("Reading in %s/%s.data...." % (outputDir,BuildTag)) 
		classDictFD = open("%s/%s.data" % (outputDir,BuildTag), "r")
		classDict = pickle.load(classDictFD)
		classDictFD.close()
		sys.stderr.write("done.\n")

#######################
# File list generation
#######################

	if (findList == ""):
		sys.stderr.write("Generating find list....") 
	 	if (bomdir != ""): 
			findList = parseBoms(WorkingDir,bomdir)
 		elif (findListFile != ""):
			findFd = open(findListFile)
			findList = findFd.read()
			findFd.close()
		else:
			findFd = popen2.popen2("find %s/ -type f | grep -v installer_rpms" % (WorkingDir))
			findList = findFd[0].read()
		sys.stderr.write("done.\n")
		sys.stderr.write("Saving find list to %s/%s.findList...." % (outputDir,BuildTag)) 
		findListSaveFd = open("%s/%s.findList" % (outputDir,BuildTag), "w")
		findListSaveFd.write(findList)
		findListSaveFd.close()
		sys.stderr.write("done.\n")
	findList = string.replace(findList, WorkingDir + "/", "")
	findList = string.replace(findList, "optional/", "")
	if ( classDict == {} ):	
		sys.stderr.write("Gathering RPM information....") 
		classDict = getClasses(findList, WorkingDir)
		sys.stderr.write("done.\n")
		sys.stderr.write("Saving RPM information to %s/%s.data...." % (outputDir,BuildTag)) 
		classDictSaveFd = open("%s/%s.data" % (outputDir,BuildTag), "w")
		pickle.dump(classDict,classDictSaveFd,2)
		classDictSaveFd.close()
		sys.stderr.write("done.\n")
	displayPrep(classDict,includeLsps)
	
	output = display_output("Wiki")
	outputFileFd = open("%s/%s.wiki" % (outputDir,BuildTag) , "w")
	outputFileFd.write(output)
	outputFileFd.close()
	print
	print "Wiki Version     : %s/%s.wiki" % (outputDir,BuildTag)

	output = display_output("Tab")
	outputFileFd = open("%s/%s.tab" % (outputDir,BuildTag), "w")
	outputFileFd.write(output)
	outputFileFd.close()
	print "Tab Version      : %s/%s.tab" % (outputDir,BuildTag)
	
	os.system("cat %s/%s.tab | column -t -s '	' > %s/%s.formated" % (outputDir, BuildTag, outputDir, BuildTag))
	print "Formated Version : %s/%s.formated" % (outputDir,BuildTag)

main()
