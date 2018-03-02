#!/usr/bin/python

import Pyro.core
import os, sys, re, string
from env_setup_class import *

VERBOSE = 0
ENV = 0
INSTALL = 1

Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
supportedEnvs = ('redhat90','centos3','centos3_64')

def system(cmd):
	if VERBOSE:
		sys.stdout.write('%s\n'%cmd)
	os.system(cmd)


class EnvSetup(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)

	def getEnvName(self,username):
		list = os.listdir('/chroot/%s/'%username)
		if len(list) != 1:
			raise SetupError
		else:
			return list[0]

	def checkMounts(self,username, code):
		if code == ENV:
			return 1
		if code == INSTALL:
			return 1

	def getuid(self, username):
		return string.strip(os.popen('id -u %s'%username).readline(),'\n')

	def setupEnvironment(self,username,envName):
		if envName not in supportedEnvs:
			raise EnvError

		if os.path.exists('/chroot/%s/'%username):
			sys.stdout.write('Cleaning up old environment')
			oldEnv = self.getEnvName(username)
			system('umount /chroot/%s/%s/proc'%(username,oldEnv))
			system('umount /chroot/%s/%s/home/%s'%(username,oldEnv,username))
			system('umount /chroot/%s/%s/mvista/engr_area'%(username,oldEnv))
			system('umount /chroot/%s/%s/opt/montavista'%(username,oldEnv))
			system('rm -rf /chroot/%s/*'%username)
		else:
			system('mkdir -p /chroot/%s'%username)

		os.chdir('/chroot/%s/'%username)
		sys.stdout.write('\nUntarring chroot environment....')
		system('tar -jxf /mvista/dev_area/buildtars/%s.tar.bz2'%envName)
		sys.stdout.write('\nSetting up mounts...')
		system('mount -t proc proc /chroot/%s/%s/proc'%(username,envName))
		system('mkdir -p /chroot/%s/%s/home/%s'%(username,envName,username))
		system('mount -t nfs schomes01:/vol/homedirs/%s /chroot/%s/%s/home/%s'%(username,username,envName,username))
		system('mkdir -p /chroot/%s/%s/mvista/engr_area'%(username,envName))
		system('mount -t nfs dumbo.sh.mvista.com:/vol/engr_area /chroot/%s/%s/mvista/engr_area'%(username,envName))
		uid = self.getuid(username)
		system('echo "%s::%s:510::/home/%s:/bin/bash" >> /chroot/%s/%s/etc/passwd  '%(username, uid, username, username,envName))
		system('echo "127.0.0.1 localhost" >> /chroot/%s/%s/etc/hosts'%(username,envName))
		return self.checkMounts(username, ENV)

	def setupInstall(self, username, installed, envName=None):
		if not os.path.exists(installed):
			raise InstallError
		if envName == None:
			envName = self.getEnvName(username)
		#if its still none then we have an issue with the Environment
		if envName == None:
			raise EnvError
		#umounts are harmless so we don't care
		sys.stdout.write('Umounting former installs, ignore error messages...\n')
		system('umount /chroot/%s/%s/opt/montavista'%(username,envName))
		sys.stdout.write('Mounting install to /chroot/%s/%s/opt/montavista...\n'%(username,envName))
		installed = re.sub('mvista','vol',installed) #we're mounting so /mvista is effectively /vol
		system('mount -t nfs dumbo.sh.mvista.com:%s/montavista /chroot/%s/%s/opt/montavista'%(installed,username,envName))
		sys.stdout.write('Verifying...\n')
		return self.checkMounts(username, INSTALL)
			
		
def main():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon()
	daemon.connect(EnvSetup(), 'env_setup')
	daemon.requestLoop()

if __name__ == "__main__":
	main()



