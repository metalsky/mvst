#!/usr/bin/python
import getopt, os, time, sys, string, datetime
from resourceManager import *
from bumpid import bumpid

# Every build starts by tagging the build_scripts repository, exporting
# it, and invoking a well-known program in the build_scripts repo with
# as few arguments as make sense.  The point is to ensure that the build
# scripts and build data that make up a build come from CVS and are
# tagged with the same tag that the other repos get.
# I envision a single script that will be fairly simple and not need to
# change much.  It will live in /home/build/bin/ but will also be kept
# in the HEAD of the build_scripts repo. 
# The inputs to the script must be taken as arguments, because most
# often this will be in a cron script.

# Inputs:
# - input-tag
#   A tag (could be a branch tag or a revision tag) of the
#   build_scripts repo to use.  Should do the right thing if
#   "HEAD" is specified.
# - type-of-build (such as "pro")
#   This will be passed verbatim as the argument to buildhhl).  It will be up to
#   buildhhl to know exactly what to do, given just this type-of-build,
#   buildtag and the buildid
# - buildtag-prefix OR entire buildtag
#   If just a prefix is passed in, a full buildtag of <prefix><date>[suffix]
#   should be generated.  If they pass in a full buildtag, then no need to
#   do the date stuff.

# Here's a suggestion of how the arguments might look, demonstrated by
# examples:

#  startbuild foundation_one_branch pro prefix pe
#  startbuild HEAD mvg mvg_pro_3_1_final

# The script will:

# - Determine the buildtag in the usual way if passed in just the prefix,
#   or just use the one given (and check that using it won't cause problems)
# - do the bumpid procedure and get the buildid for this build
# - apply the buildtag revision tag to the input-tag (or HEAD, if specified)
#   branch (or revision) tag of the build_scripts CVS repo
# - export the build_scripts repo using the buildtag tag
#   export it to /home/build/<buildtag>/exports/build_scripts/
# - invoke /home/build/<buildtag>/exports/build_scripts/buildhhl
#   with the type-of-build, buildtag, and buildid arguments.
#

# Obviously, buildhhl will need be modified to handle this set of args
# coming in.  Or, you may want to choose to create a different well-known
# scriptname as an interface to buildhhl.

def gettime():
  t_time = time.localtime(time.time())
  s_time = time.strftime("%H:%M:%S %Z %Y/%m/%d",t_time)
  f_time = time.mktime(t_time)
  print s_time + ' [' + str(f_time) + ']'
  return f_time


bindir = '/home/build/bin'
product = ""
build_script_branch = ""
prefix = ""
buildid = ""
buildtag = ""
build_type = ""
email = ""
suffix = 0
verbose = ""
e = ""
conf = ""

def usage(string):
  print \
  """Usage: 
    launch.py [--product <product>]                   ==> required, this is also the --distro used 
                                                          for mvl6 and later builds
              [--build_script_branch <branch name>]   ==> required
              [--prefix <tag prefix>]                 ==> where <tag prefix> will be prepended 
                                                          before a date string
              [--config <data file>]                  ==> config file to be used in build
              [--msd <msd name>]                      ==> msd name for mvl6 or later builds
              [-t|--tag <tag>]                        ==> where <tag> is a full tag
              [--build_type <build type>]             ==> this is used to build a component of a product,
                                                          such as a (async), e (eclipse) or pk (preview 
                                                          kit).  If this is specified, the value passed 
                                                          to buildhhl.py will be <product><build_type> 
                                                          and the buildtag will be 
                                                          <prefix><build_type><date>, so, to build a 
                                                          propk build, use --product pro --build_type pk
                                                          which will result in a buildtag of pepk<date>
              [--email <loser@mvista.com>]            ==> email address of person requesting build
                                                          [optional]
              [-h|--help]
              [-v|--verbose]
  """
  print string
  sys.exit(2)
##################
# check arguments
##################
try:
  opts, args = getopt.getopt(sys.argv[1:], "hvt:", ["help","verbose","tag=","product=","build_script_branch=", "prefix=","build_type=","email=","config=","msd="])
except getopt.GetoptError:
  # print help information and exit:
  usage("unknown option, try again")

if len(args) != 0:
  usage("no named arguments!")

if len(opts) == 0:
  usage("need at least 1 argument")

preq = 0
breq = 0
ptreq = 0
treq = 0
for o, a in opts:
  #print "o = " + o
  if o == "--product":
    #print "found --product"
    product = a
    preq = 1
  elif o == "--config":
    conf = a
  elif o == "--msd":
    msd = a
  elif o in ("--bsb","--build_script_branch"):
    #print "found --build_script_branch"
    build_script_branch = a
    breq = 1
  elif o == "--prefix":
    #print "found --prefix"
    prefix = a
    ptreq = 1
  elif o in ("-t","--tag"):
    #print "found tag"
    buildtag = a
    treq = 1
  elif o == "--build_type":
    build_type = a
  elif o == "--email":
    email = a
  elif o in ("-h", "--help"):
    usage("")
  elif o in ("-v", "--verbose"):
    print "opts:"
    print opts
    print "args:"
    print args
    verbose = 1

if not preq:
  usage("you must specify a product using --product")
elif not breq:
  usage("you must specify a build_scripts branch using --build_script_branch or --bsb")
elif not ptreq and not treq:
  usage("you must specify a tag using either --prefix or -t|--tag")

# start
print "Start time: "
start = gettime()

#############
# tagging
#############
if verbose:
  print "Scheduling Build..."
if prefix:
  # generate tag from prefix & date
  if verbose:
    print "Generating buildtag..."
  buildtag = prefix + build_type + time.strftime('%y%m%d', time.localtime(time.time()))
  if build_type == 'pk':
    product = product + build_type
#################
# run bumpid.py
#################
if verbose:
  print "Generating buildid..."
tmpdir = '/var/tmp/%s' % (buildtag)
os.system('mkdir -p %s' % (tmpdir))
os.chdir(tmpdir)

#Removed, bumpid is now a function
#os.system('cvs -Q -d :ext:rodan:/cvsdev/build_scripts export -D now hhl/bumpid.py')
#os.chdir('hhl')
#buildid = string.strip(os.popen('./bumpid.py %s' % (buildtag)).read())
getResource(buildtag,buildid,"cvs_build_scripts","Tagging and exporting")
buildid = bumpid(buildtag)
releaseResource("cvs_build_scripts")
if buildid == 'null':
  sys.exit(1)

os.chdir(bindir)
if os.path.exists('%s' % (tmpdir)):
  os.system('rm -rf %s' % (tmpdir))
# adjust buildtag to be buildtag_buildid, only if using --prefix
if prefix:
  buildtag = buildtag + '_' + buildid
  logdir = '/mvista/dev_area/%s/logs/%s' % (product,buildtag)
  while os.path.exists(logdir):
    if verbose:
      print "found existing log directory %s, creating suffix..." % (logdir)
    suffix = suffix + 1
    buildtag = buildtag + '_' + str(suffix)
    logdir = '/mvista/dev_area/%s/logs/%s' % (product,buildtag)
    if verbose:
      print "now checking %s..." % (logdir)
if verbose:
  print "buildtag is %s" % (buildtag)
  print "buildid is %s" % (buildid)

###############################
# get start tag for changelog
###############################
tmpdir = '/var/tmp/%s' % (buildtag)
os.system('mkdir -p %s' % (tmpdir))
os.chdir(tmpdir)
getResource(buildtag,buildid,"cvs_build_scripts","Tagging and exporting")
os.system('cvs -Q -d :ext:cvs.sh.mvista.com:/cvsdev/build_scripts export -D now hhl/bumpstarttag.py')
os.chdir('hhl')
starttag = string.strip(os.popen('./bumpstarttag.py %s %s' % (buildtag,product)).read())
releaseResource("cvs_build_scripts")
if starttag == "":
  starttag = "skip"
if verbose:
  print "starttag is %s" % (starttag)
os.chdir(bindir)
if os.path.exists('%s' % (tmpdir)):
  os.system('rm -rf %s' % (tmpdir))

###################################
# apply tag to build_scripts repo
###################################

getResource(buildtag,buildid,"cvs_build_scripts","Tagging and exporting")
if verbose:
  print "tagging build_scripts..."
if product in ('ip','mvl6'):
  buildmodule = 'mvl6'
else:
  buildmodule = 'hhl'
if build_script_branch in ('dev','HEAD'):
  os.system('cvs -Q -d :ext:cvs.sh.mvista.com:/cvsdev/build_scripts rtag -F -D now %s %s' % (buildtag,buildmodule))
else:
  os.system('cvs -Q -d :ext:cvs.sh.mvista.com:/cvsdev/build_scripts rtag -F -r %s %s %s' % (build_script_branch,buildtag,buildmodule))
#######################
# export build scripts
#######################
if verbose:
  print "exporting build_scripts..."
builddir = '/home/build/%s-exp/CVSREPOS' % (buildtag)
os.system('expbs %s %s-exp/CVSREPOS' % (buildtag,buildtag))
os.chdir(builddir)
releaseResource("cvs_build_scripts")

#############
# run build
#############
if verbose:
  print "running main build script..."
  if email:
    print "email = " + email
    print "sending build email to additional recipients"
if product not in ('ip','mvl6'):
  os.chdir('%s/build_scripts/hhl' % (builddir))
  if conf and email:
    os.system('./buildhhl.py %s %s %s %s %s %s conf=%s' % (product, buildtag, buildid, build_script_branch, starttag, email, conf))
  elif conf:
    os.system('./buildhhl.py %s %s %s %s %s conf=%s' % (product, buildtag, buildid, build_script_branch, starttag, conf))
  elif email:
    os.system('./buildhhl.py %s %s %s %s %s %s' % (product, buildtag, buildid, build_script_branch, starttag, email))
  else:
    os.system('./buildhhl.py %s %s %s %s %s' % (product, buildtag, buildid, build_script_branch, starttag))
elif product == 'ip':
  os.chdir('%s/build_scripts/mvl6' % (builddir))
  os.system('./buildip.py %s %s' % (buildtag,starttag))
elif product == 'mvl6' and msd == "collection":
  os.chdir('%s/build_scripts/mvl6' % (builddir))
  os.system('./collectionBuild.py %s' % buildtag)
elif product == 'mvl6':
  os.chdir('%s/build_scripts/mvl6' % (builddir))
  os.system('./main.py %s %s %s %s %s' % (buildtag,starttag,buildid,product,msd))
# once buildhhl.py is done, determine if the exported scripts repo should be deleted
if os.path.exists('/home/build/%s-exp' % buildtag):
  if product not in ('ip','mvl6'):
    conf = '/home/build/%s-exp/CVSREPOS/build_scripts/hhl/%s.dat' % (buildtag,buildtag)
    if os.path.exists(conf):
      exec(open(conf))
      if cleanexp:
        os.system('rm -rf /home/build/%s-exp' % buildtag)
  else:
    os.system('rm -rf /home/build/%s-exp' % buildtag)


# finish
print "Finish time: "
fini = gettime()

elapse = fini - start
s_elapse = str(datetime.timedelta(seconds=elapse))

print "Elapsed time: " + s_elapse

