#!/usr/bin/python

###########################################################
#		    priorityList			  #
#							  #
#	A list of builds that have priority over	  #
#	other builds.  Other processes will check	  #
#	this list when they need to know the		  #
#	priority of a particular build			  #
#							  #
#							  #
###########################################################

import sys, os, cPickle, traceback
from resourceError import ResourceError
#globals

masterPriorityList = None
TEST = 0 #set to print test output

#All scripts have access to these priorities, they need to use the variable names instead of numbers
NORMAL = 2
HIGH = 1
CRITICAL = 0



class priorityEntry:
  def __init__(self, buildTag, priority):
    self.buildTag = buildTag
    self.priority = priority

def priorityListInit():
  global masterPriorityList
  try:
    listFPtr = open("/home/build/bin/resourceManager/priority.rm","r")
  except IOError:
    raise ResourceError, "Error Opening Priority List for Reading"
  except:
    traceback.print_exc()
    raise ResourceError, "Unknown Error Opening Priority List"
  try:
    pickledList = cPickle.load(listFPtr)
  except EOFError:
    masterPriorityList = [] #empty file, set to empty list for construction
    listFPtr.close()
    return 0 #return value so we quickly know if there's anything to look at
  except:
    traceback.print_exc()
    raise ResourceError, "Unknown Error Loading Priority List"
  listFPtr.close()
  masterPriorityList = pickledList
  return 1



def priorityListStore():
  global masterPriorityList
  try:
    listFPtr = open("/home/build/bin/resourceManager/priority.rm","w")
    cPickle.dump(masterPriorityList, listFPtr, cPickle.HIGHEST_PROTOCOL)
  except PicklingError:  #exit for now, we should probably make these send an email versus printing a message
    raise ResourceError, "Error Pickling Priority List"
  except IOError:
    raise ResourceError, "Error Opening Priority List for Writing"
  except:
    traceback.print_exc()
    raise ResourceError, "Unknown Error Storing Priority List"
  listFPtr.close()
  return

###############################
#   getPriority(string buildtag)
#
# checks the list and returns the priority of "buildTag"
#
###############################
def getPriority(buildTag):
  if len(masterPriorityList) < 1: #Empty List, everything has normal priority
    return NORMAL

  #search the list
  for listEntry in masterPriorityList:
    if listEntry.buildTag == buildTag:
      return listEntry.priority

  return NORMAL

################################
#   setPriority(buildTag, priority
#
#  adds or replaces an entry in the list
#  if low priority, then entry removed from list
#
#  Valid priorities are: 0 - Critical, 1 - High, 2 - Normal 
# 
################################
def setPriority(buildTag, priority):
  global masterPriorityList
  #The situation in which someone uses this function horribly wrong
  if priority < CRITICAL or priority > NORMAL:
    print "You've asked to set an unsupported priority"
    sys.exit(1)

  if (priority == NORMAL):  #This is the case in which we would remove an entry from the priority list
    if not (priorityListInit()):
      return #nothing in the list, nothing to remove
    else: #search and destroy
      for entry in masterPriorityList:  #We can't just use list remove because our list contains objects not matchable entries
        if entry.buildTag == buildTag:
          masterPriorityList.remove(entry)
          priorityListStore()
          if TEST:
            print "removing from priority list"
          return

  else:
    if not (priorityListInit()): #Empty List, everything has normal priority
      masterPriorityList.append(priorityEntry(buildTag, priority))
      priorityListStore()
      if TEST:
        print "adding to priority list"
      return
    else:
      for entry in masterPriorityList:
        if entry.buildTag == buildTag:
          entry.priority = priority
          priorityListStore()
          if TEST:
            print "Changing Priority"
          return
      #Fell out of loop without finding anything, just add to the end of the list
      masterPriorityList.append(priorityEntry(buildTag, priority))
      priorityListStore()
      if TEST:
        print "adding to priority list"
      return

def main():
  print "You shouldn't be running this script"
  print "This script is intended as a module for the resource manager."
  print "Manual operation exists for testing only"
  print ""

  if TEST:
    print "NORMAL: %s"%(NORMAL)
    print "HIGH: %s"%(HIGH)
    print "CRITICAL: %s"%(CRITICAL)

    print "Checking priority, should be NORMAL.... ",
    priority = getPriority("ftwo123124_123124")
    if priority != NORMAL:
      print "ERROR"
    else:
      print "SUCCESS"

    setPriority("ftwo123124_123124", HIGH)
    print "Checking priority, should be HIGH.... ",
    priority = getPriority("ftwo123124_123124")
    if priority != HIGH:
      print "ERROR"
    else:
      print "SUCCESS"


    print "Checking priority, should be CRITICAL.... ",
    setPriority("ftwo123124_123124", CRITICAL)
    priority = getPriority("ftwo123124_123124")
    if priority != CRITICAL:
      print "ERROR"
    else:
      print "SUCCESS"

    print "Checking priority, should be NORMAL.... ",
    setPriority("ftwo123124_123124", NORMAL)
    priority = getPriority("ftwo123124_123124")
    if priority != NORMAL:
      print "ERROR"
    else:
      print "SUCCESS"

    print "Checking priority, should print NORMAL.... ",
    setPriority("ftwo123124_123124", NORMAL)
    priority = getPriority("ftwo123124_123124")
    if priority != NORMAL:
      print "ERROR"
    else:
      print "SUCCESS"




if __name__ == "__main__":
  main()


