#!/usr/bin/python

import sys
import config
import error

rm_path = config.getResourceManager()
error.sysDebug("Looking in '"+rm_path+"' for the resourceManager")
sys.path.append(rm_path)

try:
	from resourceManager import getResource, releaseResource
except:
	error.fatalError("Can't find resourceManager in path: "+sys.path[-1])


####abstraction.py####
#This file represents all functions that exist within the framework
#That users will want to change to suit their specific needs



#This is a function called by graceful exit.  Different resource management tools
#will require different things to clean up
def cleanupResources():
	error.debug("Cleaning resource manager")


#These are two wrappers to provide a layer of abstraction for the resource manager.  
#If this goes to open source these two functions will be empty so that people can put what they want
#for us however, we'll just pass the requested resource, these functions will then do stuff
#specific to our system.

#The argsTuple will basically contain everything that is available at the time the wrapper is called.
#The format will be as follows


def getResourceWrapper(task, dataObj):
	error.debug("Task: %s is checking out resource: %s"%(task.name,task.forkObj.remoteType))	
	resource = getResource(dataObj.shared.getVar('TAG'), dataObj.shared.getVar('ID'),task.forkObj.remoteType, "Checked out by %s"%(task.name))
	dataObj.local.putVar("resource",resource)
	return resource


def releaseResourceWrapper(task, dataObj, resource):
	error.debug("Task: %s is releasing resource: %s"%(task.name,resource))
	releaseResource(resource)
	return

#This framework is designed to work remotely with any given resource manager provided it meets an interface.
#Remote execution at present is handled using ssh to communicate with various resources in the cluster
#The functions below provide an abstraction so that we can more easily change the technology used.

#Later versions of the Execution Framework will also have the ability to execute entire tasks/tasklists remotely in addition
#to individual remote commands

WAIT = 0
NO_WAIT = 1

def rexec(mode, remote, command, user=None):
	if user != None:
		prepend = user +'@'
	else:
		prepend = ''

	if mode == NO_WAIT and user == None:
		os.system('ssh %s%s %s &'%(prepend, remote, command))
	elif mode == WAIT and user == None:
		os.system('ssh %s%s %s'%(prepend, remote, command))
	else:
		raise ValueError, "rexec recieved invalid mode"


if __name__=="__main__":
	print "No manual execution of this module"
	sys.exit(1)

