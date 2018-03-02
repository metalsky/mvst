from SecurePage import SecurePage

import server
import bugzServer
import pyroServer

import util

ErrType = type("")


class Submit(SecurePage):
	def title(self):
		return "Release Request Form"

	
	def awake(self, transaction):
		self.db = None
		self.bugzDB = None
		self.pyroServer = None
		SecurePage.awake(self, transaction)
		sess = self.session()
		
		#Form variables
		self.VarTemplate = {
			'releaseForm': 1,
			'releaseState': False,
			'errors': None,
			'package':"",
			'bug': "",
			'type': {'target':0, 'cross':0, 'common':0, 'host':0, 'host-tool':0},
			'priority':"",
			'notes':"",
			'cycle_id':"",
			}

		if sess.hasValue('submitVars'):
			self.vars = sess.value('submitVars')
			if self.vars.keys().sort() != self.VarTemplate.keys().sort():
				print "key mismatch"
				self.resetVars()
		else:
			#print "missing vars"
			self.resetVars()
			sess.setValue('submitVars', self.vars)
		self._error = None

	
	def resetVars(self):
		try:
			for key in self.vars.keys():
				del(self.vars[key])
		except:
			self.vars = {}

		for key in self.VarTemplate.keys():
			self.vars[key] = self.VarTemplate[key]
		
		#print self.vars

	
	def writeContent(self):
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


		self.realWriteContent()

		self.db.Close()
		self.bugzDB.Close()
		self.pyroServer.Close()
		return


	def realWriteContent(self):
		current_cycle = util.getCurrentReleaseCycle(self.db)
		if type(current_cycle) == ErrType:
			self.writeError(current_cycle)
			return

		self.vars['cycle_id'] = current_cycle

		#Handle Errors and success
		errors = self.vars['errors']
		state = self.vars['releaseState']
		if not state and errors:
			self.writeError(errors)	
		elif state:
			self.writeSuccess()
			return
		
		self.writeForm()
		self.writeln('''
		<br><p>
		<b>NOTES:</b> 
		<br>
		Package name is as it appears in the collective. 
		This is sometimes different than the name of the rpms produced.
		<br><p>
		Please have patience and only hit the 'Submit' button once, 
		it will take some time to process your request.
		''')
		
		return

	def writeError(self, error):
		self.writeln('''<p style="color:#FF0000">%s
		</p>
		<p style="color:#FF0000">
		Please fix the above errors and try again.
		</p>
		<br><p>'''\
			 %(str(error)))
		return


	def writeSuccess(self):
		self.writeln('''<p style="color:#333399">
		Thank You. Your Request has been Submitted!
		</p>''')
		#Im not sure if this is the proper place?
		self.resetVars()
		return

	def writeForm(self):
		cmd = '''SELECT * FROM ReleaseAutomation.release_cycle WHERE id=%d'''%(self.vars['cycle_id'])
		result = self.db.Command(cmd)
		if type(result) == ErrType:
			self.writeError(result)
			return
		#else
		cycle = result[0]
		self.writeln('''Current Cycle Date is %s, <b>LIVE</b> by <b>%s</b>.<br><p>'''%(cycle['process_date'], cycle['live_date']))
		
		self.writeln('<br><p><b>Please fill out the information below:</b>')	
		#Form
		self.writeln('''
		<form method="post">
		<input name="releaseForm" type="hidden" value="%(releaseForm)d">
		
		<label for="package">Package Name:</label>
		<input type="text" name="package" value="%(package)s">

		<br><p><label for="bug">Bug Number:</label>
		<input type="text" name="bug" value="%(bug)s">
		
		<br><p><label for"type">Types:</label>''' % self.vars)

		#Type
		dict = self.vars['type']
		for key in dict:
			self.writeln('''
			&nbsp;&nbsp;&nbsp;<input type="checkbox" name="%s" ''' % key)
			if dict[key]:
				self.writeln('''checked="True">%s''' % key)
			else:
				self.writeln('''>%s''' % key)

		#Priority
		self.writeln('''<br><p><label for="priority">Upload Priority:</label>
				<select name="priority">
		''')
		for prio in ["NORMAL", "CRITICAL", "SECURITY", "ASYNC-CRITICAL"]:
			if prio == self.vars['priority']:
				self.writeln('''<option value="%s" selected="True">%s''' \
					%(prio, prio))
			else:
				self.writeln('''<option value="%s">%s''' %(prio,prio))

		self.writeln('''</select>''')

	
		self.writeln('''
		<br><p><label for="package">Additional Notes (optional):</label>
		<br>
		<textarea name="notes" rows=4 cols=30>%(notes)s</textarea>
		
		<br><p>
		<input name="_action_process" type="submit" value="Submit">
		&nbsp;&nbsp;&nbsp;
		<input name="_action_clear" type="submit" value="Clear">
		</p>
		</form>
		''' % self.vars)
		return


	def process(self):
		#print self.request().fields()
		# save all contents
		self.vars['package']=self.request().field('package')
		self.vars['bug']=self.request().field('bug')
		self.vars['errors']= None
		self.vars['priority']=self.request().field('priority')
		self.vars['notes']=self.request().field('notes')
		self.vars['releaseState'] = False
		dict = self.vars['type']
		for t in dict:
			if self.request().hasField(t):
				dict[t] = 1
			else:
				dict[t] = 0
		#print self.vars


		#validate everything
		submitter_id = self.session().value("authenticated_user_id", None)
		submitter_user = self.session().value("authenticated_user", None) 
		name = self.vars['package']
		bug_number = self.vars['bug']
		priority = self.vars['priority']
		notes = self.vars['notes']

		type_dict = self.vars['type']
		type_list = []
		for t in type_dict:
			if self.request().hasField(t):
				type_list.append(t)
		#end type_dict
		
		if not self.db:
			self.db = server.server()
			self.bugzDB = bugzServer.server()
			self.pyroServer = pyroServer.server()
			error = self.db.Connect()
			if type(error) == ErrType:
				self.vars['errors'] = error
				self.writeBody()
				return
			error = self.bugzDB.Connect()
			if type(error) == ErrType:
				self.vars['errors'] = error
				self.writeBody()
				return
			error = self.pyroServer.Connect()
			if type(error) == ErrType:
				self.vars['errors'] = error
				self.wrteBody()
				return
		#	

		request = util.request(self.db, self.bugzDB, self.pyroServer)
		error = request.verify(submitter_id, submitter_user, name, bug_number, \
				type_list, priority, notes)
		if type(error) == ErrType:
			self.db.Close()
			self.bugzDB.Close()
			self.pyroServer.Close()
			self.vars['errors'] = error
			self.writeBody()
			return


		#Submit Request
		error = request.submit()
		self.db.Close()
		self.bugzDB.Close()
		self.pyroServer.Close()

		if type(error) == ErrType:
			self.vars['errors'] = error
			self.writeBody()
			return 

		self.vars['releaseState'] = True
		self.writeBody()
		return
	#end process


	def clear(self):
		self.resetVars()
		self.writeBody()
	#end clear
	

	def actions(self):
		acts = SecurePage.actions(self)
		
		#make sure form is valid ?
		try:
			releaseForm = int(self.request().field('releaseForm'))
		except:
			releaseForm = 0

		#print "release", releaseForm
		#print "vars reelase", self.vars['releaseForm']
		if releaseForm == self.vars['releaseForm']:
			acts.extend(['process', 'clear'])
			self.vars['releaseForm'] += 1
			self.vars['releaseState'] = False
			self.vars['errors'] = None
		else:
			#print "clear data"
			self.resetVars()

		return acts
	#end actions

#end Submit
