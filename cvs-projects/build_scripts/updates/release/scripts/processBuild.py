#! /usr/bin/env python

import os, sys
from operator import itemgetter

sys.path.append("../update")
import db

def deleteBuild(build_id, operator="equal", kill=False):
	myDB = db.db()
	myDB.Connect()

	if operator.lower() == "older":
		op = "<="
	elif operator.lower() == "newer":
		op = ">="
	else:
		op = "="

	result = myDB.Command('''SELECT * FROM Builds.builds WHERE id %s %d'''%(op, int(build_id)))
	if not result:
		print "Can't find any builds that match for %s", build_id
		myDB.Close()
		sys.exit(1)
	if type(result) == type(""):
		print result
		myDB.Close()
		sys.exit(1)
	

	for build in result:
		BuildId = build['id']
		sys.stdout.write("Removing Build: %s..."%(BuildId))
		sys.stdout.flush()

		#verify build exists
		result = myDB.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(int(BuildId)))
		if not result:
			print "Can't find Build: %s"%(BuildId)
			myDB.Close()
			sys.exit(1)

		#delete from build table
		result = myDB.Command('''DELETE FROM Builds.builds WHERE id=%d'''%(int(BuildId)))
		
		if kill:
			sys.stdout.write("deleting files...")
			sys.stdout.flush()
			path = build['path']
			os.system("rm -rf %s"%(path))
		
		print "Done!"
		sys.stdout.flush()
	#end for build_list

	myDB.Close()
#end deleteBuild


def showBuilds():
	myDB = db.db()
	myDB.Connect()
	result = myDB.Command('''SELECT * FROM Builds.builds''')
	if result:
		build_list = sorted(list(result), key=itemgetter('id'))
	else:
		build_list = []
	
	print "-----------------------------------------------------------------------------------------------------------------"
	print "|   ID    | PRODUCT ID |           TAG            |                       PATH                         | DELETE |"

	for build in build_list:
		build_id = str(build['id'])
		if len(build_id) < 7:
			build_id= "0"+build_id
		print '''| %7s |  %8s  |%26s|%52s|%8s|'''%(build_id, build['products_id'], build['buildtag'], build['path'], build['delete'])
	print "-----------------------------------------------------------------------------------------------------------------"
#end showBuilds


def usage():
	print "Usage: processBuild.py <command>"
	print "\nCommands:\n"
	print "list                - list all builds that are in the Database."
	print "delete [operator] <build_id>   - removes all the build results for"
	print "                      <build_id> from the Build Database."
	print "                      [operator] is one of 'older' or 'newer'"
	print "                      NOTE: There is an implied 'AND' when using"
	print "                      the operators"
	print "kill all <build_id> - deletes the build results from dev_area"
	print "                      and remove the results from the database."
#end usgae

def main(argv):
	if len(argv) <2 or len(argv) >4:
		usage()
		sys.exit(1)
	
	if argv[1].find("help") != -1:
		usage()
		sys.exit(0)
	
	#process commands
	if argv[1] == "list":
		if len(argv) == 2:
			showBuilds()
			sys.exit(0)
		else:
			print "The 'list' command does not accept any arguments"
			sys.exit(1)
	elif argv[1] == "delete":
		if len(argv) == 3:
			deleteBuild(argv[2])
			sys.exit(0)
		elif len(argv) ==4:
			if argv[2] == "older" or argv[2] == "newer":
				deleteBuild(argv[3], operator=argv[2])
				sys.exit(0)
			else:
				print "Options can olny be 'older' or 'newer'"
				sys.exit(1)
		else:
			print "The 'delete' command requires 1 argument"
			sys.exit(1)
	elif argv[1] == "kill":
		if len(argv) == 4 or len(argv) == 5:
			if argv[2] != "all":
				print "The 'kill' command requires 'all'"
				sys.exit(1)
			#else
			if len(argv) == 4:
				deleteBuild(argv[3], kill=True)
				sys.exit(0)
			else:
				deleteBuild(argv[4], operator=argv[3], kill=True)
				sys.exit(0)
		else:
			print "The 'kill all' command requires 1 argument"
			sys.exit(1)
	else:
		usage()
		sys.exit(1)
#end main


if __name__ == "__main__":
        main(sys.argv)
        sys.exit(1)

