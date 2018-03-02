#!/usr/bin/python

PEXPECT_PATH = "/home/rell/build_scripts/utils/retention/Pexpect/"

import sys
sys.path.append(PEXPECT_PATH)
import server, bugzServer, MySQLdb, subprocess, pexpect

def testDB():
	'''
	testDB:
		Just a simple function that tests if the SQL Database needs to be flushed, and flushes it if necessary.
	'''
	testDB = server.server()
	if testDB.Connect() in ["Can't connect to MySQL database"]:
		child = pexpect.spawn("mysqladmin -u support -p flush-hosts")
		child.expect('.*:')
		child.sendline('support')
#}

def queryDB(db, selectArg, fromArg, whereArg, where):
	'''
	queryDB:
		A pretty specific query to the SQL DB, just used to save myself repetetive typing, and to make
		some code a little cleaner.  Not really general enough for external use, what you probably want
		is server.Command(str) or bugzServer.Command(str).
	'''


	if db == None:
		db = server.server()
		db.Connect()

	if type(where) == str:
		appendString = whereArg + "=" + where[:]

	elif type(where) == list:
		appendString = "("

		
		for cycle in where:
			if type(cycle) == int:
				appendString += "%s=%s OR " % (whereArg,str(cycle))
			elif type(cycle) == str:
				appendString += "%s='%s' OR " % (whereArg, cycle)
		appendString = appendString[:-4] + ")"


	return db.Command('''SELECT %s FROM %s WHERE %s''' % (selectArg, fromArg, appendString)) 
#}

def fetchKeepers():
	'''
	fetchKeepers:
		Fetches a list of every manually entered exemption from the database.
	'''
	releaseDB = server.server()
	releaseDB.Connect()
	result = releaseDB.Command("SELECT id,name FROM BuildCfg.deletion_exempt WHERE origin='MANUAL'")
	return map(lambda x: ( str(x['id']) ,  str(x['name']) ), result)
	releaseDB.Close()
#}


def removeKeeper(index):
	'''
		Given the id of a manually entered exemption, remove it.  Silently fails if the index
		is in any way invalid.
	'''
	releaseDB = server.server()
	releaseDB.Connect()
	result = releaseDB.Command('''DELETE FROM BuildCfg.deletion_exempt WHERE (id=%s AND origin='MANUAL')''' % index)
	releaseDB.DB_SERVER.commit()
	releaseDB.Close()
#}

def repopulateDB():
	'''
		This function yanks everything from the exemptions table, erases it completely, and puts everything back.
		I found that the auto-increment field was getting out of hand too fast, which is why I implemented this.
		Also has the bonus effect of removing duplicates.
	'''
	releaseDB = server.server()
	releaseDB.Connect()
	values = releaseDB.Command('SELECT * FROM BuildCfg.deletion_exempt GROUP BY name')
	releaseDB.Command('TRUNCATE BuildCfg.deletion_exempt')
	releaseDB.DB_SERVER.commit()
	releaseDB.Close()
	releaseDB.Connect()
	releaseDB.Command("ALTER TABLE BuildCfg.deletion_exempt AUTO_INCREMENT = 1")

	for v in values:
		releaseDB.Command('INSERT INTO BuildCfg.deletion_exempt (name,origin) VALUES("%s" , "%s")' % (v['name'].replace(" ", "") , v['origin']) )

	releaseDB.Close()
#}

def addKeeper(name, origin):
	releaseDB = server.server()
	releaseDB.Connect()
	if len(releaseDB.Command('SELECT * FROM BuildCfg.deletion_exempt WHERE (name="%s" AND origin="%s")')) is 0:
		releaseDB.Command('INSERT INTO BuildCfg.deletion_exempt (name,origin) VALUES("%s" , "%s")' % (name,origin))
	else:
		print "Addition Failed -- Already Exists"
		sys.exit(0)
	releaseDB.Close()
#}


def addBugzToDB():
	releaseDB = server.server()
	releaseDB.Connect()

	buildsToAdd = fetchBugzKeepers()
	for build in buildsToAdd:
		releaseDB.Command('INSERT INTO BuildCfg.deletion_exempt (name,origin) VALUES ("%s" , "BUGZ")' % build)

	old_buildsToAdd = old_fetchBugzKeepers()
	for build in old_buildsToAdd:
		releaseDB.Command('INSERT INTO BuildCfg.deletion_exempt (name,origin) VALUES ("%s" , "BUGZ")' % build)

	releaseDB.DB_SERVER.commit()
	releaseDB.Close()
#}

def removeAllBugz():
	releaseDB = server.server()
	releaseDB.Connect()

	releaseDB.Command("DELETE FROM BuildCfg.deletion_exempt WHERE origin='BUGZ'")

	releaseDB.Close()

def dumpAllKeepers():
	outFile = open('/tmp/KEEPERS', 'w')

	releaseDB = server.server()
	releaseDB.Connect()

	builds = releaseDB.Command('SELECT name FROM BuildCfg.deletion_exempt')
	builds = map(lambda x: str(x['name']) , builds)

	for build in builds:
		outFile.write(build + '\n')

	releaseDB.Close()

#}

def listBugzFromExempt():
	returnlist = []
	releaseDB = server.server()
	try:
		releaseDB.Connect()
	except:
		print "Could not connect to database.  Aborting."
		sys.exit(1)
	
	results = releaseDB.Command('SELECT DISTINCT name FROM BuildCfg.deletion_exempt WHERE origin="BUGZ"')
	returnlist = map(lambda x: str(x['name']) , results)

	return returnlist

def fetchBugzKeepers():
	returnList = []
	releaseDB = server.server()
	
	try:
		releaseDB.Connect()
	except:
		print "Could not connect to database.  Aborting."
		sys.exit(1)

	result = releaseDB.Command('SELECT DISTINCT builds_id FROM ReleaseAutomation.release_request')
	buildIDList = map(lambda x: int(x['builds_id']) , result)

	result = queryDB(releaseDB, 'buildtag', 'Builds.builds', 'id', buildIDList)
	returnList = map(lambda x: str(x['buildtag']) , result)

	return returnList


def old_fetchBugzKeepers():

	returnList = []

	releaseDB = server.server()
	bugzDB = bugzServer.server()

	try: 
		releaseDB.Connect()
		bugzDB.Connect()
	except: 
		print "Could not connect to database.  Aborting"
		sys.exit(1)
	

	result = queryDB(releaseDB, 'id', 'ReleaseAutomation.release_cycle', 'processed', '"N"')
	idList = map(lambda x: int(x['id']), result)

	result = queryDB(releaseDB, 'id', 'ReleaseAutomation.merged', 'release_cycle_id', idList)
	idList = map(lambda x: int(x['id']), result)

	result = queryDB(releaseDB, 'bug_id', 'ReleaseAutomation.combined', 'merged_id', idList)
	idList = map(lambda x: int(x['bug_id']), result)

	result = queryDB(bugzDB, 'fixed_in', 'bugs', 'bug_id', idList)
	buildList = map(lambda x: str(x['fixed_in']) , result)

	for build in buildList:
		if ',' in build:
			for splitBuild in build.split(','):
				returnList.append(splitBuild.replace(" ",""))
		elif ' ' in build:
			for splitBuild in build.split(' '):
				returnList.append(splitBuild.replace(" ",""))
		elif build.count("_") > 1 and build[0:3] != "f5_" and build[0:5] != 'f2624' and build[0:9] != 's124omap3' and build[0:6] != 'fp2624':
			buildString = build
			print buildString
			for i in range(build.count("_")):
				endindex = buildString.index("_") + 8
				returnList.append( buildString[0:endindex] )
				buildString = buildString[endindex:]
		else:
			returnList.append(build.replace(" ",""))
				
	releaseDB.Close()
	bugzDB.Close()
	return returnList
#}

def removeBuildsByID(idList):
	releaseDB = server.server()
	releaseDB.Connect()


	for id in idList:
		pass
		#releaseDB.Command("DELETE FROM build where id=%d" % id)
		#releaseDB.Command("DELETE FROM rpm where build_id=%d" % id)
		#releaseDB.Command("DELETE FROM package where build_id=%d" % id)

	releaseDB.Close()

#}



if __name__ in ['__main__']:
	print "This module does not support execution by itself."
	sys.exit(1)
		

