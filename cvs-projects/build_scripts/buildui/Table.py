#! /usr/bin/python

class Table:
	def __init__(self, width="100%", border="1"):
		self.Width = width;
		self.RowList = []

	def addRow(self,DataList):
		self.RowList.append(DataList)


	
