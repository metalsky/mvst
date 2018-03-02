from WebKit.Page import Page
import server
import bugzServer
import pyroServer

import util


ErrType = type("")


class ErrataFields(Page):

	def title(self):
		name = self.request().field("n","")
		return "Errata: "+name

	def writeError(self, error):
		self.writeln('''ERROR="%s"''' % error)
		return
	
	def writeHTML(self):
		self.writeContent()

	def writeContent(self):
		request_id = self.request().field("i","")
		request_type = self.request().field("t", "")

		if not request_id:
			self.writeError('''Request ID not specified''')
			return
		#else
		if not request_type:
			self.writeError('''Request Type not specified''')
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
			return
		#else


		#Get and print fields
		err = self.getErrataFields(request_id, request_type)
		if type(err) == ErrType:
			self.writeError(err)

		self.db.Close()
		self.bugzDB.Close()
		self.pyroServer.Close()
		return
	#end writeContent


	def getErrataFields(self, request_id, request_type):
		#setup errata
		errata = util.errata(self.db, self.bugzDB, self.pyroServer)
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

		#get fields 
		fields = errata.TemplateData
		del(fields["<RPMS>"])

		#get rpms
		rpms = errata.Rpms
		
		#write info
		for key in fields:
			if fields[key]:
				self.writeln('''%s=%s<br>'''%(key.lstrip('<').rstrip('>'), fields[key]))
			else:
				self.writeln('''%s=none<br>'''%(key.lstrip('<').rstrip('>')))

		for rpm_type in rpms:
			if rpm_type == "cross":
				arch_buffer = ""
				wrote_arch = False
				type_dict = rpms[rpm_type]
				for arch_name in type_dict:
					buffer = ""
					wrote = ""
					arch_dict = type_dict[arch_name]
					for host_name in arch_dict:
						if len(arch_dict[host_name]) < 1:
							buffer += "%s=none<br>\n"%(host_name)
						else:
							buffer += "%s="%(host_name)
							buffer += ",".join(arch_dict[host_name])
							buffer += "<br>\n"
							wrote = True
						#
					#for hosts
					if wrote:
						arch_buffer += "%s=[<br>\n"%(arch_name)
						arch_buffer += buffer
						arch_buffer += "]<br>\n"
						wrote_arch = True
					else:
						arch_buffer += "%s=none<br>\n"%(arch_name)
					#
				#for archs

				if wrote_arch:
					self.writeln("%s=[<br>\n"%(rpm_type.upper()))
					self.writeln(arch_buffer[:-1])
					self.writeln("]<br>")
				else:
					self.writeln("%s=none<br>"%(rpm_type.upper()))
				#

			else:
				buffer = ""
				wrote = False
				type_dict = rpms[rpm_type]
				for arch_name in type_dict:
					if len(type_dict[arch_name]) < 1:
						buffer += "%s=none<br>\n"%(arch_name)
					else:
						buffer += "%s="%(arch_name)
						buffer += ",".join(type_dict[arch_name])
						buffer += "<br>\n"
						wrote = True
					#
				#for
				if wrote:
					self.writeln("%s=[<br>\n"%(rpm_type.upper()))
					self.writeln(buffer[:-1])
					self.writeln("]<br>")
				else:
					self.writeln("%s=none<br>"%(rpm_type.upper()))
			#
		#end for

		

		return None
		#end getErrataFields
		
#end ErrataFields


