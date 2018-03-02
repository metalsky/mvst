#!/usr/bin/python

SERVER_MODULE_PATH = "/var/www/release/site/MyContext/"

import MySQLdb, sys
sys.path.append(SERVER_MODULE_PATH)
import server

def queryDB(db, selectArg, fromArg, whereArg, where):
	if type(where) == str:
		appendString = whereArg + "=" + where[:]

	elif type(where) == list:
		appendString = "("
		for cycle in where:
			appendString += "%s=%s OR " % (whereArg,str(cycle))
		appendString = appendString[:-4] + ")"

	return db.Command('''SELECT %s FROM %s WHERE %s''' % (selectArg, fromArg, appendString)) 

#end def queryDB

def main():

	db = server.server()

	try: db.Connect()
	except: 
		print "Could not connect to database.  Aborting"
		sys.exit(1)
	
	#result = db.Command('''SELECT id FROM release_cycle WHERE processed="N"''')
	#cycleResults = map(lambda x: int(x['id']), result)
	#result = db.Command('''SELECT id FROM merged WHERE %s''' % (appendString))
	#return result

	result = queryDB(db, 'id', 'release_cycle', 'processed', '"N"')
	idList = map(lambda x: int(x['id']), result)

	result = queryDB(db, 'id', 'merged', 'release_cycle_id', idList)
	idList = map(lambda x: int(x['id']), result)

	result = queryDB(db, 'id', 'combined', 'merged_id', idList)
	idList = map(lambda x: int(x['id']), result)

	result = queryDB(db, 'build_id', 'release_request', 'combined_id', idList)
	idList = map(lambda x:int(x['build_id']), result)

	result = queryDB(db, 'tag', 'build', 'id', idList)
	resultList = map(lambda x: str(x['tag']), result)

	for result in resultList:
		print result

if __name__ in ['__main__']:
	main()

