#!/usr/bin/env python

import mvl
a = mvl.update(-1)
a.pushToTesting(403)
a.pushToLive(403)
#.removeFromLive()
#.removeFromTesting()
