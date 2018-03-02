#!/usr/bin/env python
import bugzServer, sys
try:
	inStr = sys.argv[1]
except:	
	print "Maybe you should try inputting something, sheesh."
	sys.exit(0)

mydb = bugzServer.server()
mydb.Connect()
results = mydb.Command('''Select bug_id,fixed_in from bugz.bugs WHERE fixed_in LIKE "%%%s%%"''' % inStr)

for result in results:
	print "Bug #: " + str(result['bug_id']) + " fixed_in: " + str(result['fixed_in'])
