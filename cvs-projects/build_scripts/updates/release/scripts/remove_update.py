#! /usr/bin/env python


import sys

sys.path.append("../update")
import update



if len(sys.argv) != 3:
	print "usage: remove_update.py <product_id> <update_name>"
	print ""
	sys.exit(1)
#else

u = update.update(int(sys.argv[1]))
u.removeFromTesting(sys.argv[2])


