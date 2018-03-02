#!/usr/bin/env python
import threading, time, os, server

class buildThread ( threading.Thread ):
	def run ( self ):
		os.system('/home/build/bin/launch.py --product mvl6 --build_script_branch HEAD --prefix %s_ --msd %s | tee /home/build/mvl6logs/%s-4.log' % ( self.MSD, self.MSD, self.MSD ))

def getmsds(id):
	db = server.server()
	db.Connect()
	results = db.Command('SELECT name FROM Mvl6Cfg.RequestedCollections WHERE type="kernel" AND breq_id=%s' % id)
	db.Close()
	return map(lambda x: str(x['name']), results)


#Automation -- Disable for staging builds of course.
msdList = getmsds(12)
print msdList

for inmsd in msdList:
	bt = buildThread()
	bt.MSD = inmsd
	bt.start()
	

		


