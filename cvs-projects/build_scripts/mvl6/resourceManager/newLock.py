#!/usr/bin/python

import os, sys
import lock

print "blach"

retVal = lock.getLock(1)
print retVal
print "got lock"
raw_input("enter to release lock")
lock.releaseLock()
