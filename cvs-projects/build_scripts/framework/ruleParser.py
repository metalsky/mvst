#! /usr/bin/env python

#
#  FILE:  rules
#
#  DESCRIPTION:
#    This file contains the RULES parser and execution components 
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



import os, sys

import error
import config
import task
import parser



def enforce(task_list):
	#get list of rules
	rules = getRules()

	#for each task item
	#run the rules
	
	

#end enforce


def getRules():
	
	rule_list=[]
	task_ptr = None
	# There are two rules files:
	# 1) user rules file - any rules specific to that job
	# 2) common rules file - rules common all jobs
	for file_name in [config.getUserRulesFile(), config.getCommonRulesFile()]:
		if not os.path.isfile(file_name):		
			continue

		file = open(file_name)
		lines = file.readlines()
		file.close()
		
		#Get the names of all the rules and import them into a list.
		for x in range(len(lines)):
			line = lines[x]
			name, tmp, tmp1, tmp2, fatal = parser.parseLine(line)

			if name == None:
				continue
			
			#We dont need to check the lib paths because that was 
			#already done in the parsing stage
			
			u_py_file, u_task_ptr = parser.findTask(name, config.getUserLibPath())
			c_py_file, c_task_ptr = parser.findTask(name, config.getCommonLibPath())

			error.sysDebug("GetRules: user: "+ str(u_py_file)+", "+str(u_task_ptr))
			error.sysDebug("GetRules: common: "+ str(c_py_file)+", "+str(c_task_ptr))
					
		
			#did we find a py file?
			if not u_py_file and not c_py_file:
				error.error("GetRules: rule: " + name + " Does not exist. See Debug output for traceback")
				continue
			
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

			if not task_ptr:
				error.error("Can't find rule: " + str(name))
			else:
				#Setup rule task
				task_item = task.Task(name, py_file, file_name, x+1, None, task_ptr, fatal)
				rule_list.append(task_item)
				error.sysDebug("getRules: adding rule:" + name)
		
	return rule_list
#end getRules




def main():
	print "No manual execution of this module"
	sys.exit(1)

if __name__ == "__main__":
	main()
				
