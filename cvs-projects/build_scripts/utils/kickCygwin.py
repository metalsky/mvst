#!/usr/bin/env python
#build     2798  0.0  0.0  20300  2388 ?        S    Sep07   0:00 ssh -p 322 cygwin-19 cd /home/build/dailybuild; /home/build/dailybuild/buildcommoncygwin overlord /mvista/dev_area/mobilinux/tahoma070907_0703947/build 0703947 /opt/montavista mobilinux mobilinux /home/build/tahoma070907_0703947-exp/CVSREPOS/build_scripts/hhl/../../mvl-installer /home/build/tahoma070907_0703947-exp/CVSREPOS/build_scripts/hhl/../../dynamicCollectiveLogs 0

import sys,os,re,smtplib
from email.MIMEText import MIMEText
DEBUG = 1

def reroute(inString):
	print inString

def main(hostName):

	if DEBUG:
		os.system = reroute 

	output = os.popen('cat deleteme').readlines()
	regexp = re.compile( r'(\S*) *(\S*) *(\S*) *(\S*) *(\S*) *(\S*) *(\S*) *(\S*) *(\S*)(?#<---date) .*(cygwin-..).*buildcommoncygwin \S* (\S*).* ' )

	for process in output:
		matchObj = regexp.match(process)
		if matchObj:
			userID = matchObj.group(1)
			processID = matchObj.group(2)
			matchedHostName = matchObj.group(10)
			buildPath = matchObj.group(11)
		if matchedHostName == hostName:
			break

	os.system('kill -9 %s' % processID)	
	os.system('touch %s/host/done/common-cygwin' % buildPath)
	sendMail(buildPath)


def sendMail(buildPath):
    smtpObject = smtplib.SMTP()
    mailMsg    = MIMEText("Build %s hung cygwin. Kicked." % buildPath)
    mailMsg['From'] = "Booter"
    mailMsg['To'] = "build@mvista.com" 
    mailMsg['Subject'] = "A cygwin build hung and has been kick-started."
    smtpObject.connect('mail.mvista.com')
    smtpObject.sendmail("build@mvista.com","build@mvista.com", mailMsg.as_string())
    smtpObject.close()

if __name__ in ['__main__']:
		main(sys.argv[1])

