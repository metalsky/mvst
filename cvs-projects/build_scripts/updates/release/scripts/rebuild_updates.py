#! /usr/bin/env python


import sys

sys.path.append("../update")
import update



if len(sys.argv) != 3:
	print "usage: %s <product_id> <type>"%(sys.argv[0])
	print ""
	sys.exit(1)
#else

u = update.update(int(sys.argv[1]))
u.rebuildTesting(sys.argv[2])


