#!/usr/bin/python

#This script just runs the commands we normally run by hand for the changelogs


import sys, os, time, re, string

if(len(sys.argv) != 4):
  print "Invalid Args"
  print "Usage - genChangelog.py <kernel branch> <date> <update>"
  print "<kernel branch> - i.e. humboldt"
  print "<date> - yyyymmdd i.e. 20050607"
  print "<update> skip/null"
  sys.exit(1)

kernelBranch = sys.argv[1]
logDate = sys.argv[2]
updateRepo = sys.argv[3]

kernelRepo = "/home/build/changelogs/%s/"%(kernelBranch)
linuxRepo = kernelRepo + "linux"

#Get the Current Date
year = string.atoi( time.strftime("%Y") )
month = string.atoi( time.strftime("%m") )
day = string.atoi( time.strftime("%d") )

print year
print month
print day

#Check to see that things have been setup, this must be done by the build engineer BEFORE using this script
if os.path.isdir(kernelRepo):
  os.chdir(kernelRepo)
else:
  print "This Kernel Repository is not setup for Automated ChangeLogging, please manually check out %s"%(kernelBranch)
  sys.exit(1)

#Open branch config file
try:
  statusFile = open(kernelRepo + "status.build", 'r')
except IOError:
  print "Error opening " + kernelRepo + "status.build"
  sys.exit(1)
except:
  print "Unhandled Exception"
  sys.exit(1)  

#extract current data in file and close
line = statusFile.readline()
statusFile.close()

#String format <date> <revision>
extracted = re.match(r"(\d\d\d\d\d\d\d\d) (\d+)", line)
oldDate   = extracted.group(1)
kernelRev = string.atoi(extracted.group(2))
kernelRev += 1

if updateRepo != 'skip':
  print "cvs -q update -dPA -r %s"%(kernelBranch)
#  os.system("cvs -q update -dPA -r %s"%(kernelBranch))

print "/home/build/cvs2cl/cvs2cl.pl -S -F %s -b -l -d\"\'>%s\'\""%(kernelBranch, logDate)
#os.system("/home/build/cvs2cl/cvs2cl.pl -S -F %s -b -l -d\"\'>%s\'\""%(kernelBranch, logDate))

print "/home/build/changelogs/adjustChangeLog.py ChangeLog %s"%(kernelBranch)
#os.system("/home/build/changelogs/adjustChangeLog.py ChangeLog %s"%(kernelBranch))

#Update status.build 
print "Updating status.build..."
try:
  statusFile = open(kernelRepo + "status.build", 'w')
except IOError:
  print "Error opening " + kernelRepo + "status.build"
  sys.exit(1)
except:
  print "Unhandled Exception"
  sys.exit(1)  

#statusFile.write("%s%s%s %s"%(year, month, day, kernelRev))
statusFile.close()


print "Your ChangeLog now exists as newChangeLog, please rename and move this to the approriate directory"
