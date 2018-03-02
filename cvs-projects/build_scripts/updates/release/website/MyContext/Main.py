from navigation import SitePage

import server

class Main(SitePage):

	def title(self):
		return 'MVZ Update Release Request'

	def writeContent(self):
		adapterName = self.request().adapterName()
		self.writeln('<h1>MVZ Update Release Request System</h1>')
		self.writeln('''
		<p>Please choose from an option on the left. Or try submitting a 
		<a href=%s/Submit>Release Request</a>.''' % adapterName)
		
		try:
			db = server.server()
			db.Connect()
			result = db.Command('''SELECT COUNT(id) FROM ReleaseAutomation.combined''') 
			combined = result[0]['COUNT(id)']

			result = db.Command('''SELECT COUNT(id) FROM ReleaseAutomation.merged''')
			merged = result[0]['COUNT(id)']
			diff = int(combined) - int(merged)
			
			db.Close()

			self.writeln('''<br><p><br><p>Since its start on June 1, 2007, this site has processed <b>%d</b> total requests and <b>%d</b> merged request.<br><p>Having regular cycles has saved a total of <b>%s</b> uploads.'''%(combined, merged, diff))
		except:
			self.writeln("")
	

		self.writeln('''
		<p><br><p>Please give feedback 
		<a href="mailto:release-request@mvista.com">here</a>.</p>''')

	
#end Main
