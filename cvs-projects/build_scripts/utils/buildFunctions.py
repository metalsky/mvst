#!/usr/bin/python
import os, sys, string, re, shutil, time, threading
from zenlib import *

cvsroot = ':ext:cvs.sh.mvista.com:/mnt/cvs'
cvsopts = 'cvs -Q -d %s/' % cvsroot

gitroot = 'git.sh.mvista.com:/var/cache/git'
#gitcmd = '/opt/git-20081217/bin/git '
gitcmd = 'git '

SELINUXTRUE	= 1
SELINUXFALSE	= 0
GCCLICENSE	= 'true'
GCCNOLICENSE	= 'false'

def printflush(msg,logfile='',scripttest=0,noprint=0):
  if not noprint:
    print string.strip(msg)
    print
    sys.__stdout__.flush()
  # if scripttest is defined as 0 or 2, write to the log file
  # if scripttest is 1, we don't want any files created, so skip it
  if logfile and scripttest in (0,2):
    f_log = open(logfile,'a')
    f_log.write(msg)
    f_log.write('\n')
    f_log.close()

# printflush() differs from printlog() because it prints the message first before writing it to the log
# so in some case we don't want the msg/line printed and only want it in a file
def printlog(line,logfile):
  os.system('echo "' + line + '" >> ' + logfile)
  sys.__stdout__.flush()

def mailError(msg,subject,resource,buildtag,logmsg,reslog,scripttest):
  systemCmd('ssh overlord "echo \"%s\" | /usr/bin/Mail -s \\"%s\\" build_failures@mvista.com"' % (msg,subject),scripttest)
  printlog('%s' % logmsg,reslog)
                                                                                                              
def getNotBuilt(logdir, log, target,builddir,scripttest=0):
  goback = os.getcwd()
  if not scripttest:
    os.chdir(builddir)
  systemCmd('./getNotBuilt %s %s %s' % (logdir, log, target),scripttest)
  os.chdir(goback)

def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  return s_time + ' [' + str(f_time) + ']'
                                                                                                              
def mstart(app,collectivelog='',scripttest=0):
  startmsg = '<' + sys.argv[0] + '>: building ' + app + ' at ' + gettime() + '...'
  if scripttest == 1:
    printflush(startmsg)
  elif collectivelog:
    printflush(startmsg,collectivelog)
  else:
    printflush(startmsg)

def mstop(app,collectivelog='',scripttest=0):
  stopmsg = '<' + sys.argv[0] + '>: finished ' + app + ' at ' + gettime() + '...'
  if scripttest == 1:
    printflush(stopmsg)
  elif collectivelog:
    printflush(stopmsg,collectivelog)
  else:
    printflush(stopmsg)

def makeDir(path,scripttest=0):
  if scripttest in (1,2):
    printflush('\ncommand: mkdir -p ' + path)
  if not os.path.exists(path) and scripttest in (0,2):
    os.makedirs(path)

def removeDir(path,scripttest=0):
  if scripttest in (1,2):
    printflush("command: rm -rf %s" % path)
  if os.path.exists(path) and scripttest != 1:
    os.system('rm -rf %s' % path)

def getdiskspace(hostname):
  printflush("Disk Usage:")
  if hostname != 'solaris8':
    os.system("df /")
  else:
    os.system("df /chroot")
  sys.__stdout__.flush()

def chroot(hostname,command,scripttest,log=''):
  chrootlog = "/chroot/%s/home/build/chroot.log" % hostname
  if hostname not in ("solaris8","windows2000"):
    cmd = 'sudo chroot /chroot/%s /bin/su - build -c "%s" > %s 2>&1 < /dev/null' % (hostname,command,chrootlog)
  elif hostname == "solaris8":
    cmd = 'chroot /chroot/%s /bin/su - build -c "export LM_LICENSE_FILE=27000@overlord; %s" > %s 2>&1' % (hostname,command,chrootlog)
  elif hostname == "windows2000":
    chrootlog = '/home/build/dailybuild/chroot.log'
    cmd = '%s > %s 2>&1' % (command,chrootlog)
  if scripttest in (1,2):
    printflush('chroot command: ' + cmd)
    if scripttest == 1:
      res = 0
  if scripttest in (0,2):
    res = os.system(cmd)
    if os.path.exists('%s' % chrootlog):
      os.system('cat %s' % chrootlog)
      if log:
        os.system('cat %s >> %s' % (chrootlog,log))
  sys.__stdout__.flush()
  return res

def wrotecheck(hostname,getReqFiles=0,minReqApps=''):
  list = 0
  #print 'minReqApps = %s' % minReqApps
  if os.path.exists('/chroot/%s/home/build/chroot.log' % (hostname)):
    list = os.popen('cat /chroot/%s/home/build/chroot.log | grep Wrote' % (hostname)).readlines()
  if list and getReqFiles:
    f_minReqApps = open(minReqApps,'a')
    for reqFile in list:
      #print 'checking %s to add...' % reqFile
      if string.find(string.strip(reqFile),'src.rpm') == -1 and string.find(string.strip(reqFile),'.mvl') > -1:
        reqFileName = string.split(string.strip(reqFile),'/')[-1]
        if string.find(reqFileName,'testsuite') == -1:
          #print 'adding %s...' % reqFileName
          f_minReqApps.write(reqFileName + '\n')
    f_minReqApps.close()
    return 1
  elif list:
    return 1
  else:
    return 0

def systemCmd(cmd,scripttest=0,log=''):
  if scripttest in (1,2):
    if log:
      printlog('\ncommand: ' + cmd + '\n',log)
    else:
      printflush('\ncommand: ' + cmd + '\n')
  if scripttest in (0,2):
    if log:
      msg = os.popen(cmd).read().strip()
      printflush(msg,log,scripttest)
    else:
      return os.system(cmd)
  if scripttest not in (0,1,2):
    if log:
      printlog('\nbad value for scripttest: ' + str(scripttest),log)
      printlog('command: ' + cmd + '\n',log)
    else:
      printflush('\nbad value for scripttest: ' + str(scripttest))
      printflush('command: ' + cmd + '\n')

def fileOpen(file,filestate,scripttest=0):
  # this function was written so we can use scripttest to print the file open commands
  # when testing the scrips
  if scripttest in (1,2):
    printflush("command: open(%s)" % file)
    return 'filehandle'
  elif scripttest in (0,2):
    return open(file,filestate)

def fileWrite(file,msg,scripttest=0):
  if scripttest in (1,2):
    printflush("command: write %s to %s" % (msg,file))
  elif scripttest in (0,2):
    file.write(msg + '\n')

def fileClose(file,scripttest=0):
  if scripttest in (1,2):
    printflush("command: close(%s)" % file)
  elif scripttest in (0,2):
    file.close()

# Source Control Functions

def sourceControlTag(repo,cvspaths,buildtag,collectivelog,scripttest,module=''):
  if string.find(repo,'git') == -1:
    srctype = 'cvs'
    if not module:
      module = '.'
    branch = cvspaths[repo][1]
  elif string.find(repo,'git') > -1:
    srctype = 'git'
    kernelbuildpath = cvspaths[repo][0]
    if cvspaths[repo][4] == 'branch':
      module = 'origin'
    else:
      module = 'build'
    buildrepo = cvspaths[repo][1]
    branch = cvspaths[repo][3]
  if branch == 'null':
    branch = 'HEAD'
  if srctype == 'cvs':
    printflush('Using ' + branch + ' branch of ' + repo + ' repository for module ' + module,collectivelog,scripttest)
    cvscmd = cvsopts + repo + ' rtag -R -F -r ' + branch + ' ' + buildtag + ' ' + module
    systemCmd(cvscmd,scripttest,collectivelog)
  elif srctype == 'git':
    # since git repositories clone and checkout before tagging, this function will do all the
    # git operation and will not do anything in the sourceControlExport function
    printflush("clone %s..." % buildrepo,collectivelog,scripttest)
    systemCmd('%sclone %s/%s' % (gitcmd,gitroot,buildrepo),scripttest,collectivelog)
    os.chdir(kernelbuildpath)
    printflush("checkout %s/%s..." % (module,branch),collectivelog,scripttest)
    systemCmd('%scheckout %s/%s' % (gitcmd,module,branch),scripttest,collectivelog)
    printflush("tag build/%s..." % buildtag,collectivelog,scripttest)
    systemCmd('%stag -a -f -m "Build System Tag" build/%s' % (gitcmd,buildtag),scripttest,collectivelog)
    printflush("push tag...",collectivelog,scripttest)
    systemCmd('%spush --tags' % gitcmd,scripttest,collectivelog)
    printflush("done with git checkout procedure...",collectivelog,scripttest)
    os.chdir('..')

def sourceControlExport(srctype,buildtag,repo,exportPath,collectivelog,scripttest):
  if srctype == 'cvs':
    printflush('Exporting ' + repo + ' repository to ' + exportPath + ' at ' + gettime()+'...',collectivelog,scripttest)
    cvscmd = cvsopts + repo + ' export -R -r ' + buildtag + ' -d ' + repo + ' .'
    systemCmd(cvscmd,scripttest,collectivelog)

def sourceControlChangelog(srctype,repo,starttag,buildtag,cvspaths,changelog,collectivelog,scripttest):
  if srctype == "cvs":
    branch = cvspaths[repo][1]
    if branch != "null":
      systemCmd('mv-changelog --repository %s/%s --start-tag %s --end-tag %s --branch %s >> %s' % (cvsroot,repo,starttag,buildtag,branch,changelog),scripttest,collectivelog)
    else:
      systemCmd('mv-changelog --repository %s/%s --start-tag %s --end-tag %s >> %s' % (cvsroot,repo,starttag,buildtag,changelog),scripttest,collectivelog)
  else:
    os.chdir(cvspaths[repo][0])
    systemCmd('%slog --pretty=full build/%s..build/%s >> %s' % (gitcmd,starttag,buildtag,changelog),scripttest,collectivelog)

def returnAllResources(buildid):
  # this function shoudl be called when a build is ended prematurely (by calling sys.exit(1))
  # it will query the resource manage and find all resources curerently checked out by the build,
  # based on buildid.  It will then check in each resource checked out with the same buildid.
  # Care needs to be used upon using this function.  Examine each instance where sys.exit(1) is called 
  # and be sure that no other build are running...example, the sht or cht builds may be running but the rest
  # of the build has died.  This function was written specifically for when buildprep fails, but it may
  # have broader usage...just be careful when using it.
  import resourceManager
  import Pyro.core

  Pyro.core.initClient(0)
  Pyro.config.PYRO_PRINT_REMOTE_TRACEBACK = 1
  resourceManager = Pyro.core.getProxyForURI("PYROLOC://resource:7766/resource_manager")
  results = resourceManager.resourceQuery(buildid,'b')

  for line in results:
    for item in line:
      if string.find(item,'Resource') > -1:
        resource = string.strip(string.split(item,':')[1])
        printflush('returning resource %s to resource pool...' % resource)
        resourceManager.releaseResource(resource)

def mountinstall(hostname,edition,mounttag,target,scripttest=0,log=''):
  systemCmd('sudo mount -t nfs san:/vol/engr_area/%s/%s/%s /chroot/%s/opt' % (edition,mounttag,target,hostname),scripttest,log)

def umountinstall(hostname,scripttest=0,log=''):
  systemCmd('sudo umount /chroot/%s/opt' % hostname,scripttest,log)

