#!/usr/bin/python

import string
import os
import sys
import shutil
import time

def usage():
	print (
"""bk2cvs-mirror <cvsroot> <module> [<end revision>|auto]
Run from the top level of a Bitkeeper repository. cvsroot and module are the
cvsroot and module name of the cvs repository to import to.

The third argument is optional. It should be either the revision number of
the last changeset to import (usefull for testing), or 'auto' for use in
automated scripts where sanity checking prompts are not desired.

NOTE: you MUST specify a full (not relative) path to the bk2cvs-mirror script, 
OR have it in your PATH, or the silly hack used to set the CVS log message
will NOT work.
"""
)

changes_file = '.bk2cvs-changes'
cwd = os.getcwd()
tmpdir = cwd + '/tmp_bk2cvs'
log = cwd + '/tmp_bk2cvs/log'
mypath = sys.argv[0]

# silly thing to get log messages in
if (len(sys.argv) == 2):
	#print(len(sys.argv))
	logmsg = os.environ['BK2CVSLOG']
	#print logmsg
	if (sys.argv[1][0:8] == '/tmp/cvs'):
		cmd = 'cp %s log2 && cat %s >> log2 && mv log2 %s' % \
			(logmsg, sys.argv[1], sys.argv[1])
		#print cmd
		os.system(cmd)
		os.system('touch -m -d "2 sec" %s' % sys.argv[1])
		sys.exit(0)
#end sillyness

#Get tag of last revision imported into cvs
def getlasttag():
	cvscmd = "cvs -Q -d %s co -p %s/%s" % (cvsroot, module, changes_file)
	bk_changes = os.popen(cvscmd).readlines()
	if len(bk_changes) == 0:
		#assume we want to start with 1.1 changeset
		return None
	else:
		#XXX heh, pray & hope that last line has tag of last bk import
		return string.strip(bk_changes[-1])

#Get key of last BK changeset imported...
def getlastkey():
	cvscmd = "cvs -Q -d %s co -p %s/%s" % (cvsroot, module, changes_file)
	bk_changes = os.popen(cvscmd).readlines()
	if len(bk_changes) == 0:
		#assume we want to start with 1.1 changeset
		return None
	else:
		#XXX heh, pray & hope that 2nd to last line has key 
		#         of last bk import
		return string.strip(bk_changes[-2])

	
def mangle(string):
	bad = '$,.:;@'
	new = ''
	for c in string:
		if c in bad:
			new = new + '_'
		else:
			new = new + c

	return new

# return a list of revisions we haven't already imported, up to limit
def getrevs(limit=None):
	key = getlastkey()
	
	f = os.popen('echo "%s" | bk key2rev ChangeSet' % key)
	lastrev = string.strip(f.read())
	
	if not lastrev:
		print 'No lastrev, starting with 1.0' 
		lastrev = '1.0'
	else:
		print 'Lastrev: %s' % lastrev
		
		
	if limit: # just a few..
		range = lastrev + '..' + limit
	else:	# do them all
		range = lastrev + '..'
	
	f = os.popen("bk prs -h -d':REV: ' -r" + range)
	revs = string.split(f.read())

	#we want first -> latest, not latest -> first
	revs.reverse()

	print "Last rev was %s, not importing it" % revs[0]

	#Don't re-import the revision we did before
	#(also has the nice side-effect of not bothering with the 1.0 version)
	return revs[1:]
		
#main...

if (len(sys.argv) != 4 and len(sys.argv) != 3):
	usage()
	sys.exit(0)

if not os.path.exists('BitKeeper'):
	print "Must run from bitkeeper directory"
	print "cwd: %s" % os.getcwd()
	os.exit(1)

cvsroot= sys.argv[1]
module= sys.argv[2]
if len(sys.argv) == 4:
	arg3 = sys.argv[3]
else:
	arg3 = None
vendor= mangle(module)

bkdir = cwd
print cwd
cvspath = tmpdir + '/' + module



revs = []

if arg3 == 'auto':
	revs = getrevs(None)
else:
	if os.path.exists(tmpdir):
		if raw_input('old tmpdir %s already exists, remove it? [yes/no] ' \
				% tmpdir ) != 'yes':
			sys.exit(1)
	revs = getrevs(arg3)

print "Will import revisions:\n%s" % (string.join(revs))

print "Going to import into cvsroot %s module %s" \
		 % (cvsroot, module)

if arg3 != 'auto':
	if raw_input('Are you sure you want do this [yes/no] ') != 'yes':
		sys.exit(1)

os.putenv('BK2CVSLOG', log)

for r in revs:
	os.chdir(bkdir)
	if (os.path.exists(tmpdir)):
		shutil.rmtree(tmpdir)
	os.mkdir(tmpdir)
	print "=========== exporting rev %s (%s is last rev) ==============" \
				% (r,revs[-1])
	# no keyword expansion (-k), 
	bkcmd = 'bk export -k -r%s %s'% (r, cvspath)
	print "-> %s" % bkcmd
	os.system(bkcmd)
	
	os.system ('bk changes -r%s > %s' % (r, log));

	key = os.popen('bk prs -h -d":KEY:" -r%s' % r).read()
	#print "key is: %s" % key
	lastkey = getlasttag()
	#print "last revision is: '%s'" % lastkey

	mkey = mangle(key)
	#print "key mangled for cvs: %s" % mkey
	
	#user = string.split(key, '@')[0]
	#print "importing to cvsroot %s, user %s" %(cvspath, user)

	os.chdir(cvspath)

	#this is a pretty stupid way to do this.. should be integrated
	# with getlasttag or something...
	os.system('cat %s >> %s' % (log, changes_file))
	os.system('echo "%s" >> %s' % (key, changes_file))
	os.system('echo "%s" >> %s' % (mkey, changes_file))

	#this doesn't seem to work
	#os.putenv('CVS_USER', user)
	cvscmd = 'cvs -Q -e %s -d %s import -I ! -ko %s VENDOR_%s "BK_%s"' % \
			(mypath, cvsroot, module,vendor,mkey) 

	print "-> %s" % cvscmd
	os.system(cvscmd)
	os.chdir(tmpdir)
	shutil.rmtree(cvspath)

        # major's suggestion for deleted files and stuff
        #cvs co -j <last tag> -j <current tag> -d <dir to checkout into> <module name>	
	if (lastkey):
		cvscmd = 'cvs -Q -d %s co -j "BK_%s" -j "BK_%s" %s' % \
			(cvsroot, lastkey, mkey, module)
		print "-> %s" % cvscmd
		os.system(cvscmd)
		os.chdir(cvspath)
		cvscmd = 'cvs -Q commit -m "bk2cvs-mirror merge cleanup"'
		print "-> %s" % cvscmd
		os.system(cvscmd)

