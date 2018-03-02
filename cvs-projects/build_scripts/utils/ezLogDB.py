#! /usr/bin/env python

import logDB,server
import sys,traceback

def _wrapper (method,*args):
	try:
		ldb = _connect()
		try:
			return method(ldb,*args)
		finally:
			ldb.getDB().Close()  # returns and exceptions do this first
	except:
		print >> sys.stderr,"-" * 72
		print >> sys.stderr,"ezLogDB: warning: caught exception [0]:", sys.exc_info()[0]
		print >> sys.stderr,"ezLogDB: warning: caught exception [1]:", sys.exc_info()[1]
		print >> sys.stderr,"ezLogDB: warning: caught exception [2]:", sys.exc_info()[2]
		traceback.print_exc()
		print >> sys.stderr,"-" * 72
		pass


def _connect():
    s = server.server()
    errmsg = s.Connect()
    if type(errmsg) == type(""):
	print errmsg
        raise Exception, "ezLogDB: couldn't connect to mysql server: " + errmsg
    return logDB.logDB(s)

def addBuild(*args):
    return _wrapper(logDB.logDB.addBuild,*args)
def addApp(*args):
    return _wrapper(logDB.logDB.addApp,*args)
def startApp(*args):
    return _wrapper(logDB.logDB.startApp,*args)
def finishApp(*args):
    return _wrapper(logDB.logDB.finishApp,*args)
def addTask(*args):
    return _wrapper(logDB.logDB.addTask,*args)
def startTask(*args):
    return _wrapper(logDB.logDB.startTask,*args)
def finishTask(*args):
    return _wrapper(logDB.logDB.finishTask,*args)
def finishBuild(*args):
    return _wrapper(logDB.logDB.finishBuild,*args)
def removeBuild(*args):
    return _wrapper(logDB.logDB.removeBuild,*args)

######################
#   main FUNCTION    #
######################

def main(argv):
	import sys
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)

if __name__ == "__main__":
        main(sys.argv)
