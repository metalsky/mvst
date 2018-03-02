#!/usr/bin/python

import os, sys, threading, smtplib
from email.MIMEText import MIMEText


def checkDevArea():
  os.system('ls /mvista/dev_area > /dev/null') 

def main():
  thread = threading.Thread(target=checkDevArea)
  thread.start()
  thread.join(10)
  alive = thread.isAlive()
  if alive:
    #Issues with dumbo, send email
    smtpObject = smtplib.SMTP()
    mailMsg    = MIMEText('')
    mailMsg['From'] = "build@mvista.com"
    mailMsg['To'] = "9253374727@vtext.com"
    mailMsg['Subject'] = "/mvista/dev_area is down"
    #Send Message
    smtpObject.connect('mail.mvista.com')
    smtpObject.sendmail('cvanarsdall@mvista.com','9253374727@vtext.com', mailMsg.as_string())
    smtpObject.close()
  
  else: 
    sys.exit(1)

if __name__ == "__main__":
  main()
