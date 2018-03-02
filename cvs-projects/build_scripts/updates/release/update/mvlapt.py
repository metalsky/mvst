#! /usr/bin/env python

import os
import apttools
import time

class update(apttools.update):
	'''
	This is the apt.update class. It exports all the functionality
	defined within generic.update. When working with apt based updates
	directly this class should be used. When working with updates for
	multiple systems (mvl, apt) the update.update class should be used.
	'''

	def pushToTesting(self, merged_id):
		#self.updateStatus(merged_id, "approved")
		self.BasePath = self.getTestPath()
		test_repo = self.getRepoPath(self.ProductID)
		self._pushUpdate(test_repo, merged_id)
		#self.updateStatus(merged_id, "testing")
		return
		

	def pushToLive(self, merged_id):
		self.BasePath = self.getLivePath()
		live_repo = self.getRepoPath(self.ProductID)
		self._pushUpdate(live_repo, merged_id)
		self.updateStatus(merged_id, "live")
		return
	

	def _pushUpdate(self, repoPath, merged_id):
		#Update Steps:
		#1) get update pkgs
		request_product = self.getProduct(self.ProductID)
		Edition = request_product['edition']
		if Edition == "foundation":
			released_products = self.getReleasedProducts(self.ProductID)

		#TODO FIXME: pkgs still need to be excluded
		updates = self.getRpmsForMerged(merged_id)
		updates = self.pruneRpms(updates)
		rr = self.getNewestUploadRequests(merged_id)
		rr_d = {"target":[], "cross":[], "host-tool":[], "common":[], "host":[]}
		for r in rr:
			rr_d[r['type']].append(r)
		#end
			

		#3) for each update set:
		
		for pkg_type in updates:
			#3.1) get update name
			if len(updates[pkg_type]) < 1:
				continue
			
			if pkg_type == "cross":
				archs = updates[pkg_type]
				srcs = archs['src']['src']
				update_name = self.getUpdateName(srcs)
			else:
				releases = updates[pkg_type]
				srcs = releases['src']
				update_name = self.getUpdateName(srcs)
				
			#3.2) createa update dir
			self.createUpdateDir(repoPath, updates, pkg_type, update_name)
				
			#3.3) copy rpms
			build_id = rr_d[pkg_type][0]['builds_id']
			build_path = self.getBuildPath(build_id)
			self.copyRpms(repoPath, build_path, updates, pkg_type, update_name)


			#3.4) create links
			if Edition == "foundation":
				for product in released_products:
					p_archs = self.getNames(self.getReleasedArchs(build_id, product['id']))
					p_hosts = self.getNames(self.getReleasedHosts(product['id']))
					repo_path = self.getRepoPath(product['id'])
					
					self.createUpdateLinks(repo_path, updates, \
								p_archs, p_hosts, \
								pkg_type, update_name)
				#
			#else: No links needed
	
			#3.5) generate manifest
			if Edition == "foundation":
				for product in released_products:
					p_archs = self.getNames(self.getReleasedArchs(build_id, product['id']))
					p_hosts = self.getNames(self.getReleasedHosts(product['id']))
					repo_path = self.getRepoPath(product['id'])
					
					self.genManifestFiles(repo_path, updates, p_archs, \
							p_hosts, pkg_type, \
							product['id'], update_name)
				#
			else:
				self.genManifestFiles(repoPath, updates, None, \
						None, pkg_type, \
						self.ProductID, update_name)

		#end for pkg_types
		
		
		#4) update builddb status (happens outside this function)
		return	
	#end _pushUpdate

	
	def createNewTestRepo(self):
		self.BasePath = self.getTestPath()
		self._createNewRepo()
	#end createNewTestRepo

	def createNewLiveRepo(self):
		self.BasePath = self.getLivePath()
		self._createNewRepo()
	#end createNewLiveRepo


	def _createNewRepo(self):
		#get products
		product = self.getProduct(self.ProductID)
		if product['edition'] == "foundation":
			products = self.getReleasedProducts(self.ProductID)
			products.insert(0, product)
		else:
			products = [product]
	

		if len(products) < 1:
			raise Error("No released products to create repo for")

		for product in products:
			archs = self.getReleasedArchs(-1, product['id'])
			hosts = self.getReleasedHosts(product['id'])
			repo_path = self.getRepoPath(product['id'])
			
			if not os.path.exists(repo_path):
				os.makedirs(repo_path)
			
			for utype in ["common", "cross", "host", "target"]:
				#type dirs
				tdir = os.path.join(repo_path, utype)
				if not os.path.exists(tdir):
					os.mkdir(tdir)

				#src dir
				sdir = os.path.join(tdir, "src")
				if not os.path.exists(sdir):
					os.mkdir(sdir)
			#end utype

			#Gen pkglist
			repo = self.getRepoPath(product['id'])
			for arch in archs:
				self.createArchRepo(repo, arch['id'])

			for host in hosts:
				self.createHostRepo(repo, host['id'])
		#end products
	#end _createNewRepo	

	
	def releaseNewTestArch(self, edition_arch_id):
		self.BasePath = self.getTestPath()
		self._releaseNewArch(edition_arch_id)
	#end releaseNewTestArch

	def releaseNewLiveArch(self, edition_arch_id):
		self.BasePath = self.getLivePath()
		self._releaseNewArch(edition_arch_id)
	#end releaseNewLiveArch


	def _releaseNewArch(self, edition_arch_id):
		#1) create repo structure
		repo = self.getRepoPath(self.ProductID)
		self.createArchRepo(repo, edition_arch_id)

		#TODO:
		#2) notify of old host/common updates that need new pages
		#3) release any old updates that need to go out for the new arch
	#end _releaseNewArch


	def releaseNewTestHost(self, edition_host_id):
		self.BasePath = self.getTestPath()
		self._releaseNewHost(edition_host_id)
	#end releaseNewTestHost


	def releaseNewLiveHost(self, edition_host_id):
		self.BasePath = self.getLivePath()
		self._releaseNewHost(edition_host_id)
	#end releaseNewLiveHost


	def _releaseNewHost(self, edition_host_id):
		repo = self.getRepoPath(self.ProductID)
		self.createHostRepo(repo, edition_host_id)
	#end _releaseNewHost
	

	def removeFromTesting(self, update_name):
		self.BasePath = self.getTestPath()
		self._removeUpdate(self.BasePath, update_name)
		return
	#end removeFromTesting



	def removeFromLive(self, update_name):
		self.BasePath = self.getLivePath()
		self._removeUpdate(self.BasePath, update_name)
		return
	#end removeFromLive


	def _removeUpdate(self, basePath, update_name):
		product = self.getProduct(self.ProductID)
		
		#trim update_name ?
		if update_name.find("RPMS.") == 0:
			update_name = update_name[len("RPMS."):]
		elif update_name.find("SRPMS.") == 0:
			update_name = update_name[len("SRPMS."):]


		#get pkg type
		if update_name.find("cross-") == 0:
			pkg_type = "cross"
		elif update_name.find("host-tool-") == 0:
			pkg_type = "common"
		elif update_name.find("common-") == 0:
			pkg_type = "common"
		elif update_name.find("host-") == 0:
			pkg_type = "host"
		else:
			pkg_type = "target"


		#make sure we delete editions and foundatiosn if they exists
		if product['edition'] == "foundation":
			products = self.getReleasedProducts(self.ProductID)
			products.insert(0, product)
		else:
			products = [product]

		removed = 0
		for product in products:
			repoPath = self.getRepoPath(product['id'])
			#FIXME: we should know which archs were released before that update
			#	but part of this requires better tracking of released updates
			archs = self.getNames(self.getAllArchs(product['id']))
			hosts = self.getNames(self.getAllHosts(product['id']))

			if product['edition'] != "foundation":
				self.delManifestEntry(repoPath, archs, hosts, pkg_type, product['id'], update_name)
			
			self.delUpdate(repoPath, archs, hosts, pkg_type, product['id'], update_name)
			removed = removed + 1
			#end pkg types
		#end products

		if removed == 0:
			raise Error("No updates removed for %s"%(update_name))
		return	
	#end _removeUpdate


	def rebuildTesting(self, pkg_type):
		self.BasePath = self.getTestPath()
		repoPath = self.getRepoPath(self.ProductID)
		self._rebuildUpdates(repoPath, pkg_type)
	#end rebuildTesting


	def rebuildLive(self, pkg_type):
		self.BasePath = self.getLivePath()
		repoPath = self.getRepoPath(self.ProductID)
		self._rebuildUpdates(repoPath, pkg_type)
	#end rebuildLive

	
	def _rebuildUpdates(self, repoPath, pkg_type):
		product = self.getProduct(self.ProductID)
		if product['edition'] == "foundation":
			return

		archs = self.getNames(self.getReleasedArchs(-1, self.ProductID))
		hosts = self.getNames(self.getReleasedHosts(self.ProductID))
		
		if pkg_type == "cross":
			for arch in archs:
				for host in hosts:
					if arch.lower() == "src" or host.lower() == "src":
						continue
					#else
					type_path = self.getTypePath(repoPath, arch, host, pkg_type)
					files = os.listdir(type_path)
					if "base" in files:
						os.system("rm -rf %s"%(os.path.join(type_path, "base", "*")))

					for file in files:
						if file.find("RPMS.") == 0:
							update_name = file[len("RPMS."):]
							archd = {arch:[host]}
							update = {'cross':archd}
							self.genManifestFiles(repoPath, update, [arch], [host], pkg_type, self.ProductID, update_name)
						#else skip
					#end files
				#end host
			#end arch
		else:
			if pkg_type == "target":
				released_list = archs
			else:
				released_list = hosts

			for released in released_list:
				if released.lower() == "src":
					continue
				#else
				type_path = self.getTypePath(repoPath, released, released, pkg_type)
				files = os.listdir(type_path)
				if "base" in files:
					os.system("rm -rf %s"%(os.path.join(type_path, "base", "*")))

				#build update structure
				for file in files:
					if file.find("RPMS.") == 0:
						update_name = file[len("RPMS."):]
						released_d = {released:released}
						update = {pkg_type:released_d}
						self.genManifestFiles(repoPath, update, [released], [released], pkg_type, self.ProductID, update_name)
					#else skip
				#end files
			#end released
	#end _rebuildUpdates	
#end update



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
