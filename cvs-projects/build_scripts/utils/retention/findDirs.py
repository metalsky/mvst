#!/usr/bin/python

#This is a modified version of the findDirs.py script in /utils.
#It should not be used for any other purpose than as a module for the retention 
#script!

import os, re, sys, getopt
from glob import glob
from time import gmtime

daysElapsed = (None,0,31,59,90,120,151,181,212,243,273,304,334)
YEAR,MONTH,DAY = 0,1,2
DEBUG = 1
WARN = 0

def usage(name):
	print '''
	findDirs -- A script to find and remove old builds from disk.

	Usage: %s [options]

	--age #       : Maximum age (in days) to keep builds around.  Default 14.
	--path /path/ : Root directory to scan for builds.  Default /mvista/engr_area
	--WARN        : Print detailed information regarding which builds will be kept and removed.
	''' % (name)
#end usage

def globWalk(dirList, dirName, filesInDir):
	"""
	globWalk: Changes dirList in place, appending every directory that looks like a build directory to it.
	          Some exceptions:
			  	Directories containing *released* or *snapshot* will not be parsed, nor will any directories under them.
				Nested build directories will be ignored.  Only the top level will be found and modified.
	 
	Arguments 
		dirName,
		filesinDir : Function has to be written specifically for os.path.walk.  Consult
	 		         that documentation for details on the arguments. 

		dirList    : The list of directories, changed in place.
	"""

	regexp = re.compile(r"(.+)(\d\d\d\d\d\d)_\d\d\d\d\d\d")
	isBuildDir = regexp.match(dirName)

	i=0

	if isBuildDir:
		dirList.append(dirName)
		while i < len(filesInDir):
			del filesInDir[i]
	else:
		while i < len(filesInDir):
			if filesInDir[i] in ["released", ".snapshot"]:
				del filesInDir[i]
			i+=1
#end globWalk

def pruneOldDirs(dirList, days):
	"""
	pruneOldDirs

	Arguments
	  	dirList    : A list of directories containing builds.  Must be a proper build dir for the regular expression to match.
		days       : The length of time, in days, before a build directory will be purged from the list.

	Returns
		returnList : The list of directories which were older than the specified days argument.
	"""
	returnList = []	
	td = gmtime()
	todaysDate = ( td[YEAR] - 2000 , td[MONTH], td[DAY] ) 

	regexp = re.compile( r"(/.+)+(/.+)(\d\d)(\d\d)(\d\d)_.+" )
	for dir in dirList:
		buildDate = ( int(regexp.match(dir).group(3)) , \
					  int(regexp.match(dir).group(4)) , \
					  int(regexp.match(dir).group(5))  )
		
		#print '''--Build %s--''' % dir
		#print buildDate, todaysDate
		#print '''Days between: %s''' % daysBetween(buildDate,todaysDate)
		#print '''---'''

		if daysBetween(buildDate, todaysDate) > days:
			returnList.append(dir)
		elif DEBUG:
			pass
#			print "Keeping: " + dir	

	return returnList
#end pruneOldDirs

def daysBetween(today, otherDate):
	"""
	daysBetween: Calculate the elapsed days between two dates.
	
	Arguments:
		today, otherDate : Tuples of the form (yy ,mm ,dd)

	Returns:
		integer representing the number of days elapsed between the two dates.
	"""

	daysToToday = today[YEAR] * 365 + daysElapsed[today[MONTH]] + today[DAY]
	daysToOther = otherDate[YEAR] * 365 + daysElapsed[otherDate[MONTH]] + otherDate[DAY]

	if daysToToday > daysToOther:
		return daysToToday - daysToOther
	else:
		return daysToOther - daysToToday
#end daysBetween

def findDirs(path="/mvista/engr_area",days=14):
	"""
	findDirs: The main function of this script.  Walks through every folder under path, identifies it as
			  a build directory, and deletes it if it is older than the specified days argument.  Defaults
			  to /mvista/engr_area and 14 days, as that is the motivation for this script right now.

			  See the globWalk documentation for more details.

			  This function is completely portable, and is compatible with the DEBUG flag that is common
			  around monta vista.  Furthermore, a WARN global variable can be issued to prompt the user before
			  deletion.

	Arguments:
		path : The root path to scan.
		days : The number of days old a build can be and survive this process.

	"""
	dirList = []
	os.path.walk(path, globWalk, dirList)
	dirsToDelete = pruneOldDirs(dirList, days)

	if WARN:
		print "The dollowing directories are older than %d days and will be deleted:" % days
	 	for dir in dirsToDelete:
			print dir

		input = raw_input("Continue [Y/N]?")
		if input in ['Y', 'y']:
			if DEBUG:
				for dir in dirsToDelete:
					print dir
			else:
				for dir in dirsToDelete:
					pass
	else:
		for dir in dirsToDelete:
			if DEBUG and 'tools' in dir and 'host-tools' not in dir:
				print dir 
			else:
				pass
			
#end findDirs

#UI if script is run from a shell.
if __name__ in ['__main__']:

	path, age = None, None

	if len(sys.argv) == 1:
		print "\nWarning: Script is about to be run with default arguments, which includes silent deletion of directories."
		print "Maybe you wanted --help.\n"
		input =  raw_input("Contine Running Script [Y/N]?")

		if input in ['Y', 'y']:
			pass
		elif input in ['N', 'n']:
			print "User Aborted."
			sys.exit(1)
		else:
			print "Invalid.  Aborting"
			sys.exit(1)
	
	try:
		optlist, list = getopt.getopt(sys.argv[1:], '', ["help","age=", "path=", "WARN"] )
	except getopt.GetoptError:
		print "Invalid Argument.  Use --help for help."
		sys.exit(1)
		
	for opt in optlist:
		if opt[0] == '--help':
			usage(sys.argv[0])
			sys.exit(1)
		elif opt[0] == '--age':
			age = int(opt[1])
		elif opt[0] == '--path':
			path = opt[1]
		elif opt[0] == '--WARN':
			WARN = 1
		else:
			print "Invalid Argument %s" % opt[0]

	path = path or '/mvista/engr_area'
	age = age or 14

	input = 'y'
	if input in ['Y', 'y']:
		findDirs(path,age)
	else:
		print "Aborted."
		sys.exit(1)



						
		
	

