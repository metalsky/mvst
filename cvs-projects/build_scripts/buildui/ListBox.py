#!/usr/bin/python

class ListBox:

	def __init__(self,size='1',varName='overrideme', firstChoice=None):
		self.varName = varName
		self.size = str(size)
		self.firstChoice = firstChoice
		self.itemList = []

	def __str__(self):
		outStr = ""
		outStr += '<SELECT NAME="%s" SIZE="%s">' % (self.varName,self.size)


		if self.firstChoice:
			outStr += '<OPTION VALUE="%s">%s</OPTION>' % (self.firstChoice, self.firstChoice)

		for item in self.itemList:
			outStr += '<OPTION VALUE="%s">%s</OPTION>' % (item,item)
		outStr += '</SELECT>'

		return outStr
			
			

	def addItem(self,item):
		self.itemList.append(item)
