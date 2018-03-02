#!/usr/bin/python
import os, string, traceback, sys, getpass

class EnvError(StandardError):
	pass


def getEnvName():
	try:	
		list = os.listdir('/chroot/%s/'%getpass.getuser())
	except:
		raise EnvError
	else:
		return list[0]

def main():
	username = getpass.getuser()
	try:
		os.system('linux32 sudo chroot /chroot/%s/%s su %s -c "export LM_LICENSE_FILE=27000@localhost;/bin/bash" -  '%(username,getEnvName(),username))
	except EnvError:
		sys.stderr.write('Could not find a configured environment, did you run env_setup?\n')
		sys.exit(1)
	except:
		traceback.print_exc()
		sys.stderr.write('Unknown Error, contact build@mvista.com\n')
		sys.exit(1)


if __name__ == "__main__":
	main()



