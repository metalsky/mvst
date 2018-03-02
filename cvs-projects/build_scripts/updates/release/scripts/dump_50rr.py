#! /usr/bin/env python

import sys
import cPickle

sys.path.append("../update")
import db



mydb = db.db()

if len(sys.argv) < 3 or len(sys.argv) > 4:
	print "usage: dump_50rr.py <cycle_id> <outfile> [excludes file]"
	sys.exit(1)

release_id = int(sys.argv[1])


excludes = ""
if len(sys.argv) == 4:
	ex_filename = sys.argv[3]
	fe = open(ex_filename, "r")
	excludes = fe.read()
	fe.close()


mydb.Connect()

result = mydb.Command('''SELECT * FROM ReleaseAutomation.merged WHERE release_cycle_id=%d and products_id IN (1,2,3,16,17)'''%(release_id))

if not result:
	print "No updaes in cycle"
	sys.exit(1)

merged_list = result

updates = []

print "%20s\t%12s\t%12s\t"%("UPATE", "PRODUCT_ID", "MERGED_ID")
for merged in merged_list:
	merged_id = int(merged['id'])
	name = merged['name']
	product_id = int(merged['products_id'])


	if merged['name'] not in excludes:
		print "%20s\t%12d\t%12d"%(name, product_id, merged_id)
		updates.append((name, product_id, merged_id))
#end

mydb.Close()

data = {}
data['updates'] = updates

file = open(sys.argv[2], "w")
cPickle.dump(data, file, cPickle.HIGHEST_PROTOCOL)
file.close()

