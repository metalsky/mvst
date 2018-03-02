from SecurePage import SecurePage

class cronGroupMgr(SecurePage):

	def title(self):
		return "Manage Groups"

	def awake(self, trans):
		SecurePage.awake(self,trans)
		req = self.request()
		parser = self.session().value('currentParser')

		if req.hasField('groupToDelete'):
			if len ( parser.getJobs( req.field('groupToDelete' ) ) ) == 0 or (req.hasField('deletionConfirmed') and req.field('deletionConfirmed') == 'True'):
 				parser.deleteGroup( req.field('groupToDelete') )
			else:
				req.setField('deletionConfirmed', 'False')
		if req.hasField('groupToAdd'):
			parser.addGroup( req.field('groupToAdd') )


	def writeStyleSheet(self):
		from LTStyle import *
		stylesheet = sheet()
		self.writeln(stylesheet)

	def writeContent(self):
		req = self.request()
		ses = self.session()
		wr = self.writeln
		parser = ses.value('currentParser')

		if req.hasField('deletionConfirmed') and req.field('deletionConfirmed') == 'False':
			wr('''Deleting group %s will delete %s jobs.  Proceed?<br>''' % (req.field('groupToDelete'), len(parser.getJobs(req.field('groupToDelete')))))
			
			wr('''<A HREF="cronGroupMgr?deletionConfirmed=True&groupToDelete=%s">Yes</A>&nbsp&nbsp''' % req.field('groupToDelete'))
			wr('''<A HREF="cronGroupMgr>No</A>''')
			return



		wr('<table border=0 width=98% cellpadding=0 cellspacing=0>')
		bg = '#c8c8c8'
		for group in parser.getGroups():
			if bg == '#c8c8c8':
				bg = '#d8d8d8'
			else:
				bg = '#c8c8c8'
			wr('''<tr bgcolor=%s><td>%s</td><td align=right>
					<A HREF="cronGroupMgr?groupToDelete=%s">Delete</A>
					</td>''' % (bg, group, group))

		wr('<tr bgcolor=#e8e8e8><td><A HREF="cronGroupMgr?addGroup">New Group...</A></td><td> </td></tr>')
		if req.hasField('addGroup'):
			wr('<tr bgcolor=#e8e8e8><td><form><input type="text" name="groupToAdd"></td><td></td></tr>')

		wr('</table>')
