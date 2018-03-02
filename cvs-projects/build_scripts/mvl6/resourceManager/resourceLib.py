#!/usr/bin/python

#########################################################
#                resourceLib.py                         #
#                                                       #
#  All functions related to the resource pool           #
#                                                       #
#                                                       #
#########################################################

import sys, os, cPickle, string, time, traceback, smtplib
from resourceError import ResourceError #ResourceManager (tm) Exception
from types import *
from email.MIMEText import MIMEText
import config
##########class definitions##################

# BuildResource defines all data associated with any given resource

NOTUSED = 0
USED = 1

USEFIRST = 0
USESECOND = 1
USETHIRD = 2
USELAST = 3

TEST = 0  #set to nonzero for test

#We'll add a testability flag for ACTIVE resources
ACTIVE = 1
PASSIVE = 0

class BuildResource:
  def __init__(self, name, typeList, priority, useType):
    if type(name) != StringType or type(priority) != IntType or type(typeList) != ListType or type(useType) != IntType:
      raise TypeError, "Bad Types passed as BuildResource"
    self.resourceName = name
    self.resourceType = typeList
    self.resourcePriority = priority
    self.resourceUseType  = useType  
    self.useFlag      = NOTUSED
    self.useTime      = None
    self.useNotes     = None
    self.buildTag     = None
    self.buildId      = None

  def notifyBuild(self):
    print "Trying to send message...."
    message = "Resource %s failed internal verification tests"%self.resourceName
    subject = "Resource Manager Status Message: Error found on %s"%self.resourceName

  #Standard SMTP SETUP
    smtpObject = smtplib.SMTP()
    mailMsg    = MIMEText(message)
    mailMsg['From'] = config.notifyEmail 
    mailMsg['To'] = config.notifyEmail 
    mailMsg['Subject'] = subject
    #Send Message
    smtpObject.connect(config.mailServer)
    smtpObject.sendmail(config.notifyEmail,config.notifyEmail, mailMsg.as_string())
    smtpObject.close()
    return
		      


  def tagUsed(self,buildTag,buildId,notes):
    self.useFlag = USED
    self.buildTag = buildTag
    self.buildId = buildId
    self.useNotes = notes
    self.useTime = time.strftime("%m/%d/%Y - %I:%M %p")

  def tagDown(self):
    self.useFlag = USED
    self.useNotes = "Resource failed internal verification tests"
    self.buildTag = "Resource Manager"
    self.buildId = "Status Message"
    self.useTime = time.strftime("%m/%d/%Y - %I:%M %p")
    try:
      self.notifyBuild()
    except:
      return #its just a notification message, we don't want to take down the whole box if a server doesn't connect


# ResourcePool contains the list of resources and all methods directly associated with this list

class ResourcePool:
  def __init__(self):
    self.resourceList = None 
    #A couple defines for this class
    self.TYPE = "type"
    self.NAME = "name"


  def initResourcePool(self):
    try:
      poolFPtr = open(config.pool,"r")
    except IOError:
      raise ResourceError, "Error Opening Resource Pool for Reading"
    except:
      traceback.print_exc()
      raise ResourceError, "Unknown Error Initializting Resource Pool"
    try:
      pickledList = cPickle.load(poolFPtr)
    except EOFError:
      print "No Existing Resource Pool, creating..."
      self.resourceList = {} #empyty file, set to empty list for construction
      poolFPtr.close()
      return
    except:
      traceback.print_exc()
      raise ResourceError, "Unknown Error with Resource Pool"
    poolFPtr.close()
    self.resourceList = pickledList
    return

  def storeResourcePool(self):
    try: 
      poolFPtr = open(config.pool,"w")
      cPickle.dump(self.resourceList, poolFPtr, cPickle.HIGHEST_PROTOCOL)
    except PicklingError:  #exit for now, we should probably make these send an email versus printing a message
      raise ResourceError, "Error Pickling Resource Pool"
    except IOError:
      raise ResourceError, "Error Opening Resource Pool for Writing"
    except:
      traceback.print_exc()
      raise ResourceError, "Unknown Error Cleaning Resource Pool"
    poolFPtr.close()
    return 

  def verifyResource(self,resourceName, resourceType=None):
    if resourceName.count("cygwin") > 0:
      if os.popen('ssh %s -p 322 "echo "hi""'%resourceName).readline() == "hi\n":
        return 1
      else:
        return 0
    else:
      fps = os.popen4('ssh %s "echo "hi""'%resourceName)
      cnt = 0
      success = 0
      for line in fps[1]:
        cnt += 1
	print line
        if line == "hi\n":
          success = 1

      print success
      print cnt

      if success == 1 and cnt == 1: #2 for hi + newline, anything else indicates an error
        return 1
      else:
        return 0


  ##########################
  #   tagResource()
  #
  # finds resource of type:resourceType in resource pool and checks resource out
  # returns None if resource unavailable, small priority scheme such that special multitype
  # resources are scheduled accordingly
  #
  #  searchMethod is an optional arguement, default search by resourceType
  #  get resource by resourceNAme is searchMethod = "name"
  ##########################
  def tagResource(self,resource,buildTag, buildId, notes, searchMethod="type"):
    backupResource = None #This variable will be set if we find something that we don't want to use the first time around
    if searchMethod not in ('type','name'):
      raise ResourceError, "Invalid mode passed to tagResource" 

    #Search and tag or fail
    if searchMethod == self.TYPE:
      existingResource = 0
      for key in self.resourceList.keys(): #must find the type, use, and priority
        resourceObj = self.resourceList[key]
	if resource in resourceObj.resourceType and resourceObj.useFlag == NOTUSED and resourceObj.resourcePriority == USEFIRST: #tag        
	  if resourceObj.resourceUseType == PASSIVE or (resourceObj.resourceUseType == ACTIVE and self.verifyResource(resourceObj.resourceName)):
	    resourceObj.tagUsed(buildTag,buildId,notes) 
	    return resourceObj.resourceName
	  else:  #we found an available resource but its down
	    resourceObj.tagDown()

	elif resource in resourceObj.resourceType and resourceObj.useFlag == NOTUSED and resourceObj.resourcePriority != USEFIRST:
	  if backupResource == None:
	    backupResource = resourceObj #save this
	  elif backupResource.resourcePriority > resourceObj.resourcePriority: #so if we've assigned a USELAST but something else shows up
	    backupResource = resourceObj
        elif resource in resourceObj.resourceType and resourceObj.useFlag == USED:  #This is so we know that a compatible resource exists
          existingResource = 1 #So, at some point we found a resource of this type
      if backupResource != None: #We broke out of our loop without returning but we found something we can use as a last resort
	if backupResource.resourceUseType == PASSIVE or (backupResource.resourceUseType == ACTIVE and self.verifyResource(backupResource.resourceName)):
          backupResource.tagUsed(buildTag,buildId,notes)
          return backupResource.resourceName
	else:  #we found an available resource but its down
	  backupResource.tagDown()

      else: #We didn't find any free resources, send error if the resource doesn't exist otherwise just return None
        if existingResource:
          return None #failure
        else:
          return "error"

    elif searchMethod == self.NAME:
      if self.resourceList.has_key(resource):
        if self.resourceList[resource].useFlag == NOTUSED:
	  resourceObj = self.resourceList[resource]
	  if resourceObj.resourceUseType == PASSIVE or (resourceObj.resourceUseType == ACTIVE and self.verifyResource(resourceObj.resourceName)):
	    resourceObj.tagUsed(buildTag,buildId,notes) 
	    return resourceObj.resourceName
	  else:
	    resourceObj.tagDown()
	    return "error"
	else:
	  return None
      else:
        sys.stderr.write("Requested Resource: %s Doesn't Exist\n"%(resource))
        return None
    else:
      raise ResourceError, "Unknown Error in tagResource"

  ########################################
  #          returnResource(string resource)
  #
  #  Sets useFlag of resource to NOTUSED
  #
  ########################################
  def returnResource(self, resourceName):
    if self.resourceList.has_key(resourceName):
      self.resourceList[resourceName].useFlag  = NOTUSED
      self.resourceList[resourceName].buildTag = None
      self.resourceList[resourceName].buildId  = None
      self.resourceList[resourceName].useNotes = None
    else:
      print "Resource: %s does not exist"%(resourceName)  
 

  #######################
  #    addResource(self, resourceName, resourceType, resourcePriority):
  #
  #  adds a resource to the current resource pool  
  #
  ######################
  def addResource(self, resourceName, resourceType, resourcePriority, useFlag):
    if self.resourceList.has_key(resourceName):
      #print "Error: Resource already exists in pool"
      return 0
    self.resourceList[resourceName] = BuildResource(resourceName, resourceType, resourcePriority, useFlag)
    #print "Resource %s successfully added to resource pool"%(resourceName)
    return 1

  ##############################
  #   delResource(self, resourceName)
  # 
  #  removes a resource from the resourcePool
  #  returns 0 if no resource removed
  #############################
  def delResource(self, resourceName):
    try:  
      del self.resourceList[resourceName]
      return 1
    except KeyError:
      #print "Resource %s doesn't exist"%(resourceName)
      return 0

  ############################
  #  getPoolstatus(self)
  #
  #  Simple function to print out the contents of the an active resource pool
  #
  ############################
  def getPoolStatus(self):
    keys = self.resourceList.keys()
    keys.sort()
    resultsList = []
    for resource in keys:
      resultsList.append(self.getResourceStatus(resource, 0))
    return resultsList


  def dumpStateToFile(self):
    try:
      poolFile = open(config.saveState,"w")
      cPickle.dump(self.resourceList, poolFile, cPickle.HIGHEST_PROTOCOL)
    except:
      print "Error while saving pickled file."
      return

    poolFile.close()
    

  def loadStateFromFile(self):
    try:
      poolFile = open(config.saveState, 'r')
      pickledPoolFile = cPickle.load(poolFile)
    except:
      print "Error while loading pickled file."
      return

    self.resourceList = pickledPoolFile
    poolFile.close()
      
  ######################################
  #		getResourceStatus(string resource)
  #
  #  Prints the current status of a resource
  #
  ######################################
  def getResourceStatus(self, resource, settings):
    results = []
    if not self.resourceList.has_key(resource):
      results.append("Resource %s does not exist"%(resource))
      return results
    results.append("\nResource: %s"%(self.resourceList[resource].resourceName))
    #print self.resourceList[resource].resourceType

    if self.resourceList[resource].useFlag == USED:
      results.append("Status: In Use")
      results.append("Build: %s"%(self.resourceList[resource].buildTag))
      results.append("Used Since: %s"%(self.resourceList[resource].useTime))
      results.append("Notes: %s\n"%(self.resourceList[resource].useNotes))
    else:
      results.append("Status: Available\n")

    if settings:
      results.append("###Config###\n")
      results.append("Types: %s"%(self.resourceList[resource].resourceType))
      results.append("Priority: %s\n"%(self.resourceList[resource].resourcePriority))
      if self.resourceList[resource].resourceUseType == ACTIVE:
        flag = "ACTIVE"
      else:
        flag = "PASSIVE"
      results.append("Flag: %s\n\n"%flag)
    return results

  ################################
  #    getResourceList()
  #
  #	Returns a list of resources in pool
  #
  ################################
  def getResourceList(self):
     return self.resourceList.keys()

  ###############################
  #   resourceQuery()
  #
  #  Some more refined searching capability using getResourceStatus to print results
  #
  ###############################

  def resourceQuery(self, searchString, queryType):
    results = []
    for resource in self.resourceList.keys():
      if queryType in ('t','T'):
        if searchString in self.resourceList[resource].resourceType:
          results.append(self.getResourceStatus(self.resourceList[resource].resourceName, 0))
      elif queryType in ('a','A'):
        if self.resourceList[resource].useFlag == NOTUSED:
          results.append(self.getResourceStatus(self.resourceList[resource].resourceName, 0))
      elif queryType in ('b','B'):
        if self.resourceList[resource].buildId == searchString:
          results.append(self.getResourceStatus(self.resourceList[resource].resourceName, 0))
    return results

#############################




###### a main function so this module can be tested individually

def main(argv=sys.argv):
  print "You really shouldn't be running this script by itself"
  print "It serves as a library to the resource manager"
  print "Manual operation exists for testing purposes only" 
 
  if(config.TEST == 1):

    resourcePool = ResourcePool()
    resourcePool.initResourcePool()

    print "Building new resource Pool..."
    resourcePool.addResource('cvs-userland',('cvs'),USEFIRST,ACTIVE)
    resourcePool.addResource('cvs-toolchain',('cvs'),USEFIRST,ACTIVE)
    resourcePool.addResource('node-1',('node','node-1','fastnode'),USEFIRST,ACTIVE)
    resourcePool.addResource('node-2',('node','node-2','fastnode'),USEFIRST,ACTIVE)
    resourcePool.addResource('node-3',('node','node-3','fastnode'),USEFIRST,ACTIVE)
    resourcePool.addResource('node-20',('node','node-20'),USELAST,ACTIVE)
    resourcePool.addResource('node-21',('node','node-21'),USEFIRST,ACTIVE)
    resourcePool.addResource('solaris8-1',('solaris','solaris8-1'),USEFIRST,PASSIVE)
    resourcePool.addResource('cygwin-1',('cygwin','cygwin-1'),USELAST,PASSIVE)

    print "Storing Pool..."
    resourcePool.storeResourcePool() #Test Store
    print "Retrieving Pool..."
    resourcePool.initResourcePool()  #Test Retrieval of real Pool

    #Some functions to interact with the pool
    print "STATUS\n"
    #resourcePool.getPoolStatus()

    #Check out a bunch of nodes#
    print "I'm going to check out several nodes, node-20 should be the last node, followed by a checkout failure"
    resource = []
    i = 0
    while (i < 6):
      resource.append( resourcePool.tagResource('node','ftwo123456_0500124','0500124','A test') )
      print resource[i]
      i = i + 1
    
    resourcePool.getPoolStatus()

    #Check in the nodes
    print "I'm going to check in the nodes I've just received"
    i = 0
    while (i < 6):
      if(resource[i] != None):
        resourcePool.returnResource(resource[i])
      i = i + 1
    resourcePool.getPoolStatus()

    print "Deleting Pool...."
    resourcePool.delResource('cvs-userland')
    resourcePool.delResource('cvs-toolchain')
    resourcePool.delResource('node-1')
    resourcePool.delResource('node-2')
    resourcePool.delResource('node-3')
    resourcePool.delResource('node-20')
    resourcePool.delResource('node-21')
    resourcePool.delResource('solaris8-1')
    resourcePool.delResource('cygwin-1')
    resourcePool.storeResourcePool()


#  if(resourcePool.delResource('node-2')):
#    print "node-2 Deleted"
#  else:
#    print "Unable to delete resource: node-2"
   
if __name__ == "__main__":
   main()





