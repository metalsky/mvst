#!/usr/bin/python

import os,sys,string
from xml.dom import minidom
from xml.parsers.expat import ExpatError

def usage(argv):
	print '''
Usage: %s <dirname>
eg. %s gcc-3.4.3-25.0.136.0703282
''' % (argv[0], argv[0])
	sys.exit(1)

#}

def main(package):
	os.chdir("/mvista/ftp/arch")
	for dir in os.popen('ls -d *').readlines():
		dir = string.replace(dir, '\012','')
		if os.path.exists('/mvista/ftp/arch/%s/updates/%s'%(dir,package)):
			print "cleaning %s"%(dir)
			print "running parseManifest on /mvista/ftp/arch/%s/updates/manifest.xml" % (dir)
			parseManifest('/mvista/ftp/arch/%s/updates/' % (dir), package)
			os.system('rm -rf /mvista/ftp/arch/%s/updates/%s/' %(dir,package)

#}

#I am just learning this minidom module, and it is very sparsely documented on the web,
#so this code probably sucks.
def parseManifest(path, pkgToRemove):

	try:
		dom = minidom.parse('%s/manifest.xml' % path)
	except IOError:
		print "IO Error.  Most likely the file does not exist."
		return
	except ExpatError:
		print "There is a problem with this XML file.  Most likely it has mismatched brackets.  Please fix it. File will not be modified."
		return
	except:
		print "\nSomething bad happened!  Please contact rell@mvista.com with as many details as possible."
		sys.exit(1)

	packageList = dom.getElementsByTagName('package')
	patchList   = dom.getElementsByTagName('patch')

	linesToWrite = "<update-site>\n <packages type=\"mvl-rpm\">\n"
	
	for p in packageList:
		fp = p.getElementsByTagName('filepath')
		if pkgToRemove in fp[0].toxml(): 
			pass
		else:
			linesToWrite += "  " + p.toxml() + "\n"

	linesToWrite += " </packages>\n <patches type=\"kernel\">\n"

	for p in patchList:
		linesToWrite += "  " + p.toxml() + "\n"

	linesToWrite += " </patches>\n</update-site>\n"

	print 'cp ' + path + 'manifest.xml' + ' ' + path + "manifest.xml.bak"
	outFile = open(path + "manifest.xml", "w")
	outFile.write(linesToWrite)
	outFile.close()

#}

if __name__ in ['__main__']:
	if len(sys.argv) != 2:
		usage(sys.argv)
	else:
		main(sys.argv[1])
