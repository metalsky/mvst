#!/usr/bin/env python
import smtplib, sys, commands, os, buildConfig
from email.MIMEText import MIMEText


class buildEmail:


	def __init__(self, bcfg):
		self.Config = bcfg
		self.From = 'rell@mvista.com'
		self.To = 'mvl6-dev@mvista.com'
		self.Subject = 'MVL6 Build %s complete.' % bcfg.BuildTag
		self.Body = self._parseBody()
		

	def sendEmail(self):
	
		dirString = ""
	
		smtpObject = smtplib.SMTP()
		mailMsg    = MIMEText(self.Body)
		mailMsg['From'] = self.From
		mailMsg['To'] = self.To
		mailMsg['Subject'] = self.Subject 
		#Send Message
		smtpObject.connect('mail.sh.mvista.com')
		smtpObject.sendmail('rell@mvista.com','mvl6-dev@mvista.com', mailMsg.as_string())
		smtpObject.close()

	def _parseBody(self):
		logDict = {}
		logfilePath = '/mvista/dev_area/mvl6/%s/' % self.Config.BuildTag

		for logfile in os.listdir(logfilePath):
			if '.log' not in logfile:
				continue

			logDict[logfile] = commands.getoutput('sed /NOTE:\ Tasks\ Summary/,/EOF/p -n %s' % os.path.join(logfilePath, logfile))



		rtext = ''
		for key in logDict.keys():
			rtext += '\n\nBuild for machine %s executed.  The 64-bit builds are 64 bit hosts, not target.  Build status follows.  Blank text indicates the build failed before launching.:\n\n' % key[:-4] + logDict[key]


		return rtext
		








if __name__ in ['__main__']:
	print "Running email unit tests"
	myconfig = buildConfig.buildConfig('mips-malta')
	myconfig.BuildTag = 'mips-malta-2.6.28_090617_0901542'
	myemail = buildEmail(myconfig)
	myemail.sendEmail()



