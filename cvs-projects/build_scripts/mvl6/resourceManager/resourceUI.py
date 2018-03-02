#!/usr/bin/python


#########################################################
#							#
#        		resourceUI.py			#
#							#
#							#
#	Collection of simple functions for the manual	#
#	operation of the Resource Manager		#
#							#
#							#
#########################################################
import os
import Pyro.core
import resourceLog, priorityList, config
from resourceLib import *
#ideally we'd like to use ncurses in this script for absolute neatness, maybe someday... :(

#Global resource manager object
resourceManager = Pyro.core.getProxyForURI(config.server)


def printMainMenu():
  print "1. Check out Resources"
  print "2. Check in Resources"
  print "3. Set Priority for Build"
  print "4. Manage Resource Pool"
  print "5. View Queue Status"
  print "6. Remove Build from Queue"
  print "7. Save Resource State"
  print "8. Load Resource State"
  print "9. Exit"
  try:
    choice = input("\n\nPlease Select Operation[1-9]:")
  except SyntaxError:
    choice = -1
  except NameError:
    choice = -1
  except:
    sys.stderr.write("Unknown Error in User Interface\n")
    sys.exit(1)
  return choice


#Manual Operations Run as soon as they can get a lock, assuming highest priority
def manualCheckOut():
  while(1):
    os.system('clear')
    print "This function isn't intended to be use for long as ultimately"
    print "all build scripts should incorporate resource checkouts into their scripts"

    searchMode = None
    while(searchMode not in ('n','N','t','T')):
      searchMode = raw_input("Node Lookup Method([N]ame/[T]ype):")  
      if searchMode not in ('n','N','t','T'):
        print "Invalid Selection, please enter N or T"
    
    if searchMode in ('N','n'):
      searchMode = "name"
    else:
      searchMode = "type"  
    requestedResource = raw_input("Please Enter the Resource You would like to check out:")
    notes = raw_input("Notes associated with this checkout:")
    resource = resourceManager.manualCheckOut(requestedResource, notes, searchMode)
    if (resource == None):
      print "Unable to check out: %s"%(requestedResource)
    else:
      if resource == 'error':
        print "Error: There is a problem with this resource, please see the system administrator"
      else:
        print "\n\nGranted: %s\n\n"%(resource)
        print "Please remember to check this resource back in when you are done with it!!!!!!!"
        resourceLog.logInfo('Manual Checkout: %s'%resource)
    another = raw_input("Would you like another? (y/N)")
    if another not in ('y','Y'): #if they don't type a yes we bail back to the main menu
      os.system('clear')
      return



def manualCheckIn():
  while(1):
    os.system('clear')
    print "Return a Resource"
    resource = raw_input("Resource to return:")
    print "Returning %s..."%(resource)
    resourceManager.manualCheckIn(resource)
    resourceLog.logInfo('Manual Checkin: %s'%resource)
    another = raw_input("Would you like another? (y/N)")
    if another not in ('y','Y'): #if they don't type a yes we bail back to the main menu
      os.system('clear')
      return


def setPriority():
  os.system('clear')
  print "Set priority for Build ID"
  while(1):
    buildId = raw_input("Build ID to set:  ")
    if buildId != '':
      break
    else:
      print "You must enter a Build ID"  

  priority = -1
  while( priority < priorityList.NORMAL or priority > priorityList.CRITICAL):
    selection = raw_input("Please Enter Priority([N]ormal,[H]igh,[C]ritical): ")
    if selection in ('n','N'):
      priority = priorityList.NORMAL
      break
    elif selection in ('h','H'):
      priority = priorityList.HIGH
      break
    elif selection in ('c','C'):
      priority = priorityList.CRITICAL
      break
    else:
      print "Invalid Selection, try again"

  print ":::REVIEW:::\n"
  print "Build Id: %s"%(buildId)
  print "Priority: %s"%(selection)
  accept = raw_input("Is this correct?[y/N] ")
  if accept not in ('y','Y'):
    os.system('clear')
    return

  print "Trying to update resource manager...."
  resourceManager.setPriority(buildId, priority)
  print "Complete!"
  raw_input("Press Enter to Continue")
  os.system('clear')

#######stuff for the Pool Manager##################
def printResourceMenu():
  print "1. Add New Resources to Pool"
  print "2. Delete Resources from Pool"
  print "3. Get Resource Status"
  print "4. Enter Query"
  print "5. Get Pool Status"
  print "6. Return to Main Menu"

  try:
    choice = input("\n\nPlease Select[1-6]:")
  except SyntaxError:
    choice = -1
  except NameError:
    choice = -1
  except:
    sys.stderr.write("Unknown Error in Pool Manager\n")
    sys.exit(1)
  return choice

def addToPool():
  os.system('clear')
  print "***Add New Resources to Pool***\n\n\n"
  resourceName = raw_input("Enter Name of Resource:")
  typeList = [resourceName]
  print "Add types for this resource, press enter to stop adding types"
  while(1):
    extraType = raw_input("Enter Type for this resource:")
    if extraType != '':
      typeList.append(extraType)
    else:
      break
  reserved = raw_input("If this resource has multiple types, should it be remain generally reserved?[y/N]  ")
  if reserved in ('y','Y'):
    priority  = USELAST
  else:
    print "The system will try to use resources with the lowest priority numbers first"
    tempPriority = raw_input("Priority For resource[0-2]:")
    if tempPriority not in ('0','1','2'):
      priority = USEFIRST
    else:
      priority = int(tempPriority)
  print "Active resources are tested for base functionality before they are used (ssh test)"
  active = raw_input("Is this an active resource?(y/n) ")
  if active in ('y','Y'):
    useType = ACTIVE
  else:
    useType = PASSIVE

  print "\n\n\n:::Please Review:::\n\n"
  print "Resource: %s"%(resourceName)
  print "Type(s): %s"%(typeList)
  if(priority == USELAST):
    print "Reserved: Yes\n\n"
  else:
    print "Reserved: No"
    print "Priority: %s"%(priority)
  print "Active Resource: %s"%(useType)
  goAhead = raw_input("Is this correct?[y/N]")
  if goAhead in ('y','Y'):
    status = resourceManager.addToPool(resourceName,typeList,priority,useType)
    if status == 0:
      print "Error: Resource Already Exists in Pool"
    else:
      print "Resource has been successfully added"
    raw_input("Press Enter to Continue")
    os.system('clear')
    return
  else:
    os.system('clear')
    return 



def delFromPool():
  os.system('clear')
  print "***Delete a Resource from Pool***"
  resource = raw_input("Resource to Delete: ")
  status = resourceManager.delFromPool(resource)
  if status == 0:
    print "Resource: %s does not exist"%resource
  else:
    print "Resource Deleted!"
  raw_input("Press Enter to Continue")
  os.system('clear')
  return 



def printResourceStatus():
  os.system('clear')
  print "***Get Resource Status***"
  while(1):
    toFind = raw_input("Enter resource name:  ")
    status = resourceManager.getResourceStatus(toFind)
    for line in status:
      print line
    another = raw_input("Would you like another?[y/N]")
    if another not in ('y','Y'):
      os.system('clear')
      return

def printResourceQuery():
  os.system('clear')
  print "***Enter Query***"
  while(1):
    searchMode = raw_input("Query by [A]vailable/[B]uild ID/[T]ype: ")
    while (searchMode not in ('b','B','t','T','a','A')):
      print "Invalid Selection"
      searchMode = raw_input("Query by [A]vailable/[B]uild ID/[T]ype: ")
    if searchMode in ('b','B'):
      searchData = raw_input("Please Enter Build ID: ")
    elif searchMode in ('t','T'):    
      searchData = raw_input("Please Enter Resource Type: ")
    elif searchMode in ('a','A'):
      searchData = ''
    else :
      print "Unkown Error"
      sys.exit(1)
    results = resourceManager.resourceQuery(searchData, searchMode)
    if len(results) > 0:
      for result in results:
        for line in result:
          print line
    else:
      print "No results found for your query."
    another = raw_input("Would you like another?[y/N]")
    if another not in ('y','Y'):
      os.system('clear')
      return
    
def printPoolStatus():
  os.system('clear')
  resultsList = resourceManager.poolStatus()
  if len(resultsList) > 0:
    for result in resultsList:
      for line in result:
        print line
  return

resourceOp = [addToPool, delFromPool, printResourceStatus, printResourceQuery, printPoolStatus]

def poolManager():
  global resourceOp
  os.system('clear')
  print "***Welcome to the Resource Pool Manager*** \n\n\n"

  while(1):
    choice = printResourceMenu()
    while (choice < 1 or choice > 6):
      os.system('clear')
      print "-----Invalid Selection-----"
      print "Please Choose one of the following:"
      choice = printResourceMenu()
    if choice == 6:
      os.system('clear')
      return
    else:
      resourceOp[choice - 1]()  
   
def getQueueStatus():
  normal, high, critical = resourceManager.getQueueStatus()
  print "Normal:"
  if len(normal) > 0:
    for result in normal:
      for line in result:
        print line
  print "High:"
  if len(high) > 0:
    for result in high:
      for line in result:
        print line

  print "Critical:"
  if len(critical) > 0:
    for result in critical :
      for line in result:
        print line

def dumpStateToFile():
  os.system('clear')
  print "This will save the current state of the resource pool, including all checked out resources, to a local backup file"
  userInput = raw_input("Continue [y/n]?")

  if userInput in ['y', 'Y']:
    resourceManager.dumpStateToFile()
    print "State backed up.  Future loads will restore from this point.\n\n"
  else:
    print "Action cancelled.\n\n"
    return

def loadStateFromFile():
  os.system('clear')
  print "**WARNING**"
  print "This will load the state of the entire resource pool from the last backup file."
  print "You probably only want to be doing this if the resource manager has recently deadlocked and"
  print "you backed it up manually before shutting it down."
  userInput = raw_input("Are you absolutely sure you wish to continue [y/n]?")
  if userInput in ['y', 'Y']:
    resourceManager.loadStateFromFile()
    print "State restored.\n\n"
  else:
    print "Action Cancelled.\n\n"
    return

def removeFromQueue():
  os.system('clear')
  print "This will remove all queue entries from a given Build ID"
  print "For a given Build ID types of: node, solaris, cygwin, and cvs will be automatically deleted"
  print "You will be prompted for additional types if necessary (i.e. requests for specific resource etc)\n\n"
  while(1):
    buildId = raw_input("Build ID to Remove:  ")
    if buildId != '':
      break
    else:
      print "You must enter a Build ID"  


  print ":::REVIEW:::\n"
  print "Build ID: %s"%(buildId)
  accept = raw_input("Is this correct?[y/N] ")
  if accept not in ('y','Y'):
    os.system('clear')
    return
  print "Deleteing..."
  resourceManager.removeFromQueue(buildId)
  raw_input("Complete! Press Enter to Continue") 
  os.system('clear')

def main():
  print "There is no manual operation of this module"
  return



#mainOp[] is a list  of function pointers, it just allows us to write things a bit more cleanly for a menu driven interface
mainOp = [manualCheckOut,manualCheckIn,setPriority,poolManager,getQueueStatus,removeFromQueue,dumpStateToFile, loadStateFromFile]


if __name__ == "__main__":
  main()



