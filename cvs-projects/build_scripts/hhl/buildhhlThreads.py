#!/usr/bin/python

##########################
#   buildhhlThreads.py
#
# We're going to be doing more and more threading in buildhhl.py
# This module contains the functions that we will thread, functions
# previously contains in buildhhl.py were moved here for neatness
#
##########################

from resourceManager import *
from buildFunctions import *
from builddefs import *
from verifyNode import *

#-------------------------------------------------------------
# Thread spawned for each parrallel build node
#-------------------------------------------------------------

#################################
#       node_thread()
#
#################################
# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def node_thread(target,conf,condition,reslog,builddir,thistest=0):
  # adding some debug commands to determine why buildcore.py is running from 
  # <cpdir>/<target>/target/optional instead of scriptpath for pro edition build
  if not thistest:
    exec(open(conf)) #This will save us passing in all sorts of stuff
  else:
    abitargets = ("target-abi",)
    buildtag = "buildtag"
    buildid = "buildid"
    nodetype = "node"
    targethost = "targethost"
    logdir = "/tmp"
    scripttest = 1
    scriptpath = "scriptpath"
    libraryapps = "libraryapps"
    appsfile = "appsfile"
    toolsonly = 0
    product = "product"
    lsps = 1
    remoteonly = 0
    chroothosts = ("host1","host2")
    cpdir = "/cpdir"

  rval = 0
  if target not in abitargets:
    while 1:
      node = getResource(buildtag, buildid, nodetype, "Building %s"%(target))
      nodeVerify = verifyNode(node,targethost)
      if nodeVerify == SUCCESS:
        break
      elif nodeVerify == FAIL:
        msg = 'verifyNode failed for %s in %s in node_thread' % (node,buildtag)
        subject = 'verifyNode Failed for %s' % node
        logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (node,buildtag)
        mailError(msg,subject,node,buildtag,logmsg,reslog,scripttest)
    logfile = "%s-%s-%s.log" % (targethost, target, buildid)
    log = "%s/%s" % (logdir, logfile)
    systemCmd('touch %s' % (log),scripttest)
    if not remoteonly:
      printlog("building target %s on node %s in %s chroot at %s" % (target,node,targethost,gettime()),reslog)
      res = systemCmd('ssh %s "cd %s; ./buildcore.py %s %s %s> %s 2>&1"' % (node,scriptpath,conf,target,targethost,log),thistest)
      printlog("Result of running buildcore.py for %s: %s" % (target,str(res)),reslog)
      getNotBuilt(logdir, logfile, target, builddir,thistest)

    # check status of buildcore
    # if <cpdir>/host/done/core-<target> exists, buildcore succeeded
    # if <logdir>/result-<target> exists, some component of the toolchain build failed
    # if neither exist, buildcore.py most likely crashed w/ a script error
    if os.path.exists(cpdir + '/host/done/core-' + target) or thistest:
      rval = 0
    elif os.path.exists(logdir + '/result-' + target):
      rval = 1
    else:
      rval = 2
    logfile = "apps-%s-%s.log" % (target, buildid)
    log = "%s/%s" % (logdir, logfile)
    systemCmd('touch %s' % (log),scripttest)
    logfile = "lsp-%s-%s.log" % (target, buildid)
    log = "%s/%s" % (logdir, logfile)
    systemCmd('touch %s' % (log),scripttest)

    if rval == 0 and toolsonly == 0:
      #Now, queue target for non-linux host build...
      logfile = "apps-%s-%s.log" % (target, buildid)
      log = "%s/%s" % (logdir, logfile)
      # build library and dev apps
      res = systemCmd('ssh %s "cd %s; ./buildtargetapps.py %s %s %s %s null 1 >> %s 2>&1"' %
               (node, scriptpath, conf, target, targethost, libraryapps, log),thistest)
      printlog("Result of running buildtargetapps.py (libraryapps) for %s: %s" % (target,str(res)),reslog)
      if not thistest:
        condition.acquire()
        condition.notifyAll()
        condition.release()

      # now build commonapps for all builds
      if appsfile:
        res = systemCmd('ssh %s "cd %s; ./buildtargetapps.py %s %s %s %s null 2 >> %s 2>&1"' %
                 (node, scriptpath, conf, target, targethost, appsfile, log),thistest)
        printlog("Result of running buildtargetapps.py (commonapps) for %s: %s" % (target,str(res)),reslog)
      #This is the old location for building lsps...if lsps are broke due to the initramfs changes
      #uncomment this block and comment the other initramfs blocks
      #if lsps:
      #  logfile = "lsp-%s-%s.log" % (target, buildid)
      #  log = "%s/%s" % (logdir, logfile)
      #  os.system('ssh %s "cd %s; ./buildlsp.py %s %s %s > %s 2>&1"' %
      #           (node, scriptpath, conf, target, targethost, log))
      #  getNotBuilt(logdir, logfile, target,builddir)

      # run arch specific target apps
      if string.find(target,'arm') > -1 or string.find(target,'ppc') > -1 or string.find(target,'x86') > -1 or string.find(target,'mips') > -1 or thistest:
        if product in ('dev','fe','product'):
          logfile = "apps-%s-%s.log" % (target, buildid)
          log = "%s/%s" % (logdir, logfile)
          if string.find(target,'arm') > -1:
            archappfile = 'armapps.dat'
          elif string.find(target,'ppc') > -1:
            archappfile = 'ppcapps.dat'
          elif string.find(target,'x86') > -1:
            archappfile = 'x86apps.dat'
          elif string.find(target,'mips') > -1:
            archappfile = 'mipsapps.dat'
          elif string.find(target,'xtensa') > -1:
            archappfile = 'xtensaapps.dat'
          elif product == "product":
            archappfile = "archappfile"
          res = systemCmd('ssh %s "cd %s; ./buildtargetapps.py %s %s %s %s null 3 >> %s 2>&1"' %
                   (node, scriptpath, conf, target, targethost, scriptpath + '/' + archappfile, log),thistest)
          printlog("Result of running buildtargetapps.py (archapps) for %s: %s" % (target,str(res)),reslog)
      # run posttargetapps.py
      logfile = "%s-%s-%s.log" % (targethost, target, buildid)
      log = "%s/%s" % (logdir, logfile)
      if product in ('cge','mobilinux','dev','fe','pro','scripttest','product'):
        res = systemCmd('ssh %s "cd %s; ./posttargetapps.py %s %s %s >> %s 2>&1"' %
                 (node, scriptpath, conf, target, targethost, log),thistest)
        printlog("Result of running posttargetapps.py for %s: %s" % (target,str(res)),reslog)
      else:
        systemCmd('touch %s' % (log),scripttest)

      if product not in ('pro','product'):
        getNotBuilt(logdir, logfile, target, builddir,thistest)
      if product in ('pro','product'):
        logfile = "apps-%s-%s.log" % (target, buildid)
        log = "%s/%s" % (logdir, logfile)
        res = systemCmd('ssh %s "cd %s; ./buildtargetapps.py %s %s %s %s null 4 0 >> %s 2>&1"' %
                 (node,scriptpath,conf,target,targethost,scriptpath + '/pemvltapps.dat',log),thistest)
        printlog("Result of running buildtargetapps.py for %s: %s" % (target,str(res)),reslog)
        getNotBuilt(logdir, logfile, target, builddir,thistest)
      # this is the new location for the lsps build for initramfs changes...if lsps are broke,
      # comment this block
      if lsps:
        logfile = "lsp-%s-%s.log" % (target, buildid)
        log = "%s/%s" % (logdir, logfile)
        res = systemCmd('ssh %s "cd %s; ./buildlsp.py %s %s %s > %s 2>&1"' %
                 (node, scriptpath, conf, target, targethost, log),thistest)
        printlog("Result of running buildlsp.py for %s: %s" % (target,str(res)),reslog)
        getNotBuilt(logdir, logfile, target,builddir,thistest)

    if not remoteonly and (rval == 0 or (rval == 2 and product in ('devrocket',))):
      # Start chrooted host builds
      for h in chroothosts:
        if h != targethost:
          releaseResource(node)
        if h == 'centos3_64':
          while 1:
            node = getResource(buildtag, buildid, "node-64", target + " 64bit Cross Build")
            nodeVerify = verifyNode(node,h)
            if nodeVerify == SUCCESS:
                break
            elif nodeVerify == FAIL:
              msg = 'verifyNode failed for %s in %s in node_thread' % (node,buildtag)
              subject = 'verifyNode Failed for %s' % node
              logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (node,buildtag)
              mailError(msg,subject,node,buildtag,logmsg,reslog,scripttest)
          uname = 'linux64'
        elif h != targethost:
          while 1:
            node = getResource(buildtag, buildid, "node", target + " Cross Build")
            nodeVerify = verifyNode(node,h)
            if nodeVerify == SUCCESS:
                break
            elif nodeVerify == FAIL:
              msg = 'verifyNode failed for %s in %s in node_thread' % (node,buildtag)
              subject = 'verifyNode Failed for %s' % node
              logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (node,buildtag)
              mailError(msg,subject,node,buildtag,logmsg,reslog,scripttest)
          uname = ''
        if h != targethost:
          logfile = "%s-%s-%s.log" % (h, target, buildid)
          log = "%s/%s" % (logdir, logfile)
          # now chroot into the host environment, and run the build script
          bcmd='ssh %s "cd %s; %s ./%s %s %s %s" > %s 2>&1' % (node,
                scriptpath,uname,'buildremote.py',conf,h,target,log)
          res = systemCmd(bcmd,thistest)
          printlog("Result of running buildremote.py for %s on %s: %s" % (target,h,str(res)),reslog)

    # if buildcore failed...
    elif not remoteonly and rval == 1:
      printlog("*** buildcore failed target %s" % target,reslog)
      #Now, queue target for non-linux host build...
      condition.acquire()
      condition.notifyAll()
      condition.release()
    elif not remoteonly and rval == 2 and product != 'devrocket':
      printlog("*** no results from buildcore.py for %s.  Possible script error." % target,reslog)
      #Now, queue target for non-linux host build...
      condition.acquire()
      condition.notifyAll()
      condition.release()
    printlog("completed target %s on node %s at %s" % (target, node, gettime()),reslog)
    releaseResource(node)

  elif target in abitargets:
    nonAbiTarget = string.split(target,'-')[0]
    abi = string.split(target,'-')[1]
    if not thistest:
      condition.acquire()
      condition.wait()
      condition.release()
    if os.path.exists(cpdir + '/host/done/core-' + nonAbiTarget) or thistest:
      while 1:
        node = getResource(buildtag, buildid, nodetype, "Building %s"%(target))
        nodeVerify = verifyNode(node,targethost)
        if nodeVerify == SUCCESS:
          break
        elif nodeVerify == FAIL:
          msg = 'verifyNode failed for %s in %s in node_thread' % (node,buildtag)
          subject = 'verifyNode Failed for %s' % node
          logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (node,buildtag)
          mailError(msg,subject,node,buildtag,logmsg,reslog,scripttest)
      if product in ('dev','fe','product'):
        if string.find(nonAbiTarget,'mips64') > -1:
          archappfile = mips64apps
        elif nonAbiTarget in ("ppc_9xx",):
          archappfile = ppc9xxapps
        elif nonAbiTarget in ('x86_amd64','x86_em64t'):
          archappfile = em64tapps
        else:
          archappfile = scriptpath + '/abiarchappfile'
      elif product in ('cge',):
        archappfile = scriptpath + '/cgeabiapps.dat'
      elif product in ('scripttest',):
        archappfile = scriptpath + '/scripttestabiapps.dat'
      else:
        archappfile = ''
      if archappfile:
        logfile = "apps-%s-%s.log" % (target, buildid)
        log = "%s/%s" % (logdir, logfile)
        printlog("building target %s on node %s in %s chroot at %s" % (target,node,targethost,gettime()),reslog)
        res = systemCmd('ssh %s "cd %s; ./buildtargetapps.py %s %s %s %s %s multilib-%s >> %s 2>&1"' %
                 (node,scriptpath,conf,target,targethost,archappfile,abi,abi,log),thistest)
        printlog("Result of running buildtargetapps.py for %s with abi of %s: %s" % (target,abi,str(res)),reslog)
      # this is the new location for the lsps build for initramfs changes...if lsps are broke,
      # comment this block
      if lsps:
        logfile = "lsp-%s-%s.log" % (target, buildid)
        log = "%s/%s" % (logdir, logfile)
        res = systemCmd('ssh %s "cd %s; ./buildlsp.py %s %s %s > %s 2>&1"' %
                 (node, scriptpath, conf, nonAbiTarget, targethost, log),thistest)
        printlog("Result of running buildlsp.py for %s: %s" % (target,str(res)),reslog)
        getNotBuilt(logdir, logfile, nonAbiTarget,builddir,thistest)

      printlog("completed target %s on node %s at %s" % (target, node, gettime()), reslog)
      releaseResource(node)
    else:
      printlog("skipping target %s since core build failed...%s" % (target,gettime()),reslog)


#################################################
#                 host_thread
#
#
#################################################
#We have to make similar changes as we did above in node_thread
#These need to get their own node, and should only be assigned a target
#Although a semaphore is used for synchronization, this needs to be looked at
#To see what exactly its doing and if we need it or if there is a better way

#The semaphore is used as a counter here
#The queue functions call release() to bump the counter by one
#This causes all aquire() calls to block waiting for release() to be called by other functions
#This semaphore should be made a global var instead of passed around

#The locks somewhat necessary still, targetlist will still be a shared resource although 
#python's Queue module may be more appropriate for the interprocess communication, this is something
#we can look into later

# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def host_thread(name, targetCondition, hostEvent, reslog,conf,builddir,target,thistest=0):
  if not thistest:
    exec(open(conf))
    targetCondition.acquire()      #make sure we're atomic,
    targetCondition.wait()
    targetCondition.release()
    if os.path.exists(cpdir + '/host/done/core-' + target):
      pass
    elif os.path.exists(logdir + '/result-' + target):
      return
    else:
      return
  else:
    # define some varibales used for testing buildhhlThreads.py only
    scripttest = 1
    scriptpath = "scriptpath"
    cpdir = "cpdir"
    installdir = "installdir"
    edition = "edition"
    cvspaths = {'toolchain': ['toolchainpath',],}

  #printlog("building target %s for %s on %s at %s" % (target, name, host, gettime()),reslog)
  if name == 'solaris8':
    logfile = "%s-%s-%s.log" % (name, target, buildid)
    log = "%s/%s" %(logdir, logfile)
    # make dynamic collective log dir
    makeDir('%s/%s/host/solaris8' % (collectivelogdir,target), scripttest)
    #if target not in ('arm_iwmmxt_le','arm_iwmmxt_le_uclibc','arm_iwmmxt2_le','arm_iwmmxt2_le_uclibc','arm_v6_vfp_be','arm_v6_vfp_le','arm_v6_vfp_le_uclibc','arm_v7_vfp_le','arm_v7_vfp_le_uclibc','arm_v5t_arm_le_uclibc'):
    printlog('solaris thread for %s waiting for required common/host rpms in host-solaris build at %s' % (target, gettime()),reslog)
    printlog('solaris thread for %s waiting for required common/host rpms in host-solaris build at %s' % (target, gettime()),log)
    if not thistest:
      hostEvent.wait()      #make sure we're atomic,
    while 1:
      host = getResource(buildtag,buildid,"solaris","Building solaris host for %s"%(target))
      hostVerify = verifyNode(host,'solaris8')
      if hostVerify == SUCCESS:
        break
      elif hostVerify == FAIL:
        msg = 'verifyNode failed for %s in %s in host_thread' % (host,buildtag)
        subject = 'verifyNode Failed for %s' % host
        logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (host,buildtag)
        mailError(msg,subject,host,buildtag,logmsg,reslog,scripttest)
    printlog("building target %s for %s on %s at %s" % (target, name, host, gettime()),reslog)
    printlog("building target %s for %s on %s at %s" % (target, name, host, gettime()),log)
    systemCmd('ssh root@%s "rm -rf /chroot/solaris8/opt/montavista"' % (host),scripttest)
    systemCmd('ssh root@%s "cd /chroot/solaris8/opt; tar -xf /opt/montavista.f3.tar"' % (host),scripttest)
    systemCmd('ssh root@%s "chown -fR build:engr /chroot/solaris8/opt/montavista"' % (host),scripttest)
    bcmd='ssh root@%s "cd %s; ./%s %s %s %s" >> %s 2>&1' % (host,scriptpath,'buildremote.py',conf,name,target,log)
    res = systemCmd(bcmd,thistest)
    printlog("Result of running buildremote.py for %s on solaris: %s" % (target,str(res)),reslog)
    printlog("Result of running buildremote.py for %s on solaris: %s" % (target,str(res)),log)
    if not thistest:
      os.chdir(builddir)
    getNotBuilt(logdir, logfile, target, builddir,thistest)
    releaseResource(host)
    #else:
    #  systemCmd('touch %s' % log,scripttest)

  elif name == 'windows2000':
    # change this to use the hostEvent if the f3 cygwin environment ever gets stable
    printlog("Windows build for %s waiting for %s/host/done/common-cygwin" % (target,cpdir),reslog)
    if not thistest:
      while not os.path.exists('%s/host/done/common-cygwin' % cpdir):
        systemCmd('sleep 300',scripttest)
    printlog("Windows build for %s found %s/host/done/common-cygwin" % (target,cpdir),reslog)
    while 1:
      host = getResource(buildtag,buildid,"cygwin","Cygwin host for %s"%(target))
      hostVerify = verifyNode(host,'cygwin-' + cygport)
      if hostVerify == SUCCESS:
        break
      elif hostVerify == FAIL:
        msg = 'verifyNode failed for %s in %s in host_thread' % (host,buildtag)
        subject = 'verifyNode Failed for %s' % host
        logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (host,buildtag)
        mailError(msg,subject,host,buildtag,logmsg,reslog,scripttest)
    printlog("building target %s for %s on %s at %s" % (target, name, host, gettime()),reslog)
    script = 'buildcygwin'
    path = '/home/build/dailybuild'
      #print 'copying cygwin build script:'
      #print 'scp -P %s %s/%s %s:%s' % (cygport,scriptpath, script, host, path)
    systemCmd('scp -P %s %s/%s %s:%s' % (cygport,scriptpath, script, host, path),scripttest)
    systemCmd('ssh -p %s %s "cd %s; rm -rf BUILD RPMS SRPMS SOURCES SPECS; mkdir -p BUILD RPMS SRPMS SOURCES SPECS"' % (cygport,host, path),scripttest)
    #if product in ('dev','fe') and 'toolchain' in cvspaths.keys() or thistest:
    #  for td in ('binutils','gcc'):
    #    systemCmd('scp -P %s %s/%s/SOURCES/* %s:%s/SOURCES' % (cygport,cvspaths['toolchain'][0],td,host,path),scripttest)
    #    systemCmd('scp -P %s %s/%s/SPECS/cross* %s:%s/SPECS' % (cygport,cvspaths['toolchain'][0],td,host,path),scripttest)
    #printlog('--> running %s/%s on %s (%s)...' % (path, script, host, name),reslog)
    logfile = "%s-%s-%s.log" %(name, target, buildid)
    log = "%s/%s" %(logdir, logfile)
    if 'mvlt' in cvspaths.keys():
      tmpmvltpath = cvspaths['mvlt'][0]
    else:
      tmpmvltpath = 'null'
    printlog("building target %s for %s on %s at %s" % (target, name, host, gettime()),log)
    res = systemCmd('ssh -p %s %s "%s/%s %s %s %s %s %s %s %s %s %s" >> %s 2>&1' %
             (cygport,host, path, script, 'overlord', cpdir, target, buildid,
              installdir, product, tmpmvltpath, edition, gcclicense, log),thistest)
    printlog("Result of running buildcygwin for %s on windows2000: %s" % (target,str(res)),reslog)
    if not thistest:
      os.chdir(builddir)
    getNotBuilt(logdir, logfile, target, builddir,thistest)
    releaseResource(host)

  printlog("completed %s cross tools for target %s at %s" % (name, target, gettime()),reslog)


########################
#  buildSolarisHost()
#
#Build Solaris Host Tools
#
##########################

# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def buildSolarisHost(logdir, buildtag, buildid, product, homepath, reslog, builddir, hosttoolpath, sht, collectivelogdir, scripttest):
  log = "%s/sht-%s.log" % (logdir, buildid)
  # make dynamic collective log dir
  makeDir('%s/hosttool/solaris' % collectivelogdir, scripttest)
  while 1:
    shthost = getResource(buildtag, buildid, "solaris", "Building Solaris Host Tools")
    shthostVerify = verifyNode(shthost,'solaris8')
    if shthostVerify == SUCCESS:
      break
    elif shthostVerify == FAIL:
      msg = 'verifyNode failed for %s in %s in buildSolarisHost' % (shthost,buildtag)
      subject = 'verifyNode Failed for %s' % shthost
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (shthost,buildtag)
      mailError(msg,subject,shthost,buildtag,logmsg,reslog,scripttest)
  printlog("Running buildsolarishost on %s at %s .." % (shthost,gettime()),log)
  printlog("Running buildsolarishost on %s at %s .." % (shthost,gettime()),reslog)
  systemCmd('ssh root@%s "rm -rf /chroot/solaris8/opt/montavista"' % (shthost),scripttest)
  systemCmd('ssh root@%s "cd /chroot/solaris8/opt; tar -xf /opt/montavista.f3.tar"' % (shthost),scripttest)
  systemCmd('ssh root@%s "chown -fR build:engr /chroot/solaris8/opt/montavista"' % (shthost),scripttest)
  systemCmd('ssh root@%s "ls -la /chroot/solaris8/opt/montavista" >> %s 2>&1' % (shthost,log),scripttest)
  res = systemCmd('ssh root@%s "cd %s; %s %s %s %s %s %s %s %s %s" >> %s 2>&1' % (shthost,builddir,
             builddir + '/buildsolarishost.py',buildid,homepath,buildtag,product,hosttoolpath,sht,collectivelogdir,scripttest,log),scripttest)
  printlog("Result of running buildsolarishost.py: %s" % str(res),reslog)
  releaseResource(shthost)
  return 


# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def chrootHostBuild(brh,conf,reslog,thistest=0):
  exec(open(conf)) #This will save us passing in all sorts of stuff
  logfile = "host-%s-%s.log" % (brh, buildid)
  log = "%s/%s" % (logdir, logfile)
  # make dynamic collectivelogdir
  makeDir('%s/hostapps/%s' % (collectivelogdir,brh), scripttest)
  uname = ''
  if product == 'tsuki':
    resourcetype = nodetype
    resourcetag = "tsuki chroot Host Build"
  elif brh == 'centos3_64':
    resourcetype = "node-64"
    resourcetag = "64bit chroot Host Build"
    uname = 'linux64'
  else:
    resourcetype = nodetype
    resourcetag = "chroot Host Build"
  while 1:
     chrootHostNode = getResource(buildtag, buildid, resourcetype, resourcetag)
     chrootHostNodeVerify = verifyNode(chrootHostNode,brh)
     if chrootHostNodeVerify == SUCCESS:
       break
     elif chrootHostNodeVerify == FAIL:
       msg = 'verifyNode failed for %s in %s in chrootHostBuild' % (chrootHostNode,buildtag)
       subject = 'verifyNode Failed for %s' % chrootHostNode
       logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (chrootHostNode,buildtag)
       mailError(msg,subject,chrootHostNode,buildtag,logmsg,reslog,scripttest)
  #Here we used to do a loop that grabbed nodes, we don't need to do this anymore
  #For as many hosts as we wants, each time this function is called it will wait until a node is available
  # chroot into the host environment, and run the build script
  printlog("Running buildremotehost.py on %s at %s .." % (chrootHostNode,gettime()),log)
  printlog("Running buildremotehost.py on %s at %s .." % (chrootHostNode,gettime()),reslog)
  bcmd='ssh %s "cd %s; %s ./%s %s %s" >> %s 2>&1' % (chrootHostNode,scriptpath,uname,'buildremotehost.py',conf,brh,log)
  res = systemCmd(bcmd,thistest)
  printlog("Result of running buildremotehost.py on %s: %s" % (brh,str(res)),reslog)
  releaseResource(chrootHostNode)
  return


# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def solarisRemoteHostBuild(solarisEvent,conf,reslog,thistest=0):
  exec(open(conf)) #This will save us passing in all sorts of stuff
  while 1:
    solarisNode = getResource(buildtag,buildid,"solaris","Solaris RemoteHost Build")
    solarisNodeVerify = verifyNode(solarisNode,'solaris8')
    if solarisNodeVerify == SUCCESS:
      break
    elif solarisNodeVerify == FAIL:
      msg = 'verifyNode failed for %s in %s in solarisRemoteHostBuild' % (solarisNode,buildtag)
      subject = 'verifyNode Failed for %s' % solarisNode
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (solarisNode,buildtag)
      mailError(msg,subject,solarisNode,buildtag,logmsg,reslog,scripttest)
  systemCmd('ssh root@%s "rm -rf /chroot/solaris8/opt/montavista"' % (solarisNode),thistest)
  systemCmd('ssh root@%s "cd /chroot/solaris8/opt; tar -xf /opt/montavista.f3.tar"' % (solarisNode),thistest)
  systemCmd('ssh root@%s "chown -fR build:engr /chroot/solaris8/opt/montavista"' % (solarisNode),thistest)
  # run buildremotehost.py in background
  logfile = "host-%s-%s.log" % ('solaris8', buildid)
  log = "%s/%s" % (logdir, logfile)
  # make dynamic collective log dir
  makeDir('%s/hostapps/solaris8' % collectivelogdir, scripttest)
  printlog("Running buildremotehost.py on %s at %s .." % (solarisNode,gettime()),log)
  printlog("Running buildremotehost.py on %s at %s .." % (solarisNode,gettime()),reslog)
  # chroot into the host environment, and run the build script
  bcmd='ssh root@%s "cd %s; ./%s %s %s" >> %s 2>&1' % (solarisNode,scriptpath,'buildremotehost.py',conf,
       'solaris8',log)
  res = systemCmd(bcmd,thistest)
  printlog("Result of running buildremotehost.py on solaris: %s" % str(res),reslog)
  solarisEvent.set()
  releaseResource(solarisNode)
  return


###################
#  buildCommonCygwin
#
#################

# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def buildCommonCygwin(cygwinEvent,buildtag,buildid,reslog,logdir,scriptpath,product,edition,cvspaths, cpdir,installdir,cygport,collectivelogdir,scripttest):
  printlog("Windows common/host build waiting for %s/common-noarch-done at %s" % (logdir,gettime()),reslog)
  if scripttest in (0,2):
    while not os.path.exists('%s/common-noarch-done' % logdir):
      systemCmd('sleep 300',scripttest)
  printlog("Windows common/host build found %s/common-noarch-done at %s" % (logdir,gettime()),reslog)
  while 1:
    commonCygwinNode = getResource(buildtag, buildid, "cygwin", "Running buildcommoncygwin")
    commonCygwinNodeVerify = verifyNode(commonCygwinNode,'cygwin-' + cygport)
    if commonCygwinNodeVerify == SUCCESS:
      break
    elif commonCygwinNodeVerify == FAIL:
      msg = 'verifyNode failed for %s in %s in buildCommonCygwin' % (commonCygwinNode,buildtag)
      subject = 'verifyNode Failed for %s' % commonCygwinNode
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (commonCygwinNode,buildtag)
      mailError(msg,subject,commonCygwinNode,buildtag,logmsg,reslog,scripttest)
  path = '/home/build/dailybuild'
  printlog("Running buildcommoncygwin on %s at %s ..." % (commonCygwinNode,gettime()),reslog)
  systemCmd('scp -P %s %s/%s %s:%s' % (cygport,scriptpath,'buildcommoncygwin',commonCygwinNode,path),scripttest)
  systemCmd('ssh -p %s %s "cd %s; rm -rf BUILD RPMS SRPMS SOURCES SPECS; mkdir -p BUILD RPMS SRPMS SOURCES SPECS"' % (cygport,commonCygwinNode,path),scripttest)
  if 'mvl-installer' in cvspaths.keys() and cvspaths['mvl-installer'][0] not in ('skip','null'):
    tmpmvlinstpath = cvspaths['mvl-installer'][0]
    printlog('### copying installer SOURCES & SPECS to ' + commonCygwinNode + ' ###',reslog)
    systemCmd('scp -P %s %s/SPECS/* %s:%s/SPECS' % (cygport,tmpmvlinstpath,commonCygwinNode,path),scripttest)
    systemCmd('scp -P %s %s/SOURCES/* %s:%s/SOURCES' %
             (cygport,tmpmvlinstpath,commonCygwinNode,path),scripttest)
  else:
    tmpmvlinstpath = 'null'
  logfile = "host-windows2000-%s.log" % buildid
  log = "%s/%s" %(logdir, logfile)
  # make dynamic collective log dir
  makeDir('%s/hostapps/windows2000' % collectivelogdir, scripttest)
  printlog("Running buildcommoncygwin on %s at %s ..." % (commonCygwinNode,gettime()),log)
  if string.find(buildtag,'fthree') > -1:
    cmncygproduct = 'f3'
  else:
    cmncygproduct = product
  res = systemCmd('ssh -p %s %s "cd %s; %s/%s %s %s %s %s %s %s %s %s %s" >> %s 2>&1' %
           (cygport,commonCygwinNode,path,path,'buildcommoncygwin','overlord',cpdir,
            buildid,installdir,cmncygproduct,edition,tmpmvlinstpath,buildtag,scripttest,log),scripttest)
  printlog("Result of running buildcommoncygwin: %s" % str(res),reslog)
  releaseResource(commonCygwinNode)
  # notify target threads for windows host build
  cygwinEvent.set()
  return


################################
#  buildCht
#
################################
# If you add arguments to this function, be sure to update the arguments in the TEST call at the bottom
# of this script
def buildCht(buildtag,buildid,reslog,logdir,builddir,homepath,cvspaths,cygport,collectivelogdir,scripttest):
  # start chtbuild on chthost
  while 1:
    chthost = getResource(buildtag,buildid,"cygwin","Running buildmvcygwin...")
    chthostVerify = verifyNode(chthost,'cygwin-' + cygport)
    if chthostVerify == SUCCESS:
      break
    elif chthostVerify == FAIL:
      msg = 'verifyNode failed for %s in %s in buildCht' % (chthost,buildtag)
      subject = 'verifyNode Failed for %s' % chthost
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (chthost,buildtag)
      mailError(msg,subject,chthost,buildtag,logmsg,reslog,scripttest)
  log = "%s/cht-%s.log" % (logdir, buildid)
  # make dynamic collective log directory
  makeDir('%s/hosttool/cygwin' % collectivelogdir,scripttest)
  printlog("Running buildmvcygwin on %s, at %s ..." % (chthost,gettime()),reslog)
  printlog("Running buildmvcygwin on %s, at %s ..." % (chthost,gettime()),log)
  if 'cygwin' in cvspaths.keys():
    tmpcygpath = cvspaths['cygwin'][1]
  else:
    tmpcygpath = 'null'
  systemCmd('cd %s'%(builddir),scripttest)
  res = systemCmd('%s/%s %s %s %s %s %s %s %s %s %s > %s 2>&1' %
     (builddir,'buildmvcygwin',homepath,buildtag,buildid,chthost,tmpcygpath,'noskip',cygport,collectivelogdir,scripttest,log),scripttest)
  printlog("Result of running buildmvcygwin:",reslog)
  printlog(str(res),reslog)
  releaseResource(chthost)
  printlog("Finished buildmvcygwin on %s, at %s ..." % (chthost,gettime()),reslog)
  return

def cleanTestLogs(logs):
    os.system('cat /tmp/buildhhlThreads.log')
    os.system('rm -f /tmp/buildhhlThreads.log')
    for log in logs:
      os.system('cat /tmp/' + log)
      os.system('rm -f /tmp/' + log)

def usage():
  print "usage: %s %s" % (sys.argv[0],"<test option>")
  print "valid <test option> includes:"
  print "cht:\t\ttests buildCht()"
  print "cmncyg:\t\ttests buildCommonCygwin()"
  print "sht:\t\ttests buildSolarisHost()"
  print "solhst:\t\ttests solarisRemoteHostBuild()"
  print "chrthst:\ttests chrootHostBuild()"
  print "hst:\t\ttests host_thread()"
  print "node:\t\ttests node_thread()"

def main():
  if len(sys.argv) == 1 or len(sys.argv) > 2:
    usage()
    sys.exit(1)
  elif len(sys.argv) == 2:
    TEST = sys.argv[1]
  reslog = "/tmp/buildhhlThreads.log"
  if TEST == "cht":
    printflush("Testing buildCht()")
    cvspaths = {}
    buildCht("buildtag","buildid",reslog,"/tmp","builddir","homepath",cvspaths,"cygport",1)
    cleanTestLogs(['cht-buildid.log',])
  elif TEST == "cmncyg":
    printflush("Testing buildCommonCygwin()")
    cvspaths = {}
    cygwinEvent = threading.Event()
    buildCommonCygwin(cygwinEvent,"buildtag","buildid",reslog,"/tmp","scriptpath","product","edition",cvspaths,"cpdir","installdir","cygport",1)
    cleanTestLogs(['host-windows2000-buildid.log',])
  elif TEST == "sht":
    printflush("Testing buildSolarisHost()")
    buildSolarisHost("/tmp","buildtag","buildid","product","homepath",reslog,"builddir","hosttoolpath","sht",1)
    cleanTestLogs(['sht-buildid.log',])
  elif TEST == "solhst":
    printflush("Testing solarisRemoteHostBuild()")
    solarisEvent = threading.Event()
    solarisRemoteHostBuild(solarisEvent,"buildtag","buildid","/tmp","scriptpath","conf",reslog,1)
    cleanTestLogs(['host-solaris8-buildid.log',])
  elif TEST == "chrthst":
    printflush("Testing chrootHostBuild()")
    chrootHostBuild("buildtag","0000000","host","/tmp","scriptpath","defaultdata.dat","product",reslog,1)
    cleanTestLogs(['host-host-0000000.log',])
  elif TEST == "hst":
    printflush("Testing host_thread() for solaris8")
    hostEvent = threading.Event()
    targetCondition = threading.Condition()
    host_thread("solaris8",targetCondition,hostEvent,reslog,"conf","builddir","target",1)
    cleanTestLogs(['solaris8-target-buildid.log',])
    printflush("Testing host_thread() for windows2000")
    host_thread("windows2000",targetCondition,hostEvent,"buildtag","buildid",reslog,"/tmp","conf","product","cygport","builddir","target",1)
    cleanTestLogs(['windows2000-target-buildid.log',])
  elif TEST == "node":
    printflush("Testing node_thread()")
    condition = threading.Condition()
    node_thread("target","defaultdata.dat",condition,reslog,"builddir",1)
    cleanTestLogs(['targethost-target-buildid.log','apps-target-buildid.log','lsp-target-buildid.log','host1-target-buildid.log','host2-target-buildid.log'])
  else:
    print "Unknown test option: %s" % TEST
    usage()

if __name__ == "__main__":
  main()

