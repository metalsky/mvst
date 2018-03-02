#! /usr/bin/env python

import sys

sys.path.append("../update")
import mvlapt


if len(sys.argv) != 2:
	print "usage: create_repo.py <product_id>"
	print ""
	sys.exit(1)
#else

u = mvlapt.update(sys.argv[1])
u.createNewTestRepo()

