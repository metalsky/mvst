#!/usr/bin/env python


import bugzServer, sys


try:
	myarg = sys.argv[1]
except:
	print "%s requires a buildtag as an argument." %(sys.argv[0])
	sys.exit(1)


mydb = bugzServer.server()
mydb.Connect()
results = mydb.Command('''SELECT bug_id,fixed_in,bug_status,resolution FROM bugz.bugs WHERE fixed_in LIKE "%%%s%%"''' %(myarg))


for result in results:
	print "Bug #" + str(result['bug_id']) + " status is: " + str(result['bug_status']) + " \tresolution is: " + str(result['resolution'])
