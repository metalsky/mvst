from navigation import SitePage

import server
import bugzServer


ErrType = type("")
ErrataType = type([])


class Queue(SitePage):
	def title(self):
		return "Queue"

	def writeError(self, error):
		self.writeln('''<p style=color:#FF0000">%s</p>''' % self.htmlEncode(error))
		return

	def writeContent(self):
		self.db = server.server()
		self.bugzDB = bugzServer.server()

		err = self.db.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			return
		
		err = self.bugzDB.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			self.db.Close()
			return


		self.writeQueue()
		self.db.Close()
		self.bugzDB.Close()

	def writeCycle(self, number):
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(number))
		if type(result) == ErrType:
			self.writeError(result)
			return
		cycle = result[0]
		process_date = cycle['process_date']
		live_date = cycle['live_date']
		
		
		result = self.db.Command('''SELECT COUNT(*) FROM ReleaseAutomation.merged WHERE release_cycle_id=%d'''%(number))
		if type(result) == ErrType:
			self.writeError(result)
			return
		updates = result[0]['COUNT(*)']
		
		#Write table header
		self.writeln('''<table Cols=14, cellspacing=0 cellpadding=7 border=0>''')
		self.writeln('''<tr bgcolor=#202080><td COLSPAN=2><font color="#ffffff"><b>ReleaseCycle</b></font></td><td COLSPAN=3><font color="#ffffff"><b>Process On: %s</b></font></td><td COLSPAN=8><font color="#ffffff"><b>LIVE BY: %s</b></font></td><td><font color="#ffffff">Merged Updates: %d</font></td></tr>'''%(process_date, live_date, updates))
		self.writeln('''<tr bgcolor=#202080><td><font color="#ffffff">ID</font></td><td COLSPAN=2><font color="#ffffff">Product</font></td><td><font color="#ffffff">Package</font></td><td><font color="#ffffff">State</font></td><td><font color="#ffffff">Upload Priority</font></td><td><font color="#ffffff">Bugs</font></td><td><font color="#ffffff">Errata</font></td><td><font color="#ffffff">Type</font></td><td><font color="#ffffff">Requested By</font></td><td><font color="#ffffff">Date Submitted</font></td><td><font color="#ffffff">Actions</font></td><td></td><td><font color="#ffffff">Assignee</font></td></tr>''')
		self.writeln('''<tr colspan=14><td></td></tr>''')


		#write Contents
		self.writeMerged(number)

		
		self.writeln('''</table><hr align='left' width='50%' size=1 color='black'><br><p>''')

		return


	def writeMerged(self, cycle_id):
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.merged WHERE release_cycle_id=%d'''%(cycle_id))
		if type(result) == ErrType:
			self.writeError(result)
			return
		for merged in result:
			id = merged['id']
			name = merged['name']
			product_id = int(merged['products_id'])
			state = self.stateText(merged['action_date'], merged['state'])
			upload_priority = merged['severity']
			errata_link = self.errataMergedText(merged['id'], name)
			if merged['assignee_id']:
				assignee = self.submitterText(merged['assignee_id'])
			else:
				assignee = ""
			products = self.db.Command('''SELECT * FROM BuildCfg.products WHERE id=%d'''%(product_id))
			if type(products) == ErrType:
				self.writeError(products)
				return
			if len(products) < 1:
				self.writeError('''Can't find product_id: %d in database'''%(product_id))

			version = products[0]['version']
			product = self.productText(products[0]['edition'], products[0]['product_match'])
			
			self.writeln('''<tr bgcolor=#c8c8c8><td>%s</td><td>%s</td><td>%s</td><td><b>%s</b></td><td>%s</td><td>%s</td><td></td><td>%s</td><td COLSPAN=5></td><td>%s</td></tr>'''%(id, product, version, name, state, upload_priority, errata_link, assignee))
			self.writeCombined(merged['id'])
			self.writeln('''<tr><td COLSPAN=14></td></tr>''')
		#end for

		return	



	def writeCombined(self, merged_id):
		result = self.db.Command('''SELECT * FROM ReleaseAutomation.combined WHERE merged_id=%d'''%(int(merged_id)))
		if type(result) == ErrType:
			self.writeError(result)
			return
		
		for combined in result:
			id = combined['id']
			severity = combined['severity']
			submitter_id = combined['submitter_id']
			submit_date = combined['submit_date']
			
			#put together submitter
			submitter = self.submitterText(submitter_id)
	

			#get raw requests
			raw_requests = self.db.Command('''SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%d'''%(int(id)))
			if type(raw_requests) == ErrType:
				self.writeError(raw_requests)
				return

			#handle bugs
			bug_list = []
			for request in raw_requests:
				if int(request['bug_id']) not in bug_list:
					bug_list.append(int(request['bug_id']))
			
			bug_list.sort()
			bugs = self.bugText(bug_list)
			

			#handle types
			type_list = []
			for request in raw_requests:
				if request['type'] not in type_list:
					type_list.append(request['type'])

			types = self.typeText(type_list)


			#Errata link
			errata = self.errataSingleText(combined['id'], combined['name'])

			#Actions links
			actions = self.actionText(combined['id'], combined['name'])
				

			#Write request
			#Bugs, Upload Priority, Errata, Type, Requested By, Date Submitted, Actions
			self.writeln('''<tr bgcolor=#d8d8d8><td COLSPAN=6><td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td></td></tr>'''%(bugs, errata, types, submitter, submit_date, actions))


		return


	def writeQueue(self):
		'''Override me'''
		return

	def stateText(self, date, state):
		if state == "live":
			return "Live: %s"%(str(date))
		elif state == "docsdone":
			return "Docs Done"
		elif state == "approved":
			return "Approved"
		elif state == "waiting":
			return "Wating Approval"
		
		return "unknown"
	
	def errataMergedText(self, id, name):
		return '''<a href="%s/Errata?i=%s&n=%s&t=m">Merged</a>''' %(self.request().adapterName(),id,name)


	def errataSingleText(self, id, name):
		return '''<a href="%s/Errata?i=%s&n=%s&t=c">Single</a>''' %(self.request().adapterName(),id,name)


	def productText(self, edition, product_match):
		foundation = "foundation%"
		if edition.find("foundation") == 0:
			result = self.db.Command('''SELECT * from BuildCfg.products WHERE product_match="%s" AND released="Y" AND NOT edition LIKE "%s"'''%(product_match, foundation))
			if type(result) == ErrType:
				self.writeError(result)
				return

			editions = {}
			for product in result:
				editions[product['edition']] = ""
			edition_text = ", ".join(editions)
		else:
			edition_text = edition

		return edition_text
	
			

	def actionText(self, id, name):
		return '''<a href="%s/Action?i=%d&n=%s">Edit</a>'''%(self.request().adapterName(), id, name)
	

	def bugText(self, bug_list):
		txt = ""
		for bug in bug_list:
			txt += '''<a href="http://bugz.sh.mvista.com/bugz/show_bug.cgi?id=%s">%s</a>, '''%(bug, bug)

		if txt:
			txt = txt[:-2]
		return txt


	def typeText(self, type_list):
		txt = ""
		for type in type_list:
			txt += type + ", "

		if txt:
			txt = txt[:-2]
		return txt

	def submitterText(self, id):
		result = self.bugzDB.Command('''SELECT * FROM profiles WHERE userid=%d'''%(id))
		if type(result) == ErrType:
			self.writeError(result)
			return

		profile = result[0]
		return '''<a href="mailto:%s">%s</a>'''%(profile['login_name'], profile['realname'])	


#end Queue
