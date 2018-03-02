#! /usr/bin/env python
import sys, os, shutil, db, generic, builddb, string
from releaseLog import *
from safecopy import *

class update(generic.update, builddb.builddb):
	def __init__(self,*args,**keyw): #{{{
		generic.update.__init__(self,*args,**keyw)
		builddb.builddb.__init__(self)

		#}}}

	def setProductID(self,releaseRequestID): #{{{
		result = self._db.Command("SELECT products_id FROM Builds.builds WHERE id=%s" % self.getBuildID(releaseRequestID))
		self.ProductID = result[0]['products_id']
		logInfo("executing  setProductID.  Setting class ProductID to %s" % result[0]['products_id'])

		#}}}

	def getBuildID(self,releaseRequestID): #{{{
		result = self._db.Command("SELECT builds_id FROM ReleaseAutomation.release_request WHERE id=%s" % releaseRequestID)
		logInfo("executing  getBuildID.  Input: %s. Returning %s" % (releaseRequestID, result[0]['builds_id']))
		maxBuild = result[0]['builds_id']

		if len(str(maxBuild)) == 6:
			maxBuild = '0' + str(maxBuild)

		return str(maxBuild)

		#}}}

	def getDestDir(self): #{{{
		'''Returns the directory where the updates will be copied to for this instantiation.'''
		result = self._db.Command("SELECT update_path FROM BuildCfg.products WHERE id=%s" % str(self.ProductID))
		logInfo("executing  getDestDir.  Returning %s" % result[0]['update_path'])
		return result[0]['update_path']

		#}}}

	def getZoneDirs(self): #{{{
		'''Returns a list of subdirectories under /ftp/arch/(dir) where this update needs to be copied on the zone.'''
		result = self._db.Command("SELECT * FROM ZoneCfg.dirs where products_id=%s" % self.ProductID)
		return result

		#}}}

	def getZoneArchs(self, dirID): #{{{
		'''Returns a list of architectures, given an ID of a zone subdirectory.'''
		result = self._db.Command("SELECT * FROM ZoneCfg.archs WHERE dirs_id=%s" % dirID)
		return map(lambda x: str(x['name']), result)

		#}}}

	def getZoneHosts(self, dirID): #{{{
		'''Returns a list of hosts, given an ID of a zone subdirectory.'''
		result = self._db.Command("SELECT * FROM ZoneCfg.hosts WHERE dirs_id=%s" % dirID)
		return map(lambda x: str(x['name']), result)

		#}}}

	def getZoneDirName(self, releaseRequestID): #{{{
		rpmDict = self.getRpmsForMerged(self.MergedID)
		print rpmDict['host-tool']
		packageType = self.getPackageType(releaseRequestID)
		appType = self.getPackageName()


		try:
			if packageType == 'cross':
				srcRpm = rpmDict['cross']['src']['src'][0]
			elif packageType == 'host':
				srcRpm = rpmDict['host']['src'][0]
			elif packageType == 'target':
				srcRpm = rpmDict['target']['src'][0]

		except:
			logErr('Source RPM was not returned from getRpmsForMerged.  Old update?')
			raise Exception, 'Source RPMs not found.  Aborting.'


		zoneDirName = string.replace(string.replace(string.strip(srcRpm),'hhl-'+appType+'-',''),'.src.rpm','') 
		return zoneDirName

		#}}}

	def getPackageName(self): #{{{
		'''Retrieve the name of the package we are updating.'''
		result = self._db.Command("SELECT name FROM ReleaseAutomation.merged WHERE id=%s" % str(self.MergedID))
		logInfo("executing  getPackageName.  Returning %s" % result[0]['name'])
		return result[0]['name']

		#}}}

	def getHighestBugID(self): #{{{
		'''Retrieve the highest ID of the bugs resolved by this update.'''
		result = self._db.Command("SELECT bug_id FROM ReleaseAutomation.combined WHERE merged_id=%s" % str(self.MergedID))
		returnval = max(map(lambda x: int(x['bug_id']) , result))
		logInfo("executing  getHighestBugID.  Returning %s" % returnval)
		return returnval

		#}}}

	def getHighestBuildID(self): #{{{
		'''Returns the most recent build ID of all the builds in this particular update instantiation.'''
		buildIDList = []
		result = self._db.Command("SELECT id FROM ReleaseAutomation.combined WHERE merged_id=%s" % str(self.MergedID))
		combinedIDList = map(lambda x: str(x['id']) , result)

		for combinedID in combinedIDList:
			results = self._db.Command("SELECT builds_id FROM ReleaseAutomation.release_request WHERE combined_id=%s" % combinedID)
			results = map(lambda x: str(x['builds_id']) , results)
			for result in results:
				buildIDList.append(result)

		#Need leading zeros.
		maxBuild = max(buildIDList)
		if len(maxBuild) == 6:
			maxBuild = '0' + maxBuild

		logInfo(" executing getHighestBuildID.  Returning %s" % maxBuild)
		return maxBuild

		#}}}

	def getBuildDir(self, releaseRequestID): #{{{
		'''Returns the directory of the build to pull the update from.'''
		buildID = self.getBuildID(releaseRequestID)
		result = self._db.Command("SELECT path FROM Builds.builds WHERE id=%s" % buildID)

		if not result:
			logError("The build that corresponds with release request %s does not exist in the db." % releaseRequestID)
			raise Exception, "The build for this update does not exist in the database.  Aborting."

		result = result[0]['path']

		if '/logs' in result:
			logError("Build directory contains '/logs'.  Should not be seeing this now.")
			raise Exception, "Bad build directory."
		else:
			logInfo("executing  getBuildDir.  Input: %s.  Returning: %s." % (releaseRequestID,result))
			return result

		#}}}

	def getAllArchs(self): #{{{
		'''Retrieve all architectures this update will be released for.'''
		result = self._db.Command("SELECT name FROM BuildCfg.archs WHERE products_id=%s AND released='Y'" % str(self.ProductID))
		logInfo("executing  getAllArchs")
		return filter(lambda x: x not in ['SRC', 'ALL', 'noarch', 'UCLIBC'], map(lambda x: str(x['name']) , result))

		#}}}
	
	def getArchID(self,name): #{{{
		'''Get a specific architecture ID'''
		result = self._db.Command("SELECT id FROM BuildCfg.archs WHERE products_id=%s AND name='%s'" % (str(self.ProductID), name))
		logInfo("executing  getArchID. Input: %s.  Returning: %s." % (name,result[0]['id']))
		return result[0]['id']

		#}}}

	def getHosts(self): #{{{
		'''Retrieve all the hosts this product is released for.'''
		result = self._db.Command("SELECT name FROM BuildCfg.hosts WHERE products_id=%s" % str(self.ProductID))
		logInfo("executing  getHosts for productID %s" % self.ProductID)
		return filter(lambda x: x not in ['SRC', 'ALL', 'noarch',], map(lambda x: str(x['name']) , result))

		#}}}

	def getHostID(self,name): #{{{
		'''Get a specific host ID'''
		result = self._db.Command("SELECT id FROM BuildCfg.hosts WHERE products_id=%s AND name='%s'" % (str(self.ProductID), name))
		logInfo("executing  getHostID.  Input: %s.  Returning: %s." % (name,result[0]['id']))
		return result[0]['id']

		#}}}

	def getReleaseRequests(self): #{{{
		''' Given a merged ID, generate release request ids that correspond to
			the combinedID from the most recent build.'''
		logInfo("executing  getReleaseReqeusts.")
		releaseList = []
		result = self._db.Command("SELECT id FROM ReleaseAutomation.combined WHERE merged_id=%s" % str(self.MergedID))
		combinedIDList = map(lambda x: str(x['id']) , result)
		
		for combinedID in combinedIDList:
			result = self._db.Command("SELECT combined_id,builds_id FROM ReleaseAutomation.release_request WHERE combined_id=%s" % combinedID)
			releaseIDList = map(lambda x: ( str(x['builds_id']) , str(x['combined_id']) ), result)

			for releaseID in releaseIDList:
				releaseList.append(releaseID)

		BID,CID=0,1
		highestBuild = 0
		newestCombinedID = 0

		for release in releaseList:
			if int(release[BID]) > highestBuild:
				highestBuild = int(release[BID])

		for release in releaseList:
			if int(release[BID]) == highestBuild:
				newestCombinedID = release[CID]

		if not newestCombinedID:
			raise Exception, "No combined ID exists -- something is wrong with the DB most likely."

		result = self._db.Command("SELECT id from ReleaseAutomation.release_request WHERE combined_id=%s" % newestCombinedID)
		return map(lambda x: str(x['id']) , result)

		#}}}

	def getPackageType(self, releaseRequestID): #{{{
		'''Retrieve the type of package (cross, host, target, etc..)'''
		packageName = self.getPackageName()
		result = self._db.Command("SELECT name,type FROM ReleaseAutomation.release_request WHERE id=%s" % releaseRequestID)
		if len(result) > 1:
			raise Exception, "testing debug stuff, this can be deleted."

		if result[0]['name'] == "cross-ramdisk":
			return "cross-common"

		logInfo("executing  getPackageType.  Input: %s.  Returning: %s." % (releaseRequestID,result[0]['type']))
		return result[0]['type']

		#}}}
	
	def getRpmExcludes(self): #{{{
		logInfo("executing  getRpmExcludes")
		result = self._db.Command("SELECT name FROM BuildCfg.rpmExcludes WHERE products_id=%s" % self.ProductID)
		return map(lambda x: str(x['name']) , result)

		#}}}

	def createTargetAppList(self, archID, srcDir, destDir): #{{{
		archName = self._db.Command("SELECT name FROM BuildCfg.archs WHERE id=%s" % archID)[0]['name']
		rpmDict = self.getRpmsForMerged(self.MergedID)

		sourceList = rpmDict['target']['src']
		for rpm in sourceList:
			try:
				safecopy(srcDir + "/SRPMS/" + rpm , destDir + "/SRPMS")
			except IOError: #test	
				pass
		try:
			return rpmDict['target'][archName]
		except KeyError:
			print "Arch %s is released for this product but not in the db." % archName
			logErr("Arch %s is released for this product but not in the db." % archName)
			return []

	#}}}

	def createHostAppList(self,host,srcDir,destDir): #{{{
		rpmDict = self.getRpmsForMerged(self.MergedID)

		if host == 'cluster':
			print "Host is defined here as cluster.  Skipping.  Copy may be incomplete, please check."
			return []

		sourceList = rpmDict['host']['src']
		for rpm in sourceList:
			try:
				safecopy(srcDir + '/SRPMS/' + rpm, destDir + '/SRPMS')
			except IOError:
				pass

		return rpmDict['host'][host]		

	#}}}

	def createHostToolAppList(self,host,srcDir,destDir): #{{{
		rpmDict = self.getRpmsForMerged(self.MergedID)

		if host == 'cluster':
			print "Host is defined here as cluster.  Skipping.  Copy may be incomplete, please check."
			return []

		sourceList = rpmDict['host-tool']['src']
		for rpm in sourceList:
			try:
				safecopy(srcDir + '/SRPMS/' + rpm, destDir + '/SRPMS')
			except IOError:
				pass

		return rpmDict['host-tool'][host]

	#}}}

	def createCrossAppList(self, hostID, archID, srcDir, destDir): #{{{
		hostName = self._db.Command("SELECT name FROM BuildCfg.hosts WHERE id=%s" % hostID)[0]['name']
		archName = self._db.Command("SELECT name FROM BuildCfg.archs WHERE id=%s" % archID)[0]['name']
		rpmDict = self.getRpmsForMerged(self.MergedID)

		sourceList = rpmDict['cross']['src']['src']

		for rpm in sourceList:
			try:
				safecopy(srcDir + "/SRPMS/" + rpm , destDir + "/SRPMS")
			except IOError:
				pass

		try:
			return rpmDict['cross'][archName][hostName]
		except KeyError:
			print "Arch %s Host %s copy failed." % (archName, hostName)
			return []

	#}}}

	def DEPRECATEDcreateAppList(self, releaseRequestID, archID=None, hostID=None, archString=None): #{{{
		'''Create and return a list of files to be copied given a release request, an architecture and/or a host.'''
		logInfo("executing  createAppList")
		results = self._db.Command("SELECT package_id FROM ReleaseAutomation.release_request WHERE id=%s" % releaseRequestID)
		buildID = self.getBuildID(releaseRequestID)
		packageID = results[0]['package_id']

		if archID and hostID:
			results = self._db.Command("SELECT * FROM rpm WHERE arch_id=%s AND host_id=%s AND package_id=%s AND build_id=%s" % \
										(archID,hostID,packageID,buildID))
		elif archID: #Target
			results = self._db.Command("SELECT name FROM Builds.targetRpms,Builds.targetMap WHERE targetMap_id=Builds.targetMap.id AND archs_id=%s AND targetPkgs_id=%s AND Builds.targetRpms.builds_id=%s" % (archID,packageID,buildID))
		elif hostID:
			results = self._db.Command("SELECT * FROM rpm WHERE host_id=%s AND package_id=%s AND build_id=%s" % (hostID,packageID,buildID))
		else:
			results = self._db.Command("SELECT * FROM rpm WHERE package_id=%s AND build_id=%s AND name LIKE '%%-%s-%%'" % (packageID,buildID,archString))

		excludeList = self.getRpmExcludes()
		appList = map(lambda x:  str(x['name']) , results)
		for app in appList:
			for exclude in excludeList:
				if exclude in app:
					appList.remove(app)

		return appList

	#}}}

	def _createSrcRPMList(self, releaseRequestID): #{{{
		'''Helper function for processSrcRPMS'''
		results = self._db.Command("SELECT builds_id, package_id,type FROM ReleaseAutomation.release_request WHERE id=%s" % releaseRequestID)
		buildID = self.getBuildID(releaseRequestID)
		packageType = str(results[0]['type'])
		packageID = results[0]['package_id']

		 
		results = self._db.Command("SELECT * FROM rpm WHERE package_id=%s AND build_id=%s" % (packageID,buildID))
		return map(lambda x: str(x['name']) , results)

	#}}}

	def processSrcRPMS(self, releaseRequestID, srcDir, destDir): #{{{
		'''Moves all the source RPMS for a release request.'''

		results = self._db.Command("SELECT name FROM release_request WHERE id=%s" % releaseRequestID)
		results = results[0]['name']

		if '-src' in results:
			rpmList = self._createSrcRPMList(releaseRequestID)
			for rpm in rpmList:
				safecopy(srcDir + "/SRPMS/" + rpm , destDir + "/SRPMS")
			logInfo("executing  processSrcRPMS.  Source update true, releaseRequestID: %s" % releaseRequestID)
			return True
		else:
			logInfo("executing  processSrcRPMS.  Source update false, releaseRequestID: %s" % releaseRequestID)
			return False

	#}}}

	def fixShit(self): #{{{ A hack until the Gen Collective is fixed.
		results =  self._db.Command("SELECT * FROM build WHERE path like '%%logs%%'")
		results = map(lambda x: [str(x['id']) , str(x['tag']) , str(x['path']) ],results )	
		for result in results:
			result[2] = result[2].replace('/logs' , '/%s' % result[1])
		for result in results:
			self._db.Command("UPDATE build SET path='%s' WHERE id=%s" % (result[2] , result[0]))
	#}}}
