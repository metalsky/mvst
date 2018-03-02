#!/usr/bin/python
import sys,os, DBInteraction, moveDirs, cleanup,lt_os
from sendEmail import sendEmail
dbi = DBInteraction

def cls():
	os.system('clear')
#}

def printMainMenu():
	print """
[1] Manage Exemptions
[2] Process Builds
[3] Repopulate Database
[4] Exit
"""

	input = raw_input("Your Choice: ")

	if input == '1':
		cls()
		printExemptionsMenu()
	elif input == '2':
		cls()
		printBuildsMenu()
	elif input == '3':
		dbi.repopulateDB()
		cls()
		print '*** LIST INDICES MAY HAVE CHANGED.  CHECK IT BEFORE REMOVING EXEMPTIONS. ***'
		printMainMenu()
	elif input == '4':
		sys.exit(1)
	else:
		pass
#}

def printExemptionsMenu():

	os.system('clear')
	while True:
		print """
[1] List Current Exemptions
[2] Add an Exemption
[3] Remove an Exemption
[4] List Bugz Exemptions
[5] Back
"""

		input = raw_input("Your Choice: ")

		if input == '1':
			cls()
			for id,build in dbi.fetchKeepers():
				print '['+id+'] ' + build
		elif input == '2':
			input = raw_input("What would you like to add to the exemptions?\n")
			dbi.addKeeper(input, 'MANUAL')
			cls()
			for id,build in dbi.fetchKeepers():
				print '['+id+'] ' + build
		elif input == '3':
			input = raw_input("Enter the index of the build you would like to remove.")
			dbi.removeKeeper(input)
			cls()
			for id,build in dbi.fetchKeepers():
				print '['+id+'] ' + build
		elif input == '4':
			cls()
			for build in dbi.listBugzFromExempt():
				print build
		elif input == '5':
			cls()
			printMainMenu()
		else:
			pass	


#}

def printBuildsMenu():

	while True:
		print """
[1] Scan for old directories, saving list to oldDirectories.txt.
[2] Read directories from oldDirectories.txt and email a warning. 
[3] Move directories to /dev_area/removal
[4] Delete logs.
[5] Sync Database.
[6] Back
"""

		input = raw_input("Your Choice: ")

		if input == '1':
			cls()
			dbi.dumpAllKeepers()
			lt_os.system('./findOldDirs.py > oldDirectories.txt', True)
			lt_os.system('./findDirs.py --path /mvista/dev_area/foundation >> oldDirectories.txt', True)
			cls()
			print "Old non-exempt directories written to oldDirectories.txt"
		elif input == '2':
			cls()
			sendEmail()
			print "Email sent to build@mvista.com."
		elif input == '3':
			cls()
			moveDirs.main()
		elif input == '4':
			cleanup.cleanupLogs()

		elif input == '5':
			cleanup.cleanupDB()


		elif input == '6':
			cls()
			printMainMenu()

#}
if __name__ in ["__main__"]:
	#Gotta test to see if the DB needs flushing.
	dbi.testDB()
	#Sync DB with Bugz
	dbi.removeAllBugz()
	dbi.addBugzToDB()
	dbi.repopulateDB()
	os.system('clear')
	printMainMenu()


