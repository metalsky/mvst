#!/usr/bin/env python
import os, shutil, sys, re, commands
import buildConfig
from datetime import datetime


class contentServer:
	def __init__(self, bc):
		self.Config = bc
		self.BuildTag = bc.BuildTag
		self.BuildPrefix = '/mvista/dev_area/mvl6'
		self.BuildDir = os.path.join(self.BuildPrefix, self.BuildTag)
		self.StagingDir = os.path.join(bc.STAGING_PREFIX, self.BuildTag) 
		self.VersionString = datetime.now().strftime("%y%m%d%H%M")
		self.KernelVersionString = self.getKernelVerstring()
		self.CollectionDict = {}
	
	def buildCollectionDict(self):
		returnDict = {}
		for line in os.listdir('/mvista/dev_area/mvl6/latest_collection/'):
			if '-ver' in line:
				ver = commands.getoutput('cat /mvista/dev_area/mvl6/latest_collection/%s' % line)
				returnDict[line[:-4]] = ver
		return returnDict
	
	def getKernelVerstring(self):
		dir = os.path.join(self.BuildDir, self.Config.COLLECTIONS_SOURCE_DIR)
		ktb_re = re.compile(r'.*-.*-([0-9]{10})\.tar\.bz2')
		for file in os.listdir(dir):
			matchObj = ktb_re.match(file)
			if matchObj:
				return matchObj.group(1)
			


	def createStagingDirs(self):
		pass

	def _safecopy(self, sourceFile, destDir, excludes=[]):
		'''Copies a source file to a destination dir.  Will not work if dest is a file. Optional list of files to exclude can be passed in.'''
		fileName = os.path.split(sourceFile)[1]
		if fileName in excludes:
			return
		if not os.path.exists(destDir):
			os.makedirs(destDir)
		shutil.copy(sourceFile,destDir)

	def stageSources(self):
		print 'Staging Sources...'
		bc = self.Config
		sourcesDir = os.path.join(self.BuildDir, bc.SOURCES_SOURCE_DIR)
		destPrefix = os.path.join(self.StagingDir, bc.SOURCES_DEST_PREFIX)
		if not os.path.exists(destPrefix):
			os.makedirs(destPrefix)

		for collectionDir in os.listdir(sourcesDir):
			dest = os.path.join(self.StagingDir, bc.SOURCES_DEST_PREFIX, collectionDir, 'sources')
			os.makedirs(dest)

			os.system('cp %s/%s/* %s -R'  % (sourcesDir, collectionDir, dest))

		print 'Done!'

	def stageCollections(self):
		print 'Staging Collection Releases...'
		verstring = self.VersionString 
		kernelColName = self.Config.BuildTag.split('_')[0]
		bc = self.Config
		collectionsDir = os.path.join(self.BuildDir, bc.COLLECTIONS_SOURCE_DIR)
		os.chdir(collectionsDir)
		#FIXME: The collectionDir variable is wrong as there are files in there now, so it's misleading.  Hence the file handling below.
		for collectionDir in os.listdir(collectionsDir):
			if os.path.isdir(os.path.join(collectionsDir, collectionDir)) and collectionDir == 'kernel':
				src = os.path.join(collectionsDir, collectionDir)
				dest = os.path.join(self.StagingDir, bc.COLLECTIONS_DEST_PREFIX, self.BuildTag.split('_')[0], 'releases')
				self.CollectionDict[kernelColName] = self.KernelVersionString
				if not os.path.exists(dest):
					os.makedirs(dest)
				#Again we aren't doing anything with the kernel dir, we just do the kernel collection copy now.  This whole
				#section is a mess of hacks to work with the evolving system and should really just be re-written.
				os.system('cp %s* %s' % (kernelColName, dest))
			elif os.path.isdir(os.path.join(collectionsDir, collectionDir)):
				pass
			elif '-ver' not in collectionDir and kernelColName not in collectionDir:
				print collectionDir
				col_RE = re.compile(r'(.*)-(\d{10})\.tar\.bz2')
				matchObj = col_RE.match(collectionDir)
				filePrefix = matchObj.group(1)
				fileVersion = matchObj.group(2)
				dest = os.path.join(self.StagingDir, bc.COLLECTIONS_DEST_PREFIX, filePrefix, 'releases')
				if not os.path.exists(dest):
					os.makedirs(dest)
				os.system('cp %s %s' % (collectionDir, dest))
				dictKey = filePrefix
				dictVal = fileVersion
				self.CollectionDict[dictKey] = dictVal
		print 'Done!'

	def stageInstallers(self):
		print 'Staging Installers...'
		bc = self.Config
		fileMatch = re.compile(r'MVL-Toolchain-(.*)-[0-9].*')
		for file in os.listdir(bc.INSTALLER_SOURCE_DIR):
			matchObj = fileMatch.match(file)
			if matchObj:
				arch = matchObj.group(1)
				self._safecopy(os.path.join(bc.INSTALLER_SOURCE_DIR, file), os.path.join(self.StagingDir, bc.INSTALLER_DEST_PREFIX, arch))
			else:
				self._safecopy(os.path.join(bc.INSTALLER_SOURCE_DIR, file), os.path.join(self.StagingDir, bc.INSTALLER_DEST_PREFIX))

		print 'Done!'



	def stageToolchains(self):
		print 'Staging Toolchains...'
		bc = self.Config
		#Sources first
		for file in os.listdir(bc.TOOLCHAIN_SOURCES_SOURCE_DIR):
			self._safecopy(os.path.join(bc.TOOLCHAIN_SOURCES_SOURCE_DIR, file), os.path.join(self.StagingDir, bc.TOOLCHAIN_SOURCES_DEST_PREFIX))

		#Binaries are separated by arch
		fileMatch = re.compile(r'montavista-linux-.*?-.*?-(.*?)-.*?\.tar\.bz2')
		for file in os.listdir(bc.TOOLCHAIN_BINARIES_SOURCE_DIR):
			fq_path = os.path.join(bc.TOOLCHAIN_BINARIES_SOURCE_DIR, file)
			if os.path.isfile(fq_path):
				matchObj = fileMatch.match(file)
				if matchObj:
					self._safecopy(fq_path, os.path.join(self.StagingDir, bc.TOOLCHAIN_BINARIES_DEST_PREFIX, "linux32", matchObj.group(1)))
				else:
					pass
			#For the hostname dirs
			elif os.path.isdir(fq_path):
				hostname = os.path.split(fq_path)[1]
				for file in os.listdir(fq_path):
					if os.path.isfile(os.path.join(fq_path, file)):
						matchObj = fileMatch.match(file)
						if matchObj:
							self._safecopy(os.path.join(fq_path, file), os.path.join(self.StagingDir, bc.TOOLCHAIN_BINARIES_DEST_PREFIX, hostname, matchObj.group(1)))
		print 'Done!'


	def stageDevrocket(self):
		print 'Staging Devrocket...'
		#Temporary stub
		bc = self.Config
		os.makedirs(os.path.join(self.StagingDir, bc.DEVROCKET_DEST_PREFIX))
		print 'Done!'


	def stagePrebuilt(self):
		print 'Staging Prebuilt...'
		bc = self.Config
		prebuiltSubdir = bc.getMSDName() + '-' + bc.KernelVersion
		destDir = os.path.join(self.StagingDir, bc.PREBUILT_DEST_PREFIX, prebuiltSubdir)
		os.makedirs(os.path.join(destDir, 'conf'))
		os.system('cp %s/prebuilt/* %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/prebuilt64/* %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/pstage %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/montavista/content/foundation/conf/local.conf %s/conf' % (self.BuildDir, destDir))

		print 'Done!'

	def stageNewPrebuilt(self):
		print 'Staging (swapped) Prebuilts...'
		bc = self.Config
		prebuiltSubdir = bc.getMSDName() + '-' + bc.KernelVersion
		destDir = os.path.join(self.StagingDir, 'content', 'msds', prebuiltSubdir, 'prebuilt')
		os.makedirs(os.path.join(destDir, 'conf'))
		os.system('cp %s/prebuilt/* %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/prebuilt64/* %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/pstage %s -R' % (self.BuildDir, destDir))
		os.system('cp %s/montavista/content/foundation/conf/local.conf %s/conf' % (self.BuildDir, destDir))

		print 'Done!'


	def makeAllLatest(self):
		bc = self.Config
		prebuiltSubdir = bc.getMSDName() + '-' + bc.KernelVersion
		collectionsDir = os.path.join(self.BuildPrefix, self.BuildTag, 'content/collections')
		prebuiltDir    = os.path.join(self.BuildPrefix, self.BuildTag, bc.PREBUILT_DEST_PREFIX)

		pb1 = os.path.join(self.BuildPrefix, self.BuildTag, 'content/msds', prebuiltSubdir)
		newprebuiltDir = os.path.join(self.BuildPrefix, self.BuildTag, 'content/msds', prebuiltSubdir, 'prebuilt')


		#Do prebuilt
		for dir in os.listdir(prebuiltDir):
			self._runmal(os.path.join(prebuiltDir, dir))

		for dir in os.listdir(newprebuiltDir):
			self._runmal(os.path.join(newprebuiltDir, dir))

		for dir in [pb1, newprebuiltDir]:
			self._runmal(dir)
			

		#Do Collections
		for dir in os.listdir(collectionsDir):
			rdExists = False
			sdExists = False
			col_dir = os.path.join(collectionsDir, dir)
			sourcesDir = os.path.join(col_dir, 'sources')
			releasesDir = os.path.join(col_dir, 'releases')
			if os.path.exists(releasesDir):
				rdExists = True
				self._runmal(releasesDir)
			if os.path.exists(sourcesDir):
				sdExists = True
				self._runmal(sourcesDir)
			if rdExists and sdExists:
				os.system('cp %s/latest %s/%s-%s.sources' % (sourcesDir, releasesDir, dir, self.CollectionDict[dir]))
				self._runmal(sourcesDir)
				self._runmal(releasesDir)
			self._runmal(col_dir)
		self._runmal(collectionsDir)
			
	
	def _runmal(self, destdir):
		verstr = self.VersionString
		cmd = 'find -type f | grep -v all$ | grep -v latest$ > /tmp/all;sudo cp /tmp/all .;sudo cp all latest' 
		curdir = os.getcwd()
		os.chdir(destdir)
		os.system(cmd)
		os.chdir(curdir)
									

	def run(self):
		self.stageSources()
		self.stageInstallers()
		self.stageToolchains()
		self.stageCollections()
		self.stageDevrocket()
		self.stagePrebuilt()
		self.stageNewPrebuilt()
		self.makeAllLatest()



if __name__ in ['__main__']:
	

	print 'Running contentServer generation unit tests.'
	myconfig = buildConfig.buildConfig('ti-omap3-zoom2')
	myconfig.BuildTag = 'ti-omap3-zoom2-2.6.29_091009_0903431'
	mycs = contentServer(myconfig)
	mycs.run()
'''
	myconfig = buildConfig.buildConfig('freescale8377rdb')
	myconfig.BuildTag = 'freescale8377rdb-2.6.27_090531_0901242'
	mycs = contentServer(myconfig)
	mycs.run()

	myconfig = buildConfig.buildConfig('freescale8548cds')
	myconfig.BuildTag = 'freescale8548cds-2.6.27_090531_0901239'
	mycs = contentServer(myconfig)
	mycs.run()

	myconfig = buildConfig.buildConfig('xilinx-ml507')
	myconfig.BuildTag = 'xilinx-ml507-2.6.29_090531_0901241'
	mycs = contentServer(myconfig)
	mycs.run()



'''
