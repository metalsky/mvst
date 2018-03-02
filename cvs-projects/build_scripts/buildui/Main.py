from SecurePage import SecurePage
from DEBUG import *
DEBUG = isDebugMode()

class Main(SecurePage):

	def title(self):
		return 'Build Database Interaction'

	def writeContent(self):
		ses = self.session()
		req = self.request()
		wr = self.writeln
		adapterName = self.request().adapterName()
		self.writeln('<h1>BuildDB</h1>')
		self.writeln('Please select an edition from the choices on the left.')

		if DEBUG: #{{{
			wr("<H2>Session Variables</H2>")
			for key in ses.values():
				wr('%s : %s<BR>' % (key, ses.value(key)))
			wr("<H2>Request Variables</H2>")
			for key in req.fields():
				wr('%s : %s<BR>' % (key, req.field(key))) #}}}



	
#end Main
