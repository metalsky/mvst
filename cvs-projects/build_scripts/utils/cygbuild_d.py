#!/usr/bin/python

import Pyro.core
import os, sys, re, string, threading, time

TEST = 0
VERBOSE = 0
ENV = 0
INSTALL = 1

Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

def system(cmd):
	if TEST:
		sys.stdout.write('%s\n'%cmd)

	elif VERBOSE:
		sys.stdout.write('%s\n'%cmd)
		os.system(cmd)
	else:
		os.system(cmd)

def today():
	return time.strftime("%y%m%d")

def exec_build():
	#Setup the build on /home/build
	buildDate = today()
	pythonpath = '/home/build/build_scripts/rpmlint/rpmlint-0.9.1-mv/:/home/build/bin/resourceManager/:/home/build/bin/common:/home/build/bin/utils'
	path = '/usr/local/bin:/usr/bin:/usr/X11R6/bin:/bin:/usr/openwin/bin:/sbin:/usr/sbin:/home/build/bin:/home/build/bin/utils'
	system('cp -a /home/build/cyg_test-exp /home/build/fdbtest%s_0700000-exp'%(buildDate))
	#execute
	system('export PATH=%s; export PYTHONPATH=%s; cd /home/build/fdbtest%s_0700000-exp/CVSREPOS/build_scripts/hhl; su build -c "./buildhhl.py fe fdbtest%s_0700000 0700000 HEAD f5_070604_0703292 prehley@mvista.com | mail build@mvista.com"'%(path, pythonpath, buildDate,buildDate))
	return


class CygBuild(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self.thread = None

	def build(self):
		self.thread = threading.Thread(target=exec_build())
		self.thread.start()
		return "Your build has been started"

def main():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon(port=7768)
	daemon.connect(CygBuild(), 'CygBuild')
	daemon.requestLoop()

if __name__ == "__main__":
	main()



