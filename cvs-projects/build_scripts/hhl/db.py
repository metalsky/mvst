#! /usr/bin/env python

import MySQLdb
import re
TAG_MATCH_RE = re.compile("[0-9]+[0-9]_[0-9]+[0-9]")



######################
#  database GLOBALS  #
######################
DB_HOST = 'overlord.borg'
DB_USER = 'collective'
DB_PASSWORD = 'collective'
DB_DB = ""



############################
# databse connection class #
############################
class db:
	def __init__(self):
		self.Cursor = None
		self.Server = None
		return

	def Connect(self):
		''' Connects to Build Database. returns None'''

		if self.Connected():
			return

		try:
			self.Server = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_DB)
			self.Server.autocommit(1)
			self.Cursor = self.Server.cursor(MySQLdb.cursors.DictCursor)
		except:
			self.Error("Can't connect to MySQL database")
	

		if not self.Cursor:
			self.Error("Can't get cusror from MySQL databse")
	#end Connect



	def Connected(self):
		if not self.Server:
			return False
		if not self.Cursor:
			return False
	
		return True
	#end Connected



	def Close(self):
		'''Closes the connection to the Build Database. returns None'''
		
		if self.Server and self.Cursor:
			self.Cursor.close()
			self.Server.close()
	
		self.Server = None
		self.Cursor = None
	#end Close


	def Command(self, cmd):
		'''Executes the given MySQL command, and returns the result.
			cmd = string, a format MySQL command
		'''
		print cmd	
		if not self.Server or not self.Cursor:
			self.Error("Not connected to database")


		ret = self.Cursor.execute(cmd)
		result = self.Cursor.fetchall()
		##raise Error("Error executing the following MySQL command:\n"+str(cmd))
	
		return result
	#end Command

	def Start(self):
		'''starts a transaction'''
		
		self.Server.autocommit(0)
		#Collective interface needs to be set read-uncommitted
		#self.Command('''SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED''') 
		self.Command('''START TRANSACTION''')
	#end Start


	def Commit(self):
		'''commits a transaction'''

		self.Command('''COMMIT''')
		self.Server.autocommit(1)
	#end Commit


	def Rollback(self):
		'''Rollsback a transaction'''
		self.Command('''ROLLBACK''')
		self.Server.autocommit(1)
	#end Rollback


	def Error(self, msg):
		self.Rollback()
		raise Error(msg);

#end db






class database(db):
	def getBuildProduct(self, BuildTag):
		'''returns the product that matches the build'''

		match_obj = TAG_MATCH_RE.search(BuildTag, 0)

		if BuildTag[:5] == 'f2624':
		    match = 'f2624'
		elif BuildTag[:6] == 'fp2624':
		    match = 'fp2624'
		elif BuildTag[:5] == 's127p':
		    match = 's127p4080_'		 
		elif match_obj:
			match = BuildTag[:match_obj.start(0)]
		else:
			return None


		print '*'
		print match
		print '*'
		result = self.Command('''SELECT * FROM BuildCfg.products WHERE tag_match="%s"'''%(match))
		if len(result) > 0:
			return result[0]
	

		return None
	#end getBuildProduct


	def getBuild(self, BuildID):
		'''Return Build if its in the database, and None otherwise'''

		result = self.Command('''SELECT * FROM Builds.builds WHERE id=%d'''%(int(BuildID)))
		if len(result) > 0:
			return result[0]
		return None
	#end buildExists


	def insertBuild(self, BuildID, BuildTag, BuildPath):
		'''insert a new entry into the build, returns the id once its in the db,
		otherwise None on failure'''
	
		print 'Inside insertBuild'

		#make sure build isn't already there
		if self.getBuild(BuildID):
			print 'Build in DB, not inserting'
			return BuildID 

		#find a product for the build:
		product = self.getBuildProduct(BuildTag)
		if not product:
			print 'No corresponding product found.  Not inserting into db'
			return None

		cmd = '''INSERT INTO Builds.builds (id, products_id, buildtag, path) VALUES (%d, %d, "%s", "%s")'''%(int(BuildID), product['id'], BuildTag, BuildPath)
		print cmd
		result = self.Command(cmd)

		return BuildID
	#end insertBuild

		
	
	def _getPkgField(self, packageType, tableType):
		if packageType in ["host-tool", "common", "host"]:
			return "host"+tableType
		elif packageType == "cross":
			return "cross"+tableType
		elif packageType == "target":
			return "target"+tableType
		
		return ""
	#end _getPkgField

	
	def _getPkgTable(self, packageType, tableType):
		return "Builds."+self._getPkgField(packageType, tableType)
	#end _getPkgTable
	

	def getPackageTable(self, packageType):
		'''return table name for packageType'''
		return self._getPkgTable(packageType, "Pkgs")
	#end getPackageTable


	def getPackageField(self, packageType):
		'''returns the field name for a packageType'''
		return self._getPkgField(packageType, "Pkgs")+"_id"
	#end getPackageField


	def getRpmTable(self, packageType):
		'''returns the table name for packageType'''
		return self._getPkgTable(packageType, "Rpms")
	#end getRpmTable


	def getRpmField(self, packageType):
		'''returns the field name or the packageType'''
		return self._getPkgField(packageType, "Rpms")+"_id"
	#end getRpmField


	def getPackageMapTable(self, packageType):
		'''return Map table name for packageType'''
		return self._getPkgTable(packageType, "Map")
	#end getPackageMapTable


	def getPackageMapField(self, packageType):
		'''return Map field name for packageType'''
		return self._getPkgField(packageType, "Map")+"_id"
	#end getPackageMapTable


	def getPackage(self, name, packageType, buildID):
		'''returns the package if it exists, None otherwise'''
		
		table = self.getPackageTable(packageType)
		result = self.Command('''SELECT * FROM %s WHERE name="%s" AND builds_id=%d'''%(table, name, buildID))
		
		if len(result) > 0:
			return result[0]
		
		return None
	#end getPackage



	def insertPackage(self, name, packageType, buildID):
		'''inserts the package into the database, returns the id once its in the db, 
		or None on failure.'''


		#make sure pkg isn't already there
		pkg = self.getPackage(name, packageType, buildID)
		if pkg:
			return pkg['id']

		#insert
		table = self.getPackageTable(packageType)
		if packageType in ["host-tool", "common", "host"]:
			result = self.Command('''INSERT INTO %s (name, builds_id, type) VALUES ("%s", %d, "%s")'''%(table, name, buildID, packageType))
		else:
			result = self.Command('''INSERT INTO %s (name, builds_id) VALUES ("%s", %d)'''%(table, name, buildID))
		
		result = self.Command('''SELECT LAST_INSERT_ID()''')
		if result:
			return result[0]['LAST_INSERT_ID()']

		return None
	#end insertPackage
	


	def getPackageMap(self, packageID, packageType, archID, hostID):
		'''returns the package if it exists, None otherwise'''
		
		table = self.getPackageMapTable(packageType)
		field = self.getPackageField(packageType)
	
		if packageType == "target":
			result = self.Command('''SELECT * FROM %s WHERE %s=%d AND archs_id=%d'''%(table, field, packageID, archID)) 
		elif packageType == "cross":
			result = self.Command('''SELECT * FROM %s WHERE %s=%d AND archs_id=%d and hosts_id=%d'''%(table, field, packageID, archID, hostID))
		else:
			result = self.Command('''SELECT * FROM %s WHERE %s=%d AND hosts_id=%d'''%(table, field, packageID, hostID))
		
		if len(result) > 0:
			return result[0]

		return None
	#end getPackageMap



	def insertPackageMap(self, name, packageType, archID, hostID, buildID):
		'''inserts the packageMap into the database, returns the id once its in the db, 
		or None on failure'''

		#find or insert a package
		package = self.getPackage(name, packageType, buildID)
		if not package:
			packageID = self.insertPackage(name, packageType, buildID)
			if not packageID:
				self.Error("Can't insert package: %s, type: %s, buildID: %d"%(name, packageType, buildID))
		else:
			packageID = package['id']


		#see if pcakageMap already exists
		pkg = self.getPackageMap(packageID, packageType, archID, hostID)
		if pkg:
			return pkg['id']

		#insert
		table = self.getPackageMapTable(packageType)
		pkgField = self.getPackageField(packageType)
		if packageType == "target":
			result = self.Command('''INSERT INTO %s (%s, archs_id, builds_id) VALUES (%d, %d, %d)'''%(table, pkgField, packageID, archID, buildID))
		
		elif packageType == "cross":
			result = self.Command('''INSERT INTO %s (%s, archs_id, hosts_id, builds_id) VALUES (%d, %d, %d, %d)'''%(table, pkgField, packageID, archID, hostID, buildID))

		elif packageType in ["host-tool", "common", "host"]:
			result = self.Command('''INSERT INTO %s (%s, hosts_id, builds_id) VALUES (%d, %d, %d)'''%(table, pkgField, packageID, hostID, buildID))

		else:
			return None

		result = self.Command('''SELECT LAST_INSERT_ID()''')
		if result:
			return result[0]['LAST_INSERT_ID()']

		return None
	#end insertPackageMap


	def updatePackageMapHost(self, packageType, packageMapID, hostID):
		'''update the host_id for the packageMap.'''

		table = self.getPackageMapTable(packageType)
		result = self.Command('''UPDATE %s SET hosts_id=%d WHERE id=%d'''%(table, hostID, packageMapID))
		return
	#end updatePackageMapHost
	

	def setPackageMapBuilt(self, packageType, packageMapID):
		'''mark a package as built'''

		table = self.getPackageMapTable(packageType)
		result = self.Command('''UPDATE %s SET built="Y" WHERE id=%d'''%(table, packageMapID))
		return
	#end setPackageMapBuilt
	

	def getRpm(self, name, packageMapID, packageType):
		'''returns the rpm if it exists, or None if not'''
		
		table = self.getRpmTable(packageType)
		pkgMapField = self.getPackageMapField(packageType)
		result = self.Command('''SELECT * FROM %s WHERE %s=%d AND name="%s"'''%(table, pkgMapField, packageMapID, name))

		if len(result) > 0:
			return result[0]

		return None
	#end getRpm



	def insertRpm(self, name, packageMapID, packageType, archID, hostID, buildID):
		'''inserts the rpm into the database, returns the id once its in the db, 
		or None on failure'''

		#find or inster the rpm
		rpm = self.getRpm(name, packageMapID, packageType)
		if rpm:
			return rpm['id']

		#insert
		table = self.getRpmTable(packageType)
		pkgMapField = self.getPackageMapField(packageType)
		result = self.Command('''INSERT INTO %s (%s, name, builds_id) VALUES (%d, "%s", %d)'''%(table, pkgMapField, packageMapID, name, buildID))

		result = self.Command('''SELECT LAST_INSERT_ID()''')
		if result:
			return result[0]['LAST_INSERT_ID()']

		return None
	#end insertRpm


	def getHost(self, name, productID):
		'''returns the host given a name and productID, otherwise returns None'''
		
		if name == "src":
			name = "SRC"

		result = self.Command('''SELECT * FROM BuildCfg.hosts WHERE products_id=%d AND name="%s"'''%(productID, name))

		if len(result) > 0:
			return result[0]


		print 'Returning None in getHost.  name=%s ID=%s' % (name, productID)
		return None
	#end getHost


	def getArch(self, name, productID):
		'''returns the arch given a name and productID, otherwise returns None'''

		if name == "src":
			name = "SRC"


		result = self.Command('''SELECT * FROM BuildCfg.archs WHERE products_id=%d AND name="%s"'''%(productID, name))


		if len(result) > 0:
			return result[0]

		print 'returning none'
		return None
	#end getArch


	def getPackageType(self, packageName):
		'''returns the package type from the package name'''

		if packageName.find("cross-") == 0:
			return "cross"
		elif packageName.find("common-") == 0:
			return "common"
		elif packageName.find("host-tool-") == 0:
			return "host-tool"
		elif packageName.find("host-") == 0:
			return "host"
		else:
			return "target"
	#end getPackageType
#end database




######################
#  helper FUNCTIONS  #
######################

class Error(Exception):
	pass




######################
#   main FUNCTION    #
######################

def main(argv):
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)


if __name__ == "__main__":
        main(sys.argv)
