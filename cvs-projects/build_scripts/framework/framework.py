#!/usr/bin/python

import sys, signal, getopt


def unhandledException(type, value, tb):
	import error, traceback, string
	error.message("SYSTEM ERROR: UNHANDLED EXCEPTION.. TERMINATING FRAMEWORK")
	error.message("Trying to get traceback information...")
	tb_list = traceback.format_exception(type, value, tb)
	tb_msg = ""
	for tb in tb_list:
		m = tb.split('\n', 200)
		for i in m:
			error.error(i)
			tb_msg = tb_msg + i
	error.message("Trying to exit gracefully...")
	error.gracefulExit("Framework terminated due to unhandled exception","Traceback information: \n\n" + tb_msg )

#Override default excepthook
sys.excepthook = unhandledException


def signalHandler(signum, frame):
	import error
	error.message("FRAMEWORK: SIGTERM CAUGHT KILLING FRAMEWORK")
	error.message("Trying to exit gracefully...")
	error.gracefulExit("Framework Killed","The Task Execution Framework has terminated due to a kill signal")


def usage():
	print "Usage: framework.py [OPTIONS] [VARIABLES] <JOB_DIR>"
	print " Options:"
	print "\t -h             - Show usage information."
	print "\t -t <TAG>       - Set the run TAG for the job (mandatory)"
	print "\t -i <ID>        - Set the ID for the job (mandatory)"
	print "\t -e <addresses> - comma seperated list of address to email" 
	print "\t                  when the job completes or fails"
	print ""
	print " Variables:"
	print "\t Variables passed in will be automatically put into"
	print "\t the shared data object. You can pass variables and"
	print "\t their values using the following format:"
	print ""
	print "\t VARNAME=VALUE"
	print ""
	print "\t Where VARNAME is the variable name, and VALUE is"
	print "\t its value. As many variable names may be passeded"
	print "\t in as needed. Each variable assigment must be"
	print "\t seperated by spaces."
	print ""
	print " JOB_DIR is the location to the job you want to"
	print " run."
	print ""
	sys.exit(1)




def parseArgs(args):
	job_dir = args[-1]
	m = job_dir.split('=', 20)
	if len(m) > 1:
		return None, None

	args = args[0:-1]
	variables = []
	for arg in args:
		m = arg.split('=', 2)
		if len(m) > 1:
			variables.append((m[0],m[1]))
		else:
			return None, None
	
	return variables, job_dir
	


#Information that will be passed to the script
#product, tag (jobtag), and optional emails

def main(argv):
	
	#Handle OPTIONS
	try:
		opts, args = getopt.getopt(argv[1:], "ht:i:e:")
	except getopt.GetoptError:
		print "Invalid option!"
		usage()
	#Default args
	tag = None
	id = None
	notificationEmail = None
	
	for opt, arg, in opts:
		if(opt == "-h"):
			usage()
		elif(opt == "-t"):
			tag = arg
		elif(opt == "-i"):
			id = arg
		elif(opt == "-e"):
			notificationEmail = arg

	if tag == None:
		print "A TAG must be specified to run!"
		usage()
	if id == None:
		print "An ID must be specified to run!"
		usage()	

	#handle VARIABLES
	variables, job_dir = parseArgs(args)
	if job_dir == None:
		print "No JOB_DIR given!"
		usage()
	if variables == None:
		print "Invalid option or variable decleration!"
		usage()
	
	
	#Finish setting up framework
	import config, error

	if not config.init(job_dir):
		error.warning("No Config file found. Using defaults")
	error.init()
	
	import data, parser, ruleParser, teu
	
	#Register our signalHandler now
	#We will need to start some kinda signal handler at this point so that we can have a graceful exit
	signal.signal(signal.SIGTERM, signalHandler)
	

	#include our command line options
	if notificationEmail != None:
		error.addEmailAddr(notificationEmail)
	
	variables.append(('TAG', tag))
	variables.append(('ID', id))


	#Parse the task lists
	error.message("Parsing the task lists...")
	taskList = parser.parseTaskList()
	if error.isError():
		error.fatalError("Error parsing the task lists!")
		
	error.message("task lists parsed OK!")
	
	
	#Parse Rules
	error.message("Parsing the rule lists...")
	ruleList = ruleParser.getRules()
	if error.isError():
		error.fatalError("Error parsing the rules list!")
		
	error.message("rule lists parsed OK!")


	#enforce the rules
	rulesObj = data.Data()
	rulesObj.shared.putVar("USER_LIB_PATH", config.getUserLibPath())
	rulesObj.shared.putVar("COMMON_LIB_PATH", config.getCommonLibPath())
	rulesObj.shared.putVar("TASK_LIST", taskList)
	
	error.message("Enforcing the Rules...")
	teu.runTaskList(ruleList, rulesObj)
	if error.isError():
		error.fatalError("Your job did not pass a FATAL rule")
		
	error.message("All FATAL rules passed!")
	
		
	
	#Start the job (run the tasks)
	error.message("Running the tasks...")
	dataObj = data.Data()
	
	for var in variables:
		name = var[0]
		value = var[1]
		dataObj.shared.putVar(name, value)
	
	teu.runTaskList(taskList,dataObj)
	if error.isError():
		error.message("Some tasks failed during execution!")
		error.message("Your job may not have completed sucessfuly!")
		error.message("Trying to exit gracefully...")
		error.gracefulExit("Framework Job: "+job_dir+"-"+tag+"  completed with errors","Framework Job: "+job_dir+"-"+tag+" completed, however some tasks failed during execution. Please check logs as your job may not have been successful.")

	error.message("All tasks completed sucessfully!")
	error.gracefulExit("Job: "+job_dir+"-"+tag+" completed successfully","The Task Execution Framework has completed Job: "+job_dir+"-"+tag )





if __name__== "__main__":
	main(sys.argv)



