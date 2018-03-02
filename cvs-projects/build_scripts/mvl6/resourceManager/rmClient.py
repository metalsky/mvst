#!/usr/bin/python

import Pyro.core, time
import config
from resourceError import ResourceError

Pyro.core.initClient(0)
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1

def remoteResourceGet(buildTag, buildId, resourceType, extraText):
	timeWaited=0
	notEnd = True
	while notEnd:
		try:
			timeWaited+=10
			if timeWaited > 1200: #Give up after waiting 20 minutes.
				raise ResourceError, "Timed out reconnecting to daemon."
			resourceManager = Pyro.core.getProxyForURI(config.server)
			resource = resourceManager.getResource(buildTag, buildId, resourceType, extraText)
			notEnd = False
			return resource
		except Pyro.errors.ProtocolError:
			time.sleep(10)
			continue
		except Pyro.errors.TimeoutError:
			time.sleep(10)
			continue
		except Pyro.errors.ConnectionClosedError:
			time.sleep(10)
			continue
		except Pyro.errors.ConnectionDeniedError:
			time.sleep(10)
			continue
		
def remoteResourceRelease(resourceName):
	resourceManager = Pyro.core.getProxyForURI(config.server)
	resourceManager.releaseResource(resourceName)


def main():
	print "This runs in an infinite loop, ctrl c to kill it"
	while(1):
		resource = remoteResourceGet('test','test', 'newnode', 'this is a test')
		print "I have resource %s"%resource
		resource2 = remoteResourceGet('test','test', 'newnode', 'this is a test')
		print "I have resource %s"%resource2
		remoteResourceRelease(resource)
		print "I have released %s"%resource
		remoteResourceRelease(resource2)
		print "Ihave release %s"%resource2


if __name__ == "__main__":
	main()



