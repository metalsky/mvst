#!/usr/bin/python

#
#  FILE:  teu
#
#  DESCRIPTION:
#     This file contains the task execution unit. This component is 
#     common for both the RULES and the TASKS 
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





#Std libs
import sys, threading, traceback
from types import *

#Our own libraries
import error
from resources import getResourceWrapper,releaseResourceWrapper
from task import *
from data import Data

threadDictionary = {}
######################
#		forkWrapper
#
#	Threads in python open up their own interpreter
#	which means that exceptions happening in the thread will not be seen by using
#	a try/except in the calling script
#
#	To get around these we use a simple wrapper around the function that can catch
#	exceptions for us in a spawned thread
#
######################
def forkWrapper(task, dataObj):
	try:
		task.taskPtr(Data(dataObj.shared, dataObj.local))
	except:
		error.error("Error Executing task: %s"%(task.name)) 
		try:
			exc_type, exc_value, exc_tb = sys.exc_info()
			tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
			for tb in tb_list:
				m = tb.split('\n', 200)
				for i in m:
					error.error(i)
		finally:
			del(exc_tb)
					
		if task.fatal == FATAL:
			error.fatalError("Cannot continue from this failure")
	return


##############################
#     fork(taskObj task)
#
#  Create a thread for a given task and execute
#
##############################
def fork(task, dataObj):
	global threadDictionary
	error.sysDebug("Forking task: %s"%(task.name))
	if threadDictionary.has_key(task.name):
		error.fatalError("SYSTEM ERROR: Thread for task %s already exists"%(task.name))
	threadDictionary[task.name] = []

	#Integration with resource Manager
	if(task.forkObj.remoteType != None):
			resource = getResourceWrapper(task, dataObj) 
	if(type(task.taskPtr) == ListType): #threading a list of tasks
		funcPtr = runTaskList
		argsTuple = (task.taskPtr,Data(dataObj.shared, dataObj.local))
	else: #threading a normal task
		funcPtr = forkWrapper #this wrapper is necessary for error handling using the exception mechanism
		argsTuple = (task, dataObj)
	i = 0
	while (i < task.forkObj.numThrds):
		threadDictionary[task.name].append(threading.Thread(target=funcPtr, args=argsTuple))
		i = i + 1
	error.sysDebug("Starting threads for %s"%(task.name))
	for thread in threadDictionary[task.name]:
		thread.start()
	#If we checked something out we can give it back
	if(task.forkObj.remoteType != None):
		releaseResourceWrapper(task, dataObj, resource)
	return

##################################
#           sync
#
# calls join on threads referenced
# by a task name
#################################
def sync(task):
	error.sysDebug("Syncing %s"%(task.name))
	for thread in threadDictionary[task.name]:
		thread.join()
	return



#############################
#     runTaskList
#
#  Takes a task list and executes tasks.  
#  This handles threading of tasks, resource aquisition from
#  the resource manager.
#
#  This function recursively calls itself if there exists a tasklist embedded in a tasklist
#
#############################
def runTaskList(taskList, dataObj):
#This really should not be possible, but we are safe.  We use the error handler incase something totally
#weird happens during a build we ALWAYS want a graceful exit
	if type(taskList) != ListType:
		error.fatalError("SYSTEM ERROR: Non task list sent to runTaskList")
  
#There are basically four cases that can happen here
#1. There is a task that requires nothing special, we just execute
#2. There is a task that needs to be threaded
#3. We receive a task list that must be executed as a thread
#4. Execution of nested tasks inline

	for task in taskList:
		#Task List
		if(task.forkObj == None and type(task.taskPtr) == ListType): #inline
				error.sysDebug("Executing Tasklist: %s"%(task.name))
				runTaskList(task.taskPtr, dataObj) #inline, so its gonna use the same local space
		#Task
		elif(task.forkObj == None and type(task.taskPtr) == FunctionType):
			try:
				error.sysDebug("Executing %s"%(task.name))
				task.taskPtr(dataObj)
			except:
				error.error("Error Executing task: %s"%(task.name))
				#Dump traceback of failed task 
				try:
					exc_type, exc_value, exc_tb = sys.exc_info()
					tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
					for tb in tb_list:
						m = tb.split('\n', 200)
						for i in m:
							error.error(i)
				finally:
					del(exc_tb)
					
				if task.fatal == FATAL:
					error.fatalError("Cannont continue from this failure")


		elif(task.forkObj != None): #threaded 
			if(task.forkObj.forkOp == FORK):
				fork(task, dataObj)
			elif(task.forkObj.forkOp == SYNC):
				sync(task)
			else:
				error.fatalError("SYSTEM ERROR: Bad Fork Op in task: %s"%(task.name))

		else:
			error.fatalError("SYSTEM ERROR: Unknown error in task list execution")

	return


def main():
	print "No manual execution of this module"
	sys.exit(1)

if __name__ == "__main__":
  main()



