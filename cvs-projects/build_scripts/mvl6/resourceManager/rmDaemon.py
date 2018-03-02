#!/usr/bin/python

#Pyro stuff
import Pyro.core
#Standard Libs
import os, sys, time, random, threading, string, traceback, copy
#Resource Manager Specific Libs
import resourceQueue, resourceLog, priorityList, resourceControl
from resourceLib import *
from resourceError import ResourceError

MODULETEST = 0

Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1	

class ResourceInterface(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		resourceLog.logInfo('Initializing resource manager....')
		self.lock = threading.Lock() #one lock, one love
		#We load the resource pool into memory using pickle, as before
		self.activePool = ResourcePool()
		self.activePool.initResourcePool()
		resourceQueue.initQueue() #setup the datastructures for use
		priorityList.priorityListInit()
		self.controlThrd = threading.Thread(target=resourceControl.controller)
		self.controlThrd.start()	
		resourceLog.logInfo('Init Complete!')

	#Code ripped off from original RM, file locking has been changed to python semaphores.
	def getResource(self, buildTag, buildId, resourceType, extraText):
		#We don't need to init in this function, do it in the constructor.  
		#change all the locks to use the class lock
		#this locking may not work, we might have to use the pyro built in locking mechanism, but i dont' trust it, we'll see

		#Remove This, fix the queue crap
		if MODULETEST:
			print "I'm waiting for lock for init for %s"%(resourceType)
		self.lock.acquire()
		if MODULETEST:
			print "I have lock for init for %s"%(resourceType)
		try: #if any of this stuff dies we must release the lock
			resourceQueue.addEntry(buildTag, buildId, resourceType)
		finally:
			if MODULETEST:
				print "Init Complete, releasing lock for %s"%(resourceType)
			self.lock.release()

        #This part stays more or less the same, what we are going to remove is the loading/unloading of various data structures
        #loop until something returns
		while(1): 
			if MODULETEST:
				print "Attemping to check out %s, waiting for lock..."%(resourceType)
			self.lock.acquire() 
            #arg is 1 for blocking, 0 for nonblocking
			#lock exceptions will propagate to the calling module, other exceptions will require cleanup
			#so we must release the lock
			try:
				if MODULETEST:
					print "Lock obtained proceeding to search for %s"%(resourceType)
				if resourceQueue.checkEntry(buildId, resourceType):  #Is it our turn to go?
					resource = self.activePool.tagResource(resourceType, buildTag, buildId, extraText)
					if resource == "error":
						#print "Error: requested resource %s doesn't exist"%(resourceType)
						resourceQueue.removeEntry(buildId, resourceType)
						resourceLog.logErr('Error Checking out: %s'%resourceType)
						self.lock.release()
						return resource #This will return the string "error" if we decide to look for it in the calling script
					elif resource: #Is the resource Available?
						resourceQueue.removeEntry(buildId, resourceType)
						if MODULETEST:
							print "I have %s, leaving..."%(resourceType)
						resourceLog.logInfo('Checking out: %s'%resource)
						self.lock.release()
						return resource
					else:  #No Resource
						if MODULETEST:
							print "Resource %s not available, going to sleep..."%(resourceType)
						self.lock.release()
						time.sleep(random.randint(1,10)) #once the paperwork is done, sleep for a random number of seconds

				else: #Not our turn
					if MODULETEST:
						print "Wasn't our turn in the Queue, releasing lock for %s"%(resourceType)
					self.lock.release()
					time.sleep(random.randint(1,10))
			except:
				self.lock.release()
				traceback.print_exc()
				raise ResourceError, "Fatal Resource Manager Error"

	def releaseResource(self, resourceName):
		if MODULETEST:
			print "awaiting lock to release %s"%(resourceName)
		self.lock.acquire()
		try:
			self.activePool.returnResource(resourceName)
			resourceLog.logInfo('Checking in: %s'%resourceName)
			if MODULETEST:
				print "resource %s returning, releasing lock"%(resourceName)
		finally:
			self.lock.release()
		return

## Special Methods
	def getPool(self):
		self.lock.acquire()
		pool = copy.deepcopy(self.activePool)
		self.lock.release()
		return pool
	def getQueue(self):
		self.lock.acquire()
		queue = copy.deepcopy(resourceQueue.masterQueue)
		self.lock.release()
		return queue

## User Interface Methods
	def setPriority(self, buildId, priority):
		self.lock.acquire()
		priorityList.setPriority(buildId, priority)
		resourceQueue.bumpPriority(buildId, priority)
		self.lock.release()


	def manualCheckOut(self, requestedResource, notes, searchMode):
		self.lock.acquire()
		try:
			resource = self.activePool.tagResource(requestedResource,"Manual Checkout","Manual Checkout", notes, searchMode)
		finally:
			self.lock.release()
		return resource

	def manualCheckIn(self, resource):
		self.lock.acquire()
		self.activePool.returnResource(resource)
		self.lock.release()


	def addToPool(self, resourceName, typeList, priority, useType):
	#two things need to happen for this bad boy.  We can create a new pool object, add it and store it.  This 
	#is so when we restart the server everything is happen.
	#We also need to add it to the running pool, so we'll do that using the objects activePool object
		#Add to pool.rm
		tempPool = ResourcePool()
		tempPool.initResourcePool()
		tempPool.addResource(resourceName, typeList, priority, useType)
		tempPool.storeResourcePool()
		#Add to running pool
		self.lock.acquire()
		retval = self.activePool.addResource(resourceName, typeList, priority, useType)
		self.lock.release()
		return retval

	def delFromPool(self, resourceName):
		tempPool = ResourcePool()
		tempPool.initResourcePool()
		tempPool.delResource(resourceName)
		tempPool.storeResourcePool()
		self.lock.acquire()
		retval = self.activePool.delResource(resourceName)
		self.lock.release()
		return retval
	
	def getResourceStatus(self,toFind):
		self.lock.acquire()
		status = self.activePool.getResourceStatus(toFind,1)
		self.lock.release()
		return status

	def poolStatus(self):
		self.lock.acquire()
		results = self.activePool.getPoolStatus()
		self.lock.release()
		return results

	def resourceQuery(self, searchData, searchMode):
		self.lock.acquire()
		results = self.activePool.resourceQuery(searchData, searchMode)
		self.lock.release()
		return results

	def getQueueStatus(self):
		self.lock.acquire()
		normal = resourceQueue.printQueue(priorityList.NORMAL)
		high = resourceQueue.printQueue(priorityList.HIGH)
		critical = resourceQueue.printQueue(priorityList.CRITICAL)
		self.lock.release()
		return normal, high, critical


	def removeFromQueue(self, buildId):
		self.lock.acquire()
		resourceQueue.removeEntry(buildId)
		self.lock.release()

	def dumpStateToFile(self):
		self.activePool.dumpStateToFile()

	def loadStateFromFile(self):
		self.activePool.loadStateFromFile()

#This guy is only called from the command line
def main():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon()

	daemon.connect(ResourceInterface(), 'resource_manager')
	daemon.requestLoop()


if __name__ == "__main__":
	main()


