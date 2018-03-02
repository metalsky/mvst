#!/usr/bin/python

import Pyro.core
import sys, os, string, traceback, re
from env_setup_class import *

Pyro.core.initClient(0)
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
cygBuild = Pyro.core.getProxyForURI("PYROLOC://overlord.borg.mvista.com:7768/CygBuild")
print "Trying to launch build..."
print cygBuild.build()
print "An email will be sent out if the build completes"


