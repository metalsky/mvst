#! /usr/bin/env python

import sys, os
import cPickle

sys.path.append("../update")
import mvlapt as apt


if len(sys.argv) == 4:
	data = {}
	data['updates'] = [(sys.argv[1], sys.argv[2], sys.argv[3])]
elif len(sys.argv) == 2 and sys.argv[1].find("--help") == -1:
	file = open(sys.argv[1], "r")
	data = cPickle.load(file)
	file.close()
else:
	print "usage: push_50rr.py <info_file | update_info>"
	print "        info_file     = pickle file produced from dump_50rr.py"
	print "        updates_info  = <name> <product_id> <merged_id>"
	print ""
	sys.exit(1)
	

for entry in data['updates']:
	sys.stdout.write("Uploading %s..."%(entry[0]))
	sys.stdout.flush()
	u = apt.update(entry[1])
	u.pushToTesting(entry[2])
	print "Done!"
#end

