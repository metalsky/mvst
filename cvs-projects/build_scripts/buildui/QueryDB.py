from SecurePage import SecurePage
from DEBUG import *
import server
import bwLog
DEBUG = isDebugMode()

class QueryDB(SecurePage):

	def __init__(self):
		SecurePage.__init__(self)
		self.productEdition = self.productVersion = self.productTag = None

	def title(self): 
		''' Returns the title of the page, to go in our fancy header.'''
		ses = self.session()
		self.testDB()
		req = self.request()
		if not self.productEdition or not self.productVersion or not self.productTag:
			return ''
		return '%s %s (%s)' % (self.productEdition, self.productVersion, self.productTag)

	
	def changeArchRelease(self, archID, productID, edition): #{{{
		self.sendRedirectAndEnd('changeArch?archID=%s&productID=%s&edition=%s' % (archID, productID, edition))
	#}}}



	def awake(self, transaction):
		''' We have to do a lot here.  
				0.  Do initial stuff.  Set variables, and open a connection to the SQL database.
				1. 	Set up the session variables to expand or contract
					the menus the user has selected.
				2.	Set class variables if the user has selected something from the menu.
					Else, grab them from the session.  This should probably be changed,
					but it works ok for right now.
				3.	Check if the user has deleted or released/unreleased an arch.  If so
					run the appropriate architecture function.
		'''

		self.bwlog = bwLog.bwLog()
		
		self.testDB()
		self.releaseDB = server.server()
		self.releaseDB.Connect()
		wr = self.writeln
		SecurePage.awake(self, transaction)
		ses = self.session()
		req = self.request()
		resp = self.response()
		
		if req.hasField('archExpand') and ses.hasValue('archExpand') and ses.value('archExpand'):
			ses.setValue('archExpand',0)
		elif req.hasField('archExpand'):
			ses.setValue('archExpand',1)	
		elif req.hasField('buildExpand') and ses.hasValue('buildExpand') and ses.value('buildExpand'): 
			ses.setValue('buildExpand',0)
		elif req.hasField('buildExpand'):
			ses.setValue('buildExpand',1)	
		elif req.hasField('hostExpand') and ses.hasValue('hostExpand') and ses.value('hostExpand'): 
			ses.setValue('hostExpand',0)	
		elif req.hasField('hostExpand'):
			ses.setValue('hostExpand',1)
		elif req.hasField('excludeExpand') and ses.hasValue('excludeExpand') and ses.value('excludeExpand'):
			ses.setValue('excludeExpand',0)
		elif req.hasField('excludeExpand'):
			ses.setValue('excludeExpand',1)

		if req.hasField('tag'):
			self.productTag     = req.field('tag')
			self.productEdition = req.field('edition')
			self.productVersion = req.field('version')
		elif ses.hasValue('tag'):
			self.productTag 	= ses.value('tag')
			self.productEdition	= ses.value('edition')
			self.productVersion = ses.value('version')
		else:
			return
		
		if DEBUG: #{{{
			wr('session')
			wr(ses.values())
			wr('<BR>')
			wr('request')
			wr(req.fields())
			wr('<BR>')
			wr('response')
			wr(SecurePage.actions(self))
			wr('<BR>') #}}}

		productID = self.getproductID(self.productTag,self.productEdition,self.productVersion)
		ses.setValue('productID',productID)

		if req.hasField('archToDelete'):
			self.deleteArch(req.field('archToDelete'))
		elif req.hasField('archToChRelease'):
			self.changeArchRelease(req.field('archToChRelease'), productID, self.productEdition)

	#}
	
	def deleteArch(self,archID):
		'''	Given the id of an architecture, delete it.
			If the architecture being deleted is in a foundation, propogate downward
			and remove it from all editions built from that foundation.
		'''
		req = self.request()
		ses = self.session()
		myID = self.session().value('productID')
		myFoundationID = self.releaseDB.Command('SELECT foundation FROM BuildCfg.products WHERE id=%s' % myID)[0]['foundation']
		archName = self.releaseDB.Command('SELECT name FROM BuildCfg.archs WHERE id=%s' % archID)[0]['name']
		
		if myFoundationID == 0:
			self.writeln('Need to implement this.  Why are you deleting from a foundation?  Contact rell@mvista') #FIXME: Propogate downwards here!
		else:
			self.writeln("User %s deleted arch %s from product ID %s" % (ses.value('authenticated_user'),archName,myID))
			self.bwlog.info("User %s deleted arch %s from product ID %s" % (ses.value('authenticated_user'),archName,myID))
			self.releaseDB.Command('DELETE FROM BuildCfg.archs WHERE id=%s' % (req.field('archToDelete')))

	def sleep(self,trans): 
		'''	Clean up.  Close the connection to the DB and delete the class variables.
			Note the AttributeError occurs when a user is logging in fresh to a page that 
			never went to sleep. Also, we don't delete the product information since they
			may be in use by another user.
		'''
		SecurePage.sleep(self,trans)
		try:
			self.releaseDB.Close()
			del self.releaseDB
			del self.log
		except AttributeError:
			pass

	def getproductID(self, tag,edition,version): 
		''' Given a tag, edition, and version of a product, return its mapping in the product_map table.'''

		result = self.releaseDB.Command("SELECT id FROM BuildCfg.products WHERE tag_match='%s' AND edition='%s' AND version='%s'" \
								% (tag,edition,version))

		return str(result[0]['id'])


	def getArchs(self, productID): 
		result = self.releaseDB.Command("SELECT name,released,id,released_build_id FROM BuildCfg.archs WHERE products_id=%s ORDER BY name" % productID)
		return map(lambda x: [str(x['name']) , str(x['released']) , str(x['id']) , str(x['released_build_id'])  ] , result)

	def getBuilds(self, productID):

		result = self.releaseDB.Command("SELECT buildtag FROM Builds.builds WHERE products_id=%s ORDER BY buildtag DESC" % productID)
		return map(lambda x: str(x['buildtag']) , result)
	
	def getHosts(self,productID): 
		result = self.releaseDB.Command("SELECT name FROM BuildCfg.hosts WHERE products_id=%s GROUP BY name" % productID)
		return map(lambda x: str(x['name']), result)

	def getExcludes(self,productID): 
		result = self.releaseDB.Command("SELECT name,archs_id,hosts_id FROM BuildCfg.foundationExcludes WHERE products_id=%s ORDER BY name" % productID)
		return map(lambda x: ( str(x['name']) , str(x['archs_id']) , str(x['hosts_id']) ) , result)

	def getExempts(self):
		result = self.releaseDB.Command("SELECT name FROM BuildCfg.deletion_exempt")
		return map(lambda x: str(x['name']) , result)

	def outputArchHTML(self, archs): 
		wr = self.writeln

		wr('<TABLE BORDER="0" CELLSPACING=0 WIDTH=100%>')
		wr('<TR bgcolor=#c8c8c8>')
		wr('<TH ALIGN=LEFT>&nbsp&nbsp ID</TH>')
		wr('<TH ALIGN=LEFT>Name</TH>')
		wr('<TH ALIGN=LEFT WIDTH=15%>Released?</TH>')
		wr('<TH ALIGN=RIGHT WIDTH=30%>Update</TH>')
		wr('</TR>')
		wr('<FONT SIZE=2>')

		color = 0
		for arch in archs:
			if color: 
				color = 0
				wr('<TR bgcolor=#c8c8c8>')
			else:
				color = 1
				wr('<TR bgcolor=#d8d8d8>')
			if arch[0] not in  ['SRC', 'noarch', 'ALL', 'UCLIBC']:

				wr('''<TD><FONT SIZE=2>
					  <A HREF=QueryDB?archToDelete=%s TITLE="Delete this architecture."> 
 					  <IMG SRC=/Images/delete_16.gif BORDER=0 WIDTH=12 HEIGHT=12></a>
					  %s</TD>
				''' % (arch[2], arch[2]))

				wr('''<TD><FONT SIZE=2> 
							 %s </TD>	   ''' % \
									(arch[0]))

				if arch[1] == 'Y':
					if int(arch[3]) == 0:
						arch[3] = ''
					else:
						arch[3] = '(' + str(arch[3]) + ')'
					wr('<TD ALIGN=LEFT WIDTH=3><FONT SIZE=2><IMG SRC=/Images/yes.gif></IMG><I>&nbsp%s</I><TD ALIGN=RIGHT>' % arch[3])
					wr('<FONT SIZE=2><A HREF=QueryDB?archToChRelease=%s>Unrelease</TD>' % \
									(arch[2]))
				elif arch[1] == 'N':
					wr('<TD ALIGN=LEFT WIDTH=3><FONT SIZE=2><IMG SRC=/Images/no.gif></IMG><TD ALIGN=RIGHT>')
					wr('<FONT SIZE=2><A HREF=QueryDB?archToChRelease=%s>Release</a></TD>' % \
									(arch[2]))
			else:
				color = not color

			wr('</TR>')
		wr('</FONT>')
		wr('</TABLE>')

	def outputBuildHTML(self, builds):
		myExempts = self.getExempts()
		wr = self.writeln
		wr('<TABLE BORDER="0" WIDTH="100%" VALIGN=TOP CELLSPACING=0>')

		color=0
		for build in builds:
			if color:
				color = 0
				wr('<TR bgcolor=#c8c8c8>')
			else:
				color = 1
				wr('<TR bgcolor=#d8d8d8>')
			wr('<TD><FONT SIZE=2>')
			if build in myExempts:	
				wr('''<A HREF=viewBuildInfo?selectedBuild=%s TITLE="Detailed Build Information">
				  <FONT COLOR=GREEN><IMG SRC=/Images/search_16_h.gif BORDER=0 WIDTH=13 HEIGHT=13></a> %s</FONT>''' % \
									(build, build) )

			else:
				wr('''<A HREF=viewBuildInfo?selectedBuild=%s TITLE="Detailed Build Information">
				  <IMG SRC=/Images/search_16_h.gif BORDER=0 WIDTH=13 HEIGHT=13></a> %s''' % \
									(build, build) )
			wr('</TR>')
			wr('</TD>')

		wr('</TABLE>')

	def outputHostHTML(self, hosts): 
		wr = self.writeln
		wr('<TABLE BORDER="0" WIDTH="100%" VALIGN=TOP CELLSPACING=0>')
		hosts = filter(lambda x: x not in ['SRC', 'ALL', 'noarch'],hosts) 
		color=0

		for host in hosts:
			if color:
				color = 0
				wr('<TR bgcolor=#c8c8c8>')
			else:
				color = 1
				wr('<TR bgcolor=#d8d8d8>')
			wr('<TD><FONT SIZE=2>')
			wr(host)
			wr('</TR>')
			wr('</TD>')

		wr('</TABLE>')

	def outputExcludeHTML(self,excludes): 
		wr = self.writeln
		NAME,ARCHID,HOSTID = 0,1,2
		color=0
		
		wr('<TABLE BORDER="0" CELLSPACING=0 WIDTH=100%>')
		wr('<TR bgcolor=#c8c8c8>')
		wr('<TH ALIGN=LEFT>Name</TH>')
		wr('<TH ALIGN=LEFT>Arch</TH>')
		wr('<TH ALIGN=RIGHT>Host</TH>')
		wr('</TR>')
		wr('<FONT SIZE=2>')
	
		for exclude in excludes:
			if color:
				color = 0
				wr('<TR bgcolor=#c8c8c8>')
			else:
				color = 1
				wr('<TR bgcolor=#d8d8d8>')
			wr('<TD><FONT SIZE =2>')
			archName = int(exclude[ARCHID]) and \
				map(lambda x: str(x['name']) , self.releaseDB.Command("SELECT name FROM BuildCfg.archs WHERE id='%s'" % exclude[ARCHID]))[0]
			hostName = int(exclude[HOSTID]) and \
				map(lambda x: str(x['name']) , self.releaseDB.Command("SELECT name FROM BuildCfg.hosts WHERE id='%s'" % exclude[HOSTID]))[0]
			self.writeln('''
				
				    %s</td>
				<td><FONT SIZE=2>%s</td>
				<td ALIGN=RIGHT><FONT SIZE=2>%s</td>
				</tr>''' % (exclude[NAME], archName or 'Undefined', hostName or 'Undefined'))

	def icon(self,icon): 
		if icon:
			return 'block-arrow-expanded.gif'
		else:
			return 'block-arrow-collapsed.gif'
	
	def writeContent(self): 
		wr = self.writeln
		adapterName = self.request().adapterName()
		ses = self.session()
		req = self.request()
		userID = ses.value('authenticated_user_id')

		if req.hasField('newLogin') or not ses.hasValue('productID'):
			self.sendRedirectAndEnd('Main')
			return

		productID = ses.value('productID')

		#try: 
		#	productID = ses.value('productID')
		#except:
		#	self.sendRedirectAndEnd('Main')			
			
		myArchs = self.getArchs(productID)
		myBuilds = self.getBuilds(productID)
		myHosts = self.getHosts(productID)
		myExcludes = self.getExcludes(productID)

		expandArchs = ses.hasValue('archExpand') and ses.value('archExpand')
		expandBuilds = ses.hasValue('buildExpand') and ses.value('buildExpand')
		expandHosts = ses.hasValue('hostExpand') and ses.value('hostExpand')
		expandExcludes = ses.hasValue('excludeExpand') and ses.value('excludeExpand')

		#{{{Archs
		wr('<TABLE BORDER="0" WIDTH="100%" CELLSPACING="0">')
		wr('<TR VALIGN=TOP>')
		wr('<TR BGCOLOR=#7e7e7e ALIGN=LEFT>')
		wr('<TD>')

		wr('<TABLE BORDER="0" WIDTH="100%" CELLSPACING="0">')
		wr('<TD>')
		wr('<A HREF=QueryDB?archExpand=1 STYLE="text-decoration: none"> ')	 
		wr('<IMG SRC=/Images/%s BORDER=0></A></IMG>' % self.icon(expandArchs))
		wr('<FONT COLOR=WHITE><b>Archs</b></TD>')

		wr('<TD ALIGN=RIGHT>')
		wr('<A HREF=/addArch TITLE="Add Architecture">')
		wr('<IMG SRC=/Images/new.gif BORDER=0></TD></IMG></A>')

		wr('</TABLE></TD></TR></FONT>')

		if len(myArchs + filter(lambda x: x not in myArchs, ['SRC','ALL','noarch','UCLIBC'])) > 4 and expandArchs:
			wr("<TD VALIGN=TOP BGCOLOR=#d8d8d8>")
			self.outputArchHTML(myArchs)
			wr('</TD></TABLE>')
		else:
			wr('</TABLE>')
		#}}}

		#{{{Builds
		wr('<TABLE BORDER="0" WIDTH="100%" CELLSPACING="0">')
		wr('<TR VALIGN=TOP>')
		wr('<TR BGCOLOR=#7e7e7e ALIGN=LEFT>')
		wr('<TH>')
		wr('<A HREF=QueryDB?buildExpand=1 STYLE="text-decoration: none"> ')
		wr('<IMG SRC=/Images/%s BORDER=0></A></IMG>' % self.icon(expandBuilds))
		wr('<FONT COLOR=WHITE><b>Builds</b></TD></TR></FONT></TH>')
		wr('</TR>')
		if len(myBuilds) > 0 and expandBuilds:
			wr("<TD VALIGN=TOP bgcolor=#d8d8d8>")
			self.outputBuildHTML(myBuilds)
			wr("</TD></TABLE>")
		else:
			wr('</TABLE>')
		#}}}

		#{{{Hosts
		wr('<TABLE BORDER="0" WIDTH="100%" CELLSPACING="0">')
		wr('<TR VALIGN=TOP>')
		wr('<TR BGCOLOR=#7e7e7e ALIGN=LEFT>')
		wr('<TH>')
		wr('<A HREF=QueryDB?hostExpand=1 STYLE="text-decoration: none">')
		wr('<IMG SRC=/Images/%s BORDER=0></A></IMG>' % self.icon(expandHosts))
		wr('<FONT COLOR=WHITE><B>Hosts</B></TR></FONT></TH>')
		wr('</TR>')
		if len(myHosts) > 0 and expandHosts:
			wr("<TD VALIGN=TOP bgcolor=#d8d8d8>")
			self.outputHostHTML(myHosts)
			wr("</TD></TABLE>")
		else:
			#wr('<TD></TD>')
			wr('</TABLE>')
		#}}}

		#{{{Excludes
		wr('<TABLE BORDER="0" WIDTH="100%" CELLSPACING="0">')
		wr('<TR VALIGN=TOP>')
		wr('<TR BGCOLOR=#7e7e7e ALIGN=LEFT>')
		wr('<TH>')
		wr('<A HREF=QueryDB?excludeExpand=1 STYLE="text-decoration: none">')
		wr('<IMG SRC=/Images/%s BORDER=0></A></IMG>' % self.icon(expandExcludes))
		wr('<FONT COLOR=WHITE><B>Excludes</B></TR></FONT></TH>')
		wr('</TR>')
		if len(myExcludes) > 0 and expandExcludes:
			wr("<TD VALIGN=TOP bgcolor=#d8d8d8>")
			self.outputExcludeHTML(myExcludes)
			wr("</TD></TABLE>")
		else:
			wr('</TABLE>')
		#}}}

		wr("</div>")
		wr('</form>')

	def writeStyleSheet(self):
		from LTStyle import sheet	
		stylesheet = sheet()
		self.writeln(stylesheet)
