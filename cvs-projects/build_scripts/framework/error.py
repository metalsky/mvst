#!/usr/bin/env python

#
#  FILE:  error
#
#  DESCRIPTION:
#    This file contains all the error and debug handling functions:
#
#	DEBUG = 
#		DEBUG_ON - display all debug messages
#		DEBUG_USER - display only user debug messages
#		DEBUG_SYSTEM - display only framework debug messages
#		DEBUG_OFF - suppress all debug messages
#
#	OUTFILE = 
#		STDOUT - write all messages to stdout
#		STDERR - write all messages to stderr
#		"filename" - write all messages to the file 'filename'
#
#	EMAIL="email address"
#		email address - a comma seperated list of adresses
#
#
#	message(msg) - log a general message
#
#	warning(msg) - log a warning
#
#	error(msg) - log an error
#
#	fatalError(msg) - log a fatal error and stop the system
#
#	isError(msg) - if any errors have been logged, print them
#			and return True, otherwise False
#
#	email(subject, msg) -  send an email to all the addresses in EMAIL
#
#
#	debug(msg) - log a user debug message
#
#	sysDebug(msg) - log a framework debug message
#
#	
#	init() - read in config info from config file
#
#	writeMsgs() - write any messages in the queue to the output
#		      file. NOTE: each time this is called, it will 
#		      overwrite the contents of the OUTPUTFILE
#		
#
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

import sys, string, smtplib
from email.MIMEText import MIMEText

import config


# ---------------------------------------------
# --- Globals ---------------------------------
# ---------------------------------------------

MsgList = []

ERROR_TYPE = "ERROR"
DEBUG_TYPE = "DEBUG"
WARNING_TYPE = "WARNING"
GENERAL_TYPE = "MESSAGE"


DEBUG_ON = "DEBUG_ON"
DEBUG_USER = "DEBUG_USER"
DEBUG_SYSTEM = "DEBUG_SYSTEM"
DEBUG_OFF = "DEBUG_OFF"

DEBUG = DEBUG_OFF


STDOUT = "STDOUT"
STDERR = "STDERR"
OUTFILE = STDERR


EMAIL = []

# ---------------------------------------------
# --- config ----------------------------------
# ---------------------------------------------

def init():
	debug = config.getDebug()
	message("DEBUG LEVEL: "+debug)

	#DEBUG
	if debug == DEBUG_ON or debug == DEBUG_USER or debug == DEBUG_SYSTEM or debug == DEBUG_OFF:
		global DEBUG
		DEBUG = debug
	
	#OUTFILE
	outfile = config.getOutfile()
	if outfile != "":
		global OUTFILE
		OUTFILE = config.getOutfile()

	#EMAIL
	email_list = config.getEmail()
	addEmailAddr(email_list)	

# ---------------------------------------------
# --- Debug statements ------------------------
# ---------------------------------------------

def debug(msg):
	if DEBUG == DEBUG_USER or DEBUG == DEBUG_ON:
		logMsg(DEBUG_TYPE, "DEBUG_USER: "+str(msg))

def sysDebug(msg):
	if DEBUG == DEBUG_SYSTEM or DEBUG == DEBUG_ON:
		logMsg(DEBUG_TYPE, "DEBUG_SYSTEM: "+str(msg))


# ---------------------------------------------
# --- Cleanup Handler--------------------------
# --------------------------------------------- 

#msg allows us to send different status messages depending on when gracefulExit was called

def gracefulExit(subject, msg):
	# FIXME: This function needs to actually do cleanup, for now just exit
	email(subject, msg)
	writeMsgs()
	sys.exit(1)

# ---------------------------------------------
# --- email functions -------------------------
# ---------------------------------------------

def email(subject, msg):
	#Return if no email addresses present
	if len(EMAIL) < 1:
		return
	smtpObj = smtplib.SMTP()
	mailMsg = MIMEText(msg)
	mailMsg['From'] = "Task Execution Framework"
	
	mailMsg['To'] = string.join(EMAIL, ", ")
	mailMsg['Subject'] = subject
	print "Sending email to:"
	for i in EMAIL:
		print "\t"+i
	try:
		smtpObj.connect(config.getSmtp())
		smtpObj.sendmail('noreply@mvista.com',string.join(EMAIL, ", "), mailMsg.as_string())
		smtpObj.close()
	except SMTPConnectError:
		logMsg(ERROR_TYPE, "Cannot send email: Error Connecting to SMTP Server - Check Framework Configuration")
	except:
		logMsg(ERROR_TYPE, "Unknown Error Sending Email")



def addEmailAddr(addr):
	if addr != "":
		global EMAIL
		m = addr.split(',', 200)
		for i in m:
			EMAIL.append(i)



# ---------------------------------------------
# --- Error and Warning statements ------------
# ---------------------------------------------

def message(msg):
	logMsg(GENERAL_TYPE, str(msg))

def warning(msg):
	logMsg(WARNING_TYPE, "WARNING: "+str(msg))


def error(msg):
	logMsg(ERROR_TYPE, "ERROR: "+str(msg))


def fatalError(msg):
	logMsg(ERROR_TYPE, "FATAL ERROR: "+str(msg))
	message("Trying to exit gracefully...")
	info = "The Task Execution Framework terminated due to the following error: \n\n" + msg
	gracefulExit("Framework Encountered Fatal Error", info)	


def isError():
	ret = False
	global MsgList
	for message in MsgList:
		if message[0] == ERROR_TYPE:
			ret = True
	return ret


def writeMsgs():
	global MsgList
	file = openOutput()
	for message in MsgList:
		file.write(message[1]+"\n")
	
	closeOutput(file)
	MsgList = []


# ---------------------------------------------
# --- helper functions ------------------------
# ---------------------------------------------


def logMsg(type,msg):
	global MsgList
	if type == WARNING_TYPE or type == ERROR_TYPE:
		found = False
		for message in MsgList:
			if message[1] == msg:
				return
				
	MsgList.append((type,msg))


def openOutput():
	if OUTFILE == STDOUT:
		return sys.stdout
	elif OUTFILE == STDERR:
		return sys.stderr
	else:
		# lets make sure we can really 
		# write to the file.
		try:
			file = open(OUTFILE, "w")
			return file
		except:
			sys.stderr.write("Can't open OUTFILE: '"+str(OUTFILE)+"' for writing\n")
			return sys.stderr
	
	#this should be impossible
	return sys.stderr



def closeOutput(file):
	if file != sys.stdout and file != sys.stderr:
		file.close()


