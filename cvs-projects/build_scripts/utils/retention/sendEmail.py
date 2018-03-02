import smtplib
from email.MIMEText import MIMEText
def sendEmail():

	dirString = ""

	buildDict = { 'blackfoot' : [], 'patagonia' : [] , 'mobilinux4' : [], 'mobilinux5' : [],'lamar' : [], 'pebblecreek' : [], \
				'f5' : [], 'f3' : [], 'f2' : [], 'f1' : [], 'devrocket' : [], 'unknown' : [] }

	headerDict = {  'blackfoot'  : 'MVL5.0.0-BLACKFOOT BUILDS UP FOR DELETION', \
					'patagonia'  : 'MVL4.0.1-PATAGONIA BUILDS UP FOR DELETION', \
					'mobilinux4' : 'MOBILINUX 4.1.0 CARBONRIVER BUILDS UP FOR DELETION', \
					'mobilinux5' : 'MOBILINUX 5.0 TAHOMA BUILDS UP FOR DELETION', \
					'lamar'      : 'MVLCGE 4.0.1 LAMAR BUILDS UP FOR DELETION', \
					'pebblecreek': 'MVLCGE 5.0 PEBBLECREEK BUILDS UP FOR DELETION', \
					'f5'         : 'F_5 BUILDS UP FOR DELETION', \
					'f3'         : 'F_3 BUILDS UP FOR DELETION', \
					'f2'         : 'F_2 BUILDS UP FOR DELETION', \
					'f1'         : 'F_1 BUILDS UP FOR DELETION', \
					'devrocket'  : 'DEVROCKET 5.0 - TSUKI BUILDS UP FOR DELETION', \
					'unknown'    : 'UNCLASSIFIED BUILDS UP FOR DELETION' }

	dirs = open('oldDirectories.txt')
	
	for dir in dirs:
		if 'blackfoot' in dir:
			buildDict['blackfoot'].append(dir)
		elif 'patagonia' in dir:
			buildDict['patagonia'].append(dir)
		elif 'carbonriver' in dir:
			buildDict['mobilinux4'].append(dir)
		elif 'tahoma' in dir:
			buildDict['mobilinux5'].append(dir)
		elif 'lamar' in dir:
			buildDict['lamar'].append(dir)
		elif 'pebblecreek' in dir:
			buildDict['pebblecreek'].append(dir)
		elif 'foundation/f5' in dir:
			buildDict['f5'].append(dir)
		elif 'foundation/fthree' in dir:
			buildDict['f3'].append(dir)
		elif 'foundation/ftwo' in dir:
			buildDict['f2'].append(dir)
		elif 'fb07' in dir or 'fe64b' in dir:
			buildDict['f1'].append(dir)
		elif 'tsuki' in dir:
			buildDict['devrocket'].append(dir)
		else:
			buildDict['unknown'].append(dir)
   		
	for key in buildDict.keys():
		if len(buildDict[key]) > 0:
			dirString += '\n' + '*' * 50 + "\n" + headerDict[key] + '\n' + '*' * 50 + '\n'
		for dir in buildDict[key]:
			if '/logs/' not in dir and '/cdimages/' not in dir:
				dirString += dir 

	smtpObject = smtplib.SMTP()
	mailMsg    = MIMEText(dirString)
	mailMsg['From'] = "build@mvista.com"
	mailMsg['To'] = 'build@mvista.com'
	mailMsg['Subject'] = "This is a test email."
	#Send Message
	smtpObject.connect('mail.mvista.com')
	smtpObject.sendmail("build@mvista.com",'build@mvista.com', mailMsg.as_string())
	#smtpObject.sendmail("rell@mvista.com",emailAddr,mailMsg.as_string())
	smtpObject.close()


#}



