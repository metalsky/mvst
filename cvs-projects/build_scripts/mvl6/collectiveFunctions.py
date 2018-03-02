#!/usr/bin/python
import string,os,sys
Header="<!--#include virtual=\"/include/header.inc\" -->\n"
Footer="<!--#include virtual=\"/include/footer.inc\" -->\n"

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

def InitExcel(TextFile):
	TextFile.write("Stage\t")

def InitStatsHeader(HtmlFile,BuildTag):
	HtmlFile.write(Header)
	HtmlFile.write("<h2>This is the statatistics for the " + BuildTag + " build. This page only contains ")
	HtmlFile.write("percentages of build items building. This is intended to show progress towards release</h2>\n")
	HtmlFile.write("<br><br><h3>For a execl importable file, hold down the shift-key and click ")
	HtmlFile.write("<a href=\"" + BuildTag + ".dat\">here</a> and save to your PC.</h3>\n")
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Stage</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Results</font></th></tr>\n")

def InitBuildHeader(HtmlFile,BuildId,BuildTag,ChangeLog):
	HtmlFile.write(Header)
	if BuildTag != BuildId:
		HtmlFile.write("<h1>This is the build results for the " + BuildTag + " build, which used a build_id of " + BuildId + ".<br>This page only contains ")
	else:
		HtmlFile.write("<h1>This is the build results for the " + BuildTag + " build.<br>This page only contains ")
	HtmlFile.write("numbers of build items not building.<br>")
	if ChangeLog != "skipcl":
		HtmlFile.write("The change logs are <a href=\"" + ChangeLog + "\">here</a>.</h1>\n")
	else:
		HtmlFile.write("</h1>\n")
	HtmlFile.write("<br clear=right>\n")
	HtmlFile.write("<Table Border Cols=2, NOSAVE cellpadding=4><tr>")
	HtmlFile.write("<th><Font size=+2>Stage</font></th>\n")
	HtmlFile.write("<th><Font size=+2>Results</font></th></tr>\n")

def AddStageToExcel(TextFile, Stage):
	TextFile.write(Stage)

def AddStageToStats(HtmlFile, Stage):
	HtmlFile.write("<tr><td align=center><Font size=+2>" + Stage +"</font></td>\n")

def AddStageToBuild(HtmlFile, Stage):
	HtmlFile.write("<tr><td align=center><Font size=+2>" + Stage +"</font></td>\n")

def AddToExcel(TextFile, Stat):
	TextFile.write("\t" + Stat)

def AddToStats(HtmlFile, Stat, Item, BuildTag,Stage):
	if(Stat != "100"):
		HtmlFile.write("<td bgcolor=red align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Stage + "/html/" + Item + ".shtml>"+Stat+"%</a></font></td>\n")
	else:
		HtmlFile.write("<td bgcolor=green align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Stage + "/html/" + Item + ".shtml>"+Stat+"%</a></font></td>\n")

def AddToBuild(HtmlFile, Built,Items,Item,BuildTag,Stage):
	if(Built != Items):
		HtmlFile.write("<td bgcolor=red align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Stage + "/html/" + Item + ".shtml>"+Built+"/"+Items+"</a></font></td>\n")
	else:
		HtmlFile.write("<td bgcolor=green align=center><Font size=+2><a href=/logs/"+ BuildTag + "/"+ Stage +"/html/" + Item + ".shtml>"+Built+"/"+Items+"</a></font></td>\n")

def StageDoneExcel(TextFile):
	TextFile.write("\n")

def StageDoneHtml(HtmlFile):
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

def AddStage(TextFile, SHtmlFile, BHtmlFile, Stage):
	AddStageToExcel(TextFile, Stage)
	AddStageToStats(SHtmlFile, Stage)
	AddStageToBuild(BHtmlFile, Stage)

def AddMainNA(TextFile, SHtmlFile, BHtmlFile):
	AddToExcelNA(TextFile)
	AddToHtmlNA(SHtmlFile)
	AddToHtmlNA(BHtmlFile)

def AddMain(TextFile, SHtmlFile, BHtmlFile,StatsFile,Item,Stage,BuildTag):
	if len(StatsFile) != 0:
		StatLine = string.split(string.replace(StatsFile[len(StatsFile) - 1], "\n","")," ")
		AddToExcel(TextFile,StatLine[4])
		AddToStats(SHtmlFile,StatLine[4],Item,BuildTag,Stage)
		AddToBuild(BHtmlFile,StatLine[2],StatLine[0],Item,BuildTag,Stage)

def StageDone(TextFile, SHtmlFile, BHtmlFile):
	StageDoneExcel(TextFile)
	StageDoneHtml(SHtmlFile)
	StageDoneHtml(BHtmlFile)

def MainClose(TextFile, SHtmlFile, BHtmlFile):
	MainCloseExcel(TextFile)
	MainCloseHtml(SHtmlFile)
	MainCloseHtml(BHtmlFile)

