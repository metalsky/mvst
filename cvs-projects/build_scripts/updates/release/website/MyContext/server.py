#! /usr/bin/env python


import MySQLdb

class server:
	######################
	# databse FUNCTIONS  #
	######################
	def __init__(self):
		self.DB_HOST = 'overlord.borg'
		self.DB_USER = 'releaseweb'
		self.DB_PASSWORD = 'releaseweb'
		self.DB_DB = ''

		self.DB_CURSOR = None
		self.DB_SERVER = None

	def Connected(self):
		if not self.DB_CURSOR:
			return False
		
		if not self.DB_SERVER:
			return False

		
		#More checks?

		return True
	#End Connected
		


	def Connect(self):
		''' Connects to Build Database. returns error string or None'''
		# This goes? 
		#global DB_CURSOR, DB_SERVER
		
		if self.Connected():
			return None
		try:
			server = MySQLdb.connect(self.DB_HOST, self.DB_USER, self.DB_PASSWORD, self.DB_DB)
			server.autocommit(1)
			cursor = server.cursor(MySQLdb.cursors.DictCursor)
		except:
			return "Can't connect to MySQL database"
		
		self.DB_SERVER = server
		self.DB_CURSOR = cursor

		if not self.DB_CURSOR:
			return "Can't get cusror from MySQL databse"
		
		return None
	#end dbConnect


	def Close(self):
		'''Closes the connection to the Build Database. returns None'''
		# This goes?
		#global DB_SERVER, DB_CURSOR
		
		
		if self.Connected():
			self.DB_CURSOR.close()
			self.DB_SERVER.close()

		self.DB_SERVER = None
		self.DB_CURSOR = None
	#end dbClose



	def Command(self,cmd):
		'''Executes the given MySQL command, and returns the result.
			cmd = string, a format MySQL command
		'''
		try:
			ret = self.DB_CURSOR.execute(cmd)
			result = self.DB_CURSOR.fetchall()
		except:
			return "Error executing the following MySQL command:\n"+str(cmd)
		
		return result
	#end dbCommand

	def Start(self):
                '''starts a transaction'''

                self.DB_SERVER.autocommit(0)
                self.Command('''START TRANSACTION''')
        #end Start


        def Commit(self):
                '''commits a transaction'''

                self.Command('''COMMIT''')
                self.DB_SERVER.autocommit(1)
        #end Commit

        def Rollback(self):
                '''Rollback a transaction'''
                if self.Connected():
                        self.Command('''ROLLBACK''')
                        self.DB_SERVER.autocommit(1)
	#end Rollback	
#end db


######################
#   main FUNCTION    #
######################

def main(argv):
	import sys
        sys.stderr.write("This module is not designed to be called directly\n")
        sys.exit(1)


if __name__ == "__main__":
        main(sys.argv)

