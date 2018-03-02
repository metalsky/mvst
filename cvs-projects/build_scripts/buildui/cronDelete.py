from SecurePage import SecurePage
import cronJob


class cronDelete(SecurePage):
	def title(self):
		return "Confirm Delete"

	def awake(self, transaction):
		SecurePage.awake(self, transaction)
		req = self.request()
		ses = self.session()

		if req.hasField('deletionConfirmed') and req.field('deletionConfirmed') == 'True':
			ses.value('currentParser').removeJobByID( req.field('jobIdToDelete') )
			self.sendRedirectAndEnd('crontabMain.py')

	def writeContent(self):
		req = self.request()
		ses = self.session()
		wr = self.writeln

		parser = ses.value('currentParser')
		currentJob = parser.getJobByID( req.field('jobIdToDelete') )

		wr('Are you sure you wish to delete the following job?<br><br>')
		wr(currentJob.outputHTML())


		wr('''<table><tr>''')
		wr('''<form>''')
		wr('''<td><input type="submit" value="Confirm"></td>''')
		wr('''<input type="hidden" name="jobIdToDelete" value="%s">''' % currentJob.ID)
		wr('''<input type="hidden" name="deletionConfirmed" value="True">''')
		wr('''</form>''')


		wr('''<form action=crontabMain>''')
		wr('''<td><input type="submit" value="Cancel"></td>''')
		wr('''<input type="hidden" name="jobIdToDelete" value="%s">''' % currentJob.ID)
		wr('''<input type="hidden" name="deletionConfirmed" value="False">''')
		wr('''</form></tr></table>''')
