#!/usr/bin/python
import os, string, time, sys, re

if len(sys.argv) == 1:
  print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
  sys.exit(1)
buildtag = sys.argv[1]

def bumpid(buildtag):
  #Check to see if we have a valid buildtag
  if not re.match(r'.+\d\d\d\d\d\d',buildtag):
    raise ValueError, "Bad Buildtag: %s passed to bumpid"%(buildtag)
  builddir = os.getcwd()
  os.system('mkdir cvstmp')
  os.chdir('cvstmp')
  os.system('cvs -d :ext:build@cvs.sh.mvista.com:/cvsdev/build_scripts -Q co hhl')
  tagfile = builddir + '/cvstmp/hhl/taglist'
  # read all of taglist
  f = open(tagfile,'r')
  line = ''
  lines = f.readlines()
  f.close()
  newlines = []
  for l in lines:
        line = string.strip(l)
        id = string.split(line,',')[1]
        newlines.append(id)
  newlines.sort()
  for l in newlines:
        line = string.strip(l)
  # get last buildid
  oldyr = line[:2]
  id = line[2:]
  nid = string.zfill(str(string.atoi(id) + 1),5)
  newyr = time.strftime("%y",time.localtime(time.time()))
  if string.atoi(newyr) == string.atoi(oldyr) + 1:
    nid = newyr + '00001'
  else:
    nid = newyr + nid
  nline = buildtag + ',' + nid
  os.system('echo "%s" >> %s' % (nline,tagfile))
  # check new taglist back into cvs
  os.popen('cvs -Q -d :ext:build@cvs.sh.mvista.com:/cvsdev/build_scripts commit -m "Updating for buildtag %s and buildid %s"' % (buildtag,nid)).read()
  os.chdir(builddir)
  os.system('rm -rf cvstmp')
  #Check to see if our buildid is valid
  if not re.match(r'\d\d\d\d\d\d\d', nid):
    raise StandardError, "bumpid produced bad buildid"
  return nid

def main(argv):
  if len(argv) == 1:
    print 'usage: %s %s' % (sys.argv[0],'<buildtag>')
    sys.exit(1)
  nid = bumpid(sys.argv[1])
  print nid



if __name__== "__main__":
  main(sys.argv)


