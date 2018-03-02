#!/usr/bin/python

import os, sys

PSERVER = "PSERVER"
SSH = "SSH"

def usage(exe_name):
	sys.stderr.write('This script will update CVS Roots to use the new server names')
	sys.stderr.write('Usage:\n %s <cvs repo> <PSERVER>|<SSH>\n'%exe_name)
	sys.stderr.write('Where <cvs repo> is a checked out CVS Repository\n')
	sys.exit(1)

def getUsername():
	return (os.popen('whoami').readlines()[0]).strip('\n')

def main(argv):
	if len(argv) != 3:
		usage(argv[0])
	if not os.path.exists(argv[1]):
		sys.stderr.write('\nError: Directory "%s" not found\n\n'%argv[1])
		usage(argv[0])
	if argv[2] != PSERVER and argv[2] != SSH:
		sys.stderr.write('\nError: Bad flag "%s" is not available\n\n'%argv[2])
		usage(argv[0])
	else:
		method = argv[2]
	

	username = getUsername()
	for root, dirs, files in os.walk(argv[1]):
		if root.find('CVS') > -1:
			cvsroot_path = os.path.join(root,'Root')
			if os.path.exists(cvsroot_path):
				repo = os.popen('cat %s'%cvsroot_path).readline().split('/')[-1].strip('\n')
				if method == PSERVER:
					os.system('echo ":pserver:%s@cvs.sh.mvista.com:/cvsdev/%s" > %s'%(username,repo,cvsroot_path))
				if method == SSH:
					os.system('echo ":ext:%s@cvs.sh.mvista.com:/cvsdev/%s" > %s'%(username,repo,cvsroot_path))				

if __name__=="__main__":
	main(sys.argv)



