#! /usr/bin/env python

#
#  FILE:  parser
#
#  DESCRIPTION:
#    This file has the parsers and related functions for the TASKS 
#    and RULES Lists.
#
#
#  AUTHOR:  MontaVista Software, Inc. <source@mvista.com>
#
#  Copyright 2006 MontaVista Software Inc.
#
#  This program is free software; you can redistribute  it and/or modify it
#  under  the terms of  the GNU General  Public License as published by the
#  Free Software Foundation;  either version 2 of the  License, or (at your
#  option) any later version.
#
#  THIS  SOFTWARE  IS PROVIDED   ``AS  IS'' AND   ANY  EXPRESS OR IMPLIED
#  WARRANTIES,   INCLUDING, BUT NOT  LIMITED  TO, THE IMPLIED WARRANTIES OF
#  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN
#  NO  EVENT  SHALL   THE AUTHOR  BE    LIABLE FOR ANY   DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
#  NOT LIMITED   TO, PROCUREMENT OF  SUBSTITUTE GOODS  OR SERVICES; LOSS OF
#  USE, DATA,  OR PROFITS; OR  BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#  ANY THEORY OF LIABILITY, WHETHER IN  CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
#  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#  You should have received a copy of the  GNU General Public License along
#  with this program; if not, write  to the Free Software Foundation, Inc.,
#  675 Mass Ave, Cambridge, MA 02139, USA.
#



import sys, os, copy, traceback
import error
import config
import task


#This is the main entry into the parser.
#its just a wrapper around parse
def parseTaskList():
	start_file = config.getUserTaskFile()
	if not os.path.isfile(start_file):
		error.fatalError(start_file + " Does not exist")
	return parse(start_file)
#end parseTaskList


def parse(file_name):
	task_list = []
	if not os.path.isfile(file_name):
		error.error( "File Not Found: " + file_name)
	else:
		file = open(file_name)
		try:
			task_list = parseFile(file, file_name)
		finally:
			file.close()
			
	return task_list
#End parse



#Recursive parser. This parses a file, and then calls itself on 
#any new files it finds while parsing
#
def parseFile(file, file_name):
	lines = file.readlines()
	task_list = []

	#for each line in the file
	for x in range(len(lines)):
		line = lines[x]
		name, fork, num, type, fatal = parseLine(line)
		
		if name == None:
			continue
		#Detect type by trying to find it as a task first:
		# if it exists:
		# if its a task list, then parse it
		# if its a real task, set it up
		

		#check common and user paths
		#we look in user lib first, then common lib
		common_lib_path = config.getCommonLibPath()
		user_lib_path = config.getUserLibPath()
	
		if not validPaths([user_lib_path]) and not validPaths([common_lib_path]):
			error.fatalError("Neither the common lib path: " + common_lib_path + \
				", or the user path: " + user_lib_path + ", exists")
		elif not validPaths([user_lib_path]):
			error.warning("User library path: " + user_lib_path + " does not exist")
		elif not validPaths([common_lib_path]):
			error.warning("Common library path: " + common_lib_path + " does not exist")
		
		
		#look for a task and try to import it 
		u_py_file, u_task_ptr = findTask(name, user_lib_path)
		c_py_file, c_task_ptr = findTask(name, common_lib_path)
		
		error.sysDebug("parseFile: user: "+ str(u_py_file)+", "+str(u_task_ptr))
		error.sysDebug("parseFile: common: "+ str(c_py_file)+", "+str(c_task_ptr))
		
		#did we find a py file?
		task_ptr = None
		if not u_py_file and not c_py_file:
			error.error("Task: " + name + " Does not exist")
			continue
		else:
			#choose a user task if one exists in multiple places
			if u_py_file == c_py_file and u_task_ptr and c_task_ptr:
				error.warning("Overriding common task with user task: " + \
					name + " from: " + u_py_file)
				py_file = u_py_file
				task_ptr = u_task_ptr
			elif u_py_file:
				py_file = u_py_file
				task_ptr = u_task_ptr
			else:
				py_file = c_py_file
				task_ptr = c_task_ptr
				
		#is this a list?
		if not task_ptr:
			task_ptr = parse(py_file)
		
		#Setup task
		error.sysDebug("parseFile: task_ptr: " + str(task_ptr))
		error.sysDebug("parseFile: " + name + " : fork= " + str(fork)) 
		if fork:
			fork_obj = task.ForkObj(fork, num, type)
		else:
			fork_obj = None
		task_item = task.Task(name, py_file, file_name, x+1, fork_obj, task_ptr, fatal)
		task_list.append(task_item)
		error.sysDebug("parseFile: adding task:" + name)
			
	return task_list
			
#End parseFile



#This parses a single line of the file. It handles interpreting the text.
def parseLine(line):
	name = None
	fork = None
	num = None
	type = None
	fatal = None
	tmp = line.split(None, 6)
	
	if len(line) < 1:
		return name, fork, num, type, fatal
	if line[0] == "#":
		return name, fork, num, type, fatal
	
	#Task Name
	if len(tmp) > 0:
		name = tmp[0]
	
	args = tmp[1:len(tmp)]

	x = 0
	while x < len(args):
		arg = args[x]
		
		#if Fatal
		if isFatal(arg):
			fatal = arg
			x = x+1
		#if Sync
		elif isSync(arg):
			fork = arg
			x = x+1
		#if Fork
		elif isFork(arg):
			if not len(args) - x >= task.FORK_ARGS:
				error.error("Not enough Fork arguments to: " + name)
				error.error("Fork args look like:  FORK <THREADS> <RESOURCE>")
				x = x+1
			else:
				fork = arg
				#Number of threads
				try:
					num = int(args[x+1])
				except:
					error.error("Number of threads: " + args[x+1] + " must be an integer")
			
				#Resource type:
				type = args[x+2]
				
				x = x+ task.FORK_ARGS
		#More args here
		else:
			error.error("Unknown task argument: " + arg + ", to task: " + name)
			x = x+1

	return name, fork, num, type, fatal
#End parseLine



#given a task file.name, this attempts to find that task in the file
#located either in the common path or the user path.
def findTask(name, path):
	error.sysDebug("findTask("+name+", "+path+")")
	tmp = name.split('.', 2)
	file_name = tmp[0]
	if len(tmp) > 1:
		#This is a function
		#Get global common path and user libs path
		function_name = tmp[1]
		if not validTaskName(function_name):
			error.error("task name: "+ function_name + " is not valid")
			return None, None

		full_path = os.path.join(path, file_name + ".py")
	
		if os.path.isfile(full_path):
			error.sysDebug("findTask: found task file")
			func = importTask(full_path, function_name)
			if func:
				error.sysDebug("findTask: imported task from file")
				return full_path, func
			else:
				error.sysDebug("findTask: couldn't import task from file")
				return None, None
		else:
			error.sysDebug("findTask: couldn't find task")
			return None, None
	else:
		#This is a task list
		#get task list path
		#search for task list
		user_path = config.getUserPath()
		if validPaths([user_path]):
			full_path = os.path.join(user_path, file_name + ".lst")
			if os.path.isfile(full_path):
				return full_path, None

	return None, None

#End findTask


def validPaths(path_list):
	for path in path_list:
		if not os.path.exists(path):
			return False
	
	return True
#end validPaths


def validTaskName(name):
	#return name.isupper()
	#We check for all uppercase in the rules
	return True
#end validTaskName


def isFork(arg):
	if arg == task.FORK:
		return True 
	return False
#End isFork

def isFatal(arg):
	if arg == task.FATAL:
		return True
	
	return False
#End isFatal


def isSync(arg):	
	if arg == task.SYNC:
		return True
	return False
#end isSync


def importTask(py_file, function):
	error.sysDebug("importTask('"+str(py_file)+"','"+str(function)+"')")
	
	path = os.path.dirname(py_file)
	mod_name = os.path.basename(py_file)
	mod_name = mod_name[0:-3]
	
	new_mod_name = py_file[0:-3]
	new_mod_name = new_mod_name.replace('/', '-', 200)
	
	saved_path = copy.deepcopy(sys.path)
	sys.path.append(path)
	
	error.sysDebug("importTask: Unique module name: "+new_mod_name)
	#Our module should now have a unique name even if the file exist in
	#both common and user locations
	
	try:
		module = __import__( mod_name, locals(), None, None)
		
		#rename modules
		sys.modules[new_mod_name] = module
		del(sys.modules[mod_name])
		
		#restore path
		sys.path = saved_path
		
		try:
			 func = getattr(module, function)
			 error.sysDebug("\t\tmodule="+str(module)+" function="+str(func))
			 return func
		except:
			error.sysDebug("\t\tFound module: "+mod_name+", but can't find function: " + function)
			return None
	
	except:
		sys.path = saved_path
		error.sysDebug("\t\tCan't import python module: " + mod_name)
		try:
			exc_type, exc_value, exc_tb = sys.exc_info()
			tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
			for tb in tb_list:
				m = tb.split('\n', 200)
				for i in m:
					error.sysDebug(i)
		finally:
			del(exc_tb)
		
	return None
#end importTask


def printTaskList(list, tab=""):
	for task in list:
		#tab = tab + "\t"	
		printTask(task, tab)
#end printTaskList


def printTask(task, tab=""):
	msg = tab
	if type(task.taskPtr) == type([]):
		msg = msg + task.name + ":LIST:"
	else:
		msg = msg + task.name + ":FUNC:"
	
	
	if task.forkObj:
		msg = msg + str(task.forkObj.forkOp)+":"
		if isFork(task.forkObj.forkOp):
			msg = msg + str(task.forkObj.numThrds)+":"+\
			str(task.forkObj.remoteType)+":"
	if isFatal(task.fatal):
		msg = msg + str(task.fatal)+":"
	

	msg = msg + task.taskFile + ","+str(task.taskLineNo) + ":"
	
	if type(task.taskPtr) == type([]):
		error.message(msg)
		printTaskList(task.taskPtr, tab+"\t")
	else:
		error.message(msg + task.pyFile)
#end printTask
		

def main():
	print "No manual execution of this module"
	sys.exit(1)

if __name__ == "__main__":
	main()
