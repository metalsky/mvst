#!/usr/bin/python

def outputArchHTML(archs):
	wr = self.writeln

	wr('<TABLE BORDER="0" CELLSPACING=0 WIDTH="100%">')
	wr('<TR bgcolor=#c8c8c8>')
	wr('<TH ALIGN=LEFT>Name</TH>')
	wr('<TH>Released?</TH>')
	wr('<TH ALIGN=RIGHT>Update</TH>')
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
		if arch[0] not in  ['SRC', 'noarch', 'ALL']:
			wr('''<TD><FONT SIZE=2> 
				<A HREF=QueryDB?tag=%s&edition=%s&version=%s&archToDelete=%s> 
				<IMG SRC=/Images/delete_16.gif BORDER=0 WIDTH=12 HEIGHT=12></a> %s</TD>''' % \
								(self.productTag, self.productEdition, self.productVersion, arch[2], arch[0]))

			if arch[1] == 'Y':
				wr('<TD ALIGN=LEFT WIDTH=3><FONT SIZE=2>Yes. <TD ALIGN=RIGHT>')
				wr('<FONT SIZE=2><A HREF=QueryDB?tag=%s&edition=%s&version=%s&archToChRelease=%s>Unrelease</TD>' % \
								(self.productTag, self.productEdition, self.productVersion, arch[0]))
			elif arch[1] == 'N':
				wr('<TD ALIGN=LEFT WIDTH=3><FONT SIZE=2>No. <TD ALIGN=RIGHT>')
				wr('<FONT SIZE=2><A HREF=QueryDB?tag=%s&edition=%s&version=%s&archToChRelease=%s>Release</a></TD>' % \
								(self.productTag, self.productEdition, self.productVersion, arch[0]))
		else:
			color = not color

		wr('</TR>')
	wr('</FONT>')
	wr('</TABLE>')

#}

def outputBuildHTML(builds):
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
		wr('''<A HREF=viewBuildInfo?tag=%s&edition=%s&version=%s&selectedBuild=%s>
			  <IMG SRC=/Images/search_16_h.gif BORDER=0 WIDTH=13 HEIGHT=13></a> %s''' % \
								(self.productTag, self.productEdition, self.productVersion, build, build) )
		wr('</TR>')
		wr('</TD>')

	wr('</TABLE>')

#}

