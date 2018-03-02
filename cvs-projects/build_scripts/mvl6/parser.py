#!/usr/bin/env python
import re,os,sys

class parser:
	def __init__(self, logdir):
		self.numLogs = 0
		logs = os.popen('ls %s/*.log' % logdir).readlines()
		if not logs:
			print "No logs, quiting."
			sys.exit(1)
		self.numLogs = len(logs)
		self.LogDict = {}
		# sample LogDict:
		# {
		#	'msd name':	[logfile, PackageDict, SummaryList, totalNumApps, totalErrors],
		# }

		for logfile in logs:
			logfile = logfile.strip()
			msdName = logfile.split('/')[-1][:-4]
			self.LogDict[msdName] = []
			self.LogDict[msdName].append(logfile)
			LogFileList = open(logfile).readlines()
			PackageDict = {}
			# sample PackageDict:
			# {
			#	pakNum:		[
			#				<package name>,
			#				<package error>,
			#				<collection>,
			#				[(linenum,line),...]],
			# }
			SummaryList = []

			RE_Summary	= re.compile(r'NOTE: Tasks Summary: (.*)')
			RE_Error	= re.compile(r'ERROR: (.*)')
			RE_QAIssue	= re.compile(r'ERROR: QA Issue(.*)')
			RE_Note		= re.compile(r'NOTE: Running task (.*) \(ID: (.*), (.*)\.bb, (.*)\)')
			# Sample match:
			# NOTE: Running task 13 of 4303 (ID: 3692, /opt/montavista/content/foundation/recipes/stage-manager/stagemanager-native_0.0.1.bb, do_patch)
	
			# group(1) = task numbers
			# group(2) = ID
			# group(3) = bitbake recipe
			# group(4) = stage (i.e. do_fetch)
		
			lineNum = 0
			newPak = 0
			pakNum = 0
			totalPaks = 0
			totalErrors = 0
			error = 0
			summaryLog = 0
			packages = []
			currentPkg = 'Parsing'
			collection = 'none'
			packages.append(currentPkg)
			try:
				PackageDict[pakNum].append(currentPkg)
			except KeyError:
				PackageDict[pakNum] = [currentPkg]
			try:
				PackageDict[pakNum].append(error)
			except KeyError:
				PackageDict[pakNum] = [error]
			try:
				PackageDict[pakNum].append(collection)
			except KeyError:
				PackageDict[pakNum] = [collection]
			for line in LogFileList:
				lineNum += 1
				noteMatch	= RE_Note.match(line)
				errorMatch	= RE_Error.match(line)
				qaMatch		= RE_QAIssue.match(line)
				summaryMatch	= RE_Summary.match(line)
				if noteMatch and not summaryMatch:
					currentPkg = noteMatch.group(3).split('/')[-1]
					collection = noteMatch.group(3).split('/')[-4]
					if currentPkg not in packages:
						packages.append(currentPkg)
						totalPaks += 1
						pakNum = totalPaks
						newPak = 1
						error = 0
					else:
						for pak in PackageDict.keys():
							if currentPkg == PackageDict[pak][0]:
								pakNum = pak
				elif summaryMatch:
					currentPkg = 'Summary'
					summaryLog = 1
				elif errorMatch and not qaMatch and not summaryLog:
					if PackageDict[pakNum][0] != 'Parsing' and PackageDict[pakNum][1] != 1:
						totalErrors += 1
					try:
						PackageDict[pakNum][1] = 1
					except KeyError:
						PackageDict[pakNum][1] = 1
				elif qaMatch:
					if PackageDict[pakNum][1] != 1:
						try:
							PackageDict[pakNum][1] = 2
						except KeyError:
							PackageDict[pakNum][1] = 2
				else:
					newPak = 0
				if newPak:
					try:
						PackageDict[pakNum].append(currentPkg)
					except KeyError:
						PackageDict[pakNum] = [currentPkg]
					try:
						PackageDict[pakNum].append(error)
					except KeyError:
						PackageDict[pakNum] = [error]
					try:
						PackageDict[pakNum].append(collection)
					except KeyError:
						PackageDict[pakNum] = [collection]
				if not summaryLog:
					try:
						PackageDict[pakNum].append((lineNum,line))
					except KeyError:
						PackageDict[pakNum] = [(lineNum,line)]
				else:
					try:
						SummaryList.append((lineNum,line))
					except KeyError:
						SummaryList = [(lineNum,line)]
			self.LogDict[msdName].append(PackageDict)
			self.LogDict[msdName].append(SummaryList)
			# totalPaks is used as the pakNUm, where Parsing is set as pakNum 0, so
			# the end value for totalPaks is the actual number of packages
			self.LogDict[msdName].append(totalPaks)
			self.LogDict[msdName].append(totalErrors)
			

	def outputHTML(self, outDir, buildtag):
		# generate Build page
		GREEN = '''<TD BGCOLOR=GREEN ALIGN=CENTER><Font size=+2>\n'''
		RED = '''<TD BGCOLOR=RED ALIGN=CENTER><Font size=+2>\n'''
		YELLOW = '''<TD BGCOLOR=YELLOW ALIGN=CENTER><Font size=+2>\n'''
		ENDROW = '''</Font></TD></TR>\n'''

		if not os.path.exists(os.path.join(outDir,buildtag)):
			os.makedirs(os.path.join(outDir,buildtag))

		outfile = open(os.path.join(outDir,buildtag,'build.shtml'),'w')
		outfile.write('<!--#include virtual="/include/header.inc" -->\n')
		for msdName in self.LogDict.keys():
			logfile = self.LogDict[msdName][0]
			PackageDict = self.LogDict[msdName][1]
			SummaryList = self.LogDict[msdName][2]
			totalPaks = int(self.LogDict[msdName][3])
			errors = int(self.LogDict[msdName][4])
			lines = SummaryList
			outfile.write('<h4>%s results</h4>\n' % msdName)
			outfile.write('<TABLE BORDER NOSAVE CELLPADDING=4 CELLSPACING=0>\n')
			outfile.write('<tr><th><Font size=+2>Tasks</font></th>\n')
			outfile.write('<th><Font size=+2>Results</font></th></tr>\n')

			# Summary
			lineOut = '<A HREF=%s-Summary>Summary</A>' % msdName
			outfile.write('''<TR><TD ALIGN=CENTER><Font size=+2>%s</Font></TD>\n''' % (lineOut))
			if lines:
				outfile.write('''%s1/1%s''' % (GREEN,ENDROW))
			else:
				outfile.write('''%s0/1%s''' % (RED,ENDROW))
		
			# bitbake
			lineOut = '<A HREF=%s.shtml>Bitbake Results</A>' % msdName
			outfile.write('''<TR><TD ALIGN=CENTER><Font size=+2>%s</Font></TD>\n''' % (lineOut))
			collections = {}
			# collections = {
			#	<collection name>:	[
			#					numPaks,
			#					numErrors],
			#	}
			if errors:
				outfile.write('''%s%s/%s%s''' % (RED,str(totalPaks - errors),str(totalPaks),ENDROW))
			else:
				outfile.write('''%s%s/%s%s''' % (GREEN,str(totalPaks),str(totalPaks),ENDROW))

			outfile.write('</TABLE>\n')
			outfile.write('&nbsp;\n')
		outfile.write('<!--#include virtual="/include/footer.inc" -->\n')
		outfile.close()

		BUILT = '''<TD BGCOLOR=GREEN ALIGN=CENTER><Font size=+2>Built</Font></TD></TR>\n'''
		FAILED = '''<TD BGCOLOR=RED ALIGN=CENTER><Font size=+2>Error</Font></TD></TR>\n'''
		MOSTLY = '''<TD BGCOLOR=YELLOW ALIGN=CENTER><Font size=+2>Mostly Right</Font></TD></TR>\n'''
		QA = '''<TD bgcolor=a0c0e0 text=midnightblue ALIGN=CENTER><Font size=+2>QA Issue</Font></TD></TR>\n'''
		for msdName in self.LogDict.keys():
			logfile = self.LogDict[msdName][0]
			PackageDict = self.LogDict[msdName][1]
			summary = self.LogDict[msdName][2]
			pakNums = PackageDict.keys()
			pakNums.sort()

			tmp = {}
			for pakNum in pakNums:
				collection = PackageDict[pakNum][2]
				try:
					tmp[collection].append(pakNum)
				except KeyError:
					tmp[collection] = [pakNum]

			pakNums = []
			collectionKeys = tmp.keys()
			collectionKeys.sort()
			for col in collectionKeys:
				for pakNum in tmp[col]:
					pakNums.append(pakNum)


				
	
			if not os.path.exists(os.path.join(outDir,buildtag)):
				os.makedirs(os.path.join(outDir,buildtag))
	
			# generate collections pages
			# generate Bitbake Page
			outfile = open(os.path.join(outDir,buildtag,'%s.shtml' % msdName),'w')
			outfile.write('<!--#include virtual="/include/header.inc" -->\n')
			outfile.write('<h4>The Parsing log is not considered an actual application so it is not included in the total built/total attempted package statistics on the previous page.  It is only included in order to show all of the data in the bitbake log file.</h4>\n')
			outfile.write('<TABLE BORDER NOSAVE CELLPADDING=4 CELLSPACING=0>\n')
			outfile.write('<tr><th><Font size=+2>Tasks</font></th>\n')
			outfile.write('<th><Font size=+2>Results</font></th></tr>\n')

			currentCollection = 'xyz'
			for pakNum in pakNums:
				package = PackageDict[pakNum][0]
				if currentCollection != PackageDict[pakNum][2]:
					currentCollection = PackageDict[pakNum][2]
					outfile.write('''<TR BGCOlOR=#d8d8d8><TD ALIGN=CENTER><FONT SIZE=+3><B>%s</B></TD><TD></TD>''' % currentCollection)
				lineOut = '<A HREF=%s-%s>%s</A>' % (msdName,package,package)
				outfile.write('''<TR><TD ALIGN=CENTER><Font size=+2>%s</Font></TD>\n''' % (lineOut))
				if PackageDict[pakNum][1] == 1:
					if PackageDict[pakNum][0] == 'Parsing':
						outfile.write(MOSTLY)
					else:
						outfile.write(FAILED)
				elif PackageDict[pakNum][1] == 2:
					outfile.write(QA)
				else:
					outfile.write(BUILT)
			outfile.write('</TABLE>\n')
			outfile.write('<!--#include virtual="/include/footer.inc" -->\n')
			outfile.close()

			for pakNum in pakNums:
				package = PackageDict[pakNum][0]
				outfile = open(os.path.join(outDir,buildtag,'%s-%s' % (msdName,package),),'w')
				lines = len(PackageDict[pakNum])
				line = 3
				while line < lines:
					outfile.write('''%s\t%s''' % (PackageDict[pakNum][line][0], PackageDict[pakNum][line][1]))
					line += 1
				outfile.close()
			outfile = open(os.path.join(outDir,buildtag,'%s-Summary' % msdName,),'w')
			if summary:
				lineNum = 0
				for line in summary:
					outfile.write('''%s\t%s''' % (summary[lineNum][0],summary[lineNum][1]))
					lineNum += 1
			else:
				outfile.write('''No Summary''')
			outfile.close()

	def updateSummarySHTML(self, outDir, buildtag):
		# first determine if the msd name exists in the summary table
		# if it does not, add a new table row
		# if it does exist, update the existing row
		summary = '%s/mvl6_summary.shtml' % outDir
		tmpsummary = '%s/mvl6_summary.shtml' % outDir
		tmpfile = '/tmp/summary-%s' % buildtag
		if os.path.exists(tmpsummary):
			RE_MSD		= re.compile('<TR><TD ALIGN=CENTER><Font size=\+1>(.*)')
			RE_buildtag	= re.compile(r'<a href=(.*)/build.shtml>(.*)</a>')
			RE_stats	= re.compile('<!--(.*)--><TD BGCOLOR=(.*) ALIGN=CENTER><Font size=\+1>(.*)/(.*)</Font></TD>')
			msdEnd		= '''</TR>'''
			footer		= '''</TABLE>&nbsp;<!--#include virtual="/include/footer.inc" -->'''
			for msdName in self.LogDict.keys():
				totalApps = self.LogDict[msdName][3]
				totalErrors = self.LogDict[msdName][4]
				f_summary = open(tmpsummary,'r')
				summaryLines = f_summary.readlines()
				f_summary.close()
				f_tmp = open(tmpfile,'w')
				host = '32'
				if msdName[-3:] == '-64':
					msdName = msdName[:-3]
					host = '64'
				newMsd = 1
				for line in summaryLines:
					msdMatch	= RE_MSD.match(line)
					if msdMatch:
						if msdName == msdMatch.group(1):
							newMsd = 0
				update = 0
				for line in summaryLines:
					msdMatch	= RE_MSD.match(line)
					tagMatch	= RE_buildtag.match(line)
					statMatch	= RE_stats.match(line)
					if msdMatch:
						if newMsd and msdMatch.group(1) > msdName:
							f_tmp.write('<TR><TD ALIGN=CENTER><Font size=+1>%s\n' % msdName)
							f_tmp.write('</Font></TD>\n')
							f_tmp.write('<TD ALIGN=CENTER><Font size=+1>\n')
							f_tmp.write('<a href=%s/build.shtml>%s</a>\n' % (buildtag,buildtag))
							f_tmp.write('</Font></TD>\n')
							f_tmp.write('<!--32--><TD BGCOLOR=GREEN ALIGN=CENTER><Font size=+1>%s/%s</Font></TD>\n' % (str(totalApps -totalErrors),str(totalApps)))
							f_tmp.write('<!--64--><TD BGCOLOR=GREEN ALIGN=CENTER><Font size=+1>%s/%s</Font></TD>\n' % (str(totalApps -totalErrors),str(totalApps)))
							f_tmp.write('</TR>\n\n')
							newMsd = 0
							update = 0
						elif msdName == msdMatch.group(1):
							update = 1
						f_tmp.write(line)
					elif tagMatch and update:
						f_tmp.write(line.replace(tagMatch.group(1),buildtag))
					elif statMatch and update:
						if statMatch.group(1) == host:
							newline = line.replace('%s/%s' % (statMatch.group(3),statMatch.group(4)),'%s/%s' % (str(totalApps -totalErrors),str(totalApps)))
							if totalErrors:
								newline = newline.replace(statMatch.group(2),'RED')
							else:
								newline = newline.replace(statMatch.group(2),'GREEN')
							f_tmp.write(newline)
							update = 0
						else:
							f_tmp.write(line)
					else:
						f_tmp.write(line)
				f_tmp.close()
				tmpsummary = tmpfile
		os.system('cp %s %s' % (tmpsummary,summary))
		os.system('rm -f %s' % tmpfile) 


if __name__ in ['__main__']:
  if len(sys.argv) != 2:
    print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
    sys.exit(0)
  buildtag = sys.argv[1]
  outDir = '/export/logs'
  if os.path.exists('/mvista/dev_area/mvl6/%s' % buildtag):
    collective = parser('/mvista/dev_area/mvl6/%s' % buildtag)
    collective.outputHTML(outDir,buildtag)
    collective.updateSummarySHTML(outDir,buildtag)
  else:
    print 'No logs exist in: /mvista/dev_area/mvl6/%s' % buildtag

