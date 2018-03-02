#!/usr/bin/python

TEST = 0
DEBUG = 0 #prints debug statements if on, can change while system is running

notifyEmail = 'build@mvista.com'
mailServer = 'mail.sh.mvista.com'
watchInterval = 300 #Inverval in seconds that the controller thread will process maintenance tasks
passiveWarn = 300 #Time in minutes a passive resource can be checked out before a warning message it sent
maxQueueAge = 5 # Time in minutes an entry should be allowed to stay at the head of the queue without checking

if TEST:
	server = "PYROLOC://glue:7766/resource_manager"
	pool = "/home/cvanarsdall/build_scripts/rm/pool.rm"
	saveState = "/home/cvanarsdall/build_scripes/rm/pickledPool.rm"
else:
	server = "PYROLOC://resource:7766/resource_manager"
	pool = "/home/build/bin/resourceManager/pool.rm"
	saveState = "/home/build/bin/resourceManager/pickledPool.rm"



