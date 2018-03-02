#!/usr/bin/python

import os, sys

cygVer = 'mvcyg5.0'
port = '322'

def system(cmd):
	sys.stderr.write('%s\n'%cmd)
	os.system(cmd)


def main(argv):
	if len(argv) != 4:
		sys.stderr.write("Usage: %s <command> <operand> <type>\n"%argv[0])
		sys.stderr.write('Ex: %s "rm -rf" "/etc/fstab" file'%argv[0])
		sys.stderr.write('Valid Types are: file, none\n')
		sys.exit(1)

	cmd = argv[1]
	operand = argv[2]
	opType = argv[3]

	for i in (1,2,3,4,5,6,7,8,9,10,12,13,14,15,17,18,19,20):

		if opType == 'file':
			if i in (10,12):
				rootPath = '/cygdrive/d/%s'%cygVer
			else:
				rootPath = '/cygdrive/c/%s'%cygVer
		else:
			rootPath = ''

		if i in (13,14):
			user = 'build'
		else:
			user = 'administrator'

		system('ssh %s@cygwin-%s -p %s "%s %s%s"'%(user,i,port,cmd,rootPath,operand))



if __name__ == "__main__":
	main(sys.argv)
