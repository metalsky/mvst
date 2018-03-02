#!/user/bin/env python
import authedUsers, datetime
Su,M,T,W,Th,F,S = 0,1,2,3,4,5,6
months = { -1:'*', 1:'January', 2:'February',3:'March',4:'April',5:'May',6:'June',7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}
lastDay = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}

class cronJob:

	def __init__(self, minutes, hours, day, month, dowfilter, jobs, isactive, user='Invalid'):

		if user in authedUsers.buildUsers():
			self.buildUser = True
		else:
			self.buildUser = False
		self.isactive = isactive

		self.minutes = minutes
		if self.minutes != '*':
			self.minutes = int(self.minutes)

		self.hours = hours
		if self.hours != '*':
			self.hours = int(self.hours)

		self.month = month
		if self.month != '*':
			self.month = int(self.month)

		self.day = day
		if self.day != '*':
			self.day = int(self.day)

		self.jobs = jobs
		self.comments = []
		self.dowfilter = dowfilter

		self.days = [0,0,0,0,0,0,0]
		if dowfilter == '*':
			self.days = [1,1,1,1,1,1,1]
		else:
			dowfilter = dowfilter.split(',')
			for filter in dowfilter:
				if len(filter) == 1:
					self.days[ int(filter) ] = 1
				elif len(filter) == 3:
					for day in range( int(filter[0]) , int(filter[2]) + 1 ):
						self.days[day] = 1

	def isValid(self):
		if len(self.jobs) == 0:
			return False
		if 'echo Insert Text Here' in self.jobs:
			return False
	
		return True

	def runsIn24h(self):

		now = datetime.datetime.now()
		#If it runs every day, return true.
		if self.days == [1,1,1,1,1,1,1] and self.day == '*' and (self.month == '*' or self.month == -1):
			return True

		#If a month and day are defined..
		if (self.month != '*' and self.month != -1) and self.day != '*':
			#If its today, see if it already ran.
			if self.month == now.month and self.day == now.day:
				if self.hours < now.hour:
					return False
				elif self.hours == now.hour:
					if self.minutes < now.minute:
						return False
				#If not, its going to run today.
				return True

			#If its going to run tomorrow
			elif (self.month == now.month and self.day == now.day + 1) or \
					(self.month == now.month + 1 and self.day == 1 and now.day == lastDay[now.month]) or \
					(self.month == 1 and now.month == 12 and self.day == 1 and now.day == 31): 
				if self.hours < now.hour:
					return True
				elif self.hours == now.hour:
					if self.minutes < now.minutes:
						return True
				return False

		#Jobs of type Mon,Fri at 12:00
		elif (self.month == '*' or self.month == -1) and self.day == '*':
			todayDow = now.isoweekday()
			tomorrowDow = todayDow + 1
			if tomorrowDow == 7:
				tomorrowDow = 0

			#Check if it will run today.
			if self.days[todayDow]:
				if self.hours > now.hour:
					return True
				elif self.hours == now.hour and self.minutes > now.minute:
					return True

			if self.days[tomorrowDow]:
				if self.hours < now.hour:
					return True
				elif self.hours == now.hour and self.minutes < now.minute:
					return True

			return False
					
		return False

	def setID(self, id):
		self.ID = id

	def hasComment(self):
		return len(self.comments)

	def addComment(self,inString):
		self.comments.append(inString)
	
	def isActive(self):
		return self.isactive == 'Y'

	def __repr__(self):
		return 'Job'

	def outputCron(self):
		blank = ' '
		if self.month == -1:
			month = '*'
		else:
			month = self.month

		outStr = str(self.minutes) + blank + str(self.hours) + blank + str(self.day) + blank + str(month) + blank

		if self.days == [1,1,1,1,1,1,1]:
			outStr += '* '
		else:
			for i in range(len(self.days)):
				if self.days[i]:
					outStr += str(i) + ','

		if outStr[-1] == ',':
			outStr = outStr[0:-1] + ' '

		for job in self.jobs:
			outStr += job + ';'

		if outStr[-1] == ';':
			outStr = outStr[0:-1]

		if not self.isActive():
			outStr = '#' + outStr
			

		return outStr


	def outputHTML(self):  #{{{

		if self.month == '*':
			self.month = -1
		else:
			self.month = int(self.month)

		if self.hours == '*':
			timeOfDay = '--'
		else:
			self.hours = int(self.hours)

		if self.hours != '*' and self.hours > 12:
			hours = self.hours - 12
			timeOfDay = 'PM'
		else:
			hours = self.hours
			timeOfDay = 'AM'

		if self.minutes == '*':
			pass
		elif self.minutes < 10:
			self.minutes = '0' + str(self.minutes)


		outString = '''<TABLE BORDER=0 WIDTH=100% CELLSPACING=0 CELLPADDING=0>'''
		
		outString += '''<TR BGCOLOR=#c8c8c8><TD><u><br>Job %s</u></td><td></td></TR>''' % self.ID



		#Output Comments
		for comment in self.comments:
			outString += '''<TR BGCOLOR=#c8c8c8><TD><I>%s</I></TD><TD></TD></TR>''' % comment

		#Output Data and Edit Button

		outString += '''<TR bgcolor=#c8c8c8><TD>'''

		#Runs on all days of all months.  Time and date specified.
		#format: Mondays at 1:00 AM.
		if self.month == -1 and self.day == '*' and self.hours != '*' and self.minutes != '*':
			if self.days == [1,1,1,1,1,1,1]:
				outString += '''Every Day at %s:%s %s''' % (str(hours), self.minutes, timeOfDay)
			else:
				outString += '''%s at %s:%s %s''' % (self.prettyParseDays(self.days), str(hours), self.minutes, timeOfDay)

		#Runs on a specific date and time, regardless of day.
		#format: Jan 01 at 1:00 AM.
		elif self.dowfilter == '*' and self.month != -1 and self.hours != '*' and self.minutes != '*' and self.day != '*':
			outString += '''%s %s at %s:%s %s ''' % (months[self.month],self.day,hours,self.minutes,timeOfDay)

		else:
			outString += '''%s %s at %s:%s %s on days: %s''' \
					% (months[self.month],self.day,hours,self.minutes,timeOfDay, self.parseDays(self.days))


		if self.buildUser:
			outString += '''</TD><TD ALIGN=RIGHT><A HREF="cronEdit?jobIdToEdit=%s">Edit</A> | ''' % self.ID
			outString += '''<A HREF="cronDelete?jobIdToDelete=%s&deletionConfirmed=False">Delete</A></TR></TD>''' % self.ID
		else:
			outString += '''<TD></TD>'''

		#Output actual jobs
		outString += '''<TR bgcolor=#c8c8c8><TD><B>Jobs:</B></TD><TD></TD></TR>'''
		color = '#c8c8c8'
		for job in self.jobs:		
			outString += '''<TR bgcolor=%s><TD>%s</TD><TD></TD></TR> ''' % (color,job)


		outString += '''<TR bgcolor=%s><TD>&nbsp </TD><TD></TD></TR></TABLE>''' % color
		return outString 
	
	
	#}}}

	def parseDays(self,dayList): #{{{
		outString = ''
		if dayList[Su]:
			outString += 'Su '
		if dayList[M]:
			outString += 'M '
		if dayList[T]:
			outString += 'Tu '
		if dayList[W]:
			outString += 'W ' 
		if dayList[Th]:
			outString += 'Th '
		if dayList[F]:
			outString += 'F '
		if dayList[S]:
			outString += 'S '

		outString = outString[0:-1]
		return outString
	#}}}

	def prettyParseDays(self,dayList): #{{{
		outString = ''
		if dayList[Su]:
			outString += 'Sunday, '
		if dayList[M]:
			outString += 'Monday, '
		if dayList[T]:
			outString += 'Tuesday, '
		if dayList[W]:
			outString += 'Wednesday, ' 
		if dayList[Th]:
			outString += 'Thursday, '
		if dayList[F]:
			outString += 'Friday, '
		if dayList[S]:
			outString += 'Saturday, '

		outString = outString[0:-2]
		return outString
	#}}}


