#!/usr/bin/python
import os, string, time, sys

if len(sys.argv) == 1:
  print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
  sys.exit(1)
buildtag = sys.argv[1]
starttag = ''
builddir = os.getcwd()
os.system('mkdir cvstmp')
os.chdir('cvstmp')
os.system('cvs -d :ext:build@cvs.sh.mvista.com:/cvsdev/build_scripts -Q co hhl')
tagfile = builddir + '/cvstmp/hhl/lastgoodbuild'
newtagfile = builddir + '/cvstmp/hhl/newlastgoodbuild'
tagprefix = string.split(buildtag,'0')[0]
# read all of lastgoodbuild
starttags = os.popen('cat %s' % (tagfile)).readlines()
for s in starttags:
  if string.find(s,tagprefix+'0') > -1:
    starttag = string.strip(s)
for s in starttags:
  if string.strip(s) != starttag:
    os.system('echo "' + string.strip(s) + '" >> ' + newtagfile)
os.system('echo "' + buildtag + '" >> ' + newtagfile)
print starttag
os.system('rm -f %s; mv %s %s' % (tagfile,newtagfile,tagfile))
# check new lastgoodbuild back into cvs
os.popen('cvs -Q -d :ext:build@cvs.sh.mvista.com:/cvsdev/build_scripts commit -m "Updating for buildtag %s"' % buildtag).read()
os.chdir(builddir)
os.system('rm -rf cvstmp')
