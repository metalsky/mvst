#! /usr/bin/env python

import sys
import db
import copy

from types import *

supportedTypes = ('target','cross','host','common','host-tool')


class builddb(db.connection):
	'''
	This class is intended to contain all the common database type routines for use 
	with mvl and apt updates. Any code that can be shared between the two should be 
	placed here to minimize any code duplication and increase consistancy between the
	two update processes.
	'''
	def __init__(self):
		db.connection.__init__(self)
		return

	def getProductsId(self, builds_id):
	    products = self._db.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(int(builds_id)))
	    return products[0]['products_id']


	
	def getCombined(self, merged_id):
		'''Gets all combined requests for a given merged_id'''
		combined = self._db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(int(merged_id)))
		if len(combined) < 1:
			raise Error("No combined request exist for Merged ID: %d"%(int(merged_id)))
		return combined


	def getRequests(self, combined_id):
		'''Gets all release_request for a given combined_id'''
		release = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(int(combined_id)))
		if len(release) < 1:
			raise Error("No release_request exist for Combined ID: %d"%(int(combined_id)))
		return release


	def getNewestUploadRequests(self, merged_id):
		'''given a merged_id return a list of release_request to upload'''
		combined_list = self.getCombined(merged_id)
		
		newest = {'target':0, 'cross':0, 'host-tool':0, 'common':0, 'host':0}
		c_newest = copy.deepcopy(newest)

		#grab the newest build for each pkg_type within each combined 
		for combined in combined_list:
			combined['build'] = copy.deepcopy(newest)
			cb = combined['build']

			requests = self.getRequests(combined['id'])
			for request in requests:
				if int(request['builds_id']) > cb[request['type']]:
					cb[request['type']] = int(request['builds_id'])
			# rr
		#combined

		#get combined for latest build per pkg_type
		for combined in combined_list:
			cb = combined['build']
			for pkg_type in newest:
				if cb[pkg_type] > newest[pkg_type]:
					newest[pkg_type] = cb[pkg_type]
					c_newest[pkg_type] = combined
				#else
			#end types
		#end combined

			
		#generate request list
		request_list = []
		for pkg_type in c_newest:
			if c_newest[pkg_type]:
				c_id = c_newest[pkg_type]['id']
				result = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE type="%s" and combined_id=%d'''%(pkg_type, c_id))
				request_list += list(result)
			#else empty
		#c_newest

		return request_list
	#end getNewestUploadRequests



	def _omniDict(self, list):
		'''Helper function that takes a list of results dicts and flattens it'''
		outputDict = {'cross': {}, 'target':{},'host':{}, 'host-tool':{}, 'common':{} }

		#Each entry in the list is going to be some dictionary and we don't necessarily know what
		#We'll need to take a look at the available keys to determine the appropriate destination dictionary
		#Then we'll need to check out architectures and hosts and append the contents of the list to the output
		for entry in list:
			for key in entry.keys():
				if key in ('host','target','host-tool','common'): #One Layer
					for subkey in entry[key].keys():
						if not outputDict[key].has_key(subkey):
							outputDict[key][subkey] = []
							outputDict[key][subkey] += entry[key][subkey]
						else:
							outputDict[key][subkey] += entry[key][subkey]
				elif key == "cross": #Two Layers
					for subkey in entry[key].keys(): #arch
						if not outputDict[key].has_key(subkey):
							outputDict[key][subkey] = {}
						for anotherkey in entry[key][subkey].keys():	#host
							if not outputDict[key][subkey].has_key(anotherkey):
								outputDict[key][subkey][anotherkey] = []
							outputDict[key][subkey][anotherkey] += entry[key][subkey][anotherkey]
		return outputDict


	#End _omniDict


	def getRpmsForMerged(self, m_id):
		'''returns a disctionary with keys of pkg_types. each value is another dictionary
		with keys of the arch/host name. Their values are a list of rpms. In the case of 
		cross, its a dict of archs, then one of hosts, then a list of rpms.'''

		#SETUP: Dictionary of major categories, then archs/hosts, then rpms
		#Get release requests
		releaseRqsts = self.getNewestUploadRequests(m_id)
		resultsList = []
		for request in releaseRqsts:
			resultsList.append(self.getRpmsForRelease(request['id']))
		return self._omniDict(resultsList)

	def getRpmsForCombined(self, c_id):
		'''Grabs release ids from a given combined id and calls getRpmsForRelease'''
		releaseRqsts = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%c_id)
		resultsList = []
		for request in releaseRqsts:
			resultsList.append(self.getRpmsForRelease(request['id']))
		return self._omniDict(resultsList)



	def getRpmsForRelease(self, r_id):
		'''This function grabs the package id from the release request and finds related rpms'''
		#Grab Pack ID call getRpms
		request = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE id=%d'''%r_id)
		if len(request) < 1:
			raise Error("No release request with id: '%d'"%r_id)

		if request[0]['type'] not in supportedTypes:
			raise Error("Package type '%s'' is not supported"%request[0]['type'])
		type = request[0]['type']
		return self.getRpms(request[0]['package_id'],type, request[0]['builds_id'])	



	def getRpms(self, p_id, type, build_id):
		rpmDict = {'target':{},'cross':{},'host':{},'host-tool':{},'common':{}}
		products_id = self.getProductsId(build_id)
		if type == 'target':
			archs = self.getReleasedArchs(build_id, products_id)
			for arch in archs:
				#Query RPMS
				rpms = self._db.Command('''SELECT name FROM Builds.targetRpms WHERE targetMap_id = (SELECT id from Builds.targetMap WHERE archs_id = %d AND targetPkgs_id = %d)'''%(arch['id'],p_id))
				rpmList = []
				for rpm in rpms:
					if not self.excludeRpm(rpm['name'], arch['name'], "", type, products_id):
						rpmList.append(rpm['name'])
				if not rpmDict[type].has_key(arch['name']):
					rpmDict[type][arch['name']]=[]
				rpmDict[type][arch['name']] += rpmList 
			return rpmDict

		elif type in ('host','host-tool','common'):
			hosts = self.getReleasedHosts(products_id)	
			#Query RPMS
			for host in hosts:
				rpms = self._db.Command('''SELECT name FROM Builds.hostRpms WHERE hostMap_id = (SELECT id from Builds.hostMap WHERE hosts_id = %d AND hostPkgs_id =%d)'''%(host['id'],p_id))
				rpmList = []
				for rpm in rpms:
					if not self.excludeRpm(rpm['name'], "", host['name'], type, products_id):
						rpmList.append(rpm['name'])
				if not rpmDict[type].has_key(host['name']):
					rpmDict[type][host['name']]=[]
				rpmDict[type][host['name']] += rpmList 
			return rpmDict

		elif type == 'cross':
			archs = self.getReleasedArchs(build_id, products_id)
			hosts = self.getReleasedHosts(products_id)	
			for arch in archs:
				for host in hosts:
					rpms = self._db.Command('''SELECT name FROM Builds.crossRpms WHERE crossMap_id = (SELECT id from Builds.crossMap WHERE hosts_id = %d AND archs_id=%d AND crossPkgs_id=%d)'''%(host['id'],arch['id'],p_id))
					rpmList = []
					for rpm in rpms:
						if not self.excludeRpm(rpm['name'], arch['name'], host['name'], type, products_id):
							rpmList.append(rpm['name'])
					if not rpmDict[type].has_key(arch['name']):
						rpmDict[type][arch['name']]={}
					if not rpmDict[type][arch['name']].has_key(host['name']):
						rpmDict[type][arch['name']][host['name']]=[]
					rpmDict[type][arch['name']][host['name']] += rpmList 
			return rpmDict


	def pruneRpms(self, rpmsDict):
		'''Given an rpmsDict from getRpmsFor*, returns a pruned version. Note: This operates on rpmsDict directly'''
		for pkg_type in rpmsDict.keys():
			if pkg_type == "cross":
				archs = rpmsDict[pkg_type]
				for arch in archs.keys():
					hosts = archs[arch]
					for host in hosts.keys():
						rpms = hosts[host]
						if len(rpms) < 1:
							del(hosts[host])
					#end hosts
					if len(archs[arch]) < 1:
						del(archs[arch])
				#end arch

			else:
				released_list = rpmsDict[pkg_type]
				for released in released_list.keys():
					rpms = released_list[released]
					if len(rpms) < 1:
						del(released_list[released])
				#end released:
			
			
			#Look at remaining pkg_types
			if len(rpmsDict[pkg_type]) < 1:
				del(rpmsDict[pkg_type])
			#
		#end pkg_types
		return rpmsDict
	#end pruneRpms



	def getProduct(self, product_id):
		'''Given a product_id, return the product_map dictionary entry'''
		result = self._db.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(int(product_id)))
		if not result:
			raise Error("Can't find product for id=%d"%(int(product_id)))

		return result[0]
	#end getProduct


	def getReleasedProducts(self, product_id):
		'''Given an product_id, return a list of products dictionary entries that are released
		and have the same tag_match'''
		result = self._db.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(int(product_id)))
		if not result:
			raise Error("No product found for id=%d"%(int(product_id)))
		product = result[0]
			
		if product['edition'] == "foundation":
			result = self._db.Command('''SELECT * FROM  BuildCfg.products WHERE product_match="%s" AND released="Y" AND NOT edition="foundation"'''%(product['product_match']))
			if not result:
				raise Error("No released editions for product id: %d"%(int(product['id'])))

			return list(result)

		else:
			if product['released'] != "Y":
				raise Error("Product id: %d is not released"%(int(product['id'])))
			return [product]
	#end getReleasedProducts


	def getReleasedArchs(self, build_id, product_id):
		'''Given a product_id, return a list of arch dictionary entries that are released'''
		if build_id == -1:
			result =  self._db.Command('''SELECT * FROM BuildCfg.archs WHERE products_id=%d AND released="Y"'''%(int(product_id)))
		else:
			result = self._db.Command('''SELECT * FROM BuildCfg.archs WHERE products_id=%d AND released="Y" AND released_build_id < %d'''%(int(product_id), int(build_id)))
		
		archs = list(result)
		arch_list = []
		for arch in archs:
			if not arch['name'].isupper() and not arch['name'] == "noarch":
				arch_list.append(arch)
			if arch['name'] == "SRC":
				arch['name'] = "src"
				arch_list.append(arch)
		#end
		return arch_list
	#end getReleasedArchs


	def getNames(self, list):
		'''given a list of dictionaries, returns a new dictionary of just the 'name' entries'''
		name_d = {}
		for item in list:
			name_d[item['name']] = item['name']
		return name_d
	#end getNames


	def getAllArchs(self, product_id):
		'''given a product_id, return a list of arch dictionary entries that exist'''
		result = self._db.Command('''SELECT * FROM BuildCfg.archs WHERE products_id=%d'''%(int(product_id)))
		archs = list(result)
		arch_list = []
		for arch in archs:
			if not arch['name'].isupper():
				arch_list.append(arch)
			if arch['name'] == "SRC":
				arch['name'] = "src"
				arch_list.append(arch)
		#end
		return arch_list
	#end getAllArchs



	def getReleasedHosts(self, product_id):
		'''given a product_id, return a list of host dictionary entries that are released'''
		result = self._db.Command('''SELECT * FROM BuildCfg.hosts WHERE products_id=%d AND released='Y' '''%(int(product_id)))
		
		hosts = list(result)
		host_list = []
		for host in hosts:
			if not host['name'].isupper():
				host_list.append(host)
			if host['name'] == "SRC":
				host['name'] = "src"
				host_list.append(host)
		#end
		return host_list
	#end getReleasedHosts



	def getAllHosts(self, product_id):
		'''given a product_id returns a list of hosts dictionary entries that exist'''
		result = self._db.Command('''SELECT * FROM BuildCfg.hosts WHERE products_id=%d and NOT name="cluster"'''%(int(product_id)))
		hosts = list(result)
		host_list = []
		for host in hosts:
			if not host['name'].isupper():
				host_list.append(host)
			if host['name'] == "SRC":
				host['name'] = "src"
				host_list.append(host)
		#end
		return host_list
	#end getAllHosts



	def getReleaseRequests(self, package_type, combined_id):
		'''given the package type and combined_id, return a list of release_request dictionary entries that
		match'''
		if package_type not in ('target','cross','host-tool','common','host'):
			raise Error("Package type '%s'' is not supported"%package_type)
		
		if package_type in ('common','host-tool'):
			package_type = 'host'

		result = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(int(combined_id)))
		if not result:
			raise Error("No release request found for type: %s and combined id: %d"%(package_type, int(combined_id)))

		#All		
#		if package_type == "all":
#			return list(result)

		#else

		request_list = result
		requests = []
		for request in request_list:
			result = self._db.Command('''SELECT * FROM Builds.%sPkgs WHERE id=%d'''%( package_type, int(request['package_id']) ))
			if not result:
				raise Error("No package found for id= %d"%(int(request['package_id'])))
				
			requests.append(request)
			#else
		#end
		return requests
	#end getReleaseRequests
				
		
			
	def getRpmsForRequest(self, request_id):
		'''Given a release_request_id, return a list of rpm dictionary entries that match'''
		result = self._db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE id=%d'''%(int(request_id)))
		if not result:
			raise Error("No request found for id=%d"%(int(request_id)))

		request = result[0]
		if request['type'] in ('host-tool','common'):
			type = 'host'
		else:
			type = request['type']

		result = self._db.Command('''SELECT * from Builds.%sRpms WHERE %sMap_id =(SELECT id from %sMap WHERE %sPkgs_id=%d)'''%(type,type,type,type,int(request['package_id'])))
		if not result:
			raise Error("No rpms found for package_id %d"%(int(request['package_id'])))
		rpm_list = list(result)

		return rpm_list
	#end getRpmsForRequest


	
	def updateStatus(self, merged_id, state):
		'''Given a merged_id and state, sets state of an update'''
		result = self._db.Command('''UDPATE ReleaseAutomation.merged SET state="%s" WHERE id=%d'''%(state, merged_id))
		return
	#end updateStatus


	def excludeUnreleased(self, released_archs, released_hosts, package_type, rpms):
		'''Given the release_arch and released_host lists and a list of rpm dictionaries, 
		remove all the rpms for archs/hosts that are not released'''
		host_names = dict( (host['name'], host['name']) for host in released_hosts )
		rpms = self.addTypeNames(rpms)

		rpm_list = []
		archs = {}
		for rpm in rpms:
			if package_type == "cross" or package_type == "target":
				for arch in released_archs:
					if rpm['arch_name'] == arch['name'] and rpm['build_id'] > arch['released_build_id']:
						rpm_list.append(rpm)
						archs[arch['name']] = arch['products_id']
			
			elif package_type == "cross" or package_type != "target":
				if rpm['host_name'] in host_names:
					rpm_list.append(rpm)
			#
		#end
		#print "rpms for releseased archs:"
		#for x in archs:
		#	print archs[x], x
		return rpm_list
	#end excludeUnreleased		



	def excludeRpm(self, rpm, arch, host, pkg_type, product_id):
		'''given a list of rpm dictionary entries remove any rpms that are supposed to be exluded'''

		#TODO: FIXME: this is a hack for -32 and -64 rpms
		if arch.lower() == "src" or host.lower() == "src":
			for f in ["_32-", "_64-"]:
				if rpm.find(f) != -1:
					return True
			#end
		#else

		#get excluded rpm match strings
		if pkg_type == "target":
			excludes = self._db.Command('''SELECT rpmExcludes.name as rpm, archs.name as arch FROM BuildCfg.rpmExcludes JOIN BuildCfg.archs ON archs.id = rpmExcludes.archs_id WHERE archs.products_id=%d'''%(product_id))
			
			#check if rpm matchs
			for exclude in excludes:
				if rpm.find(exclude['rpm']) != -1:
					if exclude['arch'] == "ALL" or exclude['arch'] == arch:
						return True
					else:
						return False
				#
			#end exclude
		elif pkg_type in ["host-tool", "common", "host"]:
			excludes = self._db.Command('''SELECT rpmExcludes.name as rpm, hosts.name as host FROM BuildCfg.rpmExcludes JOIN BuildCfg.hosts ON hosts.id = rpmExcludes.hosts_id WHERE hosts.products_id=%d'''%(product_id))
			
			for exclude in excludes:
				if rpm.find(exclude['rpm']) != -1:
					if exclude['host'] == "ALL" or exclude['host'] == host:
						return True
					else:
						return False
				#
			#end excludes
		elif pkg_type == "cross":
			excludes = self._db.Command('''SELECT rpmExcludes.name as rpm, archs.name as arch, hosts.name as host FROM BuildCfg.rpmExcludes JOIN BuildCfg.archs ON archs.id = rpmExcludes.archs_id JOIN BuildCfg.hosts on hosts.id = rpmExcludes.hosts_id WHERE hosts.products_id=%d'''%(product_id))
		
			for exclude in excludes:
				if rpm.find(exclude['rpm']) != -1:
					if exclude['arch'] == "ALL" or exclude['arch'] == arch:
						if exclude['host'] == "ALL" or exclude['host'] == host:
							return True
						else:
							return False
					else:
						return False
				#end excludes
		else:
			return True
		#default
		return False
	#end def excludeRpm


#Removal Functions
	def rmMerged(self, m_id):
		self._db.Command('''DELETE FROM ReleaseAutomation.merged WHERE id=%d'''%m_id)

	def rmCombined(self, c_id):
		self._db.Command('''DELETE FROM ReleaseAutomation.combined WHERE id=%d'''%c_id)


	def rmReleaseRequest(self, r_id):
		self._db.Command('''DELETE FROM ReleaseAutomation.release_request WHERE id=%d'''%r_id)



	def queryDB(self, db, selectArg, fromArg, whereArg, where):
		if type(where) == str:
			appendString = whereArg + "=" + where[:]
		elif type(where) == list:
			appendString = "("
			for cycle in where:
				appendString += "%s=%s OR " % (whereArg,str(cycle))
			appendString = appendString[:-4] + ")"
		return db.Command('''SELECT %s FROM %s WHERE %s''' % (selectArg, fromArg, appendString))


#update tracking functions
	def addUpdate(self, name, product_id, version_dict):
		'''add an update into the ReleaseTracking database.'''
		pass
			



#end builddb

class Error(Exception):
	pass


######################
#   main FUNCTION    #
######################

def main(argv):
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)


if __name__ == "__main__":
        main(sys.argv)
