from SecurePage import SecurePage
import server

class viewBuildInfo(SecurePage):

	def __init__(self):
		SecurePage.__init__(self)
		self.productTag = self.productEdition = self.productVersion = None

	def title(self):
		return self.request().field('selectedBuild')
	#}

	def awake(self,trans):
		SecurePage.awake(self,trans)
		req = self.request()
		ses = self.session()

		if req.hasField('tag'):
			self.productTag     = req.field('tag')
			self.productEdition = req.field('edition')
			self.productVersion = req.field('version')
		elif ses.hasValue('tag'):
			self.productTag 	= ses.value('tag')
			self.productEdition	= ses.value('edition')
			self.productVersion = ses.value('version')
			req.setField('tag', self.productTag)
			req.setField('edition', self.productEdition)
			req.setField('version',self.productVersion)
	#}


	def htBodyArgs(self):
		return '''onload="fScrollMove('10000');"'''
	#}

	#Set up javascript, all IE compatible and everything.  This actually runs slower on firefox, not sure why.
	#The following 17 lines of code represent a horrible portion of my life that I can never reclaim.
	def writeStyleSheet(self):
		if self.request().hasField('scrollpos'):
			scrollPosition = self.request().field('scrollpos')
		else:
			scrollPosition = 0
		
		from LTStyle import sheet	
		stylesheet = sheet()
		self.writeln(stylesheet)

		self.writeln('''
					<script language="javascript">

					function fScrollSave(url) {
						url += '&scrollpos=' + document.documentElement.scrollTop;
						window.location.href=url;
					}

					function fScrollMove(what) {
						window.scrollTo(0,%s);
					}

					</script>

					''' % scrollPosition)
	#}


	def writeContent(self):
		wr = self.writeln
		ses = self.session()
		req = self.request()

		#wr(ses.values())
		#wr(req.fields())
		#wr("<BR>")

		releaseDB = server.server()
		releaseDB.Connect()

		buildID = releaseDB.Command( "SELECT id FROM Builds.builds WHERE buildtag='%s'" % req.field('selectedBuild') )
		buildID = map(lambda x: str(x['id']) , buildID)
		
		if len(buildID) > 1:
			wr("Multiple Build IDS -- contact rell@mvista.com.")
		
		buildID = buildID[0]
	
		expandRPM =  req.hasField('selectedPackage')

		cross_packages = releaseDB.Command("SELECT id,name FROM Builds.crossPkgs WHERE builds_id='%s' ORDER BY name" % buildID)
		host_packages = releaseDB.Command("SELECT id,name FROM Builds.hostPkgs WHERE builds_id='%s' ORDER BY name" % buildID)
		target_packages = releaseDB.Command("SELECT id,name FROM Builds.targetPkgs WHERE builds_id='%s' ORDER BY name" % buildID)


		if expandRPM:
			RPMs     = releaseDB.Command("SELECT name FROM rpm WHERE package_id='%s' ORDER BY name" % req.field('selectedPackage')) 
			RPMs     = map(lambda x: str(x['name']) , RPMs)

		
		packagesDict = {}

		#Sort the packages into a dictionary by type.	
		for package in packages:
			try:
				packagesDict[package['type']].append((package['id'], package['name']))
			except KeyError:
				packagesDict[package['type']] = []
				packagesDict[package['type']].append((package['id'], package['name']))



		wr('<TABLE BORDER=0 CELLSPACING=0 WIDTH=100%>')

		color='#d8d8d8'
		keys = packagesDict.keys()
		keys.sort()
		for key in keys:
			wr("<TR bgcolor=#7e7e7e ALIGN=CENTER><TD><FONT SIZE=4>%s</TD></TR>" % (key))

			for package in packagesDict[key]:
				if color == '#d8d8d8':
					color = '#c8c8c8'
				else:
					color = '#d8d8d8'

				if expandRPM and package[0] == int(req.field('selectedPackage')):
					#These are the ouputted links, the + and - links expand and contract
					#the list of files under each package.  The javascript is here to maintain
					#the users position when they click the links, so the page doesnt jump back up
					#to the top.  If theres a way to do this in webkit, someone please tell me, because
					#the javascript is a horrible, horrible hack.
					wr('''<TR bgcolor=%s><TD><FONT SIZE=2>
						  <A HREF="javascript:fScrollSave('viewBuildInfo?selectedBuild=%s&expandPackages=True')" 
							STYLE="text-decoration: none">
							<IMG SRC=/Images/minus.gif BORDER=0></a></IMG>''' % (color, req.field('selectedBuild')))
					wr(package[1])
					wr("<BR>")
					for RPM in RPMs:
						wr("&nbsp&nbsp&nbsp<IMG SRC=/Images/join.gif BORDER=0></IMG>  <I> %s </I>" % RPM)
						wr("<BR>")
					
					wr("</TD></TR>")

				else:
					wr('''<TR bgcolor=%s><TD><FONT SIZE=2>
						  <A HREF="javascript:fScrollSave('viewBuildInfo?selectedBuild=%s&expandPackages=True&selectedPackage=%s')" 
						  STYLE="text-decoration: none">
						  <IMG SRC=/Images/plus.gif BORDER=0></IMG></a>''' %  (color, req.field('selectedBuild') , str(package[0])))
					wr(package[1])
					wr("</TD></TR>")

		wr('</TABLE>')
		wr('</form>')
		releaseDB.Close()
	#}


#}


