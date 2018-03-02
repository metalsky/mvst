from WebKit.SidebarPage import SidebarPage

import version

class SitePage(SidebarPage):
	""" Navigation Frame for all of the ReleaseRequest Pages"""
	
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
		self.menuItem("ReleaseAutomation bugz", "http://bugz/buglist.cgi?query_format=advanced&short_desc_type=allwordssubstr&short_desc=&product=Internal+Tools&component=Release+System&long_desc_type=substring&long_desc=&bug_file_loc_type=allwordssubstr&bug_file_loc=&status_whiteboard_type=allwordssubstr&status_whiteboard=&keywords_type=allwords&keywords=&deadlinefrom=&deadlineto=&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&emailassigned_to1=1&emailtype1=substring&email1=&emailassigned_to2=1&emailreporter2=1&emailcc2=1&emailtype2=substring&email2=&bugidtype=include&bug_id=&chfieldfrom=&chfieldto=Now&chfieldvalue=&cmdtype=doit&order=Reuse+same+sort+as+last+time&field0-0-0=noop&type0-0-0=noop&value0-0-0=")
		self.menuItem("")
		self.menuHeading("")
		self.menuItem("")
		self.menuItem("Logout", "%s/Logout?logout=1"%adapterName)

	def writeMenu(self):
		adapterName = self.request().adapterName()
		
		self.menuItem("Home", "%s/" % adapterName)
		
		self.menuHeading("Request Queues")
		self.menuItem("Current", "%s/Current/" % adapterName)
		self.menuItem("Previous", "%s/Previous/" % adapterName)

		self.menuHeading("Actions")
		self.menuItem("Submit Request", "%s/Submit/" %(adapterName))

		self.menuHeading("Instructions")
		self.menuItem("Release Schedule", "http://wiki.sh.mvista.com/thebazaar2/bin/view/Engineering/ReleaseRequest")
		self.menuItem("Release Process", "http://wiki.sh.mvista.com/thebazaar2/bin/view/Process/ApplicationPatchUpload")
		self.menuItem("Bug Fields", "%s/BugInstructions/" %adapterName)

	
	def writeVersions(self):
		self.menuHeading("Version")
		self.menuItem("ReleaseAutomation "+version.version)
		

	def title(self):
		return self.request().contextName()

#end SitePage	
