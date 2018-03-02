#!/usr/bin/python

# You can pass several parameters on the command line
# (more info by running this with option --help)
# or you can modify the default values here
# (more info in WebKit.Launch):

workDir = None
webwareDir = '/var/www/release/Webware-0.9.2'
libraryDirs = []
runProfile = 0
logFile = "/var/log/Webkit/AppServer.log" 
pidFile = "/var/run/Webkit/Run.pid"
user = None
group = None

import sys
sys.path.insert(0, webwareDir)

from WebKit import Launch

Launch.workDir = workDir
Launch.webwareDir = webwareDir
Launch.libraryDirs = libraryDirs
Launch.runProfile = runProfile
Launch.logFile = logFile
Launch.pidFile = pidFile
Launch.user = user
Launch.group = group

if __name__ == '__main__':
	Launch.main()
