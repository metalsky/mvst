#!/usr/bin/python
import os, sys, string, time, re
# logpath (most likely, /mvista/dev_area/logs)
# build_id (like shb020307, will be appended to logpath for a complete log path

def getTime(log,s_re):
  f_time = 0
  f_log = open(log,'r')
  for line in f_log.readlines():
    tmp = re.match(s_re,line)
    if tmp:
      m_time = re.match('(.*)\[([\d\.]+)\](.*)',line)
      if m_time:
        f_time = float(m_time.group(2))
  f_log.close()
  return f_time 

def getTimeFromList(list,s_re):
  f_time = 0
  for line in list:
    tmp = re.match(s_re,line)
    if tmp:
      m_time = re.match('(.*)\[([\d\.]+)\](.*)',line)
      if m_time:
        f_time = float(m_time.group(2))
  return f_time

def getNode(log,s_re):
  rval = 'no node'
  f_log = open(log,'r')
  for line in f_log.readlines():
    tmp = re.match(s_re,line)
    if tmp:
      node = re.match('(.*)([\d]of[\d])(.*)',line)
      if node:
        rval = node.group(2)
  return rval

def getHost(log,s_re):
  rval = 'no host'
  f_log = open(log,'r')
  for line in f_log.readlines():
    tmp = re.match(s_re,line)
    if tmp:
      host = re.match('(.*) on (.*) target (.*)',line)
      if host:
        rval = host.group(2)
  return rval

def secToTime(secs):
  hm = divmod(secs,3600)
  ms = divmod(hm[1],60)
  h = str(int(hm[0]))
  m = str(int(ms[0]))
  s = str(int(ms[1]))
  s_Time = h + 'hrs ' + m + 'min ' + s + 'sec'
  return s_Time

def getRpms(log):
  rpms = []
  r_log = open(log,'r')
  for line in r_log.readlines():
    tmp = re.match('(.*)building(.*)at(.*)',line)
    if tmp:
      rpms.append(string.strip(tmp.group(2)))
  return rpms

def getLines(log,type):
  lLines = []
  r_log = open(log,'r')
  for line in r_log.readlines():
    tmp = re.match('(.*)' + type + '(.*)at(.*)',line)
    if tmp:
      lLines.append(line)
  r_log.close()
  return lLines

def printScriptTimes(log):
  st_buildhhl = getTime(log,'Starting buildhhl\.py on (.*) at(.*)\[([\d\d]+)(.*)')
  ft_buildhhl = getTime(log,'Finished buildhhl\.py on (.*) at(.*)\[([\d\d]+)(.*)')
  print 'buildhhl.py took ' + secToTime(ft_buildhhl - st_buildhhl)
  # get buildprep time
  st_buildprep = getTime(log,'Running buildprep\.py (.*)\[([\d\d]+)(.*)')
  ft_buildprep = getTime(log,'Finished buildprep\.py (.*)\[([\d\d]+)(.*)')
  print 'buildprep.py took ' + secToTime(ft_buildprep - st_buildprep)
  # get buildcfg8r time
  st_buildcfg8r = getTime(log,'Running buildcfg8r\.py (.*)\[([\d\d]+)(.*)')
  ft_buildcfg8r = getTime(log,'Finished buildcfg8r\.py (.*)\[([\d\d]+)(.*)')
  print 'buildcfg8r.py took ' + secToTime(ft_buildcfg8r - st_buildcfg8r)
  # get buildhost time
  st_buildhost = getTime(log,'Running buildhost\.py (.*)\[([\d\d]+)(.*)')
  ft_buildhost = getTime(log,'Finished buildhost\.py (.*)\[([\d\d]+)(.*)')
  print 'buildhost.py took ' + secToTime(ft_buildhost - st_buildhost)
  # get node build times
  for a in archs:
    st_buildarch = getTime(log,'building target ' + a +
                           ' on node ([1-9]of[1-9]) (.*)\[([\d\d]+)(.*)')
    ft_buildarch = getTime(log,'completed target ' + a +
                           ' node ([1-9]of[1-9]) (.*)\[([\d\d]+)(.*)')
    print 'buildcore.py for %s took %s on %s' % (a,
          secToTime(ft_buildarch - st_buildarch), getNode(log,'building target ' + a +
          ' on node ([1-9]of[1-9]) (.*)\[([\d\d]+)(.*)'))
  # get host build times
  for h in hosts:
    for a in archs:
      st_buildremote = getTime(log,'building ' + h + ' host tools(.*)' + a +
                               '(.*)\[([\d\d]+)(.*)')
      ft_buildremote = getTime(log,'completed ' + h + ' host tools(.*)' + a +
                               '(.*)\[([\d\d]+)(.*)')
      print 'buildremote.py on %s for %s took %s on %s' % (h, a,
               secToTime(ft_buildremote - st_buildremote),
               getHost(log,'building ' + h + ' (.*)' + a + '(.*)'))

def printTime(log):
  rpms = getRpms(log)
  building = getLines(log,'building')
  finished = getLines(log,'finished')
  for r in rpms:
    st_bp = getTimeFromList(building,'(.*)building ' + r + '(.*)\[([\d\d]+)(.*)')
    ft_bp = getTimeFromList(finished,'(.*)finished ' + r + '(.*)\[([\d\d]+)(.*)')
    if ft_bp != 0:
      print '%s took %s' % (r,secToTime(ft_bp - st_bp))
    else:
      print r + ' failed to build'

def printTimeArch(log,arch):
  rpms = getRpms(log)
  building = getLines(log,'building')
  finished = getLines(log,'finished')
  for r in rpms:
    st_bp = getTimeFromList(building,'(.*)building ' + r + '(.*)\[([\d\d]+)(.*)')
    ft_bp = getTimeFromList(finished,'(.*)finished ' + r + '(.*)\[([\d\d]+)(.*)')
    if ft_bp != 0:
      print '%s for %s took %s' % (r,arch,secToTime(ft_bp - st_bp))
    else:
      print r + ' failed to build'

def printHostTimeArch(log,arch,host):
  rpms = getRpms(log)
  building = getLines(log,'building')
  finished = getLines(log,'finished')
  for r in rpms:
    st_bp = getTimeFromList(building,'(.*)building ' + r + '(.*)\[([\d\d]+)(.*)')
    ft_bp = getTimeFromList(finished,'(.*)finished ' + r + '(.*)\[([\d\d]+)(.*)')
    if ft_bp != 0:
      print '%s for %s on %s took %s' % (r,arch,host,secToTime(ft_bp - st_bp))
    else:
      print r + ' failed to build'

if len(sys.argv) != 3:
  print 'Usage: %s %s %s' % (sys.argv[0], '<logpath>', '<build_id>')
  print '%s will be appended to %s for the full path' % ('<build_id>', '<logpath>')
  sys.exit(1)

logpath = sys.argv[1]
build_id = sys.argv[2]

hosts = ('mandrake72','mandrake80','mandrake81','redhat62','redhat70',
         'solaris7','suse73','yellowdog21')

logdir = logpath + '/' + build_id
dontcheck = ('NotBuilt','cdimage','sht')

os.chdir(logdir)
archs = []
startarchs = 0
for l in open('hhl-' + build_id + '.log','r').readlines():
  tmp = re.match('Building the following architectures:',l)
  if tmp:
    startarchs = 1
  if startarchs:
    if string.find(l,'Building') == -1 and string.find(l,'Using') == -1:
      archs.append(string.strip(l))
    elif string.find(l,'Using') > -1:
      break

logs = []
for a in os.listdir(logdir):
  p = 0
  for b in dontcheck:
    if string.find(a,b) > -1:
      p = 1
  if not p:
    logs.append(a)

# get buildtime for buildhhl.py:
if 'hhl-' + build_id + '.log' in logs:
  printScriptTimes('hhl-' + build_id + '.log')
# get buildtime for each host noarch/cluster rpm
noarchlogs = ('buildprep-','cnfg8r-','buildhost-')
for n in noarchlogs:
  if n + build_id + '.log' in logs:
    printTime(n + build_id + '.log')
# get buildtime for each rpm built by buildcore.py
for arch in archs:
  lfs = ['core-' + arch + '-' + build_id + '.log',
         'noarch-' + arch + '-' + build_id + '.log',
         'lsp-' + arch + '-' + build_id + '.log',
        ]
  for lf in lfs:
    if lf in logs:
      printTimeArch(lf,arch)
  for h in hosts:
    if h + '-' + arch + '-' + build_id + '.log' in logs:
      printHostTimeArch(h + '-' + arch + '-' + build_id + '.log',arch,h)

