from SecurePage import SecurePage

import server
import bugzServer
import pyroServer

import util
import users

ErrType = type("")


class Action(SecurePage):
	def title(self):
		name = self.request().field("n","")
		return "Edit: %s"%(name)

	
	def awake(self, transaction):
		self.Actions = []
		self.db = None
		self.bugzDB = None
		self.pyroServer = None
		self.Trans = transaction
		self.App = transaction.application()
		SecurePage.awake(self, transaction)
		sess = self.session()
			

		#Form variables
		self.VarTemplate = {
			'editForm': 1,
			'editState': 0,
			'errors': "",
			'id': None,
			'name': None,
			'user_id': None,
			'user_login': None
			}
		
		if sess.hasValue('actionVars'):
			self.vars = sess.value('actionVars')
			if self.vars.keys().sort() != self.VarTemplate.keys().sort():
				print "key mismatch"
				self.resetVars()
		else:
			self.resetVars()
			sess.setValue('actionVars', self.vars)

	

		#DB:
		self.db = server.server()
		err = self.db.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			return
		
		self.bugzDB = bugzServer.server()
		err = self.bugzDB.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			self.db.Close()
			return

		self.pyroServer = pyroServer.server()
		err = self.pyroServer.Connect()
		if type(err) == ErrType:
			self.writeError(err)
			self.pyroServer.Close()
			return

		
		#Action vars
		self.vars['id'] = int(self.request().field("i", None))
		self.vars['name'] = self.request().field("n", None)
		self.vars['user_id'] = int(self.session().value("authenticated_user_id", None))
		self.vars['user_login'] = self.session().value("authenticated_user", None)


		##Actions

		self.Actions = []
		#approvers
		if self.vars['user_login'] in users.approvers:
			self.Actions.append(util.managerAction(self.db, self.bugzDB, self.pyroServer, \
					self.vars['user_id'], self.vars['user_login']))
	
		#Moderators
		if self.vars['user_login'] in users.moderators:
			self.Actions.append(util.moderatorAction(self.db, self.bugzDB, self.pyroServer, \
					self.vars['user_id'], self.vars['user_login']))


		#submitters
		result = self.db.Command('''SELECT submitter_id FROM ReleaseAutomation.combined WHERE id=%d'''%(self.vars['id']))
		if type(result) == ErrType:
			self.vars['errors'] = result
			return
		if len(result) < 1:
			self.vars['errors'] = "The request does not exists. Perhaps it was deleted while you were looking at it."
			return
		if self.vars['user_id'] == int(result[0]['submitter_id']):
			self.Actions.append(util.submitterAction(self.db, self.bugzDB, self.pyroServer,  \
					self.vars['user_id'], self.vars['user_login']))
		
		#


		## Init Actions
		for action in self.Actions:
			action.setVars(self.vars)
			err = action.setCombined(self.vars['id'])
			if type(err) == ErrType:
				self.vars['errors'] = err
				return
			self.vars = action.mergeVars(self.vars)

		#
		return


	
	def resetVars(self):
		try:
			for key in self.vars.keys():
				del(self.vars[key])
		except:
			self.vars = {}

		for key in self.VarTemplate.keys():
			self.vars[key] = self.VarTemplate[key]
		
		return
	
	def writeContent(self):
		#Handle Errors and success
		errors = self.vars['errors']
		state = self.vars['editState']
		if errors:
			self.writeError(errors)
			self.db.Close()
			self.bugzDB.Close()
			self.pyroServer.Close()
			return
		if state == 1:
			self.writeSuccess()
			self.db.Close()
			self.bugzDB.Close()
			self.pyroServer.Close()
			return
		elif state == 2:
			self.writeNoChange()
			self.db.Close()
			self.bugzDB.Close()
			self.pyroServer.Close()
			return

		
		err = self.writeForm()
		if type(err) == ErrType:
			self.writeError(err)

		self.db.Close()
		self.bugzDB.Close()
		self.pyroServer.Close()
		return


	def writeError(self, error):
		self.writeln('''<p style="color:#FF0000">%s
		</p>
		<p style="color:#FF0000">
		Please fix the above errors and try again.
		</p>
		<br><p>'''\
			 %(str(error)))
		self.resetVars()
		return


	def writeSuccess(self):
		self.writeln('''<p style="color:#333399">
		Thank You. Your changes have been saved!
		</p>''')
		#Im not sure if this is the proper place?
		self.resetVars()
		return

	
	def writeNoChange(self):
		self.writeln('''<p style="color:#202080">
		No changes were made.</p>''')
		self.resetVars()
		return
	
	
	def writeForm(self):
		if not self.Actions:
			return
			
		parentAction = self.Actions[0]
		self.writeln(parentAction.formHeader())

		did_action = False
		for action in self.Actions:
			self.writeln('''<div style="background:#e8e8f0">''')
			txt = action.form()
			if type(txt) == ErrType:
				self.writeln(txt)

			else:
				self.writeln(txt[0])
				did_action = True
			self.writeln('''</div>''')
		#

		if did_action:
			self.writeln(parentAction.formFooter())

		return


	def process(self):
		# save all contents
		for action in self.Actions:
			fields = action.getFields()
			for field in fields:
				try:
					self.vars[field] = self.request().field(field)
				except:
					self.vars[field] = ""
			#end fields
			action.setVars(self.vars)
		#end actions


		
		#process
		action_taken = False
		for action in self.Actions:
			err = action.process()
			if type(err) == ErrType:
				self.vars['errors'] = err
				self.writeBody()
				return
			if err == True:
				action_taken = True
			#else
		#end for action

		if action_taken:
			self.vars['editState'] = 1
		else:
			self.vars['editState'] = 2
		self.writeBody()
		return
	#end process

	
	def cancel(self):
		self.resetVars()
		self.App.forward(self.Trans, "Current")
		return


	def actions(self):
		acts = SecurePage.actions(self)
		
		#make sure form is valid ?
		try:
			editForm = int(self.request().field('editForm'))
		except:
			editForm = 0

		if editForm == self.vars['editForm']:
			acts.extend(['process', 'cancel'])
			self.vars['editForm'] += 1
			self.vars['editState'] = False
			self.vars['errors'] = ""
		else:
			#self.vars['editForm'] = 1
			self.resetVars()

		return acts
	#end actions

#end Submit
