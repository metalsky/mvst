from navigation import SitePage
import server
import bugzServer
import pyroServer

import util


ErrType = type("")


class Errata(SitePage):

	def title(self):
		name = self.request().field("n","")
		if not name:
			return 'Empty Errata'
		else:
			return "Errata: "+name
	
	def writeError(self, error):
		self.writeln('''<p style="color:#FF0000">%s</p>''' % error)
		return

	def writeContent(self):
		request_id = self.request().field("i","")
		request_type = self.request().field("t", "")

		if not request_id:
			self.writeln('''Empty Errata''')
			return
		#else
		
		
		self.db = server.server()
		err = self.db.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			return
		#else
		self.bugzDB = bugzServer.server()
		err = self.bugzDB.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			self.db.Close()
			return
		#else
	
		self.pyroServer = pyroServer.server()
		err = self.pyroServer.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			self.pyroServer.Close()
		#else
		

		#Generate errata
		err = self.generateErrata(request_id, request_type)
		if type(err) == ErrType:
			self.writeError(err)

		self.db.Close()
		self.bugzDB.Close()
		self.pyroServer.Close()
		return


	
	def generateErrata(self, request_id, request_type):
		#setup errata
		errata =  util.errata(self.db, self.bugzDB, self.pyroServer)
		if request_type.lower() == "m":
			err = errata.setMerged(request_id)
		elif request_type.lower() == 'c':
			err = errata.setCombined(request_id)

		if type(err) == ErrType:
			return err

		#generate errata
		err = errata.generate()
		if type(err) == ErrType:
			return err

		#write errata
		text = errata.write()
		
		#dump errata to page
		text = self.htmlEncode(text)
		text = text.replace("\n", "<br>\n")
		self.writeln(text)


		return None


	#end generateErrata

#end Main
