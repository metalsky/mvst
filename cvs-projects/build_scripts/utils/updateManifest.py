#!/usr/bin/python

#This script just adds a single entry to the manifest.xml file
#For multiple entries it may be more productive to run mkman.py

#RUN THIS FROM THE DIRECTORY CONTAINING THE UPDATE

import os, sys, string

if (len(sys.argv) != 3):
  print "Usage: updateManifest.py <name> <type>"
  print "<name> = carl.4.2.1-0500112"
  print "<type> = package/patch"
  sys.exit(1)

isPatch = 0
packageDir = sys.argv[1]

if(sys.argv[2] == "patch"):
  isPatch = 1

if(not os.path.exists(packageDir)):
  print "Package: %s is not available"%(packageDir)
  sys.exit(1)

try:
  manifest = open('manifest.xml','r')
except IOError:
  print "Error Opening manifest.xml for reading"
  sys.exit(1)
except:
  print "Unhandled Exception"
  sys.exit(1)

lines = manifest.readlines()
manifest.close()

try:
  manifest = open('manifest.xml','w')
except IOError:
  print "Error Opening manifest.xml for writing"
  sys.exit(1)
except:
  print "Unhandled Exception"
  sys.exit(1)

#Tokens and counters
doneWriting = 0
lineNum = 0

#Find out if we have a patch or a package
if(isPatch > 0):
#Find our spot in the file and generate Entry
  while(lineNum < len(lines)):
    if (doneWriting):
      manifest.write(lines[lineNum])
      lineNum = lineNum + 1
    else:
      if(string.find(string.strip(lines[lineNum]), '<patches type="kernel">') == 0 ): #We will insert at the beginning    
        for package in os.popen('find ' + packageDir +' -regex ".+.patch" -print').readlines():
          try:
            filepath = os.popen('find ' + string.strip(package) + ' -printf \%p').read() 
            size = os.popen('find ' + string.strip(package) + ' -printf \%s').read()
            outBuffer = '  <patch>\n'
            outBuffer = outBuffer + '   <filepatch>' + string.strip(filepath) + '</filepath>\n'
            outBuffer = outBuffer + '   <size>' + string.strip(size) + '<size>\n'
            outBuffer = outBuffer + '  </patch>'
            manifest.write(outBuffer)
          except:
            print "Error with Package: %s"%(package)
        doneWriting = 1
      else:
        manifest.write(lines[lineNum])
        lineNum = lineNum + 1
else:
#Find a place in the "packages" section and generate Entry

  while(lineNum < len(lines)):
    if (doneWriting):
      manifest.write(lines[lineNum])
      lineNum = lineNum + 1
    else:
      if(string.find(string.strip(lines[lineNum]), '<packages type="mvl-rpm">') == 0 ): #We will insert at the beginning    
        manifest.write(lines[lineNum])
        lineNum = lineNum + 1
        #Generate entry here
        for package in os.popen('find '+ packageDir + ' -regex ".+.mvl\|.+.rpm" -print').readlines(): 
          rpmval = os.popen('rpm -qp ' + string.strip(package)  + ' --qf "%{NAME}:%{VERSION}:%{RELEASE}:%{ARCH}:%{SIGMD5}:%{SHA1HEADER}"').read()
          rpmvals = string.split(rpmval,':')
          filepath = os.popen('find ' + string.strip(package) + ' -printf \%p').read()
          size = os.popen('find ' + string.strip(package) + ' -printf \%s').read()
          outBuffer ='  <package>\n'
          outBuffer = outBuffer + '   <name>'+ rpmvals[0] + '</name>\n'
          outBuffer = outBuffer + '   <version>'+ rpmvals[1] +'</version>\n'
          outBuffer = outBuffer + '   <release>'+ rpmvals[2] +'</release>\n'
          outBuffer = outBuffer + '   <target>'+ rpmvals[3] +'</target>\n' 
          outBuffer = outBuffer + '   <sigmd5>'+ rpmvals[4] +'</sigmd5>\n' 
          outBuffer = outBuffer + '   <signature>'+ rpmvals[5] +'</signature>\n'
          outBuffer = outBuffer + '   <filepath>'+ string.strip(filepath) +'</filepath>\n'
          outBuffer = outBuffer + '   <size>'+string.strip(size)+'</size>\n'
          outBuffer = outBuffer + '  </package>\n'
          #Write and move on
          manifest.write(outBuffer) 
        doneWriting = 1
      else:
        manifest.write(lines[lineNum])
        lineNum = lineNum + 1


manifest.close()




