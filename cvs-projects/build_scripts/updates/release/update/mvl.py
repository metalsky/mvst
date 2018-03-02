#!/usr/bin/env python
DEBUG = 1
import mvltools
import os
import shutil
import string
from safecopy import *
from releaseLog import *

def system(instring):
	if DEBUG:
		print instring
	else:
		os.system(instring)
		
def passer(instring):
	print "in debug mode, shouldnt be using os.system!"	

class update(mvltools.update):
#	def __init__(self,args):
#		mvltools.update.__init__(self,args)

	def pushToTesting(self, merged_id):
		self.MergedID = merged_id
		for releaseRequestID in self.getReleaseRequests():
			self.extractRpms(releaseRequestID)
		logInfo('Update %s pushed to testing server.' % merged_id)

	def pushToLive(self, merged_id):
		self.MergedID = merged_id
		for releaseRequestID in self.getReleaseRequests():
			self.updateZone(releaseRequestID)
		logInfo('Update %s pushed to mv zone' % merged_id)

	def removeFromTesting(self, merged_id):
		self.MergedID = merged_id
		for releaseRequestID in self.getReleaseRequests():
			self._removeFromTesting(releaseRequestID)
		logInfo('Update %s removed from testing server' % merged_id)

	def removeFromLive(self, merged_id):
		self.MergedID = merged_id
		for releaseRequestID in self.getReleaseRequests():
			self._removeFromLive(releaseRequestID)
		logInfo('Update %s removed from mv zone' % merged_id)


	

	def _removeFromTesting(self, releaseRequestID): #{{{
		self.setProductID(releaseRequestID)
		destDir = self.getDestDir()

		if DEBUG:
			destDir = '/home/rell' + destDir

		destDir += '/' + self.getPackageName() + '-' + str(self.getHighestBugID()) + '-' + str(self.getBuildID(releaseRequestID))

		try:
			print "Removing directory %s" % destDir
			shutil.rmtree(destDir)
		#Since multiple ID's may have the same dir, we need to silently fail here.
		except OSError:
			pass
		#}}}

	def _removeFromLive(self, releaseRequestID):
		self.setProductID(releaseRequestID)

		if DEBUG:
			destDir = '/home/rell/mvista/ftp/arch'
		else:
			destDir = '/mvista/ftp/arch'

		updateDirName = self.getZoneDirName(releaseRequestID)
		zoneDirs = self.getZoneDirs()

		for dir in zoneDirs:
			try:
				dirToDelete = os.path.join(destDir, dir['name'], 'updates', updateDirName)
				print "Removing directory %s" % dirToDelete
				shutil.rmtree(dirToDelete)
			except OSError:
				pass


	def extractRpms(self, releaseRequestID, destPath=None): #{{{
		'''	Moves the files needed for this release request into the update directory.
			Dirs are populated as follows:

			target:
				/update path/app path/$arch/target (for all archs)
			cross:
				/update path/app path/$arch/cross/$host (for all archs,hosts)
			host:
				/update path/app path/host/$host   (for all hosts)
			host-tools:
				/update path/app path/host-tools/$host (for all hosts)
			common:
				/update path/app path/host/common
		'''

		logInfo("In extractRPMs.  Initialization steps..")

		self.setProductID(releaseRequestID)	
		packageType = self.getPackageType(releaseRequestID)

		srcDir   = self.getBuildDir(releaseRequestID)

		if not destPath:
			destDir  = self.getDestDir()
		else:
			destDir = destPath

		#print "%s to %s" % (srcDir, destDir)

		if DEBUG:
			destDir = '/home/rell' + destDir

		destDir += '/' + self.getPackageName() + '-' + str(self.getHighestBugID()) + '-' + str(self.getBuildID(releaseRequestID))

		#Make the SRPM directory regardless of the package type.
		if not os.path.exists(os.path.join(destDir,"SRPMS")):
			os.makedirs(os.path.join(destDir,"SRPMS"))

		if packageType == 'target':
			logInfo("processing target package.")
			#If this release request represents source rpms, copy them and finish.
			#if self.processSrcRPMS(releaseRequestID, srcDir, destDir):
			#	return

			archList = self.getAllArchs()
			for arch in archList:
				logInfo("processing arch %s" % arch)
				targetDir = os.path.join(destDir,arch,"target")
				archID = self.getArchID(arch)
				appList = self.createTargetAppList(archID,srcDir,destDir)
				for app in appList:
					logInfo("processing app %s" % app)
					if not os.path.exists(targetDir):
						os.makedirs(targetDir)
					if DEBUG:
						pass
						print "processing target app %s" % app
					if os.path.exists(os.path.join(srcDir,arch,"target",app)):
						safecopy(os.path.join(srcDir,arch,"target",app), targetDir)
					elif os.path.exists(os.path.join(srcDir,arch,"target","optional",app)):
						if not os.path.exists(os.path.join(targetDir,"optional")):
							os.makedirs(os.path.join(targetDir,"optional"))
						safecopy(os.path.join(srcDir,arch,"target","optional",app) , os.path.join(targetDir,"optional"))
					else:	
						raise Exception, "This target app does not exist.  Something is wrong.  Aborting. \n %s" % os.path.join(srcDir,arch,"target",app)

		elif packageType == 'host':	
			logInfo("processing host package.")
			
			hostList = self.getHosts()
			for host in hostList:
				logInfo("processing host %s" % host)
				appList = self.createHostAppList(host, srcDir, destDir)
				for app in appList:
					logInfo("processing app %s" % app)
					if not os.path.exists(os.path.join(destDir,"host",host)):
						os.makedirs(os.path.join(destDir,"host",host))
					if DEBUG:
						print "processing host app %s" % app
					safecopy(os.path.join(srcDir,"host",host,app) , \
						 os.path.join(destDir,"host",host))


		elif packageType == 'host-tool':	
			logInfo("processing host-tool package.")
			
			hostList = self.getHosts()
			for host in hostList:
				logInfo("processing host %s" % host)
				appList = self.createHostToolAppList(host, srcDir, destDir)
				for app in appList:
					logInfo("processing app %s" % app)
					if not os.path.exists(os.path.join(destDir,"host-tools",host)):
						os.makedirs(os.path.join(destDir,"host-tools",host))
					if DEBUG:
						print "processing host-tool app %s" % app
					safecopy(os.path.join(srcDir,"host-tools",host,app) , \
						 os.path.join(destDir,"host-tools",host))



				
		elif packageType == 'cross':
			logInfo("processing cross package.")
			#if self.processSrcRPMS(releaseRequestID, srcDir, destDir):
			#	return

			for host in self.getHosts():
				for arch in self.getAllArchs():
					logInfo("processing host-arch pair %s/%s" % (host,arch))
					appList = self.createCrossAppList(self.getHostID(host),self.getArchID(arch), srcDir, destDir)
					for app in appList:
						logInfo("processing app %s" % app)
						if not os.path.exists( os.path.join(destDir,arch,"cross",host) ):
							os.makedirs(os.path.join(destDir,arch,"cross",host) )
						if DEBUG:
							print "processing cross app %s" % app
						safecopy(os.path.join(srcDir,arch,"cross",host,app) , \
									 os.path.join(destDir,arch,"cross",host) )		

		elif packageType == 'cross-common':
			logInfo("processing cross noarch package.")
			#if self.processSrcRPMS(releaseRequestID, srcDir, destDir):
			#	if DEBUG:
					#print "Processing Source RPMs."
				#return

			for arch in self.getAllArchs():
				logInfo("processing arch %s" % arch)
				appList =  self.createAppList(releaseRequestID, archString=arch)
				for app in appList:
					logInfo("processing app %s" % app)
					if not os.path.exists( os.path.join(destDir,arch,"cross","common") ):
						os.makedirs( os.path.join(destDir,arch,"cross","common") )
					if DEBUG:
						print "processing cross-common app %s" % app
					safecopy(os.path.join( srcDir,arch,"cross","common",app) , \
							 os.path.join( destDir,arch,"cross","common" ))

#		elif packageType == 'host-tool':
#			for host in self.getHosts():
#				pass#returnList.append(destDir + "/host-tools/" + host)
		else:
			raise Exception, "Package type mismatch. Contact rell@mvista.com with the ID of this request."

		#}}}

	def updateZone(self, releaseRequestID): #{{{
		self.setProductID(releaseRequestID)

		patchDir = self.getDestDir()

		if DEBUG:
			patchDir = '/home/rell' + patchDir

		updateDirName = self.getPackageName() + '-' + str(self.getHighestBugID()) + '-' + str(self.getBuildID(releaseRequestID))

		print os.path.join(patchDir, updateDirName)


		if os.path.exists(os.path.join( patchDir, updateDirName)):
			patchDir = os.path.join(patchDir, updateDirName)
		else:
			patchDir = '/tmp/' + self.getPackageName() + '-' + str(self.getHighestBugID()) + '-' + str(self.getBuildID(releaseRequestID))
			self.extractRpms(releaseRequestID, '/tmp')

		if DEBUG:
			patchDir = '/home/rell' + patchDir
			destDir = '/home/rell/mvista/ftp/arch' 
		else:
			destDir = '/mvista/ftp/arch'

		updateDirName = self.getZoneDirName(releaseRequestID)
		zoneDirs = self.getZoneDirs()
		
		for dir in zoneDirs:
			for arch in self.getZoneArchs(dir['id']):
				safecopy(os.path.join(patchDir, arch) , os.path.join(destDir, dir['name'], 'updates', updateDirName, arch))
				logInfo('Processing arch %s (zone)' % arch)
				
			for host in	self.getZoneHosts(dir['id']):
				safecopy(os.path.join(patchDir, 'host', host) , os.path.join(destDir, dir['name'], 'updates', updateDirName, 'host', host) )
				logInfo('Processing host %s (zone)' % host)


			safecopy(os.path.join(patchDir,'SRPMS') , os.path.join(destDir, dir['name'], 'updates', updateDirName, 'SRPMS'))
			logInfo('Processing SRPM %s (zone)' % updateDirName)


		#}}}
