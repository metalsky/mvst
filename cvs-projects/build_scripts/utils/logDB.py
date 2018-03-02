#! /usr/bin/env python

import server
import time

def _show(mytype,myvalue):
	if myvalue == None:
		return "NULL"
	elif not (type(myvalue) == mytype):
		raise Exception,"logDB error, wrong value type in _show(%s,%s)" % (mytype,myvalue)
	elif mytype == long:
		return "%d" % myvalue
	elif mytype == str:
		return "'%s'" % myvalue
	else:
		raise Exception,"logDB error, don't know how to _show(%s,%s)" % (mytype,myvalue)
def _extractFirstLong(answer,tag):
	if not (type(answer) == tuple and len(answer) > 0 and type(answer[0]) == dict):
		return None
	else:
		result = answer[0][tag]
		if type(result) == long:
			return result
		else:
			return None
def _extractFirstLongOrDie(answer,tag,calling_context):
	result = _extractFirstLong(answer,tag)
	if type(result) == long:
		return result
	else:
		raise Exception,( "logDB: cmd failed to return an extractable long:\n"
						+ "  call was to:       %s\n" % calling_context
						+ "  query result was:  %s\n" % answer
						)

class logDB:
	def __init__(self,db):
		self.DB = db
	def getDB(self):
		return self.DB
##mysql> DELETE FROM DynamicBuilds.Builds; ALTER TABLE DynamicBuilds.Builds AUTO_INCREMENT = 1;
##mysql> DELETE FROM DynamicBuilds.Applications; ALTER TABLE DynamicBuilds.Applications AUTO_INCREMENT = 1;
##mysql> DELETE FROM DynamicBuilds.Archs; ALTER TABLE DynamicBuilds.Archs AUTO_INCREMENT = 1;
##mysql> DELETE FROM DynamicBuilds.Hosts; ALTER TABLE DynamicBuilds.Hosts AUTO_INCREMENT = 1;

##mysql> DESCRIBE DynamicBuilds.Archs;
##+-----------+------------------+------+-----+---------+----------------+
##| Field     | Type             | Null | Key | Default | Extra          |
##+-----------+------------------+------+-----+---------+----------------+
##| id        | int(10) unsigned | NO   | PRI | NULL    | auto_increment | 
##| name      | varchar(255)     | NO   |     |         |                | 
##| builds_id | int(10) unsigned | NO   |     |         |                | 
##+-----------+------------------+------+-----+---------+----------------+
##type(answer) = <type 'tuple'>
##type(answer[0]) = <type 'dict'>
##type(answer[0]['id']) = <type 'long'>
	def _archID(self,name,builds_id):
		calling_context = "_archID(self,%s,%s)" % (name,builds_id)
		if name == None:
			return None
		answer = self.DB.Command("SELECT id from DynamicBuilds.Archs WHERE name='%s' && builds_id=%d;" % (name,builds_id))
		result = _extractFirstLong(answer,'id')
		if type(result) == long:
			return result
		else:
			self.DB.Command("INSERT INTO DynamicBuilds.Archs (name,builds_id) VALUES ('%s',%d);" % (name,builds_id))
			answer = self.DB.Command("SELECT last_insert_id();")
			return _extractFirstLongOrDie(answer,'last_insert_id()',calling_context)
	def _deleteArchByBuildsId(self,builds_id):
		'''Removes a build from DynamicBuilds.Archs.'''
		self.DB.Command("DELETE FROM DynamicBuilds.Archs WHERE builds_id='%s';" % builds_id)
		return
##mysql> DESCRIBE DynamicBuilds.Hosts;
##+-----------+------------------+------+-----+---------+----------------+
##| Field     | Type             | Null | Key | Default | Extra          |
##+-----------+------------------+------+-----+---------+----------------+
##| id        | int(10) unsigned | NO   | PRI | NULL    | auto_increment | 
##| name      | varchar(255)     | NO   |     |         |                | 
##| builds_id | int(10) unsigned | NO   |     |         |                | 
##+-----------+------------------+------+-----+---------+----------------+
	def _hostID(self,name,builds_id):
		calling_context = "_hostID(self,%s,%s)" % (name,builds_id)
		if name == None:
			return None
		answer = self.DB.Command("SELECT id from DynamicBuilds.Hosts WHERE name='%s' && builds_id=%d;" % (name,builds_id))
		result = _extractFirstLong(answer,'id')
		if type(result) == long:
			return result
		else:
			self.DB.Command("INSERT INTO DynamicBuilds.Hosts (name,builds_id) VALUES ('%s',%d);" % (name,builds_id))
			answer = self.DB.Command("SELECT last_insert_id();")
			return _extractFirstLongOrDie(answer,'last_insert_id()',calling_context)
	def _deleteHostByBuildsId(self,builds_id):
		'''Removes a build from DynamicBuilds.Hosts.'''
		self.DB.Command("DELETE FROM DynamicBuilds.Hosts WHERE builds_id='%s';" % builds_id)
		return
##mysql> DESCRIBE DynamicBuilds.Builds;
##+------------+------------------+------+-----+---------+----------------+
##| Field      | Type             | Null | Key | Default | Extra          |
##+------------+------------------+------+-----+---------+----------------+
##| id         | int(10) unsigned | NO   | PRI | NULL    | auto_increment | 
##| buildtag   | varchar(255)     | NO   |     |         |                | 
##| finished   | tinyint(1)       | YES  |     | 0       |                | 
##| start_time | datetime         | NO   |     |         |                | 
##| end_time   | datetime         | YES  |     | NULL    |                | 
##+------------+------------------+------+-----+---------+----------------+
	def addBuild(self,buildtag,date=None):
		'''Adds a build to the database. Queries BuildCfg to get
		released architectures for the product and populates the
		Architectures table as well. Probably best to daisy-chain
		this from the buildid rather than using tag_match'''
		calling_context = "addBuild(self,%s,%s)" % (buildtag,date)
		if date == None:
			date = time.strftime("%Y-%m-%d %H:%M:%S")
                self.DB.Command("INSERT INTO DynamicBuilds.Builds "
				+ "(buildtag,start_time) VALUES ('%s','%s') " % (buildtag,date)
				+ ";")
		answer = self.DB.Command("SELECT last_insert_id();")
		return _extractFirstLongOrDie(answer,'last_insert_id()',calling_context)
	def finishBuild(self,builds_id,date=None):
		'''Mark a build as finished.'''
		if date == None:
			date = time.strftime("%Y-%m-%d %H:%M:%S")
		self.DB.Command("UPDATE DynamicBuilds.Builds "
				+ "SET finished=1,end_time='%s' " % date
				+ "WHERE id='%s' " % builds_id
				+ ";")
		return
	def removeBuild(self,builds_id):
		'''Removes a build from the database.'''
		self.DB.Command("DELETE FROM DynamicBuilds.Builds WHERE id='%s';" % builds_id)
		## oops, this is a diamond shaped DAG, so is unsafe
		self._deleteAppByBuildsId(builds_id)
		self._deleteTaskByBuildsId(builds_id)
		self._deleteHostByBuildsId(builds_id)
		self._deleteArchByBuildsId(builds_id)
		return
	def pruneBuilds(self,numDays):
		'''Delete all builds older than numDays'''
		return
##mysql> DESCRIBE DynamicBuilds.Applications;
##+-------------+------------------+------+-----+---------+----------------+
##| Field       | Type             | Null | Key | Default | Extra          |
##+-------------+------------------+------+-----+---------+----------------+
##| id          | int(10) unsigned | NO   | PRI | NULL    | auto_increment | 
##| name        | varchar(255)     | NO   |     |         |                | 
##| type        | varchar(255)     | NO   |     |         |                | 
##| builds_id   | int(10) unsigned | NO   |     |         |                | 
##| archs_id    | int(10) unsigned | YES  |     | NULL    |                | 
##| hosts_id    | int(10) unsigned | YES  |     | NULL    |                | 
##| state       | varchar(255)     | NO   |     |         |                | 
##| log_link    | varchar(255)     | NO   |     |         |                | 
##| start_time  | datetime         | YES  |     | NULL    |                | 
##| finish_time | datetime         | YES  |     | NULL    |                | 
##| buildhost   | varchar(255)     | YES  |     | NULL    |                | October 17, 2008
##+-------------+------------------+------+-----+---------+----------------+
	def addApp(self,name,atype,builds_id,arch,host,buildhost,log_link=''):
		'''Add an application with status "Pending"'''
		calling_context = "addApp(self,%s,%s,%s,%s,%s)" % (name,atype,builds_id,arch,host)
		archs_id = self._archID(arch,builds_id)
		hosts_id = self._hostID(host,builds_id)
                self.DB.Command("INSERT INTO DynamicBuilds.Applications "
				+ "(        state,     name, type,  builds_id, archs_id,             hosts_id,             log_link, buildhost) "
				+ "VALUES ( '%s',      '%s', '%s',  %d,        %s,                   %s,                   '%s',     %s) "
				% (         'Pending', name, atype, builds_id, _show(long,archs_id), _show(long,hosts_id), log_link, _show(str,buildhost))
				+ ";" )
		answer = self.DB.Command("SELECT last_insert_id();")
		return _extractFirstLongOrDie(answer,'last_insert_id()',calling_context)
	def startApp(self,apps_id,date=None):
		'''Given the buildid and the name of the arch, add a row to
		to the Applications table with status "Building"'''
		if date == None:
			date = time.strftime("%Y-%m-%d %H:%M:%S")
		status = "Building"
		self.DB.Command("UPDATE DynamicBuilds.Applications "
				+ "SET state='%s', start_time='%s' " % (status,date)
				+ "WHERE id='%s' " % apps_id
				+ ";" )
	def finishApp(self,apps_id,status,date=None):
		'''Update an application with status of Failed or Built, as
		well as a URL to the log.'''
		if date == None:
			date = time.strftime("%Y-%m-%d %H:%M:%S")
		self.DB.Command("UPDATE DynamicBuilds.Applications "
				+ "SET state='%s', finish_time='%s' " % (status,date)
				+ "WHERE id='%s' " % apps_id
				+ ";" )
	def _deleteAppByBuildsId(self,builds_id):
		'''Removes a build from DynamicBuilds.Applications.'''
		self.DB.Command("DELETE FROM DynamicBuilds.Applications WHERE builds_id='%s' AND type != 'task';" % builds_id)
	def addTask(self,name,builds_id,arch,host,buildhost,log_link=''):
		'''Add a task.'''
		return self.addApp(name,'task',builds_id,arch,host,buildhost,log_link)
	def startTask(self,tasks_id,date=None):
		'''Set the starting timestamp of a task.'''
		self.startApp(tasks_id,date)
	def finishTask(self,tasks_id,status,date=None):
		'''Mark a task with status of Failed or Built, and set its finishing timestamp'''
		self.finishApp(tasks_id,date)
	def _deleteTaskByBuildsId(self,builds_id):
		'''Removes a task from DynamicBuilds.Applications.'''
		self.DB.Command("DELETE FROM DynamicBuilds.Applications WHERE builds_id='%s' AND type = 'task';" % builds_id)
#end logDB

######################
#   main FUNCTION    #
######################

def main(argv):
	import sys
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)

if __name__ == "__main__":
        main(sys.argv)
