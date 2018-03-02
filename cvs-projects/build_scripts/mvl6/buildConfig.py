#!/usr/bin/env python
DEBUG = 0
import sys,server, os

class buildConfig:
	def __init__(self, msdname):
		self._mirrorAddress = '10.0.12.53'
		self._IPAddress = '10.0.0.17'
		self._MSDName = msdname

		self.BuildType = 'staging'
		self.ReleaseID = 12

		#Incremental Build?
		self.IsIncremental = False

		#Set Database Info
		self.CollectionRepos = self._getRepoList()
		self.LaunchCommand = self._getLaunchCommand()
		self.KernelVersion = self._getKernelVersion()
		self.ToolchainPath = self._getToolchainPath()

		#Content Server "globals"
		self.IP_VER = '/mvista/dev_area/integration_platform/latest_ip/buildtag'
		self.TOOLCHAIN_VER = '/mvista/dev_area/integration_platform/latest_toolchain/buildtag'

		self.STAGING_PREFIX = '/mvista/dev_area/mvl6/'
		self.SOURCES_SOURCE_DIR = 'sources/collection/'
		self.SOURCES_SUFFIXES = ['.tar.gz', '.tar.bz2', '.tar.gz.md5', '.tar.bz2.md5']
		self.SOURCES_EXCLUDES = ['linux-2.6.26.tar.bz2', 'linux-2.6.26.tar.bz2.md5', \
					 'linux-2.6.27.tar.bz2', 'linux-2.6.27.tar.bz2.md5', \
					 'linux-2.6.28.tar.bz2', 'linux-2.6.28.tar.bz2.md5', \
					 'linux-2.6.29.tar.bz2', 'linux-2.6.29.tar.bz2.md5', \
					 'linux-2.6.30.tar.bz2', 'linux-2.6.30.tar.bz2.md5', \
					 'linux-2.6.31.tar.bz2', 'linux-2.6.31.tar.bz2.md5']
		self.SOURCES_DEST_PREFIX = 'content/collections/' # append /<collection_id>/sources/

		self.INSTALLER_SOURCE_DIR = '/mvista/dev_area/integration_platform/latest_toolchain/build/installers'
		self.INSTALLER_DEST_PREFIX = 'content/installer' # append /<arch>/

		self.TOOLCHAIN_SOURCES_SOURCE_DIR = '/mvista/dev_area/integration_platform/toolchains/codesourcery/current/sources'
		self.TOOLCHAIN_BINARIES_SOURCE_DIR = '/mvista/dev_area/integration_platform/toolchains/codesourcery/current/binary'
		self.TOOLCHAIN_SOURCES_DEST_PREFIX = 'content/toolchains/sources'
		self.TOOLCHAIN_BINARIES_DEST_PREFIX = 'content/toolchains/' # append /linux32/<arch>/  -- separate handling for subdirs in here

		self.COLLECTIONS_SOURCE_DIR = 'montavista/content'
		self.COLLECTIONS_DEST_PREFIX = 'content/collections/' # append /<collection_id>/releases/

		self.DEVROCKET_DEST_PREFIX = 'content/devrocket'
	
		self.PREBUILT_DEST_PREFIX = 'content/prebuilt' # append /<msd>-<kernelver>

		self.COLLECTION_BINARIES = '/mvista/dev_area/mvl6/latest_collection'

		self.CollectionVersions = self._buildVersionDict()

	def IPServer(self):
		return self._IPAddress

	def mirrorServer(self):
		return self._mirrorAddress

	def setConfig(self, distro, machine):
		self._distro = distro
		self._machine = machine

	def getMSDName(self):
		return self._MSDName

	def GetNamesByCollections(self,col_list):
		returnlist = []
		db = server.server()
		db.Connect()
		for collection in col_list:
			results = db.Command('SELECT m.name from Mvl6Cfg.MSDs m, Mvl6Cfg.Repos r WHERE m.id = r.msds_id and r.name = "%s"' % collection)
			for result in results:
				if result['name'] not in returnlist:
					returnlist.append(result['name'])

		return returnlist

	def getRequestedVersions(self):
		'''Release build.  Build a dict.  <collection_name>: fully qualified path to tarball'''
		retdict = {}
		db = server.server()
		db.Connect()
		results = db.Command('SELECT name,version from Mvl6Cfg.RequestedCollections WHERE breq_id=%s' % self.ReleaseID)

		for result in results:
			cname = result['name']
			cver  = result['version']

			buildresults = db.Command('''SELECT filename, buildtag FROM Mvl6Cfg.Collections c, Mvl6Cfg.Builds b WHERE \
									   cname='%s' and version=%s and c.builds_id=b.id''' % (cname,cver))

			for bresult in buildresults:
				filename = bresult['filename']
				buildtag = bresult['buildtag']

				fqpath = os.path.join('/mvista/dev_area/mvl6', buildtag, filename)
				if os.path.exists(fqpath):
					retdict[cname] = fqpath
					break

		return retdict


	def _getRepoList(self):
		returnlist = []
		db = server.server()
		db.Connect()
		results = db.Command('SELECT r.name from Mvl6Cfg.MSDs m, Mvl6Cfg.Repos r WHERE m.id = r.msds_id and m.name="%s"' % self._MSDName)
		db.Close()
		for result in results:
			 returnlist.append( result['name'] )

		return returnlist

	def _buildVersionDict(self):
		ret_dict = {}
		for collection in self.CollectionRepos:
			fp = open(os.path.join(self.COLLECTION_BINARIES, collection + '-ver'))
			version = fp.readline().strip()
			fp.close()
			ret_dict[collection] = version

		return ret_dict

	
	def _getLaunchCommand(self):
		db = server.server()
		db.Connect()
		result = db.Command('SELECT launchCmd FROM Mvl6Cfg.MSDs m WHERE m.name="%s"' % self._MSDName)[0]['launchCmd']
		db.Close()
		return result

	def _getKernelVersion(self):
		db = server.server()
		db.Connect()
		result = db.Command('SELECT kernelVer FROM Mvl6Cfg.MSDs m WHERE m.name="%s"' % self._MSDName)[0]['kernelVer']
		db.Close()
		return result

	def _getToolchainPath(self):
		db = server.server()
		db.Connect()
		result = db.Command('SELECT toolchainPath FROM Mvl6Cfg.MSDs m WHERE m.name="%s"' % self._MSDName)[0]['toolchainPath']
		db.Close()

		tcdir = '/mvista/dev_area/integration_platform/latest_toolchain/build/installers'
		fname = ''
		for file in os.listdir(tcdir):
			if result in file:
				fname = file

		return os.path.join(tcdir, fname)

if __name__ in ['__main__']:
	cfg = buildConfig(sys.argv[1])
	print cfg._getLaunchCommand()
	pass
