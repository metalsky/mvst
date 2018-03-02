#!/usr/bin/env python
import sys
sys.path.append("../update")
import db 


if len(sys.argv) == 1:
	print 'Usage:  ./remove_updates_list <merged_id> <merged_id> ...'
	sys.exit(0)
	
for arg in sys.argv[1:]:

	highbuild = 0
	fileList = []
	mydb = db.db()
	mydb.Connect()
	try:
		productID = mydb.Command("Select products_id from ReleaseAutomation.merged where id=%s" % arg)[0]['products_id']
	except:
		raise Exception, "You have selected an invalid update ID: %s" % arg
	combinedResult = mydb.Command("Select * from ReleaseAutomation.combined where merged_id=%s" % arg)
	for combined in combinedResult:
		requestResult = mydb.Command("SELECT * FROM ReleaseAutomation.release_request WHERE combined_id=%s" % combined['id'])
		for request in requestResult:
			if int(request['builds_id']) > highbuild:
				highbuild = int(request['builds_id'])
			if request['type'] == 'target':
				table = 'target'
			elif request['type'] in ['host', 'host-tool', 'common']:
				table = 'host'
			elif request['type'] == 'cross':
				table = 'cross'

			fnResult = mydb.Command("SELECT name from Builds.%sRpms r, Builds.%sMap m WHERE m.%sPkgs_id = %s and r.%sMap_id = m.id" % (table, table, table, request['package_id'], table))
			for filename in fnResult:
				if '.src.rpm' in filename['name'] and filename['name'] not in fileList:
					fileList.append(filename['name'])

	for file in fileList:
		if str(highbuild) in file:
			print "./remove_update %s %s" % (productID, file[:-8])




