#!/usr/bin/python

import Pyro.core
import sys, os, string, traceback, re, getpass
from env_setup_class import *

Pyro.core.initClient(0)
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
envSetup = Pyro.core.getProxyForURI("PYROLOC://127.0.0.1:7766/env_setup")


def abort():
	print "Invalid Syntax.  Perhaps you need --help."
	sys.exit(1)

def usage(cmd):
	#sys.stderr.write("\n Usage for new env: %s env <centos3/redhat90> <pathToInstall>"%cmd)
	#sys.stderr.write("\n Usage for new build: %s build <pathToInstall>"%cmd)
	#sys.stderr.write("\nYes, you will get better instructions later.\n")
	
	print """
Description: 
%s sets up an environment and a build for testing purposes

Usage:
%s [OPTION]

Mandatory Options:

 --build [path]    Specifies path to build/arch (i.e. /mvista/engr_area/pro/blackfoot070607_1234567/x86_586 )

 --chroot [envname] Specifies the chroot environment. Supported chroots are: redhat90 centos3

::*NOTE*:: --build MUST be specified if you are using --chroot.

<examples>
 %s --build /mvista/engr_area/pro/blackfoot070607_1234567/x86_586 --chroot centos3
 %s --build /mvista/engr_area/pro/blackfoot070607_1234567/x86_586

""" % (cmd, cmd, cmd, cmd)
	
	sys.exit(1)


def getChroot():
	list = os.listdir('/chroot/%s/'%getpass.getuser())
	if len(list) != 1:
		raise SetupError
	else:
		return list[0]



def installSetup(installedDir, envName=None):
	try:
		sys.stdout.write("Setting up build\n")
		code = envSetup.setupInstall(getpass.getuser(), installedDir, envName)
	except InstallError:
		sys.stderr.write("Cannot find: %s\n"%installedDir)
		sys.exit(1)
	except EnvError:
		sys.stderr.write("Could not find chroot environment... perhaps you need to specify --chroot\n")
		sys.exit(1)

	except:
		sys.stderr.write("Unknown error setting up build, please send error below to build@mvista.com\nTRACEBACK\n########\n")
		traceback.print_exc()
		sys.exit(1)

	if code:
		sys.stderr.write("Build Setup Successful\n")
	else:	
		sys.stderr.write("Error setting up build, please contact build@mvista.com\n")

def chrootSetup(chrootEnv, installedDir):
	#setup chroot
	try:
		sys.stdout.write("Setting up Chroot\n")
		code = envSetup.setupEnvironment(getpass.getuser(), chrootEnv)

	except EnvError:
		sys.stderr.write("Chroot: %s not supported"%chrootEnv)
		sys.exit(1)

	except SetupError:
		sys.stderr.write("There was a problem in the setup of the machine, please send error below to build@mvista.com\nTRACEBACK\n########\n")
		traceback.print_exc()
		sys.exit(1)
	except:
		sys.stderr.write("Unknown error setting up chroot, please send error below to build@mvista.com\nTRACEBACK\n########\n")
		traceback.print_exc()
		sys.exit(1)

	if code:
	#If that goes well, setup install
		sys.stderr.write("Environment setup successful, installing build....\n")
		installSetup(installedDir, chrootEnv)
	else:
		sys.stderr.write("There was an error setting up the chroot, please contact build@mvista.com\n")
		sys.exit(1)


def verifyRequest(installDir, chrootEnv=None):
	legacy =('redhat90',)
	current = ('centos3',)
	if chrootEnv == None:
		try:
			chrootEnv = getChroot()
			sys.stderr.write("I have your chroot as: %s\n"%chrootEnv)
		except:
			sys.stderr.write("I couldn't find your chroot, this is likely a script error\n")
			sys.exit(1)
	
	#Get path to mvl-release
	releasePath = os.popen('find %s 2> /dev/null | grep mvl-release'%installDir).readline()
	releasePath = string.strip(releasePath,'\n')
	if not os.path.isfile(releasePath):
		print releasePath
		raise InstallError

	#Grab Version	
	if int(re.search(r' Version (\d)',os.popen('cat %s'%releasePath).readline()).group(1)) < 5:
		if chrootEnv not in legacy:
			raise VersionError
	else:
		if chrootEnv not in current:
			raise VersionError
	return


def main(argv):
	
	if "--help" in argv:
		usage(argv[0])
		sys.exit(1)
    #Fetch the install directory.  If not specified, abort.
	try:
		installDir = argv[argv.index("--build") + 1]
	except: 
		installDir = None

	try:
		chrootEnv = argv[argv.index("--chroot") + 1]
	except: 
		chrootEnv = None



	if chrootEnv == None and installDir == None:
		abort()

	elif chrootEnv != None and installDir != None: 
		sys.stderr.write("Chroot env: %s\n"%chrootEnv)
		sys.stderr.write("Build: %s\n"%installDir)
		try:
			verifyRequest(installDir, chrootEnv)
		except VersionError:
			sys.stderr.write("\nError: Your chroot environment is incompatible with the product you have selected\n\n")
			sys.stderr.write("Information on supported hosts is available in section 4.1 of:\n")
			sys.stderr.write("http://wiki.sh.mvista.com/thebazaar2/bin/view/Engineering/EngineeringServer\n\n")
			sys.exit(1)
		except InstallError:
			sys.stderr.write("Error: I could not find mvl-release, perhaps there is an error in the build you have specified.\n")
			sys.stderr.write("Please double check your build tag and try again, if the problem persists please contact build@mvista.com\n")
			sys.exit(1)

		chrootSetup(chrootEnv,installDir)
		sys.stderr.write("Complete!  Use the command 'mychroot' to enter your environment\n")
		sys.exit(1)

	elif installDir != None:
		sys.stderr.write("Build: %s\n"%installDir)
		try:
			verifyRequest(installDir)
		except VersionError:
			sys.stderr.write("\nError: Your chroot environment is incompatible with the product you have selected\n\n")
			sys.stderr.write("Information on supported hosts is available in section 4.1 of:\n")
			sys.stderr.write("http://wiki.sh.mvista.com/thebazaar2/bin/view/Engineering/EngineeringServer\n\n")
			sys.exit(1)

		installSetup(installDir)
		sys.stderr.write("Complete!  Use the command 'mychroot' to enter your environment\n")
       		sys.exit(1) 
	else:
		abort()
		
	
	

if __name__=="__main__":
	main(sys.argv)


