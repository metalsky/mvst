#!/usr/bin/python

#Standard
import threading, os, sys, time, traceback
#Pyro
import Pyro.core

#Zenoss
import Globals
from Products.ZenUtils.ZenScriptBase import ZenScriptBase
from transaction import commit

SUCCESS = 1
TEST = 0

BUILDMASTER = 'overlord'

class ZenClass(ZenScriptBase):
	pass

class MasterInstance(object):
	def __init__(self, buildtag, type):
		bdmd = ZenClass(connect=True)
		buildMasterDevice = bdmd.findDevice(BUILDMASTER)
		buildMasterDevice.addBuild(buildtag, type)	
		self.buildtag = buildtag
		commit()

	def getBuild(self):
		dmd = ZenClass(connect=True)
		buildmaster = dmd.findDevice(BUILDMASTER)
		return getattr(buildmaster.builds, self.buildtag, None)


class SubInstance(object):
	def __init__(self, buildtag, hostname, task):
		dmd = ZenClass(connect=True)
		subBuildDev = dmd.findDevice(hostname)
		buildmaster = dmd.findDevice(BUILDMASTER)
		build = getattr(buildmaster.builds, buildtag, None)
		subbuild = build.addSubBuild(subBuildDev.id, task)
		self.host = hostname
		self.id = subbuild.id
		self.buildtag = buildtag
		commit()

	def getSubBuild(self):
		dmd = ZenClass(connect=True)
		buildmaster = dmd.findDevice(BUILDMASTER)
		build = getattr(buildmaster.builds, self.buildtag, None)
		return getattr(build.subbuilds,self.id,None)



class ZenBuild(Pyro.core.SynchronizedObjBase):
	def __init__(self):
		Pyro.core.SynchronizedObjBase.__init__(self)
#		self.dmd = ZenClass(connect=True)
		self.builds = {}
		self.subbuilds = {}
		self.lock = threading.Lock()

	def showBuilds(self):
		return self.builds.keys()

	def regBuild(self, buildtag, type, ETA):
#		master = self.dmd.findDevice('overlord')
		self.lock.acquire()
		try:
			if self.builds.has_key(buildtag):
				del(self.builds[buildtag])
			self.builds[buildtag] =  MasterInstance(buildtag,type)
			buildRef = self.builds[buildtag].getBuild()
			#Basic Info
			buildRef.setStartTime(time.time())
			buildRef.setStatus('OK')
			buildRef.setStagePercentComplete(0)
			buildRef.setPercentComplete(0)
			buildRef.setEstimatedEndTime(ETA)
			buildRef.setEndTime(None)
			self.lock.release()

		except:
			self.lock.release()
			return "Error adding build\n\n%s"%traceback.format_exc()
		try:
			commit()
		except:
			return "Error adding build\n\n%s"%traceback.format_exc()

		return SUCCESS


	def unregBuild(self, buildtag):
		pass

	def regSubBuild(self, buildtag, hostname, task, ETA):
		if not self.builds.has_key(buildtag):
			return "Build Tag '%s' not found in zenoss"%buildtag

		self.lock.acquire()
		try:
#			self.dmd.dmd._p_jar.sync() #This is the sync function, the class isn't actually the dmd but accessor methods to the one it contains.
#			dev = self.dmd.findDevice(hostname)
			if self.subbuilds.has_key(hostname):
				del(self.subbuilds[hostname])
			self.subbuilds[hostname] = SubInstance(buildtag, hostname, task)
			buildRef = self.subbuilds[hostname].getSubBuild()
			buildRef.setStartTime(time.time())
			buildRef.setStatus('OK')
			buildRef.setPercentComplete(0)
			buildRef.setStagePercentComplete(0)
			buildRef.setEndTime(None)
			buildRef.setEstimatedEndTime(ETA)
			self.lock.release()
		except:
			self.lock.release()
			return "Error adding subbuild: %s"%traceback.format_exc()

		try:
			commit()
		except:
			return "Error adding subbuild\n\n%s"%traceback.format_exc()

		return SUCCESS

	def completeBuild(self, buildtag):
		if not self.builds.has_key(buildtag):
			return "Build Tag '%s' not found in zenoss"%buildtag

		try:
			buildRef = self.builds[buildtag].getBuild()
			buildRef.setStatus('FIN')
			buildRef.setPercentComplete(100)
			buildRef.setStage('Complete')
			buildRef.setStagePercentComplete(100)
			buildRef.setEndTime(time.time())
			buildRef.setEstimatedEndTime(None)
			self.lock.acquire()
			del self.builds[buildtag]
			self.lock.release()
		except:
			self.lock.release()
			return "Error: %s\n\n"%traceback.format_exc()

		try:
			commit()
		except:
			return "Error: \n\n%s"%traceback.format_exc()

		return SUCCESS

	def completeSubBuild(self, device):
		if not self.subbuilds.has_key(device):
			return "Device '%s' has not registered any subbuilds"%device

		try:
			buildRef = self.subbuilds[device].getSubBuild()
			buildRef.setStatus('FIN')
			buildRef.setPercentComplete(100)
			buildRef.setStage('Complete')
			buildRef.setStagePercentComplete(100)
			buildRef.setEndTime(time.time())
			buildRef.setEstimatedEndTime(time.time())
			commit()
		except:
			return "Error: %s"%traceback.format_exc()
		return SUCCESS





	def updateBuild(self, buildtag, stage=None, stagePercentComplete=None, percentComplete=None, ETA=None, status=None):
		if not self.builds.has_key(buildtag):
			return "Build Tag '%s' not found in zenoss"%buildtag
		try:
			buildRef = self.builds[buildtag].getBuild()
			if stage != None:
				buildRef.setStage(stage)
			if stagePercentComplete != None:
				buildRef.setStagePercentComplete(stagePercentComplete)
			if percentComplete != None:
				buildRef.setPercentComplete(percentComplete)
			if ETA != None:
				buildRef.setEstimatedEndTime(ETA) 
			if status != None:
				buildRef.setStatus(status)
			commit()
		except:
			return "Error: %s"%traceback.format_exc()
		return SUCCESS

	


	def updateSubBuild(self, device, stage=None, stagePercentComplete=None, percentComplete=None, ETA=None, status=None):
		if not self.subbuilds.has_key(device):
			return "Device '%s' has not registered any subbuilds"%device
		try:
			buildRef = self.subbuilds[device].getSubBuild()
			if stage != None:
				buildRef.setStage(stage)
			if stagePercentComplete != None:
				buildRef.setStagePercentComplete(stagePercentComplete)
			if percentComplete != None:
				buildRef.setPercentComplete(percentComplete)
			if ETA != None:
				buildRef.setEstimatedEndTime(ETA) 
			if status != None:
				buildRef.setStatus(status)
			commit()
		except:
			return "Error: %s"%traceback.format_exc()
		return SUCCESS

def startPyro():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon(port=7769)
	daemon.connect(ZenBuild(),'zenbuild')
	daemon.requestLoop()

def test():
	obj = ZenBuild()
	obj.regBuild('test123456','foundation')
	obj.updateBuild('test123456',stage='buildPrep',stagePercentComplete=20, percentComplete=5)
	obj.regSubBuild('test123456','node-2','buildPrep')
	obj.updateSubBuild('node-2',stage='Tagging Userland')
	obj.regSubBuild('test123456','node-24','buildPrep')
	obj.completeSubBuild('node-2')
	obj.completeSubBuild('node-24')
	obj.completeBuild('test123456')

def main():
	if TEST:
		test()
	else:
		startPyro()


if __name__=="__main__":
	main()

