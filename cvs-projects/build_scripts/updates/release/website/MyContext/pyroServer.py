#! /usr/bin/env python


import Pyro.core

SERVER = "PYROLOC://release.sh.mvista.com:7767/release_d"


class server:
	def __init__(self):
		self.PYRO_SERVER = "PYROLOC://release.sh.mvista.com:7767/release_d"
		self.Proxy = None
	
	def Connected(self):
		return (self.Proxy != None)
	
	def Connect(self):
		if self.Connected():
			return None


		try:
			Pyro.core.initClient(0)
			Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
			self.Proxy = Pyro.core.getProxyForURI(self.PYRO_SERVER)

		except:
			return "Can't connect to Pyro server"

	
	def Close(self):
		if self.Connected():
			self.Proxy._release()
		self.Proxy = None


	def getObj(self):
		return self.Proxy

#end server


def main(argv):
	import sys
	sys.stderr.write("This moodule is not designed to be called directly\n")
	sys.exit(1)


if __name__ == "__main__":
	main(sys.argv)


