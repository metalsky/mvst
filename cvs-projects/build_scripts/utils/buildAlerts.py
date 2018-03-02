#!/usr/bin/python

import sys, syslog, traceback

#GLOBAL


#DEFINE
#Priority Levels
CRIT = syslog.LOG_CRIT
ERR = syslog.LOG_ERR
WARN = syslog.LOG_WARNING
NOTICE = syslog.LOG_NOTICE
INFO = syslog.LOG_INFO
DEBUG = syslog.LOG_DEBUG

#Facilities
FACILITY = syslog.LOG_LOCAL0

class AlertException(StandardError):
	pass


############################################
#	sendAlert(buildtag, type, message, severity
#
#  buildtag is the component - we can't parse on it but will make things look nicer on zenoss
#  type and message are combined.  We can regex out that part of the message in zenoss and alert accordingly
#
#  severity levels are also parsed.  Meaning we can have alerts for KERN CRIT and KERN ERR should we want to handle 
#  them differently or raise alert levels during release candidate time
#
############################################
def sendAlert(buildtag, type, message, severity):
	if severity not in (CRIT, ERR, WARN, NOTICE, INFO, DEBUG):
		raise AlertException
	try:
		syslog.openlog(buildtag,0, FACILITY)
		syslog.syslog(severity, "%s - %s"%(type, message))
		syslog.closelog()
	except:
		raise AlertException, "%s"%traceback.format_exc()



def main():
	sys.stderr.write('No manual execution of this module\n')
	sys.exit(1)


if __name__ == "__main__":
	main()


