#!/usr/bin/env python
import smtplib, sys, commands, os, buildConfig
from collectionBuild import genCommitList
from email.MIMEText import MIMEText


class startEmail:
	def __init__(self):
		#Just pass in a dummy MSD, it's not relevant for this
		self.Config = buildConfig.buildConfig('x86-prototype')
		self.From = 'rell@mvista.com'
		self.To = 'mvl6-dev@mvista.com'
		self.Subject = 'MVL6 Builds starting'
		self.Body = self.prepareBody()
				

	def sendEmail(self):
		dirString = ""
		smtpObject = smtplib.SMTP()
		mailMsg    = MIMEText(self.Body)
		mailMsg['From'] = self.From
		mailMsg['To'] = self.To
		mailMsg['Subject'] = self.Subject 
		#Send Message
		smtpObject.connect('mail.sh.mvista.com')
		smtpObject.sendmail('mvl6-dev@mvista.com','mvl6-dev@mvista.com', mailMsg.as_string())
		smtpObject.close()

	def prepareBody(self):
		commits = genCommitList()
		blameDict = {}
		for commit in commits:
			try:
				if commit.AuthorName not in blameDict[commit.Repo]:
					blameDict[commit.Repo].append(commit.AuthorName)
			except KeyError:
				blameDict[commit.Repo] = [commit.AuthorName]


		rtext = 'The following collections have changed:\n'
		for key in  blameDict.keys():
			rtext += key + ' '
		rtext += '\n\n'

		for key in blameDict.keys():
			rtext += key + ' modified by: '
			for name in blameDict[key]:
				rtext += name + ' '
			rtext += '\n'

		
		rtext += 'The following MSDs will therefore be built:\n'
		changedMSDs = self.Config.GetNamesByCollections(blameDict.keys())
		for msd in changedMSDs:
			rtext += msd + ' '


		return rtext 
	

if __name__ in ['__main__']:
	print "Running email unit tests"
	myemail = startEmail()
	print myemail.Body
#	myemail.sendEmail()


