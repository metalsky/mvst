from SecurePage import SecurePage
from DEBUG import *
import server
import bwLog
import cronJob, cronParser
import authedUsers
DEBUG = isDebugMode()

class crontabMain(SecurePage):
	
	def __init__(self):
		SecurePage.__init__(self)
	
	def title(self):
		return "Crontab Main Page (%s Jobs)" % self.session().value('cronViewType')

	def writeStyleSheet(self):
		from LTStyle import sheet
		stylesheet = sheet()
		self.writeln(stylesheet)

	def awake(self, transaction):
		SecurePage.awake(self, transaction)
		ses = self.session()
		req = self.request()

		if req.hasValue('saveChanges'):
			ses.value('currentParser').outputToFile()

		if not ses.hasValue('currentParser'):
			ses.setValue('currentParser', cronParser.cronParser( self.session().value('authenticated_user') ))

		if req.hasField('setViewType'):
			ses.setValue('cronViewType', req.field('setViewType'))

		if not ses.hasValue('cronViewType'):
			ses.setValue('cronViewType','Active')
	
	def writeContent(self):
		wr = self.writeln
		ses = self.session()
		req = self.request()
		#wr("Session:<BR>")
		#wr(ses.values())
		#wr("<BR>request:<BR>")
		#wr(req.fields())
		#wr("<br><br>")

		if req.hasValue('saveChanges'):
			wr('Current crontab written to /tmp/crontab.new<br>')

		viewType = ses.value('cronViewType')

		if ses.value('authenticated_user') in authedUsers.buildUsers(): 
			wr(''' <TABLE ALIGN=CENTER> <TR>
					<TD><A HREF="cronEdit?addNewJob">New Job</a></TD>
					<TD>|</TD>
					<TD><A HREF=cronGroupMgr>Manage Groups</a></TD>
					<TD>|</TD>''')

		else:
			wr('''<TABLE ALIGN=CENTER><TR>''')

		wr('''<TD><A HREF=crontabMain.py?setViewType=Active>View Active Jobs</TD>
					<TD>|</TD>
					<TD><A HREF=crontabMain.py?setViewType=Inactive>View Inactive Jobs</TD>
					<TD>|</TD>
					<TD><A HREF=crontabMain.py?setViewType=24h>View next 24 hours</TD>
					''')


		if ses.value('authenticated_user') in authedUsers.buildUsers(): 
			wr('''<TD>|</TD>
				  <TD><A HREF=crontabMain?saveChanges=True>Save Changes</TD>
				  </TABLE>''')

		else:
			wr('''</TABLE>''')

		
		
		parser = ses.value('currentParser')
		groups = parser.getGroups()


		for group in groups:
			self.writeln("<TABLE border=0 bgcolor=#7e7e7e width=100% CELLSPACING=0 CELLPADDING=0>")
			self.writeln("<TR bgcolor=#7e7e7e><td><B><FONT SIZE=6 COLOR=WHITE>%s</td></B></FONT></TR><TD>" % group)
			jobs = parser.getJobs(group)

			outputCount = 0

			if viewType == 'Active':
				for job in jobs:
					if job.isActive():
						outputCount += 1
						self.writeln(job.outputHTML())


				if outputCount == 0:
					self.writeln('''<TABLE width=100%% border=0 bgcolor=#c8c8c8><TR bgcolor=#c8c8c8><TD>This %s group is empty.</TR></TD></TABLE>''' % viewType)
				self.writeln("</TD></TABLE>")


			elif viewType == 'Inactive':
				for job in jobs:
					if not job.isActive():
						outputCount += 1
						self.writeln(job.outputHTML())
					
				if outputCount == 0:
					self.writeln('''<TABLE width=100%% border=0 bgcolor=#c8c8c8><TR bgcolor=#c8c8c8><TD>This %s group is empty.</TR></TD></TABLE>''' % viewType)
				self.writeln("</TD></TABLE>")

			elif viewType == '24h':
				for job in jobs:
					if job.isActive() and job.runsIn24h():
						outputCount += 1
						self.writeln(job.outputHTML())

				if outputCount == 0:
					self.writeln('''<TABLE width=100%% border=0 bgcolor=#c8c8c8><TR bgcolor=#c8c8c8><TD>This %s group is empty.</TR></TD></TABLE>''' % viewType)
				self.writeln("</TD></TABLE>")



		
		#self.writeln('''<form action="crontabMain?saveChanges=True" method="POST">
		#				<input type="submit" value="Save Changes">
		#				</form>''')








		

