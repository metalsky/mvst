#!/usr/bin/python

#Normal
import sys, traceback, syslog
from types import *


#Pyro
try:
	import Pyro.core
except:
	logError(traceback.format_exc())

PYROSERVER = 'PYROLOC://overlord:7769/zenbuild'

Pyro.core.initClient(0)
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

LOG_FACILITY = syslog.LOG_LOCAL0

def logError(msg):
	syslog.openlog('ZENLIB', 0, LOG_FACILITY)
	syslog.syslog(syslog.LOG_ERR, msg)
	syslog.closelog()



def regBuild(buildtag, type, ETA=None):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.regBuild(buildtag, type, ETA)
	except:
		logError(traceback.format_exc())
		

def updateBuild(buildtag, stage=None, stagePercentComplete=None, percentComplete=None, ETA=None, status=None):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.updateBuild(buildtag,stage, stagePercentComplete, percentComplete, ETA, status)
	except:
		logError(traceback.format_exc())

def regSubBuild(buildtag, hostname, task, ETA=None):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.regSubBuild(buildtag,hostname,task, ETA)
	except:
		logError(traceback.format_exc())


def updateSubBuild(device, stage=None, stagePercentComplete=None, percentComplete=None, ETA=None, status=None):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.updateSubBuild(device, stage, stagePercentComplete, percentComplete, ETA, status)
	except:
		logError(traceback.format_exc())

def completeBuild(buildtag):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.completeBuild(buildtag)
	except:
		logError(traceback.format_exc())


def completeSubBuild(device):
	try:
		bdmd = Pyro.core.getProxyForURI(PYROSERVER)
		bdmd.completeSubBuild(device)
	except:
		logError(traceback.format_exc())

def test():
	regBuild('test666','test build')
	regBuild('foundation_test_1234','foundation')
	regSubBuild('test666', 'node-24', 'arm_iwmmxt_le target apps')
	updateBuild('test666',stage="Build Prep")
	print completeSubBuild('node-24')
	print completeBuild('test666')


def main():
	test()
	sys.exit(1)


if __name__=="__main__":
	main()


