#! /usr/bin/env python

import MySQLdb
import aspects

######################
#  database GLOBALS  #
######################
DB_HOST = 'overlord.borg'
DB_USER = 'support'
DB_PASSWORD = 'support'
DB_DB = ''



######################
# databse FUNCTIONS  #
######################
def dbConnectionWrapper(self, *args, **keyw):
        ''' 
	This wrapps around method calls opening and closing the database so
	that the code is not littered with it.
	'''
        stack_entry = self.__proceed_stack[-1]
	#1rst or later method call
        if self._db == None:
		####print "$$$$$ New db connection:", stack_entry.name
		sqldb = db()
        	sqldb.Connect()
        	self._db = sqldb

        	#exec method call
        	try:
                	ret = self.__proceed(*args, **keyw)
        	finally:
                	#cleanup
			####print "$$$$$ Closing connection:", stack_entry.name
                	sqldb.Close()
			self._db = None
	else:
		#later calls (we only conncet to the first method call into our
		#class
		####print "##### resuse db connection:", stack_entry.name
		ret = self.__proceed(*args, **keyw)

        return ret
#end dbConnectionWrapper



class connection:
	'''
	Inherit from this class to have all your code automatically connect 
	and close its database connections. Just call self.dbCommand(cmd) 
	to execute mysql queries. Any class that inherits from this and 
	calls db.connection.__init__() will be wrapped with a database 
	connection.
	
	When a class inherts from this connection class and from other 
	classes that inherit fro this class, the connection will be properly 
	handled, and only the highest level calls will create new 
	connections. All other methods will reuse the connection when 
	possible.
	'''
	def __init__(self):
		self._db = None
		for member in dir(self):
			#these checks help make sure we are wrapping normal exported methods
			#we dont want to wrap stuf like __init__ or already instanciated methods
			if str(member)[0].isalpha():
				real = getattr(self, member)
				if callable(real):
					aspects.wrap_around(real, dbConnectionWrapper)
					
		return
	
	def dbCommand(self, cmd):
		return self._db.Command(cmd)
#end connection



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
			raise Error("Can't connect to MySQL database")
	

		if not self.Cursor:
			raise Error("Can't get cusror from MySQL databse")
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
		if not self.Server or not self.Cursor:
			raise Error("Not connected to database")


		ret = self.Cursor.execute(cmd)
		result = self.Cursor.fetchall()
	
		return result
	#end Command
	
	def Start(self):
		'''starts a transaction'''

		self.Server.autocommit(0)
		self.Command('''START TRANSACTION''')
	#end Start


	def Commit(self):
		'''commits a transaction'''

		self.Command('''COMMIT''')
		self.Server.autocommit(1)
	#end Commit

	def Rollback(self):
		'''Rollback a transaction'''
		if self.Connected():
			self.Command('''ROLLBACK''')
			self.Server.autocommit(1)
	#end Rollback


#end db




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

