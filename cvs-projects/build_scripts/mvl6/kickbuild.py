#!/usr/bin/env python
import commands,sys, os
lp64 = '/chroot/centos4_64/home/build/latest_prebuilt'


launchCmd = ''
print len(sys.argv)
for arg in sys.argv[1:-1]:
	launchCmd += arg + ' '

buildtag = sys.argv[-1]

if launchCmd[-1] == ' ':
	launchCmd = launchCmd[:-1]
	
machineConfs = commands.getoutput('''ls /chroot/centos4/opt/montavista/content/kernel/conf/machine''')
machineConfs = map(lambda x: x[:-5], machineConfs.split('\n'))

print commands.getoutput('''sudo chroot /chroot/centos4 /bin/su - build -c "source ~/.bashrc;bitbake -c clean linux; bitbake -c fetch linux"''')
print commands.getoutput('''sudo chroot /chroot/centos4_64 /bin/su - build -c "source ~/.bashrc;bitbake -c clean linux; bitbake -c fetch linux"''')


for machine in machineConfs:
	fp = open('/chroot/centos4/opt/montavista/content/foundation/conf/local.conf', 'a')
	fp64 = open('/chroot/centos4_64/opt/montavista/content/foundation/conf/local.conf', 'a')
	fp.write('MACHINE="%s"\n' % machine)
	fp64.write('MACHINE="%s"\n' % machine)
	fp.close()
	fp64.close()
	commands.getoutput('''sudo chroot /chroot/centos4 /bin/su - build -c "source ~/.bashrc;bitbake %s" > /tmp/%s.log''' % (launchCmd, machine))
	if not os.path.exists(lp64):
		os.makedirs(lp64)
	try:
		for dir in os.listdir('/chroot/centos4/home/build/prebuilt/'):
			os.system('cp /chroot/centos4/home/build/prebuilt/%s/* /chroot/centos4_64/home/build/latest_prebuilt' % dir)
	except:
		print 'Something wrong with prebuilt copy, this is going to take awhile'
	commands.getoutput('''sudo linux64 chroot /chroot/centos4_64 /bin/su - build -c "source ~/.bashrc;bitbake %s" > /tmp/%s-64.log''' % (launchCmd, machine))
