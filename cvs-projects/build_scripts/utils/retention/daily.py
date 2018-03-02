#!/usr/bin/env python
import sys, os, DBInteraction, moveDirs, cleanup,lt_os
dbi = DBInteraction


if __name__ in ['__main__']:
	dbi.testDB()
	#Sync DB with Bugz
	dbi.removeAllBugz()
	dbi.addBugzToDB()
	dbi.repopulateDB()

	#Write the kept builds to /tmp/KEEPERS for legacy findOldDirs.py script.
	dbi.dumpAllKeepers()

	#Run legacy script!
	lt_os.system('./findOldDirs.py > oldDirectories.txt', True)
	lt_os.system('./findDirs.py --path /mvista/dev_area/foundation >> oldDirectories.txt', True)

	moveDirs.main()	
	cleanup.cleanupLogs()
	cleanup.cleanupDB()
