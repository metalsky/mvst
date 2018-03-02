#!/usr/bin/python
import rpm
from resourceManager import *
from buildFunctions import *

# this script performs the tagging, cleaning and exporting of all repositories.

dontclean = ['CVS','CVSROOT','README','placeholder','Makefile','Makefile.reverse',
             'Makefile.stdtargets','Rules.make','Rules.nobuild', 'buildrc' ]

if len(sys.argv) != 2:
  print '\nusage: %s %s' % (sys.argv[0],'<configfile>')
  print '\n# of args = ' + str(len(sys.argv))
  print '\nHere are the args:'
  for x in sys.argv:
    print x
  sys.exit(1)

def makeResultsDirs():
 # make cpdir
  speciallsps = ()
  if not os.path.exists(cpdir):
    os.system('mkdir -p ' + cpdir)
  if product not in ('mls','tsuki'):
    makeDir(cpdir + '/SRPMS',scripttest)
    makeDir(cpdir + '/host',scripttest)
    makeDir(cpdir + '/host/common/optional',scripttest)
    makeDir(cpdir + '/host/done',scripttest)
    if product in ('dev','fe') and speciallsps:
      makeDir(cpdir + '/host/lsps',scripttest)
      for sl in speciallsps:
        makeDir(cpdir + '/host/lsps/' + sl,scripttest)
        for host in hosts:
          makeDir(cpdir + '/host/lsps/' + sl + '/' + host,scripttest)
        for host in chroothosts:
          makeDir(cpdir + '/host/lsps/' + sl + '/' + host,scripttest)
    if product in ('dev','fe'):
      makeDir(cpdir + '/host-tools/windows2000',scripttest)
    for host in hosts:
      makeDir(cpdir + '/host/' + host,scripttest)
      if product in ('cge',):
        makeDir(cpdir + '/host/' + host + '/optional',scripttest)
      makeDir(cpdir + '/host/' + host + '/testing',scripttest)
      makeDir(cpdir + '/installer_rpms/host/' + host,scripttest)
    for host in chroothosts:
      makeDir(cpdir + '/host/' + host,scripttest)
      if product in ('cge',):
        makeDir(cpdir + '/host/' + host + '/optional',scripttest)
      makeDir(cpdir + '/host/' + host + '/testing',scripttest)
      makeDir(cpdir + '/installer_rpms/host/' + host,scripttest)
    makeDir(cpdir + '/installer_rpms/install_area/host',scripttest)
    makeDir(cpdir + '/installer_rpms/docs-cd',scripttest)
    makeDir(cpdir + '/installer_rpms/install_area/docs-cd',scripttest)
  # now make directories for collective logs
  # the dynamicCollectiveLogs directory is on /home/build until
  # all testing is complete, at which point these commands will need to change 
  # to ssh commands for overlord:/export/logs/<buildtag>
  for target in all_targets:
    if target in abitargets:
      continue
    makeDir(collectivelogdir + '/' + target + '/app',scripttest)
    makeDir(collectivelogdir + '/' + target + '/cds',scripttest)
    makeDir(collectivelogdir + '/' + target + '/host',scripttest)
    makeDir(collectivelogdir + '/' + target + '/html',scripttest)
    makeDir(collectivelogdir + '/' + target + '/lsp',scripttest)
    makeDir(collectivelogdir + '/' + target + '/postapp',scripttest)
    makeDir(collectivelogdir + '/' + target + '/stats',scripttest)
    for host in hosts:
      makeDir(collectivelogdir + '/' + target + '/host',scripttest)
    for host in chroothosts:
      makeDir(collectivelogdir + '/' + target + '/host',scripttest)
  makeDir(collectivelogdir + '/buildprep',scripttest)
  makeDir(collectivelogdir + '/hostapps',scripttest)
  makeDir(collectivelogdir + '/hosttool',scripttest)

def applyModuleLabel(repo,cvspaths,module,collectivelog):
  sourceControlTag(repo,cvspaths,buildtag,collectivelog,scripttest,module)
                                                                                                              
def applyLabel(repo,cvspaths,collectivelog,):
  sourceControlTag(repo,cvspaths,buildtag,collectivelog,scripttest)
  
def cvsstuff():
  os.chdir(homepath)
  for repo in cvspaths.keys():
    collectivelog = collectivelogdir + '/buildprep/' + repo
    mstart(repo,collectivelog,scripttest)
    if string.find(repo,"git-") == -1:
      brmRepo = "cvs_" + repo
    else:
      brmRepo = "git_" + string.split(repo,'-')[1]
    getResource(buildtag, buildid, brmRepo, "Tagging and Exporting")
    printflush('Sucessfully checked out ' + brmRepo + ' for ' + repo + ' repository at ' + gettime() + '...',collectivelog,scripttest)
    if repo == 'Documentation':
      printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository at ' + gettime() + '...',collectivelog,scripttest)
      applyModuleLabel(repo,cvspaths,docsmodule,collectivelog)
    #elif repo == 'userland' and string.find(conf,'fdbtools') > -1:
    #  mods = ('rpm',)
    #  for m in mods:
    #    printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository for ' + m + \
    #               ' module at ' + gettime() + '...')
    #    applyModuleLabel(repo,cvspaths,m,collectivelog)
    elif repo == 'toolchain' and 's124atom' in buildtag:
      mods = ('gcc',)
      for m in mods:
        printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository for ' + m + \
                   ' module at ' + gettime() + '...',collectivelog,scripttest)
        applyModuleLabel(repo,cvspaths,m,collectivelog)
    elif repo == 'userland' and product == 'devrocket':
      mods = ('apache-ant','jre','jdk')
      for m in mods:
        printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository for ' + m + \
                   ' module at ' + gettime() + '...',collectivelog,scripttest)
        applyModuleLabel(repo,cvspaths,m,collectivelog)
    elif repo == 'mvltest':
      mods = ('common','harness','Makefile')
      for m in mods:
        printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository for ' + m + 
                   ' module at ' + gettime() + '...',collectivelog,scripttest)
        applyModuleLabel(repo,cvspaths,m,collectivelog)
    elif repo == 'cygwin':
      printflush('The cygwin repository is tagged and exported by the buildmvcygwin script',collectivelog,scripttest)
      printflush('which is found in the cht-%s.log file' % buildid,collectivelog,scripttest)
      mstop(repo,collectivelog,scripttest)
      releaseResource(brmRepo)
      continue
    else:
      if string.find(repo,"git-") == -1:
        srctype = "cvs"
        printflush('Applying rtag ' + buildtag + ' in ' + repo + ' repository at ' + gettime() + '...',collectivelog,scripttest)
        applyLabel(repo,cvspaths,collectivelog)
      else:
        srctype = "git"
        # the git repo linux-2.6 will be cloned as linux, so use module for that purpose
        module = 'linux'
        printflush('Cloning, check out and tagging ' + buildtag + ' in ' + repo + ' repository at ' + gettime() + '...',collectivelog,scripttest)
        sourceControlTag(repo,cvspaths,buildtag,collectivelog,scripttest)
    # export the tagged sources
    sourceControlExport(srctype,buildtag,repo,cvspaths[repo][0],collectivelog,scripttest)
    # create changelog
    if mkcl == 'mkcl':
      printflush('making changelog for ' + repo + ' at ' + gettime() + ':',collectivelog,scripttest)
      f_changelog = file(changelog,'a')
      f_changelog.write('::::::::::::::\n')
      f_changelog.close()
      sourceControlChangelog(srctype,repo,starttag,buildtag,cvspaths,changelog,collectivelog,scripttest)
      os.chdir(homepath)
    # run various make commands to prep exports for building as rpms
    if repo == 'mvl-installer':
      if os.path.exists(homepath + '/mvl-installer'):
        os.chdir(homepath + '/mvl-installer')
        printflush('Running make pkg-components at ' + gettime() + '...',collectivelog,scripttest)
        systemCmd('make pkg-components',scripttest,collectivelog)
        systemCmd('mkdir -p RPMS',scripttest)
        os.chdir(homepath)
      else:
        printflush('something happened during the cvs export and the directory does not exist...this is going to be bad for the build.',collectivelog,scripttest)
    elif repo == 'toolchain':
      if os.path.exists(homepath + '/toolchain'):
        os.chdir(homepath + '/toolchain')
        printflush('Running make to generate spec files at ' + gettime() + '...',collectivelog,scripttest)
        mods = ['binutils','elfutils','gcc','glibc','gdb','prelink','uclibc']
        for m in mods:
          if os.path.exists(cvspaths[repo][0] + '/' + m + '/SPECS'):
            os.chdir(cvspaths[repo][0] + '/' + m + '/SPECS')
            systemCmd('make specs',scripttest,collectivelog)
        os.chdir(homepath)
      else:
        printflush('something happened during the cvs export and the directory does not exist...this is going to be bad for the build.',collectivelog,scripttest)
    elif repo == 'mvlt':
      if os.path.exists(cvspaths[repo][0]):
        os.chdir(cvspaths[repo][0])
        printflush('running make all at ' + gettime() + '...')
        # don't use JAVA_HOME since nodes have been changed to have java in PATH
        #os.system('export JAVA_HOME=/usr/java/j2sdk1.4.1_01; export PATH=$JAVA_HOME/bin:$PATH; make all')
        systemCmd('make all',scripttest,collectivelog)
        os.chdir(homepath)
      else:
        printflush('something happened during the cvs export and the directory does not exist...this is going to be bad for the build.',collectivelog,scripttest)
    elif repo == 'mvl-test':
      if os.path.exists(cvspaths[repo][0]):
        os.chdir(cvspaths[repo][0])
        printflush('Running make at ' + gettime() + ':',collectivelog,scripttest)
        systemCmd('make',scripttest,collectivelog)
        systemCmd('mkdir -p RPMS SRPMS',scripttest)
        os.chdir(homepath)
      else:
        printflush('something happened during the cvs export and the directory does not exist...this is going to be bad for the build.',collectivelog,scripttest)
    elif repo == 'licensing':
      if os.path.exists(cvspaths[repo][0]):
        os.chdir(cvspaths[repo][0])
        systemCmd('mkdir -p RPMS SRPMS',scripttest)
        os.chdir(homepath)
      else:
        printflush('something happened during the cvs export and the directory does not exist...this is going to be bad for the build.',collectivelog,scripttest)
    releaseResource(brmRepo)
    mstop(repo,collectivelog,scripttest)
  
#############
# MAIN
#############
conf = sys.argv[1]
if not os.path.exists(conf):
  printflush("The config file (%s) does not exist.  Stopping build." % conf)
  sys.exit(1)
else:
  exec(open(conf))

makeResultsDirs()
mstart('buildprep-script-setup',collectivelogdir + '/buildprep/buildprep-script-setup',scripttest)

if nocl:
  mkcl = 'skipcl'
else:
  mkcl = 'mkcl'

if starttag == "skip":
  printflush("overriding mkcl since startag = skip...check lastgoodbuild for correct product buildtags","%s/buildprep/buildprep-script-setup" % collectivelogdir,scripttest)
  mkcl = 0

commonrpmbin = installdir + '/common/bin/mvl-common-rpm'
commonrpmbuild = installdir + '/common/bin/mvl-common-rpmbuild'
editionrpmbin = installdir + '/' + edition + '/bin/mvl-edition-rpm'
editionrpmbuild = installdir + '/' + edition + '/bin/mvl-edition-rpmbuild'

builddir = os.getcwd()
mstop('buildprep-script-setup',collectivelogdir + '/buildprep/buildprep-script-setup',scripttest)

#########################################################################
# cvs stuff
#########################################################################
cvsstuff()

#if not rVal:
#  sys.exit(0)
#else: 
#  #print 'Build should stop here, but scripts need to be tested, so it will continue.'
#  #print 'Be sure to fix this once scripts are working as intended'
#  #sys.exit(0)
#  print "One or more buildprep rpm failed to build...sending error to buildhhly to stop build."
#  sys.exit(1)
printflush('<' + sys.argv[0] + '>: finished buildprep at ' + gettime() + '...')

