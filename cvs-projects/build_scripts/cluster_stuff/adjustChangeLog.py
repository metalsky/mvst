#!/usr/bin/python
import sys, os, string, re

#This script goes through a ChangeLog and grabs sections based on the search string
#entered by the user.  Sections are defined as text between dates


if(len(sys.argv) != 3):
  print "Invalid Number of Args"
  print "Usage - adjustChangeLog.py filename searchString"
  sys.exit(1)

#print "Trying to open " + sys.argv[1]

#Using a try/except to catch file errors
try:
  inputFile = open(sys.argv[1],'r') #Open a file for reading
  outputFile = open("newChangeLog", 'w') #Open file for writing
except IOError:
  print "Error Opening the File"
  sys.exit(1)
except:
  print "Unhandled Exception"
  sys.exit(1)

#print "Open Successful"

#Here's the deal:  We're gonna use a for loop, run through all the lines storing
#them in a buffer
#if we find our string, we'll set a flag, when we hit a date, we'll write and flush, or just
#flush the buffer
branchRegEx = re.compile('\(' + sys.argv[2] + r'\)')
stringBuffer = "" 
matchToken = 0 #token indicating that our buffer is a good buffer
for line in inputFile.readlines():
  temp = re.match(r'\d+-\d+-\d+', line)
  temp2 = branchRegEx.search(line)
  if temp:  #new date, write if we have had a match, otherwise dump the buffer
    if(matchToken):
      outputFile.write(stringBuffer)  #write buffer 
      stringBuffer = ""   #reset the string buffer
      matchToken = 0      #reset token
      temp3 = string.split(line)
      line = temp3[0] + " " + temp3[1] #this removes the names from the changelog, formerly rmname.pl      
    else:
      stringBuffer = ""   #store nothing in the string buffer to reset it
      #We need these here again for the first entry in the CL
      temp3 = string.split(line) 
      line = temp3[0] + " " + temp3[1] #this removes the names from the changelog, formerly rmname.pl      
  elif temp2:            #we have a match, set the variable
    matchToken = 1
    line = branchRegEx.sub("", line)     #this removes the search string from the changelog
  #just copy the line to the buffer while we look for various matches
  stringBuffer += line

if matchToken:  #No date after last entry, so check one last time
  outputFile.write(stringBuffer)

#clean up
outputFile.close()
inputFile.close()
