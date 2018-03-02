#!/usr/bin/python

##################################
#					data.py
#
#	classes and methods for access to 
#	framework variables
#
##################################
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




import threading, copy, sys
from types import *

#You will notice no error checking in this module
#Any wrong doings to a dictionary will trigger an exception, either KeyError or NameError
#Since these functions will always be executed in a try/except we will always catch any
#programmer misdoings


class Local:
	def __init__(self):
		self.__userData = {}

	def getVar(self, variableName):
		return self.__userData[variableName]

	def putVar(self, variableName, value):
		self.__userData[variableName] = value
		return

	def hasVar(self, variableName):
		return self.__userData.has_key(variableName)
		
#For the shared we need to do a little bit of error handling
#The reason for this is that we may still want to continue execution upon error
#and so we must catch exceptions at this level to make sure we release the mutex

class Shared:
	def __init__(self):
		self.__userData= {}
		self.__mutex = threading.Lock() #lock object - this gaurantee's single transactions
		self.__atomicLock = threading.Event() #the atomic lock is for when we need to do more than a single transaction
		self.__atomicOwner = None #atomicOwner is the thread that is in a critical section
		self.__atomicLock.set() #set by default, no one waits until we say so

	def __checkAtomicSetLock(self):
		while(1):
			self.__mutex.acquire() 
			if self.__atomicOwner != None and threading.currentThread() != self.__atomicOwner:
				self.__mutex.release()
				self.__atomicLock.wait()
			else:
				break

	def getVar(self, variableName):
		temp = None
		self.__checkAtomicSetLock()
		try:
			temp = self.__userData[variableName]
		finally:
			self.__mutex.release()
		return temp

	def putVar(self, variableName, value):
		self.__checkAtomicSetLock()
		try:
			self.__userData[variableName] = value
		finally:
			self.__mutex.release()
	
	def hasVar(self, variableName):
		ret = False
		self.__checkAtomicSetLock()
		try:
			ret = self.__userData.has_key(variableName)
		finally:
			self.__mutex.release()
		return ret

#Atomic mode allows us to enter a critical section for multiple operations to the dataspace
#all other operations are only safe for single ops.

#The reason this is the situation in which we need to retrieve data, alter it, and store it back in the dataspace
	def setAtomic(self):
		self.__mutex.acquire() 
		try:
			self.__atomicLock.clear() #Makes everyone wait
			self.__atomicOwner = threading.currentThread()
		finally:
			self.__mutex.release()

	def clearAtomic(self):
		self.__mutex.acquire()
		try:
			self.__atomicOwner = None
			self.__atomicLock.set() #All threads waiting on this event will wait while this is set
		finally:
			self.__mutex.release()




#Data us just a container class grouping the shared and local data stores
class Data:
	def __init__(self, shared=Shared(), local=Local()):
		self.shared = shared #This is gonna be an object, so we're gonna get a reference
		self.local = copy.deepcopy(local) #We want our own copy, since this is an object we have to force it 



def main():
	print "No Manual Execution of this Module"
	sys.exit(1)


if __name__=="__main__":
	main()

