from WebKit.SidebarPage import SidebarPage


class SitePage(SidebarPage):
	""" Navigation Frame for all of the ReleaseRequest Pages"""
	
	def cornerTitle(self):
		return ""

	def isDebuggin(self):
		return 0

	def writeSidebar(self):
		self.menuHeading("")
		self.menuItem("")

	def writeMenu(self):
		return
	
	def writeVersions(self):
		return	

	def title(self):
		return self.request().contextName()

#end SitePage	
