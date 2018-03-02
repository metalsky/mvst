#!/usr/bin/python

import sys, os, string, re

#This script enters a series of CVS commands on the various repositories.
#This script can be dangerous, don't use it incorrectly or you'll screw up all sorts of tags.

if(len(sys.argv) != 4):

  print "************************************************************************"
  print "*releaseTagger.py - This script goes and tags all the repos for you    *"
  print "* Usage - releaseTagger.py <foundation tag> <edition tag> <release tag>*"
  print "*                                                                      *"
  print "****************Don't reverse the order of these tags!!!****************"
  sys.exit(1)


foundationTag = sys.argv[1]
editionTag = sys.argv[2]
releaseTag = sys.argv[3]

extracted = re.match(r"\w+\d\d\d\d\d\d_(\d+)",foundationTag)
buildNum = extracted.group(1)

os.system("clear")
print "This is the information I have:"
print "Foundation Build Tag: %s"%(foundationTag)
print "Foundation Build ID: %s"%(buildNum)
print "Edition Build Tag: %s"%(editionTag)
print "Release Tag: %s"%(releaseTag)

try:
  userInput = raw_input("Is this correct?(y to continue)")
except:
  print "Unknown Error"
  sys.exit(1)

if(userInput is not 'y'):
  print "Goodbye!"
  sys.exit(1)

cvsopts = 'cvs -z1 -Q -d :ext:build@rodan:/cvsdev'
print "Tagging mvl-kernel-26..."
os.system("%s/mvl-kernel-26 rtag -r %s %s_%s ."%(cvsopts,foundationTag,releaseTag,buildNum))
os.system("%s/mvl-kernel-26 rtag -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging toolchain..."
os.system("%s/toolchain rtag -r %s %s ."%(cvsopts,foundationTag,releaseTag))
print "Tagging userland..."
os.system("%s/userland rtag -r %s %s ."%(cvsopts,foundationTag,releaseTag))
os.system("%s/userland rtag -F -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging lsp..."
os.system("%s/lsp rtag -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging mvlt..."
os.system("%s/mvlt rtag -r %s %s ."%(cvsopts,foundationTag,releaseTag))
os.system("%s/mvlt rtag -F -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging mvl-installer..."
os.system("%s/mvl-installer rtag -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging build_scripts..."
os.system("%s/build_scripts rtag -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging Documentation..."
os.system("%s/Documentation rtag -r %s %s ."%(cvsopts,editionTag,releaseTag))
print "Tagging cygwin..."
os.system("%s/cygwin rtag -r %s %s ."%(cvsopts,foundationTag,releaseTag))
