#! /usr/bin/env python

import sys
sys.path.append("../update")

import update


if len(sys.argv) != 3:
	print "usage: add_arch.py <product_id> <arch_id>"
	print ""
	sys.exit(1)
#else


u = update.update(int(sys.argv[1]))
u.releaseNewTestArch(int(sys.argv[2]))

