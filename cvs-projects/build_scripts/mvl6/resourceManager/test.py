#!/usr/bin/python

#### This is a script to test the resource manager ####

from resourceManager import getResource,releaseResource  #This is all it should take

resource = getResource("pea12345_123415","123415","solaris","Test Checkout")
print "I have resource: %s"%(resource)

raw_input("Press Enter to release resource")

releaseResource(resource)

