#!/usr/bin/env python

import smtplib, sys
from email.MIMEText import MIMEText
def sendEmail(subject, body):

	dirString = ""

	smtpObject = smtplib.SMTP()
	mailMsg    = MIMEText(body)
	mailMsg['From'] = 'build@mvista.com'
	mailMsg['To'] = 'rell@mvista.com'
	mailMsg['Subject'] = subject 
	#Send Message
	smtpObject.connect('mail.mvista.com')
	smtpObject.sendmail("rell@mvista.com",'rell@mvista.com', mailMsg.as_string())
	smtpObject.close()


if __name__ in ['__main__']:
	print "Module not intended for standalone use."
	sys.exit(0)





