#!/usr/bin/python

anim = [0]
#mmmm....libraries....
import sys
import os
import string
import re
import time


#our binary search tree implementation
from binSearch import *

DEBUG = 0

#This script will parse through the mvista/dev_area directories and find old directories
#It will create a list of these old directories for removal at a later time

#this script should be run as a cron task.

#we're gonna be looking through /mvista/dev_area/<product>/
#and /mvista/dev_area/<product>/<edition>/


#This is a tuple listing all build tags to be deleted after two weeks
#Anything not listed in here will get a month to live
TWOWEEKS = ('tsuki','devtools','ftwotools', 'fthreetools', 'f5tools')



#######################isOld()######################
#isOld tells us if something is 6 or more months old
#startDay = date an entry was made: yyyymmdd 
#currentDay = today's date: yyyymmdd

def isOld(startDay, currentDay):
  #extract year/mo/day  
  regExp = re.compile(r"(\d\d\d\d\)(\d\d)(\d\d)")
  extracted = regExp.match("%s"%startDay)
  #calculate 6 months from now
  year  = extracted.group(1)
  month = extracted.group(2)
  day   = extracted.group(3)
  
  #calcucate 200 days from now then to a straight compare to today's date
  day += 200
  while(day > 30):
    day -= 30
    month += 1
  while(month > 12):
    month -= 12
    year += 1

  result = "%d%02d%02d"%(year,month,day)
  #compare to today
  if string.atoi(result) < currentDay: #If after adding all those days, we aren't at today the entry must be OLD!
    return 1
  else:
    return 0

#################END isOld##################################


############getExpDate##########################
def getExpDate(year, month, day, sub):
  day -= sub
  if(day < 1):
    day += 30
    month -= 1
  if(month < 1):
    year -= 1
    month += 12
  #Now, put these there numbers in a string and dump out an int
  output = "%d%02d%02d"%(year,month,day)
  output = string.atoi(output)
  return output
#################END getExpDate############################

######sendMail(buildtag, emailAddr)######
def sendMail(buildtag, emailAddr):
  if DEBUG:
    print "Expired readme.keep Entry: %s, sending mail to %s"%(buildtag, emailAddr)
  else:
    #Standard SMTP SETUP
    smtpObject = smtplib.SMTP()
    mailMsg    = MIMEText("Your build %s has expired please submit another request if you want to keep this build"%buildtag)
    mailMsg['From'] = "build@mvista.com"
    mailMsg['To'] = emailAddr
    mailMsg['Subject'] = "A build you requested to keep has expired"
    #Send Message
    smtpObject.connect(smtpServer)
    smtpObject.sendmail("build@mvista.com",emailAddr, mailMsg.as_string())
    #smtpObject.sendmail("rell@mvista.com",emailAddr,mailMsg.as_string())
    smtpObject.close()




##################findDirs################################
def findDirs(arg, dirname, names):
#arg is the root of the tree

#to be called by our walking function
#  print dirname
#so, identify things in names that look like <a-z><0-9>-<0-9>
#check if that name is a directory, if its a directory, check its build date vs current date
#if its over a month old, check it against the keep list
#anything in names that is not a build-tag dir needs to be recursively searched, otherwise ignored.
  anim[0] += 1
  if anim[0] % 25 == 0:
	  sys.stderr.write('.')
  regexp = re.compile(r"(.+)(\d\d\d\d\d\d)_\d+") #compile reg exp here for speed  
  regexpTwo = re.compile(r"mvl\w+") #extract all directories containing an mvl in front
  i = 0

  while i < len(names):
#arg[0] = cacheTree; arg[1] = rootNode; arg[2] = expDate; arg[3] = today; 
    extracted = regexp.match(names[i])
    amIaDir = os.path.join(dirname, names[i])
    #if we are deleting from the list we aren't incrementing i because the list will change    
    if names[i] in ("removal", "CHANGELOGS","pe040201","moveout","fb031223","dpb031230_64-1","newformat"): #Skip specific dirs
      del names[i]
    elif regexpTwo.match(names[i]): #skip shit that exists in our naming schema
      del names[i]
    elif extracted != None and os.path.isdir( amIaDir ):  #if its a build tag, and a dir
      name = names[i] #for searching occuring in a couple lines
      del names[i]  #remove it from our list of directories to parse through
      if string.atoi(extracted.group(2)) < arg[2] or (string.atoi(extracted.group(2)) < arg[3] and extracted.group(1) in TWOWEEKS):  #if our deal has expired - check the list
         isKeeper = arg[0].findNode(name, arg[1]) #search the tree for this node
         if isKeeper == None: #if it isn't a keeper, dump it
           print "%s/"%(amIaDir)

         elif isKeeper.date < today:  #its a keeper, but its expired...send email and move to /trash
           if isKeeper.done == 0:
             isKeeper.done = 1 #to avoid sending and email for build, cdimage and log dirs
#             sendMail(extracted.group(0), isKeeper.email)
             print "EXPIRED: %s/"%(amIaDir) #have it print out the keeper since we're not good at maintaining expiration dates

         else:  #do nothing, not necessary to write this, but disk space is cheap and its great for debugging!
#            print "I found something to keep: %s"%(isKeeper.bTag)
           pass
    else:
      i += 1  #go to the next element in the list
##################END findDirs############################


#the main part of the script
#Initial stuff to do
outputBuffer = None #to store directories to be moved, written to file at end
 
os.chdir("/mvista/dev_area/") #root of search
rootDir = os.getcwd() #set rootDir to where we are so we can refer to the start of our search anytime

#See if our file exists, parse it and dump it into a bst
############################
cacheTree = Tree()  #this tree will be passed as an arg to the os.path.walk function
readmePath = "/tmp/KEEPERS" #where the listing of files to be kept is

try:
  sys.stderr.write('Opening %s\n'%readmePath)
  keepFile = open(readmePath, 'r')
except IOError:
  print "Error opening " + readmePath
except:
  print "Unhandled Exception"

#What we need to do is parse the data in the file, dump it into a struct and then dump the struct in a tree

#FILE FORMAT: <BUILD> <START> <EXPIRE> <EMAIL>
#fileRegEx = re.compile(r"(.+) (.+) (.+) (.+@mvista.com) ")#the format of the file, and into groups for extraction
fileRegEx = re.compile(r"(.+)")
tempData = fileData()
rootNode = None
for line in keepFile.readlines():
  extracted = fileRegEx.match(line)  
  #put various groupings into a data structure
  if extracted != None:
    #sys.stderr.write('Adding build %s to tree....\n'%extracted.group(1))
    tempData.buildTag = extracted.group(1)
    #tempData.startDate= string.atoi(extracted.group(2)) #added 7/19 - date of entrance into readme_keep
    tempData.startDate = 0
    tempData.expDate  = 990101    #string.atoi(extracted.group(2)) #we want a number not a string
    tempData.emailAddr= 'rell@mvista.com'
    if rootNode == None:
      rootNode = cacheTree.addNode(tempData)   #We need a special case to create a root node for an empty tree
    else:
      cacheTree.insertNode(tempData, rootNode)
keepFile.close()
#print "File Read Complete"
#########################


#We're gonna take the time, find our 30 days previous, and use that as a comparison in the function
year = string.atoi( time.strftime("%y") )
month = string.atoi( time.strftime("%m") )
day = string.atoi( time.strftime("%d") )

today   = "%02d%02d%02d"%(year,month,day)
today   = string.atoi(today)
expDate = getExpDate(year, month, day, 30)
twoWeekExp = getExpDate(year, month, day, 14)
treeVar = [cacheTree, rootNode, expDate, twoWeekExp]

#This goes through our little world and nukes all the big bad files
os.path.walk(rootDir, findDirs, treeVar)


