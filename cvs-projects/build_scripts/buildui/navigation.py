import sys
from WebKit.SidebarPage import SidebarPage

PEXPECT_PATH = "/home/build/bin/Pexpect"
sys.path.append(PEXPECT_PATH)

import version
import server
import pexpect

class SitePage(SidebarPage):
	""" Navigation Frame for all of the ReleaseRequest Pages"""


	def __init__(self):
		SidebarPage.__init__(self)
		self.tag = self.version = self.edition = None

	def cornerTitle(self):
		return ""

	def isDebuggin(self):
		return 0

	def writeSidebar(self):
		adapterName = self.request().adapterName()
		self.writeMenu()
		self.writeVersions()
		self.menuHeading("")
		self.menuItem("")
		self.menuItem("")
		self.menuHeading("")
		self.menuItem("")
		self.menuItem("Logout", "%s/Main?logout=1"%adapterName)
	
	def testDB(self):
		testDB = server.server()
		if testDB.Connect() in ["Can't connect to MySQL database"]:
			child = pexpect.spawn("mysqladmin -u support -p flush-hosts")
			child.expect('.*:')
			child.sendline('support')
		else:
			testDB.Close()
	#}

	def awake(self, transaction):
		SidebarPage.awake(self,transaction)
		req = self.request()
		ses = self.session()

		if req.hasField('version') and req.hasField('edition') and req.hasField('tag'):
			ses.setValue('version', req.value('version'))
			ses.setValue('edition', req.value('edition'))
			ses.setValue('tag',req.value('tag'))
		elif req.hasField('version'):
			ses.setValue('version', req.value('version'))
			if ses.hasValue('edition'): 
				ses.delValue('edition')
			if ses.hasValue('tag'): 
				ses.delValue('tag')


	def writeMenu(self):
		self.testDB()

		tag = edition = version = None

		req = self.request()
		ses = self.session()
		
		if ses.hasValue('version'):
			version = ses.value('version')
		if ses.hasValue('edition'): 
			edition = ses.value('edition')
		if ses.hasValue('tag'): 
			tag = ses.value('tag')

		releaseDB = server.server()
		releaseDB.Connect()
	
		adapterName = self.request().adapterName()
		self.menuHeading('Products')
	
		productVersions = releaseDB.Command("SELECT version FROM BuildCfg.products GROUP BY version")
		productVersions = map(lambda x: str(x['version']) , productVersions)

		for ver in productVersions:
			if version == ver:
				self.writeln('<u>%s</u>' % ver)
				
				editions = releaseDB.Command("SELECT edition,tag_match FROM BuildCfg.products WHERE version='%s' ORDER BY edition" % ver)
				editions = map(lambda x: [ str(x['edition']) , str(x['tag_match']) ] , editions)

				for edition in editions:
					if edition and tag and (edition[0] in edition and edition[1] in tag):	
						self.menuItem('<I>%s (%s)</I>' % (edition[0], edition[1]), '%s/QueryDB?version=%s&edition=%s&tag=%s' % \
												  (adapterName, ver, edition[0], edition[1]))


					else:
						self.menuItem('%s (%s)' % (edition[0], edition[1]), '%s/QueryDB?version=%s&edition=%s&tag=%s' % \
												  (adapterName, ver, edition[0], edition[1]))



			else:
				self.menuItem("%s" % ver, "%s/Main?version=%s" % (adapterName, ver), indentLevel=0) 
			



		self.menuHeading("Other")
		self.menuItem("Crontab", "crontabMain.py" ,indentLevel=0 )
		
		
	def writeVersions(self):
		self.menuHeading("Version")
		self.menuItem("builddb "+version.version)
		

	def title(self):
		return self.request().contextName()

#end SitePage	
