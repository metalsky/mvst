#!/usr/bin/python
#Standard Library
import sys, time, traceback
from types import *
#Custom
import config, resourceMon, resourceLog

#FIXME: put this somewhere else
QUIT = 'quit'

#FIXME: need a real mechanism for sending messages to threads
def checkMsg():
	return 'happy'


#don't add anything to the controller, add stuff to be executed here
def exec_tasklist():
	tasklist=[resourceMon.checkPassive, resourceMon.checkQueue]
	for task in tasklist:
		try:
			task()
		except:
			resourceLog.logErr("Error Processing task  \n %s"%(traceback.format_exc()))

def controller():
	while 1:
		reload(config) #we'll reload each iteration so we can change things when we feel like without restarting the server
		time.sleep(config.watchInterval)
		cmd = checkMsg()
		if cmd == QUIT:
			return
		else:
			resourceLog.logInfo("Executing task list")
			exec_tasklist()
			resourceLog.logInfo("Task list complete!")


def main():
	sys.stderr.write('No manual execution of this module\n')
	sys.exit(1)



if __name__== "__main__":
	main()


