import commands

def run(cmd, printOutput=True, DBG=False):
	if DBG:
		print cmd
	output = commands.getoutput(cmd)
	if printOutput:
		print output

	return output

def crun(cmd, printOutput=True, DBG=False):
	run('sudo chroot /chroot/centos4 /bin/su - build -c "%s"' % cmd, printOutput, DBG)

