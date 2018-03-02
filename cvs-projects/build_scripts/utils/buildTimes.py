#!/usr/bin/python


#buildTimes.py - This script will parse the logs and tell us how long various things took to build.  
#This isn't meant to profile the build but to explore possible problems in compilers to help the toolchain with their work

#We'll do profiling in a more robust form using a profiling toolkit such as TAU

import os, sys, re, datetime, time, traceback, string

#GLOBALS
DEVAREA = '/mvista/dev_area'
timeRegex = re.compile(r'(\d\d):(\d\d):(\d\d)')

class Result:
	def __init__(self, start, resource):
		self.start = start
		self.stop  = None
		self.resource = resource
		self.elapsed = None

def getTimeDiff(dictEntry):
	if dictEntry.stop != None:
		parsedTime = timeRegex.match(dictEntry.start)
		startDelta = datetime.timedelta(seconds=int(parsedTime.group(3)), minutes=int(parsedTime.group(2)), hours=int(parsedTime.group(1)))
		parsedTime = timeRegex.match(dictEntry.stop)
		stopDelta = datetime.timedelta(seconds=int(parsedTime.group(3)), minutes=int(parsedTime.group(2)), hours=int(parsedTime.group(1)))
		duration = stopDelta - startDelta
		dictEntry.elapsed = time.strftime("%H:%M:%S",time.gmtime(duration.seconds))

def getBuildTime(edition, buildtag):
	buildid = re.match(r'.+_(\d\d\d\d\d\d\d)',buildtag).group(1)
	if string.find(edition,'devrocket') > -1:
		edition = 'devrocket/' + edition
	fileName = os.path.join(DEVAREA,edition,buildtag,'logs','buildhhl-%s.log'%buildid)
	file = open(fileName)
	
	startTime = re.compile(r'building target (.+) on node (.+) in .+ .+ at (\d.+) .+ ')
	endTime		= re.compile(r'completed target (.+) on node .+ (\d.+) .+ ')
	hostStart = re.compile(r'building target (.+) for (.+) on (.+) at (.+) P(.)T')
	hostEnd = re.compile(r'completed (.+) cross tools for target (.+) at (.+) P(.)T')
	resultsDict = {}
	cygResultsDict = {}
	solResultsDict = {}
	for line in file:
		timeVal = startTime.match(line)
		if(timeVal):
			resultsDict[timeVal.group(1)] = Result(timeVal.group(3),timeVal.group(2))
		else:
			timeVal = endTime.match(line)
			if(timeVal):
				#There's a try here in case we somehow run into a "completed" before a "building"
				try:
					resultsDict[timeVal.group(1)].stop = timeVal.group(2)
				except:
					sys.stderr.write('There was a problem parsing buildhhl log for build times, see carl\n')
					print line
					traceback.print_exc()

		if timeVal == None: #no match yet, try something else
			timeVal = hostStart.match(line)
			if(timeVal):
				if timeVal.group(2) == "solaris8":
					solResultsDict[timeVal.group(1)] = Result(timeVal.group(4),timeVal.group(3))
				elif timeVal.group(2) == "windows2000":
					cygResultsDict[timeVal.group(1)] = Result(timeVal.group(4),timeVal.group(3))
				else:
					raise StandardError, "Something got messed up in the parsing"
			else:
				timeVal = hostEnd.match(line)
				if(timeVal):
					if timeVal.group(1) == "solaris8":
						try:
							solResultsDict[timeVal.group(2)].stop = timeVal.group(3)
						except:
							sys.stderr.write("No results for %s %s\n"%(timeVal.group(1), timeVal.group(2)))
					elif timeVal.group(1) == "windows2000":
						try:
							cygResultsDict[timeVal.group(2)].stop = timeVal.group(3)
						except:
							sys.stderr.write("No results for %s %s\n"%(timeVal.group(1), timeVal.group(2)))
					else:
						print timeVal.group(1)
						raise StandardError, "Something got messed up in the parsing"


	file.close()
	#Calculate Elapsed Time


	
	for key in resultsDict.keys():
		getTimeDiff(resultsDict[key])

	for key in solResultsDict.keys():
		getTimeDiff(solResultsDict[key])

	for key in cygResultsDict.keys():
		getTimeDiff(cygResultsDict[key])


	return resultsDict,solResultsDict,cygResultsDict





def main(argv):
	if len(argv) != 3:
		print "Usage: %s <edition> <buildtag>"%argv[0]
		sys.exit(1)

	edition = argv[1]
	buildtag = argv[2]	

	buildTimes,solTimes,cygTimes = getBuildTime(edition, buildtag)
	nodeKeys = buildTimes.keys()
	solKeys = solTimes.keys()
	cygKeys = cygTimes.keys()

	nodeKeys.sort()
	solKeys.sort()
	cygKeys.sort()

	
	print "NODE TIMES:\n#######"
	for key in nodeKeys:
		print "%s on %s - Elapsed Time: %s"%(key, buildTimes[key].resource, buildTimes[key].elapsed)
	print "\nSOLARIS TIMES:\n#######"
	for key in solKeys:
		print "%s on %s - Elapsed Time: %s"%(key, solTimes[key].resource, solTimes[key].elapsed)
	print "\nCYGWIN TIMES:\n#######"
	for key in cygKeys:
		print "%s on %s - Elapsed Time: %s"%(key, cygTimes[key].resource, cygTimes[key].elapsed)



if __name__ == "__main__":
	main(sys.argv)


