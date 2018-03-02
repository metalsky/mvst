#! /usr/bin/env python

import os, sys

def print_usage():
	print "Usage: " + sys.argv[0] + " <job path>"
	print "\t" + "This program will test the job in the 'job path' dir"
	sys.exit(1)
#end print_usage


def main():

	if len(sys.argv) != 2:
		print_usage()


	#import config and error first to setup basic framework logging settings
	import config
	import error

	if not config.init(sys.argv[1]):
		error.warning("No Config file found. Using defaults")
	error.init()

	#Import everything else now that config and error are setup:
	import data
	import parser
	import ruleParser
	import teu


	
	error.message("\n\n**** TASK PARSE TREE ****")
	t_list = parser.parseTaskList()
	if error.isError():
		error.writeMsgs()
		sys.exit(1)
		
		
	parser.printTaskList(t_list)
	error.message("\n\n**** RULES LIST ****")
	r_list = ruleParser.getRules()
	if error.isError():
		error.writeMsgs()
		sys.exit(1)

	parser.printTaskList(r_list)
	
	#setup shared info for rules:
	#common = None
	common = data.Data()
	common.shared.putVar("USER_LIB_PATH", config.getUserLibPath())
	common.shared.putVar("COMMON_LIB_PATH", config.getCommonLibPath())
	common.shared.putVar("TASK_LIST", t_list)

	#enforce rules
	error.message("\nRunning Rules:")
	teu.runTaskList(r_list, common)
	if error.isError():
		error.writeMsgs()
		sys.exit(1)
		
	error.message("All 'FATAL' Rules Passed; Your job is ready to run!\n")
	error.writeMsgs()

#end main()


if __name__ == "__main__":
	main()
