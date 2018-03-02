#! /usr/bin/python

import re,sys,os,threading,traceback
from resourceManager import *

VERBOSE = 1
tarList = None
product = None
buildtag = None
pathToInstalls = None
nodetype = 'node'
globalLog = None
logLock = threading.Lock()

class TarInstallError(StandardError):
	pass


def doLog(logMsg):
	if globalLog == None:
		sys.stderr.write(logMsg)
	else:
		logLock.acquire()
		globalLog.write(logMsg)
		logLock.release()



def system(cmd):
	if VERBOSE:
		doLog("%s\n"%cmd)
		ret_code = os.system(cmd)
	else:
		ret_code = os.system(cmd)
	return ret_code

def doWork(work):
	#get arch
	try:
		installHost = getResource('install','install' ,nodetype,'Installing tarballs to engr_area')
		arch = re.match(r'\w+-host-(.*)-\d+\.tar\.bz2',work).group(1)
		dest = '/mvista/engr_area/%s/%s/%s'%(product,buildtag,arch)
		system('ssh %s "mkdir -p %s"'%(installHost,dest ))
		system('ssh %s "sudo tar -jxf %s/%s -C %s"'%(installHost,pathToInstalls,work,dest))
		system('ssh %s "sudo mv %s/opt/montavista %s/ "'%(installHost,dest,dest))
		system('ssh %s "sudo rmdir %s/opt/ "'%(installHost,dest))
	finally:
		releaseResource(installHost)	

def workerThread(lock):
	global tarList
	while(1):
		lock.acquire()
		if len(tarList) == 0:
			lock.release()
			return
		else:
			work = tarList.pop()
			lock.release()
			doWork(work)



def unpackTars(localProduct, localTag, logfile=None):
	global pathToInstalls, tarList, product, buildtag, globalLog
	if localProduct not in ('pro','cge','mobilinux','foundation','fe','mvl'):
		raise TarInstallError, "Bad product type: %s\n"%localProduct
	pathToInstalls = '/mvista/dev_area/%s/%s/installs'%(localProduct,localTag)
	if logfile != None:
		globalLog = open(logfile, 'w')

	if os.path.exists(pathToInstalls):
		tarList = os.listdir(pathToInstalls)
		product = localProduct
		buildtag = localTag
		lock = threading.Lock()
		i = 0
		threadList = []
		while i < len(tarList):
			threadList.append(threading.Thread(target=workerThread, args=(lock,)))
			i += 1
		for thread in threadList:
			thread.start()
		for thread in threadList:
			thread.join()
		globalLog.close()
	else:
		globalLog.close()
		raise TarInstallError, "The directory %s does not exist, check the buildtag\n"%(pathToInstalls)

def main(argv):
	if len(argv) != 3:
		sys.stderr.write("bad args\n")
		sys.stderr.write("%s <product> <buildtag> \n"%argv[0])
		sys.exit(1)
	try:
		unpackTars(argv[1],argv[2])
	except:
		traceback.print_exc()
		sys.stderr.write("Error installing tars, check the exception...\n")
		sys.exit(1)



if __name__ == "__main__":
	main(sys.argv)




