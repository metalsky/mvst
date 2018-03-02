from SecurePage import SecurePage
from DEBUG import *
import server, ListBox
DEBUG = isDebugMode()

class addArch(SecurePage):
	

	def awake(self,trans):
		SecurePage.awake(self,trans)
		req = self.request()
		ses = self.session()
		self.db = server.server()
		self.db.Connect()

		if req.hasField('archToAdd') and req.field('archToAdd') != 'Choose an Arch:' and req.field('archReleased') != 'Select:':
			valid = self.validate(req.field('archToAdd'),req.field('archReleased'))
			if valid:
				duplicate = len(self.db.Command("SELECT id FROM BuildCfg.archs WHERE name='%s' AND products_id=%s" % (req.field('archToAdd'), ses.value('productID'))))
				if not duplicate:
					self.db.Command("INSERT INTO BuildCfg.archs (name,released,products_id) VALUES ('%s','%s',%s)" % (req.field('archToAdd'), req.field('archReleased')[0], ses.value('productID')))
					req.setField('archAddSuccess',1)
				else:
					req.setField('archAddSuccess',0)
			else:
				req.setField('archAddSuccess',0)

	def sleep(self,trans):
		SecurePage.sleep(self,trans)
		try:
			self.db.Close()
			del self.db
		except AttributeError:
			pass

	def title(self):
		return "Add Architecture"

	def writeContent(self):
		wr = self.writeln
		ses = self.session()
		req = self.request()

		if req.hasField('newLogin'):
			self.sendRedirectAndEnd('Main')
			return


		if req.hasField('archAddSuccess'):
			if req.field('archAddSuccess'):
				wr('Architecture Added Successfully.')
				wr('<BR><A HREF=QueryDB>Back</A>')
				return
			else:
				wr('''Architecture Addition Failed.  One of three things happened:<br>
						-You attempted to add an architecture that does not exist in this product's foundation.<br>
						-You tried to add a released architecture for which the foundation is not released.<br>
						-You attempted to add a duplicate architecture.<br><br>
						
						There is a small chance that I screwed something up.  Contact me
						if you think this page is in error.  rell@mvista.com<br>
						
						<BR><A HREF=addArch>Back</A>''')
				return

		archBox = ListBox.ListBox(1,'archToAdd', 'Choose an Arch:')
		releasedBox = ListBox.ListBox(1,'archReleased', 'Select:')
		knownArchs = map(lambda x: str(x['name']), self.db.Command("SELECT name FROM BuildCfg.archs GROUP BY name"))
		

		for choice in ["Yes", "No"]:
			releasedBox.addItem(choice)
	
		for arch in knownArchs:
			archBox.addItem(arch)


		wr('<H2 ALIGN=CENTER>Adding to %s %s (%s) <BR></H2>' % (ses.value('edition') , ses.value('version') , ses.value('tag')))	
		wr('<TABLE BORDER=0 WIDTH=100% CELLSPACING=0>')

		wr('<FORM METHOD=POST>')
		wr('<TR bgcolor=#c8c8c8><TD>')
		wr('Architecture to Add....</TD>')
		wr('<TD ALIGN=RIGHT>')
		wr(archBox)
		wr('</TD></TR>')
		wr('<TR bgcolor=#d8d8d8>')
		wr('<TD>Is this architecture released?</TD>')
		wr('<TD ALIGN=RIGHT>')
		wr(releasedBox)
		wr('</TD>')
		wr('</TR>')
		wr('<TR><TD><INPUT NAME="inputButton" TYPE="Submit" VALUE="Submit"</TR></TD>')
		wr('</FORM>')

		wr('</TABLE>')



		if DEBUG: #{{{
			wr("<H2>Session Variables</H2>")
			for key in ses.values():
				wr('%s : %s<BR>' % (key, ses.value(key)))
			wr("<H2>Request Variables</H2>")
			for key in req.fields():
				wr('%s : %s<BR>' % (key, req.field(key))) #}}}




	def validate(self,arch,isReleased):
		ses = self.session()
		productID = ses.value('productID')
		foundationID = map(lambda x: int(x['foundation']) ,self.db.Command('SELECT foundation FROM BuildCfg.products WHERE id=%s' % productID))
		foundationID = foundationID[0]
	
		#If we are a foundation, then it's ok to add.
		if foundationID == 0:
			return 1
		else: #Otherwise, make sure the arch is in the foundation.
			results = self.db.Command("SELECT * FROM BuildCfg.archs WHERE name='%s' AND products_id=%s" % (arch,foundationID))
			if len(results) > 0:
				results = results[0]
				self.writeln(results)
			else:
				return 0

		if results['released'] == 'Y' and isReleased[0] == 'N': #Foundation released, this isn't.  Ok!
			return 1
		elif results['released'] != isReleased[0]:              #Foundation not released, this is.  Bad!
			return 0
		else:										            #Otherwise, they match.  Ok!
			return 1 
