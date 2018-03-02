import urllib, commands, os,shutil, buildConfig
from debug import debugPrint
from runCmd import crun

class IPSource:
	def __init__(self, config):

		cmdStatus, cmdOut = commands.getstatusoutput('uname -m')
		cmdStatus = not cmdStatus
		
		if cmdStatus and ('i386' in cmdOut or 'i686' in cmdOut):
			self.Bits = 32
		elif cmdStatus and 'x86_64' in cmdOut:
			self.Bits = 64
		else:
			raise Error, "Could not determine architecture type of host machine.  Aborting."

		latestBuild = self._getLatestBuild()
		
		self.SourceURI           = '/mvista/dev_area/integration_platform/latest_ip/build/integration-platform.tar.bz2'
		self.ToolchainSourceURI  = config.ToolchainPath
		self.IPSourceFile        = os.path.split(self.SourceURI)[1]
		self.ToolchainSourceFile = os.path.split(config.ToolchainPath)[1]

	def _getLatestBuild(self):
		return '09030519'


	def Fetch(self,dir='/tmp/'):
		ipDestFile = r'%s/%s' % (dir, self.IPSourceFile)
		toolchainDestFile = r'%s/%s' % (dir, self.ToolchainSourceFile)
		self.DownloadDir = dir
		
		print 'Fetching Integration Platform...'
		commands.getstatusoutput('cp %s %s' % (self.SourceURI, ipDestFile))
		print 'Fetching Toolchain...'
		commands.getstatusoutput('cp %s %s' % (self.ToolchainSourceURI, toolchainDestFile))

		
		return self._verifyFile(ipDestFile)

	def Install(self):
		destPathPrefix = '/chroot/centos4/opt/'
		tempDir = self.DownloadDir + '/tmp-IP/'
		if os.path.exists(tempDir):
			os.system('rm -rf %s' % tempDir)
		os.mkdir(tempDir)
		os.chdir(tempDir)

		#Install Integration Platform
	

		print 'Installing Integration Platform...'
		os.chdir(destPathPrefix)
		files = commands.getoutput('tar jxvf %s/%s' % (self.DownloadDir, self.IPSourceFile)).split('\n')


	
		#Install Toolchain
		print 'Installing Toolchain...'
		os.system('cp %s/%s /chroot/centos4/home/build/' % (self.DownloadDir, self.ToolchainSourceFile))
		crun('./%s --mode silent --prefix /opt/montavista' % self.ToolchainSourceFile)
	
				


	def _verifyFile(self,file):
		fileTest = commands.getoutput('file %s' % file)
		tarTest = not commands.getstatusoutput('tar tzf %s' % file)[0]

		if tarTest and 'gzip compressed data' in fileTest:
			return True
		else:
			return False
		



		
		
		
