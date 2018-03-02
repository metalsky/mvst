#!/usr/bin/python
import re, os, DBInteraction,lt_os


dbi = DBInteraction

def cleanupLogs():
	regexp = re.compile(r"/.*/(.*\d+_\d+).*")
	removalDirs = open("oldDirectories.txt", "r")

	for line in removalDirs.readlines():
		if "RELEASED_by_buildtag" not in line:
			extracted = regexp.match(line)
			lt_os.system ("sudo rm -rf /export/logs/" + extracted.group(1), False)
#}

def cleanupDB():
	regexp = re.compile(r"/.*/(.*\d+_\d+).*")
	removalDirs = open("oldDirectories.txt", "r")
	buildList = []

	for line in removalDirs.readlines():
		extracted = regexp.match(line)
		buildList.append(extracted.group(1))

	if(len(buildList) > 0):
		result = dbi.queryDB(None, 'id', 'Builds.builds', 'buildtag', buildList)
		buildIDList = map(lambda x: int(x['id']), result)
		dbi.removeBuildsByID(buildIDList)

#}



if __name__ in ['__main__']:
	cleanupDB()
