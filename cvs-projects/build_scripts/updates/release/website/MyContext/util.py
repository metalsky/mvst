#!/usr/bin/python
import errataTemplate
import users
import notify

import copy
import sys
import time
from operator import itemgetter
from string import digits

import pyroServer
import socket

ErrType = type("")
IntType = type(1)
NoneType = type(None)

def getCurrentReleaseCycle(db):
	result = db.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE processed="N" AND closed="N"''')
	if type(result) == ErrType:
		return result
	
	if len(result) < 1:
		return '''There are no current cycles setup. Please file a bug.'''
	
	cycle_list = []
	for cycle in result:
		cycle_list.append(int(cycle['id']))
	
	cycle_list.sort()
	return cycle_list[0]
#end getCurrentReleaseCycle

class request:
	def __init__(self, db, bugzDB, pyro):
		self.db = db
		self.bugzDB = bugzDB
		self.Pyro = pyro.getObj()

		self.Name = ""
		self.BugID = None
		self.ProductID = None
		self.MergedIDs = []
		self.RequestIDs = []
		self.CycleID = None
		self.BuildIDs = []
		self.PackageIDs = {}
		self.Types = []
		self.UploadPriority = ""
		self.State = ""
		self.DateSubmitted = None
		self.Notes = ""

		self.SubmitterID = None
		self.SubmitterUser = ""
		self.SubmitterName = ""
		self.SubmitterEmail = ""
		self.Bug = None
		return


	def verify(self, submitter_id, submitter_user, name, bug_number, type_list, priority, notes):
		#Verify information was filled in
		result = self._verifyCompleteFields(submitter_id, submitter_user, name, \
				bug_number, type_list, priority)
		if type(result) == ErrType:
			return result

		#Set known fields
		self.Name = name
		self.BugID = int(bug_number)
		self.Types = type_list
		self.UploadPriority = priority
		self.Notes = notes
		self.SubmitterID = int(submitter_id)
		self.SubmitterUser = submitter_user
	
		#Get Submitter Info
		result = self.bugzDB.Command('''SELECT * FROM profiles WHERE userid=%d'''%(self.SubmitterID))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find user in database. Are you logged in?"

		self.SubmitterName = result[0]['realname']
		self.SubmitterEmail = result[0]['login_name']
	

		#Verify bug info
		result = self._verifyBug()
		if type(result) == ErrType:
			return result


		#Verify builds and packages
		result = self._verifyBuilds()
		if type(result) == ErrType:
			return result


		result = self._verifyRpmsBuilt()
		if type(result) == ErrType:
			return result

		result = self._verifyOverride()
		if type(result) == ErrType:
			return result

		return None

	

	def _verifyCompleteFields(self, submitter_id, submitter_user, name, bug_number, type_list, priority):
		errors = ""
		if len(str(submitter_user)) < 1:
			errors += "You must be logged in to submit a request.<br>\n"
		if len(str(submitter_id)) < 1:
			errors += "You need a bugz account to submit a request.<br>\n"
		if len(str(name)) < 1:
			errors += "You need to specify a package name.<br>\n"
		if len(str(bug_number)) < 1:
			errors += "You need to specify a bug number.<br>\n"
		if not type_list:
			errors += "You need to specify at least one package type.<br>\n"
		if not priority:
			errors += "You must select an upload priority.<br>\n"

		if errors:
			return errors

		return None


	
	def _verifyBug(self):
		
		result = self.bugzDB.Command('''SELECT * FROM bugs WHERE bug_id=%d'''%(self.BugID))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find bug: '%d' in bugzilla."%(self.BugID)

		self.Bug = result[0]

		#
		#Verify required fields are filled in
		#

		errors = ""
		bug_owner = self.Bug['assigned_to']

		if not self._userCanSubmit(bug_owner):
			return "Only the Bug Owner can submit an upload request.<br>\n"

			
		#Verify Customer Viewable
		customer_viewable = self.Bug['cust_viewdesc']
		if len(str(customer_viewable)) < 3:
			errors += "The Bug's Customer Viewable Field needs to be filled out.<br>\n"

		cv_flag = self.Bug['cust_viewflag']
		if str(cv_flag) != "Y":
			errors += "The Bug's Customer Viewable Flag needs to be checked.<br>\n"


		#Verify Status is set correctly
		status = self.Bug['bug_status']
		if str(status) != "VERIFIED" and str(status) != "CLOSED":
			errors += "The Bug needs to be marked VERIFIED or CLOSED.<br>\n"


		#Verify fixedin field 
		fixed_in = self.Bug['fixed_in']
		fixed_in = str(fixed_in).replace(',', ' ').replace(';', ' ')
		builds = fixed_in.split(' ')

		build_list = []
		for build in builds:
			build = build.strip()
			if len(build) > 3:
				build_list.append(build)
			
		if len(build_list) < 1:
			errors += "The FixedIn field needs to contain at least one BuildTag.<br>\n"

		if errors:
			return errors

		#
		#Verify information is correct
		#

		#verify build tags exists and are correct 
		for build in build_list:
			cut = build.rfind('_')
			if cut != -1:
				build_id = build[cut+1:]
			else:
				build_id = build
			
			build_id = filter(lambda d: d in digits, build_id)
			try:
				build_id = int(build_id)
			except:
				return "Found an invalid BuildID in the FixedIn Field: '%s'"%(fixed_in)

			result = self.db.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(build_id))
			if type(result) == ErrType:
				return result

			if len(result) < 1:
				return "Can't find BuildID '%s' in Databse"%(build_id)

			self.BuildIDs.append(int(build_id))
				

		return None

	def _verifyOverride(self):
		#First, if we are an edition, we don't care	
		result = self.db.Command('''SELECT foundation FROM BuildCfg.products WHERE id=%d'''%(self.ProductID))
		if type(result) == ErrType:
			return result
		if result[0]['foundation'] == 0:
			#Get all of the package names
			pakNames = []
			for build in self.BuildIDs:
				for i in range(len(self.PackageIDs[str(build)])):
					packid,packtype = self.PackageIDs[str(build)][i]
					pakNames.append(self._getPakName(packid,packtype))

			#Get editions for our foundation
			nextresult = self.db.Command('''SELECT id FROM BuildCfg.products WHERE foundation=%d'''%(self.ProductID))
			if type(result) == ErrType:
				return result
			#check the foundation override table for editions claiming to own each package in the request
			errors = []
			for name in pakNames: #For all of the packagse
				for item in nextresult: #try all of the products
					moreresults = self.db.Command('''SELECT * FROM BuildCfg.foundationOverride WHERE products_id=%d AND name='%s' '''%(int(item['id']),name))
					if len(moreresults) != 0:
						errors.append(name)

			if len(errors) > 0:
				return "The packages :: %s :: cannot be released from a foundation.  Please specify edition buildtags in the bug."%errors
			else:
				return None #Success case

		else:
			return None

	def _getPakName(self,pakID,pakType):
		if pakType in ('common','host-tool'):
			dbType = 'host'
		else:
			dbType = pakType
		result = self.db.Command('''SELECT name FROM Builds.%sPkgs WHERE id=%d'''%(dbType,int(pakID)))
		return result[0]['name']


	def _userCanSubmit(self, bug_owner):
		#pinocchio hack
		if socket.gethostname() == 'pinocchio':
			self.SubmitterID = int(bug_owner)
			return True

		if self.SubmitterID == int(bug_owner):
			return True	

		return False


	def _verifyBuilds(self):
		id_list = []
		tag_list = []
		for build in self.BuildIDs:
			result = self.db.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(build))
			if type(result) == ErrType:
				return result

			build_result = result[0]
			product_id = int(build_result['products_id'])
			self.ProductID = product_id

			if not product_id in id_list:
				id_list.append(product_id)
			else:
				result = self.db.Command('''SELECT * from BuildCfg.products WHERE id=%d'''%(product_id))
				if type(result) == ErrType:
					return result
				product = result[0]
				return "You listed more than one %s (%s) buid to pull from. You can only list one."%(product['edition'], product['tag_match'])
			#
			result = self.db.Command('''SELECT * from BuildCfg.products WHERE id=%d'''%(product_id))
			if type(result) == ErrType:
				return result
			product = result[0]
			tag_list.append(product['tag_match'])		
		#for builds

		#make sure product is released:
		for product_id in id_list:
			result = self.db.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(product_id))
			if type(result) == ErrType:
				return result
			product = result[0]
			if product['released'] == 'N':
				return "You are requesting an update for an unreleased product: %s %s"%(product['edition'], product['version'])
		#done



		result = self.db.Command('''SELECT * FROM ReleaseAutomation.f1_exempt''')
		if type(result) == ErrType:
			return result
		matched = False
		for exempt in result:
			if self.Name.find(exempt['name']) != -1:
				matched = True
		#done
		if not matched:
			if "fb" in tag_list and not "fe64b" in tag_list:
				return "You listed a foundationOne build, but no foundationOne_64 build."
			if "fe64b" in tag_list and not "fb" in tag_list:
				return "You listed a foundationOne_64 build, but no foundationOne build."
			if not "fb" in tag_list and not "fe64b" in tag_list:
				if len(tag_list) > 1:
					return "You have listed more that one build in the fixed_in field, but that is only allowed for foundationOne/foundationOne_64"
		#non toolchain f1 build check

		#look for packages
		for build in self.BuildIDs:
			self.PackageIDs[str(build)] = []
			for package_type in self.Types:
				package_name = self.Name
				if package_type != "target":
					if package_name.find(package_type) < 0:
						package_name = package_type+"-"+package_name
					#else
				#else
				
				if package_type in ('host','host-tool','common'):
					dbtype = 'host'
				else:
					dbtype = package_type
				for tag in ["", "-n64", "-o32", "-32", "-64", "-src"]:
					wild_name = package_name+tag
					result = self.db.Command('''SELECT * FROM Builds.%sPkgs WHERE builds_id=%d AND name="%s"'''%(dbtype, build, wild_name))
					if type(result) == ErrType:
						return result

					if tag == "":
						if len(result) < 1:
							return '''Can't find package: "%s" of type: "%s" in BuildID: "%d"'''%(package_name, package_type, build)
					for package in result:
						self.PackageIDs[str(build)].append((package['id'],package_type))

				#end for tag
			#end for Types
		#end for BuildIDs

		return None
	#end _verifyBuilds

	def _rpmFail(self, p_id, pkg_type, buildid, result):
		if pkg_type in ('target','cross'):
			hostarch = 'archs'
		else:
			hostarch = 'hosts'

		pkgs = self.db.Command('''SELECT %sPkgs.name,%sMap.%s_id FROM Builds.%sPkgs,Builds.%sMap WHERE %sPkgs.id=%sMap.%sPkgs_id AND %sPkgs.id=%d AND %sMap.builds_id=%d limit 1'''%(pkg_type,pkg_type,hostarch,pkg_type,pkg_type,pkg_type,pkg_type,pkg_type,pkg_type,p_id,pkg_type,int(buildid)))
		if type(pkgs) == ErrType:
			return pkgs
		
		packName = pkgs[0]['name']

		archResult = self.db.Command('''SELECT name FROM BuildCfg.%s WHERE id=%d'''%(hostarch,result['%s_id'%hostarch]))
		if type(archResult) == ErrType:
			return archResult
		archNames = archResult[0]['name']

		if pkg_type == 'cross':
			hostResult = self.db.Command('''SELECT name FROM BuildCfg.hosts WHERE id=%d'''%(result['hosts_id']))
			if type(hostResult) == ErrType:
				return hostResult 
			crossHost = hostResult[0]['name']
			
		buildtags = self.db.Command('''SELECT buildtag FROM Builds.builds WHERE id=%d'''%(int(buildid)))
		buildtag = buildtags[0]['buildtag']

		if pkg_type == 'cross':
			return "Error: Rpms for '%s' were not produced in Build '%s' for arch: '%s' host: '%s' "%(packName,buildtag,archNames,crossHost)
		else:
			return "Error: Rpms for '%s' were not produced in Build '%s' for %s: '%s'"%(packName,buildtag,hostarch, archNames)

	#end _rpmFail


	def _verifyRpmsBuilt(self):
		print "verify"
		failList = ""
		for buildid in self.BuildIDs:
			for package in self.PackageIDs[str(buildid)]:
				p_id = package[0]
				pkg_type = package[1]
				print "verify:", package
				if pkg_type == 'target':
					archs = self.Pyro.exec_task("getReleasedArchs",method_args=(buildid, self.ProductID,))
					if type(archs) == ErrType:
						return archs
					for arch in archs:
						result = self.db.Command('''SELECT * FROM Builds.targetPkgs,Builds.targetMap WHERE targetPkgs.id=targetMap.targetPkgs_id AND targetPkgs.id=%d AND targetMap.archs_id=%d AND targetMap.builds_id=%d AND targetMap.built='N' '''%(p_id,arch['id'],buildid))
						if len(result) > 0 :
							failList += "%s<br>"%self._rpmFail(p_id,pkg_type,buildid,result[0])

				elif pkg_type in ('host','host-tool','common'):
					hosts = self.Pyro.exec_task("getReleasedHosts",method_args=(self.ProductID,))
					if type(hosts) == ErrType:
						return hosts
					for host in hosts:
						result = self.db.Command('''SELECT * FROM Builds.hostPkgs,Builds.hostMap WHERE hostPkgs.id=hostMap.hostPkgs_id AND hostPkgs.id=%d AND hostMap.hosts_id=%d AND hostMap.builds_id=%d AND hostMap.built='N' '''%(p_id,host['id'],buildid))
						if len(result) > 0:
							failList += "%s<br>"%self._rpmFail(p_id,pkg_type,buildid,result[0])

				elif pkg_type == 'cross':
					archs = self.Pyro.exec_task("getReleasedArchs",method_args=(buildid, self.ProductID,))
					hosts = self.Pyro.exec_task("getReleasedHosts",method_args=(self.ProductID,))
					if type(archs) == ErrType:
						return archs
					if type(hosts) == ErrType:
						return hosts

					for arch in archs:
						for host in hosts:
							result = self.db.Command('''SELECT * FROM Builds.crossPkgs,Builds.crossMap WHERE crossPkgs.id=crossMap.crossPkgs_id AND crossPkgs.id=%d AND crossMap.hosts_id=%d AND crossMap.builds_id=%d AND crossMap.archs_id=%d AND crossMap.built='N' '''%(p_id,host['id'],buildid,arch['id']))
							if len(result) > 0:
								failList += "%s<br>"%self._rpmFail(p_id,pkg_type,buildid,result[0])


		if len(failList) > 0:
			return failList
		#else
		return None

	#end _verifyBuiltRpms


	def submit(self):
		self.DateSubmitted = time.strftime("%Y-%m-%d", time.localtime())

		#setup priority and state
		self.State = "approved"
		
		if self.UploadPriority == "ASYNC-CRITICAL":
			self.UploadPriority = "async"
			self.State = "waiting"

		self.UploadPriority = self.UploadPriority.lower()
	
		self.db.Start()
		current_cycle_id = getCurrentReleaseCycle(self.db)
		if type(current_cycle_id) == ErrType:
			return result

		if self.UploadPriority == "async":
			merged_id = None
			process = time.strftime("%Y-%m-%d", time.localtime())
			live = "0000-00-00"
			
			#Move from current cycle to async?
			result = self.db.Command('''SELECT id FROM ReleaseAutomation.merged WHERE name="%s" AND products_id=%d AND release_cycle_id=%d'''%(self.Name, self.ProductID, current_cycle_id))
			if type(result) == ErrType:
				return result
			if len(result) > 0:
				merged_id = result[0]['id']


			result = self.db.Command('''INSERT INTO ReleaseAutomation.release_cycle (process_date,live_date,processed,closed,async) VALUES ("%s", "%s", "N", "Y", "Y")'''%(process, live))
			if type(result) == ErrType:
				return result
			result = self.db.Command('''SELECT LAST_INSERT_ID()''')
			if type(result) == ErrType:
				return result
			self.CycleID = int(result[0]['LAST_INSERT_ID()'])


			#Now move the merged request to the async
			if merged_id:
				result = self.db.Command('''UPDATE ReleaseAutomation.merged SET release_cycle_id=%d WHERE id=%d'''%(self.CycleID, merged_id))
				if type(result) == ErrType:
					return result

		else:
			self.CycleID = current_cycle_id

		#Find/add merged request
		result = self.db.Command('''SELECT id FROM ReleaseAutomation.merged WHERE name="%s" AND products_id=%d AND release_cycle_id=%d'''%(self.Name, self.ProductID, self.CycleID))
		if type(result) == ErrType:
			return result

		if len(result) > 0:
			merged = result[0]
			self.MergedID = int(merged['id'])
			result = self.db.Command('''UPDATE ReleaseAutomation.merged SET state="approved", action_date="%s" WHERE id=%d'''%(self.DateSubmitted, self.MergedID))
			if type(result) == ErrType:
				return result
		else:
			#Add new merged:
			result = self.db.Command('''INSERT INTO ReleaseAutomation.merged (name,severity,release_cycle_id,state,action_date,products_id) VALUES("%s", "%s", %d, "%s", "%s", %d)'''%(self.Name, self.UploadPriority, self.CycleID, self.State, self.DateSubmitted, self.ProductID))
			if type(result) == ErrType:
				return result

			result = self.db.Command('''SELECT LAST_INSERT_ID()''')
			if type(result) == ErrType:
				return result
			last_id = result[0]
			self.MergedID = int(last_id['LAST_INSERT_ID()'])


		#check for existing request
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE bug_id=%d AND name LIKE "%s"'''%(self.BugID, self.Name))
		if type(result) == ErrType:
			return result
		if len(result) > 0:
			self.db.Rollback()
			return "There is already a request for this package and bug. If you are trying to update the package a second time, please create a related incident."


		
		#insert combined request
		result = self.db.Command('''INSERT INTO ReleaseAutomation.combined (name,merged_id,bug_id,severity,submitter_id,submit_date,notes) VALUES("%s", %d, %d, "%s", %d, "%s", "%s")'''%(self.Name, self.MergedID, self.BugID, self.UploadPriority, self.SubmitterID, self.DateSubmitted, self.Notes))
		if type(result) == ErrType:
			return result
			
		result = self.db.Command('''SELECT LAST_INSERT_ID()''')
		if type(result) == ErrType:
			return result
		last_id = result[0]
		self.CombinedID = int(last_id['LAST_INSERT_ID()'])

		

		#insert release_request
		package_list = []
		for build in self.BuildIDs:
			for package_id in self.PackageIDs[str(build)]:
				#get types per package
				if package_id[1] in ["host-tool", "common", "host"]:
					table = "Builds.hostPkgs"
				else:
					table = "Builds."+package_id[1]+"Pkgs"
				result = self.db.Command('''SELECT * FROM %s WHERE id=%d'''%(table,package_id[0]))
				if type(result) == ErrType:
					return result

				package = result[0]
				package_name = package['name']
				package_type = package_id[1]
				package_list.append(package_type)
				result = self.db.Command('''INSERT INTO ReleaseAutomation.release_request (name,combined_id,bug_id,builds_id, type, package_id) VALUES("%s", %d, %d, %d, "%s", %d)'''%( package_name, self.CombinedID, self.BugID, build, package_type, package_id[0]))
				if type(result) == ErrType:
					return result
			#end for packageIDs
		#end for BuildIDs
		self.db.Commit()

		#NOTIFY
		subject = '''[Bug %d] Release Request Submitted'''%(self.BugID)
		msg = '''The following Request has been submitted into the Release Request Queue:\r\n'''
		msg += '''Bug %d\r\nPackage:%s\r\nType: %s\r\nSubmitter: %s (%s)\r\nPriority: %s\r\nDate Submitted: %s\r\n\r\n'''%(self.BugID, self.Name, ", ".join(package_list), self.SubmitterName, self.SubmitterEmail, self.UploadPriority, self.DateSubmitted)
		if self.UploadPriority == "async":
			msg += '''Note: This Request Requires manager approval before it will be processed\r\n\r\n'''

		
		email = notify.email()
		result = email.send([], subject, msg)
		if type(result) == ErrType:
			return result

		return None

#end requests





class errata:
	def __init__(self, db, bugzDB, pyro):
		self.db = db
		self.bugzDB = bugzDB
		self.Pyro = pyro.getObj()

		self.MergedID = None
		self.CombinedID = None
		self.BugIDs = []
		self.BuildIDs = []
		self.UploadBuildIDs = []
		self.PackageIDs = []
		self.PackageName = None
		self.Rpms = None
		
		self.TemplateData = { \
				"<BUG_NUMBERS>": "", \
				"<PACKAGE>": "", \
				"<DATE>": "", \
				"<PRIORITY>": "", \
				"<PRODUCTS>": "", \
				"<ARCHITECTURE>": "", \
				"<VERSION_BUGS>": "", \
				"<BUG_CUSTOMER_VIEWABLES>": "", \
				"<NOTES>": "", \
				"<RPMS>": "" }

		return
	

	def setMerged(self, merged_id):
		self.MergedID = int(merged_id)
		
		#get matching combined request
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(self.MergedID))
		if type(result) == ErrType:
			return result
		combined_list = result

		return self._setCombined(combined_list)
	

	def _setCombined(self, combined_results):
		#get matching release_request
		for combined in combined_results:
			combined_id = int(combined['id'])
			
			#handle bugs
			bug_id = int(combined['bug_id'])
			if not bug_id in self.BugIDs:
				self.BugIDs.append(bug_id)


			result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(combined_id))
			if type(result) == ErrType:
				return result

			#process package IDs and build IDs
			request_list = result
			for request in request_list:
				package_id = int(request['package_id'])
				pkg_type = request['type']
				token = 0
				for item in self.PackageIDs:
					if item[0] == package_id:
						token = 1
				if token == 0:
					self.PackageIDs.append((package_id, pkg_type))
				
				build_id = int(request['builds_id'])
				if not build_id in self.BuildIDs:
					self.BuildIDs.append(build_id)

			#end for request

		#end for combined
				
		return None

	
	def setCombined(self, combined_id):
		self.CombinedID = int(combined_id)
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE id=%d'''%(self.CombinedID))
		if type(result) == ErrType:
			return result

		return self._setCombined(result)



	
	def _setUploadItems(self):
		#
		#Process Builds
		#
		buildDict = {}
		for build_id in self.BuildIDs:
			result = self.db.Command('''SELECT * FROM BuildCfg.products WHERE id=(SELECT products_id FROM Builds.builds WHERE id=%d)'''%(build_id))
			if type(result) == ErrType:
				return result
			product = result[0]
			product_id = int(product['id'])
			if product_id in buildDict:
				buildDict[product_id].append(build_id)
			else:
				buildDict[product_id] = [build_id]
		#end for builds
		
		for product_id in buildDict:
			buildDict[product_id].sort()
			self.UploadBuildIDs.append(buildDict[product_id][-1])
		
		#
		#Process Packages
		#
		#I removed a bunch of stuff here because it looked like we had a better way to get the RPMs
		for package in self.PackageIDs:
			p_id = package[0]
			pkg_type = package[1]
			if pkg_type in ('host','host-tool','common'):
				dbtype = 'host'
			else:
				dbtype = pkg_type
			result = self.db.Command('''SELECT * FROM Builds.%sPkgs WHERE id=%d '''%(dbtype, p_id))
			if type(result) == ErrType:
				return result

		#end for packages

			

		return

	
	def _setUploadRpms(self):
		
		##
		## get rpms
		##
		if type(self.MergedID) == IntType:
			result = self.Pyro.exec_task("getRpmsForMerged",method_args=(self.MergedID,))
		elif type(self.MergedID) == NoneType and type(self.CombinedID) == IntType:
			result = self.Pyro.exec_task("getRpmsForCombined",method_args=(self.CombinedID,))
		if type(result) == ErrType:
			return result
		
		self.Rpms = result
		#This is a dictionary... hrms.
			


		return

	def _setRpmInfo(self):
		rpmlines = []
		for package_type in self.Rpms:
			rpmlines.append(package_type.upper()+":\n\n")
			type_dict = self.Rpms[package_type]
			if package_type in ["target", "host-tool", "common", "host"]:
				type_list = sorted(type_dict.items())
				

				for t in type_list:
					if t[0] == "src":
						x = type_list.index(t)
						type_list.insert(0, t)
						del(type_list[x+1])
				for a in type_list:
					arch_name = a[0]
					arch_list = a[1]
					if len(arch_list) > 0:
						rpmlines.append(arch_name+":\n")
						for rpm in arch_list:
							rpmlines.append(rpm+"\n")
						rpmlines.append("\n")
				#end for arch
			elif package_type == "cross":
				type_list = sorted(type_dict.items())
				for t in type_list:
					if t[0] == "src":
						x = type_list.index(t)
						type_list.insert(0, t)
						del(type_list[x+1])
				for a in type_list:
					arch_name = a[0]
					arch_dict = a[1]
					show_list = False
					for host_name in arch_dict:
						if len(arch_dict[host_name]) > 0:
							show_list = True
							break
					#
					if show_list:
						rpmlines.append(arch_name+":\n")
						for host_name in arch_dict:
							if len(arch_dict[host_name]) > 0:
								rpmlines.append(host_name+":\n")
								for rpm in arch_dict[host_name]:
									rpmlines.append(rpm+"\n")
								rpmlines.append("\n")
						rpmlines.append("\n")
				#end for arch
		#end for package_types
		
		self.TemplateData["<RPMS>"]="".join(rpmlines)
		return None




	def _setBugInfo(self):
		bug_list = []
		for bug_id in self.BugIDs:
			result = self.bugzDB.Command('''SELECT * FROM bugs WHERE bug_id=%d'''%(bug_id))
			if type(result) == ErrType:
				return result
			if len(result) < 1:
				return "Can't find bug '%d' in Bugzilla"%(bug_id)
			bug = result[0]
			
			bug_list.append(str(bug_id))
			severity = self.mapSeverity(bug['bug_severity'])
			self.TemplateData["<BUG_CUSTOMER_VIEWABLES>"]+= "%s\n Severity: %s\n\n"%(str(bug['bug_id']), severity)

			self.TemplateData["<BUG_CUSTOMER_VIEWABLES>"]+= bug['cust_viewdesc'] + "\n\n\n"
			self.TemplateData["<VERSION_BUGS>"] += "("+bug['version'].lower()+" "+str(bug_id)+")\n"
		#end for bugs
		self.TemplateData["<VERSION_BUGS>"] = self.TemplateData["<VERSION_BUGS>"][:-1]
		self.TemplateData["<BUG_NUMBERS>"] = ", ".join(bug_list)

		return
	
	def mapSeverity(self, severity):

		if "blocker" == severity:
			return "critical"
		elif "critical" == severity:
			return "critical"
		elif "serious" == severity:
			return "serious"
		elif "normal" == severity:
			return "normal"
		elif "low" == severity:
			return "low"
		elif "enhancement" == severity:
			return "enhancement"
		else:
			return "normal"
	#end mapSeverity


	def generate(self):

		#
		# set general request info
		#
		merged_id = self.MergedID
		if self.CombinedID:
			combined_ids = [self.CombinedID]
		else:
			combined_ids = []
		severity = []
		if self.MergedID:
			result = self.db.Command('''SELECT * FROM ReleaseAutomation.merged WHERE id=%d'''%(self.MergedID))
			if type(result) == ErrType:
				return result
			if not result:
				return "Merged ID does not exists in database"
			self.TemplateData["<PACKAGE>"] = result[0]['name']
			severity.append(result[0]['severity'])
			
			result = self.db.Command('''SELECT id FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(self.MergedID))
			if type(result) == ErrType:
				return result

			for combined in result:
				combined_ids.append(int(combined['id']))


		#Verify that build information still exists. Otherwise this is an old update
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(combined_ids[0]))
		if not result:
			return "Can't find release request for ReleaseAutomation.combined ID=%d"%(combined_ids[0])
		request = result[0]
		result = self.db.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(int(request['builds_id'])))
		if not result:
			return "Build information for this Update no longer exists. This Errata can no longer be generated"


		
		package = None
		for combined_id in combined_ids:
			result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE id=%d'''%(combined_id))
			if type(result) == ErrType:
				return result

			combined = result[0]
			merged_id = int(combined['merged_id'])
			severity.append(combined['severity'])
			package = combined['name']
			if combined['notes']:
				self.TemplateData["<NOTES>"] += combined['notes']+"\n\n"
		#end for combined
			
		if not self.TemplateData["<PACKAGE>"]:
			self.TemplateData["<PACKAGE>"] = str(package)
		
		#
		
		result = self.db.Command('''SELECT process_date FROM ReleaseAutomation.release_cycle WHERE id=(SELECT release_cycle_id FROM ReleaseAutomation.merged WHERE id=%d)'''%(merged_id))
		if type(result) == ErrType:
			return result
		cycle = result[0]
		self.TemplateData["<DATE>"] = str(result[0]['process_date'])



		#
		# Set products
		#
		products = {}
		for build_id in self.UploadBuildIDs:
			result = self.db.Command('''SELECT * FROM BuildCfg.products WHERE id=(SELECT products_id FROM Builds.builds WHERE id=%d)'''%(build_id))
			if type(result) == ErrType:
				return result
			
			product = result[0]
			prodcucts[product['edition']+" "+product['version']] = ""
		#end for builds

		self.TemplateData["<PRODUCTS>"]= ", ".join(products)
		#
			

		
		#
		# Set arch
		#

		self.TemplateData["<ARCHITECTURE>"] = "all"	
	

		#
		# Set priority
		#

		if "async" in severity:
			self.TemplateData["<PRIORITY>"] = "ASYNC-CRITICAL"
		elif "security" in severity:
			self.TemplateData["<PRIORITY>"] = "SECURITY"
		elif "critical" in severity:
			self.TemplateData["<PRIORITY>"] = "CRITICAL"
		else:
			self.TemplateData["<PRIORITY>"] = ""


		#set upload builds
		err = self._setUploadItems()
		if type(err) == ErrType:
			return err


		#set upload rpms
		err = self._setUploadRpms()
		if type(err) == ErrType:
			return err

		err = self._setRpmInfo()
		if type(err) == ErrType:
			return err


		#set bug specific info
		err = self._setBugInfo()
		if type(err) == ErrType:
			return err


		return


		
	def write(self):
		text = copy.deepcopy(errataTemplate.template)

		for field in self.TemplateData:
			text = text.replace(field, self.TemplateData[field])


		return text
#end errata





class actions:
	def __init__(self, db, bugzDB, pyro, user_id, user_login):
		self.db = db
		self.bugzDB = bugzDB
		self.Pyro = pyro.getObj()

		self.UserID = int(user_id)
		self.UserLogin = str(user_login)
		self.UserProfile = {}

		self.CombinedID = None
		self.CombinedRequest = {}

		self.MergedRequest = {}
		self.ReleaseCycle = {}
		self.ProductMap = {}
		self.SubmitterProfile = {}
		self.ReleaseRequests = []

		self.ApproverText = ""

		self.Vars = {}
		self.Fields = []
		self.Process = True
		
		return
	
	
	def setCombined(self, combined_id):
		self.CombinedID = int(combined_id)

		#Combined
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE id=%d'''%(self.CombinedID))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find combined ID '%d' in database."%(self.CombinedID)
		
		self.CombinedRequest = result[0]

		#User Profile
		result = self.bugzDB.Command('''SELECT * FROM profiles WHERE userid=%d'''%(self.UserID))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "I can find your bugz ID. Are you logged in?"
		self.UserProfile = result[0]


		#Submitter Profile
		result = self.bugzDB.Command('''SELECT * FROM profiles WHERE userid=%d'''%(int(self.CombinedRequest['submitter_id'])))
		if type(result) == ErrType:
			return result
		
		self.SubmitterProfile = result[0]

		

		#Merged
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.merged WHERE id=%d'''%(int(self.CombinedRequest['merged_id'])))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find merged ID '%s' in database."%(self.CombinedRequest['merged_id'])

		self.MergedRequest = result[0]


		#Approver
		if self.CombinedRequest['severity'] == 'async':
			if self.MergedRequest['approver_id']:
				result = self.bugzDB.Command('''SELECT * FROM profiles WHERE userid=%d'''%(int(self.MergedRequest['approver_id'])))
				if type(result) == ErrType:
					return result
				if len(result) < 1:
					return "Can't find approver ID: '%s' in database"%(self.MergedRequest['approver_id'])

				profile = result[0]
				self.ApproverText = '''%s %s'''%(profile['realname'], profile['login_name'])
		#




		#Release Cycle
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(int(self.MergedRequest['release_cycle_id'])))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find release cycle: %d in database."%(int(self.MergedRequest['release_cycle_id']))

		self.ReleaseCycle = result[0]

		
		#Product Map
		result = self.db.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(int(self.MergedRequest['products_id'])))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find product id '%s' in database."%(self.MergedRequest['products_id'])

		self.ProductMap = result[0]

		#Release Request
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(self.CombinedID))
		if type(result) == ErrType:
			return result
		if len(result) < 1:
			return "Can't find release request for combined ID '%d' in database."%(self.CombinedID)

		self.ReleaseRequests = result

		return None


	def getVars(self):
		return self.Vars

	def mergeVars(self, vars):
		for key in self.Vars:
			vars[key] = self.Vars[key]
		return vars


	def setVars(self, vars):
		for key in vars:
			self.Vars[key] = vars[key]
		return


	#override these
	def process(self):
		return None
	def form(self):
		return None
	def getFields(self):
		return self.Fields

	
	def bugLink(self, bug):
		return '''<a href="http://bugz.sh.mvista.com/bugz/show_bug.cgi?id=%s">%s</a>, '''%(bug, bug)
	
	
	def formHeader(self):
		text = '''<br><p><b>Request Information:</b><br><p>\n'''
		text += '''<b>Package:</b> %s<br>\n'''%(self.CombinedRequest['name'])
		text += '''<b>Bug Number:</b> %s<br>\n'''%(self.bugLink(int(self.CombinedRequest['bug_id'])))
		text += '''<b>Release:</b> %s<br>\n'''%(self.ProductMap['version'])
		text += '''<b>Edition:</b> %s<br>\n'''%(self.ProductMap['edition'])
		text += '''<b>Submitter:</b> %s %s<br>\n'''%(self.SubmitterProfile['realname'], self.SubmitterProfile['login_name'])
		text += '''<b>Priority:</b> %s<br>\n'''%(self.CombinedRequest['severity'])
		text += '''<b>State:</b> %s<br>\n'''%(self.MergedRequest['state'])
		text += '''<b>Approver:</b> %s<br>\n'''%(self.ApproverText)
		text += '''\n\n<form method="post">
		<input name="editForm" type="hidden" value="%(editForm)d">'''%(self.Vars)
		return text


	def formFooter(self):
		text = '''<br><p><input name="_action_process" type="submit" value="Submit">
		&nbsp;&nbsp;&nbsp;
		<input name="_action_cancel" type="submit" value="Cancel">
		</from><br><p>'''
		return text
#end actions



class managerAction(actions):
	def __init__(self, db, bugzDB, pyro, user_id, user_login):
		actions.__init__(self, db, bugzDB, pyro, user_id, user_login)

		self.Vars = {'approval':None, 'notes':""}
		self.Fields = ['approval', 'notes']



	def setCombined(self, id):
		ret = actions.setCombined(self, id)
		if type(ret) == ErrType:
			return ret
		
		#if self.MergedRequest['severity'] != "async":
		#	self.Process = False

		if self.MergedRequest['state'] == "docsdone" or self.MergedRequest['state'] == "live":
			self.Process = False

		return None
		

	def form(self):
		text = '''<br><b>Manager Actions:</b><p>'''
		
		if self.Process == False:
			text += "<b>This request does not require any approval.</b><br><p>"
			return text
		#else
		if self.MergedRequest['severity'] == "async":
			async_txt = "Async"
		else:
			async_txt = ""

		text += '''
		<label for="approval">%s Release approval:</label><br>
		<input type="radio" name="approval" value="deny">deny<br>'''%(async_txt)
		
		if self.MergedRequest['severity'] == "async":
			text += '''
			<input type="radio" name="approval" value="approve">approve<br>
			<br><p>'''
			text += '''<b>NOTE:</b> If you deny this request, it will be automatically moved to the current queue and marked as CRITICAL.<br><p>'''

		text += '''
			<br><p><label for="package">Approve/deny message:</label>
			<br>
			<textarea name="notes" rows=4 cols=30>%(notes)s</textarea>
			'''%(self.Vars)

		return [text]

	
	def process(self):
		action = "Denied"
		if not self.Process:
			return False

		if not self.Vars['approval']:
			return False

		if self.Vars['approval'] == "approve":
			action = "Approved"
			date = time.strftime("%Y-%m-%d", time.localtime())
			result = self.db.Command('''UPDATE ReleaseAutomation.merged SET approver_id=%d, state="approved", action_date="%s" WHERE id=%d'''%(self.UserID, date, int(self.MergedRequest['id'])))
			if type(result) == ErrType:
				return result

			return True

		elif self.Vars['approval'] == "deny":
			if self.MergedRequest['severity'] == "async":
				result = getCurrentReleaseCycle(self.db)
				if type(result) == ErrType:
					return result
			
				cycle_id = result 
				old_cycle_id = int(self.MergedRequest['release_cycle_id'])
			
				#merged
				result = self.db.Command('''UPDATE ReleaseAutomation.merged SET state="approved", severity="critical", release_cycle_id=%d WHERE id=%d'''%(cycle_id, int(self.MergedRequest['id'])))
				if type(result) == ErrType:
					return result
	
				#combined
				result = self.db.Command('''UPDATE ReleaseAutomation.combined SET severity="critical" WHERE id=%d'''%(self.CombinedID))
				if type(result) == ErrType:
					return result


				#cleanup release_cycle
				result = self.db.Command('''SELECT * FROM ReleaseAutomation.merged WHERE release_cycle_id=%d'''%(old_cycle_id))
				if type(result) == ErrType:
					return result
				if len(result) < 1:
					result = self.db.Command('''DELETE FROM ReleaseAutomation.release_cycle WHERE id=%d AND async="Y"'''%(old_cycle_id))
					if type(result) == ErrType:
						return result
			
			#delete regular request
			else:
				result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d AND NOT id=%d'''%(int(self.MergedRequest['id']), int(self.CombinedRequest['id'])))
				if type(result) == ErrType:
					return result
				if not result:
					#there are no other combined, so we delete the merged, whihc takes care of everything
					result = self.Pyro.exec_task("rmMerged",method_args=(int(self.MergedRequest['id']),))
					if type(result) == ErrType:
						return result
				else:
					#Otherwise we delete from combined
					result = self.Pyro.exec_task("rmCombined",method_args=(int(self.CombinedRequest['id']),))
					if type(result) == ErrType:
						return result

			#NOTIFY
			subject = '''[Bug %d] Has been %s.'''%(int(self.CombinedRequest['bug_id']), action)
			msg = '''This request has been %s by:\r\n'''%(action)
			msg += '''%s (%s)\r\n'''%(self.UserProfile['realname'], self.UserProfile['login_name'])
			if action == "Denied" and self.MergedRequest['severity'] == "async":
				msg += '''\r\nThe request has been automatically moved into the current release cycle and its priority lowered to CRITICAL.\r\n'''
			msg += "\r\n"
			msg += self.Vars['notes']
			msg += "\r\n\r\n"
			email = notify.email()
			result = email.send([], subject, msg)
			if type(result) == ErrType:
				return result


			return True

		return False

#end managerAction



class submitterAction(actions):
	def __init__(self, db, bugzDB, pyro, user_id, user_login):
		actions.__init__(self, db, bugzDB, pyro, user_id, user_login)

		self.Vars = {}
		return

	def setCombined(self, id):
		ret = actions.setCombined(self, id)
		if type(ret) == ErrType:
			return ret

		if self.ReleaseCycle['closed'] == "Y" and self.CombinedRequest['severity'] != "async":
			self.Process = False
		
		if self.MergedRequest['state'] == 'docsdone' or self.MergedRequest['state'] == 'live':
			self.Process = False


		return None
		


	def form(self):
		text = ""
		text += '''<br><b>Submitter Actions:</b><p>\n'''
		
		if not self.Process:
			text +='''<b>You can no longer edit this request.</b><br>\n'''
			return text
	


		text += '''<b>Request:</b><table Cols=7, cellpadding=7>
		<tr bgcolor=#c8c8c8><td>ID</td><td>Name</td><td>Bug</td><td>Severity</td><td>Submitter</td><td>Email</td><td>Notes</td></tr>
		<tr bgcolor=#FFFFFF><td>%(id)s</td><td>%(name)s</td><td>%(bug_id)s</td><td>%(severity)s</td>'''%(self.CombinedRequest)
		text += '''<td>%(realname)s</td><td>%(login_name)s</td>\n'''%(self.SubmitterProfile)
		text += '''<td>%(notes)s</td></tr></table><br><p>\n'''%(self.CombinedRequest)
		
		
		text += '''<b>subRequest:</b><br><p>
		<table Cols=7, cellpadding=7>
		<tr bgcolor=#c8c8c8><td>Delete</td><td>ID</td><td>Name</td><td>Bug</td><td>Build ID</td><td>Type</td><td>Package ID</td></tr>'''
		
		for x in range(len(self.ReleaseRequests)):
			request = self.ReleaseRequests[x]
			text += '''<tr bgcolor=#FFFFFF><td><input type=checkbox name="%(id)s"></td><td>%(id)s</td><td>%(name)s</td<td>%(bug_id)s</td><td>%(builds_id)s</td><td>%(type)s</td><td>%(package_id)s</td></tr>'''%(request)
		#
		text += '''</table><br><p><b>NOTE:</b> You must delete all the subrequest to completely remove the request.<br> '''
		
		return [text]
	
	
	def getFields(self):
		self.Fields = []
		for request in self.ReleaseRequests:
			self.Fields.append(str(request['id']))

		return self.Fields

	def process(self):
		if not self.Process:
			return False

		removed = {'combined': False, 'release': []}

		for request in self.ReleaseRequests:
			id = str(request['id'])
			if id in self.Vars and self.Vars[id] == "on":
				result = self.db.Command('''DELETE FROM ReleaseAutomation.release_request WHERE id=%d'''%(int(id)))
				if type(result) == ErrType:
					return result
				removed['release'].append(request)
			#else
		
		#Delete combined?
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(int(self.CombinedRequest['id'])))
		if type(result) == ErrType:
			return result

		if len(result) < 1:
			result = self.db.Command('''DELETE FROM ReleaseAutomation.combined WHERE id=%d'''%(int(self.CombinedRequest['id'])))
			if type(result) == ErrType:
				return result
		#

		#DELETE Merged?
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(int(self.CombinedRequest['merged_id'])))
		if type(result) == ErrType:
			return result

		if len(result) < 1:
			result = self.db.Command('''DELETE FROM ReleaseAutomation.merged WHERE id=%d'''%(int(self.CombinedRequest['merged_id'])))
			if type(result) == ErrType:
				return result
			removed['combined'] = True
		#

		#Delete async request?
		if self.CombinedRequest['severity'] == "async":
			result = self.db.Command('''SELECT * FROM ReleaseAutomation.merged WHERE release_cycle_id=%d'''%(int(self.MergedRequest['release_cycle_id'])))
			if type(result) == ErrType:
				return result

			if len(result) < 1:
				result = self.db.Command('''SELECT async FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(int(self.MergedRequest['release_cycle_id'])))
				if type(result) == ErrType:
					return result
				if len(result) > 0:
					if result[0]['async'] == "Y":
						result = self.db.Command('''DELETE FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(int(self.MergedRequest['release_cycle_id'])))
						if type(result) == ErrType:
							return result
		#

		#NOTIFY
		subject = '''[Bug %d] Release Request has been edited.'''%(int(self.CombinedRequest['bug_id']))
		if removed['combined']:
			msg = '''%s (%s) has removed %s from the Release Request Queue\r\n'''%(self.UserProfile['realname'], self.UserProfile['login_name'], self.CombinedRequest['name'])
		
		elif removed['release']:
			msg = '''%s %s has removed the following portions of %s from the Release Request Queue:\r\n\r\n'''%(self.UserProfile['realname'], self.UserProfile['login_name'], self.CombinedRequest['name'])
			for request in removed['release']:
				msg += '''Name: %s, Type: %s, BuildID: %07d\r\n'''%(request['name'], request['type'], int(request['builds_id']))
			msg += "\r\n\r\n"
		
		else:
			return False

		email = notify.email()
		result = email.send([], subject, msg)
		if type(result) == ErrType:
			return result

		return True
#end submitterAction




class moderatorAction(actions):
	def __init__(self, db, bugzDB, pyro, user_id, user_login):
		actions.__init__(self, db, bugzDB, pyro, user_id, user_login)

		self.Vars = {'state': "", 'assignee':""}
		self.Fields = ['state', 'assignee']
		return

	def form(self):
		checked = {'waiting':"", 'approved':"", 'docsdone':"", 'live':""}
		checked[self.MergedRequest['state']]="CHECKED"

		assigned = {'accept':"", 'clear':""}
		if self.UserID == self.MergedRequest['assignee_id']:
			assigned['accept'] = "CHECKED"

		
		text = ""
		text += '''<br><b>Moderator Actions:</b><p>'''
		text += '''<label for="state">Update State:</label><br>
		<input type="radio" name="state" value="waiting" %(waiting)s >waiting for approval<br>
		<input type="radio" name="state" value="approved" %(approved)s >approved<br>
		<input type="radio" name="state" value="docsdone" %(docsdone)s >docs done<br>
		<input type="radio" name="state" value="live" %(live)s >live (rpms and MVZ pages)<br>
		<br><p>'''%(checked)

		text += '''<br><p><br><label for="assigneee">Update Assigned To:</label><br>
		<input type="radio" name="assignee" value="accept" %(accept)s >Accept update<br>
		<input type="radio" name="assignee" value="clear" %(clear)s >Remove any ownership<br>
		<br><p>'''%(assigned)

		return [text]

	
	def process(self):
		ret1 = self.processState() 
		ret2 = self.processAssignee()
		return ret1 or ret2
	

	def processAssignee(self):
		assignee = self.Vars['assignee']
		if assignee == "accept":
			self.db.Command('''UPDATE ReleaseAutomation.merged SET assignee_id=%d WHERE id=%d'''%(self.UserID, self.MergedRequest['id']))
			return True
		elif assignee == "clear":
			self.db.Command('''UPDATE ReleaseAutomation.merged SET assignee_id=NULL WHERE id=%d'''%(self.MergedRequest['id']))
			return True
		elif assignee == "":
			return True
		
		return False

	def processState(self):
		state = self.Vars['state']
		if state != self.MergedRequest['state']:
			date = time.strftime("%Y-%m-%d", time.localtime())
			result = self.db.Command('''UPDATE ReleaseAutomation.merged SET state="%s", action_date="%s" WHERE id=%d'''%(state, date, int(self.MergedRequest['id'])))
			if type(result) == ErrType:
				return result

			if state == 'live' and self.MergedRequest['severity'] == 'async':
				result = self.db.Command('''UPDATE ReleaseAutomation.release_cycle SET processed="Y" WHERE id=%d'''%(int(self.MergedRequest['release_cycle_id'])))
				if type(result) == ErrType:
					return result


			#NOTIFY each bug
			result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(int(self.MergedRequest['id'])))
			if type(result) == ErrType:
				return result
			combined_list = result
			for combined in combined_list:
				subject = '''[Bug %d] Release Request has been updated'''%(int(combined['bug_id']))
				msg = '''%s (%s) has changed the state of this request to %s'''%(self.UserProfile['realname'], self.UserProfile['login_name'], state.upper())
			
				email = notify.email()
				result = email.send([], subject, msg)
				if type(result) == ErrType:
					return result
			#done
			return True
		#else

		return False
	
#end moderatorAction

def main():
	sys.stderr.write('No manual execution of this module\n')
	sys.exit(1)

if __name__ == "__main__":
	main()


