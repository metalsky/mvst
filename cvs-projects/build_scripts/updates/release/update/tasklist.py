#!/usr/bin/python

import sys
from release_d import IMMEDIATE, BACKGROUND

#This is a big list of tasks.  Each list entry is a tuple and they will ALL share a common format.

##########################FORMAT##############################
#  (funcName, className, moduleName, threadsafe, scheduleInterval)
##############################################################

#defines you can use for scheduling
#IMMEDIATE 
#BACKGROUND


tasklist = [
('imaginaryFunc','ImaginaryClass','imaginaryModule',IMMEDIATE),
#('testFunc',None,'testMod',30),
('classFunc','testClass','testMod',IMMEDIATE),
('releaseNewArch', 'update', 'update',IMMEDIATE),
('rmMerged','builddb','builddb',IMMEDIATE),
('rmCombined','builddb','builddb',IMMEDIATE),
('getReleasedArchs','builddb','builddb',IMMEDIATE),
('getReleasedHosts','builddb','builddb',IMMEDIATE),
('getRpmsForMerged','builddb','builddb',IMMEDIATE),
('getRpmsForCombined','builddb','builddb',IMMEDIATE),

]

if __name__=="__main__":
	print "No manual execution of this module"
	sys.exit(1)


