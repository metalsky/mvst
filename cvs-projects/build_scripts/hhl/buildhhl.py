#!/usr/bin/python
import getopt, traceback, diskuse, buildTimes
import signal #so ctrl-c's go to main thread..
import unpack_buildtars

from buildhhlThreads import * # functions that are threaded
from resourceManager import *
from buildFunctions import *
from builddefs import *
from verifyNode import *

# we define thistest as a variable used to test only buildhhl.py
# it differs from scripttest which is used to test an entire build

if len(sys.argv) == 2 and sys.argv[1] == 'test':
  printflush("Testing buildhhl.py only, no functions from buildhhlThreads.py will run")
  printflush("and no other scripts will be run")
  exec(open('defaultdata.dat'))
  thistest = 1
  scripttest = 1
  buildbranch = "buildbranch"
  mkcd = 0
  runqa = 0
  email = 0
  email_addr = ""
  all_targets = ["<target1>","<target2>"]
  chroothosts = ["<chroothost1>","<chroothost2>"]
  hosts = ["<host1>","<host2>"]
elif len(sys.argv) < 5:
  printflush('usage: %s %s %s %s %s %s %s %s' % (sys.argv[0],'<product>','<buildtag>','<buildid>','<build branch>','<start tag>','[email addr]','[conf=datafile]'))
  printflush("use 'test' in place of <product> to run a scripttest build.")
  sys.exit(1)
else:
  thistest = 0
if len(sys.argv) == 6:
  product = sys.argv[1]
  buildtag = sys.argv[2]
  buildid = sys.argv[3]
  buildbranch = sys.argv[4]
  starttag = sys.argv[5]
  email_addr = ""
  conf = ""
elif len(sys.argv) > 6:
  product = sys.argv[1]
  buildtag = sys.argv[2]
  buildid = sys.argv[3]
  buildbranch = sys.argv[4]
  starttag = sys.argv[5]
  email_addr = sys.argv[6]
  conf = ""

def genTimesPage(current_edition, buildtag,scriptpath):
  #The buildTimes script uses the edition to know where to find the logs, fe is the only one we really need to translate
  if current_edition == "fe":
    current_edition = "foundation"
  elif current_edition == "devstb":
    current_edition = "foundation"

  nodeTimes,solTimes,cygTimes = buildTimes.getBuildTime(current_edition, buildtag)
  if os.path.exists('%s/collectivelogs/%s' % (scriptpath,buildtag)):
    outFile = open('%s/collectivelogs/%s/buildtimes' % (scriptpath,buildtag), 'w')
    outFile.write("NODE TIMES\n")
    outFile.write("##########\n\n")
    for key in nodeTimes.keys():
      outFile.write("%s on %s - Elapsed Time: %s\n"%(key, nodeTimes[key].resource, nodeTimes[key].elapsed))
      
    outFile.write("\n\nSOLARIS TIMES\n")
    outFile.write("#############\n\n")
    for key in solTimes.keys():
      outFile.write("%s on %s - Elapsed Time: %s\n"%(key, solTimes[key].resource, solTimes[key].elapsed))

    outFile.write("\n\nCYGWIN TIMES\n")
    outFile.write("############\n\n")
    for key in cygTimes.keys():
      outFile.write("%s on %s - Elapsed Time: %s\n"%(key, cygTimes[key].resource, cygTimes[key].elapsed))

    outFile.close()
  else:
    printflush('no %s/collectivelogs/%s...not generating build times' % (scriptpath,buildtag),reslog,thistest)

def gencollective(nocl,scriptpath,logdir,buildid,buildtag,hhllog,changelog,reslog,edition):
    printflush("Generating collective pages...",reslog,thistest)
    makeDir('%s/collectivelogs' % scriptpath,thistest)
    for target in abitargets:
      if os.path.exists('%s/apps-%s-%s.log' % (logdir,target,buildid)):
        nonAbiTarget = string.split(target,'-')[0]
        systemCmd('cat %s/apps-%s-%s.log >> %s/apps-%s-%s.log' % (logdir,target,buildid,
                   logdir,nonAbiTarget,buildid),thistest)
    if not nocl:
      if changelog == "":
        changelog = "skipcl"
      collectivecmd = 'cd %s; ./GenCollective %s %s %s >> %s 2>&1' % (scriptpath,logdir + '/hhl-' + buildid + '.log',scriptpath + '/collectivelogs',changelog,hhllog)
      collectivecmdnodb = 'cd %s; ./GenCollective %s %s %s --nodb >> %s 2>&1' % (scriptpath,logdir + '/hhl-' + buildid + '.log',scriptpath + '/collectivelogs',changelog,hhllog)
    else:
      collectivecmd = 'cd %s; ./GenCollective %s %s %s >> %s 2>&1' % (scriptpath,logdir + '/hhl-' + buildid + '.log',scriptpath + '/collectivelogs','skipcl',hhllog)
      collectivecmdnodb = 'cd %s; ./GenCollective %s %s %s --nodb >> %s 2>&1' % (scriptpath,logdir + '/hhl-' + buildid + '.log',scriptpath + '/collectivelogs','skipcl',hhllog)
    # run the collective and capture return code
    printflush("collective command: %s" % collectivecmd,reslog,thistest)
    result = systemCmd(collectivecmd,thistest)
    if result:
      # GenCollective failed, print error mesage and then re-run 
      printflush("result:",reslog,thistest)
      printflush(str(result),reslog,thistest)
      # remove any existing collective lgos
      systemCmd('rm -rf %s/collectivelogs' % scriptpath,thistest)
      # send email then run again with no db
      systemCmd('echo "GenCollective failed for ' + buildtag + '" | /usr/bin/Mail -s "GenCollective Failed for ' + btype + '" build_failures@mvista.com',thistest)
      printflush("Generating collective pages with --nodb, due to previous failure...",reslog,thistest)
      printflush("collective command: %s" % collectivecmdnodb,reslog,thistest)
      systemCmd(collectivecmdnodb,thistest)
    if not scripttest:
      genTimesPage(edition, buildtag, scriptpath)
    else:
      printflush("genTimesPage(edition, buildtag, scriptpath)")
    if os.popen('ls %s/collectivelogs/%s' % (scriptpath,buildtag)).readlines() or thistest: 	 
      printflush("Copying local collective pages from %s/collectivelogs to /export/logs..." % scriptpath,reslog,thistest) 	 
      systemCmd('cp -a %s/collectivelogs/%s /export/logs/temp-%s' % (scriptpath,buildtag,buildid),thistest) 	 
      systemCmd('cd /export/logs; mv temp-%s %s' % (buildid,buildtag),thistest) 	 
      systemCmd('cd /export/logs; rm -f CurrentBuild; ln -s %s CurrentBuild' % buildtag,thistest) 	 
    else: 	 
      printflush("No log directory for Collective...check the logs for errors!",reslog,thistest)                                                                  

# remove exported repositories
def cleanxp(reslog,builddir,cpdir):
  printflush('Removing ' + builddir + '/CVSREPOS...',reslog,thistest)
  os.chdir(builddir + '/../..')
  if os.path.exists(cpdir + '/host/done/mvcygwin'):
    systemCmd('ls | grep -v build_scripts | xargs rm -rf ',thistest)
  else:
    systemCmd('ls | grep -v build_scripts | grep -v cygwin | xargs rm -rf ',thistest)

#-------------------------------------------------------------
# main
#-------------------------------------------------------------
builddir = os.getcwd()
for arg in sys.argv:
  if 'conf=' in arg:
    conf = builddir + '/' + arg.split('=')[1]
if not conf:
  if product in ('fe',):
	conf = builddir + '/fedata.dat'
	product = 'dev'
  # product = fep is a foundation for pro 5.0.24 that does not use licensing.
  elif product in ('fep',):
	conf = builddir + '/feprodata.dat'
	product = 'fe'
  elif product == 'dev':
	conf = builddir + '/devdata.dat'
  elif product == 'devrocket':
	conf = builddir + '/devrocket_dev_data.dat'
  elif product == 'pro':
	conf = builddir + '/pedata.dat'
  elif product == 'proasync':
	conf = builddir + '/peasyncdata.dat'
  elif product == 'cge':
	conf = builddir + '/cgedata.dat'
  elif product == 'mobilinux':
	conf = builddir + '/mobilinuxdata.dat'
  elif product == 'blacktopasync':
	conf = builddir + '/blacktopasyncdata.dat'
	product = 'mobiasync'
  elif product == 'mobiasync':
	conf = builddir + '/mobilinuxasyncdata.dat'
  elif product == 'scripttest':
	conf = builddir + '/scripttestdata.dat'
  elif product == 'stb':
	conf = builddir + '/stbdata.dat'
	product = 'dev'
  elif product == 'devstb':
	conf = builddir + '/devstbdata.dat'
	product = 'dev'
  elif product == 'devusr':
	conf = builddir + '/devusrdata.dat'
	product = 'dev'
  elif product == 'tsuki':
	conf = builddir + '/tsukidata.dat'
  elif product == 'mls':
	conf = builddir + '/licensedata.dat'
  elif product != 'product':
	printflush('Unrecognized product specified...Stopping build.')
	sys.exit(1)
  elif product == 'product':
	conf = 'conf'

f_dat = fileOpen('%s/%s.dat' % (builddir,buildtag), 'a',thistest)
for line in os.popen('cat %s/defaultdata.dat' % builddir).readlines():
  fileWrite(f_dat,line,thistest)
if os.path.exists(conf):
  for line in os.popen('cat %s' % conf).readlines():
    fileWrite(f_dat,line,thistest)
else:
  fileWrite(f_dat,'<conf> lines',thistest)
conf = "%s/%s.dat" % (builddir,buildtag)

# add various variables to buildtag_buildid.dat
fileWrite(f_dat,"product\t\t= '%s'\n" % product,thistest)
fileWrite(f_dat,"buildtag\t= '%s'\n" % buildtag,thistest)
fileWrite(f_dat,"buildid\t\t= '%s'\n" % buildid,thistest)
fileWrite(f_dat,"starttag\t= '%s'\n" % starttag,thistest)
fileClose(f_dat,thistest)
if os.path.exists(conf):
  exec(open(conf))
else:
  printflush('command: exec(open(conf))')
f_dat = fileOpen(conf,'a',thistest)

buildday        = time.strftime('%A', time.localtime(time.time()))
if buildday in uploaddays:
        uploadcds       = 1
else:
        uploadcds       = 0

cpdir = copydir + '/' + buildtag + '/build'
fileWrite(f_dat,"cpdir\t\t= '%s'\n" % cpdir,thistest)
logdir = copydir + '/' + buildtag + '/logs'
fileWrite(f_dat,"logdir\t\t= '%s'\n" % logdir,thistest)
changelog = '%s/%s-%s-%s-Changelog' % (logdir,edition,starttag,buildtag)
fileWrite(f_dat,"changelog\t= '%s'\n" % changelog,thistest)

hhllog = logdir + '/hhl-' + buildid + '.log'
if not thistest:
  reslog = logdir + '/buildhhl-' + buildid + '.log'
else:
  reslog = 'reslog'
fileWrite(f_dat,"reslog\t= '%s'\n" % reslog,thistest)

makeDir(cpdir,thistest)
makeDir(logdir,thistest)

greet = 'Starting buildhhl.py on ' + string.strip(os.popen('uname -n').read()) + \
		' at ' + gettime() + ' on ' + \
		time.strftime('%Y/%m/%d', time.localtime(time.time())) + '\n'
if product == 'fe':
	greet = greet + 'This is a foundation build (product = fe).\n'
elif product == 'dev':
	greet = greet + 'This is a dev foundation build (product = dev).\n'
elif product == 'asyncfe':
	greet = greet + 'This is an async foundation build (product = asyncfe).\n'
else:
	greet = greet + 'This is a ' + product + ' build, using ' + foundation + \
		' foundation build.\n'
	if os.path.islink(foundation):
		realfoundation = os.readlink(foundation)
		greet = greet + '(' + realfoundation + ')\n'
gt = ''
if all_targets:
  greet = greet + 'Building the following architectures:\n'
  for a in all_targets:
    if a not in abitargets:
      gt = gt + a + '\n'
greet = greet + gt + 'Using ' + buildtag + ' for buildtag.\n' + \
	'Using ' + buildid + ' for build_id.\n'
for h in chroothosts:
  greet = greet + h + ' '
greet = greet + '\n'

greet = greet + 'Using ' + buildbranch + ' branch of the build_scripts repository\n'
if cvspaths:
  for repo in cvspaths.keys():
    if string.find(repo,'git') == -1:
      if cvspaths[repo][0] not in('null','skip') and cvspaths[repo][1] == 'null':
        greet = greet + 'Using HEAD branch of ' + repo + ' repository.\n'
      elif cvspaths[repo][0] not in ('null','skip') and cvspaths[repo][1] != 'null':
        greet = greet + 'Using ' + cvspaths[repo][1] + ' branch of ' + repo + ' repository.\n'
    elif string.find(repo,'git') > -1:
      greet = greet + "Using " + cvspaths[repo][1] + " git repository, "
      if cvspaths[repo][4] == 'branch':
        greet = greet + cvspaths[repo][3] + " branch.\n"
      elif cvspaths[repo][4] == 'origin':
        greet = greet + cvspaths[repo][3] + " tag.\n"

if appsfile:
	greet = greet + 'Using ' + appsfile + ' for list of common apps to build.\n'
if lspdat:
	greet = greet + 'Using ' + lspdat + ' for list of lsps to build.\n'
if remoteonly:
	greet = greet + 'Only remote hosts will be built.\n' 
greet = greet + 'Build results will be in ' + cpdir + '.\n' + \
	'Logs will be in ' + logdir
printflush(greet,hhllog,thistest)
if not thistest:
  printlog(greet,reslog)
  printlog(greet,cpdir + '/README.build')
if email:
  printflush("email_addr = " + email_addr,reslog,thistest)
  if email_addr:
	systemCmd('echo "' + greet + '" | /usr/bin/Mail -s "Build starting for ' + btype + '" -c ' + email_addr + ' build_status@mvista.com',scripttest)
  else:
	systemCmd('echo "' + greet + '" | /usr/bin/Mail -s "Build starting for ' + btype + '" build_status@mvista.com',scripttest)

if product in ('bst','devrocket','proadk','propk','scripttest'):
  makekernel = 'skipkernel'
else:
  makekernel = 'makekernel'
fileWrite(f_dat,"makekernel\t= '%s'\n" % makekernel,thistest)
fileWrite(f_dat,"nodetype\t= '%s'\n" % nodetype,thistest)
fileWrite(f_dat,"mktar\t= %s\n" % mktar,thistest)
if sht and cht and hosttoolpath == 'null':
  hosttoolpath = '%s/host-tools/%s' % (copydir,buildtag)
  fileWrite(f_dat,"hosttoolpath\t= '%s'\n" % hosttoolpath,thistest)
  makeDir(hosttoolpath + '/build',scripttest)
# close f_dat for now, we'll re-open it once buildprep is done so we can add kernel and hhlversion
fileClose(f_dat,thistest)

################################################
# build cygwin host tools (cygwin environment)
if cht and not remoteonly and product in ('dev','fe','scripttest'):
  if not thistest:
    chtThread = threading.Thread(target=buildCht,args=(buildtag,buildid,reslog,logdir,builddir,homepath,cvspaths,cygport,collectivelogdir,scripttest))
    chtThread.start()
  else:
    printflush("command: chreating chtThread, for buildCht in buildhhlThreads.py")
    printflush("command: chtThread.start()")

# buildprep
if runprep and not remoteonly: 
    printflush("Running buildprep.py %s .." % gettime(),reslog,thistest)
    logfile = "buildprep-%s.log" % (buildid)
    log = "%s/%s" % (logdir, logfile)
    os.chdir(builddir)
    rprep = systemCmd('%s/buildprep.py %s > %s 2>&1'%(builddir,conf,log),thistest)
    printflush("Finished buildprep.py %s .." % gettime(),reslog,thistest)
    if rprep:
      printflush("buildprep failed.  Stopping build and sending email to build_failures. CHECK RESOURCE MANAGER FOR ANY RESOURCES THAT NEED TO BE CHECKED IN.",reslog,thistest)
      systemCmd('echo "buildprep failed for ' + buildtag + '. CHECK RESOURCE MANAGER TO SEE IF ANY RESOURCES NEED TO BE CHECKED IN." | /usr/bin/Mail -s "Build Failed for ' + btype + '-- CHECK RESOURCE MANAGER" build_failures@mvista.com',scripttest)
      returnAllResources(buildid)
      sys.exit(1)
    getNotBuilt(logdir, logfile, 'host', builddir,scripttest)

f_dat = fileOpen('%s/%s.dat' % (builddir,buildtag), 'a',thistest)
# get kernel and hhlversion
kernelpath              = ""
gitkernel		= 0
if cvspaths:
  for repo in cvspaths.keys():
    if repo in ('mvl-kernel','mvl-kernel-26',):
      kernelpath = cvspaths[repo][0]
    elif string.find(repo,'git-') > -1:
      kernelpath = cvspaths[repo][0]
      gitkernel = 1
kernel = '0.0.0'
hhlversion = 'foo'
if product not in ('mls','tsuki'):
  if os.path.exists(kernelpath) and kernelpath or thistest:
    os.chdir(kernelpath)
    printlog('Running make kernelrelease in %s...' % kernelpath,reslog)
    if 'mvl-kernel-26' in cvspaths.keys():
      systemCmd('make -s LSPTYPE=%s kernelrelease >> %s 2>&1' % (lsptype,reslog),scripttest,reslog)
      if os.path.exists('linux'):
        os.chdir('linux')
        kr = string.strip(os.popen('make LSPTYPE=%s kernelrelease' % lsptype).read())
        tmp = re.match('(.+)_(.+)',kr)
        if tmp:
            kernel = tmp.group(1)
            hhlversion = tmp.group(2)
        else:
          printlog("Failed to get kernel and hhlversion",reslog)
          systemCmd('cp %s %s' % (conf,logdir),scripttest)
          sys.exit(1)
      else:
        if scripttest in (0,2):
          printlog("No linux directory after make kernelrelease",reslog)
          systemCmd('cp %s %s' % (conf,logdir),scripttest,reslog)
          sys.exit(1)
    elif gitkernel:
      printlog('git...run make checksetconfig & make prepare first...',reslog)
      systemCmd('make checksetconfig >> %s 2>&1' % reslog,scripttest,reslog)
      systemCmd('make prepare >> %s 2>&1' % reslog,scripttest,reslog)
      kernelrelease = string.strip(os.popen('make kernelrelease').readline())
      kernel = string.split(kernelrelease,'_')[0]
      hhlversion = string.split(kernelrelease,'_')[1]
fileWrite(f_dat,"kernel\t\t= '%s'\n" % kernel,thistest)
fileWrite(f_dat,"hhlversion\t= '%s'\n" % hhlversion,thistest)
fileClose(f_dat,thistest)
# STOP
if stopbuild:
  sys.exit(1)
# copy conf file to logdir in case it is needed to rebuild something
# this is done regardless of the value for scripttest since we want to be able to check the
# data file when running a scripttest build to validate the data file is correct
systemCmd('cp %s %s' % (conf,logdir),scripttest)
os.chdir(scriptpath)

commonrpmbin = '/opt/montavista/common/bin/mvl-common-rpm'
editionrpmbin = '/opt/montavista/' + edition + '/bin/mvl-edition-rpm'

# copy rpm2cpio.exe for edition builds supporting windows
if product in ('pro','proasync'):
  if os.path.exists("%s/build/installer_rpms/install_area/host/windows2000/bin/rpm2cpio.exe" % (foundation)):
    systemCmd('mkdir -p %s/installer_rpms/install_area/host/windows2000/bin' % (cpdir),scripttest,reslog)
    systemCmd('cp -a %s/build/installer_rpms/install_area/host/windows2000/bin/rpm2cpio.exe %s/installer_rpms/install_area/host/windows2000/bin' % (foundation,cpdir),scripttest,reslog)

#######################################
# link foundation directories for product builds
if product not in ('dev','fe','mls','tsuki'):
  # hardlink SRPMS
  systemCmd('mkdir -p %s/SRPMS' % (cpdir),scripttest,reslog)
  if product not in ('bst','cgeasync','mobiasync','proasync'):
    systemCmd('cd %s/SRPMS; ln %s/build/SRPMS/*.rpm .' % (cpdir,foundation),scripttest,reslog)
    if os.path.exists('%s/SRPMS' % (cpdir)):
      os.chdir('%s/SRPMS' % (cpdir))
    if src_link_exclusions:
      for f in src_link_exclusions:
        systemCmd('ls *%s* | grep -v %s | xargs rm -f' % (f,buildid),scripttest,reslog)
    os.chdir(scriptpath)

  # hardlink host/common
  systemCmd('mkdir -p %s/host/common/optional' % (cpdir),scripttest,reslog)
  systemCmd('cd %s/host/common; ln %s/build/host/common/*.mvl .' % (cpdir,foundation),scripttest,reslog)
  if os.path.exists('%s/host/common' % (cpdir)):
    os.chdir('%s/host/common' % (cpdir))
  if product not in ('proasync','mobiasync','cgeasync'):
    for f in ('eclipse-edition','eclipse-enabler','eclipse-templates'):
      systemCmd('ls *%s* | grep -v %s | xargs rm -f' % (f,buildid),scripttest,reslog)
  if product == "propk":
    systemCmd('cd %s/host/common/optional; ln %s/build/host/common/optional/host-kernel* .' % (cpdir,foundation),scripttest,reslog)
  os.chdir(scriptpath)

  # hardlink host/<host>
  for h in hosts:
    systemCmd('mkdir -p %s/host/%s' % (cpdir, h),scripttest,reslog)
    systemCmd('cd %s/host/%s; ln %s/build/host/%s/*.mvl .' % (cpdir,h,foundation,h),scripttest,reslog)
    systemCmd('cd %s/host/%s/testing; ln %s/build/host/%s/testing/* .' % (cpdir,h,foundation,h),scripttest,reslog)
    if host_link_exclusions:
      for f in host_link_exclusions:
        systemCmd('rm -f %s/host/%s/%s*' % (cpdir,h,f),scripttest,reslog)

  for h in chroothosts:
    systemCmd('mkdir -p %s/host/%s' % (cpdir, h),scripttest,reslog)
    systemCmd('cd %s/host/%s; ln %s/build/host/%s/* .' % (cpdir,h,foundation,h),scripttest,reslog)
    systemCmd('cd %s/host/%s/testing; ln %s/build/host/%s/testing/* .' % (cpdir,h,foundation,h),scripttest,reslog)
    if host_link_exclusions:
      for f in host_link_exclusions:
        systemCmd('rm -f %s/host/%s/%s*' % (cpdir,h,f),scripttest,reslog)

if product not in ('dev','fe','devrocket','mls','tsuki'):
  # copy <arch> directories
  for a in all_targets:
    if a in abitargets:
      continue
    # make <arch>/cross directory
    systemCmd('mkdir -p %s/%s/cross/common' % (cpdir,a),scripttest,reslog)
    # start with <arch>/cross/common
    systemCmd('cd %s/%s/cross/common; ln %s/build/%s/cross/common/*.mvl .' % (cpdir,a,foundation,a),scripttest,reslog)
    # remove the foundation eclipse enabler
    if cross_link_exclusions:
      if os.path.exists('%s/%s/cross/common' % (cpdir,a)):
        for f in cross_link_exclusions:
          systemCmd('rm -f %s/%s/cross/common/*%s*' % (cpdir,a,f),scripttest,reslog)
    # <arch>/cross/<host>
    for h in hosts:
      systemCmd('mkdir -p %s/%s/cross/%s/testing' % (cpdir,a,h),scripttest,reslog)
      systemCmd('cd %s/%s/cross/%s; ln %s/build/%s/cross/%s/*.mvl .' % (cpdir,a,h,foundation,a,h),scripttest,reslog)
      systemCmd('cd %s/%s/cross/%s/testing; ln %s/build/%s/cross/%s/testing/*.mvl .' % (cpdir,a,h,foundation,a,h),scripttest,reslog)
    for ch in chroothosts:
      systemCmd('mkdir -p %s/%s/cross/%s/testing' % (cpdir,a,ch),scripttest,reslog)
      systemCmd('cd %s/%s/cross/%s; ln %s/build/%s/cross/%s/*.mvl .' % (cpdir,a,ch,foundation,a,ch),scripttest,reslog)
      systemCmd('cd %s/%s/cross/%s/testing; ln %s/build/%s/cross/%s/testing/*.mvl .' % (cpdir,a,ch,foundation,a,ch),scripttest,reslog)
if product not in ('bst','dev','fe','devrocket','mls','tsuki'):
  for a in all_targets:
    if a in abitargets:
      continue
    # <arch>/target
    systemCmd('mkdir -p %s/%s/target/optional' % (cpdir,a),scripttest,reslog)
    systemCmd('mkdir -p %s/%s/target/testing' % (cpdir,a),scripttest,reslog)
    systemCmd('cd %s/build/%s/target; ln *.mvl %s/%s/target/' % (foundation,a,cpdir,a),scripttest,reslog)
    if target_link_exclusions:
      for f in target_link_exclusions:
        systemCmd('rm -f %s/%s/target/*%s*' % (cpdir,a,f),scripttest,reslog)
    systemCmd('cd %s/%s/target/optional; ln %s/build/%s/target/optional/*.mvl .' % (cpdir,a,foundation,a),scripttest,reslog)
    systemCmd('cd %s/%s/target/testing; ln %s/build/%s/target/testing/*.mvl .' % (cpdir,a,foundation,a),scripttest,reslog)
    if targopt_link_exclusions:
      if os.path.exists('%s/%s/target/optional' % (cpdir,a)):
        os.chdir('%s/%s/target/optional' % (cpdir,a))
      for f in targopt_link_exclusions:
        systemCmd('ls %s* | grep -v %s | xargs rm -f' % (f,buildid),scripttest,reslog)
    if product in ('cge',):
      if os.path.exists('%s/%s/target/optional' % (cpdir,a)):
        os.chdir('%s/%s/target/optional' % (cpdir,a))
      for f in ('uSDE','libuSDE'):
        systemCmd('mv %s* %s/%s/target' % (f,cpdir,a),scripttest,reslog)

if product == "proasync" and "mips2_fp_le" in all_targets:
  systemCmd('mkdir -p %s/mips2_fp_le/lsps/philips-pnx8950/common' % cpdir,scripttest,reslog)
  systemCmd('cd %s/mips2_fp_le/lsps/philips-pnx8950/common; ln %s/mips2_fp_le/lsps/philips-pnx8950/common/*.mvl .' % (cpdir,foundation),scripttest,reslog)
elif x11apps:
  # move X11 apps from target/ to target/optional/
  # this is done by deleting the links just created above and making new links
  for a in all_targets:
    if a in abitargets:
      continue
    for app in x11apps:
      systemCmd('rm -f %s/%s/target/%s-*' % (cpdir,a,app),scripttest,reslog)
      systemCmd('cd %s/build/%s/target; ln %s-*.mvl %s/%s/target/optional' % (foundation,a,app,cpdir,a),scripttest,reslog)
    systemCmd('rm -f %s/%s/target/optional/xorg-x11-fonts-*' % (cpdir,a),scripttest,reslog)
    systemCmd('cd %s/build/%s/target; ln xorg-x11-fonts-*.mvl %s/%s/target' % (foundation,a,cpdir,a),scripttest,reslog)


####End of linking stuff#######
os.chdir(scriptpath)
conditionDict = {}
eventDict = {}
runsht	= 0
# This isn't synchronous with other things here, we can check to see if its done later 
# by doing a shtThread.join() to block until this thread is done
if 'solaris8' in hosts and not remoteonly and product in ('dev','fe','scripttest'):
  if not thistest:
    shtThread = threading.Thread(target=buildSolarisHost,args=(logdir, buildtag, buildid, product, homepath, reslog, builddir, hosttoolpath, sht, collectivelogdir, scripttest))
    shtThread.start()
    runsht = 1
  else:
    printflush("command: creating shtThread for buildSolarisHost in buildhhlThreads.py")
    printflush("command: shtThread.start()")


#This probably won't work right with the threaded version
if sht_only:
  if not thistest:
    shtThread.join()
  else:
    printflush("command: shtThread.join()")
  sys.exit(1)

# run buildremotehost for solaris and linux chroots to build all common (except solaris) and all
# host apps

hostThrdList = []
for brh in chroothosts:
  if not thistest:
    hostThrdList.append(threading.Thread(target=chrootHostBuild,args=(brh,conf,reslog)))
  else:
    hostThrdList.append(brh + '-thrd')
    printflush("command: adding %s thread to hostThreadList for chrootHostBuild in buildhhlThreads.py()" % brh)

if 'solaris8' in hosts or thistest:
  if not thistest:
    eventDict['solaris8'] = threading.Event()  
    solarisHostThrd = threading.Thread(target=solarisRemoteHostBuild,args=(eventDict['solaris8'],conf,reslog))
    solarisHostThrd.start()
  else:
    printflush("command: creathing threading.Event() for solaris8")
    printflush("command: creating solarisHostThrd for solarisRemoteHostBuild in buildhhlThreads.py")
    printflush("command: solarisHostThrd.start()")

#Let's start the work
for thrd in hostThrdList:
  if not thistest:
    thrd.start()
  else:
    printflush("command: thrd.start() for %s" % thrd)

####Moved commented lines to buildhhlThreads.py#####
# run buildcommoncygwin which will build common-rpm, host-rpm, and all common- apps
# so that it is only build once for cygwin, rather than for every target
if 'windows2000' in hosts or thistest:
  if not thistest:
    eventDict['windows2000'] = threading.Event()
    commonCygwinThrd = threading.Thread(target=buildCommonCygwin,args=(eventDict['windows2000'],buildtag,buildid,reslog,logdir,scriptpath,product,edition,cvspaths,cpdir,installdir,cygport,collectivelogdir,scripttest))
    commonCygwinThrd.start()
  else:
    printflush("command: creating windows2000 threading.Event()")
    printflush("command: creating commonCygwinThrd for buildCommonCygwin() in buildhhlThreads.py")
    printflush("command: commonCygwinThrd.start()")

for thrd in hostThrdList:
  if not thistest:
    thrd.join()
  else:
    printflush("command: thrd.join() for %s" % thrd)

# copy docs
if 'Documentation' in cvspaths.keys() and docsmodule != 'skip':
  if product in ('mobilinux','pro','proadk','cge'):
    if os.path.exists('%s/%s' % (cvspaths['Documentation'][0],docsmodule)):
      systemCmd('cp -a %s/%s/* %s' % (cvspaths['Documentation'][0],docsmodule,cpdir),scripttest,reslog)
    else:
      printlog('No docs exported not coping docs to %s' % (cpdir),reslog)

# parrallel build stuff

# Turns out each target needs a condition object, that is, one target build 
# can flag multiple hosts to start we're gonna use a dictionary, the targets are the keys
#######################################
# STOP
if stopbuild:
  sys.exit(1)

for target in all_targets:
  if target not in abitargets:
    if not thistest:
      conditionDict[target] = threading.Condition() #new condition object made per TARGET
    else:
      printflush("command: creating threading.Condition() for %s" % target)


node_threads = []
for targetToBuild in all_targets:
  if targetToBuild not in abitargets:
    if not thistest:
      t = threading.Thread(target=node_thread, name=targetToBuild, args=(targetToBuild,conf,conditionDict[targetToBuild],reslog,builddir))
    else:
      t = targetToBuild + '-thrd'
      printflush("command: creating %s thread for node_thread in buildhhlThreads.py" % t)
  else:
    nonAbiTarget = string.split(targetToBuild,'-')[0]
    if not thistest:
      t = threading.Thread(target=node_thread, name=targetToBuild, args=(targetToBuild,conf,conditionDict[nonAbiTarget],reslog,builddir))
    else:
      t = targetToBuild + '-thrd'
      printflush("command: creating %s thread (using %s condition) for node_thread in buildhhlThreads.py" % (t,nonAbiTarget))
  node_threads.append(t)
  if thistest:
    printflush("command: appending thread %s to node_threads" % t)

host_threads = []

if multihost: #always multihost?
  for name in hosts:
    for target in all_targets:
      if target not in abitargets:
        printflush("Making thread for host: %s target:%s at %s"%(name,target,gettime()),reslog,thistest)
        if not thistest:
          t = threading.Thread(target=host_thread,args=(name,conditionDict[target],eventDict[name],reslog,conf,builddir,target))
        else:
          t = name + '-' + target + '-thrd'
          printflush("command: creating %s host thread for host_thread() in buildhhlThreads.py" % t)
        host_threads.append(t)
  

#ready, set, go..
for t in host_threads + node_threads:
  if not thistest:
    t.start()
  else:
    printflush("command: %s.start()" % t)

#wait for node threads..
if thistest:
  printflush("Waiting for target builds to complete (node_threads join)")
else:
  printlog("Waiting for target builds to complete (node_threads join) at %s" % gettime(),reslog)
for t in node_threads:
  if not thistest:
    t.join()
  else:
    printflush("command %s.join()" % t)
if not thistest:
  printlog("Finished waiting for target builds to complete (node_threads join) at %s" % gettime(),reslog)
else:
  printflush("Finished waiting for target builds to complete (node_threads join)")

#let host threads know we're done, then wait for them to finish
if not thistest:
  printlog("Waiting for host (solaris/windows) builds to complete (host_threads join) at %s" % gettime(),reslog)
else:
  printflush("Waiting for host (solaris/windows) builds to complete (host_threads join)")
for t in host_threads:
  if not thistest:
    t.join()
  else:
    printflush("command: %s.join()" % t)
if not thistest:
  printlog("Finished waiting for host (solaris/windows) builds to complete (host_threads join) at %s" % gettime(),reslog)
else:
  printflush("Finished waiting for host (solaris/windows) builds to complete (host_threads join)")

# get BUILD ERROR messages for buildsolarishost
if 'solaris8' in hosts:
  getNotBuilt(logdir, 'sht-' + buildid + '.log', 'sht', builddir,scripttest)

# for bst builds, remove all links so that only bst rpms remain, then re-link the host-kernel rpm
if product == 'bst':
  prodir = ('/mvista/release_area/pro/mvl310')
  if os.path.exists(cpdir):
    os.chdir(cpdir)
  for f in os.popen('find').readlines():
    if not os.path.isdir(string.strip(f)) and os.stat(string.strip(f))[3] > 1:
      systemCmd('rm -f ' + string.strip(f),scripttest,reslog)
  systemCmd('cd %s/host/common/; ln %s/host/common/optional/host-kernel* .' % (cpdir,prodir),scripttest,reslog)


#Sychronization of threads here before we make cds

if 'solaris8' in hosts and not remoteonly and runsht:
  if not thistest:
    printlog("Waiting for solaris host tool build to complete at %s" % gettime(),reslog)
    shtThread.join()
    printlog("solaris host tool build completed at %s" % gettime(),reslog)
    getNotBuilt(logdir, 'sht-' + buildid + '.log', 'sht', builddir,scripttest)
  else:
    printflush("Waiting for solaris host tool build to complete")
    printflush("command: shtThread.join()")
    printflush("solaris host tool build completed")

if 'windows2000' in hosts:
  if not thistest:
    printlog("Waiting for common cygwin build to complete at %s" % gettime(),reslog)
    commonCygwinThrd.join()
    printlog("common cygwin build completed at %s" % gettime(),reslog)
  else:
    printflush("Waiting for common cygwin build to complete")
    printflush("command: commonCygwinThrd.join()")
    printflush("common cygwin build completed")

if 'solaris8' in hosts:
  if not thistest:
    printlog("Waiting for solaris host build to complete at %s" % gettime(),reslog)
    solarisHostThrd.join()
    printlog("solaris host build completed at %s" % gettime(),reslog)
  else:
    printflush("Waiting for solaris host build to complete")
    printflush("command: solarisHostThrd.join()")
    printflush("solaris host build completed")

if cht and not remoteonly and product in ('dev','fe') or thistest:
  if not thistest:
    printlog("Waiting for cygwin environment build to complete at %s" % gettime(),reslog)
    chtThread.join()
    printlog("cygwin environment build completed at %s" % gettime(),reslog)
  else:
    printflush("Waiting for cygwin environment build to complete")
    printflush("command: chtThread.join()")
    printflush("cygwin environment build completed")

# link files from hosttoolpath to build area
if product not in ('bst','devrocket','mls','tsuki') and hosttoolpath != 'null':
  printlog("linking host-tools rpms from %s at %s" % (hosttoolpath,gettime()),reslog)
  # add host-tools
  systemCmd('mkdir -p %s/host-tools/solaris8' % (cpdir),scripttest,reslog)
  systemCmd('cd %s/host-tools/solaris8; ln %s/build/host-tools/solaris8/* .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s/SRPMS; ln %s/build/SRPMS/host-tool* .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('mkdir -p %s/host-tools/windows2000/RPMS' % (cpdir),scripttest,reslog)
  systemCmd('mkdir -p %s/host-tools/windows2000/SRPMS' % (cpdir),scripttest,reslog)
  systemCmd('cd %s; ln %s/build/autorun.inf .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s; ln %s/build/mvista.ico .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s/host-tools/windows2000; ln %s/build/host-tools/windows2000/setup* .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s/host-tools/windows2000; ln %s/build/host-tools/windows2000/webinstall-start* .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s/host-tools/windows2000/SRPMS; ln %s/build/host-tools/windows2000/SRPMS/* .' % (cpdir,hosttoolpath),scripttest,reslog)
  systemCmd('cd %s/host-tools/windows2000/RPMS; ln %s/build/host-tools/windows2000/RPMS/* .' % (cpdir,hosttoolpath),scripttest,reslog)

# remove foundation versions of common-apt-rpm-config and apt-rpm-config from editions
# which rebuilt them and only used the foundation versions in order to get common-apt-rpm and
# apt-rpm installed during the foundation install steps
if product in ('cge','mobilinux','pro'):
  for a in all_targets:
    if a in abitargets:
      continue
    os.chdir('%s/%s/target' % (cpdir,a))
    for f in os.popen('ls apt-rpm-config*').readlines():
      if buildid not in f.strip():
        systemCmd('rm -f %s' % f.strip(),scripttest,reslog)
  for h in hosts:
    os.chdir('%s/host/%s' % (cpdir,h))
    for f in os.popen('ls common-apt-rpm-config*').readlines():
      if buildid not in f.strip():
        systemCmd('rm -f %s' % f.strip(),scripttest,reslog)
    for f in os.popen('ls host-apt-rpm-config*').readlines():
      if buildid not in f.strip():
        systemCmd('rm -f %s' % f.strip(),scripttest,reslog)
  for h in chroothosts:
    os.chdir('%s/host/%s' % (cpdir,h))
    for f in os.popen('ls common-apt-rpm-config*').readlines():
      if buildid not in f.strip():
        systemCmd('rm -f %s' % f.strip(),scripttest,reslog)
    for f in os.popen('ls host-apt-rpm-config*').readlines():
      if buildid not in f.strip():
        systemCmd('rm -f %s' % f.strip(),scripttest,reslog)


#######################################
# STOP
if stopbuild:
  sys.exit(1)

#make cds

# for foundation builds, append the posttargetapps apps list to the normal list
if product in ('dev','fe','f3') and 'windows2000' in hosts or thistest:
  for target in all_targets:
    if os.path.exists('%s/%s/MVL-foundation-postapps-%s-%s' % (cpdir,target,target,buildid)):
      systemCmd('cat %s/%s/MVL-foundation-postapps-%s-%s >> %s/%s/MVL-foundation-apps-%s-%s' % (cpdir,target,target,buildid,cpdir,target,target,buildid),scripttest,reslog)
      systemCmd('rm -f %s/%s/MVL-foundation-postapps-%s-%s' % (cpdir,target,target,buildid),scripttest,reslog)

# for edition builds with windows, append the list of minimum required apps from the foundation build
# to the list generated by the edition build.

if product in ('cge','mobilinux','pro') and 'windows2000' in hosts or thistest:
  for target in all_targets:
    systemCmd('cat %s/build/etc/config/volume/MVL-foundation-apps-%s-* >> %s/%s/MVL-%s-apps-%s-%s' % (foundation,target,cpdir,target,product,target,buildid),scripttest,reslog)

# for 'dev' builds, remove glibc-bootstrap* rpm from cpdir since glibc will be rebuilt
if product in ('dev',):
  for target in all_targets:
    if target not in abitargets:
      systemCmd('mkdir -p %s/%s/target/bsglibc' % (cpdir,target),scripttest,reslog)
      if os.path.exists('%s/%s/target/bsglibc' % (cpdir,target)):
        systemCmd('mv %s/%s/target/*bootstrap* %s/%s/target/bsglibc' % (cpdir,target,cpdir,target),scripttest,reslog)
      elif os.path.exists('%s/%s/target/optional' % (cpdir,target)):
        msg = 'Missing target/bsglibc directory, moving glibc-bootstrap-libs rpms to target/optional.\nThese must be removed manually if the build is to be used for release.'
        systemCmd('echo "' + msg + '" | /usr/bin/Mail -s "WARNING: Build Issue for ' + btype + '" build@mvista.com',scripttest)
        systemCmd('mv %s/%s/target/*bootstrap* %s/%s/target/optional' % (cpdir,target,cpdir,target),scripttest,reslog)
      else:
        msg = 'Missing target/bsglibc and target/optional directories, removing glibc-bootstrap-libs rpms.'
        systemCmd('echo "' + msg + '" | /usr/bin/Mail -s "WARNING: Build Issue for ' + btype + '" build@mvista.com',scripttest)
        systemCmd('rm -f %s/%s/target/*bootstrap*' % (cpdir,target),scripttest,reslog)

if 's124atom' in buildtag:
  # remove xorg-x11 rpms
  #if x11remove:
    #for f in x11remove:
      os.chdir('%s/SRPMS' % cpdir)
      systemCmd('rm -f xorg-x11*',scripttest)
      for t in all_targets:
        os.chdir('%s/%s/target' % (cpdir,t))
        systemCmd('rm -f xorg-x11*',scripttest)
        os.chdir('%s/%s/target/optional' % (cpdir,t))
        systemCmd('rm -f xorg-x11*',scripttest)

#install the installers and create the cdimages
if mkcd: 
  cddir = copydir + '/' + buildtag + '/cdimages'
  dvddir = copydir + '/' + buildtag + '/dvdimages'
  logfile = "cdimages-%s.log" % (buildid)
  log = "%s/%s" % (logdir, logfile)
  os.chdir(scriptpath)
  while 1:
    cdnode = getResource(buildtag,buildid,nodetype,"Running installimage.py")
    cdnodeVerify = verifyNode(cdnode,'none')
    if cdnodeVerify == SUCCESS:
      break
    elif cdnodeVerify == FAIL:
      msg = 'verifyNode failed for %s in %s in mkcd' % (cdnode,buildtag)
      subject = 'verifyNode Failed for %s' % cdnode
      logmsg = '%s failed verification, it will remain checked out using %s buildtag' % (cdnode,buildtag)
      mailError(msg,subject,cdnode,buildtag,logmsg,reslog)
  if thistest:
    printflush("Making cd images at %s on %s..." % (gettime(),cdnode),reslog,thistest)
  else:
    printlog("Making cd images at %s on %s..." % (gettime(),cdnode),reslog)
  systemCmd('ssh %s "cd %s; %s/installimage.py %s > %s 2>&1"' % (cdnode,builddir,builddir,conf,log),thistest)
  if thistest:
    printflush("Finished making cd images at %s ..." % gettime(),reslog,thistest)
  else:
    printlog("Finished making cd images at %s ..." % gettime(),reslog)
  releaseResource(cdnode)
  if product in ('proasync','cgeasync','mobiasync') or thistest:
    if not thistest:
      printlog("Linking released images...",reslog)
    else:
      printflush("Linking released images...",reslog,thistest)
    for target in lspIsos.keys():
      systemCmd('mkdir -p %s/%s' % (dvddir,target),scripttest,reslog)
      if os.path.exists(dvddir + '/' + target):
        os.chdir(dvddir + '/' + target)
      if extrareleaseimgs and target in extrareleaseimgs.keys():
        imgpath = extrareleaseimgs[target]
      else:
        imgpath = releaseimgpath
      for isotype in ('src','docs'):
        systemCmd('ln -s %s/%s* .' % (imgpath,isotype),scripttest,reslog)
        systemCmd('cat %s/README.md5sum | grep %s >> README.md5sum' % (imgpath,isotype),scripttest,reslog)
      for isotype in ('host',):
        if string.find(target,'uclibc') > -1:
          linktarget = string.split(target,'_uclibc')[0]
        else:
          linktarget = target
        systemCmd('ln -s %s/*%s*%s* .' % (imgpath,isotype,linktarget),scripttest,reslog)
        systemCmd('cat %s/README.md5sum | grep %s | grep %s >> README.md5sum' % (imgpath,isotype,linktarget),scripttest,reslog)
      if not thistest:
        printlog("Linking lsp images...",reslog)
      else:
        printflush("Linking lsp images...",reslog,thistest)
      systemCmd('ln -s %s/%s/lsps-* .' % (cddir,target),scripttest,reslog)
      systemCmd('cat %s/%s/README.md5sum >> README.md5sum' % (cddir,target),scripttest,reslog)

  # upload images
#I wonder how much we can get away with here, can we do this and some of the other copying at the same time?   
  if uploadcds:
    os.chdir(builddir)
    if product in ('cge',):
      # tempe upload
      systemCmd('./tempe.upload ' + buildtag + ' ' + product + ' ' + buildid,scripttest,reslog)

# copy devrocket cdimages from devrocketpath
#if os.path.exists(devrocketpath + '/cdimages') and mkcd:
#  os.chdir(cddir)
#  os.system('ln %s/cdimages/devrocket* .' % (devrocketpath))
  
if runqa:
  if not thistest:
    printlog("QA Trigger: runqa = %s" % runqa,reslog)
    printlog("Running QA setup %s .." % gettime(),reslog)
  else:
    printflush("QA Trigger: runqa = %s" % runqa,reslog,thistest)
    printflush("Running QA setup %s .." % gettime(),reslog,thistest)
  if product not in ('mls','tsuki') and not scripttest:
    result = os.popen('ssh ferret -l ferret bin/kickit qalx/buildtrigger %s 2>&1' % buildtag).read()
    if "Defaulting" in result:
      print result
    else:
      # send error message to QA email list
      os.system('echo "%s" | /usr/bin/Mail -s "[Ferret Trigger Failure] %s" qa_ferret_alert@mvista.com' % (result,buildtag))
  elif product == 'tsuki':
    systemCmd('ssh tbuild@indra.sh.mvista.com bin/kickit %s' % buildtag,scripttest,reslog)

# should probably get resource for this so multiple builds dont run chkrpms on same node
if chkrpms:
  if not thistest:
    printlog('Checking for bad magic:',reslog)
  else:
    printflush('Checking for bad magic:',reslog,thistest)
  os.chdir(builddir)
  systemCmd('chkrpms %s' % (cpdir),scripttest,reslog)

fini = 'Finished buildhhl.py on ' + string.strip(os.popen('uname -n').read()) + \
         ' finished at ' + gettime() + ' on ' + \
         time.strftime('%Y/%m/%d', time.localtime(time.time())) + '\n' + \
         'Logs appear on the Collective at: http://collective.sh.mvista.com/logs/' + \
         buildtag + '/build.shtml\n'
ft = ''
if all_targets:
  fini = fini + 'Builds were attempted for the following architectures:\n'
  for a in all_targets:
    if a not in abitargets:
      ft = ft + a + '\n'
fini = fini + ft + 'The buildtag was ' + buildtag + '\n' + \
          'The build_id was ' + buildid + '\n'
fini = fini + 'Used ' + buildbranch + ' branch of the build_scripts repository\n'
if cvspaths:
  for repo in cvspaths.keys():
    if cvspaths[repo][0] not in ('null','skip') and cvspaths[repo][1] == 'null':
      fini = fini + 'Used HEAD branch of ' + repo + ' repository.\n'
    elif cvspaths[repo][0] not in ('null','skip') and cvspaths[repo][1] != 'null':
      fini = fini + 'Used ' + cvspaths[repo][1] + ' branch of ' + repo + ' repository.\n'
if appsfile:
	fini = fini + appsfile + ' was used for the list of common apps to build.\n'
fini = fini + 'Used the following nodes:\n'

#for n in nodes:
#  fini = fini + n + ' '
fini = fini + '\nUsed the following hosts:\n'
for h in hosts:
  fini = fini + h + ' '
for h in chroothosts:
  fini = fini + h + ' '
fini = fini + '\n'
#if sht:
#  fini = fini + 'Used ' + shthost + ' for sht build.'
#if cht:
#  fini = fini + 'Used ' + chthost + ' for cht build.\n'
if remoteonly:
    fini = fini + 'Only remote hosts were built.\n'
fini = fini + 'Build results are in ' + cpdir + '.\n' + \
          'Logs are in ' + logdir
fini = fini + '\n\n\nCD Diff:'
if not thistest:
  printlog(fini,reslog)
else:
  printflush(fini,reslog,thistest)

if email:
  if email_addr:
    systemCmd('echo "' + fini + '" | /usr/bin/Mail -s "Build finished for ' + btype + '" -c ' + email_addr + ' build_status@mvista.com',scripttest)
  else:
    systemCmd('echo "' + fini + '" | /usr/bin/Mail -s "Build finished for ' + btype + '" build_status@mvista.com',scripttest)

# touch build.done in cpdir, so QA can determine when build is finished
systemCmd('touch %s/build.done' % (cpdir),scripttest)

# get disk usage for all hosts
# this needs to be done before the multilib log files are appended to the non-multilib build since
# each is done on a single node

# [s|c]ht-<buildid>.log 	- usage for host environment build (solaris & cygwin)
# host-<hostname>-<buildid>.log - usage for common/host builds
# <targethost>-<target>-<buildid>.log + apps-<target>-<buildi>.log + lsp-<target>-<build>.log
#				- usage for core build + apps & lsps, all done on one node
# <hostname>-<target>-<build>.log
#				- usage for cross host build
#
# [s|c]ht-<buildid>.log
if 'solaris8' in hosts:
  logfile = '%s/sht-%s.log' % (logdir,buildid)
  if os.path.exists(logfile):
    printlog('sht build used %s k-bytes\n' % diskuse.getusage(logfile),reslog)
if cht:
  logfile = '%s/cht-%s.log' % (logdir,buildid)
  if os.path.exists(logfile):
    printlog('cht build used %s k-bytes\n' % diskuse.getusage(logfile),reslog)

# host-<hostname>-<buildid>.log
for host in chroothosts:
  logfile = '%s/host-%s-%s.log' % (logdir,host,buildid)
  if os.path.exists(logfile):
    printlog('host build for %s used %s k-bytes\n' % (host,diskuse.getusage(logfile)),reslog)
for host in hosts:
  logfile = '%s/host-%s-%s.log' % (logdir,host,buildid)
  if os.path.exists(logfile):
    printlog('host build for %s used %s k-bytes' % (host,diskuse.getusage(logfile)),reslog)
printlog('\n',reslog)

# targethost cross build
for target in all_targets:
  totalUsage = 0
  # <targethost>-<target>-<buildid>.log
  logfile = '%s/%s-%s-%s.log' % (logdir,targethost,target,buildid)
  if os.path.exists(logfile):
    totalUsage = totalUsage + diskuse.getusage(logfile)
  # apps-<target>-<buildid>.log
  logfile = '%s/apps-%s-%s.log' % (logdir,target,buildid)
  if os.path.exists(logfile):
    totalUsage = totalUsage + diskuse.getusage(logfile)
  # lsp-<target>-<buildid>.log
  logfile = '%s/lsp-%s-%s.log' % (logdir,target,buildid)
  if os.path.exists(logfile):
    totalUsage = totalUsage + diskuse.getusage(logfile)
  printlog('target & lsp build (including cross toolchain build on %s) for %s used %s k-bytes' % 
          (targethost,target,str(totalUsage)),reslog)
  if target in abitargets:
    printlog('...multilib target builds were for target apps only, cross toolchain built with non-multilib target build',reslog)
  printlog('\n',reslog)

# non-targethost cross builds
for host in chroothosts:
  if host != targethost:
    for target in all_targets:
      logfile = '%s/%s-%s-%s.log' % (logdir,host,target,buildid)
      if os.path.exists(logfile):
        printlog('%s cross build for %s used %s k-bytes' % (host,target,diskuse.getusage(logfile)),reslog)
printlog('\n',reslog)
for host in hosts:
  if host != targethost:
    for target in all_targets:
      logfile = '%s/%s-%s-%s.log' % (logdir,host,target,buildid)
      if os.path.exists(logfile):
        printlog('%s cross build for %s used %s k-bytes' % (host,target,diskuse.getusage(logfile)),reslog)
printlog('\n',reslog)

if os.path.exists(homepath + '/dynamicCollectiveLogs'):
  systemCmd('cp -a %s/%s %s' % (homepath,'dynamicCollectiveLogs',logdir),scripttest)

if not remoteonly:
  try:
    gencollective(nocl,scriptpath,logdir,buildid,buildtag,hhllog,changelog,reslog,edition)
  except:
    sys.stderr.write('There was a problem running GenCollective')
    traceback.print_exc()

# remove exported repositories
#This has to change, we can't clean like this
if cleanexp:
  cleanxp(reslog,builddir,cpdir)

# make link that edition builds can use as latest foundation
if mkretardlink and product != 'tsuki':
  if os.path.exists(logdir):
    os.chdir(logdir)
    corelist = os.popen('ls %s-*.log' % targethost).readlines()
    resultlist = os.popen('ls result*.log').readlines()
    if len(corelist) == len(resultlist):
      print "all cores failed, skipping link"
    else:
      if os.path.exists(copydir):
        os.chdir(copydir)
        systemCmd('rm -f %s' % linkname,scripttest,reslog)
        systemCmd('ln -s %s %s' % (buildtag,linkname),scripttest,reslog)
elif mkretardlink and product == 'tsuki':
  if os.path.exists(copydir):
    os.chdir(copydir)
  systemCmd('rm -f %s' % linkname,scripttest,reslog)
  systemCmd('ln -s %s %s' % (buildtag,linkname),scripttest,reslog)
if mkretardlink and (sht or cht):
  # make link for last host-tool build
  if os.path.exists('/mvista/dev_area/foundation/host-tools'):
    os.chdir('/mvista/dev_area/foundation/host-tools')
  systemCmd('rm -f %s' % linkname,scripttest,reslog)
  systemCmd('ln -s %s %s' % (buildtag,linkname),scripttest,reslog)

# make link for last devrocket build
if product == 'devrocket':
  if os.path.exists(copydir):
    os.chdir(copydir)
  systemCmd('rm -f %s' % linkname,scripttest,reslog)
  systemCmd('ln -s %s %s' % (buildtag,linkname),scripttest,reslog)

# if mktar is true, run unpack_buildtars.unpackTars(product, buildtag)
if mktar:
  if product in ('dev','fe'):
    product = 'foundation'
  elif 's124' in buildtag or 's127' in buildtag or 's129' in buildtag:
    product = 'mvl'
  untarlog = '%s/untar-%s.log' % (logdir,buildid)
  systemCmd('touch %s' % untarlog,scripttest)
  untarProduct = product
  #if untarProduct == 'dev':
  #  untarProduct = 'fe'
  try:
    unpack_buildtars.unpackTars(untarProduct, buildtag, untarlog)
  except:
    traceback.print_exc()
    printlog("Error installing tars, check the exception...\n",reslog)
    sys.exit(1)

