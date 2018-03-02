#!/usr/bin/python

#Third Party
import Pyro.core

#Standard
import os, sys, re, string, threading, Queue, traceback, time 
from types import *

#Custom
from releaseClass import *
import tasklist
from releaseLog import *

#Defines
VERBOSE = 1
Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
NUM_THREADS = 1
TASKSIZE=4 #defines the size of the task tuple, should we need to make one and make sure things are placed into the right indexes

QUIT = 'quit'
LOAD = 'load'
ALL = 'all'

NAME = 0  #method name
CLASS = 1 #class name
MODULE = 2 #position of module name
SCHEDULE = 3 #position of scheduling information

IMMEDIATE = "im"
BACKGROUND = "bg"

LOGSIZE = 5000000
NUMLOGS = 5


#Globals
queue = Queue.Queue()
schedulePool = {}
cmdDict = {}
cmdLock = threading.Lock()



#Errors
class VersionError(StandardError):
	pass


def system(cmd):
	if VERBOSE:
		sys.stdout.write('%s\n'%cmd)
	os.system(cmd)

def now():
	return time.strftime("%m/%d/%Y - %I:%M %p")

def flagError(job, errorMsg):
	logErr(errorMsg)
	return

def flagSuccess(job):
	pass


def doTask():
	while(1):
		logDebug('Trying to get work...')
		job = queue.get()
		logDebug('Work recieved....')
		if job.cmd == QUIT:
			logInfo('QUIT was recieved... exiting')
			return
		else:
			try:
				logInfo('[%s]: Running job...'%(job.jobId))
				task=[None]*TASKSIZE
				task[NAME] = job.funcName
				task[CLASS]= job.className
				task[MODULE]= job.moduleName
				ret = execute(task, job.class_args, job.method_args)
				if type(ret) == StringType:
					flagError(job, ret)
				logInfo('[%s]:  Task Complete'%(job.jobId))
	
			except:
				#print traceback to logs
				flagError(job, traceback.format_exc() )
			else:
				flagSuccess(job)

#########
#  chkCommand()
#
#  Commands are stored in a dictionary, keys are associated with thread names.
#  There is a special dictionary entry named "ALL" that we can use to send commands to everything
#  chkCommand() will find out who called it and report relevant commands to the caller.
##########
def chkCommand():
		if cmdDict.has_key(ALL):
			cmdLock.acquire()
			cmd = cmdDict[ALL]
			cmdLock.release()
			return cmd
		elif cmdDict.has_key(sys._getframe(1).f_code.co_name):
			cmdLock.acquire()
			cmd = cmdDict[sys._getframe(1).f_code.co_name]
			logDebug(sys._getframe(1).f_code.co_name)
			del(cmdDict[sys._getframe(1).f_code.co_name])
			cmdLock.release()
			return cmd
		else:
			return None

############
#  execute()
#
#  load modules, instantiate classes if they execute, and execute functions that are callable.
#  returns error or values returned by callee.
############
def execute(task, class_args, method_args):
	#Import the module we want
	try:
		if sys.modules.has_key(task[MODULE]):
			reload(sys.modules[task[MODULE]])
			module = sys.modules[task[MODULE]]
		else:
			module = __import__(task[MODULE], locals(), None, None)	
	except:
		return "Error importing module '%s' \nTRACEBACK\n%s"%(task[MODULE],traceback.format_exc())

	#If we get a module, check for the class, then check for the method in the class or just the method if no class
	if task[CLASS] == None:
		try:
			func = getattr(module, task[NAME])
		except AttributeError:
			return "Error: Function '%s.%s' not found"%(task[MODULE], task[NAME])

		try:
			if callable(func):
				if not method_args:
					return func()
				else:
					return func(*method_args, **{})
			else:
				return "Error: '%s.%s' is not callable"%(task[MODULE], task[NAME])
		except:
			return "An Error was detected while running '%s.%s' \n\n TRACEBACK\n %s"%(task[MODULE], task[NAME],traceback.format_exc())
			 

	else:
		try:
			classPtr = getattr(module, task[CLASS])
		except AttributeError:
			return "Error: Could not find class '%s' in module '%s'"%(task[CLASS],task[MODULE])

		if type(classPtr) != ClassType:
			return "Error: An item named '%s' but it was not a class"%task[CLASS]

		try:
			if not class_args:
				classInstance = classPtr()
			else:
				classInstance = classPtr(*class_args, **{})
		except:
			
			return "Error: Could not instantiate class '%s' with args '%s'\n\n TRACEBACK\n%s"%(task[CLASS],class_args, traceback.format_exc())

		try:
			method = getattr(classInstance, task[NAME])
		except AttributeError:
			return "Error: Method '%s' not found in '%s.%s'"%(task[NAME],task[MODULE],task[CLASS])
		try:
			if callable(method):
				if not method_args:
					return method()
				else:
					return method(*method_args, **{})
			else:
				return "Error: '%s.%s.%s' is not callable"%(task[MODULE], task[CLASS], task[NAME])
		except:
			return "An Error was detected while running '%s.%s.%s' \n\n TRACEBACK\n %s"%(task[MODULE], task[CLASS], task[NAME],traceback.format_exc())


def scheduledTask(task):
	while(1):
		#Anything we need to do?
		cmd = chkCommand() 
		if cmd == QUIT:
			return
		#If not, execute and sleep for the specified interval
		else:
			logInfo("Scheduler: Executing '%s'"%task[NAME])
			try:
				message = execute(task,None,None) #args[0] is the "task"
				logInfo("Scheduler: Message from '%s': %s"%(task[NAME],message))
				time.sleep(task[SCHEDULE])
			except:
				logCrit("Scheduler: Error executing '%s'\n\n TRACEBACK\n%s"%(task[NAME],traceback.format_exc()))
				return #the return terminates the bunk thread

def scheduleControl():
	logDebug("Scheduler: Init")
	global schedulePool
	while 1:
		cmd = chkCommand() #deletes after it checks so we need to store it if we have multiple cases
		if cmd == QUIT:
			return
		elif cmd == LOAD:
			reload(tasklist)
			logDebug("Scheduler: Scanning Tasklist")
			for entry in tasklist.tasklist:
				if entry[SCHEDULE] != None and type(entry[SCHEDULE]) == IntType:
					#Load the module

					#Check to make sure we haven't already scheduled the task, check the interval if we have
					#running the task will cause it to reload for us so we don't need to do that here.
					#FIXME: make this actually work
					if schedulePool.has_key(entry[NAME]):
						pass
					#Create a scheduled thread
					else:
						logInfo("Scheduler: Adding job '%s' at a %s second interval"%(entry[NAME],entry[SCHEDULE]))
						schedulePool[entry[NAME]]= threading.Thread(target=scheduledTask,name=entry[NAME],args=(entry,))
						schedulePool[entry[NAME]].start()
		logDebug("Scheduler: Task list scan complete.")
		time.sleep(750)


class ReleaseDaemon(Pyro.core.ObjBase):
	def __init__(self):
		Pyro.core.ObjBase.__init__(self)
		self.thrdPool = []
		self.jobId = 0
		self.lock = threading.Lock()
		for i in range(NUM_THREADS):
			logDebug("Setting up threads")
			thrd = threading.Thread(target=doTask)
			thrd.setDaemon(True)
			self.thrdPool.append(thrd) #store so we can do stuff with em later
			thrd.start()
		self.scheduleCtrlThrd = threading.Thread(target=scheduleControl)
		cmdLock.acquire()
		global cmdDict
		cmdDict['scheduleControl'] = LOAD #Initial scheduling when the server starts
		cmdLock.release()
		self.scheduleCtrlThrd.start()



#Need destructor too so that this thing cleans itself up

#args == edition, version, combined_id, merged_id
	def __queueJob(self, task,class_args,method_args):
#		print "Scheduling Job"
		self.lock.acquire()
		self.jobId += 1
		if self.jobId == 65534:
			self.jobId = 1
		self.lock.release()

		try:
			logInfo('[%s]Adding Job to queue: %s.%s(%s).%s(%s)'%(self.jobId,task[MODULE],task[CLASS],class_args,task[NAME],method_args ) )
			queue.put(ReleaseJob(task[NAME],task[CLASS],task[MODULE],class_args,method_args,self.jobId))
			return "Job Succesffuly Added  Job ID: %s"%self.jobId

		except:
			logInfo('[%s]An Error was recieved'%self.jobId)
			logCrit(traceback.format_exc())
			return "An error occured while submitting job, please check logs for Job ID %s"%self.jobId

############################
#	expose()
#
#  Returns list of server's callable functions
#
###########################
	def expose(self, func=None):
		if func != None:
			reload(tasklist)
			for entry in tasklist.tasklist:
				if entry[NAME] == func:
					return entry
					 
			return None #Error Case

		else:
			reload(tasklist)
			output = []
			id = 0
			for entry in tasklist.tasklist:
				if entry[SCHEDULE] == BACKGROUND:
					sched = "Background"
				elif entry[SCHEDULE] == IMMEDIATE:
					sched = "Immediate"
				else:
					print "Found %s" %entry[SCHEDULE]

				output.append("%s: Method: %s Class: %s Module: %s Properties: %s"%(id,entry[NAME],entry[CLASS],entry[MODULE],sched))
				id += 1
			return output


###########################
#	exec()
#
#	Schedules background tasks or executes immediate/threadsafe tasks
#
###########################
	def exec_task(self, func, class_args=None, method_args=None):
		#Verify Args
		if type(class_args) != TupleType and  type(class_args) != NoneType:
			return "Internal Error: class_args must be a tuple or None, type was %s"%type(class_args)
		if type(method_args) != TupleType and type(method_args) != NoneType:
			return "Internal Error: method_args must be a tuple or None, type was %s"%type(method_args)

		task = self.expose(func)
		if task == None:
			return "Internal Error: Task '%s' not found"%func

		if type(task[MODULE]) != StringType:
			return "Internal Error: Module field must contain a string"

		if type(task[CLASS]) != StringType and type(task[CLASS]) != NoneType:
			return "Internal Error: Class field must contain either a string or a None"


		#queue or execute
		if task[SCHEDULE] == BACKGROUND:
			return self.__queueJob(task,class_args,method_args)
		elif task[SCHEDULE] == IMMEDIATE:
			try:
				ret = execute(task,class_args,method_args)
				if type(ret) == StringType:
					logErr("Error: Task '%s' returned error: %s"%(task[NAME],ret))
					return ret
				else:
					return ret
			except:
				return "There was a problem executing '%s'\n\n TRACEBACK: \n\n %s "%(task[NAME], traceback.format_exc())

		else:
			return "Internal Error: Task '%s' is not callable"%func

######################
#
#  command()
#
#  This allows us to send commands to the server 
#FIXME: This function needs to do oh so much more now
######################
	def command(self,cmd,dest):
		global cmdDict
		try:
			cmdLock.acquire()
			if dest == ALL:
				queue.put(ReleaseJob(None, None, None, None, None, None, QUIT))		
				cmdDict[ALL] = QUIT
			else:
				cmdDict[dest]=cmd
		finally:
			cmdLock.release()
			return 1


def main():
	Pyro.core.initServer()
	daemon = Pyro.core.Daemon(port=7767)
	daemon.connect(ReleaseDaemon(), 'release_d')
	daemon.requestLoop()

if __name__ == "__main__":
	main()

