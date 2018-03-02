from SecurePage import SecurePage
from DEBUG import *
import cronJob, cronParser
DEBUG = isDebugMode()

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']


class cronEdit(SecurePage):
	
	def __init__(self):
		SecurePage.__init__(self)
	
	def title(self):
		return "Crontab Editor"

	def awake(self, transaction):
		SecurePage.awake(self, transaction)
		req = self.request()
		ses = self.session()

		if req.hasField('addNewJob'):
			parser = ses.value('currentParser')
			id = parser.getNewID()
			job = cronJob.cronJob('0', '12', '1', '1', '*', ["echo Insert Text Here"], 'Y')
			job.ID = id
			parser.addJobToGroup(job, "Ungrouped")
			self.sendRedirectAndEnd('cronEdit?jobIdToEdit=%s' % id)
		
		if req.hasField('jobEdited'):
			self.verifyEditedJob()

	def writeContent(self):
		ses = self.session()
		req = self.request()
		wr = self.writeln
		#wr("Session:<BR>")
		#wr(ses.values())
		#wr("<BR>request:<BR>")
		#wr(req.fields())
		#wr("<br><br>")



		parser = ses.value('currentParser')
		groups = parser.getGroups()
		jobIdToEdit = int(req.field('jobIdToEdit'))

		for group in groups:
			for job in parser.getJobs(group):
				if job.ID == jobIdToEdit:
					jobToEdit = job
					curGroup = group


		self.outputJobForm(jobToEdit, curGroup)


	def writeStyleSheet(self):
		from LTStyle import *
		stylesheet = sheet()
		self.writeln(stylesheet)

	def verifyEditedJob(self):
		req = self.request()
		ses = self.session()
		wr = self.writeln
		get = req.field

		comment = get('comment')

		dayToRun = get('dayToRun')
		if dayToRun == 'All':
			dayToRun = '*'
		
		monthToRun = get('monthToRun')
		if monthToRun == 'All':
			monthToRun = '*'
		else:
			monthToRun = months.index(monthToRun) + 1

		jobsGroup = get('jobsGroup')
		ID = get('editedJobID')
		isActive = get('jobIsActive')
		
		minuteToRun = get('minuteToRun')
		if minuteToRun == 'All':
			minuteToRun = '*'

		hourToRun = get('hourToRun')
		timeOfDay = get('timeOfDay')

		if hourToRun == 'All':
			hourToRun = '*'
		else:
			hourToRun = int(hourToRun)
			if timeOfDay == 'PM':
				hourToRun += 12

		hourToRun = str(hourToRun)

		dayfilter = ''
		daysToRun = get('daysToRun')

		if 'Sunday' in daysToRun:
			dayfilter += '0,'
		if 'Monday' in daysToRun:
			dayfilter += '1,'
		if 'Tuesday' in daysToRun:
			dayfilter += '2,'
		if 'Wednesday' in daysToRun:
			dayfilter += '3,'
		if 'Thursday' in daysToRun:
			dayfilter += '4,'
		if 'Friday' in daysToRun:
			dayfilter += '5,'
		if 'Saturday' in daysToRun:
			dayfilter += '6,'

		dayfilter = dayfilter[0:-1]


		jobs = get('jobs')

		if type(jobs) == str:
			jobs = [jobs]


		while '' in jobs:
			jobs.remove('')

		isActive = get('jobIsActive')

		jobID = get('editedJobID')

		jobComment = get('comment')

		jobToAdd = cronJob.cronJob(minuteToRun, hourToRun, dayToRun, monthToRun, dayfilter,  jobs, isActive, ses.value('authenticated_user'))
		jobToAdd.ID = int(jobID)

		if jobComment.lstrip() != '':
			jobToAdd.addComment(jobComment)

		ses.value('currentParser').removeJobByID(jobID)


		if jobToAdd.isValid():
			ses.value('currentParser').addJobToGroup(jobToAdd, get('jobsGroup'))

		self.sendRedirectAndEnd('crontabMain.py')
	
	
	
	def outputJobForm(self,job,groupFilter): #{{{
		allGroups = self.session().value('currentParser').getGroups()
		wr = self.writeln

		if self.request().hasField('additionalJobs'):
			additionalJobFilter = int(self.request().field('additionalJobs'))
		else:
			additionalJobFilter = 0



		checkBoxFilter = job.days
		for i in range(len(checkBoxFilter)):
			if checkBoxFilter[i] == 1:
				checkBoxFilter[i] = 'CHECKED'
			elif checkBoxFilter[i] == 0:
				checkBoxFilter[i] = ''

		if job.hasComment():
			commentFilter = job.comments[0]
		else:
			commentFilter = ""

		monthFilter = job.month
		if monthFilter != -1:
			monthFilter = months[monthFilter-1]

		dayFilter = job.day
		if dayFilter != '*':
			dayFilter = int(dayFilter)

		hourFilter = job.hours
		if hourFilter != '*':
			hourFilter = int(job.hours)

		if hourFilter > 12 and hourFilter != '*':
			timeOfDay = 'PM'
			hourFilter -= 12
		else:
			timeOfDay='AM'

		minuteFilter = job.minutes
		if minuteFilter != '*':
			minuteFilter = int(job.minutes)



		#Header
		outStr = '''<table border=0 WIDTH=100% CELLSPACING=0 CELLPADDING=2>'''
		outStr += '''<H1>Editing Job %s</H1>''' % job.ID
		
		
		outStr += '''<form>'''

		#Active?
		outStr += '''<tr bgcolor=#c8c8c8><td>Active:</td> '''
		outStr += '''<td><select name='jobIsActive'>'''
		if job.isActive():
			outStr += 	'''
					  	<option value="Y" SELECTED>Yes</option>
						<option value="N">No</option>'''
		else:
			outStr += 	'''
						<option value="Y">Yes</option>
						<option value="N" SELECTED>No</option>'''

		outStr += '''</select></tr></td>'''
						


		#Comment
		outStr += '''<tr bgcolor=#d8d8d8><td>Comment:</td> '''
		outStr += '''<td><input type="text" name="comment" size="150" value="%s"></td></tr>''' % commentFilter



		#Group
		outStr += '''<tr bgcolor=#c8c8c8><td>Group:</td>'''
		outStr += '''<td><select name="jobsGroup">'''
		for group in allGroups:
			if group == groupFilter:
				selString = 'SELECTED'
			else:
				selString = ''

			outStr += '''<option value="%s" %s>%s</option>''' % (group,selString,group)
		outStr += '''</select></td></tr>'''




		#Days of Week checkbox
		
		outStr += '''<tr bgcolor=#d8d8d8><td>Days To Run:</td>'''

		outStr += '''<td>
					Su<input type="checkbox" name="daysToRun" value="Sunday" %s>
					M <input type="checkbox" name="daysToRun" value="Monday" %s>
					Tu<input type="checkbox" name="daysToRun" value="Tuesday" %s>
		 			W <input type="checkbox" name="daysToRun" value="Wednesday" %s>
					Th<input type="checkbox" name="daysToRun" value="Thursday" %s>
					F <input type="checkbox" name="daysToRun" value="Friday" %s>
					Sa<input type="checkbox" name="daysToRun" value="Saturday" %s>
					</td></tr>

					''' % (checkBoxFilter[0],checkBoxFilter[1],checkBoxFilter[2],checkBoxFilter[3],checkBoxFilter[4], \
							checkBoxFilter[5],checkBoxFilter[6])


		#Month Dropdown
		outStr += '''<tr bgcolor=#c8c8c8><td>Date:</td>'''
		outStr += '''<td><select name="monthToRun">'''
		outStr += '''<option value="All">All</option>'''
		for month in months:
			if month == monthFilter:
				selString = 'SELECTED'
			else:
				selString = ''
			outStr += '''<option value="%s" %s>%s</option>''' % (month,selString,month)
		outStr += '''</select>'''

		#Day Dropdown
		outStr += '''<select name="dayToRun">'''
		outStr += '''<option value="All">All</option>'''

		for date in range(1,32):
			if date == dayFilter:
				selString = 'SELECTED'
			else:
				selString = ''
			outStr += '''<option value="%s" %s>%s</option>''' % (date,selString,date)
		outStr += '''</select></td></tr>'''

		#Hour Dropdown
		outStr += '''<tr bgcolor=#d8d8d8><td>Time:</td>'''
		outStr += '''<td><select name="hourToRun">'''
		outStr += '''<option value="All">All</option>'''

		for hour in range(1,13):
			if hour == hourFilter:
				selString = 'SELECTED'
			else:
				selString = ''
			outStr += '''<option value="%s" %s>%s</option>''' % (hour,selString,hour)
		outStr += '''</select>'''

		#Minute Dropdown
		outStr += '''<select name="minuteToRun">'''
		outStr += '''<option value="All">All</option>'''

		for minute in range(0,60):
			if minute == minuteFilter:
				selString = 'SELECTED'
			else:
				selString = ''
			if minute < 10:
				minute = '0' + str(minute)
			outStr += '''<option value="%s" %s>%s</option>''' % (minute,selString,minute)
		outStr += '''</select>'''

		#AM/PM Dropdown
		outStr += '''<select name="timeOfDay">'''
		
		for time in ['AM', 'PM']:
			if time == timeOfDay:
				selString = 'SELECTED'
			else:
				selString = ''
			outStr += '''<option value="%s" %s>%s</option>''' % (time,selString,time)

		outStr += '''</tr></td>'''


		#Job Fields
		outStr += '''<tr bgcolor=#c8c8c8><td>Jobs (<A HREF="cronEdit?jobIdToEdit=%s&additionalJobs=%s">new</a>):</td>''' % (job.ID, additionalJobFilter+1)
		firstDone = False
		for jobString in job.jobs:
			if firstDone:
				outStr += '''<td></td>'''
			else:
				firstDone = True
						
			outStr += '''<td><input type="text" name="jobs" size="150" value="%s"></td></tr>''' % jobString.lstrip()

		for i in range(additionalJobFilter):
			outStr += '''<tr bgcolor=#c8c8c8><td></td><td><input type="text" name="jobs" size="150"></td></tr> '''




		outStr += '''</table>'''
		outStr += '''<input type="hidden" name="jobEdited" value="True">'''
		outStr += '''<input type="hidden" name="editedJobID" value="%s"''' % job.ID
		outStr += '''<br>'''
		outStr += '''<input type="submit" value="Submit">'''
		outStr += '''</form>'''

		wr(outStr)

		
		#}}}
