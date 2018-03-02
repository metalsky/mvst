#! /usr/bin/env python

import os
import shutil
import socket

import db
import generic
import builddb



class update(generic.update, builddb.builddb):
	'''
	This is a helper class for the apt updates. It does most of the 
	actual work of implementing the methods in generic.update, where
	as the apt.update class is mostly used to export the implemented
	methods and make things a little cleaner.
	'''
	def __init__(self, *args, **keyw):
		generic.update.__init__(self, *args, **keyw)
		builddb.builddb.__init__(self)

		self.TmpPath = "/tmp"
		self.ToolPath = "/opt/mvl-repo-tools/bin"
		self.BasePath = ""

		return
	#end __init__

	def printSystem(self,cmd):
		print cmd
		os.system(cmd)

	def getTestPath(self):
		'''Returns a string of the absolute path to the test repository'''
		if socket.gethostname() in ['build', 'node-42']:
			test_path = "/tmp2/products"
		else:
			test_path = "/mvista/apt-tool-layout/products"
		return test_path


	def getLivePath(self):
		'''Returns a string of the absolute path to the live repository'''
		live_path = "/mvista/release_area"
		return live_path


	def getRepoPath(self, product_id):
		''' Returns a string of the absolute path to the repository'''
		p = self.getProduct(product_id)
		return os.path.join(self.BasePath, p['version'], "repositories", p['edition'])


	def getUpdateName(self, src_rpms):
		'''Returns a string of the update name. ie package-version-release-build'''
		src_rpms.sort()
		if len(src_rpms) < 1:
			raise Error("No src rpms found for release_request: %d"%(int(request['id'])))

		src_rpm = src_rpms[0]

		tmp = src_rpm.split('.')
		idx = tmp.index('src')
		name_list = []
		for x in range(idx):
			name_list.append(tmp[x])

		return ".".join(name_list)
	#end getUpdateName

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
			raise Exception, 'Source RPMs not found.  Aborting.'

		zoneDirName = string.replace(string.replace(string.strip(srcRpm),'hhl-'+appType+'-',''),'.src.rpm','') 
		return zoneDirName

		#}}}

	
	def getBuildPath(self, build_id):
		'''Returns a string of the absolute path to the build dir'''
		result = self._db.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(int(build_id)))
		if not result:
			raise Error("Can't find build for id: %d"%(int(build_id)))
		build = result[0]

		return os.path.join(build['path'], "build")
		
	#end getBuildPath


	def getUpdateDir(self, update_name):
		'''returns a string of the basename for the update directory'''
		return "RPMS."+update_name
	#end getUpdateDir


	def getUpdateSrcDir(self, update_name):
		'''returns a string of the basename for the update directory for src rpms'''
		return "S"+self.getUpdateDir(update_name)
	#end getUpdateSrcDir


	def addTypeNames(self, rpms):
		'''Given a list of rpm dictionary entries from the database, adds two 
		fields: arch_name and host_name, that are populated with the string name
		of the arch and host type.
		'''
		for rpm in rpms:
			if rpm['archs_id']:
				result = self._db.Command('''SELECT * FROM BuildCfg.archs WHERE id=%d'''%(int(rpm['archs_id'])))
				if not result:
					raise Error("No arch for id: %d"%(int(rpm['archs_id'])))
				arch = result[0]
				rpm['arch_name'] = arch['name'].lower()
			else:
				rpm['arch_name'] = ""

			if rpm['hosts_id']:
				result = self._db.Command('''SELECT * FROM BuildCfg.hosts WHERE id=%d'''%(int(rpm['hosts_id'])))
				if not result:
					raise Error("No host for id: %d"%(int(rpm['hosts_id'])))
				host = result[0]
				rpm['host_name'] = host['name'].lower()
			else:
				rpm['host_name'] = ""
		#end
		return rpms
	#end addTypeNames


	def getTypePath(self, repo_path, arch_name, host_name, package_type):
		'''Returns a string of the absolute path to the update type directry'''
			
		if package_type == "cross":
			if arch_name.lower() == "src" or host_name.lower() == "src":
				return os.path.join(repo_path, package_type, "src")
			else:
				return os.path.join(repo_path, package_type, arch_name, host_name)

		elif package_type == "target":
			return os.path.join(repo_path, package_type, arch_name)
		
		else:
			return os.path.join(repo_path, package_type, host_name)
	#end getTypePath



	def getUpdatePath(self, repo_path, arch_name, host_name, package_type, update_name):
		'''Returns a string of the absolute path to the update directory'''
		if arch_name.lower() == "src" or host_name.lower() == "src":
			update_dir = self.getUpdateSrcDir(update_name)
		else:
			update_dir = self.getUpdateDir(update_name)

		return os.path.join(self.getTypePath(repo_path, arch_name, host_name, package_type), \
				update_dir)
	#end getUpdatePath



	def getUpdateLinkPath(self, arch_name, host_name, package_type, update_path):
		'''Returns the relative path of the foundation update directory (for symlinking)'''
		update_dir = os.path.split(update_path)[-1]

		if package_type == "cross":
			if arch_name.lower() == "src" or host_name.lower() == "src":
				return os.path.join("../../../", "foundation", package_type, "src", update_dir)
			else:
				return os.path.join( "../../../../", "foundation", package_type, arch_name, host_name, update_dir)

		elif package_type == "target":
			return os.path.join("../../../", "foundation", package_type, arch_name, update_dir)

		else:
			return os.path.join("../../../", "foundation", package_type, host_name, update_dir)
	#end getUpdateLinkPath


	def getBuiltRpm(self, build_path, package_type, arch, host, rpm):
		'''Returns a string to the absolute path of the rpm in the build'''
	

		if arch.lower() == "src" or host.lower() == "src":
			return os.path.join(build_path, "SRPMS", rpm)

		if package_type == "target":
			return os.path.join(build_path, arch, "target", rpm)
		elif package_type == "cross":
			if host == "noarch":
				return os.path.join(build_path, arch, "cross", "common", rpm)
			return os.path.join(build_path, arch, "cross", host, rpm)
		elif package_type == "cross" and host == "noarch":
			return os.path.join(build_path, arch, "cross", "common", rpm)
		elif package_type == "common" and rpm.find("host-tool-") == 0:
			return os.path.join(build_path, "host-tools", host, rpm)
		else:
			if host == "noarch":
				return os.path.join(build_path, "host", "common", rpm)
			else:
				return os.path.join(build_path, "host", host, rpm)
	#end getBuiltRpm


	def getBuiltOptionalRpm(self, build_path, package_type, arch, rpm):
		'''Returns a string to the absolute path of the optional rpm in the build'''
		if package_type == "target":
			return os.path.join(build_path, arch, "target", "optional", rpm)
		else:
			return self.getBuiltRpm(build_path, package_type, arch, arch, rpm)
	#end getBuiltOptionalRpm
		

	def createUpdateDir(self, repo_path, updates, package_type, update_name):
		'''Creates the update directory on the filesystem for all the host/archs that are released'''
		if package_type == "cross":
			archs = updates[package_type]
			for arch in archs:
				hosts = archs[arch]
				for host in hosts:
					update_path = self.getUpdatePath(repo_path, arch, host, package_type, update_name)
					type_path = os.path.abspath(os.path.join(update_path, "../"))

					#check for path errors
					if not os.path.exists(type_path):
						raise Error("Update location: %s, does not yet exists"%(type_path))
					if os.path.exists(update_path):
						raise Error("update directory: %s, already exists"%(update_path))
					
					#make the dir
					os.mkdir(update_path)
				#end
			#end
		else:
			released_list = updates[package_type]
			for released in released_list:
				update_path = self.getUpdatePath(repo_path, released, released, package_type, update_name)
				type_path = os.path.abspath(os.path.join(update_path, "../"))
				
				#check for path errors
				if not os.path.exists(type_path):
					raise Error("Update location: %s, does not yet exists"%(type_path))
				if os.path.exists(update_path):
					raise Error("update directory: %s, already exists"%(update_path))
				
				#make the dir
				os.mkdir(update_path)
			#end
		return
	#end createUpdateDir
				
	
	def copyRpms(self, repo_path, build_path, updates, package_type, update_name):
		'''Copy the built rpms from the build into the update directory'''

		if package_type =="cross":
			archs = updates[package_type]
			for arch in archs:
				hosts = archs[arch]
				for host in hosts:
					#TODO FIXME
					rpms = hosts[host]
					for rpm in rpms:
						#get update dir and built rpm
						update_path = self.getUpdatePath(repo_path, arch, host, package_type, update_name)
						built_file = self.getBuiltRpm(build_path, package_type, arch, host, rpm)

						#Check for path errors
						if not os.path.isdir(update_path):
							raise Error("Update Directory does not exist: %s"%(update_path))
						if not os.path.isfile(built_file):
							#FIXME: this is a hack for optional pkgs
							built_op_file = self.getBuiltOptionalRpm(build_path, package_type, arch, rpm)
							if not os.path.isfile(built_op_file):
								raise Error("(c) Cant find rpm: %s"%(built_file))
							else:
								built_file = built_op_file

						#copy rpm
						dest_file = os.path.join(update_path, rpm)
						shutil.copy(built_file, dest_file)
					#end rpm
				#end host
			#end arch
		else:
			released_list = updates[package_type]
			for released in released_list:
				rpms = released_list[released]
				for rpm in rpms:
					#get update dir and buit rpm
					update_path = self.getUpdatePath(repo_path, released, released, package_type, update_name)
					built_file = self.getBuiltRpm(build_path, package_type, released, released, rpm)
					
					#check for path errors
					if not os.path.isdir(update_path):
						raise Error("Update Directory does not exist: %s"%(update_path))
					if not os.path.isfile(built_file):
						#FIXME: this is a hack for optional pkgs
						built_op_file = self.getBuiltOptionalRpm(build_path, package_type, released, rpm)
						if not os.path.isfile(built_op_file):
							raise Error("Cant find rpm: %s"%(built_file))
						else:
							built_file = built_op_file
					
					#copy rpms
					dest_file = os.path.join(update_path, rpm)
					shutil.copy(built_file, dest_file)
				#end rpms
			#end released
		return
	#end copyRpms


	def createUpdateLinks(self, repo_path, updates, released_archs, released_hosts, package_type, update_name):
		'''Create the symlinks from the edition back to the foundation update directory'''

		if package_type == "cross":
			archs = updates[package_type]
			for arch in archs:
				if not arch in released_archs:
					continue
				hosts = archs[arch]
				for host in hosts:
					if not host in released_hosts:
						continue

					update_path = self.getUpdatePath(repo_path, arch, host, package_type, update_name)
					src_path = self.getUpdateLinkPath(arch, host, package_type, update_path)

					#check for path errors
					link_path = os.path.abspath(os.path.join(update_path, "../", src_path))
					if not os.path.isdir(link_path):
						raise Error("Link directory does not exists: %s"%(link_path))

					#link path
					os.symlink(src_path, update_path)
				#end host
			#end arch

		else:
			if package_type == "target":
				check_list = released_archs
			else:
				check_list = released_hosts

			released_list = updates[package_type]
			for released in released_list:
				if not released in check_list:
					continue

				update_path = self.getUpdatePath(repo_path, released, released, package_type, update_name)
				full_dest_path = os.path.split(update_path)[0]
				src_path = self.getUpdateLinkPath(released, released, package_type, update_path)

				#link path
				full_src_path = os.path.abspath(os.path.join(update_path, "../", src_path))
				if not os.path.isdir(full_src_path):
					raise Error("src path does not exist: "+full_src_path)
				
				if not os.path.isdir(full_dest_path):
					raise Error("dest path does not exist: "+full_dest_path)
				if os.path.exists(update_path):
					raise Error("destination link already exists: "+update_path)
					
				os.symlink(src_path, update_path)
			#end released
		return
	#end createUpdateLinks



	def genManifestFiles(self, repo_path, updates, released_archs, released_hosts, package_type, product_id, update_name):
		'''Generate the pkglist (manifest) files for the update'''
		product = self.getProduct(product_id)
		saved_path = os.getcwd()
		if package_type == "cross":
			archs = updates[package_type]
			for arch in archs:
				if released_archs and not arch in released_archs:
					continue
				hosts = archs[arch]
				for host in hosts:
					if released_hosts and not host in released_hosts:
						continue
					if arch.lower() == "src" and host.lower() == "src":
						continue


					update_path = self.getUpdatePath( repo_path, arch, \
									host, package_type, \
									update_name)
					
					#only gen if binary exists
					if os.path.isdir(update_path):
						type_path = os.path.split(update_path)[0]
						base_path = os.path.join(type_path, "base")
						os.chdir(base_path)

						#gen files
						self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --cross --partial --meta=updates %s %s 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], host, type_path, update_name))
					#else
				#end host
			#end arch
		else:
			if package_type == "target":
				check_list = released_archs
			else:
				check_list = released_hosts

			released_list = updates[package_type]
			for released in released_list:
				if check_list and not released in check_list:
					continue
				if released.lower() == "src":
					continue

				update_path = self.getUpdatePath( repo_path, released, released, package_type, update_name)

				#only gen if binarys exist
				if os.path.isdir(update_path):
					type_path = os.path.split(update_path)[0]
					base_path = os.path.join(type_path, "base")
					os.chdir(base_path)


					#gen files
					self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --partial --meta=updates %s %s 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], released, type_path, update_name))
				#else
			#end released
		os.chdir(saved_path)
		return
	#end genManifestFiles

	
	def fixEmptyRelease(self, base_path):
		os.system("touch %s"%(os.path.join(base_path, "pkglist.updates")))
		os.system("touch %s"%(os.path.join(base_path, "srclist.updates")))
		f = open(os.path.join(base_path, "release"), "r+")
		lines = f.readlines()
		lines.insert(-1, " d41d8cd98f00b204e9800998ecf8427e 0 base/pkglist.updates\n")
		lines.insert(-1, " d41d8cd98f00b204e9800998ecf8427e 0 base/srclist.updates\n")
		f.truncate(0)
		f.seek(0)
		for line in lines:
			f.write(line)
		f.close()
	#end fixEmptyRelease


	def createArchRepo(self, repo_path, arch_id):
		'''Given an arch id, a repo structure will be created for it if one
		does not already exists'''

		result = self._db.Command('''SELECT * FROM BuildCfg.archs WHERE id=%d'''%(int(arch_id)))
		if not result:
			raise Error("Can't find arch for id=%d"%(int(arch_id)))
		arch = result[0]

		product = self.getProduct(arch['products_id'])
		
		#target
		target_path = os.path.join(repo_path, "target")
		if not os.path.isdir(target_path):
			raise Error("target_path: %s, does not exists"%(target_path))
		
		#Only create base and files for non-src arches
		if arch['name'].lower() == "src":
			return
		#else


		arch_path = os.path.join(target_path, arch['name'])
		if not os.path.isdir(arch_path):
			os.mkdir(arch_path)


		if product['edition'] != "foundation":
			base_path = os.path.join(arch_path, "base")
			if not os.path.isdir(base_path):
				os.mkdir(base_path)

			if not os.path.isfile(os.path.join(base_path, "release.updates")):
				self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --partial --meta=updates %s none 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], arch['name'], arch_path))
			if not os.path.isfile(os.path.join(base_path, "pkglist.updates")):
				self.fixEmptyRelease(base_path)
		#else foundation


		#cross
		cross_path = os.path.join(repo_path, "cross")
		if not os.path.isdir(cross_path):
			raise Error("cross_path: %s, does not exists"%(cross_path))

		arch_path = os.path.join(cross_path, arch['name'])
		if not os.path.isdir(arch_path):
			os.mkdir(arch_path)

		result = self._db.Command('''SELECT * FROM BuildCfg.hosts WHERE products_id=%d AND NOT name="ALL" and NOT name="SRC"'''%(product['id']))
		if not result:
			raise Error("Couldn't find any released host for products_id=%d"%(product['id']))
		for host in result:
			host_path = os.path.join(arch_path, host['name'])
			if not os.path.isdir(host_path):
				os.mkdir(host_path)
			
			if product['edition'] != "foundation":
				base_path = os.path.join(host_path, "base")
				if not os.path.isdir(base_path):
					os.mkdir(base_path)

				if not os.path.isfile(os.path.join(base_path, "release.updates")):
					self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --cross --partial --meta=updates %s none 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], host['name'], host_path))
				if not os.path.isfile(os.path.join(base_path, "pkglist.updates")):	
					self.fixEmptyRelease(base_path)
			#else foundation
		#end for

		return
	#end createArchRepo


	def createHostRepo(self, repo_path, host_id):
		'''Given a host id, a repo structure will be created for it if one
		does not already exists'''
		

		result = self._db.Command('''SELECT * FROM BuildCfg.hosts WHERE id=%d'''%(int(host_id)))
		if not result:
			raise Error("Can't find host for id=%d"%(int(host_id)))
		host = result[0]
		product = self.getProduct(host['products_id'])
		
		#FIXME: hack
		h_types = [('solaris',"sun4u"), ("windows","i386"), ('_64',"x86_64"), ('',"i386")]
		h_type = 'i386'
		for h in h_types:
			if host['name'].find(h[0]) != -1:
				h_type = h[1]
				break;
			#else
		#end for h


		for host_type in ['common', 'host']:
			host_path = os.path.join(repo_path, host_type)
			if not os.path.isdir(host_path):
				raise Error("%s_path: %s, does not exist"%(host_type, host_path))

			#Only create base and files for non-src hosts
			if host['name'].lower() == "src":
				return
			#else

			h_path = os.path.join(host_path, host['name'])
			if not os.path.isdir(h_path):
				os.mkdir(h_path)
	
			if product['edition'] != "foundation":
				base_path = os.path.join(h_path, "base")
				if not os.path.isdir(base_path):
					os.mkdir(base_path)

				if not os.path.isfile(os.path.join(base_path, "release.updates")):
					self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --partial --meta=updates %s none 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], h_type, h_path))
				if not os.path.isfile(os.path.join(base_path, "pkglist.updates")):
					self.fixEmptyRelease(base_path)
			#else foundation
		#end for hosts
	#end createHostRepo


	def delManifestEntry(self, repo_path, archs, hosts, package_type, product_id, update_name):
		'''Remove the update from the manifest files for the given archs, type, and name'''
		product = self.getProduct(product_id)
		saved_path = os.getcwd()
		if package_type == "cross":
			for arch in archs:
				for host in hosts:
					if arch.lower() == "src" or host.lower() == "src":
						continue
					#else
					update_path = self.getUpdatePath( repo_path, arch, \
									host, package_type, \
									update_name)
					
					#only gen if binary exists
					if os.path.isdir(update_path):
						type_path = os.path.split(update_path)[0]
						base_path = os.path.join(type_path, "base")
						os.chdir(base_path)

						#gen files
						self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --cross --partial --remove --meta=updates %s %s 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], host, type_path, update_name))
					#else
				#end host
			#end arch
		else:
			if package_type == "target":
				r_list = archs
			else:
				r_list = hosts

			for released in r_list:
				if released.lower() == "src":
					continue

				update_path = self.getUpdatePath( repo_path, released, released, package_type, update_name)

				#only gen if binarys exist
				if os.path.isdir(update_path):
					type_path = os.path.split(update_path)[0]
					base_path = os.path.join(type_path, "base")
					os.chdir(base_path)


					#gen files
					self.printSystem("%s/mvl-genbasedir --edition=%s --release=%s --architecture=%s --partial --remove --meta=updates %s %s 2>&1 1>/dev/null"%(self.ToolPath, product['edition'], product['version'], released, type_path, update_name))
				#else
			#end released
		os.chdir(saved_path)
		return
	#end delManifestEntry


	def delUpdate(self, repo_path, archs, hosts, package_type, product_id, update_name):
		'''Remove the update files (binaries/src) from the repository'''
		product = self.getProduct(product_id)
		if package_type == "cross":
			for arch in archs:
				for host in hosts:
					update_path = self.getUpdatePath( repo_path, arch, \
									host, package_type, \
									update_name)
					
					if os.path.isdir(update_path) or os.path.islink(update_path):
						os.system("rm -rf %s"%(update_path))
				#end hosts
			#end arch
		else:
			if package_type == "target":
				r_list = archs
			else:
				r_list = hosts
			
			for released in r_list:
				update_path = self.getUpdatePath( repo_path, released, released, package_type, update_name)
				
				if os.path.isdir(update_path) or os.path.islink(update_path):
					os.system("rm -rf %s"%(update_path))

			#end r_list
		return
	#end delUpdate

#end update




class Error(Exception):
	pass
#end Error




######################
#   main FUNCTION    #
######################

def main(argv):
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)


if __name__ == "__main__":
        main(sys.argv)
