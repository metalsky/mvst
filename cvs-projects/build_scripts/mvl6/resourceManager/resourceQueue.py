#!/usr/bin/python



#########################################################
#             resourceQueue.py                          #
#                                                       #
#  All objects to the resource manager queue            #
#                                                       #
#                                                       #
#########################################################

import sys, os, cPickle, string, time, traceback
from types import *
from priorityList import *
from resourceError import ResourceError

TEST = 0

class QueueEntry:
  def __init__(self, buildTag, buildId, timeOrig, resourceType):
    for var in (buildTag, buildId, resourceType, timeOrig):
      if type(var) != StringType:
        raise TypeError, "Non-string types added to QueueEntry Object"
    self.buildTag = buildTag
    self.buildId  = buildId
    self.timeOrig = timeOrig
    self.timeLast = timeOrig
    self.resourceType = resourceType



#####################################
#       initQueue()
#
# private function that loads queue from file into memory via cPickle
#
#####################################
#def initQueue():
#  global masterQueue
#  try:
#    queueFPtr = open("/home/build/bin/resourceManager/queue.rm","r")
#  except IOError:
#    raise ResourceError,"Error Opening Queue for Reading"
#  except:
#    traceback.print_exc()
#    raise ResourceError, "Unknown Error Opening Queue"
def initQueue():
  global masterQueue #empty file, set to empty list for construction
  masterQueue = [[],[],[]]
  #there exist 3 blank lists in the master list, these list refer to various priorities 0, 1, and 2
  return 

#####################################
#       storeQueue()
#
# function that stores queue to file via cPickle
#
#####################################
def storeQueue():
  global masterQueue
  try:
    queueFPtr = open("/home/build/bin/resourceManager/queue.rm","w")
    cPickle.dump(masterQueue, queueFPtr, cPickle.HIGHEST_PROTOCOL)
  except PicklingError:  #exit for now, we should probably make these send an email versus printing a message
    sys.stderr.write("Error Pickling Queue\n")
    raise
  except IOError:
    raise ResourceError, "Error Opening Queue for Writing"
  except:
    traceback.print_exc()
    raise ResourceError, "Unknown Error Storing Queue"
  queueFPtr.close()
  masterQueue = None #must reset the list
  return


############################
#	now()
#
#  returns a string with the current date/time
#
############################
def now():
  return time.strftime("%m/%d/%Y - %I:%M %p") 

#####################################
#   checkEntry(buildTag, buildId, resourceType)
#
#  Checks to see if a process has permission to proceed.  Checks for the existence of more important
#  processes before hand so that priority is maintained
#####################################
def checkEntry(buildId, resourceType):
  #There are three FIFO Queues all directly related to a specific priority level
  #Things that are not highest priority always give up if a higher priority action exists
  global masterQueue, TEST
  if type(buildId) != StringType or type(resourceType) != StringType:
    raise ResourceError, "Non-string type passed to checkEntry"  
  #We don't want to allow the build to tell us its priority, so we will check a priority list
  priority = getPriority(buildId) 

  #Check to see if we are the first spot in our queue
  if(masterQueue[priority][0].buildId != buildId): #Not the front of FIFO
    if TEST == 2:
      print "Not Front of FIFO, denying..."
    return 0 #Exit Failure

  i = 0
  while( i <= priority ):
    #No one more important, our turn - Exit Success, place on end of FIFO for next process' turn
    if(i == priority): 
      masterQueue[priority][0].timeLast = now() #show time last attempt for resource
      tempEntry = masterQueue[priority].pop(0) #Remove from the front of this queue
      masterQueue[priority].append(tempEntry) #Place on the end of the FIFO
      if TEST == 2:
        print "Nothing more important granting..."
      return 1 #we're done with the queue
    #Higher Priority is empty move to next queue
    elif( i < priority and len(masterQueue[i]) == 0):
      i = i + 1
    #Higher priority items exist, we have to check and see if anyone is waiting for the resource we want
    elif( i < priority and len(masterQueue[i]) > 0):
      for queueEntry in masterQueue[i]:
        if TEST == 2:
          print "Examining: %s"%(queueEntry.buildTag)  
        if queueEntry.resourceType == resourceType:
          #Someone more important wants this resource, we have to take a backseat
          masterQueue[priority][0].timeLast = now() 
          tempEntry = masterQueue[priority].pop(0) #Remove from the front of this queue
          masterQueue[priority].append(tempEntry) #Place on the end of the FIFO
          if TEST == 2:
            print "Examining priority %s"%(i)
            print "%s %s"%(queueEntry.resourceType, resourceType)
            print "High priority Item Exists, denying..."
          return 0
      #If we survive the for loop, go to the next priority queue
      i = i + 1
    #There is some serious problem, we shouldn't end up here
    else:
      raise ResourceError, "Unhandled case in checkEntry"
  #If we ever get here, there's a serious problem
  raise ResourceError, "Queue broke out of main control loop"
  


#######################################
#    addEntry()
#
# Adds QueueEntry object to end of its priority FIFO 
#
########################################
def addEntry(buildTag, buildId, resourceType):
  global masterQueue
  priority = getPriority(buildId)
  masterQueue[priority].append(QueueEntry(buildTag,buildId,now(),resourceType))
  return  

#######################################
#    bumpPriority(string buildId, int priority)
#
# Find all currently existing existences of a build tag in a queue and raise the priority
#
#######################################

def bumpPriority(buildId, priority):
  global masterQueue
  global NORMAL, CRITICAL
  #We're going to go through all priority queues and move all entries to the appropriate queue
  i = NORMAL
  while ( i >= CRITICAL ):
    if i == priority: #We're not going to reset anything in our own priority
      i = i - 1
    elif len(masterQueue[i]) == 0: #Stuff may need to be moved, check, pop and then push to the appropriate list
      i = i - 1
    else:  
      j = 0
      while(j < len(masterQueue[i])):
        entry = masterQueue[i][j]
        if entry.buildId == buildId: #we have a match, move this to appropriate priority
           if TEST == 2:
             print "Moving %s from %s to %s"%(entry.buildId, i, priority)
           masterQueue[priority].append(entry) #add to the priority we want
           masterQueue[i].remove(entry) #remove from old priority
           #notice we remove an entry, we do not increment j
        else:
          j = j + 1
      i = i - 1 #we broke out of the while loop, we're done checking this queue, move on
  


####################################
#      removeEntry(string buildId, string resourceType)
#
#  find entry and remove it
#
#
###################################
def removeEntry(buildId, resourceType=None):
  global masterQueue
  #We have to find out the priority of this build so we know which queue to look in
  priority = getPriority(buildId)
  i = 0
  if (len(masterQueue[priority]) == 0):
    #print "Info: Nothing to remove for priority %s"%(priority)
    return
  if resourceType == None:
    while(i < len(masterQueue[priority])):
      if( masterQueue[priority][i].buildId == buildId):
        del masterQueue[priority][i]
      else:
        i = i + 1
  else:
    while(i < len(masterQueue[priority])):
      if( masterQueue[priority][i].buildId == buildId and masterQueue[priority][i].resourceType == resourceType):
        del masterQueue[priority][i]
        return
      else:
        i = i + 1

  return


############################
#    printQueue(priority)
#
# prints our the queue for a specific priority, priority -1 will print all queues
# I still need to add pretty formatting for this function
###########################
def printQueue(priority):
  i = 0
  results = []
  if(len(masterQueue[priority]) > 0):
    for entry in masterQueue[priority]:
      tempResults = []
      tempResults.append("Build Tag:       %s"%(entry.buildTag))
      tempResults.append("Build Id:        %s"%(entry.buildId))
      tempResults.append("Waiting for:     %s"%(entry.resourceType))
      tempResults.append("Time of Request: %s"%(entry.timeOrig))
      tempResults.append("Last Attempt   : %s\n"%(entry.timeLast))
      results.append(tempResults)
  else:
    tempResults = []
    tempResults.append("Empty Queue\n")
    results.append(tempResults)
  return results


def main():
  print "There is no manual operation of this module."
  global masterQueue
  if TEST:
    initQueue()
    addEntry("fb101234_0500112","0500112","node")
    addEntry("ftwo10124_05003672","05003672","node")
    addEntry("makena101234_0567112","0567112","node-2")
    addEntry("blah101234_0501782","0501782","node")
    addEntry("yeppers101234_0598612","0598612","cygwin")
 


    print "Normal:"
    printQueue(NORMAL)
    print "High:"
    printQueue(HIGH)
    print "Critical:"
    printQueue(CRITICAL)

    if not checkEntry("0500112","node"):
      print "Priority Test: PASS"
    else:
      print "Priority Test: FAIL"

    if( masterQueue[NORMAL][-1].buildId == "0500112" ):
      print "Queue Rotation: PASS"
    else:
      print "Queue Rotation: FAIL"

    if not checkEntry("0567112","node"):
      print "Not Front of Queue Test: PASS"
    else:
      print "Not Front of Queue Test: FAIL"

    #In order to rotate the FIFO one more time
    checkEntry("05003672","node")
  
    if checkEntry("0567112","node-2"):
      print "Front of Queue/Priority: PASS"
    else:
      print "Front of Queue/Priority: FAIL"

    removeEntry("0567112","node-2")
    printQueue(NORMAL)
    #storeQueue()


if __name__ == "__main__":
  main()



