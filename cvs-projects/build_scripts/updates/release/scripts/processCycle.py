#! /usr/bin/env python

import os, sys
sys.path.append("../update")

import db



######################
#     FUNCTIONS      #
######################

def printTable(result):
	print "---------------------------------------------"
	print "|   ID   |   PROCESS DATE   |   LIVE DATE   |"
	print "---------------------------------------------"
	for x in result:
		print '''|%8s|%18s|%15s|'''%(x['id'], x['process_date'], x['live_date'])
	print "---------------------------------------------"
#end printTable


def unclosedCycles():
	mydb = db.db()
	mydb.Connect()
	result = mydb.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE closed="N"''')
	if type(result) == type(""):
		print result
	
	mydb.Close()
	printTable(result)
#end openCycles


def closeCycle(id):
	mydb = db.db()
	mydb.Connect()
	result = mydb.Command('''UPDATE ReleaseAutomation.release_cycle SET closed="Y" WHERE id=%d'''%(int(id)))
	if type(result) == type(""):
		print result

	print "Cycle %d is now closed."%(int(id))
	mydb.Close()
#end closeCycle


def addCycle(process, live):
	mydb = db.db()
	mydb.Connect()
	
	# ( id, start_date, process_date, live_date, processed (N,Y))
	result = mydb.Command('''INSERT INTO ReleaseAutomation.release_cycle (process_date,live_date,processed,closed,async) VALUES ("%s", "%s", "N", "N", "N")'''%(process, live)) 
	if type(result) == type(""):
		print result

	result = mydb.Command('''SELECT LAST_INSERT_ID()''')
	if not result:
		print "Error getting id"
	
	tmp = result[0]
	id = tmp['LAST_INSERT_ID()']

	print "ADDED cycle:"
	printTable([{'id':id, 'process_date':process, 'live_date':live}])

#end addCycle


def showCompleted():
	mydb = db.db()
	mydb.Connect()
	
	result = mydb.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE processed="Y"''')

	if result:
		print "COMPLETED Cycles:"
		printTable(result)
	mydb.Close()
#end showCompleted


def showPending():
	mydb = db.db()
	mydb.Connect()
	result = mydb.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE processed="N"''')
	if result:
		print "PENDING Cycles:"
		printTable(result)
	mydb.Close()
#end showPending


def showList(cycle):
	mydb = db.db()
	mydb.Connect()
	result = mydb.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(int(cycle)))
	if not result:
		print "Cant Find Cycle:%s"%(cycle)
		mydb.Close()
		sys.exit(1)

	result = mydb.Command('''SELECT * FROM ReleaseAutomation.merged WHERE release_cycle_id=%d'''%(int(cycle)))
	if result:
		print "PACKAGES in Cycle:"
		print "----------------------------------------------------------------------------------"
		print "|   ID   |      NAME      |  SEVERITY  |   STATE   |  STATE DATE  |    PRODUCT   |"
		print "----------------------------------------------------------------------------------"
		for x in result:
			id = str(x['id'])
			name = x['name']
			severity = x['severity']
			state = x['state']
			action_date = str(x['action_date'])
			product_id = int(x['products_id'])
			ret = mydb.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(product_id))
			if not ret:
				print "Can't find product id %d"%(product_id)
				mydb.Close()
				return
			#else
			product_map = ret[0]
			product = product_map['edition']+" "+product_map['version']

			print '''|%8s|%16s|%12s|%11s|%14s|%14s|'''%(id, name, severity, state, action_date, product) 
		print "----------------------------------------------------------------------------------"
	mydb.Close()
#end showList



def finalizeCycle(cycle_id):
	mydb = db.db()
	mydb.Connect()

	result = mydb.Command('''UPDATE ReleaseAutomation.release_cycle SET processed="Y" WHERE id=%d'''%(int(cycle_id)))

	mydb.Close()
#end finalizeCycle



def usage():
	print "Usage: processCycle.py <command>"
	print "\nCommands:\n"
	print "completed          - list all completed cycles"
	print "pending            - list all unprocessed release cycles"
	print "list <cycle_id>    - list all updates for a given cycle_id"
	print "unclosed           - show all open cycles"
	print "close <cycle_id>   - close the given cycle_id so that no new"
	print "                     request can go into it."
	print "add <process_date> <live_date>"
	print "                    - add a new cycle. process_date is the"
	print "                      1rst day request will be taken."
	print "                      live_date is the day the requests are"
	print "                      expected to be on the zone. Date format"
	print "                      should be YYYY-MM-DD"
	print "finalize <cycle_id> - manually marks the cycle as processed."

#end usage

def main(argv):
	if len(argv) < 2 or len(argv) > 4:
		usage()
		sys.exit(1)
	
	if argv[1].find("help") != -1:
		usage()
		sys.exit(0)
	
	#process commands
	if argv[1] == "completed":
		showCompleted()
		sys.exit(0)
	elif argv[1] == "pending":
		showPending()
		sys.exit(0)
	elif argv[1] == "list":
		if len(argv) == 3:
			showList(argv[2])
			sys.exit(0)
		else:
			print "The 'list' command requires 1 argument"
			sys.exit(1)
	elif argv[1] == "unclosed":
		if len(argv) == 2:
			unclosedCycles()
			sys.exit(0)
		else:
			print "The 'unclosed' command does not accept arguments"
			sys.exit(1)
	elif argv[1] == "close":
		if len(argv) == 3:
			closeCycle(argv[2])
			sys.exit(0)
		else:
			print "The 'close' command requires 1 argument"
			sys.exit(1)
	elif argv[1] == "add":
		if len(argv) == 4:
			addCycle(argv[2], argv[3])
			sys.exit(0)
		else:
			print "The 'add' command requires 2 arguments"
			sys.exit(1)
	elif argv[1] == "finalize":
		if len(argv) == 3:
			finalizeCycle(argv[2])
			sys.exit(0)
		else:
			print "The 'finalize' command requires 1 argument"
			sys.exit(1)
	else:
		usage()
		sys.exit(1)

#end main

if __name__ == "__main__":
        main(sys.argv)
        sys.exit(1)


