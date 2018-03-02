#!/usr/bin/python

import syslog, sys

syslog.openlog('release',0,syslog.LOG_LOCAL0)

def logInfo(msg):
	syslog.syslog(syslog.LOG_INFO,msg)

def logDebug(msg):
	syslog.syslog(syslog.LOG_DEBUG,msg)

def logErr(msg):
	syslog.syslog(syslog.LOG_ERR,msg)

def logCrit(msg):
	syslog.syslog(syslog.LOG_CRIT,msg)

def main():
	sys.stderr.write('No Manual Execution of this module\n')
	sys.exit(1)

if __name__=="__main__":
	main()

