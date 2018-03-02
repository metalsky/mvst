#! /usr/bin/env python

#
#  FILE:  config
#
#  DESCRIPTION:
#    This file contains all the global config options for the framework.
#
#
#	Config file: framework.config (optional)
#		DEBUG=<debug level>  - See error.py for available levels
#
#		OUTPUTFILE=
#			STDOUT
#			STDERR
#			"filename" - See error.py for more info. 
#				     Note: 'filename' needs to be abs.
#
#
#		COMMONPATH=<common path> - path to the 'common' 
#					   components (optional)
#					   Note: this needs to be abs,
#					   otherwise its relative to the
#					   job path.
#
#		
#		EMAIL=<address list> - comma seperated list of email 
#				       addresses to notify when the
#				       job finishes (failure or not)
#
#
#
#	init(task_dir) - setup the config module. task_dir is the 
#			   execution directory 
#
#		
#
#
#	getCommonPath() - return the path to the common components
#
#	getCommonLibPath() - return the path to the common libs
#
#	getCommonRulesFile() - return the path to the common rules 
#			       file
#
#
#	getUserPath() - return the path to the execution dir
#
#	getUserLibPath() - return the path to the user libs
#
#	getUserTaskFile() - return the path to the user's task 
#			    file
#
#	getUserRulesFile() - return the path to the user's rules 
#			     file
#
#
#
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

import os


# ---------------------------------------------
# --- Global config options -------------------
# ---------------------------------------------


USER_TASK_PATH = "./"
CONF_FILE = "framework.config"



# ---------------------------------------------
# --- config setup ----------------------------
# ---------------------------------------------


def init(task_dir):
	if not os.path.isabs(task_dir):
		task_dir = os.path.abspath(task_dir)

	global USER_TASK_PATH 
	USER_TASK_PATH = task_dir
	config_file = os.path.join(USER_TASK_PATH, CONF_FILE)
	if os.path.isfile(config_file):
		return True
	else:
		return False



# ---------------------------------------------
# --- General Framework settings --------------
# ---------------------------------------------

CONFIG_COMMONPATH = "COMMONPATH"

COMMON_PATH = "../common"
TASK_FILE = "START.lst"
RULE_FILE = "RULES.lst"
LIB_PATH = "lib"



def getCommonPath():
	c_path = read(CONFIG_COMMONPATH)
	if c_path != "":
		if not os.path.isabs(c_path):
			c_path = os.path.join(USER_TASK_PATH, c_path)
			c_path = os.path.abspath(c_path)
		global COMMON_PATH
		COMMON_PATH = c_path
	return COMMON_PATH

def getCommonLibPath():
	c_path = getCommonPath()
	return os.path.join(c_path, LIB_PATH)

def getCommonRulesFile():
	c_path = getCommonPath()
	return os.path.join(c_path, RULE_FILE)




def getUserPath():
	return USER_TASK_PATH

def getUserLibPath():
	return os.path.join(USER_TASK_PATH, LIB_PATH)

def getUserTaskFile():
	return os.path.join(USER_TASK_PATH, TASK_FILE)

def getUserRulesFile():
	return os.path.join(USER_TASK_PATH, RULE_FILE)


# ---------------------------------------------
# --- Error module settings -------------------
# ---------------------------------------------

ERROR_DEBUG = "DEBUG"
ERROR_OUTFILE = "OUTPUTFILE"
ERROR_EMAIL = "EMAIL"
ERROR_SMTP = "SMTP"

SMTP_DEFAULT = "localhost"

def getDebug():
	ret = read(ERROR_DEBUG)
	return ret

def getOutfile():
	return read(ERROR_OUTFILE)

def getEmail():
	return read(ERROR_EMAIL)

def getSmtp():
	server = read(ERROR_SMTP)
	if server == "":
		return SMTP_DEFAULT
	else:
		return server

# ---------------------------------------------
# --- Resources config options ----------------
# ---------------------------------------------

RESOURCE_MANAGER = "RESOURCEMANAGER"

def getResourceManager():
	r_path = read(RESOURCE_MANAGER)
	if not r_path == "":
		if not os.path.isabs(r_path):
			r_path = os.path.join(USER_TASK_PATH, r_path)
			r_path = os.path.abspath(r_path)
		
	return r_path


# ---------------------------------------------
# --- helper functions ------------------------
# ---------------------------------------------


def read(key):
	config_file = os.path.join(USER_TASK_PATH, CONF_FILE)
	if not os.path.isfile(config_file):
		return ""	
	
	file = open(config_file, "r")
	lines = file.readlines()
	file.close()

	for line in lines:
		if line.find(key) == 0:
			try:
				m = line.split('=',2)
				value = m[-1]
				value = value.strip()
				value = value.strip('"')
				return value
			except:
				return ""
	return ""
				




def main():
	print "No manual execution of this module"
	sys.exit(1)



if __name__ == "__main__":
	main()
	      
