#!/usr/bin/python

#rmlog - resource manager logger

#Functions for resource manager logging

import sys, time, os, traceback, syslog
from resourceError import ResourceError
import config
GET = 0
REL = 1

syslog.openlog('rmd',0,syslog.LOG_USER)

def logInfo(msg):
	syslog.syslog(syslog.LOG_INFO, msg)

def logErr(msg):
	syslog.syslog(syslog.LOG_ERR, msg)

def logCrit(msg):
	syslog.syslog(syslog.LOG_CRIT, msg)

def logDebug(msg):
	reload(config)
	if config.DEBUG:
		syslog.syslog(syslog.LOG_INFO, msg)


def main():
	sys.stderr.write('No Manual Execution of this module\n')
	sys.exit()


if __name__=="__main__":
  main()



