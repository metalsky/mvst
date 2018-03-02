import ListBox
import server
from SecurePage import SecurePage
from DEBUG import *
DEBUG = isDebugMode()

class changeArch(SecurePage): #{{{

	def awake(self, trans):
		SecurePage.awake(self,trans)
		self.releaseDB = server.server()
		self.releaseDB.Connect()

	def sleep(self,trans):
		self.releaseDB.Close()
		del self.releaseDB

	def title(self):
		return 'Build Database Interaction'

	def checkFoundation(self, productID, archName):
		'''Return 0 if the foundation is released.
		   Else, return the architecture ID corresponding to the foundation that needs to be released.
		'''
		foundationID = self.releaseDB.Command("SELECT foundation FROM BuildCfg.products WHERE id=%s" % productID)
		foundationID = int(foundationID[0]['foundation'])

		results = self.releaseDB.Command("SELECT id,released FROM BuildCfg.archs WHERE name='%s' AND products_id=%s" % (archName, foundationID))
		isReleased = results[0]['released']
		foundationArchID = results[0]['id']

		if isReleased == 'Y':
			return 0
		elif isReleased == 'N':
			return foundationArchID
		

	def writeContent(self):
		ses = self.session()
		req = self.request()
		wr = self.writeln
		adapterName = self.request().adapterName()

		if DEBUG:
			wr(ses.values())
			wr('<BR>')
			wr(req.fields())

		archID = req.field('archID')
		productID = req.field('productID')
		edition = req.field('edition')

		archName = self.releaseDB.Command("SELECT name FROM BuildCfg.archs WHERE id='%s'" % archID) 
		isReleased = self.releaseDB.Command("SELECT released FROM BuildCfg.archs WHERE id='%s'" % archID)
		archName = archName[0]['name']
		isReleased = isReleased[0]['released']

		buildList = self.releaseDB.Command("SELECT buildtag FROM Builds.builds WHERE products_id=%s" % ses.value('productID'))
		buildList = map(lambda x: str(x['buildtag']), buildList)

		
		archBox = ListBox.ListBox(1,'originBuild', 'Select:')
		for build in buildList:
			archBox.addItem(build)

		isFoundation = 'foundation' in edition

		#The foundation check failed -- redirect user.
		if not isFoundation:
			foundationArchID = self.checkFoundation(productID, archName)
			if foundationArchID:
				#need -- productID of foundation, 
				result = self.releaseDB.Command("SELECT foundation FROM BuildCfg.products where id=%s" % productID)
				foundationID = result[0]['foundation']
				result = self.releaseDB.Command("SELECT tag_match,version FROM BuildCfg.products WHERE id=%s" % foundationID)
				foundationTag = result[0]['tag_match']
				foundationVersion = result[0]['version']
				 		
				wr('This architecture is not released in this edition''s foundation.  Would you like to \
					<A HREF=QueryDB?archToChRelease=%s&productID=%s&edition=foundation&tag=%s&version=%s>Release it?</A>' % (foundationArchID,foundationID,foundationTag,foundationVersion))
				return
					
			

		if isReleased == 'Y' and isFoundation:
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='N' WHERE id='%s'" % archID)
			self.sendRedirectAndEnd('QueryDB')
		elif isReleased == 'Y':
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='N' WHERE id='%s'" % archID)
			self.sendRedirectAndEnd('QueryDB')
		elif req.hasField('originBuild') and req.field('originBuild') != 'Select:':
			obuildID = req.field('originBuild')[-6:]
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='Y',released_build_id='%s' WHERE id='%s'" % (obuildID,archID))
			self.sendRedirectAndEnd('QueryDB')	

		wr('<H2 ALIGN=CENTER>Releasing %s in %s %s (%s) <BR></H2>' % (archName, ses.value('edition') , ses.value('version') , ses.value('tag')))	
		wr('<TABLE BORDER=0 WIDTH=100% CELLSPACING=0>')
		wr('<FORM METHOD=POST>')
		wr('<TR bgcolor=#c8c8c8><TD>')
		wr('Build to release this arch from....</TD>')
		wr('<TD ALIGN=RIGHT>')
		wr(archBox)
		wr('</TD></TR>')
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

#}}}

	def DEPRECATEDchangeArchRelease(self, archID, productID, edition): #{{{
		'''Gotta hack this up a bit for the new table.

		'''
	

		#We are a foundation, so just change it.
		if isReleased == 'Y' and isFoundation:
			pass
		elif isReleased == 'N' and isFoundation:
			pass

		elif isReleased == 'Y':
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='N' WHERE id='%s'" % archID)
		#If we aren't a foundation and we are releasing an arch, we better update our foundation too!
		elif isReleased == 'N':
			myFoundationID = self.releaseDB.Command("SELECT foundation FROM BuildCfg.products WHERE id='%s'" % str(productID))
			myFoundationID = myFoundationID[0]['foundation']
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='Y' WHERE id='%s'" % archID)
			self.releaseDB.Command("UPDATE BuildCfg.archs SET released='Y' WHERE name='%s' AND product_id='%s'" % (archName,myFoundationID))
	#}}}
	
#end Main
