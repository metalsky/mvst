#!/usr/bin/python

###############################################
#               resourceManager.py	      #
#					      #
# Main script of the build system resource    #
# management system.  This script will remain #
# small, only used to handle the main control #
# flow of the system.			      #
#					      #
###############################################


import os, sys, time, random, Pyro.core, threading, string, traceback #standard python libraries
import rmClient, resourceLog

Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

### Resouce Checkout Related Functions ###

#################################
#   getResource(string buildTag, string buildId, string resourceType, string extraText)
#
#  blocks until resource becomes available
#  updates resource pool
#  returns with available resource
#################################
def getResource(buildTag, buildId, resourceType, extraText):
  resource = rmClient.remoteResourceGet(buildTag, buildId, resourceType, extraText)
  return resource

###################################
#   releaseResource(string resourceName):
#
#  blocks until resource can be returned 
#  
#
##################################
def releaseResource(resourceName):
  rmClient.remoteResourceRelease(resourceName)


#################################
#     getResourceWrapper(tuple args)
#
#  This function wraps getResource so we can call it in threads for maintenance mode
#  args is going to be a tuple passed in by the thread caller
#
#################################
def _getResourceWrapper(buildTag,buildId,resourceType,notes):
  resource = getResource(buildTag, buildId, resourceType, notes)
  print "I have %s"%(resource)
  return


#############################
#  releaseResourceWrapper (tuple args)
#
# Wraps releaseResource for use in threading
#
#############################
def _releaseResourceWrapper(args):
  releaseResource(args)
  print "I have released %s"%(args)

############################
#    maintenanceMode()
#
#  Attempts to Check out ALL build resources
#  ALL resources are entered with a CRITICAL priority so that no builds take any
#  Resources
#
###########################
def _maintenanceMode(type="all"):
  os.system('clear')
  solaris = 0
  cygwin = 0
  node = 0
  if type == "all":
    solaris = 1
    cygwin = 1
    node = 1
  elif type == "solaris":
    solaris = 1
  elif type == "cygwin":
    cygwin = 1
  elif type == "node":
    node = 1
  else:
    print "Invalid Type: all cygwin solaris node"
    sys.exit(1)
  print "Getting resource list..."
#  lock.getLock(1)
#  activePool = ResourcePool()
#  activePool.initResourcePool()
#  resourceList = activePool.getResourceList()
#  activePool.cleanResourcePool()
#  lock.releaseLock()
  buildTag = "Maintenance"
  notes = "This resource has been checked out for maitenance"
  #We have the list of resources, now we're going to do some threading
  threadList = []
  print "Getting List of resources..."

  #We need to find out how many machines of each type we have.  We can't take advantage of the priority
  #scheme to reserve these nodes if we ask for them all by name specifically
  nodeCnt = 0
  solarisCnt = 0
  cygwinCnt = 0
  i = 0
  maintenanceResources = []
  while(i < len(resourceList)):
    if string.find(resourceList[i],"node-") >= 0 and node:
      nodeCnt = nodeCnt + 1
      maintenanceResources.append(resourceList[i])
      i = i + 1
    elif string.find(resourceList[i],"solaris-") >= 0 and solaris:
      solarisCnt = solarisCnt + 1
      maintenanceResources.append(resourceList[i])
      i = i + 1
    elif string.find(resourceList[i],"cygwin-") >= 0 and cygwin:
      cygwinCnt = cygwinCnt + 1
      maintenanceResources.append(resourceList[i])
      i = i + 1
    else:
      i = i + 1 #Didn't have to write this but it spells out everything we're interested in


  #Setup the threads
  if node:
    i = 0
    while(i < nodeCnt - 1): 
      threadList.append(threading.Thread(target=_getResourceWrapper,args=(buildTag,buildTag,"node",notes)))
      i = i + 1

  if solaris:
    i = 0
    while(i < solarisCnt - 1): 
      threadList.append(threading.Thread(target=_getResourceWrapper,args=(buildTag,buildTag,"solaris",notes)))
      i = i + 1

  if cygwin:
    i = 0
    while(i < cygwinCnt - 1): 
      threadList.append(threading.Thread(target=_getResourceWrapper,args=(buildTag,buildTag,"cygwin",notes)))
      i = i + 1
  print "Checking out resources..."
  #Launch threads and wait for them to all return
  for thread in threadList:
    thread.start()

  for thread in threadList:
    thread.join() #We must block until all of the resources are checked out.

  print "Complete, I have all resources"
  raw_input("Press Enter to release resources")
  threadList = []
  print "Returning resources...."
  for resourceName in maintenanceResources:
    threadList.append(threading.Thread(target=_releaseResourceWrapper, args=(resourceName,)))
  
  for thread in threadList:
    thread.start()

  for thread in threadList:
    thread.join()

  print "I've released all the resources"
  raw_input("Press Enter to Continue")
  os.system('clear')

###Functions for the direct User interface###

def main(argv=sys.argv):
  if len(argv) > 1:
    if argv[1] == "maintenance":
      _maintenanceMode(argv[2])
      sys.exit(1)
    if argv[1] == "q":  #This is a hack, we need better printing ability, use something like ncurses
      import resourceUI
      resourceUI.getQueueStatus()
      sys.exit(1)
  import resourceUI #all the user interface/manual operation stuff

  os.system('clear')  
  print "Welcome to the Build Resource Manager(tm) Interactive Prompt"
  print "What would you like to do today?\n\n\n" 

  #This is it, everything else is in resourceUI.py
  while(1):
    choice = resourceUI.printMainMenu()
    while (choice < 1 or choice > 9):
      os.system('clear')
      print "-----Invalid Selection-----"
      print "Please Choose one of the following:"
      choice = resourceUI.printMainMenu()
    if choice == 9:
      print "Goodbye"
      sys.exit(1)
    else:
      resourceUI.mainOp[choice - 1]()  #yes, this is a function call



if __name__ == "__main__":
  main()




