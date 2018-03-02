#!/usr/bin/python
                                                                                                              
import string,os,sys
Header="<!--#include virtual=\"/include/header.inc\" -->\n"
Footer="<!--#include virtual=\"/include/footer.inc\" -->\n"
                                                                                                              
AllCoresFailed=0
DistroList = [ "centos", "redhat", "suse", "solaris", "windows" ]

def GetHostList(LogDir, BuildId):
	HostList = []
	hostlogs = os.popen("cd "+ LogDir + "; ls host-*-" + BuildId + ".log").readlines()
	for hostlog in hostlogs:
		cleanHost = string.split((string.split(hostlog,"-")[1]),"/")
		HostList.append(cleanHost[len(cleanHost) - 1])
	if(HostList != []):
		return HostList
	return -1

def GenItemHtml(ItemDir, HtmlFile, StatFile, Name, BuildTag):
	HtmlFile.write(Header)
	HtmlFile.write("<h1>" + BuildTag + " " + Name + "</h1>\n")
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<center>\n")
	HtmlFile.write("<Table Border Cols=2, width=\"60%\" NOSAVE cellpadding=4>\n")
	HtmlFile.write("<tr><th align=center><Font size=+3>Build Item</font></th><th align=center><Font size=+3>Status</font></th></tr>\n")
	i = 0
	if len(StatFile) != 0:
		while(string.find(StatFile[i],"----") == -1):
			StatLine = string.split(string.replace(StatFile[i],"\n","")," ")
			HtmlFile.write("<tr>\n")
			HtmlFile.write("<td align=center><font size=+2><a href=\"" + ItemDir + StatLine[0] +"\">" + StatLine[0] + "</a>" + "</font></td>\n")
			if(StatLine[1] == "1"):
				HtmlFile.write("<td bgcolor=red align=center><font size=+2>Failed</font></td>\n")
			else:
				HtmlFile.write("<td bgcolor=green align=center><font size=+2>Built</font></td>\n")
			HtmlFile.write("</tr>\n")
			i = i + 1
	HtmlFile.write("</table>\n")
	HtmlFile.write("<Table Border Cols=5, width=\"60%\" NOSAVE cellpadding=4>\n")
	HtmlFile.write("<tr><th><Font size=+1>Items</font></th>\n")
	HtmlFile.write("<th><Font size=+1>Not Built</font></th>\n")
	HtmlFile.write("<th><Font size=+1>Built</font></th>\n")
	HtmlFile.write("<th><Font size=+1>% Not Built</font></th>\n")
	HtmlFile.write("<th><Font size=+1>% Built</font></th>\n</tr>\n")
	if len(StatFile) != 0:
		Stats=string.split(string.replace(StatFile[i+1],"\n",""), " ")
		HtmlFile.write("<tr>\n")
		for each in Stats:
			HtmlFile.write("<td align=center>"+ each + "</td>\n")
	HtmlFile.write("</tr>\n")
	HtmlFile.write("</table>\n")
	HtmlFile.write(Footer)
                                                                                                              
def InitExcel(TextFile,HostList):
	TextFile.write("Arch\t")
	if not AllCoresFailed:
		for each in HostList:
			TextFile.write("\t" + each)
	TextFile.write("\tApps")
	TextFile.write("\tLsps")
	TextFile.write("\tCDs\n")

def InitStatsHeader(HtmlFile,BuildTag,HostList):
	HtmlFile.write(Header)
	HtmlFile.write("<h1>This is the statatistics for the " + BuildTag + " build. This page only contains ")
	HtmlFile.write("percentages of build items building. This is intended to show progress towards release</h1>\n")
	HtmlFile.write("<br><br><h3>For a execl importable file, hold down the shift-key and click ")
	HtmlFile.write("<a href=\"" + BuildTag + ".dat\">here</a> and save to your PC.</h3>\n")
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Script</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Results</font></th></tr>\n")
                                                                                                              
def InitStatsHT(HtmlFile,BuildTag,HostList):
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Host</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Host-Tools</font></th></tr>\n")

def InitStatsHostHeader(HtmlFile,BuildTag,HostList):
	if HostList != -1:
		HostLen=len(HostList)
		HtmlFile.write("<br clear=right><center>\n")
		HtmlFile.write("<Table Border Cols=%d, width=\"100%%\" NOSAVE cellpadding=4><tr>" % (6 + HostLen))
		HtmlFile.write("<th><Font size=+2>App Type</font></th>\n")
		for each in HostList:
			HtmlFile.write("<th><Font size=+2>" + each + "</font></th>\n")
		HtmlFile.write("</tr>\n")
                                                                                                              
def InitStats(HtmlFile,BuildTag,HostList):
	print AllCoresFailed
	if(AllCoresFailed == 1):
		HostLen=0
	else:
		HostLen=len(HostList)
	HtmlFile.write("<br clear=right><center>\n")
	HtmlFile.write("<Table Border Cols=%d, width=\"100%%\" NOSAVE cellpadding=4><tr>" % (6 + HostLen))
	HtmlFile.write("<th><Font size=+2>Arch</font></th>\n")
	if(AllCoresFailed != 1):
		for each in HostList:
			HtmlFile.write("<th><Font size=+2>" + each + "</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Apps</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Lsps</font></th>\n")
	HtmlFile.write("<th><Font size=+2>CDs</font></th></tr>\n")

def InitBuildHeader(HtmlFile,BuildId,BuildTag,HostList,ChangeLog):
	HtmlFile.write(Header)
	if BuildTag != BuildId:
		HtmlFile.write("<h1>This is the build numbers for the " + BuildTag + " build, which used a build_id of " + BuildId + ".<br>This page only contains ")
	else:
		HtmlFile.write("<h1>This is the build numbers for the " + BuildTag + " build.<br>This page only contains ")
	HtmlFile.write("numbers of build items not building.<br>This is intended to help the developers.<br>")
	HtmlFile.write("This <a href=\"hhl-" + BuildId + ".log\">file</a> describes the branches used in this build.<br>")
	HtmlFile.write("This <a href=\" " + BuildTag + ".tab\">file</a> is the tab delineated version table.<br>")
	HtmlFile.write("This <a href=\"buildtimes\"> file </a> show build times<br>")
	if ChangeLog != "skipcl":
		HtmlFile.write("The change logs are <a href=\"" + ChangeLog + "\">here</a>.</h1>\n")
	else:
		HtmlFile.write("</h1>\n")
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Script</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Results</font></th></tr>\n")

def InitBuildHT(HtmlFile,BuildId,BuildTag,HostList):
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Host</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Host Tools</font></th></tr>\n")
                                                                                                              
def InitBuildHostHeader(HtmlFile,BuildId,BuildTag,HostList):
	if HostList != -1:
		HostLen=len(HostList)
		HtmlFile.write("<br clear=right><center>\n")
		HtmlFile.write("<Table Border Cols=%d, width=\"100%%\" NOSAVE cellpadding=4><tr>" % (6 + HostLen))
		HtmlFile.write("<th align=center><Font size=+2>App Type</font></th>\n")
		for each in HostList:
			HtmlFile.write("<th align=center><Font size=+2>" + each + "</font></th>\n")
		HtmlFile.write("</tr>\n")

def InitBuild(HtmlFile,BuildId,BuildTag,HostList):
	print AllCoresFailed
	if(AllCoresFailed == 1):
		HostLen=0
	else:
		HostLen=len(HostList)
	HtmlFile.write("<br clear=right><center>\n")
	HtmlFile.write("<Table Border Cols=%d, width=\"100%%\" NOSAVE cellpadding=4><tr>" % (6 + HostLen))
	HtmlFile.write("<th align=center><Font size=+2>Arch</font></th>\n")
	if(AllCoresFailed != 1):
		for each in HostList:
			HtmlFile.write("<th align=center><Font size=+2>" + each + "</font></th>\n")
	HtmlFile.write("<th align=center><Font size=+2>Apps</font></th>\n")
	HtmlFile.write("<th align=center><Font size=+2>Lsps</font></th>\n")
	HtmlFile.write("<th align=center><Font size=+2>CDs</font></th></tr>\n")
                                                                                                              
def AddArchToExcel(TextFile, Arch):
	TextFile.write(Arch)
                                                                                                              
def AddArchToStats(HtmlFile, Arch):
	HtmlFile.write("<tr><td align=center><Font size=+2>" + Arch +"</font></td>\n")
                                                                                                              
def AddArchToBuild(HtmlFile, Arch):
	HtmlFile.write("<tr><td align=center><Font size=+2>" + Arch +"</font></td>\n")

def AddToExcel(TextFile, Stat):
	TextFile.write("\t" + Stat)
                                                                                                              
def AddToStats(HtmlFile, Stat, Item, BuildTag,Arch):
	if(Stat != "100"):
		HtmlFile.write("<td bgcolor=red align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Arch + "/html/" + Item + ".shtml>"+Stat+"%</a></font></td>\n")
	else:
		HtmlFile.write("<td bgcolor=green align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Arch + "/html/" + Item + ".shtml>"+Stat+"%</a></font></td>\n")
                                                                                                              
def AddToBuild(HtmlFile, Built,Items,Item,BuildTag,Arch):
	if(Built != Items):
		HtmlFile.write("<td bgcolor=red align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Arch + "/html/" + Item + ".shtml>"+Built+"/"+Items+"</a></font></td>\n")
	else:
		HtmlFile.write("<td bgcolor=green align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Arch +"/html/" + Item + ".shtml>"+Built+"/"+Items+"</a></font></td>\n")
                                                                                                              
def ArchDoneExcel(TextFile):
	TextFile.write("\n")
                                                                                                              
def ArchDoneHtml(HtmlFile):
	HtmlFile.write("</tr>")
                                                                                                              
def MainCloseExcel(TextFile):
	TextFile.close()

def MainCloseHtml (HtmlFile):
	HtmlFile.write("</table>")
	HtmlFile.write(Footer)
                                                                                                              
def AddToExcelNA(TextFile):
	TextFile.write("\t0")

def AddToHtmlNA(HtmlFile):
	HtmlFile.write("<td bgcolor=red align=center><Font size=+2>N/A</a></font></td>\n")

def AddArch(TextFile, SHtmlFile, BHtmlFile, Arch):
	AddArchToExcel(TextFile, Arch)
	AddArchToStats(SHtmlFile, Arch)
	AddArchToBuild(BHtmlFile, Arch)
                                                                                                              
def AddMainNA(TextFile, SHtmlFile, BHtmlFile):
	AddToExcelNA(TextFile)
	AddToHtmlNA(SHtmlFile)
	AddToHtmlNA(BHtmlFile)
                                                                                                              
def AddMain(TextFile, SHtmlFile, BHtmlFile,StatsFile,Item,Arch,BuildTag):
	if len(StatsFile) != 0:
		StatLine = string.split(string.replace(StatsFile[len(StatsFile) - 1], "\n","")," ")
		AddToExcel(TextFile,StatLine[4])
		AddToStats(SHtmlFile,StatLine[4],Item,BuildTag,Arch)
		AddToBuild(BHtmlFile,StatLine[2],StatLine[0],Item,BuildTag,Arch)
                                                                                                              
def ArchDone(TextFile, SHtmlFile, BHtmlFile):
	ArchDoneExcel(TextFile)
	ArchDoneHtml(SHtmlFile)
	ArchDoneHtml(BHtmlFile)
                                                                                                              
def MainClose(TextFile, SHtmlFile, BHtmlFile):
	MainCloseExcel(TextFile)
	MainCloseHtml(SHtmlFile)
	MainCloseHtml(BHtmlFile)

