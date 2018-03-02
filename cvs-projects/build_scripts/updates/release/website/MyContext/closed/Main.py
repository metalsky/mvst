from navigation import SitePage

class Main(SitePage):

	def title(self):
		return 'MVZ Update Release Request'

	def writeContent(self):
		adapterName = self.request().adapterName()
		self.writeln('<h1><font color=red>The Release Request System is currently closed for maintenance.</font></h1>')
		
		self.writeln('''<p><br>
		<b> This site is currently getting the following enhancements: </b><p>\n
		''')

		self.writeln('''
		<p>
		<b>The server should be back online within a few hours.</b>
		<br><p>''')

	
#end Main
