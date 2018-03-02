#!/usr/bin/python
import lt_os,retentionLog
DEBUG = 0 

def main():
	dirFile = open('oldDirectories.txt')
	for dir in dirFile.readlines():

		destDir = dir.replace('/mvista/dev_area' , '/mvista/dev_area/removal').replace('\n', '')
		if destDir[len(destDir)-1] == "/":
			buildIndex = destDir[0:-1].rindex("/")
		else:
			buildIndex = destDir.rindex("/")

#		if False:
#			print "**"
#			print ""
#			print 'dir - %s' % dir
#			print 'sudo mkdir -p ' + dir.replace('/mvista/dev_area' , '/mvista/dev_area/removal') 
#			print "sudo mv %s" % (dir) + ' ' + destDir[0:buildIndex]
#			print "**"
#			print ""

		cmd = dir + ' ' + destDir[0:buildIndex] 
		cmd = cmd.replace("\n","")
		#system('sudo mkdir -p ' + dir.replace('/mvista/dev_area' , '/mvista/dev_area/removal') )
		retentionLog.logInfo("Deleting Build %s" % dir)
	
		if "RELEASED_by_buildtag" not in dir:
			lt_os.system( "sudo rm -rf %s" % dir, False)
	
		



if __name__ in ['__main__']:
	main()
	
