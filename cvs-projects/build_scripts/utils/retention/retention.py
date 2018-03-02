#!/usr/bin/python
# --- retention.py ---
#A helper script to send some emails and move files around.

import smtplib, re, os, sys, string,lt_os
from email.MIMEText import MIMEText

smtpServer = 'mail.mvista.com'
sender = 'build@mvista.com'
destinationEmail ="awaters@mvista.com"

DEBUG = 1

def warningMessage():
  lt_os.system('/home/build/build_scripts/utils/findOldDirs.py > /home/build/build_scripts/utils/trashed_dirs', True)
  try:
    removal_list = open('/home/build/build_scripts/utils/trashed_dirs')
  except:
    sys.stderr.write('Failure Encountered while opening Trash listings\n')
    sys.exit(1)

  warning_message = "Build will be removing stuff from dev_area in two days \n\n\n"
  warning_subject = "TEST TEST Build will delete stuff in two days"

  for line in removal_list:
    warning_message += line

  #Standard SMTP SETUP
  smtpObject = smtplib.SMTP()
  mailMsg    = MIMEText(warning_message)
  mailMsg['From'] = sender
  mailMsg['To'] = destinationEmail #Change to engr at some point
  mailMsg['Subject'] = warning_subject
  #Send Message
  smtpObject.connect(smtpServer)
#  print "OMG MAIL BEING SENT!"
  smtpObject.sendmail(sender,destinationEmail, mailMsg.as_string())
  smtpObject.close()
  return



def moveToRemoval():
  lt_os.system('/home/build/build_scripts/utils/findOldDirs.py > /home/build/build_scripts/utils/trashed_dirs', True)
  try:
    removal_list = open('/home/build/build_scripts/utils/trashed_dirs')
  except:
    sys.stderr.write('Failure Encounters while opening Trash listings\n')
    sys.exit(1)
  #Our regular expression for parsing, the third and fourth portions of the directory name are the most important, they tell us
  #the product as well as the type of thing we're moving: log, cdimage, async

  #/mvista/dev_area/<product>/<type>

  #we have to be careful with type, type can end up being: async, logs, cdimages
  #If we get a cdimages, we have to check more to see if its async cdimages
  #logs also don't follow the standard.  If the bottom part is confusing as all hell that's the reason why
  msg = "These directories have been removed from /mvista/dev_area\n\n\n"
  parser = re.compile(r'/mvista/dev_area/(.+)/(.+)/') 
  buildtagRegEx = re.compile(r'.+\d\d\d\d\d\d_\d+')
  for removalDir in removal_list:
    parsed = parser.match(removalDir)
    if parsed:
      #find out the product: cge, foundation, pro, tsuki, etc
      product = parsed.group(1)

      #Simple case: buildtag
      if buildtagRegEx.match(parsed.group(2)):
        removeLocation = '/mvista/dev_area/%s/REMOVE/build/'%(product)  
      #Found: async
      elif parsed.group(2) == 'async':
	removeLocation = '/mvista/dev_area/%s/REMOVE/async/'%(product) 
      #Found: cdimages
      elif parsed.group(2) == 'cdimages':
	removeLocation = '/mvista/dev_area/%s/REMOVE/cdimages/'%(product) 
      #Found: logs
      elif parsed.group(2) == 'logs': #if we're here we know its not an async so this one is easy
        removeLocation = '/mvista/dev_area/%s/REMOVE/logs/'%(product)
      else:
        print "NO MATCH: %s"%removalDir
        removeLocation = None

      if DEBUG:
        if removeLocation != None:
          print "mkdir -p %s"%removeLocation
          print "mv %s  %s"%(string.strip(removalDir), removeLocation)
      else:
        if removeLocation != None:
          lt_os.system("mkdir -p %s"%removeLocation, False)
          lt_os.system("mv %s  %s"%(string.strip(removalDir), removeLocation), False)
      parsed = None
      #Add to email message
      msg += removalDir #This should already have the newline in it, so im not gonna mess with it

  #Send email of removed Directories:
  if  DEBUG:  
    print "Sending email..."
    print msg
  else:
    smtpObject = smtplib.SMTP()
    mailMsg    = MIMEText(msg)
    mailMsg['From'] = sender
    mailMsg['To'] = destinationEmail
    mailMsg['Subject'] = '/mvista/dev_area/ Cleanup list'
    #Send Message
    smtpObject.connect(smtpServer)
    smtpObject.sendmail(sender,destinationEmail, mailMsg.as_string())
    smtpObject.close()


def deleteRemovalDirs():
  lt_os.system('rm -rf `find | grep REMOVE`', False)


def main(argv):
  if len(argv) != 2:
    print "Usage: ./retention.py <WARN|PREP|DELETE>"
    sys.exit(1)

  if argv[1] == "WARN": 
    warningMessage()
  elif argv[1] == "PREP":
    moveToRemove()
  elif argv[1] == "DELETE":
    deleteRemovalDirs()
  else:
    print "Usage: ./retention.py <WARN|PREP|DELETE>"
    sys.exit(1)


if __name__=="__main__":
  main(sys.argv)


