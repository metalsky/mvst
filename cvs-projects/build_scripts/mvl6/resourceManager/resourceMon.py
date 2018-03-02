#!/usr/bin/python

import os, sys, re, datetime
import Pyro.core

import resourceLog,config
from resourceLib import *
from priorityList import NORMAL

HOUR = "hour"
MIN = "min"

Pyro.core.initClient(0)
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1


#Helper functions for checkPassive
#Format of timeStamp: MM/DD/YYYY - HH:MM AM/PM
def getAge(timeStamp, type):
	resourceLog.logDebug('Time Stamp is: %s'%timeStamp)
	parse = re.match(r'(\d\d)/(\d\d)/(\d\d\d\d) - (\d\d):(\d\d) (\w\w)', timeStamp)
	month,day,year,hours,minutes,pm = int(parse.group(1)),int(parse.group(2)),int(parse.group(3)),int(parse.group(4)), int(parse.group(5)), parse.group(6)
	if pm == "PM" and hours != 12: 
		hours += 12
#Midnight bug
	if pm == "AM" and hours == 12:
		hours = 0

	outTime = datetime.datetime(year, month, day, hours, minutes)
	currentTime = datetime.datetime.today()
	resourceLog.logDebug('Outtime: %s Today: %s'%(outTime, currentTime))
	diff = currentTime - outTime

	if type == MIN:
		output = diff.seconds/60
	if type == HOUR:
		output = diff.seconds/60/60

	resourceLog.logDebug('Time difference is %s %s'%(output,type))
	return output

def getPool():
	try:
		resourceManager = Pyro.core.getProxyForURI(config.server)
		return resourceManager.getPool()
	except:
		resourceLog.logErr("Could not acquire resource pool, there may be a problem with the resource manager")
		resourceLog.logErr('%s'%traceback.format_exc())
		return None

def getQueue():
	try:
		resourceManager = Pyro.core.getProxyForURI(config.server)
		return resourceManager.getQueue()
	except:
		resourceLog.logErr("Could not acquire queue, there may be a problem with the resource manager")
		resourceLog.logErr('%s'%traceback.format_exc())
		return None

####################################
#	checkPassive()
#
#  This function acquires the resource pool and then checks the age of ANY checked out passive resource
#  Critical messages are sent to the logging facility if something looks to be old
#
####################################
def checkPassive():
	reload(config) #so we can throttle the times based on our needs.
	pool = getPool()
	if pool == None:
		return
	resourceList = pool.resourceList #its not a list but a dict, oops
	passiveCnt = 0
	errorCnt = 0
	for resource in resourceList.keys():
		if resourceList[resource].useFlag == USED and resourceList[resource].resourceUseType == PASSIVE:
			passiveCnt += 1
			resourceLog.logDebug('Trying... %s: %s'%(resourceList[resource].resourceName, resourceList[resource].useTime))
			resourceLog.logDebug('Passive Timeout set to: %s'%config.passiveWarn)
			if getAge(resourceList[resource].useTime, MIN) >= config.passiveWarn:
				errorCnt += 1
				resourceLog.logCrit("%s has been checked out a long time"%(resourceList[resource].resourceName))
			

	resourceLog.logInfo("%s Errors found out of %s checked out passive resources"%(errorCnt,passiveCnt))	
	return

#####################################
#          checkQueue()
#
#  This function will get the head of all current queues and examine the last time they were checked.  If this time
#  is over the time specified in the configuration then a critical message will be sent to the logger.
#
####################################
def checkQueue():
	queue = getQueue()
	if queue == None:
		return
	#Normal always has the highest number
	for priority in range(NORMAL+1): #normal is 2, we need 3 so that range produces 0-2
		if len (queue[priority]):
			if getAge(queue[priority][0].timeLast,MIN) > config.maxQueueAge: 
				resourceLog.logCrit("Queue rotation is taking a long time, check build: %s"%queue[priority][0].buildTag)
	resourceLog.logDebug('Queue rotation normal')

def main():
	sys.stderr.write('No manual execution of this module\n')
	sys.exit(1)

if __name__=="__main__":
	main()


