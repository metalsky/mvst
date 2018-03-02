#! /usr/bin/env python

from inspect import getframeinfo,currentframe

class update:
	'''
	This is a generic update class for defining a common set
	of functionality between the newer apt update system and 
	the older mvl update system. Any methods defined here need
	to be implemented within the mvl and apt update classes.
	Those classes should inherit from this one to ensure proper
	method and argument checking.
	'''

	def __init__(self, product_id):
		self.ProductID = product_id
		return

	def _error(self, name):
		raise Error(name + " is not implemented")
	

	#These need to be overidden by the superclass
	def pushToTesting(self, merged_id):
		'''given a merged_id, push the update to the testing server'''
		return self._error(getframeinfo(currentframe())[2])

	def pushToLive(self, merged_id):
		'''given a merged_id, push the update to the live server'''
		return self._error(getframeinfo(currentframe())[2])
	
	def releaseNewTestArch(self, edition_arch_id):
		'''given the edition_arch_id, setup the repo for the new 
		arch, and push any updates that need to go out for it.'''
		return self._error(getframeinfo(currentframe())[2])
	
	def releaseNewLiveArch(self, edition_arch_id):
		'''given the edition_arch_id, setup the repo for the new 
		arch, and push any updates that need to go out for it.'''
		return self._error(getframeinfo(currentframe())[2])

	def removeFromTesting(self, merged_id):
		'''given a merged_id, remove the update from the testing server'''
		return self._error(getframeinfo(currentframe())[2])
	
	def removeFromLive(self, merged_id):
		'''given a merged_id remove the update from the live server'''
		return self._error(getframeinfo(currentframe())[2])

	def rebuildTesting(self, pkg_type):
		'''rebuild the manifest for all updates of type pkg_type'''
		return self._error(getframeinfo(currentframe())[2])
	
	def rebuildLive(self, pkg_type):
		'''rebuild the manifest for all updates of type pkg_type'''
		return self._error(getframeinfo(currentframe())[2])

#end update

class Error(Exception):
	pass


######################
#   main FUNCTION    #
######################

def main(argv):
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)


if __name__ == "__main__":
        main(sys.argv)
