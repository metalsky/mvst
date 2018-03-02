import os, retentionLog
DEBUG = 1



def system(cmd, runCmd):
	if DEBUG and runCmd:
		retentionLog.logInfo("DEBUG: Running: %s" % cmd)
		os.system(cmd)
	elif DEBUG and not runCmd:
		print cmd
		retentionLog.logInfo("DEBUG: Not Running: %s" % cmd)
	elif not DEBUG:
		print cmd
		os.system(cmd)
